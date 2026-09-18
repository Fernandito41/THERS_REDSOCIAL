# Caso de uso: "Reenviar código" en la pantalla de verificación de registro
# (ADR-011-mandatory-email-verification.md). Público, sin JWT -- quien lo
# llama todavía no completó la verificación obligatoria, no puede haber
# iniciado sesión. Mismo criterio anti-enumeración que
# forgot_password_use_case.py: la respuesta nunca distingue "el email no
# existe" de "ya está verificado" de "está en cooldown".

from app.application.auth.send_registration_code_use_case import send_registration_code
from app.domain.auth.token_policy import REGISTRATION_CODE_REQUEST_COOLDOWN_SECONDS

GENERIC_MESSAGE = (
    "Si existe una cuenta pendiente de verificación con ese correo, "
    "enviaremos un código nuevo."
)


def resend_registration_code(
    email, user_repository, email_verification_token_repository, email_service
):
    user = user_repository.find_by_email(email)

    if (
        user is not None
        and not user.email_verified
        and not email_verification_token_repository.has_recent_unused_code(
            user.id, REGISTRATION_CODE_REQUEST_COOLDOWN_SECONDS
        )
    ):
        send_registration_code(user, email_verification_token_repository, email_service)

    return {"msg": GENERIC_MESSAGE}
