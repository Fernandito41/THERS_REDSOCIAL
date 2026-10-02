# Excepciones de dominio para `sessions` (ADR-025-session-registry.md).


class SessionNotFoundError(Exception):
    """La sesion no existe, ya estaba cerrada, o pertenece a otra persona.
    Los tres casos se tratan igual (404, sin distinguir cual ocurrio): un 403
    confirmaria que esa sesion existe, que es informacion que no corresponde
    dar -- mismo criterio que NotificationNotFoundError (ADR-008) y
    FollowRequestNotFoundError (ADR-022)."""
