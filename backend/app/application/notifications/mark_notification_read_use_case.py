# Caso de uso: marcar una notificación como leída (PATCH
# /api/notifications/<id>/read, ADR-008-notifications-minimal-model.md).
# Idempotente: si ya estaba leída, no falla -- solo confirma el estado
# actual (mismo criterio que like_post/follow_user).

from app.domain.notifications.exceptions import NotificationNotFoundError


def mark_notification_read(notification_id, user_id, notification_repository):
    found = notification_repository.mark_as_read(notification_id, user_id)
    if not found:
        raise NotificationNotFoundError()

    return {"read": True}
