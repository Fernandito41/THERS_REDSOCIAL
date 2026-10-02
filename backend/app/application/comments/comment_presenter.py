# Forma pública del objeto `comment` devuelto por create/list (ADR-006
# §Contrato) -- centralizada acá para no duplicarla entre casos de uso,
# mismo patrón que application/posts/post_presenter.py. El autor se expone
# con la misma forma reducida que en `posts` -- nunca email/phone/
# password_hash ni otros campos privados.


from app.application.auth.user_presenter import to_author_summary


def to_public_comment(comment):
    return {
        "id": str(comment.id),
        "post_id": str(comment.post_id),
        "author": to_author_summary(comment.author),
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
    }
