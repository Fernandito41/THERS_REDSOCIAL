# Puerto (interfaz) del repositorio de likes. Vive en domain/ porque es un
# contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL --
# que application/ consume y que infraestructura implementa (mismo patrón
# Repository que domain/posts/repositories.py ya estableció).

from abc import ABC, abstractmethod


class LikeRepository(ABC):
    @abstractmethod
    def add(self, post_id, user_id):
        """Registra que `user_id` dio like a `post_id`. Idempotente: si el
        like ya existía (UNIQUE (post_id, user_id)), no falla ni duplica
        (ADR-005 §Decisión, Opción A)."""

    @abstractmethod
    def remove(self, post_id, user_id):
        """Quita el like de `user_id` sobre `post_id`. Idempotente: si no
        existía, no falla."""

    @abstractmethod
    def count_for_post(self, post_id):
        """Cantidad total de likes de un post."""

    @abstractmethod
    def counts_for_posts(self, post_ids):
        """Devuelve un dict {post_id: cantidad} para varios posts a la vez
        -- evita N+1 en GET /api/posts (un post por fila de mockCapsules ya
        pedía esto, ver ADR-005 §Impacto en Backend)."""

    @abstractmethod
    def liked_post_ids(self, user_id, post_ids):
        """Devuelve el subconjunto de `post_ids` que `user_id` ya likeó --
        misma razón anti-N+1 que counts_for_posts."""
