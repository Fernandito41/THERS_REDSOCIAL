# Caso de uso: crear un post (POST /api/posts, ADR-004-posts-minimal-model.md).
# `author_id` viene exclusivamente de get_jwt_identity() en la route; `content`
# ya llega validado en formato por la route (domain/posts/validators.py) --
# este caso de uso solo orquesta, mismo patrón que application/auth/*.

from app.application.posts.post_presenter import to_public_post


def create_post(author_id, content, post_repository):
    post = post_repository.create(author_id, content)
    return to_public_post(post)
