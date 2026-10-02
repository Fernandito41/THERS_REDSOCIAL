# Excepciones de dominio del 2FA (ADR-022-two-factor-authentication.md).
# En un módulo propio y no en domain/auth/exceptions.py para no engordar el de
# autenticación básica, que ya tiene siete -- mismo criterio que separa
# domain/follows/exceptions.py de domain/auth/exceptions.py.


class TwoFactorAlreadyEnabledError(Exception):
    """Se intentó iniciar o confirmar un alta de 2FA sobre una cuenta que ya lo
    tiene activo. Para cambiar de dispositivo hay que desactivarlo y volver a
    activarlo: regenerar el secreto de un 2FA activo dejaría afuera al
    dispositivo que funcionaba si el alta nueva no se completa. La route lo
    traduce a 409 -- el pedido es válido pero choca con el estado del recurso
    (mismo criterio que UsernameAlreadyExistsError, ADR-003)."""


class TwoFactorNotEnabledError(Exception):
    """Se intentó desactivar el 2FA, o regenerar códigos de recuperación, sobre
    una cuenta que no lo tiene activo. La route lo traduce a 409."""


class TwoFactorSetupNotStartedError(Exception):
    """Se intentó confirmar un alta de 2FA sin haber pedido antes un secreto
    (`POST /api/2fa/setup`). La route lo traduce a 409: falta un paso previo,
    no es un dato mal formado."""


class InvalidTwoFactorCodeError(Exception):
    """El código no es un TOTP válido para el secreto de la cuenta ni un código
    de recuperación sin usar.

    **Un solo error para los dos casos, a propósito:** distinguir "ese no era un
    TOTP pero lo probé como recuperación" revelaría qué formato espera el
    servidor y en qué estado está la cuenta. La route lo traduce a 401 en el
    login (es un fallo de autenticación) y a 400 durante el alta (ahí la
    identidad ya está probada; lo que falla es el dato)."""


class TwoFactorRequiredError(Exception):
    """Credenciales correctas, pero la cuenta tiene 2FA activo: falta el segundo
    factor. No es un fallo -- es el estado intermedio esperado del login. La
    route lo traduce a un 200 con `two_factor_required: true` y un token de
    desafío, nunca a un 4xx: nada salió mal (ADR-022 §Contrato API)."""
