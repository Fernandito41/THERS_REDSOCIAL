# Fábrica del `EmailSender` concreto -- el único punto que decide entre
# ResendEmailSender (real) y NullEmailSender (desarrollo sin
# RESEND_API_KEY), para no duplicar ese `if` en cada route que necesita un
# EmailService (interfaces/routes/auth_routes.py y user_routes.py, ver
# ADR-009-password-reset-and-email-verification.md §Decisión).

from app.infrastructure.email.null_email_sender import NullEmailSender
from app.infrastructure.email.resend_email_sender import ResendEmailSender


def create_email_sender(api_key, from_email):
    if not api_key:
        return NullEmailSender()
    return ResendEmailSender(api_key, from_email)
