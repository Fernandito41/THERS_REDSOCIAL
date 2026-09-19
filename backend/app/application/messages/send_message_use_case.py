# Caso de uso: mandar un mensaje directo (POST /api/users/<user_id>/messages,
# ADR-013-messages-minimal-model.md). `sender_id` viene exclusivamente de
# get_jwt_identity() en la route; `content` ya llega validado en formato
# por la route (domain/messages/validators.py) -- este caso de uso solo
# orquesta, mismo patrón que application/comments/create_comment_use_case.py.

from app.application.messages.message_presenter import to_public_message
from app.domain.auth.exceptions import UserNotFoundError
from app.domain.messages.exceptions import CannotMessageSelfError


def send_message(sender_id, recipient_id, content, user_repository, message_repository):
    if sender_id == recipient_id:
        raise CannotMessageSelfError()

    recipient = user_repository.find_by_id(recipient_id)
    if recipient is None:
        raise UserNotFoundError()

    message = message_repository.create(sender_id, recipient_id, content)
    return to_public_message(message)
