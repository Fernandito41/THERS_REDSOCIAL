# Caso de uso: pedir el correo de verificación de email (POST
# /api/send-verification-email, ADR-009-password-reset-and-email-verification.md).
# A diferencia de forgot_password_use_case, este endpoint está protegido
# (@jwt_required()) -- `user_id` ya identifica a una cuenta real, así que no
# hace falta ocultar si existe (no hay enumeración posible: quien pregunta
# ya demostró ser dueño de la cuenta con su JWT).

from datetime import datetime, timedelta, timezone

from app.domain.auth.exceptions import UserNotFoundError
from app.domain.auth.token_generator import generate_raw_token, hash_token
from app.domain.auth.token_policy import (
    EMAIL_VERIFICATION_REQUEST_COOLDOWN_SECONDS,
    EMAIL_VERIFICATION_TOKEN_TTL_HOURS,
)


def send_verification_email(
    user_id, frontend_url, user_repository, email_verification_token_repository, email_service
):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    if user.email_verified:
        return {"msg": "Tu correo ya está verificado."}

    if email_verification_token_repository.has_recent_unused_token(
        user.id, EMAIL_VERIFICATION_REQUEST_COOLDOWN_SECONDS
    ):
        return {
            "msg": "Ya te enviamos un correo de verificación hace poco. "
                   "Revisá tu bandeja de entrada (y spam) antes de pedir otro."
        }

    raw_token = generate_raw_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=EMAIL_VERIFICATION_TOKEN_TTL_HOURS
    )
    email_verification_token_repository.create(user.id, hash_token(raw_token), expires_at)

    verify_link = f"{frontend_url}/verify-email?token={raw_token}"
    email_service.send_verification_email(
        user.email, user.name, verify_link, EMAIL_VERIFICATION_TOKEN_TTL_HOURS
    )

    return {"msg": "Te enviamos un correo de verificación."}
