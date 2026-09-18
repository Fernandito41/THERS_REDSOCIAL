# Puerto (interfaz) de verificación de identidad de Google
# (ADR-012-google-sign-in.md). Mismo patrón que domain/email/sender.py
# (EmailSender): domain/ define el contrato sin conocer la librería
# concreta (`google-auth`) que lo implementa -- application/ y domain/ nunca
# importan `google.oauth2`/`google.auth` directamente, solo esta interfaz.
# infrastructure/auth/google_id_token_verifier.py la implementa con la
# librería oficial de Google.
#
# Deliberadamente mínimo: solo sabe verificar un ID Token y devolver los
# claims ya validados que THERS necesita -- no sabe nada sobre `users`,
# `user_identities`, ni ningún caso de uso concreto (esa capa de significado
# vive en application/auth/google_auth_use_case.py).

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleIdentity:
    """Claims ya verificados criptográficamente de un ID Token de Google
    (firma, `iss`, `aud`, `exp` -- ver GoogleIdentityVerifier.verify()).
    `sub` es el identificador estable de la cuenta de Google (FASE 6 de la
    tarea origen) -- nunca `email`, que en teoría podría cambiar."""

    sub: str
    email: str
    email_verified: bool
    name: str


class GoogleIdentityVerifier(ABC):
    @abstractmethod
    def verify(self, credential):
        """Verifica un ID Token de Google (`credential`, tal como lo entrega
        Google Identity Services al Frontend) contra las claves públicas
        reales de Google: firma, `iss` (`accounts.google.com` o
        `https://accounts.google.com`), `aud` (debe ser exactamente el
        `GOOGLE_CLIENT_ID` configurado para THERS -- nunca otro Client ID),
        y `exp` (no expirado). Nunca decodifica el JWT sin validar su firma.

        Devuelve un `GoogleIdentity` con los claims ya confiables. Debe
        lanzar `InvalidGoogleCredentialError` (domain/auth/exceptions.py) si
        cualquiera de esas verificaciones falla."""
