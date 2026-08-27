# Puerto (interfaz) del repositorio de usuarios. Vive en domain/ porque es un
# contrato de negocio puro — sin SQLAlchemy, sin Flask, sin PostgreSQL — que
# application/ consume y que infraestructura implementa (Repository pattern,
# BACKEND_ARCHITECTURE.md §8/§18: "la forma exacta del repositorio... queda
# PENDIENTE", esta tarea la resuelve). Cumple la regla de dependencia: domain/
# no depende de nada externo; es infraestructura la que depende de este
# módulo, no al revés.

from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    def create(self, name, username, email, phone, country_code, birth_date, password_hash):
        """Crea un usuario y devuelve el registro creado (con `id` generado
        por PostgreSQL). Debe lanzar `EmailAlreadyExistsError` si el email ya
        existe, o `UsernameAlreadyExistsError` si el username ya existe
        (ambas en domain/auth/exceptions.py; columnas de perfil agregadas en
        ADR-002 — docs/architecture/ADR-002-user-profile-fields.md)."""

    @abstractmethod
    def find_by_email(self, email):
        """Devuelve el registro de usuario cuyo email coincide
        (case-insensitive), o `None` si no existe."""

    @abstractmethod
    def find_by_id(self, user_id):
        """Devuelve el registro de usuario cuyo `id` (UUID) coincide, o
        `None` si no existe. Usado por GET /api/users/me a partir de
        get_jwt_identity() (ADR-002 §3)."""
