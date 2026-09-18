# Caso de uso: aplicar un nuevo password usando la autorización temporal
# emitida por POST /api/verify-reset-code (POST /api/reset-password,
# ADR-010-password-reset-otp-flow.md, reemplaza el consumo directo del
# token de enlace de ADR-009-password-reset-and-email-verification.md).
# `new_password` ya llega validada en formato por la route
# (domain/auth/validators.is_valid_password) -- este caso de uso hashea y
# persiste, mismo patrón que register_use_case hashea dentro del caso de
# uso (no en la route).
#
# Ya no hace falta invalidar "cualquier otro token de recuperación
# pendiente" (ADR-009 lo hacía): con el flujo OTP hay a lo sumo una
# solicitud activa por usuario en todo momento (uq_password_reset_tokens_active_user,
# ADR-010 §Decisión) -- marcar esta fila como usada ya cubre todo.

from app.domain.auth.auth_service import hash_password
from app.domain.auth.exceptions import InvalidOrExpiredResetTokenError
from app.domain.auth.token_generator import hash_token


def reset_password(
    raw_authorization, new_password, user_repository, password_reset_token_repository, email_service
):
    request_row = password_reset_token_repository.find_valid_by_reset_authorization_hash(
        hash_token(raw_authorization)
    )
    if request_row is None:
        # No existe, expiró, ya se usó, o nunca se verificó -- ninguno se
        # distingue en la respuesta (ADR-010 §Contrato API).
        raise InvalidOrExpiredResetTokenError()

    user = user_repository.find_by_id(request_row.user_id)
    if user is None:
        raise InvalidOrExpiredResetTokenError()

    user_repository.update(user.id, {"password_hash": hash_password(new_password)})
    password_reset_token_repository.mark_used(request_row.id)

    email_service.send_password_changed_email(user.email, user.name)

    return {"msg": "Tu contraseña fue actualizada correctamente."}
