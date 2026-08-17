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
    def create(self, name, email, password_hash):
        """Crea un usuario y devuelve el registro creado (con `id` generado
        por PostgreSQL). Debe lanzar `EmailAlreadyExistsError`
        (ver domain/auth/exceptions.py) si el email ya existe."""

    @abstractmethod
    def find_by_email(self, email):
        """Devuelve el registro de usuario cuyo email coincide
        (case-insensitive), o `None` si no existe."""
