# Caso de uso: listar los posts más recientes (GET /api/posts,
# ADR-004-posts-minimal-model.md). Feed global -- todos los autores, sin
# filtrar por `follows` (esa relación no existe todavía, ver ADR-004
# §Opciones consideradas). Sin paginación real en esta versión -- límite fijo.
#
# viewer_id + like_repository (ADR-005-likes-minimal-model.md),
# comment_repository (ADR-006-comments-minimal-model.md) y
# follow_repository (ADR-007-follows-minimal-model.md): los resúmenes de
# likes/comentarios/follow se resuelven con consultas agregadas sobre todos
# los posts de la página, no una por post -- evita el N+1 que tendría
# preguntar "¿cuántos likes/comentarios tiene?"/"¿lo likeé?"/"¿sigo a este
# autor?" post por post.

from app.application.posts.post_presenter import to_public_post

DEFAULT_LIMIT = 50


def list_posts(
    post_repository, like_repository, comment_repository, follow_repository,
    viewer_id, limit=DEFAULT_LIMIT,
):
    posts = post_repository.list_recent(limit)
    post_ids = [post.id for post in posts]
    author_ids = {post.author.id for post in posts}

    counts = like_repository.counts_for_posts(post_ids)
    liked_ids = like_repository.liked_post_ids(viewer_id, post_ids)
    comment_counts = comment_repository.counts_for_posts(post_ids)
    followed_author_ids = follow_repository.followed_user_ids(viewer_id, author_ids)

    return [
        to_public_post(
            post,
            likes_count=counts.get(post.id, 0),
            liked_by_me=post.id in liked_ids,
            comments_count=comment_counts.get(post.id, 0),
            is_followed_by_me=post.author.id in followed_author_ids,
        )
        for post in posts
    ]
