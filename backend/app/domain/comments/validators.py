# Validación pura del contenido de un comentario (ADR-006-comments-minimal-model.md).
# Solo tipos nativos de Python -- domain/ no debe importar Flask ni
# SQLAlchemy (BACKEND_ARCHITECTURE.md §7/§17). Mismo patrón que
# domain/posts/validators.py.

MAX_CONTENT_LENGTH = 1000


def is_valid_content(value):
    """No vacío tras trim() y dentro del límite máximo. El límite es un
    placeholder de producto explícito y revisable, más corto que el de
    posts (2000, ADR-004) -- mismo criterio pragmático, no una regla
    derivada (ADR-006 §Modelo de datos)."""
    if not isinstance(value, str):
        return False
    trimmed = value.strip()
    return 0 < len(trimmed) <= MAX_CONTENT_LENGTH
