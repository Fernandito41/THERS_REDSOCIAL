# Puerto (interfaz) del repositorio de posts. Vive en domain/ porque es un
# contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL --
# que application/ consume y que infraestructura implementa (mismo patrón
# Repository que domain/auth/repositories.py ya estableció para `users`).

from abc import ABC, abstractmethod


class PostRepository(ABC):
    @abstractmethod
    def create(self, author_id, content):
        """Crea un post y devuelve el registro creado (con `id`/`created_at`
        generados por PostgreSQL, y el autor ya resuelto)."""

    @abstractmethod
    def list_recent(self, limit):
        """Devuelve los `limit` posts más recientes de todos los autores,
        ordenados por `created_at` descendente, con el autor ya resuelto
        (sin N+1) -- ADR-004: feed global, sin filtrar por `follows`
        (esa relación no existe todavía)."""
