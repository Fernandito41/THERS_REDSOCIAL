# Validaciones puras de los campos de perfil de registro (ADR-002 —
# docs/architecture/ADR-002-user-profile-fields.md). Solo `re`/`datetime` de
# la librería estándar -- domain/ no debe importar Flask ni SQLAlchemy
# (BACKEND_ARCHITECTURE.md §7/§17).
#
# Deliberadamente NO se valida aquí formato de `email` ni longitud mínima de
# `password`: siguen `PENDIENTE DE APROBACIÓN` (API_CONTRACT.md §9, ítem 2),
# sin cambios por este módulo.

import re
from datetime import date

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
COUNTRY_CODE_RE = re.compile(r"^\+[1-9]\d{0,3}$")

# Mismo placeholder de edad mínima que el Frontend (dateUtils.js,
# MIN_AGE_YEARS) -- ratificado como regla real del servidor en ADR-002 §3.
MIN_AGE_YEARS = 13


def is_valid_username(value):
    return isinstance(value, str) and bool(USERNAME_RE.match(value))


def is_valid_phone(value):
    if not isinstance(value, str):
        return False
    digits_only = re.sub(r"[^0-9]", "", value)
    return 7 <= len(digits_only) <= 15


def is_valid_country_code(value):
    return isinstance(value, str) and bool(COUNTRY_CODE_RE.match(value))


def parse_birth_date(value):
    """Devuelve un `date` si `value` es una fecha ISO (yyyy-mm-dd) válida,
    o `None` si no lo es -- nunca lanza excepción, para que la route decida
    el mensaje/código HTTP."""
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def meets_minimum_age(birth_date, today=None, min_age_years=MIN_AGE_YEARS):
    today = today or date.today()
    age = today.year - birth_date.year
    had_birthday_this_year = (today.month, today.day) >= (birth_date.month, birth_date.day)
    if not had_birthday_this_year:
        age -= 1
    return age >= min_age_years
