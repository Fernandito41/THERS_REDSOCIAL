# Forma pública del objeto `comment` devuelto por create/list (ADR-006
# §Contrato) -- centralizada acá para no duplicarla entre casos de uso,
# mismo patrón que application/posts/post_presenter.py. El autor se expone
# con la misma forma reducida que en `posts` -- nunca email/phone/
# password_hash ni otros campos privados.


from app.application.mentions.mention_presenter import to_public_mentions


def to_public_comment(comment, mentions=None):
    return {
        "id": str(comment.id),
        "post_id": str(comment.post_id),
        "author": {
            "id": str(comment.author.id),
            "username": comment.author.username,
            "name": comment.author.name,
        },
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
        # Mismo criterio y misma forma que `post.mentions` (ADR-023).
        "mentions": to_public_mentions(mentions),
        # Booleano, nunca el timestamp `edited_at` crudo -- mismo criterio
        # que `read` en messages/notifications (ADR-021-content-editing.md).
        "edited": comment.edited_at is not None,
    }
