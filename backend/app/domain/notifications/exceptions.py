# Excepciones de dominio para `notifications` (ADR-008-notifications-minimal-model.md).


class NotificationNotFoundError(Exception):
    """La notificación no existe, o existe pero no pertenece al usuario
    autenticado (`get_jwt_identity()`) -- ambos casos se tratan igual (404,
    sin distinguir cuál ocurrió) para no revelar la existencia de
    notificaciones de otro usuario, mismo criterio que
    InvalidCredentialsError (domain/auth/exceptions.py) no distingue email
    inexistente de password incorrecta."""
