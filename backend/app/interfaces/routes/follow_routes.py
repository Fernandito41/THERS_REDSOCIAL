# POST y DELETE /api/users/<user_id>/follow (ADR-007-follows-minimal-model.md).
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
from app.application.follows.unfollow_user_use_case import unfollow_user
from app.domain.auth.exceptions import UserNotFoundError
from app.domain.follows.exceptions import CannotFollowSelfError
from app.infrastructure.persistence.repositories.follow_repository import (
    SQLAlchemyFollowRepository,
)
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

follows_bp = Blueprint("follows", __name__)

_user_repository = SQLAlchemyUserRepository()
_follow_repository = SQLAlchemyFollowRepository()


@follows_bp.route("/users/<uuid:user_id>/follow", methods=["POST"])
@jwt_required()
def follow(user_id):
    # Identidad exclusivamente del JWT -- nunca del body (mismo principio
    # que el resto de endpoints protegidos). `get_jwt_identity()` devuelve
    # un string; `user_id` (de la URL) ya es un uuid.UUID -- se compara como
    # string para que ambos lados usen la misma representación.
    follower_id = get_jwt_identity()

    try:
        result = follow_user(follower_id, str(user_id), _user_repository, _follow_repository)
    except CannotFollowSelfError:
        return jsonify({"msg": "No podés seguirte a vos mismo"}), 400
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404

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
