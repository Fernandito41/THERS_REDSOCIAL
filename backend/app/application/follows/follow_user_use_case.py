# Caso de uso: seguir a un usuario (POST /api/users/<user_id>/follow,
# ADR-007-follows-minimal-model.md). Idempotente: si ya lo seguía, no falla.

from app.domain.auth.exceptions import UserNotFoundError
from app.domain.follows.exceptions import CannotFollowSelfError


def follow_user(follower_id, followed_id, user_repository, follow_repository, notification_repository):
    if follower_id == followed_id:
        raise CannotFollowSelfError()

    target = user_repository.find_by_id(followed_id)
    if target is None:
        raise UserNotFoundError()

    was_created = follow_repository.add(follower_id, followed_id)

    # Solo notifica en la transición real (nuevo follow, no un POST
    # repetido sobre un follow ya existente) -- nunca hace falta el guard
    # de auto-seguimiento acá, ya lo cubrió CannotFollowSelfError arriba
    # (ADR-008-notifications-minimal-model.md §No objetivos).
    if was_created:
        notification_repository.create(
            recipient_id=followed_id, actor_id=follower_id, notification_type="follow"
        )

    return {"following": True}
