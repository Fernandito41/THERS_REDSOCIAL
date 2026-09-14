# Forma pública del objeto `notification` devuelto por GET /api/notifications
# (ADR-008-notifications-minimal-model.md §Contrato) -- centralizada acá para
# no duplicarla, mismo patrón que application/posts/post_presenter.py y
# application/comments/comment_presenter.py. El actor se expone con la misma
# forma reducida que en `posts`/`comments` -- nunca email/phone/
# password_hash ni otros campos privados.


def to_public_notification(notification):
    return {
        "id": str(notification.id),
        "type": notification.type,
        "actor": {
            "id": str(notification.actor.id),
            "username": notification.actor.username,
            "name": notification.actor.name,
        },
        "post_id": str(notification.post_id) if notification.post_id else None,
        # Se expone como booleano, nunca como el timestamp `read_at` crudo
        # -- mismo criterio que `username_changed_at` nunca cruza la
        # frontera HTTP tal cual (API_CONTRACT.md §5).
        "read": notification.read_at is not None,
        "created_at": notification.created_at.isoformat(),
    }
