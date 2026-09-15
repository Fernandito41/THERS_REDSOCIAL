# Caso de uso: solicitar recuperación de contraseña (POST /api/forgot-password,
# ADR-009-password-reset-and-email-verification.md). `email` ya llega
# validado en formato por la route (domain/auth/validators.is_valid_email) --
# este caso de uso solo orquesta.
#
# FASE 4 de la tarea: nunca revela si el email existe o no -- la route
# siempre responde el mismo mensaje genérico y este caso de uso nunca lanza
# una excepción distinguible según ese resultado (a diferencia de
# login_user, que sí distingue -- acá ni siquiera se propaga la diferencia
# hacia arriba). Si el email no corresponde a ningún usuario, simplemente no
# se crea ningún token ni se envía ningún correo -- la función igual
# "tiene éxito".

from datetime import datetime, timedelta, timezone

from app.domain.auth.token_generator import generate_raw_token, hash_token
from app.domain.auth.token_policy import (
    PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS,
    PASSWORD_RESET_TOKEN_TTL_MINUTES,
)

GENERIC_MESSAGE = (
    "Si existe una cuenta asociada a ese correo, recibirás instrucciones "
    "para restablecer tu contraseña."
)


def forgot_password(
    email, frontend_url, user_repository, password_reset_token_repository, email_service
):
    user = user_repository.find_by_email(email)

    if user is not None and not password_reset_token_repository.has_recent_unused_token(
        user.id, PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS
    ):
        raw_token = generate_raw_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=PASSWORD_RESET_TOKEN_TTL_MINUTES
        )
        password_reset_token_repository.create(user.id, hash_token(raw_token), expires_at)

        reset_link = f"{frontend_url}/reset-password?token={raw_token}"
        email_service.send_password_reset_email(
            user.email, user.name, reset_link, PASSWORD_RESET_TOKEN_TTL_MINUTES
        )

    # Mismo mensaje siempre -- exista o no el usuario, esté o no en cooldown
    # (FASE 4: evitar enumeración de usuarios).
    return {"msg": GENERIC_MESSAGE}
