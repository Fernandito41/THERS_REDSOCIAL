# Caso de uso: listar los posts más recientes (GET /api/posts,
# ADR-004-posts-minimal-model.md). Feed global -- todos los autores, sin
# filtrar por `follows` (esa relación no existe todavía, ver ADR-004
# §Opciones consideradas). Sin paginación real en esta versión -- límite fijo.
#
# viewer_id + like_repository (ADR-005-likes-minimal-model.md): el resumen
# de likes se resuelve con dos consultas agregadas sobre todos los posts de
# la página, no una por post -- evita el N+1 que tendría preguntar
# "¿cuántos likes tiene?"/"¿lo likeé?" post por post.

from app.application.posts.post_presenter import to_public_post

DEFAULT_LIMIT = 50


def list_posts(post_repository, like_repository, viewer_id, limit=DEFAULT_LIMIT):
    posts = post_repository.list_recent(limit)
    post_ids = [post.id for post in posts]

    counts = like_repository.counts_for_posts(post_ids)
    liked_ids = like_repository.liked_post_ids(viewer_id, post_ids)

    return [
        to_public_post(
            post,
            likes_count=counts.get(post.id, 0),
            liked_by_me=post.id in liked_ids,
        )
        for post in posts
    ]
