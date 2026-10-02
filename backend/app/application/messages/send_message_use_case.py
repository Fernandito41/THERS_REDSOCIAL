# Caso de uso: mandar un mensaje directo (POST /api/users/<user_id>/messages,
# ADR-013-messages-minimal-model.md). `sender_id` viene exclusivamente de
# get_jwt_identity() en la route; `content` ya llega validado en formato
# por la route (domain/messages/validators.py) -- este caso de uso solo
# orquesta, mismo patrón que application/comments/create_comment_use_case.py.
#
# Desde ADR-024-content-filters-and-privacy-preferences.md respeta además la
# preferencia `who_can_message` del destinatario.

from app.application.messages.message_presenter import to_public_message
from app.domain.auth.exceptions import UserNotFoundError
from app.domain.follows.follow_status import ACCEPTED
from app.domain.messages.exceptions import CannotMessageSelfError, MessagesNotAllowedError
from app.domain.privacy.audience import is_allowed
from app.domain.restrictions.exceptions import AccountBlockedError
from app.domain.restrictions.kinds import BLOCK


def send_message(
    sender_id, recipient_id, content, user_repository, message_repository, follow_repository,
    restriction_repository,
):
    if sender_id == recipient_id:
        raise CannotMessageSelfError()

    recipient = user_repository.find_by_id(recipient_id)
    if recipient is None:
        raise UserNotFoundError()

    # Bloqueos (ADR-029), mismo criterio que follow_user: si el destinatario
    # bloqueó al remitente, la cuenta "no existe" para él; si fue el remitente
    # quien bloqueó, se le explica.
    if restriction_repository.get_kind(recipient_id, sender_id) == BLOCK:
        raise UserNotFoundError()
    if restriction_repository.get_kind(sender_id, recipient_id) == BLOCK:
        raise AccountBlockedError()

    # `who_can_message = 'followers'` significa "solo quienes me siguen".
    # Ojo con la dirección: hay que preguntar si QUIEN ESCRIBE sigue al
    # DESTINATARIO -- es el destinatario el que pone la condición sobre su
    # propia bandeja. `actor_is_self` no hace falta: mandarse un mensaje a sí
    # mismo ya está descartado arriba (y por ck_messages_no_self_message).
    sender_follows_recipient = (
        follow_repository.follow_statuses(sender_id, [recipient.id]).get(recipient.id)
        == ACCEPTED
    )
    if not is_allowed(recipient.who_can_message, sender_follows_recipient):
        raise MessagesNotAllowedError()

    message = message_repository.create(sender_id, recipient_id, content)
    return to_public_message(message)
