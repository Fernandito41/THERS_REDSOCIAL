# Puerto del repositorio de exportaciones (ADR-024-data-export.md). Sin
# SQLAlchemy ni Flask: application/ lo consume, infraestructura lo implementa.

from abc import ABC, abstractmethod


class DataExportRepository(ABC):
    @abstractmethod
    def collect_user_data(self, user_id):
        """Todo lo que THERS guarda sobre `user_id`, como un dict de secciones
        serializables a JSON. **Nunca** incluye secretos (hash de contraseña,
        secreto TOTP, `jti` de sesión)."""

    @abstractmethod
    def create(self, user_id, file_name, content, expires_at):
        """Guarda el archivo generado y devuelve la fila."""

    @abstractmethod
    def latest_created_at(self, user_id):
        """`created_at` de la última solicitud de `user_id`, o None."""

    @abstractmethod
    def discard_expired_content(self, user_id):
        """Pasa a NULL el contenido de las exportaciones vencidas de `user_id`."""

    @abstractmethod
    def list_for_user(self, user_id, limit):
        """Historial, más reciente primero, **sin cargar el contenido**."""

    @abstractmethod
    def get_for_user(self, export_id, user_id):
        """La exportación si existe Y es de `user_id`; None en otro caso."""

    @abstractmethod
    def mark_downloaded(self, export_id):
        """Registra una descarga."""
