# Caso de uso: listar las solicitudes de seguimiento sin responder
# (GET /api/follow-requests, ADR-022-private-accounts.md). Siempre desde la
# perspectiva del usuario autenticado -- `user_id` sale de get_jwt_identity()
# en la route, nunca de la URL ni del body, así que nadie puede listar las
# solicitudes de otra persona (mismo criterio que GET /api/notifications y
# GET /api/conversations).
#
# Sin paginación real: límite fijo, mismo criterio que el resto de listados
# del proyecto (ADR-006/ADR-008/ADR-013).

from app.application.follows.follow_presenter import to_public_follow_request

DEFAULT_LIMIT = 50


def list_follow_requests(user_id, follow_repository, limit=DEFAULT_LIMIT):
    requests = follow_repository.list_pending_requests(user_id, limit)
    return [to_public_follow_request(request) for request in requests]
