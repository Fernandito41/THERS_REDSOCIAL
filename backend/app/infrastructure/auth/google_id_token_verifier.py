# Adaptador del puerto `GoogleIdentityVerifier` (domain/auth/google_identity.py)
# sobre la librería oficial `google-auth` (ver requirements.txt). Único
# punto del backend que importa `google.oauth2`/`google.auth.transport` --
# domain/ y application/ no conocen esa librería, solo la interfaz
# (BACKEND_ARCHITECTURE.md §17, mismo principio que confina `resend` a
# infrastructure/email/).
#
# `id_token.verify_oauth2_token()` es la función oficial recomendada por
# Google para verificar un ID Token servidor-a-servidor (ADR-012-google-sign-in.md
# §Decisión, FASE 2/14 de la tarea): descarga y cachea en memoria las claves
# públicas reales de Google, verifica la firma RS256, y valida `iss`/`exp`
# por sí sola -- lo único que este adaptador todavía debe comprobar
# explícitamente es `aud` contra el Client ID exacto configurado para THERS
# (se lo pasa como segundo argumento, que la propia función ya usa para
# rechazar cualquier token emitido para otro Client ID -- doble chequeo,
# nunca confiamos en un solo punto de validación de audience).

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.domain.auth.exceptions import InvalidGoogleCredentialError
from app.domain.auth.google_identity import GoogleIdentity, GoogleIdentityVerifier

# Un único `Request` reutilizado entre verificaciones -- internamente cachea
# las claves públicas de Google (JWKS) en memoria y solo las refresca cuando
# expiran, en vez de pedirlas de nuevo en cada login/registro con Google.
_HTTP_REQUEST = google_requests.Request()


class GoogleIdTokenVerifier(GoogleIdentityVerifier):
    def __init__(self, client_id):
        # `client_id` es el `GOOGLE_CLIENT_ID` de THERS (Config, app/config.py)
        # -- nunca se acepta un token emitido para un Client ID distinto,
        # aunque la firma/issuer/expiración sean válidas (evita que un
        # token real de Google pero emitido para OTRA aplicación se use
        # para autenticarse en THERS).
        self._client_id = client_id

    def verify(self, credential):
        if not credential or not isinstance(credential, str):
            raise InvalidGoogleCredentialError()

        try:
            claims = google_id_token.verify_oauth2_token(
                credential, _HTTP_REQUEST, self._client_id
            )
        except Exception as exc:  # noqa: BLE001 -- ver nota abajo
            # `verify_oauth2_token` levanta `google.auth.exceptions.GoogleAuthError`
            # (firma inválida, issuer inesperado, JWKS inalcanzable) o
            # `ValueError` (token expirado, `aud` incorrecta, JWT malformado)
            # según el caso -- se capturan ambas familias con la misma
            # respuesta: ninguna distinción es útil para quien llama, y
            # nunca se debe dejar escapar la excepción real de la librería
            # (podría filtrar detalles internos hasta la respuesta HTTP).
            raise InvalidGoogleCredentialError() from exc

        # `iss` ya lo valida verify_oauth2_token() internamente (rechaza
        # cualquier valor que no sea "accounts.google.com" o
        # "https://accounts.google.com") -- no se repite acá.
        sub = claims.get("sub")
        email = claims.get("email")
        if not sub or not email:
            # Un ID Token de Google real, con el scope "openid email
            # profile" que pide el botón de Sign-In, siempre trae ambos --
            # su ausencia indicaría un token emitido con otro scope/flujo,
            # que THERS no soporta.
            raise InvalidGoogleCredentialError()

        return GoogleIdentity(
            sub=sub,
            email=email,
            email_verified=bool(claims.get("email_verified", False)),
            name=claims.get("name") or "",
        )
