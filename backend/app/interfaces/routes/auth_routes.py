from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.application.auth.login_use_case import login_user
from app.application.auth.register_use_case import register_user
from app.domain.auth.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UsernameAlreadyExistsError,
)
from app.domain.auth.validators import (
    is_valid_country_code,
    is_valid_phone,
    is_valid_username,
    meets_minimum_age,
    parse_birth_date,
)
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
    username = data.get("username").strip() if isinstance(data.get("username"), str) else data.get("username")
    # .strip() solo en email/username -- CITEXT ya resuelve mayúsculas/minúsculas a
    # nivel de motor (models.py) para email, pero no espacios en blanco; sin esto, un
    # email con espacio final (autocompletado/copy-paste) se guarda distinto
    # a como se compara en el login, y find_by_email() nunca hace match.
    # La contraseña nunca se normaliza (no aplica, y alteraría su valor real).
    email = data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email")
    phone = data.get("phone")
    country_code = data.get("country_code")
    birth_date_raw = data.get("birth_date")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    # Campos de perfil agregados por ADR-002 (docs/architecture/ADR-002-user-profile-fields.md).
    if (
        not name
        or not username
        or not email
        or not phone
        or not country_code
        or not birth_date_raw
        or not password
        or not confirm_password
    ):
        return jsonify({
            "msg": "Nombre, username, email, teléfono, código de país, fecha de "
                   "nacimiento, contraseña y confirmación de contraseña son obligatorios"
        }), 400

    if password != confirm_password:
        return jsonify({"msg": "Las contraseñas no coinciden"}), 400

    if not is_valid_username(username):
        return jsonify({"msg": "El username debe tener 3 a 20 caracteres alfanuméricos o guion bajo"}), 400

    if not is_valid_phone(phone):
        return jsonify({"msg": "El teléfono no es válido"}), 400

    if not is_valid_country_code(country_code):
        return jsonify({"msg": "El código de país no es válido"}), 400

    birth_date = parse_birth_date(birth_date_raw)
    if birth_date is None:
        return jsonify({"msg": "La fecha de nacimiento no es válida"}), 400
    if not meets_minimum_age(birth_date):
        return jsonify({"msg": "Debes tener al menos 13 años para registrarte"}), 400

    try:
        user = register_user(
            name, username, email, phone, country_code, birth_date, password, _user_repository
        )
    except EmailAlreadyExistsError:
        return jsonify({"msg": "Ya existe una cuenta con ese email"}), 409
    except UsernameAlreadyExistsError:
        return jsonify({"msg": "Ya existe una cuenta con ese username"}), 409

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
