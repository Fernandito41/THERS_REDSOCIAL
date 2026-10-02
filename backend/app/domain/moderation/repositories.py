# Puerto (interfaz) del repositorio de muted_keywords
# (ADR-020-content-filters-and-privacy-preferences.md). Vive en domain/ porque
# es un contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL
# -- mismo patrón Repository que domain/follows/repositories.py.

from abc import ABC, abstractmethod


class MutedKeywordRepository(ABC):
    @abstractmethod
    def list_for_user(self, user_id):
        """Los términos filtrados de `user_id`, ya normalizados, más
        recientes primero. Lista vacía si no definió ninguno."""

    @abstractmethod
    def count_for_user(self, user_id):
        """Cuántos términos tiene -- sostiene el límite
        MAX_KEYWORDS_PER_USER sin traerse la lista entera."""

    @abstractmethod
    def add(self, user_id, keyword):
        """Agrega un término ya normalizado. Idempotente: si ya existía
        (UNIQUE (user_id, keyword)) no falla ni duplica -- devuelve False;
        True si se creó en esta llamada. Mismo criterio que
        FollowRepository.add/LikeRepository.add (ADR-005/ADR-007)."""

    @abstractmethod
    def remove(self, user_id, keyword):
        """Quita un término ya normalizado. Devuelve True si borró algo,
        False si ese usuario no lo tenía -- el caso de uso traduce False a
        404."""
