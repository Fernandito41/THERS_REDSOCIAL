# Puerto (interfaz) del repositorio de messages. Vive en domain/ porque es
# un contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL --
# que application/ consume y que infraestructura implementa (mismo patrón
# Repository que domain/follows/repositories.py y
# domain/notifications/repositories.py ya establecieron).

from abc import ABC, abstractmethod


class MessageRepository(ABC):
    @abstractmethod
    def create(self, sender_id, recipient_id, content):
        """Crea un mensaje de `sender_id` hacia `recipient_id`. Nunca es
        idempotente -- cada llamada es una fila nueva, mismo criterio que
        CommentRepository.create (ADR-013 §Modelo de datos: sin UNIQUE,
        dos mensajes entre las mismas personas son eventos legítimos)."""

    @abstractmethod
    def list_thread(self, user_a_id, user_b_id, limit):
        """Historial de mensajes entre `user_a_id` y `user_b_id` (ambos
        sentidos), orden cronológico ascendente (más viejo primero), límite
        fijo de `limit` mensajes más recientes -- sin paginación real,
        mismo criterio que CommentRepository.list_for_post."""

    @abstractmethod
    def mark_thread_as_read(self, recipient_id, sender_id):
        """Marca como leídos todos los mensajes que `sender_id` le mandó a
        `recipient_id` y que seguían sin leer. Efecto secundario de abrir
        un hilo (ADR-013 §Opciones consideradas) -- no es un endpoint
        propio, se llama siempre junto con `list_thread`."""

    @abstractmethod
    def list_conversations(self, user_id):
        """Lista, para cada persona con la que `user_id` tiene al menos un
        mensaje (enviado o recibido), el último mensaje del hilo y cuántos
        mensajes sin leer le mandó esa persona a `user_id`. Más reciente
        primero por fecha del último mensaje."""
