# Caso de uso: crear un post (POST /api/posts, ADR-004-posts-minimal-model.md).
# `author_id` viene exclusivamente de get_jwt_identity() en la route; `content`
# ya llega validado en formato por la route (domain/posts/validators.py) --
# este caso de uso solo orquesta, mismo patrón que application/auth/*.
#
# Desde ADR-019-mentions.md resuelve también las menciones del texto: hay que
# hacerlo DESPUÉS de crear la fila, porque una mención necesita el `post_id`
# al que apunta.

from app.application.mentions.resolve_mentions import resolve_post_mentions
from app.application.posts.post_presenter import to_public_post


def create_post(
    author_id, content, post_repository, user_repository, follow_repository,
    mention_repository, notification_repository, restriction_repository,
    is_sensitive=False,
):
    post = post_repository.create(author_id, content, is_sensitive)

    # Las menciones no autorizadas (username inexistente, o quien no acepta
    # menciones de esta persona) se descartan en silencio: el post se publica
    # igual y el @texto queda como texto plano. Nadie pierde lo que escribió
    # por haber etiquetado a quien no podía (ADR-019 §Decisión).
    mentions = resolve_post_mentions(
        post.id, author_id, content, user_repository, follow_repository,
        mention_repository, notification_repository, restriction_repository,
    )

    return to_public_post(post, mentions=mentions)
