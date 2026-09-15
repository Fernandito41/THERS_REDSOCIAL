# Pruebas de integración de POST /api/send-verification-email (protegido) y
# POST /api/verify-email (público) --
# ADR-009-password-reset-and-email-verification.md -- contra PostgreSQL 16
# real (thers_test, ver conftest.py). Mismo criterio que
# test_password_reset.py para obtener el token crudo en las pruebas de
# consumo: se inserta directamente con las funciones de dominio reales
# (generate_raw_token/hash_token), ya que la API nunca lo devuelve.

import uuid
from datetime import datetime, timedelta, timezone

from app.domain.auth.token_generator import generate_raw_token, hash_token
from app.extensions import db
from app.infrastructure.persistence.models import EmailVerificationToken

VALID_PASSWORD = "secretpass"


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


def _register_and_login(client, **overrides):
    payload = _register_payload(**overrides)
    res = client.post("/api/register", json=payload)
    user_id = res.get_json()["user"]["id"]
    res = client.post(
        "/api/login", json={"email": payload["email"], "password": VALID_PASSWORD}
    )
    return res.get_json()["token"], user_id


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _create_verification_token(app, user_id, hours_until_expiry=24, used=False):
    raw_token = generate_raw_token()
    with app.app_context():
        token = EmailVerificationToken(
            user_id=uuid.UUID(user_id),
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=hours_until_expiry),
            used_at=datetime.now(timezone.utc) if used else None,
        )
        db.session.add(token)
        db.session.commit()
    return raw_token


class TestSendVerificationEmail:
    def test_new_user_is_unverified(self, client):
        token, _ = _register_and_login(client)

        response = client.get("/api/users/me", headers=_auth_headers(token))

        assert response.get_json()["user"]["email_verified"] is False

    def test_sends_verification_and_creates_token(self, app, client):
        token, user_id = _register_and_login(client)

        response = client.post(
            "/api/send-verification-email", headers=_auth_headers(token)
        )

        assert response.status_code == 200
        with app.app_context():
            tokens = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=uuid.UUID(user_id))
                .all()
            )
            assert len(tokens) == 1

    def test_without_token_returns_401(self, client):
        response = client.post("/api/send-verification-email")
        assert response.status_code == 401

    def test_repeated_request_within_cooldown_does_not_duplicate_token(self, app, client):
        token, user_id = _register_and_login(client)

        client.post("/api/send-verification-email", headers=_auth_headers(token))
        client.post("/api/send-verification-email", headers=_auth_headers(token))

        with app.app_context():
            tokens = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=uuid.UUID(user_id))
                .all()
            )
            assert len(tokens) == 1

    def test_already_verified_user_does_not_create_new_token(self, app, client):
        token, user_id = _register_and_login(client)
        verify_token = _create_verification_token(app, user_id)
        client.post("/api/verify-email", json={"token": verify_token})

        response = client.post(
            "/api/send-verification-email", headers=_auth_headers(token)
        )

        assert response.status_code == 200
        assert "ya está verificado" in response.get_json()["msg"].lower()
        with app.app_context():
            tokens = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=uuid.UUID(user_id))
                .all()
            )
            assert len(tokens) == 1  # solo la que ya existía, ninguna nueva


class TestVerifyEmail:
    def test_valid_token_marks_email_verified(self, app, client):
        token, user_id = _register_and_login(client)
        verify_token = _create_verification_token(app, user_id)

        response = client.post("/api/verify-email", json={"token": verify_token})

        assert response.status_code == 200
        assert response.get_json()["email_verified"] is True

        me = client.get("/api/users/me", headers=_auth_headers(token))
        assert me.get_json()["user"]["email_verified"] is True

    def test_token_is_single_use(self, app, client):
        _, user_id = _register_and_login(client)
        verify_token = _create_verification_token(app, user_id)

        first = client.post("/api/verify-email", json={"token": verify_token})
        second = client.post("/api/verify-email", json={"token": verify_token})

        assert first.status_code == 200
        assert second.status_code == 400

    def test_expired_token_returns_400(self, app, client):
        _, user_id = _register_and_login(client)
        verify_token = _create_verification_token(app, user_id, hours_until_expiry=-1)

        response = client.post("/api/verify-email", json={"token": verify_token})

        assert response.status_code == 400

    def test_already_used_token_returns_400(self, app, client):
        _, user_id = _register_and_login(client)
        verify_token = _create_verification_token(app, user_id, used=True)

        response = client.post("/api/verify-email", json={"token": verify_token})

        assert response.status_code == 400

    def test_garbage_token_returns_400(self, client):
        response = client.post("/api/verify-email", json={"token": "not-a-real-token"})
        assert response.status_code == 400

    def test_missing_token_returns_400(self, client):
        response = client.post("/api/verify-email", json={})
        assert response.status_code == 400

    def test_empty_body_returns_400(self, client):
        response = client.post("/api/verify-email")
        assert response.status_code == 400

    def test_does_not_require_authentication(self, app, client):
        _, user_id = _register_and_login(client)
        verify_token = _create_verification_token(app, user_id)

        # Sin header Authorization -- verificar el email no exige sesión
        # iniciada en este navegador/dispositivo (ADR-009 §Contrato API).
        response = client.post("/api/verify-email", json={"token": verify_token})

        assert response.status_code == 200
