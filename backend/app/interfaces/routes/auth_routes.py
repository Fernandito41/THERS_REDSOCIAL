from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import create_access_token

from app.application.auth.forgot_password_use_case import forgot_password
from app.application.auth.login_use_case import login_user
from app.application.auth.register_use_case import register_user
from app.application.auth.reset_password_use_case import reset_password
from app.application.auth.verify_email_use_case import verify_email
from app.application.email.email_service import EmailService
from app.config import Config
from app.domain.auth.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidOrExpiredResetTokenError,
    InvalidOrExpiredVerificationTokenError,
    UsernameAlreadyExistsError,
)
from app.domain.auth.validators import (
    MIN_PASSWORD_LENGTH,
    is_valid_country_code,
    is_valid_email,
    is_valid_password,
    is_valid_phone,
    is_valid_username,
    meets_minimum_age,
    parse_birth_date,
)
from app.infrastructure.email.factory import create_email_sender
from app.infrastructure.persistence.repositories.email_verification_repository import (
    SQLAlchemyEmailVerificationTokenRepository,
)
from app.infrastructure.persistence.repositories.password_reset_repository import (
    SQLAlchemyPasswordResetTokenRepository,
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
_password_reset_token_repository = SQLAlchemyPasswordResetTokenRepository()
_email_verification_token_repository = SQLAlchemyEmailVerificationTokenRepository()

# EmailSender se decide una sola vez, al importar este módulo (mismo momento
# en que Config ya resolvió RESEND_API_KEY desde el entorno) -- Resend real
# si hay API key, NullEmailSender si no (ADR-009-password-reset-and-email-verification.md
# §Decisión, infrastructure/email/factory.py).
_email_service = EmailService(create_email_sender(Config.RESEND_API_KEY, Config.EMAIL_FROM))


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

    if not is_valid_email(email):
        return jsonify({"msg": "El email no es válido"}), 400

    if password != confirm_password:
        return jsonify({"msg": "Las contraseñas no coinciden"}), 400

    if not is_valid_password(password):
        return jsonify(
            {"msg": f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"}
        ), 400

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


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password_route():
    # Público, sin @jwt_required() -- quien lo llama todavía no tiene
    # sesión (por eso perdió su contraseña). ADR-009 §Contrato API.
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    email = data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email")
    if not email:
        return jsonify({"msg": "El email es obligatorio"}), 400
    if not is_valid_email(email):
        return jsonify({"msg": "El email no es válido"}), 400

    result = forgot_password(
        email,
        current_app.config["FRONTEND_URL"],
        _user_repository,
        _password_reset_token_repository,
        _email_service,
    )
    # Siempre 200 con el mismo mensaje genérico, exista o no el email --
    # FASE 4: no revelar si una dirección está registrada.
    return jsonify(result), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    token = data.get("token")
    new_password = data.get("password")
    confirm_password = data.get("confirm_password")

    if not token or not isinstance(token, str):
        return jsonify({"msg": "El token es obligatorio"}), 400
    if not new_password or not confirm_password:
        return jsonify({"msg": "La contraseña y su confirmación son obligatorias"}), 400
    if new_password != confirm_password:
        return jsonify({"msg": "Las contraseñas no coinciden"}), 400
    if not is_valid_password(new_password):
        return jsonify(
            {"msg": f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"}
        ), 400

    try:
        result = reset_password(
            token,
            new_password,
            _user_repository,
            _password_reset_token_repository,
            _email_service,
        )
    except InvalidOrExpiredResetTokenError:
        # Mismo mensaje/código sin importar si el token no existe, expiró o
        # ya se usó -- ADR-009 §Contrato API.
        return jsonify({"msg": "El enlace de recuperación no es válido o expiró"}), 400

    return jsonify(result), 200


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email_route():
    # Público -- quien hace clic en el enlace del correo puede no tener
    # sesión iniciada en ese navegador/dispositivo (ADR-009 §Contrato API).
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    token = data.get("token")
    if not token or not isinstance(token, str):
        return jsonify({"msg": "El token es obligatorio"}), 400

    try:
        result = verify_email(token, _user_repository, _email_verification_token_repository)
    except InvalidOrExpiredVerificationTokenError:
        return jsonify({"msg": "El enlace de verificación no es válido o expiró"}), 400

    return jsonify(result), 200
