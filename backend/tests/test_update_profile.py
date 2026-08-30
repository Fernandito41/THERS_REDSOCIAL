# Pruebas de integración de PATCH /api/users/me (ADR-003 —
# docs/architecture/ADR-003-profile-update-contract.md). Corren contra
# PostgreSQL 16 real (thers_test, ver conftest.py), no contra mocks --
# mismo patrón que test_auth.py/test_users_me.py. Reutiliza
# `_register_and_login` de test_users_me.py en vez de duplicarlo.

from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.infrastructure.persistence.models import User
from tests.test_users_me import _register_and_login


def _patch(client, token, payload):
    return client.patch(
        "/api/users/me",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )


class TestAuthentication:
    def test_patch_without_jwt_returns_401(self, client):
        response = client.patch("/api/users/me", json={"name": "Fernando"})

        assert response.status_code == 401
        assert "msg" in response.get_json()


class TestUpdate:
    def test_update_name(self, client):
        token, user = _register_and_login(client)

        response = _patch(client, token, {"name": "Fernando"})

        assert response.status_code == 200
        body = response.get_json()["user"]
        assert body["name"] == "Fernando"
        assert body["username"] == user["username"]

    def test_update_username(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"username": "nuevo_username"})

        assert response.status_code == 200
        assert response.get_json()["user"]["username"] == "nuevo_username"

    def test_partial_update_only_touches_sent_field(self, client):
        token, user = _register_and_login(client)

        response = _patch(client, token, {"name": "Solo Nombre"})

        body = response.get_json()["user"]
        assert body["name"] == "Solo Nombre"
        assert body["username"] == user["username"]
        assert body["phone"] == user["phone"]
        assert body["country_code"] == user["country_code"]
        assert body["birth_date"] == user["birth_date"]

    def test_persistence_survives_a_new_request(self, client):
        token, _ = _register_and_login(client)

        patch_response = _patch(client, token, {"name": "Persistido"})
        assert patch_response.status_code == 200

        get_response = client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert get_response.get_json()["user"]["name"] == "Persistido"


class TestSecurity:
    def test_id_and_password_hash_are_not_mass_assignable(self, app, client):
        token, user = _register_and_login(client)

        response = _patch(
            client,
            token,
            {"id": "11111111-1111-1111-1111-111111111111", "password_hash": "hacked"},
        )

        # Ningún campo whitelisted presente en el body -> 400, nunca un 200
        # silencioso que sugiera que algo se aplicó (ADR-003 §Contrato PATCH).
        assert response.status_code == 400

        with app.app_context():
            db_user = db.session.get(User, user["id"])
            assert str(db_user.id) == user["id"]
            assert db_user.password_hash != "hacked"

    def test_response_never_exposes_password_hash(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"name": "Sin Hash"})

        body = response.get_json()
        assert "password_hash" not in body["user"]
        assert "password_hash" not in body


class TestValidation:
    def test_empty_body_returns_400(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {})

        assert response.status_code == 400

    def test_body_without_whitelisted_fields_returns_400(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"favorite_color": "blue"})

        assert response.status_code == 400

    def test_invalid_username_returns_400(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"username": "a?"})

        assert response.status_code == 400

    def test_invalid_phone_returns_400(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"phone": "123", "country_code": "+503"})

        assert response.status_code == 400

    def test_invalid_country_code_returns_400(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"phone": "7000-1234", "country_code": "503"})

        assert response.status_code == 400

    def test_invalid_birth_date_returns_400(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"birth_date": "not-a-date"})

        assert response.status_code == 400

    def test_phone_without_country_code_returns_400(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"phone": "7000-1234"})

        assert response.status_code == 400

    def test_country_code_without_phone_returns_400(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"country_code": "+503"})

        assert response.status_code == 400


class TestUniqueness:
    def test_duplicate_username_returns_409(self, client):
        _, user_a = _register_and_login(client, email="a@example.com", username="user_a")
        token_b, _ = _register_and_login(client, email="b@example.com", username="user_b")

        response = _patch(client, token_b, {"username": user_a["username"]})

        assert response.status_code == 409
        assert "msg" in response.get_json()


class TestUsernameCooldown:
    def test_first_change_is_allowed(self, client):
        token, _ = _register_and_login(client)

        response = _patch(client, token, {"username": "primer_cambio"})

        assert response.status_code == 200
        assert response.get_json()["user"]["username"] == "primer_cambio"

    def test_second_change_within_30_days_is_rejected(self, client):
        token, _ = _register_and_login(client)

        first = _patch(client, token, {"username": "primer_cambio"})
        assert first.status_code == 200

        second = _patch(client, token, {"username": "segundo_cambio"})

        assert second.status_code == 400
        assert "msg" in second.get_json()

    def test_change_after_cooldown_window_is_allowed(self, app, client):
        token, user = _register_and_login(client)

        first = _patch(client, token, {"username": "primer_cambio"})
        assert first.status_code == 200

        # Simula que el último cambio ocurrió hace más de 30 días
        # escribiendo directamente en la base de datos real (no un mock),
        # para no depender de esperar 30 días reales en el test.
        with app.app_context():
            db_user = db.session.get(User, user["id"])
            db_user.username_changed_at = datetime.now(timezone.utc) - timedelta(days=31)
            db.session.commit()

        second = _patch(client, token, {"username": "tercer_cambio"})

        assert second.status_code == 200
        assert second.get_json()["user"]["username"] == "tercer_cambio"


class TestSameUsername:
    def test_sending_current_username_is_not_treated_as_a_change(self, app, client):
        token, user = _register_and_login(client)

        response = _patch(client, token, {"username": user["username"]})

        assert response.status_code == 200
        assert response.get_json()["user"]["username"] == user["username"]

        with app.app_context():
            db_user = db.session.get(User, user["id"])
            assert db_user.username_changed_at is None

        # Al no contar como cambio real, no consume el cooldown -- un cambio
        # real inmediatamente después sigue permitido.
        follow_up = _patch(client, token, {"username": "cambio_real"})
        assert follow_up.status_code == 200
