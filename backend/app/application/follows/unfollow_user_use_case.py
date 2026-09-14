# Caso de uso: dejar de seguir a un usuario (DELETE /api/users/<user_id>/follow,
# ADR-007-follows-minimal-model.md). Idempotente: si no lo seguía, no falla.
# Dejar de seguirse a uno mismo es un no-op inofensivo -- la restricción de
# auto-seguimiento solo importa para *empezar* a seguir (ADR-007 §Contrato).

from app.domain.auth.exceptions import UserNotFoundError


def unfollow_user(follower_id, followed_id, user_repository, follow_repository):
    target = user_repository.find_by_id(followed_id)
    if target is None:
        raise UserNotFoundError()

    follow_repository.remove(follower_id, followed_id)
    return {"following": False}
