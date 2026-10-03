# Excepciones de la eliminación de cuenta (ADR-031-account-deletion.md).


class InvalidDeletionCodeError(Exception):
    """Cuenta inexistente, sin solicitud activa, código vencido, intentos
    agotados o código incorrecto. **Un solo error para todos los casos**:
    distinguirlos permitiría enumerar correos registrados (ADR-031 §Seguridad,
    mismo criterio que ADR-010)."""


class DeletionConfirmationError(Exception):
    """El correo escrito no coincide con el de la cuenta, o la palabra de
    confirmación no es exactamente `DELETE`. Se lanza **solo con el código ya
    verificado**, así no sirve para averiguar si un correo existe."""


class TwoFactorRequiredForDeletionError(Exception):
    """La cuenta tiene 2FA y no se envió `two_factor_code`. Se lanza **solo con
    el código de correo ya verificado** y sin consumirlo (ADR-031 §Seguridad):
    antes de eso, responder "falta el 2FA" revelaría que la cuenta existe y lo
    tiene activo."""
