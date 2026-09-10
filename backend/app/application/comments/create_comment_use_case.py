# Caso de uso: crear un comentario (POST /api/posts/<post_id>/comments,
# ADR-006-comments-minimal-model.md). `author_id` viene exclusivamente de
# get_jwt_identity() en la route; `content` ya llega validado en formato
# por la route (domain/comments/validators.py) -- este caso de uso solo
# orquesta, mismo patrón que application/posts/create_post_use_case.py.

from app.application.comments.comment_presenter import to_public_comment
from app.domain.posts.exceptions import PostNotFoundError


def create_comment(post_id, author_id, content, post_repository, comment_repository):
    post = post_repository.get_by_id(post_id)
    if post is None:
        raise PostNotFoundError(post_id)

    comment = comment_repository.create(post_id, author_id, content)
    return to_public_comment(comment)
