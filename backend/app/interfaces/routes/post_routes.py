# POST /api/posts y GET /api/posts (ADR-004-posts-minimal-model.md).
# Blueprint separado de auth_bp/users_bp -- primer endpoint de una entidad
# social real, no de autenticación ni de perfil. Composition root igual que
# el resto de interfaces/routes/ (BACKEND_ARCHITECTURE.md §17): único punto
# que conoce tanto el caso de uso (application/) como la implementación
# concreta del repositorio (infrastructure/).

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.posts.create_post_use_case import create_post
from app.application.posts.list_posts_use_case import DEFAULT_LIMIT, list_posts
from app.domain.posts.validators import MAX_CONTENT_LENGTH, is_valid_content
from app.infrastructure.persistence.repositories.post_repository import (
    SQLAlchemyPostRepository,
)

posts_bp = Blueprint("posts", __name__)

_post_repository = SQLAlchemyPostRepository()


@posts_bp.route("/posts", methods=["POST"])
@jwt_required()
def create():
    # Identidad exclusivamente del JWT -- nunca de query string, body ni
    # headers personalizados (mismo principio que auth_routes.py/user_routes.py).
    author_id = get_jwt_identity()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    # Whitelist explícita: solo `content` se lee del body -- nunca
    # `author_id`/`id`/`created_at` (mismo principio anti mass-assignment
    # que PATCH /api/users/me, ADR-003 §Seguridad).
    content = data.get("content")
    if not is_valid_content(content):
        return jsonify(
            {"msg": f"El contenido debe tener entre 1 y {MAX_CONTENT_LENGTH} caracteres"}
        ), 400

    post = create_post(author_id, content.strip(), _post_repository)
    return jsonify({"post": post}), 201


@posts_bp.route("/posts", methods=["GET"])
@jwt_required()
def list_all():
    # Auth requerida por consistencia con el resto del feed hoy -- AppShell
    # (donde vive /feed en el Frontend) solo es alcanzable dentro de
    # ProtectedRoute. No existe todavía ningún concepto de "feed público".
    posts = list_posts(_post_repository, DEFAULT_LIMIT)
    return jsonify({"posts": posts}), 200
