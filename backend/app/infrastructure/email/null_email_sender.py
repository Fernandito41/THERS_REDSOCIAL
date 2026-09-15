# Implementación nula del puerto `EmailSender` (domain/email/sender.py) --
# se usa automáticamente cuando RESEND_API_KEY no está definida (ver
# app/config.py, interfaces/routes/auth_routes.py) para que el backend
# arranque y los flujos de recuperación/verificación funcionen de punta a
# punta en desarrollo local sin necesitar una cuenta de Resend todavía
# (ADR-009-password-reset-and-email-verification.md §Riesgos). Nunca falla,
# nunca llama a ningún servicio externo -- solo imprime el intento por
# stderr, mismo mecanismo que los avisos de fallback de app/config.py (no
# `logging`: con `app.run(debug=False)`, ver run.py, ni el logger de Flask
# ni el root logger tienen un handler que muestre nivel INFO por defecto --
# un `print(..., file=sys.stderr)` es el único que se ve siempre, sin
# depender de configuración de logging adicional).
#
# Deliberadamente NO imprime `html_body` -- solo destinatario y asunto. El
# cuerpo puede incluir el token crudo de recuperación/verificación (dentro
# del enlace) y no debe aparecer en ningún log (HB-001 §19.1, mismo
# principio que nunca loguear password_hash/JWT_SECRET_KEY).

import sys

from app.domain.email.sender import EmailSender


class NullEmailSender(EmailSender):
    def send(self, to_email, subject, html_body):
        print(
            f"[email] RESEND_API_KEY no configurada -- correo NO enviado "
            f"(to={to_email!r}, subject={subject!r})",
            file=sys.stderr,
        )
