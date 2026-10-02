# Endpoints de la pantalla "Cuentas bloqueadas y restringidas" (REF-SET-10,
# ADR-029-blocked-and-restricted-accounts.md):
#   · GET/POST /api/users/me/blocks, DELETE /api/users/me/blocks/<user_id>
#   · GET/POST /api/users/me/restrictions, DELETE /api/users/me/restrictions/<user_id>
#
# Colección propia del usuario autenticado, bajo `/users/me/...` igual que
# privacidad y seguridad: nunca se listan ni se modifican las de otra persona.
# El destino de un POST se nombra en el body por `user_id` o por `username`
# (la tarjeta de una publicación conoce el id; la pantalla de Configuración,
# solo lo que la persona escribe).
#
# Composition root igual que el resto de interfaces/routes/
# (BACKEND_ARCHITECTURE.md §17).

import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.restrictions.restriction_use_cases import (
    block_user,
    list_blocked,
    list_restricted,
    restrict_user,
    unblock_user,
    unrestrict_user,
)
from app.domain.auth.exceptions import UserNotFoundError
from app.domain.restrictions.exceptions import AccountBlockedError, CannotRestrictSelfError
from app.infrastructure.persistence.repositories.follow_repository import (
    SQLAlchemyFollowRepository,
)
from app.infrastructure.persistence.repositories.restriction_repository import (
    SQLAlchemyRestrictionRepository,
)
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

restrictions_bp = Blueprint("restrictions", __name__)

_user_repository = SQLAlchemyUserRepository()
_restriction_repository = SQLAlchemyRestrictionRepository()
_follow_repository = SQLAlchemyFollowRepository()


def _parse_target():
    """`(user_id, username, error_response)` a partir del body. Exactamente uno
    de `user_id` / `username`; whitelist explícita, nunca el body entero."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, None, (jsonify({"msg": "No se enviaron datos"}), 400)

    raw_id = data.get("user_id")
    raw_username = data.get("username")

    if raw_id is not None:
        try:
            return str(uuid.UUID(str(raw_id))), None, None
        except ValueError:
            return None, None, (jsonify({"msg": "El identificador de usuario no es válido"}), 400)

    if isinstance(raw_username, str) and raw_username.strip().lstrip("@"):
        return None, raw_username.strip(), None

    return None, None, (jsonify({"msg": "Indica el usuario (user_id o username)"}), 400)


# ===========================================================================
# Bloqueos
# ===========================================================================
@restrictions_bp.route("/users/me/blocks", methods=["GET"])
@jwt_required()
def get_blocks():
    owner_id = get_jwt_identity()
    return jsonify({"blocks": list_blocked(owner_id, _restriction_repository)}), 200


@restrictions_bp.route("/users/me/blocks", methods=["POST"])
@jwt_required()
def create_block():
    owner_id = get_jwt_identity()

    user_id, username, error = _parse_target()
    if error:
        return error

    try:
        result = block_user(
            owner_id, user_id, username, _user_repository,
            _restriction_repository, _follow_repository,
        )
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    except CannotRestrictSelfError:
        return jsonify({"msg": "No puedes bloquearte a ti mismo"}), 400

    return jsonify(result), 200


@restrictions_bp.route("/users/me/blocks/<uuid:user_id>", methods=["DELETE"])
@jwt_required()
def delete_block(user_id):
    owner_id = get_jwt_identity()
    return jsonify(unblock_user(owner_id, str(user_id), _restriction_repository)), 200


# ===========================================================================
# Restricciones
# ===========================================================================
@restrictions_bp.route("/users/me/restrictions", methods=["GET"])
@jwt_required()
def get_restrictions():
    owner_id = get_jwt_identity()
    return jsonify({"restrictions": list_restricted(owner_id, _restriction_repository)}), 200


@restrictions_bp.route("/users/me/restrictions", methods=["POST"])
@jwt_required()
def create_restriction():
    owner_id = get_jwt_identity()

    user_id, username, error = _parse_target()
    if error:
        return error

    try:
        result = restrict_user(
            owner_id, user_id, username, _user_repository, _restriction_repository
        )
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    except CannotRestrictSelfError:
        return jsonify({"msg": "No puedes restringirte a ti mismo"}), 400
    except AccountBlockedError:
        return jsonify({"msg": "Esa cuenta está bloqueada. Desbloquéala antes de restringirla."}), 409

    return jsonify(result), 200


@restrictions_bp.route("/users/me/restrictions/<uuid:user_id>", methods=["DELETE"])
@jwt_required()
def delete_restriction(user_id):
    owner_id = get_jwt_identity()
    return jsonify(unrestrict_user(owner_id, str(user_id), _restriction_repository)), 200
