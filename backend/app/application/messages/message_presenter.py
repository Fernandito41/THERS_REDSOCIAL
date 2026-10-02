# Forma pública del objeto `message` devuelto por POST/GET
# /api/users/<id>/messages (ADR-013-messages-minimal-model.md §Contrato) --
# centralizada acá para no duplicarla, mismo patrón que
# application/notifications/notification_presenter.py.


from app.application.auth.user_presenter import to_author_summary


def to_public_message(message):
    return {
        "id": str(message.id),
        "sender_id": str(message.sender_id),
        "recipient_id": str(message.recipient_id),
        "content": message.content,
        # Se expone como booleano, nunca como el timestamp `read_at` crudo
        # -- mismo criterio que `notifications.read` (ADR-008).
        "read": message.read_at is not None,
        "created_at": message.created_at.isoformat(),
    }


def to_public_conversation(conversation):
    other_user = conversation["other_user"]
    last_message = conversation["last_message"]
    return {
        "user": to_author_summary(other_user),
        "last_message": {
            "content": last_message.content,
            "sender_id": str(last_message.sender_id),
            "created_at": last_message.created_at.isoformat(),
        },
        "unread_count": conversation["unread_count"],
    }
