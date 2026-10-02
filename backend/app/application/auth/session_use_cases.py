# Casos de uso de sesión (ADR-017-jwt-session-policy.md): emitir al iniciar
# sesión, rotar el refresh token, y cerrar sesión.

import uuid

from app.domain.auth.exceptions import InvalidRefreshTokenError
from app.domain.auth.refresh_token_repository import RotationStatus
from app.domain.auth.token_generator import hash_token


def issue_session(user_id, refresh_token_repository, tokens):
    """Abre una sesión nueva (una familia de refresh tokens). Lo usan
    `POST /api/login` y `POST /api/auth/google`. Devuelve los dos tokens;
    el llamador los agrega al cuerpo de su respuesta (ADR-017 §2.1)."""
    family_id = uuid.uuid4()
    refresh_token, jti, expires_at = tokens.new_refresh(user_id, family_id)
    refresh_token_repository.create(user_id, family_id, hash_token(jti), expires_at)

    return {"token": tokens.new_access(user_id), "refresh_token": refresh_token}


def rotate_session(user_id, presented_jti, family_claim, refresh_token_repository, user_repository, tokens):
    """Consume el refresh token presentado y emite un access y un refresh
    nuevos de la misma familia. `user_id`, `presented_jti` y `family_claim`
    salen de los claims ya verificados (firma y expiración) del token
    presentado. Ante cualquier problema lanza `InvalidRefreshTokenError`
    (-> 401 sin detalle)."""
    if not user_id or not presented_jti or not family_claim:
        raise InvalidRefreshTokenError()

    # El sucesor se firma ANTES de rotar: la rotación necesita su hash y todo
    # ocurre en una sola transacción. Si la rotación falla, este JWT se
    # descarta sin haberse persistido ni entregado.
    new_token, new_jti, new_expires_at = tokens.new_refresh(user_id, family_claim)

    result = refresh_token_repository.rotate(
        hash_token(presented_jti), hash_token(new_jti), new_expires_at
    )

    if result.status is not RotationStatus.OK:
        # INVALID o REUSED (en este último caso la familia ya quedó revocada).
        raise InvalidRefreshTokenError()

    # Defensa en profundidad: el `fid` firmado debe coincidir con la fila, y
    # el usuario debe seguir existiendo.
    if str(result.family_id) != str(family_claim) or str(result.user_id) != str(user_id):
        refresh_token_repository.revoke_all_for_user(result.user_id)
        raise InvalidRefreshTokenError()

    if user_repository.find_by_id(result.user_id) is None:
        refresh_token_repository.revoke_all_for_user(result.user_id)
        raise InvalidRefreshTokenError()

    return {"token": tokens.new_access(user_id), "refresh_token": new_token}


def logout_session(presented_jti, refresh_token_repository):
    """Revoca la sesión (familia) del refresh token presentado. Idempotente:
    no distingue "ya revocada" de "nunca existió" (ADR-017 §2, logout)."""
    if presented_jti:
        refresh_token_repository.revoke_family_of(hash_token(presented_jti))
