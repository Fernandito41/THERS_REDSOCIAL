# Caso de uso: quitar el like de un post (DELETE /api/posts/<post_id>/like,
# ADR-005-likes-minimal-model.md). Idempotente: si el usuario no lo había
# likeado, no falla -- solo devuelve el estado actual.

from app.domain.posts.exceptions import PostNotFoundError


def unlike_post(post_id, user_id, post_repository, like_repository):
    post = post_repository.get_by_id(post_id)
    if post is None:
        raise PostNotFoundError(post_id)

    like_repository.remove(post_id, user_id)

    return {
        "likes_count": like_repository.count_for_post(post_id),
        "liked_by_me": False,
    }
