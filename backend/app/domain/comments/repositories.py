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
    def list_for_post(self, post_id, limit):
        """Devuelve los `limit` comentarios más antiguos primero de un post
        (ADR-006 §Opciones consideradas: orden cronológico, no como el
        feed), con el autor ya resuelto (sin N+1)."""

    @abstractmethod
    def counts_for_posts(self, post_ids):
        """Devuelve un dict {post_id: cantidad} para varios posts a la vez
        -- evita N+1 en GET /api/posts, mismo patrón que
        LikeRepository.counts_for_posts."""
