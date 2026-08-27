# GET /api/users/me (ADR-002 §3 — docs/architecture/ADR-002-user-profile-fields.md).
# Blueprint separado de auth_bp: no es un endpoint de autenticación en sí
# (no emite ni valida credenciales), es el primer endpoint protegido del
# backend (@jwt_required()) -- BACKEND_ARCHITECTURE.md §9/§14 señalaba que
# no existía todavía ningún caso real de "endpoint protegido" que fijara el
# patrón; este archivo lo fija.
#
# Composition root igual que auth_routes.py (BACKEND_ARCHITECTURE.md §17):
# único punto que conoce tanto el caso de uso (application/) como la
# implementación concreta del repositorio (infrastructure/).

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.auth.get_current_user_use_case import get_current_user
from app.domain.auth.exceptions import UserNotFoundError
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

users_bp = Blueprint("users", __name__)

_user_repository = SQLAlchemyUserRepository()


@users_bp.route("/users/me", methods=["GET"])
@jwt_required()
def me():
    # La identidad viene exclusivamente del JWT (get_jwt_identity()) -- nunca
    # de query string, body ni headers personalizados (ADR-002 §3).
    user_id = get_jwt_identity()

    try:
        user = get_current_user(user_id, _user_repository)
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({"user": user}), 200
