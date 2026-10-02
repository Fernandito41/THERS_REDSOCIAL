# Casos de uso: listar, agregar y quitar términos filtrados
# (GET/POST/DELETE /api/users/me/muted-keywords --
# ADR-020-content-filters-and-privacy-preferences.md).
#
# Los tres en el mismo módulo: son el CRUD completo de una colección pequeña
# que siempre pertenece al usuario autenticado, y separarlos en tres archivos
# de cinco líneas no aclararía nada. `user_id` sale exclusivamente de
# get_jwt_identity() en la route.

from app.domain.moderation.exceptions import (
    KeywordLimitReachedError,
    MutedKeywordNotFoundError,
)
from app.domain.moderation.keyword_matching import MAX_KEYWORDS_PER_USER


def list_muted_keywords(user_id, muted_keyword_repository):
    return {"muted_keywords": list(muted_keyword_repository.list_for_user(user_id))}


def add_muted_keyword(user_id, keyword, muted_keyword_repository):
    # `keyword` ya llega normalizado por la route (normalize_keyword), que
    # también rechazó los vacíos y los demasiado largos -- este caso de uso
    # solo orquesta, mismo patrón que create_post_use_case.
    #
    # El límite se comprueba ANTES de insertar, y solo cuenta si el término es
    # nuevo: reagregar uno que ya tenía es idempotente y nunca debe chocar con
    # el tope (si no, con la lista llena no se podría ni repetir una llamada).
    existing = muted_keyword_repository.list_for_user(user_id)
    if keyword not in existing and len(existing) >= MAX_KEYWORDS_PER_USER:
        raise KeywordLimitReachedError()

    muted_keyword_repository.add(user_id, keyword)

    # Devuelve la lista completa, no solo el término agregado: la pantalla de
    # Configuración siempre muestra la lista entera, así que ahorra una
    # segunda petición (mismo criterio que PATCH /api/posts/<id>, que devuelve
    # el post completo -- ADR-017).
    return {"muted_keywords": list(muted_keyword_repository.list_for_user(user_id))}


def remove_muted_keyword(user_id, keyword, muted_keyword_repository):
    if not muted_keyword_repository.remove(user_id, keyword):
        raise MutedKeywordNotFoundError()

    return {"muted_keywords": list(muted_keyword_repository.list_for_user(user_id))}
