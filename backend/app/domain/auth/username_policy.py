# Regla de negocio pura: cada cuánto puede un usuario volver a cambiar su
# `username` (ADR-003 §Evolución futura — "Cambios de username": máximo 1
# cambio cada 30 días — docs/architecture/ADR-003-profile-update-contract.md).
# Solo `datetime`/`date` de la librería estándar -- domain/ no debe importar
# Flask ni SQLAlchemy (BACKEND_ARCHITECTURE.md §7/§17). `today` es
# inyectable para que los tests sean deterministas sin acceder al reloj del
# sistema.

from datetime import date

USERNAME_CHANGE_COOLDOWN_DAYS = 30


def can_change_username(last_changed_at, today=None):
    """`last_changed_at` es `users.username_changed_at` (un `datetime` con
    zona horaria, o `None` si el usuario nunca cambió su username -- en ese
    caso el cambio siempre está permitido). Devuelve `True` si ya
    transcurrieron `USERNAME_CHANGE_COOLDOWN_DAYS` días desde el último
    cambio."""
    if last_changed_at is None:
        return True

    today = today or date.today()
    last_change_date = (
        last_changed_at.date() if hasattr(last_changed_at, "date") else last_changed_at
    )
    return (today - last_change_date).days >= USERNAME_CHANGE_COOLDOWN_DAYS
