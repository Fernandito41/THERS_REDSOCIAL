# Adaptador del puerto `EmailSender` (domain/email/sender.py) sobre el SDK
# oficial de Resend (`resend`, ver requirements.txt). Único punto del
# backend que importa `resend` -- domain/ y application/ no conocen Resend,
# solo la interfaz `EmailSender` (BACKEND_ARCHITECTURE.md §17, mismo
# principio que confina SQLAlchemy a infrastructure/persistence/).

import resend

from app.domain.email.sender import EmailSender


class ResendEmailSender(EmailSender):
    def __init__(self, api_key, from_email):
        # `resend.api_key` es un atributo global del propio SDK (no hay un
        # cliente instanciable) -- se fija acá, en el único adaptador que
        # debería tocarlo, en vez de en config.py o en cualquier otro
        # módulo (ADR-009-password-reset-and-email-verification.md §Decisión).
        resend.api_key = api_key
        self._from_email = from_email

    def send(self, to_email, subject, html_body):
        resend.Emails.send({
            "from": self._from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        })
