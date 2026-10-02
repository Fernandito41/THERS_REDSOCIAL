# Puerto (interfaz) del repositorio de sessions. Vive en domain/ porque es un
# contrato de negocio puro -- sin SQLAlchemy, sin Flask, sin PostgreSQL --
# que application/ consume y que infraestructura implementa (mismo patrón
# Repository que domain/follows/repositories.py ya estableció).

from abc import ABC, abstractmethod


class SessionRepository(ABC):
    @abstractmethod
    def create(self, user_id, jti, user_agent, ip_address):
        """Registra la sesión que representa un token recién emitido. Se llama
        justo después de `create_access_token`, con el `jti` de ese token
        (ADR-025-session-registry.md)."""

    @abstractmethod
    def is_active(self, jti):
        """True si existe una sesión con ese `jti` y no está revocada.

        **Es la consulta más caliente del backend**: corre en cada petición a
        un endpoint protegido (`token_in_blocklist_loader`). Va por la UNIQUE
        `uq_sessions_jti`, así que es una búsqueda por índice -- pero sigue
        siendo una ida a la base de datos que antes no existía
        (ADR-025 §Riesgos)."""

    @abstractmethod
    def list_for_user(self, user_id, limit):
        """Las sesiones **no revocadas** de `user_id`, más reciente primero.
        Las revocadas no se listan: la fila se conserva para no perder el
        rastro, pero mostrarlas solo acumularía ruido en la pantalla
        (ADR-025 §Decisión)."""

    @abstractmethod
    def revoke(self, session_id, user_id):
        """Revoca la sesión `session_id` solo si pertenece a `user_id`.

        Devuelve el `jti` de la sesión revocada, o None si no existía, ya
        estaba revocada o era de otra persona -- la pertenencia se confirma en
        la misma sentencia que la existencia (ADR-025 §Seguridad).

        Devuelve el `jti` y no un booleano para que quien llama pueda saber si
        la sesión cerrada era **la suya** sin una segunda consulta: ese dato
        decide si el Frontend tiene que redirigir a /login. El `jti` no sale de
        application/ -- el presenter nunca lo expone."""

    @abstractmethod
    def revoke_all_except(self, user_id, keep_jti):
        """Revoca todas las sesiones vivas de `user_id` salvo la del `jti`
        indicado. Devuelve cuántas revocó.

        Nunca revoca la sesión en curso: "cerrar las demás sesiones" no debe
        desloguear a quien lo pide -- si quiere salir de esta también, el botón
        es "cerrar sesión" (ADR-025 §Decisión)."""

    @abstractmethod
    def revoke_all_for_user(self, user_id):
        """Revoca **todas** las sesiones de `user_id`, incluida la actual.
        Se usa tras un cambio de contraseña o al desactivar el 2FA: cualquier
        token emitido antes de ese cambio deja de valer (ADR-025 §Decisión)."""

    @abstractmethod
    def touch(self, jti, min_interval_seconds):
        """Actualiza `last_used_at` de la sesión, con throttle en el propio
        WHERE -- mismo criterio que UserRepository.touch_last_seen (ADR-024):
        sin él, el polling del chat escribiría en cada petición."""

    @abstractmethod
    def has_seen_user_agent(self, user_id, user_agent):
        """True si `user_id` ya tuvo antes alguna sesión con ese `user_agent`
        (revocada o no). Es la heurística de "dispositivo conocido" que
        decide si una alerta de inicio de sesión se manda o no
        (ADR-025 §Decisión; sus límites, en §Riesgos)."""
