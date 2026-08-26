from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.application.auth.login_use_case import login_user
from app.application.auth.register_use_case import register_user
from app.domain.auth.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

auth_bp = Blueprint("auth", __name__)

# Composición: interfaces/routes/ es el único punto que conoce tanto los casos
# de uso (application/) como la implementación concreta del repositorio
# (infrastructure/) — domain/ y application/ nunca importan SQLAlchemy
# directamente (BACKEND_ARCHITECTURE.md §17).
_user_repository = SQLAlchemyUserRepository()


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    name = data.get("name")
    # .strip() solo en email -- CITEXT ya resuelve mayúsculas/minúsculas a
    # nivel de motor (models.py), pero no espacios en blanco; sin esto, un
    # email con espacio final (autocompletado/copy-paste) se guarda distinto
    # a como se compara en el login, y find_by_email() nunca hace match.
    # La contraseña nunca se normaliza (no aplica, y alteraría su valor real).
    email = data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"msg": "Nombre, email y contraseña son obligatorios"}), 400

    try:
        user = register_user(name, email, password, _user_repository)
    except EmailAlreadyExistsError:
        return jsonify({"msg": "Ya existe una cuenta con ese email"}), 409

    return jsonify({"user": user}), 201


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    # Mismo .strip() que en /register (ver comentario ahí) -- sin esto, un
    # login con un espacio de más en el email produce 401 aunque la
    # contraseña sea correcta, porque find_by_email() no hace match.
    email = data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    try:
        user = login_user(email, password, _user_repository)
    except InvalidCredentialsError:
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    # Identity del JWT: user.id (UUID de PostgreSQL), no email — ver
    # BACKEND_ARCHITECTURE.md §9 nota de impacto sobre esta migración.
    token = create_access_token(identity=user["id"])

    return jsonify({
        "token": token,
        "user": user
    }), 200
