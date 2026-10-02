# Caso de uso: borrar una publicación propia (DELETE /api/posts/<post_id>,
# ADR-015-post-deletion.md). `author_id` viene exclusivamente de
# get_jwt_identity() en la route -- solo se puede borrar un post que uno
# mismo publicó. Mismo patrón que delete_message_use_case.py (ADR-014).

from app.domain.posts.exceptions import PostNotFoundError


def delete_post(post_id, author_id, post_repository):
    deleted = post_repository.delete(post_id, author_id)
    if not deleted:
        # Mismo error tanto si el id no existe como si existe pero es de
        # otro autor -- la route los traduce al mismo 404, sin revelar cuál
        # de los dos ocurrió (ADR-015 §Seguridad).
        raise PostNotFoundError()
    return {"deleted": True}
