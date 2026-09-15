# Pruebas de integración de POST /api/forgot-password y POST
# /api/reset-password (ADR-009-password-reset-and-email-verification.md)
# contra PostgreSQL 16 real (thers_test, ver conftest.py) -- no mocks.
#
# El token crudo nunca lo devuelve la API (viaja únicamente dentro del
# enlace del correo, que en el entorno de test nunca se envía de verdad --
# RESEND_API_KEY no está definida, así que se usa NullEmailSender). Para
# probar POST /api/reset-password de punta a punta, estas pruebas insertan
# el token directamente en la base con las mismas funciones de dominio que
# usa el caso de uso real (generate_raw_token/hash_token) -- no se inventa
# ningún atajo que el código de producción no tenga.

import uuid
from datetime import datetime, timedelta, timezone

from app.domain.auth.token_generator import generate_raw_token, hash_token
from app.extensions import db
from app.infrastructure.persistence.models import PasswordResetToken, User

VALID_PASSWORD = "secretpass"
NEW_PASSWORD = "brandnewpass123"


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


def _create_reset_token(app, user_id, minutes_until_expiry=30, used=False):
    raw_token = generate_raw_token()
    with app.app_context():
        token = PasswordResetToken(
            user_id=uuid.UUID(user_id),
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=minutes_until_expiry),
            used_at=datetime.now(timezone.utc) if used else None,
        )
        db.session.add(token)
        db.session.commit()
    return raw_token


class TestForgotPassword:
    def test_existing_email_returns_generic_message_and_creates_token(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]

        response = client.post("/api/forgot-password", json={"email": "ada@example.com"})

        assert response.status_code == 200
        assert "instrucciones" in response.get_json()["msg"].lower()

        with app.app_context():
            tokens = db.session.query(PasswordResetToken).filter_by(user_id=uuid.UUID(user_id)).all()
            assert len(tokens) == 1
            assert tokens[0].used_at is None

    def test_nonexistent_email_returns_same_generic_message(self, client):
        response = client.post(
            "/api/forgot-password", json={"email": "nobody@example.com"}
        )

        assert response.status_code == 200
        assert "instrucciones" in response.get_json()["msg"].lower()

    def test_existing_and_nonexistent_email_return_identical_response(self, client):
        # FASE 4: no debe ser posible distinguir un email registrado de uno
        # que no lo está a partir de la respuesta.
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

    def test_repeated_request_within_cooldown_does_not_duplicate_token(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]

        client.post("/api/forgot-password", json={"email": "ada@example.com"})
        client.post("/api/forgot-password", json={"email": "ada@example.com"})

        with app.app_context():
            tokens = db.session.query(PasswordResetToken).filter_by(user_id=uuid.UUID(user_id)).all()
            assert len(tokens) == 1


class TestResetPassword:
    def test_valid_token_updates_password(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_token = _create_reset_token(app, user_id)

        response = client.post(
            "/api/reset-password",
            json={
                "token": raw_token,
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

    def test_token_is_single_use(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_token = _create_reset_token(app, user_id)

        first = client.post(
            "/api/reset-password",
            json={"token": raw_token, "password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )
        second = client.post(
            "/api/reset-password",
            json={"token": raw_token, "password": "anotherpass1", "confirm_password": "anotherpass1"},
        )

        assert first.status_code == 200
        assert second.status_code == 400

    def test_expired_token_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_token = _create_reset_token(app, user_id, minutes_until_expiry=-1)

        response = client.post(
            "/api/reset-password",
            json={"token": raw_token, "password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )

        assert response.status_code == 400

    def test_already_used_token_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_token = _create_reset_token(app, user_id, used=True)

        response = client.post(
            "/api/reset-password",
            json={"token": raw_token, "password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )

        assert response.status_code == 400

    def test_garbage_token_returns_400(self, client):
        response = client.post(
            "/api/reset-password",
            json={
                "token": "not-a-real-token",
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )
        assert response.status_code == 400

    def test_password_mismatch_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_token = _create_reset_token(app, user_id)

        response = client.post(
            "/api/reset-password",
            json={"token": raw_token, "password": NEW_PASSWORD, "confirm_password": "different"},
        )

        assert response.status_code == 400

    def test_password_too_short_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_token = _create_reset_token(app, user_id)

        response = client.post(
            "/api/reset-password",
            json={"token": raw_token, "password": "short", "confirm_password": "short"},
        )

        assert response.status_code == 400

    def test_missing_fields_returns_400(self, client):
        response = client.post("/api/reset-password", json={"token": "x"})
        assert response.status_code == 400

    def test_successful_reset_invalidates_other_outstanding_tokens(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        token_a = _create_reset_token(app, user_id)
        token_b = _create_reset_token(app, user_id)

        used = client.post(
            "/api/reset-password",
            json={"token": token_a, "password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )
        assert used.status_code == 200

        still_outstanding = client.post(
            "/api/reset-password",
            json={"token": token_b, "password": "yetanotherpass1", "confirm_password": "yetanotherpass1"},
        )
        assert still_outstanding.status_code == 400

    def test_reset_does_not_change_username_or_email(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        raw_token = _create_reset_token(app, user_id)

        client.post(
            "/api/reset-password",
            json={"token": raw_token, "password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )

        with app.app_context():
            user = db.session.get(User, user_id)
            assert user.email == "ada@example.com"
            assert user.username == "ada_lovelace"
            assert user.password_hash != NEW_PASSWORD
