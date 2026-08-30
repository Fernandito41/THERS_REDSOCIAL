# Validaciones puras de los campos de registro (ADR-002 —
# docs/architecture/ADR-002-user-profile-fields.md; email/password —
# API_CONTRACT.md §9 ítem 2, cerrado por decisión técnica de bajo impacto,
# ver informe de la tarea que agrega is_valid_email/is_valid_password). Solo
# `re`/`datetime` de la librería estándar -- domain/ no debe importar Flask
# ni SQLAlchemy (BACKEND_ARCHITECTURE.md §7/§17).

import re
from datetime import date

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
COUNTRY_CODE_RE = re.compile(r"^\+[1-9]\d{0,3}$")
# Formato básico -- exige un único "@" con algo a cada lado y un "." en la
# parte del dominio. No verifica que el dominio exista ni sigue la RFC 5322
# completa (deliberado: mismo nivel de rigor que el resto de este módulo,
# sin sobre-ingeniería). Rechaza espacios en blanco.
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

# Mismo placeholder de edad mínima que el Frontend (dateUtils.js,
# MIN_AGE_YEARS) -- ratificado como regla real del servidor en ADR-002 §3.
MIN_AGE_YEARS = 13

# Placeholder de producto, igual de revisable que MIN_AGE_YEARS -- no exige
# mayúscula/número/símbolo (esa combinación sí sería una decisión de UX de
# registro, fuera del alcance de esta validación de formato).
MIN_PASSWORD_LENGTH = 8


def is_valid_username(value):
    return isinstance(value, str) and bool(USERNAME_RE.match(value))


def is_valid_email(value):
    return isinstance(value, str) and bool(EMAIL_RE.match(value))


def is_valid_password(value, min_length=MIN_PASSWORD_LENGTH):
    return isinstance(value, str) and len(value) >= min_length


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
