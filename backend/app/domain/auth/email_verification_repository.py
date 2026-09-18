# Puerto (interfaz) del repositorio de códigos de verificación de email al
# registrarse. Vive en domain/auth/ (no en un domain/registration/ propio)
# porque es una política de la propia entidad `users` -- mismo criterio que
# domain/auth/password_reset_repository.py
# (ADR-011-mandatory-email-verification.md, reemplaza el flujo de enlace de
# ADR-009-password-reset-and-email-verification.md).
#
# Se mantiene como interfaz separada de PasswordResetTokenRepository, no una
# genérica de "tokens OTP con propósito" -- mezclarlas facilitaría por
# accidente que un código de un flujo sirviera para el otro, exactamente lo
# que ADR-011 §Seguridad prohíbe explícitamente. A diferencia de la
# recuperación de contraseña, verificar el email es de una sola etapa: no
# hay una "autorización temporal" posterior, el propio acierto del código ya
# es la acción final (marca `email_verified = true`).

from abc import ABC, abstractmethod


class EmailVerificationTokenRepository(ABC):
    @abstractmethod
    def create_code(self, user_id, code_hash, expires_at):
        """Invalida cualquier código activo previo de `user_id` (a lo sumo
        uno vigente por usuario en todo momento) y crea uno nuevo. Ambos
        pasos ocurren de forma atómica frente a solicitudes concurrentes
        (p. ej. dos "Reenviar código" simultáneos) -- ver implementación en
        infrastructure/ para el mecanismo exacto."""

    @abstractmethod
    def find_active_by_user_id(self, user_id):
        """Devuelve el código vigente (no usado) de `user_id` sin importar
        si ya expiró o agotó sus intentos -- quien llama decide qué hacer
        con cada caso; o `None` si no hay ninguno."""

    @abstractmethod
    def increment_attempts(self, token_id):
        """Suma uno a `attempts` tras un código incorrecto. Devuelve el
        nuevo conteo."""

    @abstractmethod
    def mark_used(self, token_id):
        """Marca el código como usado -- el email ya quedó verificado,
        invalida esta fila para cualquier uso futuro."""

    @abstractmethod
    def has_recent_unused_code(self, user_id, cooldown_seconds):
        """True si `user_id` ya tiene un código sin usar creado dentro de
        los últimos `cooldown_seconds` -- sostiene el cooldown anti-spam de
        POST /api/register/"Reenviar código"."""
