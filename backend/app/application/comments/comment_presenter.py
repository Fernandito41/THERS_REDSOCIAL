# Forma pública del objeto `comment` devuelto por create/list (ADR-006
# §Contrato) -- centralizada acá para no duplicarla entre casos de uso,
# mismo patrón que application/posts/post_presenter.py. El autor se expone
# con la misma forma reducida que en `posts` -- nunca email/phone/
# password_hash ni otros campos privados.


def to_public_comment(comment):
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
    }
