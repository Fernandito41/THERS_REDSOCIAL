class CannotRestrictSelfError(Exception):
    """No se puede bloquear ni restringir la propia cuenta."""


class AccountBlockedError(Exception):
    """La cuenta destino está bloqueada por quien intenta interactuar con ella.

    Es distinta del caso inverso (el destino bloqueó a quien actúa): a quien
    bloqueó se le puede decir qué pasa; a quien fue bloqueado no se le revela,
    se le responde como si la cuenta no existiera (ADR-029 §Seguridad)."""
