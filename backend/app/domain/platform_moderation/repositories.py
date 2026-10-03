# Puerto de la moderación de la plataforma (ADR-032, fase 2). Interfaz pura: la
# implementación con SQLAlchemy vive en `infrastructure/persistence/repositories`.

from abc import ABC, abstractmethod


class ModerationRepository(ABC):
    @abstractmethod
    def list_reports(self, status, limit, offset):
        """Devuelve `(reportes, hay_más)` con ese estado. Orden: lo crítico
        primero (ADR-038) y, dentro de cada prioridad, del más antiguo al más
        nuevo (ADR-032 §3)."""

    @abstractmethod
    def count_reports_by_target(self, targets):
        """`targets`: lista de `(tipo, id)`. Devuelve `{(tipo, id): cantidad}` con
        cuántos reportes hay sobre cada objetivo, para que quien modera vea si lo
        reportado tiene un patrón. No identifica a quien reportó."""

    @abstractmethod
    def get_report_for_update(self, report_id):
        """Devuelve el reporte bloqueado para escribir (`FOR UPDATE`), o `None`.
        El bloqueo evita que dos moderadores resuelvan el mismo reporte a la vez."""

    @abstractmethod
    def close_report(self, report, status, moderator_id, note):
        """Cierra el reporte (`actioned` o `dismissed`): fija quién, cuándo y la
        nota, y **vacía `content_snapshot`** (ADR-032 §4)."""

    @abstractmethod
    def close_other_reports_on_target(self, report, moderator_id, note):
        """Cierra como `actioned` los demás reportes abiertos sobre el mismo
        objetivo (el contenido ya no existe, no hay nada más que revisar) y vacía
        sus copias. Devuelve cuántos cerró."""

    @abstractmethod
    def get_user(self, user_id):
        """Devuelve la cuenta (entidad) o `None`."""

    @abstractmethod
    def suspend_user(self, user_id, reason):
        """Suspende la cuenta. **Idempotente:** si ya estaba suspendida se
        conserva la suspensión original (fecha y motivo). Devuelve `True` si la
        suspendió ahora."""

    @abstractmethod
    def unsuspend_user(self, user_id):
        """Levanta la suspensión. Devuelve `True` si estaba suspendida."""

    @abstractmethod
    def set_moderator(self, user_id, value):
        """Concede o retira el rol. Solo lo llama la línea de comandos."""
