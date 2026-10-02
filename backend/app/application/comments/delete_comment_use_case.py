# Caso de uso: borrar un comentario propio (DELETE /api/comments/<comment_id>,
# ADR-020-comment-deletion.md). `author_id` viene exclusivamente de
# get_jwt_identity() en la route -- solo se puede borrar un comentario que
# uno mismo escribió. Mismo patrón que delete_post_use_case.py (ADR-019).

from app.domain.comments.exceptions import CommentNotFoundError


def delete_comment(comment_id, author_id, comment_repository):
    deleted = comment_repository.delete(comment_id, author_id)
    if not deleted:
        raise CommentNotFoundError()
    return {"deleted": True}
