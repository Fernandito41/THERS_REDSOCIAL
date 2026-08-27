# Caso de uso: obtener el usuario autenticado (GET /api/users/me, ADR-002 §3
# — docs/architecture/ADR-002-user-profile-fields.md). `user_id` viene
# exclusivamente de get_jwt_identity() en la route -- este caso de uso no
# conoce Flask ni JWT, solo recibe el id ya resuelto (mismo patrón de
# inyección de repositorio que login_use_case/register_use_case).

from app.domain.auth.exceptions import UserNotFoundError
from app.application.auth.user_presenter import to_public_user


def get_current_user(user_id, user_repository):
    user = user_repository.find_by_id(user_id)

    if user is None:
        raise UserNotFoundError()

    return to_public_user(user)
