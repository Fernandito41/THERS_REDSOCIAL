# Casos de uso: subir/quitar foto de perfil o portada (ADR-015-profile-media.md).
# `user_id` viene exclusivamente del JWT. La imagen se valida y re-codifica
# (`process_image`) ANTES de guardarse; la clave del objeto es aleatoria
# (uuid) para que nunca sea adivinable ni dependa de datos de la persona, y
# cambia en cada subida (la URL nueva evita caché vieja de la anterior).
# El objeto anterior se elimina best-effort: un fallo al borrarlo nunca
# rompe la actualización ya persistida.

import uuid

from app.application.auth.user_presenter import to_public_user
from app.domain.auth.exceptions import UserNotFoundError

_COLUMN = {"avatar": "avatar_path", "cover": "cover_path"}
_PREFIX = {"avatar": "avatars", "cover": "covers"}


def _discard(storage, key):
    if not key:
        return
    try:
        storage.delete(key)
    except Exception:  # noqa: BLE001 -- limpieza best-effort, ver cabecera
        pass


def set_profile_image(user_id, kind, raw, process, storage, user_repository, follow_repository):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    data, content_type = process(raw, kind)
    key = f"{_PREFIX[kind]}/{uuid.uuid4().hex}.webp"
    old_key = getattr(user, _COLUMN[kind])

    storage.save(key, data, content_type)
    try:
        user = user_repository.update(user_id, {_COLUMN[kind]: key})
    except Exception:
        _discard(storage, key)
        raise
    _discard(storage, old_key)

    return _present(user, follow_repository)


def remove_profile_image(user_id, kind, storage, user_repository, follow_repository):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    old_key = getattr(user, _COLUMN[kind])
    user = user_repository.update(user_id, {_COLUMN[kind]: None})
    _discard(storage, old_key)

    return _present(user, follow_repository)


def _present(user, follow_repository):
    return to_public_user(
        user,
        followers_count=follow_repository.followers_count(user.id),
        following_count=follow_repository.following_count(user.id),
    )
