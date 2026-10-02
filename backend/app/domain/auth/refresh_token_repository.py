# Puerto (interfaz) del repositorio de refresh tokens
# (ADR-017-jwt-session-policy.md). Vive en domain/auth/ junto a los puertos de
# recuperación de contraseña y verificación de email: es una política de la
# propia entidad `users`.
#
# Modelo (ADR-017 §2): cada login abre una "familia" de tokens. Cada uso del
# refresh consume el token vigente y emite uno nuevo de la misma familia;
# reusar uno ya consumido revoca toda la familia. Solo se persiste el HASH del
# `jti` del token (nunca el token ni su `jti` en claro, ADR-017 §4.1).

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class RotationStatus(Enum):
    OK = "ok"
    REUSED = "reused"
    INVALID = "invalid"


@dataclass(frozen=True)
class RotationResult:
    status: RotationStatus
    # Solo con `OK`: de quién es el token y a qué familia pertenece.
    user_id: object = None
    family_id: object = None


class RefreshTokenRepository(ABC):
    @abstractmethod
    def create(self, user_id, family_id, token_hash, expires_at):
        """Registra un refresh token nuevo y vigente. Falla (IntegrityError
        de infraestructura) si la familia ya tiene otro token activo -- ese
        es el índice único parcial de ADR-017 §4.3."""

    @abstractmethod
    def rotate(self, token_hash, new_token_hash, new_expires_at):
        """Consume de forma ATÓMICA el token `token_hash` y registra su
        sucesor en la misma familia. Devuelve un `RotationResult`:
        - `OK` más los datos de la familia, si el token estaba vigente;
        - `REUSED` si ya había sido consumido -- en ese caso revoca la
          familia entera antes de devolver;
        - `INVALID` si no existe, está revocado o expiró.
        Concurrente-seguro: dos rotaciones simultáneas del mismo token
        nunca producen dos sucesores (ADR-017 §4.3)."""

    @abstractmethod
    def revoke_family_of(self, token_hash):
        """Revoca todos los tokens de la familia a la que pertenece
        `token_hash`. Idempotente: devuelve `False` si el token no existe,
        `True` en cualquier otro caso (incluida una familia ya revocada)."""

    @abstractmethod
    def revoke_all_for_user(self, user_id):
        """Revoca todas las familias vigentes de `user_id` (p. ej. tras
        cambiar la contraseña, ADR-017 §7 decisión 1)."""
