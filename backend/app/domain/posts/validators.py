# Validación pura del contenido de un post (ADR-004-posts-minimal-model.md).
# Solo tipos nativos de Python -- domain/ no debe importar Flask ni
# SQLAlchemy (BACKEND_ARCHITECTURE.md §7/§17).

MAX_CONTENT_LENGTH = 2000


def is_valid_content(value):
    """No vacío tras trim() y dentro del límite máximo. El límite es un
    placeholder de producto explícito y revisable -- mismo criterio que
    MIN_AGE_YEARS/MIN_PASSWORD_LENGTH en domain/auth/validators.py."""
    if not isinstance(value, str):
        return False
    trimmed = value.strip()
    return 0 < len(trimmed) <= MAX_CONTENT_LENGTH
