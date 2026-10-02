# Casos de uso de bloqueo y restricción de cuentas
# (/api/users/me/blocks y /api/users/me/restrictions --
# ADR-029-blocked-and-restricted-accounts.md).
#
# `owner_id` sale exclusivamente del JWT en la route: nadie bloquea ni
# restringe en nombre de otra persona.

from app.domain.auth.exceptions import UserNotFoundError
from app.domain.restrictions.exceptions import AccountBlockedError, CannotRestrictSelfError
from app.domain.restrictions.kinds import BLOCK, RESTRICT

DEFAULT_LIMIT = 200


def to_public_restriction(restriction):
    target = restriction.target
    return {
        "user": {"id": str(target.id), "name": target.name, "username": target.username},
        "created_at": restriction.created_at.isoformat(),
    }


def _resolve_target(owner_id, user_id, username, user_repository):
    """Quién es el destino, por id o por @username. El mismo `UserNotFoundError`
    si no existe, sea cual sea la forma en que se lo nombró."""
    if user_id is not None:
        target = user_repository.find_by_id(user_id)
    else:
        found = user_repository.find_by_usernames([username.lstrip("@")])
        target = found[0] if found else None

    if target is None:
        raise UserNotFoundError()
    if str(target.id) == str(owner_id):
        raise CannotRestrictSelfError()
    return target


def block_user(
    owner_id, user_id, username, user_repository, restriction_repository, follow_repository
):
    target = _resolve_target(owner_id, user_id, username, user_repository)

    restriction_repository.set_kind(owner_id, target.id, BLOCK)

    # Bloquear corta el vínculo en los dos sentidos: ninguno sigue al otro y
    # las solicitudes pendientes se cancelan. `remove` borra la fila sea cual
    # sea su estado (ADR-022), así que cubre seguidores aceptados y pendientes.
    follow_repository.remove(owner_id, target.id)
    follow_repository.remove(target.id, owner_id)

    return {"blocked": True, "user_id": str(target.id)}


def unblock_user(owner_id, target_id, restriction_repository):
    # Idempotente: desbloquear a quien no está bloqueado no falla.
    restriction_repository.remove(owner_id, target_id, BLOCK)
    return {"blocked": False, "user_id": str(target_id)}


def restrict_user(owner_id, user_id, username, user_repository, restriction_repository):
    target = _resolve_target(owner_id, user_id, username, user_repository)

    # Restringir a quien ya está bloqueado sería bajar el nivel de protección
    # sin que nadie lo pida. Se obliga a desbloquear primero.
    if restriction_repository.get_kind(owner_id, target.id) == BLOCK:
        raise AccountBlockedError()

    restriction_repository.set_kind(owner_id, target.id, RESTRICT)
    return {"restricted": True, "user_id": str(target.id)}


def unrestrict_user(owner_id, target_id, restriction_repository):
    restriction_repository.remove(owner_id, target_id, RESTRICT)
    return {"restricted": False, "user_id": str(target_id)}


def list_blocked(owner_id, restriction_repository, limit=DEFAULT_LIMIT):
    rows = restriction_repository.list_for_owner(owner_id, BLOCK, limit)
    return [to_public_restriction(row) for row in rows]


def list_restricted(owner_id, restriction_repository, limit=DEFAULT_LIMIT):
    rows = restriction_repository.list_for_owner(owner_id, RESTRICT, limit)
    return [to_public_restriction(row) for row in rows]
