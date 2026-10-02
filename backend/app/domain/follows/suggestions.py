# Puerto del repositorio de cuentas sugeridas (GET /api/users/suggestions,
# ADR-030-content-preferences.md). Sin SQLAlchemy ni Flask.

from abc import ABC, abstractmethod

#: Cuántas cuentas sugiere el panel «Personas que resuenan».
DEFAULT_SUGGESTION_LIMIT = 5


class SuggestionRepository(ABC):
    @abstractmethod
    def list_for_user(self, viewer_id, limit):
        """Cuentas que `viewer_id` todavía no sigue, ordenadas por cuántos
        seguidores aceptados tienen (la más seguida primero) y, a igualdad, la
        más reciente.

        Excluye: la propia cuenta, a quien ya sigue o ya le pidió seguir, y
        cualquier cuenta con la que haya un bloqueo en cualquiera de los dos
        sentidos (ADR-029) -- sugerirle a alguien la cuenta que bloqueó, o a
        quien lo bloqueó a él, deshace el bloqueo en la práctica."""
