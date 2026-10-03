# Pruebas de la edad mínima de 18 años (ADR-034-minimum-age-18.md) contra
# PostgreSQL real (ver conftest.py).
#
# La edad se calcula por fecha COMPLETA (año, mes y día), no por diferencia de
# años. Es la fecha que la persona declara: ninguna de estas pruebas pretende
# verificar documentos.

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from app.domain.auth.validators import MIN_AGE_YEARS, meets_minimum_age
from app.extensions import db
from app.infrastructure.persistence.models import User
from tests.conftest import mark_email_verified
from tests.test_google_auth import _mock_google_identity

PASSWORD = "secretpass"


def _years_ago(years, days_offset=0, today=None):
    """Fecha de hace `years` años exactos (cuidando el 29 de febrero) más/menos días."""
    today = today or date.today()
    try:
        base = today.replace(year=today.year - years)
    except ValueError:  # hoy es 29-feb y el año destino no es bisiesto
        base = today.replace(year=today.year - years, day=28)
    return base + timedelta(days=days_offset)


def _payload(**overrides):
    payload = {
        "name": "Ada Lovelace",
        "username": "ada_lovelace",
        "email": "ada@example.com",
        "phone": "7000-1234",
        "country_code": "+503",
        "birth_date": "1990-01-01",
        "password": PASSWORD,
        "confirm_password": PASSWORD,
    }
    payload.update(overrides)
    return payload


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def test_the_minimum_age_is_eighteen():
    assert MIN_AGE_YEARS == 18


# ===========================================================================
# Cálculo de la edad (función pura, con `today` fijo)
# ===========================================================================
class TestAgeCalculation:
    TODAY = date(2026, 10, 2)

    def test_turning_eighteen_today_qualifies(self):
        assert meets_minimum_age(date(2008, 10, 2), today=self.TODAY)

    def test_turning_eighteen_tomorrow_does_not_qualify(self):
        assert not meets_minimum_age(date(2008, 10, 3), today=self.TODAY)

    def test_one_day_after_the_birthday_qualifies(self):
        assert meets_minimum_age(date(2008, 10, 1), today=self.TODAY)

    def test_comparison_uses_month_and_day_not_just_the_year(self):
        # Mismo año de nacimiento, mes posterior: todavía tiene 17.
        assert not meets_minimum_age(date(2008, 12, 31), today=self.TODAY)
        assert meets_minimum_age(date(2008, 1, 1), today=self.TODAY)

    def test_a_future_birth_date_does_not_qualify(self):
        assert not meets_minimum_age(date(2027, 1, 1), today=self.TODAY)

    def test_leap_day_birthday_counts_from_march_first_in_a_common_year(self):
        born = date(2008, 2, 29)
        # 2026 no es bisiesto: el 28-feb todavía no cumplió, el 1-mar sí.
        assert not meets_minimum_age(born, today=date(2026, 2, 28))
        assert meets_minimum_age(born, today=date(2026, 3, 1))

    def test_leap_day_birthday_qualifies_on_the_leap_day_itself(self):
        # 2028 sí es bisiesto: cumple 20, y el propio 29-feb de 2026+... la
        # comprobación relevante es que no se rompa con fechas válidas.
        assert meets_minimum_age(date(2008, 2, 29), today=date(2028, 2, 29))


# ===========================================================================
# Registro tradicional
# ===========================================================================
class TestRegistration:
    def test_exactly_eighteen_today_can_register(self, client):
        response = client.post(
            "/api/register", json=_payload(birth_date=_years_ago(18).isoformat())
        )

        assert response.status_code == 201

    def test_turning_eighteen_tomorrow_cannot_register(self, client):
        response = client.post(
            "/api/register",
            json=_payload(birth_date=_years_ago(18, days_offset=1).isoformat()),
        )

        assert response.status_code == 400
        assert response.get_json()["min_age"] == 18

    @pytest.mark.parametrize("birth_date", ["2010-06-15", "2015-01-01", "2020-01-01", "2099-01-01"])
    def test_minors_cannot_register(self, client, birth_date):
        response = client.post("/api/register", json=_payload(birth_date=birth_date))

        assert response.status_code == 400
        with client.application.app_context():
            assert db.session.query(User).count() == 0

    def test_the_message_names_the_age_from_the_single_constant(self, client):
        body = client.post("/api/register", json=_payload(birth_date="2015-01-01")).get_json()

        assert "18" in body["msg"]
        assert "13" not in body["msg"]

    def test_a_malformed_date_is_still_a_plain_400(self, client):
        response = client.post("/api/register", json=_payload(birth_date="18 años"))

        assert response.status_code == 400


# ===========================================================================
# Google Sign-In: una cuenta de Google no demuestra la edad
# ===========================================================================
class TestGoogleAccounts:
    def _google_session(self, client, monkeypatch):
        _mock_google_identity(monkeypatch, sub="g-age", email="goog@example.com")
        response = client.post("/api/auth/google", json={"credential": "x"})
        assert response.status_code == 200
        body = response.get_json()
        return body["token"], body["user"]

    def test_a_new_google_account_starts_without_a_birth_date_and_incomplete(
        self, client, monkeypatch
    ):
        _, user = self._google_session(client, monkeypatch)

        assert user["profile_completed"] is False
        assert user["birth_date"] is None

    def test_completing_the_profile_as_a_minor_is_rejected(self, client, monkeypatch):
        token, _ = self._google_session(client, monkeypatch)

        response = client.patch(
            "/api/users/me",
            json={
                "phone": "7000-1234",
                "country_code": "+503",
                "birth_date": _years_ago(18, days_offset=1).isoformat(),
            },
            headers=_h(token),
        )

        assert response.status_code == 400
        assert response.get_json()["min_age"] == 18
        # Y la cuenta sigue incompleta.
        me = client.get("/api/users/me", headers=_h(token)).get_json()["user"]
        assert me["profile_completed"] is False

    def test_completing_the_profile_as_an_adult_works(self, client, monkeypatch):
        token, _ = self._google_session(client, monkeypatch)

        response = client.patch(
            "/api/users/me",
            json={
                "phone": "7000-1234",
                "country_code": "+503",
                "birth_date": _years_ago(18).isoformat(),
            },
            headers=_h(token),
        )

        assert response.status_code == 200
        assert response.get_json()["user"]["profile_completed"] is True

    def test_an_incomplete_google_account_cannot_create_content_through_the_api(
        self, client, monkeypatch
    ):
        # La redirección a "Completar perfil" es solo de interfaz: quien llame a
        # la API con ese token no puede publicar sin haber declarado su edad.
        token, _ = self._google_session(client, monkeypatch)

        attempts = [
            client.post("/api/posts", json={"content": "hola"}, headers=_h(token)),
            client.post(
                "/api/posts/00000000-0000-0000-0000-000000000001/comments",
                json={"content": "hola"},
                headers=_h(token),
            ),
            client.post(
                "/api/posts/00000000-0000-0000-0000-000000000001/like", headers=_h(token)
            ),
            client.post(
                "/api/users/00000000-0000-0000-0000-000000000001/follow", headers=_h(token)
            ),
            client.post(
                "/api/users/00000000-0000-0000-0000-000000000001/messages",
                json={"content": "hola"},
                headers=_h(token),
            ),
        ]

        for response in attempts:
            assert response.status_code == 403
            assert response.get_json()["profile_incomplete"] is True

    def test_after_completing_the_profile_the_same_account_can_post(self, client, monkeypatch):
        token, _ = self._google_session(client, monkeypatch)
        client.patch(
            "/api/users/me",
            json={
                "phone": "7000-1234",
                "country_code": "+503",
                "birth_date": _years_ago(25).isoformat(),
            },
            headers=_h(token),
        )

        response = client.post("/api/posts", json={"content": "hola"}, headers=_h(token))

        assert response.status_code == 201

    def test_the_gate_does_not_block_reading(self, client, monkeypatch):
        token, _ = self._google_session(client, monkeypatch)

        assert client.get("/api/users/me", headers=_h(token)).status_code == 200


# ===========================================================================
# Cuentas existentes: no se bloquean, no se borran, no se inventan fechas
# ===========================================================================
class TestExistingAccounts:
    def _insert_user(self, app, email, username, birth_date):
        with app.app_context():
            user = User(
                name="Existente",
                username=username,
                email=email,
                phone="7000-1234",
                country_code="+503",
                birth_date=birth_date,
                password_hash="x",
                email_verified=True,
                profile_completed=True,
            )
            db.session.add(user)
            db.session.commit()

    def test_an_existing_account_declared_as_a_minor_is_left_untouched(self, app, client):
        client.post("/api/register", json=_payload())
        with app.app_context():
            user = db.session.query(User).one()
            user.birth_date = date(2012, 5, 5)  # declarada antes de la regla de 18
            db.session.commit()
            user_id = str(user.id)
        mark_email_verified(user_id)

        login = client.post("/api/login", json={"email": "ada@example.com", "password": PASSWORD})

        # Sigue pudiendo entrar y usar la app: qué hacer con ella es una decisión
        # de producto (ADR-034 §Cuentas existentes), no un bloqueo silencioso.
        assert login.status_code == 200
        with app.app_context():
            assert db.session.get(User, user.id).birth_date == date(2012, 5, 5)

    def test_the_audit_counts_each_category_without_changing_anything(self, app):
        today = date(2026, 10, 2)
        self._insert_user(app, "a@example.com", "adulto_a", date(1990, 1, 1))
        self._insert_user(app, "b@example.com", "adulto_b", date(2008, 10, 2))  # 18 hoy
        self._insert_user(app, "c@example.com", "menor_c", date(2008, 10, 3))  # 17
        self._insert_user(app, "d@example.com", "menor_d", date(2014, 1, 1))
        with app.app_context():
            user = User(
                name="Google", username="goog_e", email="e@example.com",
                email_verified=True, profile_completed=False,
            )
            db.session.add(user)
            db.session.commit()

        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        import audit_minimum_age

        with app.app_context():
            before = db.session.query(User).count()
            counts = audit_minimum_age.audit(today=today)
            after = db.session.query(User).count()

        assert counts == {"mayores_de_edad": 2, "menores_declarados": 2, "sin_fecha": 1}
        assert before == after == 5
