# Caso de uso: login contra persistencia real (reemplaza la validación
# hardcodeada anterior — BACKEND_ARCHITECTURE.md §8/§9/§19, "migrar login/
# validate_user al modelo User real"). El repositorio se inyecta desde
# interfaces/routes/auth_routes.py, igual que en register_use_case.

from app.domain.auth.auth_service import verify_password
from app.domain.auth.exceptions import InvalidCredentialsError
from app.application.auth.user_presenter import to_public_user


def login_user(email, password, user_repository):
    user = user_repository.find_by_email(email)

    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()

    return to_public_user(user)
