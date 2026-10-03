# Pruebas de integración de la aceptación de términos de uso
# (ADR-032-content-reports-and-moderation.md §5, fase 1) contra PostgreSQL real
# (ver conftest.py). Verifican, contra la base de datos:
# - el registro y el alta con Google guardan la aceptación (y solo con `true`);
# - con la exigencia activada, no se crea una cuenta sin aceptar, y las cuentas
#   de Google que ya existían siguen entrando;
# - `POST /api/users/me/terms-acceptance` solo acepta la versión vigente;
# - `terms_accepted` del usuario público cae a `false` cuando cambia la versión.

import pytest

from app.application.terms.terms_version import configure_terms_version
from app.domain.terms.policy import DEFAULT_TERMS_VERSION
from app.extensions import db
from app.infrastructure.persistence.models import User
from tests.conftest import mark_email_verified
from tests.test_google_auth import _mock_google_identity

VALID_PASSWORD = "secretpass"


@pytest.fixture(autouse=True)
def _restore_terms_version():
    """`configure_terms_version` guarda estado global del módulo: se restaura
    siempre, para que una prueba que cambie la versión no contamine a las demás."""
    yield
    configure_terms_version(DEFAULT_TERMS_VERSION)


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


def _login_token(client, email="ada@example.com"):
    return client.post("/api/login", json={"email": email, "password": VALID_PASSWORD}).get_json()[
        "token"
    ]


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def _user_row(app, user_id):
    with app.app_context():
        user = db.session.get(User, user_id)
        return user.terms_accepted_at, user.terms_version


def _registered_and_logged_in(client):
    user_id = _register(client).get_json()["user"]["id"]
    mark_email_verified(user_id)
    return user_id, _login_token(client)


class TestRegistrationRecordsAcceptance:
    def test_without_the_field_the_account_is_created_as_not_accepted(self, app, client):
        response = _register(client)

        assert response.status_code == 201
        body = response.get_json()["user"]
        assert body["terms_accepted"] is False
        assert _user_row(app, body["id"]) == (None, None)

    def test_with_true_the_acceptance_and_its_version_are_stored(self, app, client):
        response = _register(client, terms_accepted=True)

        assert response.status_code == 201
        body = response.get_json()["user"]
        assert body["terms_accepted"] is True
        accepted_at, version = _user_row(app, body["id"])
        assert accepted_at is not None
        assert version == DEFAULT_TERMS_VERSION

    @pytest.mark.parametrize("value", ["true", 1, "yes", {"a": 1}, [True], "on"])
    def test_only_a_real_true_counts_as_acceptance(self, app, client, value):
        # Un consentimiento no se adivina: ni la cadena "true" ni el número 1.
        response = _register(client, terms_accepted=value)

        assert response.status_code == 201
        assert response.get_json()["user"]["terms_accepted"] is False

    def test_false_is_stored_as_not_accepted(self, client):
        response = _register(client, terms_accepted=False)

        assert response.get_json()["user"]["terms_accepted"] is False


class TestRegistrationWhenAcceptanceIsRequired:
    def test_without_acceptance_the_account_is_not_created(self, app, client):
        app.config["TERMS_ACCEPTANCE_REQUIRED"] = True

        response = _register(client)

        assert response.status_code == 400
        assert response.get_json()["terms_required"] is True
        with app.app_context():
            assert db.session.query(User).count() == 0

    @pytest.mark.parametrize("value", [False, "true", 1, None])
    def test_a_value_that_is_not_true_is_rejected(self, app, client, value):
        app.config["TERMS_ACCEPTANCE_REQUIRED"] = True

        assert _register(client, terms_accepted=value).status_code == 400

    def test_with_acceptance_the_account_is_created(self, app, client):
        app.config["TERMS_ACCEPTANCE_REQUIRED"] = True

        response = _register(client, terms_accepted=True)

        assert response.status_code == 201
        assert response.get_json()["user"]["terms_accepted"] is True

    def test_the_requirement_is_off_by_default(self, app):
        assert app.config["TERMS_ACCEPTANCE_REQUIRED"] is False


class TestAcceptingTermsAfterRegistration:
    def test_requires_authentication(self, client):
        response = client.post(
            "/api/users/me/terms-acceptance", json={"version": DEFAULT_TERMS_VERSION}
        )

        assert response.status_code == 401

    def test_missing_body_is_400(self, client):
        _, token = _registered_and_logged_in(client)

        assert client.post("/api/users/me/terms-acceptance", headers=_h(token)).status_code == 400

    def test_accepting_the_current_version_marks_the_account(self, app, client):
        user_id, token = _registered_and_logged_in(client)

        response = client.post(
            "/api/users/me/terms-acceptance",
            json={"version": DEFAULT_TERMS_VERSION},
            headers=_h(token),
        )

        assert response.status_code == 200
        assert response.get_json()["user"]["terms_accepted"] is True
        accepted_at, version = _user_row(app, user_id)
        assert accepted_at is not None
        assert version == DEFAULT_TERMS_VERSION

    def test_accepting_again_is_idempotent(self, client):
        _, token = _registered_and_logged_in(client)
        body = {"version": DEFAULT_TERMS_VERSION}

        first = client.post("/api/users/me/terms-acceptance", json=body, headers=_h(token))
        second = client.post("/api/users/me/terms-acceptance", json=body, headers=_h(token))

        assert first.status_code == second.status_code == 200

    @pytest.mark.parametrize("version", ["1999-01-01", "", None, 20261002, ["x"], "x" * 100])
    def test_a_version_that_is_not_the_current_one_is_409_with_the_current(self, app, client, version):
        user_id, token = _registered_and_logged_in(client)

        response = client.post(
            "/api/users/me/terms-acceptance", json={"version": version}, headers=_h(token)
        )

        assert response.status_code == 409
        assert response.get_json()["current_version"] == DEFAULT_TERMS_VERSION
        assert _user_row(app, user_id) == (None, None)

    def test_the_users_me_response_reflects_the_acceptance(self, client):
        _, token = _registered_and_logged_in(client)
        assert client.get("/api/users/me", headers=_h(token)).get_json()["user"][
            "terms_accepted"
        ] is False

        client.post(
            "/api/users/me/terms-acceptance",
            json={"version": DEFAULT_TERMS_VERSION},
            headers=_h(token),
        )

        assert client.get("/api/users/me", headers=_h(token)).get_json()["user"][
            "terms_accepted"
        ] is True


class TestChangingTheTermsVersion:
    def test_an_older_acceptance_stops_counting_when_the_version_changes(self, client):
        _, token = _registered_and_logged_in(client)
        client.post(
            "/api/users/me/terms-acceptance",
            json={"version": DEFAULT_TERMS_VERSION},
            headers=_h(token),
        )

        configure_terms_version("2027-01-15")

        # Aceptó la versión anterior: ADR-032 §5, se le vuelve a pedir.
        assert client.get("/api/users/me", headers=_h(token)).get_json()["user"][
            "terms_accepted"
        ] is False

    def test_the_old_version_is_no_longer_accepted(self, client):
        _, token = _registered_and_logged_in(client)
        configure_terms_version("2027-01-15")

        response = client.post(
            "/api/users/me/terms-acceptance",
            json={"version": DEFAULT_TERMS_VERSION},
            headers=_h(token),
        )

        assert response.status_code == 409
        assert response.get_json()["current_version"] == "2027-01-15"

    def test_accepting_the_new_version_works(self, client):
        _, token = _registered_and_logged_in(client)
        configure_terms_version("2027-01-15")

        response = client.post(
            "/api/users/me/terms-acceptance", json={"version": "2027-01-15"}, headers=_h(token)
        )

        assert response.status_code == 200
        assert response.get_json()["user"]["terms_accepted"] is True

    def test_a_blank_version_falls_back_to_the_default(self):
        configure_terms_version("   ")

        from app.application.terms.terms_version import current_terms_version

        assert current_terms_version() == DEFAULT_TERMS_VERSION


class TestGoogleSignUp:
    def test_a_new_google_account_without_acceptance_is_not_created_when_required(
        self, app, client, monkeypatch
    ):
        app.config["TERMS_ACCEPTANCE_REQUIRED"] = True
        _mock_google_identity(monkeypatch, sub="g-new", email="nuevo@example.com")

        response = client.post("/api/auth/google", json={"credential": "x"})

        assert response.status_code == 400
        assert response.get_json()["terms_required"] is True
        with app.app_context():
            assert db.session.query(User).count() == 0

    def test_a_new_google_account_with_acceptance_is_created_and_recorded(
        self, app, client, monkeypatch
    ):
        app.config["TERMS_ACCEPTANCE_REQUIRED"] = True
        _mock_google_identity(monkeypatch, sub="g-new", email="nuevo@example.com")

        response = client.post("/api/auth/google", json={"credential": "x", "terms_accepted": True})

        assert response.status_code == 200
        body = response.get_json()
        assert body["user"]["terms_accepted"] is True
        assert "token" in body and "refresh_token" in body
        assert _user_row(app, body["user"]["id"])[1] == DEFAULT_TERMS_VERSION

    def test_an_existing_google_account_can_still_sign_in_without_the_field(
        self, app, client, monkeypatch
    ):
        _mock_google_identity(monkeypatch, sub="g-old", email="viejo@example.com")
        assert client.post("/api/auth/google", json={"credential": "x"}).status_code == 200

        # Ahora se exige, pero la cuenta ya existe: iniciar sesión no la necesita.
        app.config["TERMS_ACCEPTANCE_REQUIRED"] = True
        response = client.post("/api/auth/google", json={"credential": "x"})

        assert response.status_code == 200
        assert response.get_json()["user"]["terms_accepted"] is False

    def test_when_not_required_a_new_account_is_created_without_acceptance(
        self, app, client, monkeypatch
    ):
        _mock_google_identity(monkeypatch, sub="g-new", email="nuevo@example.com")

        response = client.post("/api/auth/google", json={"credential": "x"})

        assert response.status_code == 200
        assert response.get_json()["user"]["terms_accepted"] is False

    @pytest.mark.parametrize("value", ["true", 1])
    def test_google_only_counts_a_real_true(self, app, client, monkeypatch, value):
        app.config["TERMS_ACCEPTANCE_REQUIRED"] = True
        _mock_google_identity(monkeypatch, sub="g-new", email="nuevo@example.com")

        response = client.post(
            "/api/auth/google", json={"credential": "x", "terms_accepted": value}
        )

        assert response.status_code == 400
