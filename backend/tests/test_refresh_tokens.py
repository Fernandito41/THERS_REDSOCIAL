# Pruebas de integración de refresh tokens rotativos (ADR-017-jwt-session-policy.md)
# contra PostgreSQL 16 real (thers_test, ver conftest.py). Cubren las pruebas
# obligatorias de ADR-017 §4.8:
# - refresh válido renueva;
# - refresh rotado y reusado revoca la familia;
# - refresh expirado rechaza;
# - un access token no sirve para renovar (ni un refresh como access);
# - logout invalida;
# más: carrera real de dos renovaciones simultáneas, Google, varias sesiones
# independientes, cambio de contraseña y que nunca se guarde el token en claro.

import threading
import uuid
from datetime import datetime, timedelta, timezone

from flask_jwt_extended import create_refresh_token, decode_token

from app.domain.auth.token_generator import hash_token
from app.extensions import db
from app.infrastructure.persistence.models import RefreshToken, User
from tests.conftest import mark_email_verified
from tests.test_auth import _register_payload
from tests.test_google_auth import _mock_google_identity
from tests.test_password_reset import NEW_PASSWORD, _create_verified_request

VALID_PASSWORD = "secretpass"


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def _register_verified(client, **overrides):
    overrides.setdefault("password", VALID_PASSWORD)
    overrides.setdefault("confirm_password", VALID_PASSWORD)
    response = client.post("/api/register", json=_register_payload(**overrides))
    assert response.status_code == 201
    user_id = response.get_json()["user"]["id"]
    mark_email_verified(user_id)
    return user_id


def _login(client, email="ada@example.com"):
    response = client.post("/api/login", json={"email": email, "password": VALID_PASSWORD})
    assert response.status_code == 200
    return response.get_json()


def _claims(app, token):
    with app.app_context():
        return decode_token(token)


def _refresh(client, refresh_token):
    return client.post("/api/refresh", headers=_bearer(refresh_token))


class TestLoginIssuesSession:
    def test_login_returns_access_refresh_and_user(self, app, client):
        _register_verified(client)

        body = _login(client)

        assert set(body) == {"token", "refresh_token", "user"}
        assert body["token"] != body["refresh_token"]
        assert _claims(app, body["token"])["type"] == "access"
        assert _claims(app, body["refresh_token"])["type"] == "refresh"

    def test_refresh_token_is_never_stored_in_clear(self, app, client):
        _register_verified(client)
        refresh_token = _login(client)["refresh_token"]
        jti = _claims(app, refresh_token)["jti"]

        with app.app_context():
            rows = db.session.query(RefreshToken).all()

        assert len(rows) == 1
        # Se guarda el SHA-256 del jti: ni el token ni su jti en claro.
        assert rows[0].token_hash == hash_token(jti)
        assert rows[0].token_hash not in (refresh_token, jti)
        assert refresh_token not in repr(rows[0].__dict__)

    def test_access_and_refresh_lifetimes_are_explicit(self, app):
        assert app.config["JWT_ACCESS_TOKEN_EXPIRES"] == timedelta(minutes=15)
        assert app.config["JWT_REFRESH_TOKEN_EXPIRES"] == timedelta(days=30)

    def test_google_login_also_returns_a_refresh_token(self, app, client, monkeypatch):
        _mock_google_identity(monkeypatch, sub="g-r1", email="google@example.com")

        response = client.post("/api/auth/google", json={"credential": "x"})

        assert response.status_code == 200
        body = response.get_json()
        assert _claims(app, body["refresh_token"])["type"] == "refresh"
        assert _refresh(client, body["refresh_token"]).status_code == 200


class TestRefresh:
    def test_valid_refresh_issues_new_working_tokens(self, client):
        _register_verified(client)
        first = _login(client)

        response = _refresh(client, first["refresh_token"])

        assert response.status_code == 200
        body = response.get_json()
        assert set(body) == {"token", "refresh_token"}
        assert body["refresh_token"] != first["refresh_token"]
        me = client.get("/api/users/me", headers=_bearer(body["token"]))
        assert me.status_code == 200
        assert me.get_json()["user"]["email"] == "ada@example.com"

    def test_rotation_chain_keeps_working(self, client):
        _register_verified(client)
        token = _login(client)["refresh_token"]

        for _ in range(3):
            response = _refresh(client, token)
            assert response.status_code == 200
            token = response.get_json()["refresh_token"]

    def test_reusing_a_rotated_refresh_revokes_the_whole_family(self, client):
        _register_verified(client)
        first = _login(client)["refresh_token"]
        second = _refresh(client, first).get_json()["refresh_token"]

        reuse = _refresh(client, first)

        assert reuse.status_code == 401
        # La familia entera quedó cortada: el sucesor legítimo ya no sirve.
        assert _refresh(client, second).status_code == 401

    def test_reuse_marks_every_row_of_the_family_revoked(self, app, client):
        _register_verified(client)
        first = _login(client)["refresh_token"]
        _refresh(client, first)
        _refresh(client, first)  # reuso

        with app.app_context():
            rows = db.session.query(RefreshToken).all()

        assert len(rows) == 2
        assert all(row.revoked_at is not None for row in rows)

    def test_expired_refresh_jwt_is_rejected(self, app, client):
        user_id = _register_verified(client)
        with app.app_context():
            expired = create_refresh_token(
                identity=user_id,
                additional_claims={"fid": str(uuid.uuid4())},
                expires_delta=timedelta(seconds=-1),
            )

        assert _refresh(client, expired).status_code == 401

    def test_refresh_expired_in_database_is_rejected(self, app, client):
        _register_verified(client)
        refresh_token = _login(client)["refresh_token"]
        with app.app_context():
            db.session.query(RefreshToken).update(
                {"expires_at": datetime.now(timezone.utc) - timedelta(seconds=5)}
            )
            db.session.commit()

        assert _refresh(client, refresh_token).status_code == 401

    def test_unregistered_but_validly_signed_refresh_is_rejected(self, app, client):
        user_id = _register_verified(client)
        with app.app_context():
            forged = create_refresh_token(
                identity=user_id, additional_claims={"fid": str(uuid.uuid4())}
            )

        assert _refresh(client, forged).status_code == 401

    def test_refresh_without_token_is_401(self, client):
        assert client.post("/api/refresh").status_code == 401

    def test_refresh_for_deleted_user_is_rejected(self, app, client):
        user_id = _register_verified(client)
        refresh_token = _login(client)["refresh_token"]
        with app.app_context():
            db.session.delete(db.session.get(User, uuid.UUID(user_id)))
            db.session.commit()

        assert _refresh(client, refresh_token).status_code == 401


class TestTokenTypesAreNotInterchangeable:
    def test_access_token_cannot_refresh(self, client):
        _register_verified(client)
        access = _login(client)["token"]

        assert _refresh(client, access).status_code == 401

    def test_refresh_token_cannot_call_protected_endpoints(self, client):
        _register_verified(client)
        refresh_token = _login(client)["refresh_token"]

        response = client.get("/api/users/me", headers=_bearer(refresh_token))

        assert response.status_code == 401

    def test_access_token_cannot_logout(self, client):
        _register_verified(client)
        access = _login(client)["token"]

        assert client.post("/api/logout", headers=_bearer(access)).status_code == 401


class TestLogout:
    def test_logout_invalidates_the_refresh_token(self, client):
        _register_verified(client)
        refresh_token = _login(client)["refresh_token"]

        logout = client.post("/api/logout", headers=_bearer(refresh_token))

        assert logout.status_code == 200
        assert _refresh(client, refresh_token).status_code == 401

    def test_logout_also_kills_the_rotated_successor(self, client):
        _register_verified(client)
        first = _login(client)["refresh_token"]
        second = _refresh(client, first).get_json()["refresh_token"]

        assert client.post("/api/logout", headers=_bearer(second)).status_code == 200
        assert _refresh(client, second).status_code == 401

    def test_logout_is_idempotent(self, client):
        _register_verified(client)
        refresh_token = _login(client)["refresh_token"]

        assert client.post("/api/logout", headers=_bearer(refresh_token)).status_code == 200
        assert client.post("/api/logout", headers=_bearer(refresh_token)).status_code == 200

    def test_logout_without_token_is_401(self, client):
        assert client.post("/api/logout").status_code == 401


class TestIndependentSessions:
    def test_logging_out_one_device_does_not_affect_another(self, client):
        _register_verified(client)
        device_a = _login(client)["refresh_token"]
        device_b = _login(client)["refresh_token"]

        client.post("/api/logout", headers=_bearer(device_a))

        assert _refresh(client, device_a).status_code == 401
        assert _refresh(client, device_b).status_code == 200

    def test_each_login_opens_its_own_family(self, app, client):
        _register_verified(client)
        _login(client)
        _login(client)

        with app.app_context():
            families = {row.family_id for row in db.session.query(RefreshToken).all()}

        assert len(families) == 2


class TestPasswordResetRevokesSessions:
    def test_resetting_the_password_revokes_all_refresh_tokens(self, app, client):
        user_id = _register_verified(client)
        device_a = _login(client)["refresh_token"]
        device_b = _login(client)["refresh_token"]
        authorization = _create_verified_request(app, user_id)

        reset = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": authorization,
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )

        assert reset.status_code == 200
        assert _refresh(client, device_a).status_code == 401
        assert _refresh(client, device_b).status_code == 401


class TestConcurrentRotation:
    def test_two_simultaneous_refreshes_of_the_same_token_yield_one_success(self, app, client):
        _register_verified(client)
        refresh_token = _login(client)["refresh_token"]
        barrier = threading.Barrier(2)
        statuses = []

        def attempt():
            thread_client = app.test_client()
            barrier.wait()
            statuses.append(_refresh(thread_client, refresh_token).status_code)

        threads = [threading.Thread(target=attempt) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Nunca dos sucesores (ADR-017 §4.3): uno gana, el otro es un reuso.
        assert sorted(statuses) == [200, 401]

        with app.app_context():
            active = (
                db.session.query(RefreshToken)
                .filter(RefreshToken.used_at.is_(None), RefreshToken.revoked_at.is_(None))
                .count()
            )
        assert active == 0  # el reuso revocó la familia; no queda ningún activo


class TestAuthenticatedResponsesAreNotCacheable:
    def test_authenticated_response_has_no_store(self, client):
        _register_verified(client)
        access = _login(client)["token"]

        response = client.get("/api/users/me", headers=_bearer(access))

        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "no-store"

    def test_unauthenticated_rejection_is_also_not_cached_when_a_token_was_sent(self, client):
        response = client.get("/api/users/me", headers=_bearer("basura"))

        assert response.status_code == 401
        assert response.headers["Cache-Control"] == "no-store"

    def test_requests_without_authorization_are_left_alone(self, client):
        response = client.post("/api/login", json={"email": "nadie@example.com", "password": "x"})

        assert "Cache-Control" not in response.headers
