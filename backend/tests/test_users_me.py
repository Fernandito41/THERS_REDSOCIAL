# Pruebas de integración de GET /api/users/me (ADR-002 §3 —
# docs/architecture/ADR-002-user-profile-fields.md), el primer endpoint
# protegido del backend. Corren contra PostgreSQL 16 real (thers_test, ver
# conftest.py), no contra mocks.

import uuid
from datetime import timedelta

from flask_jwt_extended import create_access_token

from tests.test_auth import _register_payload

VALID_PASSWORD = "secretpass"


def _register_and_login(client, **overrides):
    overrides.setdefault("password", VALID_PASSWORD)
    overrides.setdefault("confirm_password", VALID_PASSWORD)
    register_response = client.post("/api/register", json=_register_payload(**overrides))
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/login",
        json={"email": overrides.get("email", "ada@example.com"), "password": VALID_PASSWORD},
    )
    assert login_response.status_code == 200

    return login_response.get_json()["token"], register_response.get_json()["user"]


class TestGetCurrentUser:
    def test_valid_token_returns_200_with_user(self, client):
        token, registered_user = _register_and_login(client)

        response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.get_json()["user"]["id"] == registered_user["id"]

    def test_missing_token_returns_401(self, client):
        response = client.get("/api/users/me")

        assert response.status_code == 401
        assert "msg" in response.get_json()

    def test_invalid_token_returns_401(self, client):
        response = client.get(
            "/api/users/me", headers={"Authorization": "Bearer not-a-real-token"}
        )

        assert response.status_code == 401
        assert "msg" in response.get_json()

    def test_expired_token_returns_401(self, app, client):
        _register_and_login(client)

        with app.app_context():
            expired_token = create_access_token(
                identity="00000000-0000-0000-0000-000000000000",
                expires_delta=timedelta(seconds=-1),
            )

        response = client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "msg" in response.get_json()

    def test_nonexistent_user_returns_404(self, app, client):
        # Token válido (firma correcta, no expirado) pero cuyo `sub` no
        # corresponde a ningún usuario real -- p. ej. la cuenta fue borrada
        # después de emitirse el token.
        with app.app_context():
            token = create_access_token(identity=str(uuid.uuid4()))

        response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 404
        assert "msg" in response.get_json()

    def test_response_contains_expected_public_fields(self, client):
        token, _ = _register_and_login(client)

        response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        user = response.get_json()["user"]

        for field in ("id", "username", "email", "name", "phone", "country_code", "birth_date"):
            assert field in user

    def test_response_never_exposes_sensitive_fields(self, client):
        token, _ = _register_and_login(client)

        response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        body = response.get_json()

        for forbidden in ("password", "password_hash", "confirm_password", "token", "secret"):
            assert forbidden not in body["user"]
            assert forbidden not in body
