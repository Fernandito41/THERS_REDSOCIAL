# Pruebas de integración de GET /api/users/me (ADR-002 §3 —
# docs/architecture/ADR-002-user-profile-fields.md), el primer endpoint
# protegido del backend. Corren contra PostgreSQL 16 real (thers_test, ver
# conftest.py), no contra mocks.

import uuid
from datetime import timedelta

from flask_jwt_extended import create_access_token

from tests.conftest import mark_email_verified
from tests.test_auth import _register_payload

VALID_PASSWORD = "secretpass"


def _register_and_login(client, **overrides):
    overrides.setdefault("password", VALID_PASSWORD)
    overrides.setdefault("confirm_password", VALID_PASSWORD)
    register_response = client.post("/api/register", json=_register_payload(**overrides))
    assert register_response.status_code == 201
    mark_email_verified(register_response.get_json()["user"]["id"])

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

    def test_token_without_a_registered_session_returns_401(self, app, client):
        # Token válido (firma correcta, no expirado) pero emitido sin pasar por
        # `POST /api/login`, así que no tiene fila en `sessions`.
        #
        # **Antes de ADR-025-session-registry.md esto devolvía 404**: el JWT era
        # puramente stateless, llegaba a la route y ahí se descubría que su `sub`
        # no correspondía a ningún usuario. Desde el registro de sesiones, un
        # token sin sesión viva ya no autentica nada y se rechaza con 401 antes
        # de llegar al handler -- que es precisamente lo que hace posible
        # "cerrar sesión en ese dispositivo".
        #
        # Efecto colateral honesto: la rama 404 de GET /api/users/me quedó
        # **inalcanzable en la práctica**. `sessions.user_id` es una FK con
        # ON DELETE CASCADE, así que si la cuenta se borra su sesión se borra
        # con ella y el token cae en este mismo 401. La rama se conserva en el
        # código como defensa, no porque haya un camino que la produzca
        # (ADR-025 §Consecuencias).
        with app.app_context():
            token = create_access_token(identity=str(uuid.uuid4()))

        response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 401
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
