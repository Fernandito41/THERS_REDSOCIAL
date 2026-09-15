# Caso de uso: consumir un token de verificación de email (POST
# /api/verify-email, ADR-009-password-reset-and-email-verification.md).
# Público (no requiere JWT) -- quien hace clic en el enlace del correo puede
# no tener sesión iniciada en ese navegador/dispositivo todavía.

from app.domain.auth.exceptions import InvalidOrExpiredVerificationTokenError
from app.domain.auth.token_generator import hash_token


def verify_email(raw_token, user_repository, email_verification_token_repository):
    token_row = email_verification_token_repository.find_valid_by_hash(hash_token(raw_token))
    if token_row is None:
        raise InvalidOrExpiredVerificationTokenError()

    user = user_repository.find_by_id(token_row.user_id)
    if user is None:
        raise InvalidOrExpiredVerificationTokenError()

    user_repository.update(user.id, {"email_verified": True})
    email_verification_token_repository.mark_used(token_row.id)

    return {"msg": "Tu correo fue verificado correctamente.", "email_verified": True}
