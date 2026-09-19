# Caso de uso: borrar un mensaje propio (DELETE /api/messages/<message_id>,
# ADR-014-messages-ux-improvements.md). `sender_id` viene exclusivamente de
# get_jwt_identity() en la route -- solo se puede borrar un mensaje que uno
# mismo mandó.

from app.domain.messages.exceptions import MessageNotFoundError


def delete_message(message_id, sender_id, message_repository):
    deleted = message_repository.delete(message_id, sender_id)
    if not deleted:
        raise MessageNotFoundError()
    return {"deleted": True}
