# Puerto del repositorio de bloqueos y restricciones
# (ADR-029-blocked-and-restricted-accounts.md). Sin SQLAlchemy ni Flask.

from abc import ABC, abstractmethod


class RestrictionRepository(ABC):
    @abstractmethod
    def set_kind(self, owner_id, target_id, kind):
        """Fija la relación `owner -> target` en `kind`, reemplazando la que
        hubiera (bloquear a quien estaba restringido lo pasa a bloqueado)."""

    @abstractmethod
    def remove(self, owner_id, target_id, kind):
        """Borra la relación SOLO si es de ese `kind`. True si borró algo."""

    @abstractmethod
    def get_kind(self, owner_id, target_id):
        """'block' | 'restrict' | None -- lo que `owner` le tiene puesto a `target`."""

    @abstractmethod
    def is_blocked_between(self, user_a_id, user_b_id):
        """True si alguno de los dos bloqueó al otro. El bloqueo es simétrico
        a efectos de acceso."""

    @abstractmethod
    def blocked_ids_either_way(self, user_id):
        """Ids (str) de las cuentas con las que `user_id` tiene un bloqueo en
        cualquiera de los dos sentidos."""

    @abstractmethod
    def list_for_owner(self, owner_id, kind, limit):
        """Relaciones de `owner` de ese `kind`, la más reciente primero, con el
        usuario destino ya resuelto."""
