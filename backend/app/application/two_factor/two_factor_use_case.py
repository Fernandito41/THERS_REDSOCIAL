# Casos de uso del 2FA con TOTP (ADR-026-two-factor-authentication.md).
#
# El alta tiene DOS pasos a propósito:
#   1. `start_two_factor_setup` genera un secreto y lo guarda **sin activar**.
#   2. `confirm_two_factor_setup` exige un código válido de ese secreto y recién
#      entonces activa el 2FA y entrega los códigos de recuperación.
#
# Sin esa separación, escanear el QR y abandonar (o escanearlo mal) dejaría la
# cuenta exigiendo un código que la app de la persona no puede generar: se
# quedaría afuera de su propia cuenta sin haber terminado de configurar nada.
#
# `user_id` sale siempre de get_jwt_identity() en la route.

from app.domain.auth.auth_service import hash_password, verify_password
from app.domain.auth.exceptions import InvalidCredentialsError, UserNotFoundError
from app.domain.auth.token_generator import (
    generate_recovery_code,
    normalize_recovery_code,
)
from app.domain.auth.two_factor import RECOVERY_CODES_COUNT
from app.domain.auth.two_factor_exceptions import (
    InvalidTwoFactorCodeError,
    TwoFactorAlreadyEnabledError,
    TwoFactorNotEnabledError,
    TwoFactorSetupNotStartedError,
)

#: Nombre que la app autenticadora muestra como emisor. Constante del producto,
#: no configurable: cambiarla haría que las entradas ya vinculadas se vieran
#: con un nombre distinto al de las nuevas.
TOTP_ISSUER = "THERS"


def get_two_factor_status(user_id, user_repository, recovery_code_repository):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()

    return {
        "enabled": user.two_factor_enabled,
        # Hay un secreto guardado pero todavía sin confirmar: el Frontend lo usa
        # para ofrecer "continuá donde lo dejaste" en vez de empezar de cero.
        "setup_pending": user.totp_secret is not None and not user.two_factor_enabled,
        "recovery_codes_remaining": (
            recovery_code_repository.count_unused(user_id)
            if user.two_factor_enabled
            else 0
        ),
    }


def start_two_factor_setup(user_id, user_repository, totp_provider):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    if user.two_factor_enabled:
        # Para cambiar de dispositivo hay que desactivar y volver a activar:
        # regenerar el secreto de un 2FA activo dejaría afuera al dispositivo
        # que funcionaba si la persona no completa el nuevo alta.
        raise TwoFactorAlreadyEnabledError()

    # Un `start` repetido genera un secreto nuevo y descarta el anterior: si
    # alguien empezó el alta, cerró la pantalla y volvió, lo que tenga a medio
    # escanear ya no sirve y es mejor que empiece limpio.
    secret = totp_provider.generate_secret()
    user_repository.update(user_id, {"totp_secret": secret})

    # El `otpauth://` lleva el secreto en claro: solo puede viajar a quien ya
    # está autenticado, y nunca debe registrarse en un log (ADR-026 §Seguridad).
    return {
        "secret": secret,
        "provisioning_uri": totp_provider.provisioning_uri(
            secret, account_name=user.email, issuer_name=TOTP_ISSUER
        ),
    }


def confirm_two_factor_setup(
    user_id, code, user_repository, recovery_code_repository, totp_provider
):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    if user.two_factor_enabled:
        raise TwoFactorAlreadyEnabledError()
    if user.totp_secret is None:
        raise TwoFactorSetupNotStartedError()

    if not totp_provider.verify(user.totp_secret, code):
        # El secreto NO se borra: la persona puede reintentar con el siguiente
        # código de su app sin volver a escanear el QR.
        raise InvalidTwoFactorCodeError()

    user_repository.update(user_id, {"two_factor_enabled": True})

    # Los códigos de recuperación se generan recién acá, no en `start`: antes de
    # confirmar no hay 2FA del que recuperarse, y entregarlos antes invitaría a
    # guardarlos para un 2FA que nunca se activó.
    return {"recovery_codes": _regenerate_recovery_codes(user_id, recovery_code_repository)}


def regenerate_recovery_codes(user_id, password, user_repository, recovery_code_repository):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    if not user.two_factor_enabled:
        raise TwoFactorNotEnabledError()

    _require_password(user, password)
    return {"recovery_codes": _regenerate_recovery_codes(user_id, recovery_code_repository)}


def disable_two_factor(
    user_id, password, user_repository, recovery_code_repository, session_repository
):
    user = user_repository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError()
    if not user.two_factor_enabled:
        raise TwoFactorNotEnabledError()

    # Desactivar el 2FA pide la contraseña, no un código TOTP: si alguien perdió
    # el dispositivo, exigir un código lo dejaría atrapado con el 2FA puesto
    # para siempre. La contraseña es lo que ya protegía la cuenta antes.
    _require_password(user, password)

    user_repository.update(user_id, {"two_factor_enabled": False, "totp_secret": None})
    # Los códigos se borran: dejarlos permitiría entrar con un código de
    # recuperación de un 2FA que ya no existe.
    recovery_code_repository.delete_all(user_id)

    # Y se cierran TODAS las sesiones, incluida la actual: bajar el nivel de
    # protección de la cuenta es exactamente el momento en que conviene forzar
    # un login nuevo (ADR-025/ADR-026 §Decisión).
    session_repository.revoke_all_for_user(user_id)

    return {"enabled": False}


# ---------------------------------------------------------------------------
# Verificación en el login (segundo paso del desafío)
# ---------------------------------------------------------------------------
def verify_two_factor_challenge(
    user, code, user_repository, recovery_code_repository, totp_provider
):
    """Valida el segundo factor de un login en curso.

    Acepta **o** un código TOTP de 6 dígitos **o** un código de recuperación.
    Se prueba el TOTP primero porque es el caso normal; el de recuperación es la
    excepción y consume el código.

    Lanza `InvalidTwoFactorCodeError` si ninguno de los dos valida -- con el
    mismo error en ambos casos, sin decir "ese no era un TOTP pero probé como
    recuperación": distinguirlo revelaría qué formato espera el servidor.
    """
    if totp_provider.verify(user.totp_secret, code):
        return {"used_recovery_code": False}

    normalized = normalize_recovery_code(code)
    if normalized:
        for recovery_code in recovery_code_repository.list_unused(user.id):
            # scrypt usa sal, así que no se puede buscar por hash: hay que
            # comparar contra cada uno. Son 10 como máximo.
            if verify_password(normalized, recovery_code.code_hash):
                # `mark_used` tiene la condición en el WHERE, así que dos
                # peticiones simultáneas con el mismo código no lo consumen
                # las dos -- la segunda falla y cae al error de abajo.
                if recovery_code_repository.mark_used(recovery_code.id):
                    return {"used_recovery_code": True}

    raise InvalidTwoFactorCodeError()


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------
def _require_password(user, password):
    # Una cuenta creada solo con Google no tiene contraseña (ADR-012), así que
    # no puede confirmar nada por esta vía. Se trata como credencial inválida,
    # sin revelar que la cuenta es Google-only -- mismo criterio que
    # login_use_case.
    if user.password_hash is None or not isinstance(password, str):
        raise InvalidCredentialsError()
    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()


def _regenerate_recovery_codes(user_id, recovery_code_repository):
    codes = [generate_recovery_code() for _ in range(RECOVERY_CODES_COUNT)]
    # Se hashea la forma NORMALIZADA (sin guion, en mayúsculas), que es la misma
    # contra la que después se compara -- si se hasheara la forma con guion,
    # escribir el código sin guion no validaría nunca.
    recovery_code_repository.replace_all(
        user_id, [hash_password(normalize_recovery_code(code)) for code in codes]
    )
    # Es la única vez que estos valores existen en claro: se devuelven acá y no
    # se pueden volver a consultar (solo quedan sus hashes).
    return codes
