# Caso de uso: listar las notificaciones del usuario autenticado (GET
# /api/notifications, ADR-008-notifications-minimal-model.md). Más reciente
# primero -- mismo orden que el feed de posts, a diferencia de los
# comentarios (ascendente). Sin paginación real en esta versión -- límite
# fijo, mismo criterio que list_comments_use_case.py.

from app.application.notifications.notification_presenter import to_public_notification

DEFAULT_LIMIT = 50


def list_notifications(user_id, notification_repository, limit=DEFAULT_LIMIT):
    notifications = notification_repository.list_for_user(user_id, limit)
    return [to_public_notification(notification) for notification in notifications]
