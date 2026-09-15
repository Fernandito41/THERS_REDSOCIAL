# Caso de uso: aplicar un nuevo password usando un token de recuperación
# (POST /api/reset-password, ADR-009-password-reset-and-email-verification.md).
# `new_password` ya llega validada en formato por la route
# (domain/auth/validators.is_valid_password) -- este caso de uso hashea y
# persiste, mismo patrón que register_user hashea dentro del caso de uso
# (no en la route).

from app.domain.auth.auth_service import hash_password
from app.domain.auth.exceptions import InvalidOrExpiredResetTokenError
from app.domain.auth.token_generator import hash_token


def reset_password(
    raw_token, new_password, user_repository, password_reset_token_repository, email_service
):
    token_row = password_reset_token_repository.find_valid_by_hash(hash_token(raw_token))
    if token_row is None:
        # No existe, expiró, o ya se usó -- los tres casos se tratan igual,
        # sin distinguir cuál ocurrió (ADR-009 §Contrato API).
        raise InvalidOrExpiredResetTokenError()

    user = user_repository.find_by_id(token_row.user_id)
    if user is None:
        # El usuario del token ya no existe (cuenta eliminada después de
        # emitirse el token) -- mismo error genérico, no uno distinto que
        # revele que el token en sí era válido.
        raise InvalidOrExpiredResetTokenError()

    user_repository.update(user.id, {"password_hash": hash_password(new_password)})

    # Invalida el token usado y cualquier otro token de recuperación
    # vigente de este usuario (ADR-009 §Decisión) -- un enlace de un pedido
    # anterior que el usuario nunca abrió deja de servir apenas la
    # contraseña cambia.
    password_reset_token_repository.mark_used(token_row.id)
    password_reset_token_repository.invalidate_all_for_user(user.id)

    email_service.send_password_changed_email(user.email, user.name)

    return {"msg": "Tu contraseña fue actualizada correctamente."}
