# Puerto (interfaz) del repositorio de comentarios. Vive en domain/ porque es
# un contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL --
# que application/ consume y que infraestructura implementa (mismo patrón
# Repository que domain/posts/repositories.py y domain/likes/repositories.py
# ya establecieron).

from abc import ABC, abstractmethod


class CommentRepository(ABC):
    @abstractmethod
    def create(self, post_id, author_id, content):
        """Crea un comentario y devuelve el registro creado (con `id`/
        `created_at` generados por PostgreSQL, y el autor ya resuelto)."""

    @abstractmethod
    def list_for_post(self, post_id, limit, viewer_id, muted_keywords=()):
        """Devuelve los `limit` comentarios más antiguos primero de un post
        (ADR-006 §Opciones consideradas: orden cronológico, no como el
        feed), con el autor ya resuelto (sin N+1), **filtrados para
        `viewer_id`**.

        Desde ADR-024-content-filters-and-privacy-preferences.md se excluyen
        los comentarios que contienen alguno de los `muted_keywords` del
        espectador, y los que la lista de ofensivos del sistema detecta *si el
        dueño de la publicación activó* `hide_offensive_comments`. Nunca se le
        oculta a alguien su propio comentario."""

    @abstractmethod
    def counts_for_posts(self, post_ids, viewer_id, muted_keywords=()):
        """Devuelve un dict {post_id: cantidad} para varios posts a la vez
        -- evita N+1 en GET /api/posts, mismo patrón que
        LikeRepository.counts_for_posts.

        Aplica **el mismo filtro** que `list_for_post` (ADR-024): el contador
        de la tarjeta tiene que coincidir con lo que el panel muestra."""

    @abstractmethod
    def delete(self, comment_id, author_id):
        """Borra el comentario `comment_id` solo si su autor es `author_id`.
        Devuelve True si borró algo, False si no existía o era de otro autor
        -- la pertenencia se confirma en la misma operación que la
        existencia (ADR-020-comment-deletion.md, mismo criterio que
        PostRepository.delete, ADR-019)."""

    @abstractmethod
    def update_content(self, comment_id, author_id, content):
        """Reemplaza el texto del comentario `comment_id` solo si su autor es
        `author_id`, y marca `edited_at`. Devuelve el comentario actualizado
        (con el autor ya resuelto), o None si no existía o era de otro autor
        -- mismo criterio que PostRepository.update_content
        (ADR-021-content-editing.md)."""
