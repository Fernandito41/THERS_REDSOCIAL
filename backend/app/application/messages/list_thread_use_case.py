# Caso de uso: ver el historial de mensajes con otro usuario
# (GET /api/users/<user_id>/messages, ADR-013-messages-minimal-model.md).
# Efecto secundario a propósito: marca como leídos los mensajes que
# `other_user_id` le mandó a `user_id` (ADR-013 §Opciones consideradas --
# "abrir el hilo" es "leerlo", no hay un PATCH separado).

from app.application.messages.message_presenter import to_public_message
from app.domain.auth.exceptions import UserNotFoundError

DEFAULT_LIMIT = 50


def list_thread(user_id, other_user_id, user_repository, message_repository, limit=DEFAULT_LIMIT):
    other_user = user_repository.find_by_id(other_user_id)
    if other_user is None:
        raise UserNotFoundError()

    messages = message_repository.list_thread(user_id, other_user_id, limit)
    message_repository.mark_thread_as_read(recipient_id=user_id, sender_id=other_user_id)

    return [to_public_message(message) for message in messages]
