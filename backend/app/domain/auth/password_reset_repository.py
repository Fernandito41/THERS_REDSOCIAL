# Puerto (interfaz) del repositorio de solicitudes de recuperación de
# contraseña. Vive en domain/auth/ (no en un domain/password_reset/ propio)
# porque es una política de la propia entidad `users` -- mismo criterio que
# domain/auth/username_policy.py (ADR-010-password-reset-otp-flow.md,
# reemplaza el flujo de enlace de ADR-009-password-reset-and-email-verification.md).
#
# Una sola fila cubre todo el ciclo de vida de una solicitud: se crea con el
# hash del código OTP, se verifica (gana una autorización temporal), y se
# consume al cambiar la contraseña -- no hay una tabla separada por etapa
# (ADR-010 §Decisión, evita duplicar entidades para el mismo concepto).

from abc import ABC, abstractmethod


class PasswordResetTokenRepository(ABC):
    @abstractmethod
    def create_code(self, user_id, code_hash, expires_at):
        """Invalida cualquier solicitud activa previa de `user_id` (a lo
        sumo una queda vigente por usuario en todo momento, ADR-010
        §Opciones consideradas) y crea una nueva con el hash del código OTP.
        Ambos pasos ocurren de forma atómica frente a solicitudes
        concurrentes (p. ej. dos "Reenviar código" simultáneos) -- ver
        implementación en infrastructure/ para el mecanismo exacto."""

    @abstractmethod
    def find_active_by_user_id(self, user_id):
        """Devuelve la solicitud vigente (no usada) de `user_id` sin
        importar si ya expiró o agotó sus intentos -- quien llama decide
        qué hacer con cada caso; o `None` si no hay ninguna."""

    @abstractmethod
    def increment_attempts(self, token_id):
        """Suma uno a `attempts` tras un código incorrecto. Devuelve el
        nuevo conteo."""

    @abstractmethod
    def mark_verified(self, token_id, reset_authorization_hash, reset_authorization_expires_at):
        """Marca la solicitud como verificada (código correcto) y le asigna
        el hash de la autorización temporal que el Frontend usará para
        POST /api/reset-password."""

    @abstractmethod
    def find_valid_by_reset_authorization_hash(self, reset_authorization_hash):
        """Devuelve la solicitud cuya autorización coincide, solo si fue
        verificada, no expiró esa autorización, y no se usó todavía -- o
        `None` en cualquier otro caso (no se distingue cuál, mismo criterio
        que el resto de tokens de esta app)."""

    @abstractmethod
    def mark_used(self, token_id):
        """Marca la solicitud como usada -- el cambio de contraseña ya se
        aplicó, invalida esta fila para cualquier uso futuro."""

    @abstractmethod
    def has_recent_unused_code(self, user_id, cooldown_seconds):
        """True si `user_id` ya tiene una solicitud sin usar creada dentro
        de los últimos `cooldown_seconds` -- sostiene el cooldown anti-spam
        de POST /api/forgot-password/"Reenviar código"."""
