# Caso de uso: seguir a un usuario (POST /api/users/<user_id>/follow,
# ADR-007-follows-minimal-model.md, extendido por
# ADR-018-private-accounts.md). Idempotente: si ya lo seguía -- o si ya le
# había mandado una solicitud -- no falla ni cambia el estado.

from app.domain.auth.exceptions import UserNotFoundError
from app.domain.follows.exceptions import CannotFollowSelfError
from app.domain.follows.follow_status import ACCEPTED, PENDING
from app.domain.restrictions.exceptions import AccountBlockedError
from app.domain.restrictions.kinds import BLOCK


def follow_user(
    follower_id, followed_id, user_repository, follow_repository, notification_repository,
    restriction_repository,
):
    if follower_id == followed_id:
        raise CannotFollowSelfError()

    target = user_repository.find_by_id(followed_id)
    if target is None:
        raise UserNotFoundError()

    # Bloqueos (ADR-025). Si el destino bloqueó a quien intenta seguir, se
    # responde como si la cuenta no existiera: decirle "te bloqueó" sería
    # justo lo que el bloqueo quiere evitar. Si fue quien intenta seguir
    # quien bloqueó, sí se le dice (409) para que sepa por qué no funciona.
    if restriction_repository.get_kind(followed_id, follower_id) == BLOCK:
        raise UserNotFoundError()
    if restriction_repository.get_kind(follower_id, followed_id) == BLOCK:
        raise AccountBlockedError()

    # Seguir a una cuenta privada no es seguirla: es pedirlo (ADR-018
    # §Decisión). El estado lo decide la cuenta destino, nunca el cliente --
    # no hay ningún campo del body que pueda influir en esto.
    status = PENDING if target.is_private else ACCEPTED

    was_created = follow_repository.add(follower_id, followed_id, status)

    if not was_created:
        # Ya existía una fila: se devuelve SU estado, no el que acabamos de
        # calcular. Si no, un POST repetido sobre un follow ya aceptado
        # reportaría 'pending' solo porque la cuenta se volvió privada
        # después (ADR-018 §Decisión).
        status = follow_repository.get_status(follower_id, followed_id)
    else:
        # Solo notifica en la transición real (ADR-008 §No objetivos). El tipo
        # distingue los dos eventos: 'follow' ya es un hecho consumado,
        # 'follow_request' pide una acción al destinatario.
        notification_repository.create(
            recipient_id=followed_id,
            actor_id=follower_id,
            notification_type="follow" if status == ACCEPTED else "follow_request",
        )

    return {"following": status == ACCEPTED, "follow_status": status}
