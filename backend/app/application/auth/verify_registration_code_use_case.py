# Caso de uso: verificar el código OTP de registro (POST
# /api/verify-registration-code, ADR-011-mandatory-email-verification.md).
# No autentica con JWT -- quien llama todavía no puede iniciar sesión (la
# cuenta sigue sin verificar). Mismo criterio anti-enumeración que
# verify_reset_code_use_case.py (ADR-010): todos los casos de rechazo
# (email inexistente, ya verificada, sin código activo, expirado, intentos
# agotados, código incorrecto) terminan en la misma excepción.
#
# A diferencia de la recuperación de contraseña, acá no se emite ninguna
# autorización temporal -- verificar el código ES la acción final (marca
# `email_verified = true` directamente, ADR-011 §Decisión).

from datetime import datetime, timezone

from app.domain.auth.auth_service import verify_password
from app.domain.auth.exceptions import InvalidRegistrationCodeError
from app.domain.auth.token_policy import REGISTRATION_MAX_ATTEMPTS


def verify_registration_code(email, code, user_repository, email_verification_token_repository):
    user = user_repository.find_by_email(email)
    if user is None or user.email_verified:
        # Una cuenta ya verificada nunca tiene un código activo (se marca
        # usado al verificarse) -- en la práctica este segundo `or` es
        # redundante con el chequeo de `request_row is None` de abajo, pero
        # se deja explícito para no depender de ese detalle de implementación.
        raise InvalidRegistrationCodeError()

    request_row = email_verification_token_repository.find_active_by_user_id(user.id)
    if request_row is None:
        raise InvalidRegistrationCodeError()

    now = datetime.now(timezone.utc)
    if request_row.expires_at <= now:
        raise InvalidRegistrationCodeError()

    if request_row.attempts >= REGISTRATION_MAX_ATTEMPTS:
        raise InvalidRegistrationCodeError()

    if not verify_password(code, request_row.code_hash):
        email_verification_token_repository.increment_attempts(request_row.id)
        raise InvalidRegistrationCodeError()

    user_repository.update(user.id, {"email_verified": True})
    email_verification_token_repository.mark_used(request_row.id)

    return {"msg": "Tu correo fue verificado correctamente.", "email_verified": True}
