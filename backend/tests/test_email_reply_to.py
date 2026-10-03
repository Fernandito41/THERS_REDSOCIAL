# Pruebas del Reply-To de los correos transaccionales (campo `reply_to` del SDK de
# Resend). No se envía ningún correo: se sustituye `resend.Emails.send` por una
# función que captura lo que recibiría el SDK, y se comprueba ese mensaje.
#
# Se usan las plantillas REALES (`EmailService` + `templates.py`), así que también se
# comprueba que añadir el Reply-To no cambió el contenido de los correos.

import resend

from app.application.email.email_service import EmailService
from app.infrastructure.email.factory import create_email_sender
from app.infrastructure.email.null_email_sender import NullEmailSender
from app.infrastructure.email.resend_email_sender import ResendEmailSender

FROM = "THERS <avisos@notificaciones.thersweb.com>"
REPLY_TO = "soporte@thersweb.com"


def _capture(monkeypatch):
    sent = []
    monkeypatch.setattr(resend.Emails, "send", lambda params: sent.append(params))
    return sent


def _service(reply_to):
    return EmailService(ResendEmailSender("re_test_not_a_real_key", FROM, reply_to))


class TestReplyTo:
    def test_the_message_includes_reply_to_and_keeps_the_sender(self, monkeypatch):
        sent = _capture(monkeypatch)

        _service(REPLY_TO).send_registration_code_email("ana@example.com", "Ana", "123456", 10)

        assert len(sent) == 1
        assert sent[0]["reply_to"] == REPLY_TO
        assert sent[0]["from"] == FROM
        assert sent[0]["to"] == ["ana@example.com"]

    def test_the_templates_are_unchanged(self, monkeypatch):
        sent = _capture(monkeypatch)

        _service(REPLY_TO).send_registration_code_email("ana@example.com", "Ana", "123456", 10)

        assert "THERS" in sent[0]["subject"]
        assert "123456" in sent[0]["html"]

    def test_every_transactional_email_carries_reply_to(self, monkeypatch):
        sent = _capture(monkeypatch)
        service = _service(REPLY_TO)

        service.send_registration_code_email("a@example.com", "Ana", "111111", 10)
        service.send_password_reset_code_email("a@example.com", "Ana", "222222", 10)
        service.send_password_changed_email("a@example.com", "Ana")
        service.send_login_alert_email("a@example.com", "Ana", "Firefox", "1.2.3.4", None)

        assert len(sent) == 4
        assert all(message["reply_to"] == REPLY_TO for message in sent)
        assert all(message["from"] == FROM for message in sent)

    def test_without_reply_to_the_field_is_omitted(self, monkeypatch):
        sent = _capture(monkeypatch)

        _service(None).send_password_changed_email("ana@example.com", "Ana")

        # Omitido, no `None` ni cadena vacía: el SDK enviaría un Reply-To inválido.
        assert "reply_to" not in sent[0]

    def test_an_empty_reply_to_is_treated_as_not_configured(self, monkeypatch):
        sent = _capture(monkeypatch)

        _service("").send_password_changed_email("ana@example.com", "Ana")

        assert "reply_to" not in sent[0]


class TestFactory:
    def test_the_factory_passes_reply_to_to_the_real_sender(self, monkeypatch):
        sent = _capture(monkeypatch)

        sender = create_email_sender("re_test_not_a_real_key", FROM, REPLY_TO)
        sender.send("ana@example.com", "Asunto", "<p>hola</p>")

        assert isinstance(sender, ResendEmailSender)
        assert sent[0]["reply_to"] == REPLY_TO

    def test_the_old_two_argument_call_still_works(self, monkeypatch):
        sent = _capture(monkeypatch)

        sender = create_email_sender("re_test_not_a_real_key", FROM)
        sender.send("ana@example.com", "Asunto", "<p>hola</p>")

        assert "reply_to" not in sent[0]

    def test_without_an_api_key_nothing_is_sent_to_resend(self, monkeypatch):
        sent = _capture(monkeypatch)

        sender = create_email_sender("", FROM, REPLY_TO)
        sender.send("ana@example.com", "Asunto", "<p>hola</p>")

        assert isinstance(sender, NullEmailSender)
        assert sent == []


class TestConfig:
    def test_the_setting_is_read_from_the_environment(self, monkeypatch):
        import importlib

        import app.config as config

        monkeypatch.setenv("EMAIL_REPLY_TO", "  soporte@thersweb.com  ")
        try:
            importlib.reload(config)
            assert config.Config.EMAIL_REPLY_TO == "soporte@thersweb.com"

            monkeypatch.setenv("EMAIL_REPLY_TO", "   ")
            importlib.reload(config)
            assert config.Config.EMAIL_REPLY_TO is None
        finally:
            monkeypatch.delenv("EMAIL_REPLY_TO", raising=False)
            importlib.reload(config)
