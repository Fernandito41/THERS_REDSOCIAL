# Caso de uso: actualización parcial del perfil del usuario autenticado
# (PATCH /api/users/me, ADR-003 — docs/architecture/ADR-003-profile-update-contract.md).
# `user_id` viene exclusivamente de get_jwt_identity() en la route; `fields`
# ya llega validado en formato por la route (whitelist + domain/auth/validators.py)
# -- este caso de uso solo aplica las reglas de negocio que ADR-003 exige:
# - un `username` igual al actual no cuenta como cambio real (§5 de la tarea
#   origen / ADR-003 "Un valor igual al actual es válido... " no aplica
#   optimización de no-op salvo para username, que sí tiene una regla
#   explícita de "no reescribir username_changed_at si no hay cambio real").
# - cooldown de 30 días entre cambios de username (domain/auth/username_policy.py).
# No conoce Flask ni SQLAlchemy -- mismo patrón de inyección de repositorio
# que register_use_case/login_use_case/get_current_user_use_case.

from datetime import datetime, timezone

from app.application.auth.user_presenter import to_public_user
from app.domain.auth.exceptions import UserNotFoundError, UsernameChangeNotAllowedError
from app.domain.auth.username_policy import can_change_username


def update_profile(user_id, fields, user_repository):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    update_fields = dict(fields)

    if "username" in update_fields:
        new_username = update_fields["username"]
        if new_username == user.username:
            # Mismo username actual -- no se trata como un cambio real
            # (ADR-003 §5): no toca username_changed_at ni cuenta contra el
            # cooldown.
            del update_fields["username"]
        elif not can_change_username(user.username_changed_at):
            raise UsernameChangeNotAllowedError()
        else:
            update_fields["username_changed_at"] = datetime.now(timezone.utc)

    if not update_fields:
        # El único campo enviado era `username` igual al actual: nada que
        # persistir, pero la request sigue siendo válida -- se devuelve el
        # usuario tal como está (no es un 400: ya pasó la whitelist/validación
        # de formato en la route).
        return to_public_user(user)

    updated_user = user_repository.update(user_id, update_fields)
    if updated_user is None:
        raise UserNotFoundError()

    return to_public_user(updated_user)
