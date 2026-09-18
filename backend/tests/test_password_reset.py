# Pruebas de integración de POST /api/forgot-password, POST
# /api/verify-reset-code y POST /api/reset-password
# (ADR-010-password-reset-otp-flow.md) contra PostgreSQL 16 real (thers_test,
# ver conftest.py) -- no mocks.
#
# El código OTP real y la autorización temporal nunca los devuelve la API
# (viajan por correo / se generan internamente tras verificar -- en el
# entorno de test nunca se envía nada de verdad, RESEND_API_KEY no está
# definida, se usa NullEmailSender). Para probar verify-reset-code/
# reset-password de punta a punta, estas pruebas insertan la solicitud
# directamente en la base con las mismas funciones de dominio que usa el
# código real (hash_password para el código, generate_raw_token/hash_token
# para la autorización) -- no se inventa ningún atajo que el código de
# producción no tenga. POST /api/forgot-password sí se prueba end-to-end de
# verdad (no hay forma de conocer el código que genera, así que sus propias
# pruebas se limitan a lo que se puede observar desde afuera: la respuesta y
# el estado en la base).

import uuid
from datetime import datetime, timedelta, timezone

from app.domain.auth.auth_service import hash_password
from app.domain.auth.token_generator import generate_raw_token, hash_token
from app.extensions import db
from app.infrastructure.persistence.models import PasswordResetToken, User
from tests.conftest import mark_email_verified

VALID_PASSWORD = "secretpass"
NEW_PASSWORD = "brandnewpass123"
KNOWN_CODE = "123456"


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


def _register(client, **overrides):
    return client.post("/api/register", json=_register_payload(**overrides))


def _create_code_request(
    app, user_id, code=KNOWN_CODE, minutes_until_expiry=10, attempts=0, used=False
):
    with app.app_context():
        request_row = PasswordResetToken(
            user_id=uuid.UUID(user_id),
            code_hash=hash_password(code),
            attempts=attempts,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=minutes_until_expiry),
            used_at=datetime.now(timezone.utc) if used else None,
        )
        db.session.add(request_row)
        db.session.commit()
        return str(request_row.id)


def _create_verified_request(app, user_id, minutes_until_expiry=10, used=False):
    raw_authorization = generate_raw_token()
    with app.app_context():
        request_row = PasswordResetToken(
            user_id=uuid.UUID(user_id),
            code_hash=hash_password(KNOWN_CODE),
            attempts=0,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            verified_at=datetime.now(timezone.utc),
            reset_authorization_hash=hash_token(raw_authorization),
            reset_authorization_expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=minutes_until_expiry),
            used_at=datetime.now(timezone.utc) if used else None,
        )
        db.session.add(request_row)
        db.session.commit()
    return raw_authorization


class TestForgotPassword:
    def test_existing_email_returns_generic_message_and_creates_request(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]

        response = client.post("/api/forgot-password", json={"email": "ada@example.com"})

        assert response.status_code == 200
        assert "código" in response.get_json()["msg"].lower()

        with app.app_context():
            requests = (
                db.session.query(PasswordResetToken).filter_by(user_id=uuid.UUID(user_id)).all()
            )
            assert len(requests) == 1
            assert requests[0].used_at is None
            assert requests[0].attempts == 0

    def test_nonexistent_email_returns_same_generic_message(self, client):
        response = client.post(
            "/api/forgot-password", json={"email": "nobody@example.com"}
        )

        assert response.status_code == 200
        assert "código" in response.get_json()["msg"].lower()

    def test_existing_and_nonexistent_email_return_identical_response(self, client):
        _register(client)

        existing = client.post("/api/forgot-password", json={"email": "ada@example.com"})
        nonexistent = client.post(
            "/api/forgot-password", json={"email": "nobody@example.com"}
        )

        assert existing.status_code == nonexistent.status_code == 200
        assert existing.get_json() == nonexistent.get_json()

    def test_invalid_email_format_returns_400(self, client):
        response = client.post("/api/forgot-password", json={"email": "not-an-email"})
        assert response.status_code == 400

    def test_missing_email_returns_400(self, client):
        response = client.post("/api/forgot-password", json={})
        assert response.status_code == 400

    def test_empty_body_returns_400(self, client):
        response = client.post("/api/forgot-password")
        assert response.status_code == 400

    def test_repeated_request_within_cooldown_does_not_duplicate_code(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]

        client.post("/api/forgot-password", json={"email": "ada@example.com"})
        client.post("/api/forgot-password", json={"email": "ada@example.com"})

        with app.app_context():
            requests = (
                db.session.query(PasswordResetToken).filter_by(user_id=uuid.UUID(user_id)).all()
            )
            assert len(requests) == 1

    def test_resend_after_cooldown_invalidates_previous_code(self, app, client):
        # Simula un "Reenviar código" fuera del cooldown insertando la
        # solicitud anterior ya vieja (created_at en el pasado) -- no hay
        # forma de esperar 60 segundos reales en la suite.
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        old_request_id = _create_code_request(app, user_id)
        with app.app_context():
            db.session.query(PasswordResetToken).filter_by(
                id=uuid.UUID(old_request_id)
            ).update({"created_at": datetime.now(timezone.utc) - timedelta(minutes=5)})
            db.session.commit()

        response = client.post("/api/forgot-password", json={"email": "ada@example.com"})
        assert response.status_code == 200

        with app.app_context():
            old_row = db.session.get(PasswordResetToken, uuid.UUID(old_request_id))
            assert old_row.used_at is not None  # invalidada

            active = (
                db.session.query(PasswordResetToken)
                .filter_by(user_id=uuid.UUID(user_id), used_at=None)
                .all()
            )
            assert len(active) == 1
            assert str(active[0].id) != old_request_id


class TestVerifyResetCode:
    def test_correct_code_returns_reset_authorization(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_code_request(app, user_id)

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )

        assert response.status_code == 200
        body = response.get_json()
        assert isinstance(body["reset_authorization"], str)
        assert len(body["reset_authorization"]) > 20

    def test_correct_code_marks_request_as_verified(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        request_id = _create_code_request(app, user_id)

        client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )

        with app.app_context():
            row = db.session.get(PasswordResetToken, uuid.UUID(request_id))
            assert row.verified_at is not None
            assert row.reset_authorization_hash is not None

    def test_wrong_code_returns_400_and_increments_attempts(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        request_id = _create_code_request(app, user_id)

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": "000000"}
        )

        assert response.status_code == 400
        assert "incorrecto" in response.get_json()["msg"].lower()
        with app.app_context():
            row = db.session.get(PasswordResetToken, uuid.UUID(request_id))
            assert row.attempts == 1

    def test_nonexistent_email_returns_same_400(self, client):
        response = client.post(
            "/api/verify-reset-code", json={"email": "nobody@example.com", "code": KNOWN_CODE}
        )
        assert response.status_code == 400

    def test_no_active_request_returns_400(self, client):
        _register(client)

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )

        assert response.status_code == 400

    def test_expired_code_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_code_request(app, user_id, minutes_until_expiry=-1)

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )

        assert response.status_code == 400

    def test_max_attempts_blocks_even_the_correct_code(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        # PASSWORD_RESET_MAX_ATTEMPTS = 5 (domain/auth/token_policy.py)
        _create_code_request(app, user_id, attempts=5)

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )

        assert response.status_code == 400

    def test_brute_force_exhausts_attempts_then_blocks_correct_code(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_code_request(app, user_id)

        for _ in range(5):
            client.post(
                "/api/verify-reset-code", json={"email": "ada@example.com", "code": "000000"}
            )

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )
        assert response.status_code == 400

    def test_used_request_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_code_request(app, user_id, used=True)

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )

        assert response.status_code == 400

    def test_missing_email_returns_400(self, client):
        response = client.post("/api/verify-reset-code", json={"code": KNOWN_CODE})
        assert response.status_code == 400

    def test_missing_code_returns_400(self, client):
        response = client.post("/api/verify-reset-code", json={"email": "ada@example.com"})
        assert response.status_code == 400

    def test_empty_body_returns_400(self, client):
        response = client.post("/api/verify-reset-code")
        assert response.status_code == 400

    def test_does_not_require_authentication(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_code_request(app, user_id)

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )

        assert response.status_code == 200


class TestResetPassword:
    def test_valid_authorization_updates_password(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        mark_email_verified(user_id)
        raw_authorization = _create_verified_request(app, user_id)

        response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )

        assert response.status_code == 200

        old_login = client.post(
            "/api/login", json={"email": "ada@example.com", "password": VALID_PASSWORD}
        )
        assert old_login.status_code == 401

        new_login = client.post(
            "/api/login", json={"email": "ada@example.com", "password": NEW_PASSWORD}
        )
        assert new_login.status_code == 200

    def test_authorization_is_single_use(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_authorization = _create_verified_request(app, user_id)

        first = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )
        second = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": "anotherpass1",
                "confirm_password": "anotherpass1",
            },
        )

        assert first.status_code == 200
        assert second.status_code == 400

    def test_expired_authorization_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_authorization = _create_verified_request(app, user_id, minutes_until_expiry=-1)

        response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )

        assert response.status_code == 400

    def test_unverified_request_cannot_be_used(self, app, client):
        # Defensivo: una fila con código creado pero NUNCA verificado
        # (verified_at NULL) no debe poder consumirse aunque alguien
        # adivinara un valor de reset_authorization -- en la práctica
        # imposible sin verificar primero, find_valid_by_reset_authorization_hash
        # exige verified_at IS NOT NULL.
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_authorization = generate_raw_token()
        with app.app_context():
            row = PasswordResetToken(
                user_id=uuid.UUID(user_id),
                code_hash=hash_password(KNOWN_CODE),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
                reset_authorization_hash=hash_token(raw_authorization),
                reset_authorization_expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            )
            db.session.add(row)
            db.session.commit()

        response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )

        assert response.status_code == 400

    def test_garbage_authorization_returns_400(self, client):
        response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": "not-a-real-authorization",
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )
        assert response.status_code == 400

    def test_password_mismatch_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_authorization = _create_verified_request(app, user_id)

        response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": NEW_PASSWORD,
                "confirm_password": "different",
            },
        )

        assert response.status_code == 400

    def test_password_too_short_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_authorization = _create_verified_request(app, user_id)

        response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": "short",
                "confirm_password": "short",
            },
        )

        assert response.status_code == 400

    def test_missing_fields_returns_400(self, client):
        response = client.post("/api/reset-password", json={"reset_authorization": "x"})
        assert response.status_code == 400

    def test_reset_does_not_change_username_or_email(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_authorization = _create_verified_request(app, user_id)

        client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )

        with app.app_context():
            user = db.session.get(User, uuid.UUID(user_id))
            assert user.email == "ada@example.com"
            assert user.username == "ada_lovelace"
            assert user.password_hash != NEW_PASSWORD


class TestFullOtpFlow:
    def test_verify_then_reset_end_to_end(self, app, client):
        # Simula el flujo completo tal como lo vive el Frontend, salvo el
        # paso de "leer el código del correo" (se inserta directamente con
        # un valor conocido, ver docstring del módulo).
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        mark_email_verified(user_id)
        _create_code_request(app, user_id)

        verify_response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )
        assert verify_response.status_code == 200
        reset_authorization = verify_response.get_json()["reset_authorization"]

        reset_response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": reset_authorization,
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )
        assert reset_response.status_code == 200

        login_response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": NEW_PASSWORD}
        )
        assert login_response.status_code == 200
