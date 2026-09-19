# POST/GET /api/users/<user_id>/messages y GET /api/conversations
# (ADR-013-messages-minimal-model.md). Blueprint separado de users_bp --
# "messages" es su propia entidad (mismo criterio que separa follows_bp de
# users_bp), aunque la URL de mandar/leer un hilo anide bajo /users/<id> por
# ser un sub-recurso natural de un usuario. `GET /api/conversations` no
# anida bajo ningún recurso -- siempre se lista desde la perspectiva del
# usuario autenticado, mismo criterio que `GET /api/notifications`.
#
# `<uuid:user_id>`: el conversor `uuid` de Flask/Werkzeug ya devuelve 404
# (ninguna ruta matchea) para cualquier segmento que no sea un UUID válido,
# sin necesidad de validarlo a mano (mismo criterio que follow_routes.py).

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.messages.list_conversations_use_case import list_conversations
from app.application.messages.list_thread_use_case import DEFAULT_LIMIT, list_thread
from app.application.messages.send_message_use_case import send_message
from app.domain.auth.exceptions import UserNotFoundError
from app.domain.messages.exceptions import CannotMessageSelfError
from app.domain.messages.validators import MAX_CONTENT_LENGTH, is_valid_content
from app.infrastructure.persistence.repositories.message_repository import (
    SQLAlchemyMessageRepository,
)
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

messages_bp = Blueprint("messages", __name__)

_user_repository = SQLAlchemyUserRepository()
_message_repository = SQLAlchemyMessageRepository()


@messages_bp.route("/users/<uuid:user_id>/messages", methods=["POST"])
@jwt_required()
def create(user_id):
    # Identidad exclusivamente del JWT -- nunca del body (mismo principio
    # que el resto de endpoints protegidos).
    sender_id = get_jwt_identity()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    # Whitelist explícita: solo `content` se lee del body -- nunca
    # `sender_id`/`recipient_id`/`id` (recipient_id viene de la URL, no del
    # body; mismo principio anti mass-assignment que POST /api/posts).
    content = data.get("content")
    if not is_valid_content(content):
        return jsonify(
            {"msg": f"El contenido debe tener entre 1 y {MAX_CONTENT_LENGTH} caracteres"}
        ), 400

    try:
        message = send_message(
            sender_id, str(user_id), content.strip(), _user_repository, _message_repository
        )
    except CannotMessageSelfError:
        return jsonify({"msg": "No podés mandarte un mensaje a vos mismo"}), 400
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({"message": message}), 201


@messages_bp.route("/users/<uuid:user_id>/messages", methods=["GET"])
@jwt_required()
def thread(user_id):
    current_user_id = get_jwt_identity()

    try:
        messages = list_thread(
            current_user_id, str(user_id), _user_repository, _message_repository, DEFAULT_LIMIT
        )
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({"messages": messages}), 200


@messages_bp.route("/conversations", methods=["GET"])
@jwt_required()
def conversations():
    # Identidad exclusivamente del JWT -- nunca de query string. Un usuario
    # solo puede listar sus propias conversaciones, nunca las de otro
    # (mismo principio que GET /api/notifications).
    user_id = get_jwt_identity()

    result = list_conversations(user_id, _message_repository)
    return jsonify({"conversations": result}), 200
