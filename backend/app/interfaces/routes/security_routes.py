# Endpoints de la pantalla de Seguridad (REF-SET-03):
#   · GET/PATCH /api/users/me/security                      (ADR-021-session-registry.md)
#   · GET/DELETE /api/sessions y DELETE /api/sessions/<id>  (ADR-021-session-registry.md)
#   · GET/POST /api/2fa/setup, POST /api/2fa/confirm, POST /api/2fa/disable,
#     POST /api/2fa/recovery-codes                           (ADR-022-two-factor-authentication.md)
#
# `POST /api/2fa/verify` NO vive acá sino en auth_routes.py: es el segundo paso
# de un login, no una operación sobre una cuenta ya autenticada -- es el único
# de estos endpoints que no lleva `@jwt_required()`.
#
# Blueprint propio, separado de privacy_bp (ADR-018/ADR-019/ADR-020): privacidad
# es "quién ve qué", seguridad es "quién puede entrar". Comparten pantalla de
# Configuración pero no dominio.
#
# Composition root igual que el resto de interfaces/routes/
# (BACKEND_ARCHITECTURE.md §17).

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.application.sessions.manage_sessions_use_case import (
    DEFAULT_LIMIT,
    list_sessions,
    revoke_other_sessions,
    revoke_session,
)
from app.application.rate_limiting import rate_limit_guard
from app.application.two_factor.two_factor_use_case import (
    confirm_two_factor_setup,
    disable_two_factor,
    get_two_factor_status,
    regenerate_recovery_codes,
    start_two_factor_setup,
)
from app.domain.auth.exceptions import InvalidCredentialsError, UserNotFoundError
from app.domain.auth.two_factor_exceptions import (
    InvalidTwoFactorCodeError,
    TwoFactorAlreadyEnabledError,
    TwoFactorNotEnabledError,
    TwoFactorSetupNotStartedError,
)
from app.domain.rate_limiting import policy
from app.domain.rate_limiting.exceptions import RateLimitExceededError
from app.domain.sessions.exceptions import SessionNotFoundError
from app.infrastructure.auth.pyotp_totp_provider import PyotpTotpProvider
from app.infrastructure.persistence.repositories.rate_limit_repository import (
    SQLAlchemyRateLimitRepository,
)
from app.infrastructure.persistence.repositories.session_repository import (
    SQLAlchemySessionRepository,
)
from app.infrastructure.persistence.repositories.two_factor_recovery_code_repository import (
    SQLAlchemyTwoFactorRecoveryCodeRepository,
)
from app.infrastructure.persistence.repositories.user_repository import (
    SQLAlchemyUserRepository,
)

security_bp = Blueprint("security", __name__)

_user_repository = SQLAlchemyUserRepository()
_session_repository = SQLAlchemySessionRepository()
_recovery_code_repository = SQLAlchemyTwoFactorRecoveryCodeRepository()
_totp_provider = PyotpTotpProvider()
# ADR-023-rate-limiting.md: los tres endpoints que verifican una credencial
# (un código TOTP al confirmar, la contraseña al desactivar o regenerar)
# limitan intentos.
_rate_limit_repository = SQLAlchemyRateLimitRepository()


def _rate_limited_response(error):
    """429 uniforme con `Retry-After` (ADR-023 §Contrato API). Mismo formato que
    el de auth_routes.py; se repite acá porque son blueprints distintos y
    compartirlo exigiría un módulo común para seis líneas."""
    response = jsonify({
        "msg": "Demasiados intentos. Esperá un momento antes de volver a probar.",
        "retry_after_seconds": error.retry_after_seconds,
    })
    response.status_code = 429
    response.headers["Retry-After"] = str(error.retry_after_seconds)
    return response


def _enforce_two_factor_manage_limit(user_id):
    """Límite de los endpoints de gestión del 2FA, por cuenta.

    Por cuenta y no por IP: estos endpoints son protegidos, así que la identidad
    ya está probada -- quien intenta adivinar la contraseña acá es alguien que
    robó el token de sesión, y lo que hay que acotar son sus intentos sobre
    **esta** cuenta (ADR-023).
    """
    rate_limit_guard.enforce(
        policy.TWO_FACTOR_MANAGE, f"user:{user_id}", _rate_limit_repository
    )


def _clear_two_factor_manage_limit(user_id):
    rate_limit_guard.clear(
        policy.TWO_FACTOR_MANAGE, f"user:{user_id}", _rate_limit_repository
    )


def _current_jti():
    """El `jti` del token con el que se hizo esta petición.

    Se usa para marcar "este dispositivo" en la lista y para no cerrar la propia
    sesión en `DELETE /api/sessions`. **Nunca se devuelve al cliente** -- es el
    identificador que valida cada petición (ver session_presenter.py).
    """
    return get_jwt().get("jti")


# ===========================================================================
# Sesiones activas (ADR-021)
# ===========================================================================
@security_bp.route("/sessions", methods=["GET"])
@jwt_required()
def get_sessions():
    # Identidad exclusivamente del JWT: nadie lista las sesiones de otro.
    user_id = get_jwt_identity()
    sessions = list_sessions(user_id, _current_jti(), _session_repository, DEFAULT_LIMIT)
    return jsonify({"sessions": sessions}), 200


@security_bp.route("/sessions/<uuid:session_id>", methods=["DELETE"])
@jwt_required()
def delete_session(session_id):
    user_id = get_jwt_identity()

    try:
        result = revoke_session(user_id, str(session_id), _current_jti(), _session_repository)
    except SessionNotFoundError:
        # Mismo 404 si no existe, si ya estaba cerrada o si es de otra persona
        # -- no revela cuál de los tres ocurrió.
        return jsonify({"msg": "Sesión no encontrada"}), 404

    # `was_current` en el body: si cerró la suya, el token con el que hizo esta
    # petición ya no sirve para la siguiente, y el Frontend tiene que ir a /login.
    return jsonify(result), 200


@security_bp.route("/sessions", methods=["DELETE"])
@jwt_required()
def delete_other_sessions():
    # Cierra todas menos la actual. No lleva id en la URL porque la acción es
    # "las demás", no "una concreta".
    user_id = get_jwt_identity()
    result = revoke_other_sessions(user_id, _current_jti(), _session_repository)
    return jsonify(result), 200


# ===========================================================================
# 2FA (ADR-022)
# ===========================================================================
@security_bp.route("/2fa", methods=["GET"])
@jwt_required()
def two_factor_status():
    user_id = get_jwt_identity()

    try:
        status = get_two_factor_status(user_id, _user_repository, _recovery_code_repository)
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({"two_factor": status}), 200


@security_bp.route("/2fa/setup", methods=["POST"])
@jwt_required()
def two_factor_setup():
    # Primer paso del alta: genera un secreto y lo guarda SIN activar el 2FA.
    # La respuesta lleva el secreto en claro (hace falta para el QR y para el
    # alta manual) -- por eso el endpoint es POST y protegido, y por eso el
    # valor nunca se registra en un log (ADR-022 §Seguridad).
    user_id = get_jwt_identity()

    try:
        result = start_two_factor_setup(user_id, _user_repository, _totp_provider)
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    except TwoFactorAlreadyEnabledError:
        # 409: el pedido es válido pero choca con el estado actual. Para cambiar
        # de dispositivo hay que desactivar primero.
        return jsonify(
            {"msg": "Ya tenés la verificación en dos pasos activada. Desactivala antes de volver a configurarla."}
        ), 409

    return jsonify({"two_factor_setup": result}), 200


@security_bp.route("/2fa/confirm", methods=["POST"])
@jwt_required()
def two_factor_confirm():
    # Segundo paso del alta: exige un código válido del secreto guardado y recién
    # entonces activa el 2FA. Devuelve los códigos de recuperación, que es la
    # ÚNICA vez que existen en claro.
    user_id = get_jwt_identity()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    code = data.get("code")
    if not isinstance(code, str) or not code.strip():
        return jsonify({"msg": "Falta el código de tu app autenticadora"}), 400

    # Un código TOTP son 10^6 combinaciones: también acá hay que acotar los
    # intentos, aunque la identidad ya esté probada (ADR-023).
    try:
        _enforce_two_factor_manage_limit(user_id)
    except RateLimitExceededError as error:
        return _rate_limited_response(error)

    try:
        result = confirm_two_factor_setup(
            user_id, code, _user_repository, _recovery_code_repository, _totp_provider
        )
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    except TwoFactorAlreadyEnabledError:
        return jsonify({"msg": "Ya tenés la verificación en dos pasos activada."}), 409
    except TwoFactorSetupNotStartedError:
        return jsonify(
            {"msg": "Primero tenés que generar un código QR para vincular tu app."}
        ), 409
    except InvalidTwoFactorCodeError:
        # 400 y no 401: la identidad ya está probada (el endpoint es protegido);
        # lo que falla es el dato. En el login el mismo error sí es 401.
        return jsonify(
            {"msg": "El código no coincide. Revisá que la hora de tu teléfono esté bien y probá con el siguiente."}
        ), 400

    _clear_two_factor_manage_limit(user_id)
    return jsonify(result), 200


@security_bp.route("/2fa/disable", methods=["POST"])
@jwt_required()
def two_factor_disable():
    # Pide la CONTRASEÑA, no un código TOTP: si alguien perdió el dispositivo,
    # exigir un código lo dejaría atrapado con el 2FA puesto para siempre
    # (ADR-022 §Decisión).
    #
    # Es POST y no DELETE aunque "apague" algo: además de desactivar, borra los
    # códigos de recuperación y cierra todas las sesiones. No es la eliminación
    # de un recurso, es una operación con efectos.
    user_id = get_jwt_identity()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    try:
        _enforce_two_factor_manage_limit(user_id)
    except RateLimitExceededError as error:
        return _rate_limited_response(error)

    try:
        result = disable_two_factor(
            user_id,
            data.get("password"),
            _user_repository,
            _recovery_code_repository,
            _session_repository,
        )
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    except TwoFactorNotEnabledError:
        return jsonify({"msg": "No tenés la verificación en dos pasos activada."}), 409
    except InvalidCredentialsError:
        # Mismo mensaje genérico que un login fallido -- no revela si la cuenta
        # tiene contraseña (una cuenta creada solo con Google no la tiene,
        # ADR-012).
        return jsonify({"msg": "La contraseña no es correcta"}), 401

    _clear_two_factor_manage_limit(user_id)

    # Todas las sesiones quedaron cerradas, incluida la de quien pidió esto:
    # bajar la protección de la cuenta es el momento de forzar un login nuevo.
    return jsonify({**result, "sessions_revoked": True}), 200


@security_bp.route("/2fa/recovery-codes", methods=["POST"])
@jwt_required()
def two_factor_regenerate_recovery_codes():
    # Regenerar invalida los anteriores en la misma operación. Pide contraseña
    # por el mismo motivo que desactivar: es una credencial de acceso.
    user_id = get_jwt_identity()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    try:
        _enforce_two_factor_manage_limit(user_id)
    except RateLimitExceededError as error:
        return _rate_limited_response(error)

    try:
        result = regenerate_recovery_codes(
            user_id, data.get("password"), _user_repository, _recovery_code_repository
        )
    except UserNotFoundError:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    except TwoFactorNotEnabledError:
        return jsonify({"msg": "No tenés la verificación en dos pasos activada."}), 409
    except InvalidCredentialsError:
        return jsonify({"msg": "La contraseña no es correcta"}), 401

    _clear_two_factor_manage_limit(user_id)
    return jsonify(result), 200


# ===========================================================================
# Preferencias de seguridad (ADR-021)
# ===========================================================================
# Endpoint propio y NO parte de `PATCH /api/users/me/privacy` (ADR-020): aquel
# contrato es "quién ve qué" y este es "quién puede entrar". Hoy transporta una
# sola preferencia, y es el lugar correcto para ella -- meterla en el de
# privacidad obligaría a la próxima persona a buscarla donde no está.
#
# Whitelist declarada como dato, igual que en privacy_routes.py: agregar una
# preferencia es una línea y es imposible que se cuele una columna que no esté
# en la tupla (mismo principio anti mass-assignment que ADR-003 §Seguridad).
_BOOLEAN_SECURITY_FIELDS = ("login_alerts_enabled",)


def _security_settings(user):
    return {"login_alerts_enabled": user.login_alerts_enabled}


@security_bp.route("/users/me/security", methods=["GET"])
@jwt_required()
def get_security_settings():
    user_id = get_jwt_identity()
    user = _user_repository.find_by_id(user_id)
    if user is None:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({"security": _security_settings(user)}), 200


@security_bp.route("/users/me/security", methods=["PATCH"])
@jwt_required()
def patch_security_settings():
    user_id = get_jwt_identity()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"msg": "No se recibió ningún campo para actualizar"}), 400

    fields = {}
    for field in _BOOLEAN_SECURITY_FIELDS:
        if field in data:
            value = data.get(field)
            # `isinstance(value, bool)` y no truthiness: aceptar el string
            # "false" (verdadero en Python) dejaría a alguien creyendo que
            # apagó las alertas cuando las encendió.
            if not isinstance(value, bool):
                return jsonify({"msg": f"`{field}` debe ser true o false"}), 400
            fields[field] = value

    if not fields:
        return jsonify({"msg": "No se recibió ningún campo para actualizar"}), 400

    user = _user_repository.update(user_id, fields)
    if user is None:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({"security": _security_settings(user)}), 200
