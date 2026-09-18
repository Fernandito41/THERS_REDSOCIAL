# Pruebas de integración de POST /api/auth/google
# (ADR-012-google-sign-in.md) contra PostgreSQL 16 real (thers_test, ver
# conftest.py) -- no mocks de base de datos, solo de Google: se monkeypatchea
# `auth_routes._google_identity_verifier.verify` con identidades de Google
# fabricadas a mano (FASE 24 de la tarea origen, "mockea Google
# apropiadamente... los tests NO deben depender de llamadas reales a
# Google") -- la verificación criptográfica en sí (firma/issuer/audience/
# expiración) la cubre tests/test_google_id_token_verifier.py por separado,
# sin red tampoco.

import uuid

from flask_jwt_extended import decode_token

import app.interfaces.routes.auth_routes as auth_routes
from app.domain.auth.exceptions import GoogleEmailNotVerifiedError, InvalidGoogleCredentialError
from app.domain.auth.google_identity import GoogleIdentity
from app.extensions import db
from app.infrastructure.persistence.models import User, UserIdentity
from tests.conftest import mark_email_verified

VALID_PASSWORD = "secretpass"


def _mock_google_identity(monkeypatch, sub, email, email_verified=True, name="Test Google"):
    def _fake_verify(credential):
        return GoogleIdentity(sub=sub, email=email, email_verified=email_verified, name=name)

    monkeypatch.setattr(auth_routes._google_identity_verifier, "verify", _fake_verify)


def _mock_google_invalid_credential(monkeypatch):
    def _fake_verify(credential):
        raise InvalidGoogleCredentialError()

    monkeypatch.setattr(auth_routes._google_identity_verifier, "verify", _fake_verify)


def _register_payload(**overrides):
    payload = {
        "name": "Ada Lovelace",
        "username": "ada_lovelace",
        "email": "ada@example.com",
        "phone": "7000-1234",
        "country_code": "+503",
        "birth_date": "1990-01-01",
        "password": VALID_PASSWORD,
        "confirm_password": VALID_PASSWORD,
    }
    payload.update(overrides)
    return payload


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestInvalidCredential:
    def test_invalid_credential_returns_400_without_creating_a_user(self, app, client, monkeypatch):
        _mock_google_invalid_credential(monkeypatch)

        response = client.post("/api/auth/google", json={"credential": "garbage"})

        assert response.status_code == 400
        with app.app_context():
            assert db.session.query(User).count() == 0

    def test_missing_credential_returns_400(self, client):
        response = client.post("/api/auth/google", json={})
        assert response.status_code == 400

    def test_empty_body_returns_400(self, client):
        response = client.post("/api/auth/google")
        assert response.status_code == 400


class TestGoogleEmailNotVerified:
    def test_unverified_google_email_returns_400_without_creating_a_user(
        self, app, client, monkeypatch
    ):
        _mock_google_identity(
            monkeypatch, sub="g-1", email="sinverificar@example.com", email_verified=False
        )

        response = client.post("/api/auth/google", json={"credential": "whatever"})

        assert response.status_code == 400
        with app.app_context():
            assert db.session.query(User).filter_by(email="sinverificar@example.com").count() == 0


class TestNewGoogleUser:
    def test_creates_user_with_incomplete_profile_and_issues_token(
        self, app, client, monkeypatch
    ):
        _mock_google_identity(
            monkeypatch, sub="g-new-1", email="nuevo@example.com", name="Persona Nueva"
        )

        response = client.post("/api/auth/google", json={"credential": "whatever"})

        assert response.status_code == 200
        body = response.get_json()
        assert "token" in body
        user = body["user"]
        assert user["email"] == "nuevo@example.com"
        assert user["email_verified"] is True
        assert user["profile_completed"] is False
        assert user["has_password"] is False
        assert user["phone"] is None
        assert user["country_code"] is None
        assert user["birth_date"] is None
        # username provisorio, pero válido según el mismo formato que exige
        # el registro tradicional -- nunca vacío ni None.
        assert len(user["username"]) >= 3

        with app.app_context():
            db_user = db.session.query(User).filter_by(email="nuevo@example.com").one()
            assert db_user.password_hash is None
            assert db_user.profile_completed is False
            identity = (
                db.session.query(UserIdentity)
                .filter_by(provider="google", provider_subject="g-new-1")
                .one()
            )
            assert identity.user_id == db_user.id

    def test_never_exposes_the_google_subject_in_the_response(self, client, monkeypatch):
        _mock_google_identity(monkeypatch, sub="g-secret-sub", email="a@example.com")

        response = client.post("/api/auth/google", json={"credential": "whatever"})

        raw_body = response.get_data(as_text=True)
        assert "g-secret-sub" not in raw_body

    def test_jwt_identity_is_user_uuid_not_google_sub(self, app, client, monkeypatch):
        _mock_google_identity(monkeypatch, sub="g-new-2", email="nuevo2@example.com")

        response = client.post("/api/auth/google", json={"credential": "whatever"})
        token = response.get_json()["token"]
        user_id = response.get_json()["user"]["id"]

        with app.app_context():
            decoded = decode_token(token)
        assert decoded["sub"] == user_id
        assert decoded["sub"] != "g-new-2"
        uuid.UUID(decoded["sub"])  # no lanza si es un UUID válido

    def test_users_me_works_after_google_login(self, client, monkeypatch):
        _mock_google_identity(monkeypatch, sub="g-new-3", email="nuevo3@example.com")
        response = client.post("/api/auth/google", json={"credential": "whatever"})
        token = response.get_json()["token"]

        me_response = client.get("/api/users/me", headers=_auth_headers(token))

        assert me_response.status_code == 200
        assert me_response.get_json()["user"]["email"] == "nuevo3@example.com"

    def test_traditional_login_fails_for_a_google_only_account(self, client, monkeypatch):
        # Sin contraseña local -- FASE 12/13 de la tarea origen. Nunca se
        # revela que la cuenta es Google-only, mismo mensaje/código que
        # cualquier otro login fallido.
        _mock_google_identity(monkeypatch, sub="g-new-4", email="nuevo4@example.com")
        client.post("/api/auth/google", json={"credential": "whatever"})

        response = client.post(
            "/api/login", json={"email": "nuevo4@example.com", "password": "cualquier-cosa"}
        )

        assert response.status_code == 401

    def test_complete_profile_via_existing_patch_users_me(self, app, client, monkeypatch):
        # FASE 18: "Complete your profile" reutiliza PATCH /api/users/me
        # (ADR-003) tal cual, sin endpoint nuevo.
        _mock_google_identity(monkeypatch, sub="g-new-5", email="nuevo5@example.com")
        response = client.post("/api/auth/google", json={"credential": "whatever"})
        token = response.get_json()["token"]

        patch_response = client.patch(
            "/api/users/me",
            json={
                "username": "nombre_elegido",
                "phone": "7000-9999",
                "country_code": "+503",
                "birth_date": "1995-05-20",
            },
            headers=_auth_headers(token),
        )

        assert patch_response.status_code == 200
        assert patch_response.get_json()["user"]["profile_completed"] is True
        assert patch_response.get_json()["user"]["username"] == "nombre_elegido"

    def test_choosing_username_during_onboarding_does_not_hit_cooldown(
        self, app, client, monkeypatch
    ):
        # El username provisorio nunca cuenta como "un cambio" -- username_changed_at
        # se queda en NULL hasta que la persona elige el suyo, así que esa
        # primera elección real nunca choca con el cooldown de 30 días
        # (domain/auth/username_policy.py).
        _mock_google_identity(monkeypatch, sub="g-new-6", email="nuevo6@example.com")
        response = client.post("/api/auth/google", json={"credential": "whatever"})
        token = response.get_json()["token"]

        first = client.patch(
            "/api/users/me", json={"username": "primera_eleccion"}, headers=_auth_headers(token)
        )
        assert first.status_code == 200

        second = client.patch(
            "/api/users/me", json={"username": "segunda_eleccion"}, headers=_auth_headers(token)
        )
        # Cambiar de nuevo SÍ debería chocar con el cooldown -- confirma que
        # la primera elección post-onboarding ya se contó como un cambio
        # real, a diferencia del placeholder inicial.
        assert second.status_code == 400


class TestExistingGoogleUser:
    def test_second_login_with_same_sub_returns_the_same_user_without_duplicating(
        self, app, client, monkeypatch
    ):
        _mock_google_identity(monkeypatch, sub="g-existing-1", email="existente@example.com")

        first = client.post("/api/auth/google", json={"credential": "whatever"})
        second = client.post("/api/auth/google", json={"credential": "whatever"})

        assert first.status_code == second.status_code == 200
        assert first.get_json()["user"]["id"] == second.get_json()["user"]["id"]

        with app.app_context():
            assert (
                db.session.query(User).filter_by(email="existente@example.com").count() == 1
            )
            assert (
                db.session.query(UserIdentity)
                .filter_by(provider="google", provider_subject="g-existing-1")
                .count()
                == 1
            )

    def test_returning_user_does_not_reset_a_completed_profile(self, client, monkeypatch):
        _mock_google_identity(monkeypatch, sub="g-existing-2", email="existente2@example.com")
        first = client.post("/api/auth/google", json={"credential": "whatever"})
        token = first.get_json()["token"]
        client.patch(
            "/api/users/me",
            json={"phone": "7000-1111", "country_code": "+503", "birth_date": "1990-01-01"},
            headers=_auth_headers(token),
        )

        second = client.post("/api/auth/google", json={"credential": "whatever"})

        assert second.get_json()["user"]["profile_completed"] is True


class TestAccountLinking:
    def test_verified_traditional_account_auto_links_google(self, app, client, monkeypatch):
        # FASE 9, caso "se vincula automático": la cuenta YA estaba
        # verificada (alguien probó controlar el correo antes) -- Google se
        # agrega como método adicional, la contraseña original sigue
        # funcionando.
        register_response = client.post("/api/register", json=_register_payload())
        user_id = register_response.get_json()["user"]["id"]
        mark_email_verified(user_id)

        _mock_google_identity(monkeypatch, sub="g-link-1", email="ada@example.com")
        response = client.post("/api/auth/google", json={"credential": "whatever"})

        assert response.status_code == 200
        assert response.get_json()["user"]["id"] == user_id

        with app.app_context():
            db_user = db.session.get(User, uuid.UUID(user_id))
            assert db_user.password_hash is not None  # la contraseña original NO se toca
            identity = (
                db.session.query(UserIdentity)
                .filter_by(provider="google", provider_subject="g-link-1")
                .one()
            )
            assert identity.user_id == db_user.id

        # La contraseña tradicional sigue funcionando -- Google se agregó
        # como método ADICIONAL, no reemplazó al que había.
        login_response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": VALID_PASSWORD}
        )
        assert login_response.status_code == 200

    def test_never_verified_traditional_account_is_reclaimed_and_password_revoked(
        self, app, client, monkeypatch
    ):
        # FASE 9, caso "se reclama": nadie había probado nunca ser el dueño
        # real de esa cuenta (email_verified=false) -- Google ahora sí lo
        # prueba. La contraseña que hubiera puesto quien la registró se
        # anula (podría no ser la persona real) y la cuenta pasa a
        # verificada.
        register_response = client.post(
            "/api/register", json=_register_payload(email="squatter@example.com")
        )
        user_id = register_response.get_json()["user"]["id"]
        # Deliberadamente NO se verifica -- simula que "squatter@example.com"
        # nunca completó el OTP (podría no ser el dueño real del correo).

        _mock_google_identity(monkeypatch, sub="g-reclaim-1", email="squatter@example.com")
        response = client.post("/api/auth/google", json={"credential": "whatever"})

        assert response.status_code == 200
        assert response.get_json()["user"]["id"] == user_id
        assert response.get_json()["user"]["email_verified"] is True
        assert response.get_json()["user"]["has_password"] is False

        with app.app_context():
            db_user = db.session.get(User, uuid.UUID(user_id))
            assert db_user.password_hash is None
            assert db_user.email_verified is True

        # La contraseña original (de quien haya registrado la cuenta antes
        # de que Google la reclamara) ya no sirve para nada.
        old_login = client.post(
            "/api/login", json={"email": "squatter@example.com", "password": VALID_PASSWORD}
        )
        assert old_login.status_code == 401

    def test_linking_does_not_create_a_duplicate_user_row(self, app, client, monkeypatch):
        register_response = client.post(
            "/api/register", json=_register_payload(email="unico@example.com")
        )
        mark_email_verified(register_response.get_json()["user"]["id"])

        _mock_google_identity(monkeypatch, sub="g-link-2", email="unico@example.com")
        client.post("/api/auth/google", json={"credential": "whatever"})

        with app.app_context():
            assert db.session.query(User).filter_by(email="unico@example.com").count() == 1


class TestSetPasswordForGoogleOnlyAccount:
    def test_forgot_password_flow_sets_a_first_password_for_a_google_only_account(
        self, app, client, monkeypatch
    ):
        # FASE 10: una cuenta Google-only puede usar el flujo existente de
        # recuperación de contraseña para FIJAR su primera contraseña, sin
        # ningún cambio de código en forgot-password/verify-reset-code/
        # reset-password -- un UPDATE funciona igual si el valor previo era
        # NULL.
        import uuid as uuid_module
        from datetime import datetime, timedelta, timezone

        from app.domain.auth.auth_service import hash_password
        from app.infrastructure.persistence.models import PasswordResetToken

        _mock_google_identity(monkeypatch, sub="g-setpw-1", email="googleonly@example.com")
        register_response = client.post("/api/auth/google", json={"credential": "whatever"})
        user_id = register_response.get_json()["user"]["id"]

        forgot_response = client.post(
            "/api/forgot-password", json={"email": "googleonly@example.com"}
        )
        assert forgot_response.status_code == 200

        known_code = "123456"
        with app.app_context():
            db.session.query(PasswordResetToken).filter_by(
                user_id=uuid_module.UUID(user_id)
            ).update(
                {
                    "code_hash": hash_password(known_code),
                    "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
                }
            )
            db.session.commit()

        verify_response = client.post(
            "/api/verify-reset-code",
            json={"email": "googleonly@example.com", "code": known_code},
        )
        assert verify_response.status_code == 200
        reset_authorization = verify_response.get_json()["reset_authorization"]

        reset_response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": reset_authorization,
                "password": "miPrimerPassword1",
                "confirm_password": "miPrimerPassword1",
            },
        )
        assert reset_response.status_code == 200

        login_response = client.post(
            "/api/login",
            json={"email": "googleonly@example.com", "password": "miPrimerPassword1"},
        )
        assert login_response.status_code == 200
