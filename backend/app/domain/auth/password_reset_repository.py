# Puerto (interfaz) del repositorio de tokens de recuperación de contraseña.
# Vive en domain/auth/ (no en un domain/password_reset/ propio) porque es
# una política de la propia entidad `users` -- mismo criterio que
# domain/auth/username_policy.py ya vive junto al resto de reglas de auth en
# vez de en un dominio separado (ADR-009-password-reset-and-email-verification.md).

from abc import ABC, abstractmethod


class PasswordResetTokenRepository(ABC):
    @abstractmethod
    def create(self, user_id, token_hash, expires_at):
        """Crea un token de recuperación para `user_id`. Devuelve el
        registro creado (con `id` generado por PostgreSQL)."""

    @abstractmethod
    def find_valid_by_hash(self, token_hash):
        """Devuelve el token cuyo hash coincide, solo si no expiró y no fue
        usado todavía -- o `None` si no existe, expiró, o ya se usó (los
        tres casos se tratan igual por quien llama, ADR-009 §Contrato API,
        para no revelar cuál de los tres ocurrió)."""

    @abstractmethod
    def mark_used(self, token_id):
        """Marca el token como usado (`used_at`) -- lo invalida para
        cualquier uso futuro, incluso si técnicamente no había expirado
        todavía."""

    @abstractmethod
    def invalidate_all_for_user(self, user_id):
        """Marca como usados todos los tokens de recuperación vigentes de
        `user_id` -- se invoca al completar un reset exitoso (ADR-009
        §Decisión): si existían otros enlaces de recuperación sin usar
        (p. ej. de un pedido anterior que el usuario nunca abrió), dejan de
        servir apenas la contraseña cambia."""

    @abstractmethod
    def has_recent_unused_token(self, user_id, cooldown_seconds):
        """True si `user_id` ya tiene un token sin usar creado dentro de los
        últimos `cooldown_seconds` -- sostiene el cooldown anti-spam de
        POST /api/forgot-password (ADR-009 §Seguridad), sin importar si ese
        token ya expiró o no."""
