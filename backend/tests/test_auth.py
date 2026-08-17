# Pruebas de integración de /api/register y /api/login contra PostgreSQL 16
# real (thers_test, ver conftest.py). Verifican, contra la base de datos real:
# - el id lo genera PostgreSQL (gen_random_uuid()), nunca uuid.uuid4() en Python;
# - el email es único e insensible a mayúsculas (CITEXT);
# - password_hash nunca es la contraseña en texto plano;
# - el identity del JWT es el id (UUID) del usuario, no su email.

import uuid

from flask_jwt_extended import decode_token

from app.extensions import db
from app.infrastructure.persistence.models import User


def _register(client, name="Ada Lovelace", email="ada@example.com", password="secretpass"):
    return client.post(
        "/api/register",
        json={"name": name, "email": email, "password": password},
    )


class TestRegister:
    def test_register_persists_user_with_postgres_generated_uuid(self, app, client):
        response = _register(client)

        assert response.status_code == 201
        body = response.get_json()["user"]
        assert body["email"] == "ada@example.com"
        assert body["name"] == "Ada Lovelace"

        user_id = uuid.UUID(body["id"])  # no lanza si es un UUID válido

        with app.app_context():
            user = db.session.get(User, user_id)
            assert user is not None
            assert user.email == "ada@example.com"
            # nunca se guarda la contraseña en claro
            assert user.password_hash != "secretpass"
            assert user.password_hash.startswith("scrypt:")

    def test_register_duplicate_email_returns_409(self, client):
        first = _register(client, email="dup@example.com")
        assert first.status_code == 201

        second = _register(client, name="Otra Persona", email="dup@example.com", password="otrapass")

        assert second.status_code == 409
        assert "msg" in second.get_json()

    def test_register_duplicate_email_is_case_insensitive(self, client):
        first = _register(client, email="ada@example.com")
        assert first.status_code == 201

        second = _register(client, email="ADA@EXAMPLE.COM")

        assert second.status_code == 409

    def test_register_missing_fields_returns_400(self, client):
        response = client.post("/api/register", json={"name": "Sin Datos"})

        assert response.status_code == 400

    def test_register_empty_body_returns_400(self, client):
        response = client.post("/api/register", data="", content_type="application/json")

        assert response.status_code == 400

    def test_register_response_never_exposes_password_hash(self, client):
        response = _register(client)

        assert "password_hash" not in response.get_json()["user"]
        assert "password" not in response.get_json()["user"]


class TestLogin:
    def test_login_with_correct_credentials_returns_token(self, client):
        _register(client, email="ada@example.com", password="secretpass")

        response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": "secretpass"}
        )

        assert response.status_code == 200
        body = response.get_json()
        assert "token" in body
        assert body["user"]["email"] == "ada@example.com"

    def test_login_email_is_case_insensitive(self, client):
        _register(client, email="ada@example.com", password="secretpass")

        response = client.post(
            "/api/login", json={"email": "ADA@EXAMPLE.COM", "password": "secretpass"}
        )

        assert response.status_code == 200

    def test_login_jwt_identity_is_user_uuid_not_email(self, app, client):
        register_response = _register(client, email="ada@example.com", password="secretpass")
        user_id = register_response.get_json()["user"]["id"]

        login_response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": "secretpass"}
        )
        token = login_response.get_json()["token"]

        with app.app_context():
            decoded = decode_token(token)

        assert decoded["sub"] == user_id
        assert decoded["sub"] != "ada@example.com"
        uuid.UUID(decoded["sub"])  # no lanza si es un UUID válido

    def test_login_wrong_password_returns_401(self, client):
        _register(client, email="ada@example.com", password="secretpass")

        response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": "wrong-password"}
        )

        assert response.status_code == 401

    def test_login_nonexistent_user_returns_401(self, client):
        response = client.post(
            "/api/login", json={"email": "nadie@example.com", "password": "whatever"}
        )

        assert response.status_code == 401

    def test_login_nonexistent_user_and_wrong_password_return_same_message(self, client):
        # No debe ser posible enumerar emails registrados a partir del mensaje de error.
        _register(client, email="ada@example.com", password="secretpass")

        wrong_password = client.post(
            "/api/login", json={"email": "ada@example.com", "password": "wrong"}
        )
        nonexistent_user = client.post(
            "/api/login", json={"email": "nadie@example.com", "password": "wrong"}
        )

        assert wrong_password.get_json() == nonexistent_user.get_json()

    def test_login_missing_fields_returns_400(self, client):
        response = client.post("/api/login", json={"email": "ada@example.com"})

        assert response.status_code == 400
