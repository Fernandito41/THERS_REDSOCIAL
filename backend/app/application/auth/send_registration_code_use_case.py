# Genera y envía un código de verificación de registro -- compartido por
# register_use_case.py (envío automático al registrarse) y
# resend_registration_code_use_case.py ("Reenviar código"), para no
# duplicar la lógica de generación/hash/envío entre ambos
# (ADR-011-mandatory-email-verification.md §Decisión: "no duplicar
# generadores OTP/hashing/EmailSender/templates/TTL").
#
# No es un "caso de uso" en el sentido de estar atado a un endpoint propio
# -- es la pieza interna que ambos casos de uso sí expuestos por endpoint
# reutilizan tal cual.

from datetime import datetime, timedelta, timezone

from app.domain.auth.auth_service import hash_password
from app.domain.auth.token_generator import generate_otp_code
from app.domain.auth.token_policy import REGISTRATION_CODE_TTL_MINUTES


def send_registration_code(user, email_verification_token_repository, email_service):
    code = generate_otp_code()
    # Hash lento (scrypt, mismo algoritmo que password_hash) -- no el
    # SHA-256 rápido de domain/auth/token_generator.hash_token (ADR-010/
    # ADR-011 §Seguridad: un código de 6 dígitos necesita un hash lento).
    code_hash = hash_password(code)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=REGISTRATION_CODE_TTL_MINUTES)

    email_verification_token_repository.create_code(user.id, code_hash, expires_at)
    email_service.send_registration_code_email(
        user.email, user.name, code, REGISTRATION_CODE_TTL_MINUTES
    )
