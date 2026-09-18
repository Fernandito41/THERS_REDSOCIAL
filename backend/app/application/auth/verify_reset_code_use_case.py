# Caso de uso: verificar el código OTP de recuperación de contraseña (POST
# /api/verify-reset-code, ADR-010-password-reset-otp-flow.md). No autentica
# con JWT -- quien llama todavía no puede iniciar sesión (por eso perdió su
# contraseña); la identidad la aporta `email` + el código correcto.
#
# Todos los casos de rechazo (email inexistente, sin solicitud activa,
# código expirado, intentos agotados, código incorrecto) terminan en la
# misma excepción -- ADR-010 §Seguridad: distinguirlos permitiría enumerar
# usuarios (un email real eventualmente agotaría sus intentos; uno falso
# nunca lo haría, si el mensaje fuera distinto).

from datetime import datetime, timedelta, timezone

from app.domain.auth.auth_service import verify_password
from app.domain.auth.exceptions import InvalidResetCodeError
from app.domain.auth.token_generator import generate_raw_token, hash_token
from app.domain.auth.token_policy import (
    PASSWORD_RESET_AUTHORIZATION_TTL_MINUTES,
    PASSWORD_RESET_MAX_ATTEMPTS,
)


def verify_reset_code(email, code, user_repository, password_reset_token_repository):
    user = user_repository.find_by_email(email)
    if user is None:
        raise InvalidResetCodeError()

    request_row = password_reset_token_repository.find_active_by_user_id(user.id)
    if request_row is None:
        raise InvalidResetCodeError()

    now = datetime.now(timezone.utc)
    if request_row.expires_at <= now:
        raise InvalidResetCodeError()

    if request_row.attempts >= PASSWORD_RESET_MAX_ATTEMPTS:
        # Ya agotó sus intentos -- ni siquiera se compara el código: no
        # importa si "code" es correcto o no, la solicitud ya quedó
        # inutilizable (domain/auth/token_policy.PASSWORD_RESET_MAX_ATTEMPTS).
        raise InvalidResetCodeError()

    if not verify_password(code, request_row.code_hash):
        password_reset_token_repository.increment_attempts(request_row.id)
        raise InvalidResetCodeError()

    raw_authorization = generate_raw_token()
    authorization_expires_at = now + timedelta(
        minutes=PASSWORD_RESET_AUTHORIZATION_TTL_MINUTES
    )
    password_reset_token_repository.mark_verified(
        request_row.id, hash_token(raw_authorization), authorization_expires_at
    )

    return {
        "msg": "Código verificado correctamente.",
        "reset_authorization": raw_authorization,
    }
