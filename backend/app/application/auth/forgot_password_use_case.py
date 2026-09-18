# Caso de uso: solicitar recuperación de contraseña (POST /api/forgot-password,
# ADR-010-password-reset-otp-flow.md, reemplaza el flujo de enlace de
# ADR-009-password-reset-and-email-verification.md). `email` ya llega
# validado en formato por la route (domain/auth/validators.is_valid_email) --
# este caso de uso solo orquesta. También sirve para "Reenviar código"
# (ADR-010 §Decisión): el Frontend llama a este mismo endpoint de nuevo, no
# existe un endpoint de resend separado.
#
# Nunca revela si el email existe o no -- la route siempre responde el mismo
# mensaje genérico y este caso de uso nunca lanza una excepción distinguible
# según ese resultado. Si el email no corresponde a ningún usuario,
# simplemente no se crea ningún código ni se envía ningún correo -- la
# función igual "tiene éxito".

from datetime import datetime, timedelta, timezone

from app.domain.auth.auth_service import hash_password
from app.domain.auth.token_generator import generate_otp_code
from app.domain.auth.token_policy import (
    PASSWORD_RESET_CODE_TTL_MINUTES,
    PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS,
)

GENERIC_MESSAGE = (
    "Si existe una cuenta asociada a ese correo, enviaremos un código de recuperación."
)


def forgot_password(email, user_repository, password_reset_token_repository, email_service):
    user = user_repository.find_by_email(email)

    if user is not None and not password_reset_token_repository.has_recent_unused_code(
        user.id, PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS
    ):
        code = generate_otp_code()
        # Hash lento (scrypt, mismo algoritmo que password_hash) -- no el
        # SHA-256 rápido que usan los tokens de alta entropía de esta app
        # (domain/auth/token_generator.hash_token), ver ADR-010 §Seguridad.
        code_hash = hash_password(code)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=PASSWORD_RESET_CODE_TTL_MINUTES
        )
        password_reset_token_repository.create_code(user.id, code_hash, expires_at)

        email_service.send_password_reset_code_email(
            user.email, user.name, code, PASSWORD_RESET_CODE_TTL_MINUTES
        )

    # Mismo mensaje siempre -- exista o no el usuario, esté o no en cooldown
    # (evitar enumeración de usuarios).
    return {"msg": GENERIC_MESSAGE}
