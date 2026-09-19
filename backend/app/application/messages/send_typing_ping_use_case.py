# Caso de uso: avisar que se le está escribiendo a otro usuario
# (POST /api/users/<user_id>/typing, ADR-014-messages-ux-improvements.md).
# `sender_id` viene exclusivamente de get_jwt_identity(); `recipient_id`
# viene de la URL.

from app.domain.auth.exceptions import UserNotFoundError


def send_typing_ping(sender_id, recipient_id, user_repository, typing_repository):
    recipient = user_repository.find_by_id(recipient_id)
    if recipient is None:
        raise UserNotFoundError()

    typing_repository.ping(sender_id, recipient_id)
