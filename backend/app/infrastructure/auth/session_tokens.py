# Emisión de los tokens JWT de sesión (ADR-017-jwt-session-policy.md). Único
# punto del backend que llama a `create_access_token`/`create_refresh_token`
# de flask_jwt_extended -- `application/` solo conoce esta clase, no la
# librería (mismo principio que confina Resend/SQLAlchemy a infrastructure/).

from datetime import datetime, timezone

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token

# Claim propio del refresh token: familia (cadena de renovaciones de un login).
# Va firmado dentro del JWT, así que se puede confiar en él al renovar.
FAMILY_CLAIM = "fid"


class JwtSessionTokens:
    def new_access(self, user_id):
        # `identity` = id (UUID) del usuario, igual que siempre (BACKEND_
        # ARCHITECTURE.md §9): ningún endpoint protegido cambia.
        return create_access_token(identity=str(user_id))

    def new_refresh(self, user_id, family_id):
        """Devuelve `(token, jti, expires_at)`. El `jti` es lo único que se
        hashea y persiste (ADR-017 §4.1); el token en claro solo viaja al
        cliente."""
        token = create_refresh_token(
            identity=str(user_id), additional_claims={FAMILY_CLAIM: str(family_id)}
        )
        claims = decode_token(token)
        expires_at = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
        return token, claims["jti"], expires_at
