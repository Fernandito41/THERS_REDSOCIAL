# POST y DELETE /api/users/<user_id>/follow (ADR-007-follows-minimal-model.md),
# más GET /api/follow-requests, POST /api/follow-requests/<user_id>/accept y
# DELETE /api/follow-requests/<user_id> (ADR-022-private-accounts.md).
#
# `/follow-requests` no anida bajo `/users/<id>`: siempre se listan y se
# responden las solicitudes dirigidas al usuario autenticado, nunca las de
# otra persona -- mismo criterio que `GET /api/notifications` y
# `GET /api/conversations`, que tampoco llevan el id en la URL.
# Blueprint separado de users_bp -- "follows" es su propia entidad (mismo
# criterio que separa like_routes.py/comment_routes.py de sus respectivos
# recursos padre), aunque la URL anide bajo /users/<id> por ser un sub-recurso
# natural de un usuario.
#
# `<uuid:user_id>`: el conversor `uuid` de Flask/Werkzeug ya devuelve 404
# (ninguna ruta matchea) para cualquier segmento que no sea un UUID válido,
# sin necesidad de validarlo a mano (mismo criterio que like_routes.py).

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.follows.follow_user_use_case import follow_user
from app.application.follows.list_follow_requests_use_case import (
    DEFAULT_LIMIT,
    list_follow_requests,
)
from app.application.follows.respond_follow_request_use_case import (
    accept_follow_request,
    reject_follow_request,
)
from app.application.follows.unfollow_user_use_case import unfollow_user
from app.domain.auth.exceptions import UserNotFoundError
from app.domain.follows.exceptions import (
    CannotFollowSelfError,
    FollowRequestNotFoundError,
)
from app.domain.restrictions.exceptions import AccountBlockedError
from app.interfaces.profile_gate import profile_completed_required
from app.infrastructure.persistence.repositories.follow_repository import (
    SQLAlchemyFollowRepository,
)
from app.infrastructure.persistence.repositories.notification_repository import (
    SQLAlchemyNotificationRepository,
)
from app.infrastructure.persistence.repositories.restriction_repository import (
    SQLAlchemyRestrictionRepository,
)
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

follows_bp = Blueprint("follows", __name__)

_user_repository = SQLAlchemyUserRepository()
_follow_repository = SQLAlchemyFollowRepository()
_notification_repository = SQLAlchemyNotificationRepository()
# ADR-029-blocked-and-restricted-accounts.md: no se sigue a quien bloqueó ni a
# quien se bloqueó.
_restriction_repository = SQLAlchemyRestrictionRepository()


@follows_bp.route("/users/<uuid:user_id>/follow", methods=["POST"])
@jwt_required()
@profile_completed_required
def follow(user_id):
    # Identidad exclusivamente del JWT -- nunca del body (mismo principio
    # que el resto de endpoints protegidos). `get_jwt_identity()` devuelve
    # un string; `user_id` (de la URL) ya es un uuid.UUID -- se compara como
    # string para que ambos lados usen la misma representación.
    follower_id = get_jwt_identity()

    try:
        result = follow_user(
            follower_id, str(user_id), _user_repository, _follow_repository,
            _notification_repository, _restriction_repository,
        )
    except CannotFollowSelfError:
        return jsonify({"msg": "No podés seguirte a vos mismo"}), 400
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    except AccountBlockedError:
        return jsonify({"msg": "Tienes bloqueada a esta cuenta. Desbloquéala para seguirla."}), 409

    return jsonify(result), 200


@follows_bp.route("/users/<uuid:user_id>/follow", methods=["DELETE"])
@jwt_required()
def unfollow(user_id):
    follower_id = get_jwt_identity()

    try:
        result = unfollow_user(follower_id, str(user_id), _user_repository, _follow_repository)
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify(result), 200


@follows_bp.route("/follow-requests", methods=["GET"])
@jwt_required()
def pending_requests():
    # Identidad exclusivamente del JWT -- nunca de query string. Un usuario
    # solo puede listar sus propias solicitudes (ADR-022 §Seguridad, mismo
    # principio que GET /api/notifications).
    user_id = get_jwt_identity()

    requests = list_follow_requests(user_id, _follow_repository, DEFAULT_LIMIT)
    return jsonify({"follow_requests": requests}), 200


@follows_bp.route("/follow-requests/<uuid:user_id>/accept", methods=["POST"])
@jwt_required()
def accept_request(user_id):
    # `user_id` de la URL es QUIEN PIDIÓ seguir; quien acepta es el del JWT.
    # La pertenencia se confirma dentro del UPDATE (ADR-022 §Seguridad), no
    # acá -- esta route no lee la fila para compararla después.
    responder_id = get_jwt_identity()

    try:
        result = accept_follow_request(
            responder_id, str(user_id), _follow_repository, _notification_repository
        )
    except FollowRequestNotFoundError:
        # Mismo mensaje/código si la solicitud no existe, si ya se respondió o
        # si está dirigida a otra persona -- no revela cuál de los tres
        # ocurrió.
        return jsonify({"msg": "Solicitud no encontrada"}), 404

    return jsonify(result), 200


@follows_bp.route("/follow-requests/<uuid:user_id>", methods=["DELETE"])
@jwt_required()
def reject_request(user_id):
    # Rechazar es un DELETE sobre la solicitud, no un POST a /reject: lo que
    # pasa es que la solicitud deja de existir (ADR-022 §Opciones
    # consideradas). Aceptar sí es un POST porque crea una relación nueva.
    responder_id = get_jwt_identity()

    try:
        result = reject_follow_request(responder_id, str(user_id), _follow_repository)
    except FollowRequestNotFoundError:
        return jsonify({"msg": "Solicitud no encontrada"}), 404

    return jsonify(result), 200
