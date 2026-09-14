# Puerto (interfaz) del repositorio de notifications. Vive en domain/ porque
# es un contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin
# PostgreSQL -- que application/ consume y que infraestructura implementa
# (mismo patrón Repository que domain/likes/repositories.py,
# domain/comments/repositories.py y domain/follows/repositories.py ya
# establecieron).

from abc import ABC, abstractmethod


class NotificationRepository(ABC):
    @abstractmethod
    def create(self, recipient_id, actor_id, notification_type, post_id=None):
        """Crea una notificación para `recipient_id`, disparada por
        `actor_id`. `post_id` es opcional -- solo aplica a los tipos 'like'/
        'comment' (ADR-008-notifications-minimal-model.md §Modelo de datos);
        en 'follow' viaja como None. A diferencia de `LikeRepository.add`/
        `FollowRepository.add`, este método no es idempotente por sí mismo
        -- quien llama (los casos de uso de likes/comments/follows) ya
        decide de antemano si corresponde crear la notificación (solo en la
        transición real, nunca en un no-op idempotente) antes de invocarlo."""

    @abstractmethod
    def list_for_user(self, user_id, limit):
        """Lista las notificaciones donde `user_id` es el destinatario, más
        reciente primero. Sin paginación real en esta versión -- límite
        fijo (mismo criterio que `CommentRepository.list_for_post`)."""

    @abstractmethod
    def mark_as_read(self, notification_id, user_id):
        """Marca como leída una notificación, solo si pertenece a
        `user_id`. Devuelve True si existía y era de `user_id` (idempotente:
        si ya estaba leída, no falla); False si no existe o pertenece a otro
        usuario -- el caso de uso traduce False a 404 sin distinguir cuál de
        los dos ocurrió, mismo criterio que InvalidCredentialsError en login
        (no revelar qué existe)."""
