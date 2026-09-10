# Forma pública del objeto `post` devuelto por create/list (ADR-004 §Contrato,
# extendido por ADR-005 con likes_count/liked_by_me y por ADR-006 con
# comments_count) -- centralizada acá para no duplicarla entre casos de uso,
# mismo patrón que application/auth/user_presenter.py. El autor se expone
# con la misma forma reducida en ambos endpoints -- nunca email/phone/
# password_hash/otros campos privados de `users`.


def to_public_post(post, likes_count=0, liked_by_me=False, comments_count=0):
    # Defaults en 0/False: un post recién creado (create_post_use_case.py)
    # no tiene resumen de likes/comentarios que calcular todavía (ADR-005/
    # ADR-006 §Contrato API).
    return {
        "id": str(post.id),
        "author": {
            "id": str(post.author.id),
            "username": post.author.username,
            "name": post.author.name,
        },
        "content": post.content,
        "created_at": post.created_at.isoformat(),
        "likes_count": likes_count,
        "liked_by_me": liked_by_me,
        "comments_count": comments_count,
    }
