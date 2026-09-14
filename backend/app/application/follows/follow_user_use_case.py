# Caso de uso: seguir a un usuario (POST /api/users/<user_id>/follow,
# ADR-007-follows-minimal-model.md). Idempotente: si ya lo seguía, no falla.

from app.domain.auth.exceptions import UserNotFoundError
from app.domain.follows.exceptions import CannotFollowSelfError


def follow_user(follower_id, followed_id, user_repository, follow_repository):
    if follower_id == followed_id:
        raise CannotFollowSelfError()

    target = user_repository.find_by_id(followed_id)
    if target is None:
        raise UserNotFoundError()

    follow_repository.add(follower_id, followed_id)
    return {"following": True}
