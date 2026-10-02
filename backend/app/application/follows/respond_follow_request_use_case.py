# Casos de uso: aceptar o rechazar una solicitud de seguimiento
# (POST /api/follow-requests/<user_id>/accept y
# DELETE /api/follow-requests/<user_id>, ADR-018-private-accounts.md).
#
# Los dos viven en el mismo módulo porque son las dos caras de la misma
# decisión sobre la misma fila, y los dos comparten exactamente la misma
# regla de pertenencia: solo se puede responder una solicitud **dirigida a
# uno mismo**. `user_id` (quien responde) sale de get_jwt_identity() en la
# route; `requester_id` viene de la URL.

from app.domain.follows.exceptions import FollowRequestNotFoundError
from app.domain.follows.follow_status import ACCEPTED


def accept_follow_request(user_id, requester_id, follow_repository, notification_repository):
    # `set_status` filtra por followed_id == user_id Y status == 'pending' en
    # la misma sentencia, así que confirma existencia y pertenencia a la vez
    # -- no hay ventana entre comprobar y actuar (ADR-018 §Seguridad). Un
    # segundo intento sobre una solicitud ya aceptada devuelve False, porque
    # ya no está en 'pending': es un 404, no un no-op silencioso.
    accepted = follow_repository.set_status(requester_id, user_id, ACCEPTED)
    if not accepted:
        raise FollowRequestNotFoundError()

    # El solicitante sí se entera de que lo aceptaron: sin esto no tendría
    # forma de saber que ya puede ver el contenido (el rechazo, en cambio, no
    # se notifica -- ADR-018 §Decisión).
    notification_repository.create(
        recipient_id=requester_id, actor_id=user_id, notification_type="follow_accepted"
    )

    return {"accepted": True}


def reject_follow_request(user_id, requester_id, follow_repository):
    # Rechazar **borra** la fila, no la marca como rechazada: así la persona
    # puede volver a pedirlo más adelante, y no queda un registro permanente
    # de un "no" (ADR-018 §Opciones consideradas). El efecto es idéntico a que
    # nunca hubiera pedido.
    rejected = follow_repository.remove_pending(requester_id, user_id)
    if not rejected:
        raise FollowRequestNotFoundError()

    # Deliberadamente sin notificación: avisarle a alguien que lo rechazaste
    # es información que no aporta y que invita a insistir (ADR-018 §Decisión).
    return {"rejected": True}
