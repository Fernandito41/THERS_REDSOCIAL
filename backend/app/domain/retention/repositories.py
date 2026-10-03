# Puerto del borrado por antigüedad (ADR-037-data-retention.md).

from abc import ABC, abstractmethod


class RetentionRepository(ABC):
    @abstractmethod
    def purge_older_than(self, cutoff):
        """Borra, en una sola transacción, los datos técnicos más viejos que `cutoff`
        (un instante con zona horaria) según `domain/retention/policy.py`.

        Devuelve un dict `{tabla: filas_borradas}` con SOLO conteos: nunca devuelve ni
        registra el contenido (IP, agentes de usuario, correos) de lo borrado.

        No toca cuentas, contenido de las personas ni sesiones vigentes."""
