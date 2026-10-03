# Qué pasa cuando el proveedor de correo (Resend) FALLA: dominio sin verificar, clave de
# otro equipo, límite diario del plan gratuito agotado...
#
# Se simula haciendo que el envío lance un error, sin tocar la red. Garantías:
#  - el registro NO responde 500 después de haber creado la cuenta (`email_sent: false`);
#  - `forgot-password` y el reenvío responden IGUAL exista o no la cuenta (un 500 solo
#    para las cuentas que existen revelaría qué correos están registrados);
#  - cambiar la contraseña no responde 500 si solo falló el aviso posterior;
#  - los registros del fallo NO contienen el código ni el destinatario.

import logging
import uuid

import pytest

from app.extensions import db
from app.infrastructure.persistence.models import EmailVerificationToken, User
from app.interfaces.routes import auth_routes
from tests.conftest import mark_email_verified
from tests.test_password_reset import NEW_PASSWORD, _create_verified_request
from tests.test_password_reset import _register as _register_user

SECRET_CODE = "654321"


class ProviderError(Exception):
    """Imita a `resend.exceptions.ResendError` (lleva `code` y `error_type`)."""

    code = 403
    error_type = "validation_error"


@pytest.fixture()
def failing_provider(monkeypatch):
    def boom(self, *args, **kwargs):
        raise ProviderError("El dominio notificaciones.example no está verificado: ana@example.com")

    # Se parchea la CLASE, no la instancia: al deshacer un parche sobre una instancia,
    # pytest deja un atributo propio que taparía parches de clase de otras pruebas.
    monkeypatch.setattr(type(auth_routes._email_service._email_sender), "send", boom)
    # Código conocido SOLO para buscarlo después en respuestas y registros.
    monkeypatch.setattr(
        "app.application.auth.send_registration_code_use_case.generate_otp_code",
        lambda: SECRET_CODE,
    )
    monkeypatch.setattr(
        "app.application.auth.forgot_password_use_case.generate_otp_code", lambda: SECRET_CODE
    )


def _payload(**overrides):
    payload = {
        "name": "Ada Lovelace",
        "username": "ada_lovelace",
        "email": "ada@example.com",
        "phone": "7000-1234",
        "country_code": "+503",
        "birth_date": "1990-01-01",
        "password": "secretpass",
        "confirm_password": "secretpass",
    }
    payload.update(overrides)
    return payload


class TestRegistration:
    def test_a_provider_failure_does_not_turn_into_a_500(self, app, client, failing_provider):
        response = client.post("/api/register", json=_payload())

        assert response.status_code == 201
        body = response.get_json()
        assert body["email_sent"] is False
        # La cuenta existe: la persona puede pedir otro código con «Reenviar».
        with app.app_context():
            user = db.session.query(User).one()
            assert user.email_verified is False
            assert db.session.query(EmailVerificationToken).count() == 1

    def test_when_the_email_goes_out_email_sent_is_true(self, client):
        response = client.post("/api/register", json=_payload())

        assert response.status_code == 201
        assert response.get_json()["email_sent"] is True

    def test_the_response_and_the_logs_never_contain_the_code_or_the_recipient(
        self, client, failing_provider, caplog
    ):
        with caplog.at_level(logging.WARNING):
            response = client.post("/api/register", json=_payload())

        assert SECRET_CODE not in response.get_data(as_text=True)
        assert SECRET_CODE not in caplog.text
        # Ni el destinatario ni el mensaje del proveedor (puede incluir direcciones).
        assert "ada@example.com" not in caplog.text
        assert "no está verificado" not in caplog.text
        # Sí lo útil para diagnosticar: qué correo, qué error y el código del proveedor.
        assert "registration_code" in caplog.text
        assert "ProviderError" in caplog.text
        assert "code=403" in caplog.text

    def test_resending_works_once_the_provider_recovers(self, app, client, monkeypatch):
        sent = []
        monkeypatch.setattr(
            type(auth_routes._email_service._email_sender),
            "send",
            lambda self, *a, **k: sent.append(a),
        )
        client.post("/api/register", json=_payload())
        sent.clear()
        with app.app_context():
            db.session.query(EmailVerificationToken).delete()
            db.session.commit()

        response = client.post("/api/resend-registration-code", json={"email": "ada@example.com"})

        assert response.status_code == 200
        assert len(sent) == 1


class TestResendRegistrationCode:
    def test_a_provider_failure_gets_the_same_answer_as_an_unknown_email(
        self, app, client, failing_provider
    ):
        client.post("/api/register", json=_payload())
        with app.app_context():
            db.session.query(EmailVerificationToken).delete()
            db.session.commit()

        real = client.post("/api/resend-registration-code", json={"email": "ada@example.com"})
        fake = client.post("/api/resend-registration-code", json={"email": "nadie@example.com"})

        assert real.status_code == fake.status_code == 200
        assert real.get_json() == fake.get_json()


class TestForgotPassword:
    def test_a_provider_failure_does_not_reveal_which_emails_exist(
        self, client, failing_provider
    ):
        _register_user(client)

        real = client.post("/api/forgot-password", json={"email": "ada@example.com"})
        fake = client.post("/api/forgot-password", json={"email": "nadie@example.com"})

        # Sin esto, una cuenta real daría 500 (falla el envío) y una inexistente 200.
        assert real.status_code == fake.status_code == 200
        assert real.get_json() == fake.get_json()

    def test_the_code_is_not_in_the_response_or_the_logs(self, client, failing_provider, caplog):
        _register_user(client)

        with caplog.at_level(logging.WARNING):
            response = client.post("/api/forgot-password", json={"email": "ada@example.com"})

        assert SECRET_CODE not in response.get_data(as_text=True)
        assert SECRET_CODE not in caplog.text
        assert "password_reset_code" in caplog.text


class TestResetPassword:
    def test_a_failed_confirmation_email_does_not_undo_or_hide_the_password_change(
        self, app, client, failing_provider
    ):
        user_id = _register_user(client).get_json()["user"]["id"]
        mark_email_verified(user_id)
        authorization = _create_verified_request(app, user_id)

        response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": authorization,
                "password": NEW_PASSWORD,
                "confirm_password": NEW_PASSWORD,
            },
        )

        assert response.status_code == 200
        # La contraseña SÍ cambió aunque falló el aviso: se puede entrar con la nueva.
        login = client.post(
            "/api/login", json={"email": "ada@example.com", "password": NEW_PASSWORD}
        )
        assert login.status_code == 200
        assert uuid.UUID(user_id)
