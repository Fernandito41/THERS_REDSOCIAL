# Casos de uso: listar y cerrar sesiones activas
# (GET /api/sessions, DELETE /api/sessions/<id>, DELETE /api/sessions --
# ADR-025-session-registry.md).
#
# Los tres en el mismo módulo: son el CRUD completo de una colección pequeña
# que siempre pertenece al usuario autenticado. `user_id` y `current_jti` salen
# exclusivamente del JWT en la route -- nadie puede listar ni cerrar las
# sesiones de otra persona.

from app.application.sessions.session_presenter import to_public_session
from app.domain.sessions.exceptions import SessionNotFoundError

DEFAULT_LIMIT = 50


def list_sessions(user_id, current_jti, session_repository, limit=DEFAULT_LIMIT):
    sessions = session_repository.list_for_user(user_id, limit)
    return [to_public_session(session, current_jti) for session in sessions]


def revoke_session(user_id, session_id, current_jti, session_repository):
    """Cierra una sesión concreta.

    **Se permite cerrar la sesión en curso.** Es coherente: "cerrar esta
    sesión" es lo mismo que cerrar sesión, y bloquearlo obligaría al Frontend a
    distinguir dos casos sin ganar nada. El efecto es que el token con el que
    se hizo la petición deja de valer a partir de la siguiente -- la route
    informa de eso en la respuesta para que el Frontend sepa que tiene que
    redirigir a /login.
    """
    revoked_jti = session_repository.revoke(session_id, user_id)
    if revoked_jti is None:
        # Mismo 404 si no existe, si ya estaba cerrada o si es de otra persona
        # -- un 403 confirmaría que esa sesión existe (ADR-025 §Seguridad).
        raise SessionNotFoundError()

    # `was_current` le dice al Frontend si el token con el que acaba de hacer
    # esta petición ya no sirve, para que redirija a /login en vez de dejar la
    # pantalla rota en el siguiente fetch. El `jti` en sí no se expone.
    return {"revoked": True, "was_current": revoked_jti == current_jti}


def revoke_other_sessions(user_id, current_jti, session_repository):
    """Cierra todas las sesiones menos la actual.

    Nunca cierra la propia: "cerrar las demás sesiones" no debe dejar afuera a
    quien lo pide. Es la acción que alguien ejecuta justamente cuando sospecha
    que otro dispositivo tiene acceso -- hacerlo salir también sería
    contraproducente (ADR-025 §Decisión).
    """
    revoked = session_repository.revoke_all_except(user_id, current_jti)
    return {"revoked_count": revoked}
