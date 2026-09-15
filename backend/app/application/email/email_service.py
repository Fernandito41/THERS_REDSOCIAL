# "Email Service" pedido explícitamente por la tarea (FASE 2): la única capa
# que arma el contenido (asunto + HTML, vía application/email/templates.py)
# de cada correo de THERS y lo envía a través del puerto `EmailSender`
# (domain/email/sender.py) -- ningún caso de uso llama a Resend
# directamente, ni construye HTML inline (ADR-009-password-reset-and-email-verification.md
# §Decisión):
#
#   routes -> use cases -> EmailService -> EmailSender (puerto) -> Resend (adaptador)
#
# Recibe el `EmailSender` concreto por inyección (mismo patrón Repository
# que el resto de application/ ya usa) -- no sabe si es Resend real o el
# NullEmailSender de desarrollo (infrastructure/email/), ni le importa.
#
# Deliberadamente NO atrapa excepciones de envío -- si Resend falla (red,
# API key inválida, etc.), la excepción se propaga hasta la route, que la
# deja caer en el manejador global de errores (interfaces/error_handlers.py,
# responde 500 genérico) en vez de tragarse el fallo en silencio. La única
# excepción a esto es intencional y vive en cada caso de uso, no acá: FASE 4
# pide que un email inexistente en forgot-password nunca se distinga de uno
# real, así que ese caso de uso directamente no llama a este servicio si el
# usuario no existe -- no es este servicio el que decide ocultar nada.

from app.application.email.templates import (
    email_verification_email,
    password_changed_email,
    password_reset_email,
)


class EmailService:
    def __init__(self, email_sender):
        self._email_sender = email_sender

    def send_password_reset_email(self, to_email, name, reset_link, ttl_minutes):
        subject, html = password_reset_email(name, reset_link, ttl_minutes)
        self._email_sender.send(to_email, subject, html)

    def send_password_changed_email(self, to_email, name):
        subject, html = password_changed_email(name)
        self._email_sender.send(to_email, subject, html)

    def send_verification_email(self, to_email, name, verify_link, ttl_hours):
        subject, html = email_verification_email(name, verify_link, ttl_hours)
        self._email_sender.send(to_email, subject, html)
