# Caso de uso: listar los posts más recientes (GET /api/posts,
# ADR-004-posts-minimal-model.md). Feed global -- todos los autores, sin
# filtrar por `follows` (esa relación no existe todavía, ver ADR-004
# §Opciones consideradas). Sin paginación real en esta versión -- límite fijo.

from app.application.posts.post_presenter import to_public_post

DEFAULT_LIMIT = 50


def list_posts(post_repository, limit=DEFAULT_LIMIT):
    posts = post_repository.list_recent(limit)
    return [to_public_post(post) for post in posts]
