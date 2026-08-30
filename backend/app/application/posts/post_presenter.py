# Forma pública del objeto `post` devuelto por create/list (ADR-004 §Contrato)
# -- centralizada acá para no duplicarla entre casos de uso, mismo patrón que
# application/auth/user_presenter.py. El autor se expone con la misma forma
# reducida en ambos endpoints -- nunca email/phone/password_hash/otros campos
# privados de `users`.


def to_public_post(post):
    return {
        "id": str(post.id),
        "author": {
            "id": str(post.author.id),
            "username": post.author.username,
            "name": post.author.name,
        },
        "content": post.content,
        "created_at": post.created_at.isoformat(),
    }
