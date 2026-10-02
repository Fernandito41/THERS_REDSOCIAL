# Puerto del repositorio de temas silenciados (ADR-030-content-preferences.md).
# Sin SQLAlchemy ni Flask.

from abc import ABC, abstractmethod


class MutedTopicRepository(ABC):
    @abstractmethod
    def list_for_user(self, user_id):
        """Los temas silenciados de `user_id`, ya normalizados, más recientes
        primero. Lista vacía si no definió ninguno."""

    @abstractmethod
    def add(self, user_id, topic):
        """Agrega un tema ya normalizado. Idempotente: si ya existía devuelve
        False sin duplicar; True si se creó en esta llamada."""

    @abstractmethod
    def remove(self, user_id, topic):
        """Quita un tema ya normalizado. True si borró algo, False si ese
        usuario no lo tenía."""
