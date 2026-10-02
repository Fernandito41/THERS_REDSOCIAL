# Forma pública de una sesión activa, devuelta por GET /api/sessions
# (ADR-025-session-registry.md §Contrato API).
#
# El `jti` **nunca** cruza la frontera HTTP: es el identificador que
# `token_in_blocklist_loader` usa para validar cada petición, así que exponerlo
# convertiría la lista de sesiones en una lista de identificadores de token.
# Para revocar se usa el `id` de la fila, que no sirve para autenticar nada.
#
# `user_agent` se expone **crudo**, sin parsear a "Chrome en Windows": el
# servidor no tiene una base de datos de user agents y adivinar produciría
# errores ("Chrome" donde hay un Edge). Es el Frontend quien lo resume, y si no
# lo reconoce muestra el texto tal cual -- que sigue siendo más útil que una
# etiqueta equivocada.


def to_public_session(session, current_jti=None):
    return {
        "id": str(session.id),
        "user_agent": session.user_agent,
        "ip_address": session.ip_address,
        "created_at": session.created_at.isoformat(),
        "last_used_at": session.last_used_at.isoformat() if session.last_used_at else None,
        # Para que el Frontend pueda marcarla como "Este dispositivo" y no
        # ofrecer cerrarla con el mismo botón que las demás. Se calcula
        # comparando con el `jti` de quien pregunta -- ese valor no se expone.
        "is_current": current_jti is not None and session.jti == current_jti,
    }
