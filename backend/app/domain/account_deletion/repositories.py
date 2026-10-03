# Puertos del repositorio de eliminación de cuenta (ADR-031-account-deletion.md).
# Vive en domain/ porque es un contrato de negocio puro -- sin SQLAlchemy ni
# Flask -- mismo patrón Repository que domain/auth/password_reset_repository.py.

from abc import ABC, abstractmethod


class AccountDeletionCodeRepository(ABC):
    @abstractmethod
    def create_code(self, user_id, code_hash, expires_at):
        """Invalida cualquier código activo previo de `user_id` (a lo sumo uno
        vigente por cuenta) y crea uno nuevo con el hash del código. Atómico
        frente a dos solicitudes simultáneas."""

    @abstractmethod
    def find_active_by_user_id(self, user_id):
        """Código vigente (no usado) de `user_id`, sin importar si ya expiró o
        agotó sus intentos; o `None`."""

    @abstractmethod
    def increment_attempts(self, code_id):
        """Suma un intento fallido y devuelve el nuevo conteo."""

    @abstractmethod
    def mark_used(self, code_id):
        """Consume el código. Devuelve `True` solo si esta llamada lo consumió
        (dos confirmaciones simultáneas no pueden usarlo las dos)."""

    @abstractmethod
    def has_recent_unused_code(self, user_id, cooldown_seconds):
        """`True` si ya hay un código sin usar creado dentro del cooldown."""


class AccountDeleter(ABC):
    @abstractmethod
    def delete_account(self, user_id):
        """Elimina la cuenta y todo lo que depende de ella **en una sola
        transacción**. Devuelve `{"media_keys": [...]}` con las claves de los
        archivos del almacenamiento de objetos (avatar y portada) que el
        llamador debe borrar **después** de que la transacción se confirme."""
