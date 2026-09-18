# Caso de uso: login contra persistencia real (reemplaza la validación
# hardcodeada anterior — BACKEND_ARCHITECTURE.md §8/§9/§19, "migrar login/
# validate_user al modelo User real"). El repositorio se inyecta desde
# interfaces/routes/auth_routes.py, igual que en register_use_case.
#
# ADR-011-mandatory-email-verification.md: credenciales correctas ya NO
# alcanzan por sí solas -- una cuenta sin verificar (`email_verified=false`)
# no puede iniciar sesión. Se comprueba DESPUÉS de validar la contraseña
# (nunca antes): así la respuesta sigue sin filtrar si un email existe
# cuando la contraseña es incorrecta (InvalidCredentialsError sigue
# ganando en ese caso), y EmailNotVerifiedError solo aparece cuando ambos
# datos ya probaron ser correctos -- no es una vía nueva para enumerar
# cuentas.
#
# ADR-012-google-sign-in.md: una cuenta creada exclusivamente vía "Continuar
# con Google" tiene `password_hash IS NULL` (nunca una contraseña vacía/
# falsa) -- `verify_password(password, None)` haría explotar
# `werkzeug.security.check_password_hash` (espera un hash con formato
# `scrypt:...`, no `None`), así que se corta antes de llamarlo, con el mismo
# `InvalidCredentialsError` genérico que cualquier otro login fallido -- sin
# revelar que esa cuenta es Google-only.

from app.domain.auth.auth_service import verify_password
from app.domain.auth.exceptions import EmailNotVerifiedError, InvalidCredentialsError
from app.application.auth.user_presenter import to_public_user


def login_user(email, password, user_repository):
    user = user_repository.find_by_email(email)

    if user is None or user.password_hash is None or not verify_password(
        password, user.password_hash
    ):
        raise InvalidCredentialsError()

    if not user.email_verified:
        raise EmailNotVerifiedError()

    return to_public_user(user)
