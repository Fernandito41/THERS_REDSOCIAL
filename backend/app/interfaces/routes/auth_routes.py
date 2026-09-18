from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.application.auth.forgot_password_use_case import forgot_password
from app.application.auth.google_auth_use_case import authenticate_with_google
from app.application.auth.login_use_case import login_user
from app.application.auth.register_use_case import register_user
from app.application.auth.resend_registration_code_use_case import resend_registration_code
from app.application.auth.reset_password_use_case import reset_password
from app.application.auth.verify_registration_code_use_case import verify_registration_code
from app.application.auth.verify_reset_code_use_case import verify_reset_code
from app.application.email.email_service import EmailService
from app.config import Config
from app.domain.auth.exceptions import (
    EmailAlreadyExistsError,
    EmailNotVerifiedError,
    GoogleEmailNotVerifiedError,
    IdentityAlreadyLinkedError,
    InvalidCredentialsError,
    InvalidGoogleCredentialError,
    InvalidOrExpiredResetTokenError,
    InvalidRegistrationCodeError,
    InvalidResetCodeError,
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
from app.infrastructure.auth.google_id_token_verifier import GoogleIdTokenVerifier
from app.infrastructure.email.factory import create_email_sender
from app.infrastructure.persistence.repositories.email_verification_repository import (
    SQLAlchemyEmailVerificationTokenRepository,
)
from app.infrastructure.persistence.repositories.password_reset_repository import (
    SQLAlchemyPasswordResetTokenRepository,
)
from app.infrastructure.persistence.repositories.user_identity_repository import (
    SQLAlchemyUserIdentityRepository,
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
_user_identity_repository = SQLAlchemyUserIdentityRepository()

# EmailSender se decide una sola vez, al importar este módulo (mismo momento
# en que Config ya resolvió RESEND_API_KEY desde el entorno) -- Resend real
# si hay API key, NullEmailSender si no (ADR-009-password-reset-and-email-verification.md
# §Decisión, infrastructure/email/factory.py).
_email_service = EmailService(create_email_sender(Config.RESEND_API_KEY, Config.EMAIL_FROM))

# Mismo criterio: el Client ID se resuelve una sola vez al importar este
# módulo (ADR-012-google-sign-in.md §Decisión, infrastructure/auth/google_id_token_verifier.py).
_google_identity_verifier = GoogleIdTokenVerifier(Config.GOOGLE_CLIENT_ID)


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
            name, username, email, phone, country_code, birth_date, password,
            _user_repository, _email_verification_token_repository, _email_service,
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
    except EmailNotVerifiedError:
        # 403, no 401: las credenciales SÍ eran correctas -- la cuenta
        # todavía no completó la verificación obligatoria
        # (ADR-011-mandatory-email-verification.md §Decisión). Nunca se
        # llega a create_access_token() en este caso -- ningún JWT de
        # sesión normal se emite mientras la cuenta siga sin verificar.
        # `email_verified` explícito en el body (no solo el mensaje) para
        # que el Frontend distinga este caso sin parsear texto.
        return jsonify({
            "msg": "Tu correo electrónico todavía no fue verificado.",
            "email_verified": False,
        }), 403

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
    # sesión (por eso perdió su contraseña). También sirve para "Reenviar
    # código" -- el Frontend llama a este mismo endpoint de nuevo con el
    # mismo email (ADR-010-password-reset-otp-flow.md §Decisión, reemplaza
    # el flujo de enlace de ADR-009-password-reset-and-email-verification.md).
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    email = data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email")
    if not email:
        return jsonify({"msg": "El email es obligatorio"}), 400
    if not is_valid_email(email):
        return jsonify({"msg": "El email no es válido"}), 400

    result = forgot_password(email, _user_repository, _password_reset_token_repository, _email_service)
    # Siempre 200 con el mismo mensaje genérico, exista o no el email --
    # evitar enumeración de usuarios.
    return jsonify(result), 200


@auth_bp.route("/verify-reset-code", methods=["POST"])
def verify_reset_code_route():
    # Público -- quien lo llama todavía no tiene sesión (ADR-010 §Contrato
    # API). No usa @jwt_required(): la identidad la aporta email + código.
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    email = data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email")
    code = data.get("code")

    if not email:
        return jsonify({"msg": "El email es obligatorio"}), 400
    if not code or not isinstance(code, str):
        return jsonify({"msg": "El código es obligatorio"}), 400

    try:
        result = verify_reset_code(email, code, _user_repository, _password_reset_token_repository)
    except InvalidResetCodeError:
        # Mismo mensaje sin importar si el email no existe, no hay solicitud
        # activa, el código expiró, se agotaron los intentos, o el código es
        # simplemente incorrecto -- ADR-010 §Seguridad.
        return jsonify({"msg": "El código es incorrecto. Inténtalo nuevamente."}), 400

    return jsonify(result), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    reset_authorization = data.get("reset_authorization")
    new_password = data.get("password")
    confirm_password = data.get("confirm_password")

    if not reset_authorization or not isinstance(reset_authorization, str):
        return jsonify({"msg": "La autorización de recuperación es obligatoria"}), 400
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
            reset_authorization,
            new_password,
            _user_repository,
            _password_reset_token_repository,
            _email_service,
        )
    except InvalidOrExpiredResetTokenError:
        # Mismo mensaje/código sin importar si la autorización no existe,
        # expiró o ya se usó -- ADR-010 §Contrato API.
        return jsonify(
            {"msg": "La autorización para restablecer tu contraseña no es válida o expiró"}
        ), 400

    return jsonify(result), 200


@auth_bp.route("/verify-registration-code", methods=["POST"])
def verify_registration_code_route():
    # Público -- quien lo llama todavía no puede iniciar sesión (la cuenta
    # sigue sin verificar, ADR-011-mandatory-email-verification.md §Contrato
    # API, reemplaza `POST /api/verify-email` de ADR-009).
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    email = data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email")
    code = data.get("code")

    if not email:
        return jsonify({"msg": "El email es obligatorio"}), 400
    if not code or not isinstance(code, str):
        return jsonify({"msg": "El código es obligatorio"}), 400

    try:
        result = verify_registration_code(
            email, code, _user_repository, _email_verification_token_repository
        )
    except InvalidRegistrationCodeError:
        # Mismo mensaje sin importar si el email no existe, ya está
        # verificado, no hay código activo, expiró, se agotaron los
        # intentos, o el código es simplemente incorrecto -- ADR-011
        # §Seguridad.
        return jsonify({"msg": "El código es incorrecto. Inténtalo nuevamente."}), 400

    return jsonify(result), 200


@auth_bp.route("/resend-registration-code", methods=["POST"])
def resend_registration_code_route():
    # Público, mismo criterio que POST /api/forgot-password -- quien lo
    # llama todavía no puede iniciar sesión (ADR-011 §Contrato API).
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    email = data.get("email").strip() if isinstance(data.get("email"), str) else data.get("email")
    if not email:
        return jsonify({"msg": "El email es obligatorio"}), 400
    if not is_valid_email(email):
        return jsonify({"msg": "El email no es válido"}), 400

    result = resend_registration_code(
        email, _user_repository, _email_verification_token_repository, _email_service
    )
    # Siempre 200 con el mismo mensaje genérico -- evitar enumeración de
    # usuarios (mismo criterio que POST /api/forgot-password).
    return jsonify(result), 200


@auth_bp.route("/auth/google", methods=["POST"])
def google_auth_route():
    # Público -- es, en sí mismo, el mecanismo de autenticación (ADR-012-google-sign-in.md
    # §Contrato API). El Frontend nunca envía email/nombre directamente: solo
    # el `credential` (ID Token) que Google Identity Services le entregó, tal
    # cual, sin que el Frontend lo interprete.
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    credential = data.get("credential")
    if not credential or not isinstance(credential, str):
        return jsonify({"msg": "La credencial de Google es obligatoria"}), 400

    try:
        user = authenticate_with_google(
            credential, _google_identity_verifier, _user_repository, _user_identity_repository
        )
    except InvalidGoogleCredentialError:
        # Nunca hay una cuenta de THERS involucrada todavía en este punto --
        # no hay enumeración que proteger, el mensaje puede ser directo.
        return jsonify({"msg": "No pudimos verificar tu cuenta de Google. Intentá de nuevo."}), 400
    except GoogleEmailNotVerifiedError:
        return jsonify(
            {"msg": "Tu cuenta de Google no tiene el correo verificado. THERS no puede usarla."}
        ), 400
    except IdentityAlreadyLinkedError:
        # Condición de carrera: dos requests simultáneas de POST /api/auth/google
        # para una cuenta de Google que todavía no existía en THERS (ADR-012
        # §Seguridad) -- el otro request ya la vinculó, un reintento hace login
        # normal, así que el mismo mensaje genérico de "intentá de nuevo" aplica.
        return jsonify({"msg": "No pudimos verificar tu cuenta de Google. Intentá de nuevo."}), 400

    # Mismo mecanismo de siempre (BACKEND_ARCHITECTURE.md §9): Google
    # autenticó la identidad, pero el JWT que autoriza el resto de la API de
    # THERS lo emite exclusivamente este backend, con `identity=user["id"]`
    # -- ningún endpoint protegido (incluido GET /api/users/me) necesita ni
    # acepta un token de Google (FASE 15 de la tarea origen).
    token = create_access_token(identity=user["id"])

    return jsonify({"token": token, "user": user}), 200
