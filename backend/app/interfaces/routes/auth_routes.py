from datetime import timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, decode_token

from app.application.auth.forgot_password_use_case import forgot_password
from app.application.auth.google_auth_use_case import authenticate_with_google
from app.application.auth.login_use_case import login_user
from app.application.auth.register_use_case import register_user
from app.application.auth.resend_registration_code_use_case import resend_registration_code
from app.application.auth.reset_password_use_case import reset_password
from app.application.auth.verify_registration_code_use_case import verify_registration_code
from app.application.auth.verify_reset_code_use_case import verify_reset_code
from app.application.auth.user_presenter import to_public_user
from app.application.email.email_service import EmailService
from app.application.rate_limiting import rate_limit_guard
from app.application.sessions.issue_session_use_case import issue_session
from app.application.two_factor.two_factor_use_case import verify_two_factor_challenge
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
from app.domain.auth.two_factor_exceptions import InvalidTwoFactorCodeError
from app.domain.rate_limiting import policy
from app.domain.rate_limiting.exceptions import RateLimitExceededError
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
from app.infrastructure.auth.pyotp_totp_provider import PyotpTotpProvider
from app.infrastructure.email.factory import create_email_sender
from app.infrastructure.persistence.repositories.email_verification_repository import (
    SQLAlchemyEmailVerificationTokenRepository,
)
from app.infrastructure.persistence.repositories.password_reset_repository import (
    SQLAlchemyPasswordResetTokenRepository,
)
from app.infrastructure.persistence.repositories.rate_limit_repository import (
    SQLAlchemyRateLimitRepository,
)
from app.infrastructure.persistence.repositories.session_repository import (
    SQLAlchemySessionRepository,
)
from app.infrastructure.persistence.repositories.two_factor_recovery_code_repository import (
    SQLAlchemyTwoFactorRecoveryCodeRepository,
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
# ADR-021-session-registry.md: cada token emitido se registra como sesión
# revocable. ADR-022-two-factor-authentication.md: el login puede exigir un
# segundo factor antes de emitir ese token.
_session_repository = SQLAlchemySessionRepository()
_recovery_code_repository = SQLAlchemyTwoFactorRecoveryCodeRepository()
_totp_provider = PyotpTotpProvider()
# ADR-023-rate-limiting.md: los endpoints de credenciales de este blueprint
# limitan intentos. Cierra el ítem 8 de `API_CONTRACT.md` §9.
_rate_limit_repository = SQLAlchemyRateLimitRepository()

# EmailSender se decide una sola vez, al importar este módulo (mismo momento
# en que Config ya resolvió RESEND_API_KEY desde el entorno) -- Resend real
# si hay API key, NullEmailSender si no (ADR-009-password-reset-and-email-verification.md
# §Decisión, infrastructure/email/factory.py).
_email_service = EmailService(create_email_sender(Config.RESEND_API_KEY, Config.EMAIL_FROM))

# Mismo criterio: el Client ID se resuelve una sola vez al importar este
# módulo (ADR-012-google-sign-in.md §Decisión, infrastructure/auth/google_id_token_verifier.py).
_google_identity_verifier = GoogleIdTokenVerifier(Config.GOOGLE_CLIENT_ID)


# Cuánto vive el token de desafío de 2FA. Cinco minutos: lo suficiente para
# abrir la app autenticadora y teclear un código, lo bastante corto para que no
# quede flotando. No es una sesión -- no sirve para ningún endpoint protegido
# (ver extensions.py: no tiene fila en `sessions`, así que el blocklist loader
# lo rechaza).
_TWO_FACTOR_CHALLENGE_MINUTES = 5

# Marca que distingue un token de desafío de un token de sesión. Viaja como
# claim dentro del JWT firmado, así que el cliente no puede falsificarla.
TWO_FACTOR_CHALLENGE_PURPOSE = "2fa_challenge"


def _client_ip():
    """IP del cliente, para limitar por origen (ADR-023).

    Mismo criterio que `_client_fingerprint`: `X-Forwarded-For` cuando existe,
    porque detrás de un proxy `remote_addr` es la del proxy. **Es un header que
    el cliente puede falsificar**, así que un atacante decidido puede rotarlo y
    saltarse el límite por IP -- por eso los endpoints que protegen una cuenta
    concreta (login, 2FA) limitan *además* por cuenta, que no se puede falsear
    (ADR-023 §Riesgos).
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _rate_limited_response(error):
    """429 uniforme con `Retry-After` (ADR-023 §Contrato API).

    El header es tan importante como el código: sin él, el cliente reintenta a
    ciegas -- peor para la persona legítima (no sabe cuándo volver) y peor para
    el servidor (sigue recibiendo peticiones).
    """
    response = jsonify({
        "msg": "Demasiados intentos. Esperá un momento antes de volver a probar.",
        "retry_after_seconds": error.retry_after_seconds,
    })
    response.status_code = 429
    response.headers["Retry-After"] = str(error.retry_after_seconds)
    return response


def _client_fingerprint():
    """Lo que se sabe del cliente que está iniciando sesión.

    `User-Agent` se guarda crudo, sin parsear: el servidor no tiene una base de
    datos de user agents y adivinar produciría etiquetas equivocadas
    (ADR-021 §Decisión).

    La IP sale de `X-Forwarded-For` cuando existe, porque detrás de un proxy
    `remote_addr` es la del proxy. Es un header que el cliente puede falsificar,
    así que **solo se usa para mostrarlo**, nunca para autorizar nada.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0].strip() if forwarded else request.remote_addr
    return request.headers.get("User-Agent"), ip


def _issue_session_token(user_entity):
    """Emite el JWT de sesión y registra su sesión. Único camino por el que se
    emite un token de sesión en todo el backend (login, Google y verificación de
    2FA pasan por acá) -- centralizarlo es lo que garantiza que no exista un
    token sin sesión asociada, que funcionaría pero sería irrevocable."""
    token = create_access_token(identity=str(user_entity.id))
    user_agent, ip_address = _client_fingerprint()
    issue_session(
        user_entity,
        decode_token(token)["jti"],
        user_agent,
        ip_address,
        _session_repository,
        _email_service,
    )
    return token


def _two_factor_challenge_token(user_id):
    return create_access_token(
        identity=str(user_id),
        additional_claims={"purpose": TWO_FACTOR_CHALLENGE_PURPOSE},
        expires_delta=timedelta(minutes=_TWO_FACTOR_CHALLENGE_MINUTES),
    )


@auth_bp.route("/register", methods=["POST"])
def register():
    # Límite por IP, contando TODAS las llamadas (no solo los fallos): acá el
    # éxito es el abuso -- lo que se frena es crear cuentas en masa
    # (ADR-023, policy.REGISTER con clear_on_success=False).
    try:
        rate_limit_guard.enforce(policy.REGISTER, _client_ip(), _rate_limit_repository)
    except RateLimitExceededError as error:
        return _rate_limited_response(error)


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

    # Dos límites, no uno (ADR-023 §Decisión):
    #  · por email -> protege UNA cuenta concreta de un ataque por diccionario,
    #    y es la identidad que un atacante NO puede falsear.
    #  · por IP -> frena el relleno de credenciales contra muchas cuentas desde
    #    un mismo origen, que el límite por email no vería.
    # Se cuentan ANTES de verificar la contraseña: si se contara solo al fallar,
    # el scrypt (lento a propósito) ya se habría ejecutado, y eso es por sí mismo
    # un vector de agotamiento de CPU.
    client_ip = _client_ip()
    try:
        rate_limit_guard.enforce(policy.LOGIN, f"email:{email.lower()}", _rate_limit_repository)
        rate_limit_guard.enforce(policy.LOGIN, f"ip:{client_ip}", _rate_limit_repository)
    except RateLimitExceededError as error:
        return _rate_limited_response(error)

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

    # Credenciales correctas: se borran los contadores. Lo que hay que frenar es
    # *adivinar*, no *usar* -- sin esto, alguien que entra y sale legítimamente
    # varias veces acabaría bloqueado como un atacante
    # (ADR-023, policy.LOGIN con clear_on_success=True).
    rate_limit_guard.clear(policy.LOGIN, f"email:{email.lower()}", _rate_limit_repository)
    rate_limit_guard.clear(policy.LOGIN, f"ip:{client_ip}", _rate_limit_repository)

    # Se relee la entidad (no solo el dict público) porque emitir una sesión
    # necesita `email`/`name`/`login_alerts_enabled` y decidir el 2FA necesita
    # `two_factor_enabled` -- ninguno de los cuatro forma parte del objeto
    # público. Es una búsqueda por clave primaria y solo ocurre en el login.
    user_entity = _user_repository.find_by_id(user["id"])

    if user_entity.two_factor_enabled:
        # 200, no 4xx: nada salió mal -- las credenciales eran correctas y falta
        # el segundo paso del login (ADR-022 §Contrato API). **No se emite token
        # de sesión ni se registra ninguna sesión acá**: hasta que el segundo
        # factor valide, no hay sesión.
        return jsonify({
            "two_factor_required": True,
            "two_factor_token": _two_factor_challenge_token(user_entity.id),
        }), 200

    # Identity del JWT: user.id (UUID de PostgreSQL), no email — ver
    # BACKEND_ARCHITECTURE.md §9 nota de impacto sobre esta migración.
    token = _issue_session_token(user_entity)

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

    # Límite por IP contando TODAS las llamadas: cada una exitosa manda un
    # correo, así que acá el éxito ES el abuso (ADR-023, policy.EMAIL_DISPATCH
    # con clear_on_success=False).
    #
    # Complementa, no reemplaza, el cooldown de 60 s por cuenta que ADR-010/
    # ADR-011 ya imponen: aquel frena el reenvío a una misma persona, esto frena
    # a una misma IP bombardeando muchas direcciones distintas.
    try:
        rate_limit_guard.enforce(
            policy.EMAIL_DISPATCH, _client_ip(), _rate_limit_repository
        )
    except RateLimitExceededError as error:
        return _rate_limited_response(error)
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

    # Límite por IP (ADR-023, policy.OTP_VERIFY). Estos endpoints YA tienen un
    # contador de 5 intentos POR CÓDIGO (ADR-010/ADR-011); esto cierra el hueco
    # de que ese contador es por código, así que pedir uno nuevo daba 5 intentos
    # más cada 60 s indefinidamente.
    try:
        rate_limit_guard.enforce(policy.OTP_VERIFY, _client_ip(), _rate_limit_repository)
    except RateLimitExceededError as error:
        return _rate_limited_response(error)
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
            _session_repository,
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

    # Límite por IP (ADR-023, policy.OTP_VERIFY). Estos endpoints YA tienen un
    # contador de 5 intentos POR CÓDIGO (ADR-010/ADR-011); esto cierra el hueco
    # de que ese contador es por código, así que pedir uno nuevo daba 5 intentos
    # más cada 60 s indefinidamente.
    try:
        rate_limit_guard.enforce(policy.OTP_VERIFY, _client_ip(), _rate_limit_repository)
    except RateLimitExceededError as error:
        return _rate_limited_response(error)
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

    # Límite por IP contando TODAS las llamadas: cada una exitosa manda un
    # correo, así que acá el éxito ES el abuso (ADR-023, policy.EMAIL_DISPATCH
    # con clear_on_success=False).
    #
    # Complementa, no reemplaza, el cooldown de 60 s por cuenta que ADR-010/
    # ADR-011 ya imponen: aquel frena el reenvío a una misma persona, esto frena
    # a una misma IP bombardeando muchas direcciones distintas.
    try:
        rate_limit_guard.enforce(
            policy.EMAIL_DISPATCH, _client_ip(), _rate_limit_repository
        )
    except RateLimitExceededError as error:
        return _rate_limited_response(error)
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
    # Mismo criterio que en /login: Google ya autenticó la identidad, pero si
    # la cuenta tiene 2FA activo ese segundo factor también aplica acá -- si no,
    # "Continuar con Google" sería una puerta que lo saltea (ADR-022 §Seguridad).
    user_entity = _user_repository.find_by_id(user["id"])

    if user_entity.two_factor_enabled:
        return jsonify({
            "two_factor_required": True,
            "two_factor_token": _two_factor_challenge_token(user_entity.id),
        }), 200

    token = _issue_session_token(user_entity)

    return jsonify({"token": token, "user": user}), 200


@auth_bp.route("/2fa/verify", methods=["POST"])
def verify_two_factor():
    """Segundo paso del login con 2FA (ADR-022-two-factor-authentication.md).

    **No lleva `@jwt_required()` a propósito.** El token de desafío no es un
    token de sesión: no tiene fila en `sessions`, así que el
    `token_in_blocklist_loader` (extensions.py) lo rechazaría. Acá se decodifica
    a mano y se comprueba explícitamente que su `purpose` sea el del desafío --
    así un token de sesión normal tampoco sirve para este endpoint, y el desafío
    no sirve para ningún otro.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    raw_token = data.get("two_factor_token")
    code = data.get("code")
    if not isinstance(raw_token, str) or not isinstance(code, str):
        return jsonify({"msg": "Faltan el token de verificación o el código"}), 400

    try:
        payload = decode_token(raw_token)
    except Exception:
        # Firma inválida, malformado o expirado -- los tres con el mismo 401,
        # sin distinguir cuál: el cliente solo necesita saber que tiene que
        # volver a empezar el login.
        return jsonify({"msg": "El token de verificación no es válido o expiró"}), 401

    if payload.get("purpose") != TWO_FACTOR_CHALLENGE_PURPOSE:
        # Un token de sesión normal llega hasta acá pero no pasa de este punto:
        # sin esta comprobación, cualquiera con una sesión válida podría usar
        # este endpoint para emitirse sesiones nuevas sin el segundo factor.
        return jsonify({"msg": "El token de verificación no es válido o expiró"}), 401

    user_entity = _user_repository.find_by_id(payload.get("sub"))
    if user_entity is None or not user_entity.two_factor_enabled:
        return jsonify({"msg": "El token de verificación no es válido o expiró"}), 401

    # ───────────────────────────────────────────────────────────────────────
    # EL MOTIVO POR EL QUE EXISTE ADR-023-rate-limiting.md.
    #
    # Un código TOTP son 10^6 combinaciones en una ventana de 30 s. Sin límite,
    # quien ya tiene la contraseña (y por tanto el token de desafío) puede
    # recorrer el espacio entero en minutos y el segundo factor no protege nada.
    #
    # Se limita por CUENTA y no solo por IP: un atacante rota IPs
    # trivialmente, y lo que se protege es esta cuenta concreta. La IP se limita
    # además, aparte, para que un mismo origen no ataque muchas cuentas en
    # paralelo.
    #
    # Va DESPUÉS de validar el token de desafío (así un token basura no consume
    # el presupuesto de intentos de una cuenta real) y ANTES de verificar el
    # código.
    # ───────────────────────────────────────────────────────────────────────
    account_identity = f"user:{user_entity.id}"
    try:
        rate_limit_guard.enforce(
            policy.TWO_FACTOR_VERIFY, account_identity, _rate_limit_repository
        )
        rate_limit_guard.enforce(
            policy.TWO_FACTOR_VERIFY, f"ip:{_client_ip()}", _rate_limit_repository
        )
    except RateLimitExceededError as error:
        return _rate_limited_response(error)

    try:
        result = verify_two_factor_challenge(
            user_entity, code, _user_repository, _recovery_code_repository, _totp_provider
        )
    except InvalidTwoFactorCodeError:
        # 401: es un fallo de autenticación, no un dato mal formado. Mismo error
        # para un TOTP incorrecto y para un código de recuperación inválido o ya
        # usado -- distinguirlos revelaría el estado de la cuenta.
        return jsonify({"msg": "El código no es válido"}), 401

    # Segundo factor correcto: se liberan los contadores (ADR-023).
    rate_limit_guard.clear(policy.TWO_FACTOR_VERIFY, account_identity, _rate_limit_repository)
    rate_limit_guard.clear(
        policy.TWO_FACTOR_VERIFY, f"ip:{_client_ip()}", _rate_limit_repository
    )

    token = _issue_session_token(user_entity)

    return jsonify({
        "token": token,
        "user": to_public_user(user_entity),
        # Para que el Frontend pueda avisar "usaste un código de recuperación,
        # te quedan N" en vez de dejarlo pasar inadvertido.
        "used_recovery_code": result["used_recovery_code"],
        "recovery_codes_remaining": _recovery_code_repository.count_unused(user_entity.id),
    }), 200
