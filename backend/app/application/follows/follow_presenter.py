# Forma pública de una solicitud de seguimiento pendiente, devuelta por
# GET /api/follow-requests (ADR-022-private-accounts.md §Contrato API) --
# centralizada acá para no duplicarla, mismo patrón que
# application/notifications/notification_presenter.py.
#
# El solicitante se expone con la misma forma reducida que `post.author` y
# `notification.actor` -- nunca email/phone/password_hash ni otros campos
# privados. Que alguien te haya pedido seguirte no da acceso a sus datos.


def to_public_follow_request(request):
    follow = request["follow"]
    requester = request["requester"]
    return {
        "user": {
            "id": str(requester.id),
            "username": requester.username,
            "name": requester.name,
            "is_private": requester.is_private,
        },
        # Cuándo se pidió, no cuándo se respondió -- una solicitud pendiente
        # por definición no tiene respuesta todavía.
        "requested_at": follow.created_at.isoformat(),
    }
