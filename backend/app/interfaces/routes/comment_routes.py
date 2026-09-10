# POST y GET /api/posts/<post_id>/comments (ADR-006-comments-minimal-model.md).
# Blueprint separado de posts_bp -- "comments" es su propia entidad (mismo
# criterio que separa auth_bp de users_bp, y que like_routes.py de posts_bp),
# aunque su URL anide bajo /posts/<id> por ser un sub-recurso natural de un
# post.
#
# `<uuid:post_id>`: el conversor `uuid` de Flask/Werkzeug ya devuelve 404
# (ninguna ruta matchea) para cualquier segmento que no sea un UUID válido,
# sin necesidad de validarlo a mano (mismo criterio que like_routes.py).

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.comments.create_comment_use_case import create_comment
from app.application.comments.list_comments_use_case import (
    DEFAULT_LIMIT,
    list_comments,
)
from app.domain.comments.validators import MAX_CONTENT_LENGTH, is_valid_content
from app.domain.posts.exceptions import PostNotFoundError
from app.infrastructure.persistence.repositories.comment_repository import (
    SQLAlchemyCommentRepository,
)
from app.infrastructure.persistence.repositories.post_repository import (
    SQLAlchemyPostRepository,
)

comments_bp = Blueprint("comments", __name__)

_post_repository = SQLAlchemyPostRepository()
_comment_repository = SQLAlchemyCommentRepository()


@comments_bp.route("/posts/<uuid:post_id>/comments", methods=["POST"])
@jwt_required()
def create(post_id):
    # Identidad exclusivamente del JWT -- nunca del body (mismo principio
    # que el resto de endpoints protegidos).
    author_id = get_jwt_identity()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    # Whitelist explícita: solo `content` se lee del body -- nunca
    # `post_id`/`author_id`/`id` (post_id viene de la URL, no del body;
    # mismo principio anti mass-assignment que POST /api/posts).
    content = data.get("content")
    if not is_valid_content(content):
        return jsonify(
            {"msg": f"El contenido debe tener entre 1 y {MAX_CONTENT_LENGTH} caracteres"}
        ), 400

    try:
        comment = create_comment(
            post_id, author_id, content.strip(), _post_repository, _comment_repository
        )
    except PostNotFoundError:
        return jsonify({"msg": "Post no encontrado"}), 404

    return jsonify({"comment": comment}), 201


@comments_bp.route("/posts/<uuid:post_id>/comments", methods=["GET"])
@jwt_required()
def list_all(post_id):
    try:
        comments = list_comments(
            post_id, _post_repository, _comment_repository, DEFAULT_LIMIT
        )
    except PostNotFoundError:
        return jsonify({"msg": "Post no encontrado"}), 404

    return jsonify({"comments": comments}), 200
