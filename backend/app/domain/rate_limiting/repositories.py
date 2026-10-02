# Puerto (interfaz) del repositorio de rate limiting
# (ADR-023-rate-limiting.md). Vive en domain/ porque es un contrato de negocio
# puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL -- mismo patrón Repository
# que domain/sessions/repositories.py ya estableció.

from abc import ABC, abstractmethod


class RateLimitRepository(ABC):
    @abstractmethod
    def hit(self, scope, identity, window_seconds):
        """Registra un intento en el contador de `(scope, identity)` y devuelve
        `(attempts, retry_after_seconds)`.

        `attempts` incluye este intento. `retry_after_seconds` es cuánto falta
        para que la ventana actual venza.

        **Tiene que ser atómico.** Reiniciar la ventana vencida y sumar el
        intento ocurren en la misma operación: si fueran dos (leer, decidir,
        escribir), dos peticiones simultáneas podrían leer el mismo valor y
        escribir el mismo incremento, perdiendo uno de los dos. Y la
        concurrencia es precisamente el escenario de un ataque de fuerza bruta,
        no un caso raro (ADR-023 §Decisión).

        `identity` llega en claro y es la implementación la que decide cómo
        persistirla -- hoy la hashea, porque esta tabla solo necesita contar,
        nunca saber de quién (ADR-023 §Seguridad)."""

    @abstractmethod
    def clear(self, scope, identity):
        """Borra el contador de `(scope, identity)`.

        Lo llaman los endpoints de credenciales cuando el intento acierta: lo
        que hay que frenar es *adivinar*, no *usar*. Sin esto, alguien que entra
        y sale legítimamente varias veces acabaría bloqueado como si fuera un
        atacante (ADR-023 §Decisión, `clear_on_success`)."""

    @abstractmethod
    def purge_expired(self, older_than_seconds):
        """Borra los contadores cuya ventana venció hace más de
        `older_than_seconds`. Sin esto la tabla crece con cada IP que haya
        intentado entrar alguna vez.

        No hay proceso programado en el proyecto (DevOps sin documentación
        oficial, `CLAUDE.md` §15), así que hoy lo dispara de forma oportunista
        el propio camino de escritura -- ver la implementación
        (ADR-023 §Riesgos)."""
