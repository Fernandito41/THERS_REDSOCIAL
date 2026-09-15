# Puerto (interfaz) del repositorio de tokens de verificación de email.
# Misma forma que PasswordResetTokenRepository (domain/auth/password_reset_repository.py)
# -- se mantienen como dos interfaces separadas, no una genérica de "tokens
# con propósito", porque sus políticas difieren (TTL, quién puede pedirlos,
# qué pasa al consumirlos) y mezclarlas complicaría más de lo que ahorra
# (ADR-009-password-reset-and-email-verification.md §Opciones consideradas).

from abc import ABC, abstractmethod


class EmailVerificationTokenRepository(ABC):
    @abstractmethod
    def create(self, user_id, token_hash, expires_at):
        """Crea un token de verificación para `user_id`. Devuelve el
        registro creado (con `id` generado por PostgreSQL)."""

    @abstractmethod
    def find_valid_by_hash(self, token_hash):
        """Devuelve el token cuyo hash coincide, solo si no expiró y no fue
        usado todavía -- o `None` en cualquier otro caso (mismo criterio que
        PasswordResetTokenRepository.find_valid_by_hash)."""

    @abstractmethod
    def mark_used(self, token_id):
        """Marca el token como usado -- lo invalida para cualquier uso
        futuro."""

    @abstractmethod
    def has_recent_unused_token(self, user_id, cooldown_seconds):
        """True si `user_id` ya tiene un token de verificación sin usar
        creado dentro de los últimos `cooldown_seconds` -- sostiene el
        cooldown anti-spam de POST /api/send-verification-email."""
