# Puerto (interfaz) del repositorio de identidades externas vinculadas a un
# usuario (ADR-012-google-sign-in.md §Decisión). Mismo patrón Repository que
# domain/auth/repositories.py (UserRepository) -- domain/ no conoce
# SQLAlchemy, infraestructura implementa el contrato.
#
# `provider` es un string libre ("google" hoy) en vez de un `ENUM` de
# PostgreSQL -- mismo criterio que `notifications.type`
# (ADR-008-notifications-minimal-model.md): agregar Apple/Microsoft más
# adelante es una fila nueva en `user_identities` con otro valor de
# `provider`, sin migración de esquema.

from abc import ABC, abstractmethod


class UserIdentityRepository(ABC):
    @abstractmethod
    def find_by_provider_and_subject(self, provider, provider_subject):
        """Devuelve la fila de `user_identities` cuyo (`provider`,
        `provider_subject`) coincide exactamente, o `None` si esa identidad
        externa todavía no está vinculada a ningún usuario de THERS."""

    @abstractmethod
    def create(self, user_id, provider, provider_subject):
        """Vincula una identidad externa a `user_id`. Debe lanzar
        `IdentityAlreadyLinkedError` (domain/auth/exceptions.py) si
        (`provider`, `provider_subject`) ya está vinculada a otro usuario --
        nunca dos usuarios de THERS pueden compartir el mismo `google_sub`
        (constraint `UNIQUE (provider, provider_subject)` a nivel de
        PostgreSQL, última línea de defensa)."""
