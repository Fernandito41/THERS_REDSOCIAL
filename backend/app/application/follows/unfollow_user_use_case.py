# Caso de uso: dejar de seguir a un usuario (DELETE /api/users/<user_id>/follow,
# ADR-007-follows-minimal-model.md). Idempotente: si no lo seguía, no falla.
# Dejar de seguirse a uno mismo es un no-op inofensivo -- la restricción de
# auto-seguimiento solo importa para *empezar* a seguir (ADR-007 §Contrato).

from app.domain.auth.exceptions import UserNotFoundError


def unfollow_user(follower_id, followed_id, user_repository, follow_repository):
    target = user_repository.find_by_id(followed_id)
    if target is None:
        raise UserNotFoundError()

    # Borra la fila sea cual sea su estado: el mismo DELETE sirve para dejar
    # de seguir y para cancelar una solicitud que todavía no respondieron
    # (ADR-018 §Decisión) -- son el mismo gesto desde el Frontend ("ya no
    # quiero esta relación") y no hace falta un endpoint aparte.
    follow_repository.remove(follower_id, followed_id)
    return {"following": False, "follow_status": None}
