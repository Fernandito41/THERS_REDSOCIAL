# Caso de uso: editar un comentario propio (PATCH /api/comments/<comment_id>,
# ADR-021-content-editing.md). `author_id` viene exclusivamente de
# get_jwt_identity() en la route; `content` ya llega validado en formato por
# la route (domain/comments/validators.py, mismo validador que crear un
# comentario) -- mismo patrón que delete_comment_use_case.py (ADR-020).

from app.application.comments.comment_presenter import to_public_comment
from app.application.mentions.resolve_mentions import resolve_comment_mentions
from app.domain.comments.exceptions import CommentNotFoundError


def update_comment(
    comment_id, author_id, content, comment_repository, user_repository,
    follow_repository, mention_repository, notification_repository,
    restriction_repository,
):
    comment = comment_repository.update_content(comment_id, author_id, content)
    if comment is None:
        raise CommentNotFoundError()

    # Las menciones se recalculan sobre el texto nuevo (ADR-023 §Decisión):
    # las que ya no están se borran, las nuevas se crean y se notifican. A
    # quien ya estaba mencionado no se le vuelve a notificar.
    #
    # No se revisa la visibilidad del post: editar un comentario propio ya
    # publicado sigue permitido aunque el dueño del post se haya vuelto privado
    # después -- el comentario ya está ahí, y corregirlo no expone nada nuevo
    # (ADR-022 §Decisión).
    mentions = resolve_comment_mentions(
        comment.id, comment.post_id, author_id, content, user_repository,
        follow_repository, mention_repository, notification_repository,
        restriction_repository,
    )

    # No se notifica al autor de la publicación: la notificación "comentó tu
    # publicación" (ADR-008) ya se emitió al crear el comentario y editarlo no
    # es un evento social nuevo (ADR-021 §Decisión). Tampoco hay contador que
    # mover -- `comments_count` no cambia al editar.
    return to_public_comment(comment, mentions=mentions)
