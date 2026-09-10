# Caso de uso: listar los comentarios de un post (GET
# /api/posts/<post_id>/comments, ADR-006-comments-minimal-model.md). Orden
# cronológico ascendente -- más antiguo primero (ADR-006 §Opciones
# consideradas), a diferencia del feed de posts. Sin paginación real en
# esta versión -- límite fijo.

from app.application.comments.comment_presenter import to_public_comment
from app.domain.posts.exceptions import PostNotFoundError

DEFAULT_LIMIT = 100


def list_comments(post_id, post_repository, comment_repository, limit=DEFAULT_LIMIT):
    post = post_repository.get_by_id(post_id)
    if post is None:
        raise PostNotFoundError(post_id)

    comments = comment_repository.list_for_post(post_id, limit)
    return [to_public_comment(comment) for comment in comments]
