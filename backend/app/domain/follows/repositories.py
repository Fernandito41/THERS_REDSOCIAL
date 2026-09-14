# Puerto (interfaz) del repositorio de follows. Vive en domain/ porque es un
# contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL --
# que application/ consume y que infraestructura implementa (mismo patrón
# Repository que domain/likes/repositories.py y domain/comments/repositories.py
# ya establecieron).

from abc import ABC, abstractmethod


class FollowRepository(ABC):
    @abstractmethod
    def add(self, follower_id, followed_id):
        """Registra que `follower_id` sigue a `followed_id`. Idempotente:
        si el follow ya existía (UNIQUE (follower_id, followed_id)), no
        falla ni duplica (ADR-007 §Decisión, mismo criterio que ADR-005).
        Devuelve True si el follow se creó en esta llamada, False si ya
        existía -- ADR-008-notifications-minimal-model.md lo usa para no
        notificar en una repetición idempotente de un follow ya hecho."""

    @abstractmethod
    def remove(self, follower_id, followed_id):
        """Deja de seguir. Idempotente: si no existía, no falla."""

    @abstractmethod
    def is_following(self, follower_id, followed_id):
        """True si `follower_id` sigue a `followed_id`."""

    @abstractmethod
    def followers_count(self, user_id):
        """Cantidad de usuarios que siguen a `user_id`."""

    @abstractmethod
    def following_count(self, user_id):
        """Cantidad de usuarios que `user_id` sigue."""

    @abstractmethod
    def followed_user_ids(self, follower_id, candidate_ids):
        """Devuelve el subconjunto de `candidate_ids` que `follower_id` ya
        sigue -- evita N+1 al resolver `is_followed_by_me` en GET /api/posts,
        mismo patrón que LikeRepository.liked_post_ids."""
