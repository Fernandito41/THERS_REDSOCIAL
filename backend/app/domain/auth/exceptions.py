# Excepciones de dominio para el flujo de autenticación (BACKEND_ARCHITECTURE.md
# §11 marca "no existen excepciones de dominio propias" como hueco — este
# módulo lo resuelve para register/login, sin depender de Flask ni SQLAlchemy).


class EmailAlreadyExistsError(Exception):
    """Se intentó registrar un email que ya existe en `users` (comparación
    case-insensitive vía CITEXT, ver DATABASE_ARCHITECTURE.md §5)."""


class InvalidCredentialsError(Exception):
    """Login con email inexistente o password incorrecta. Deliberadamente no
    se distingue cuál de los dos casos ocurrió (mismo mensaje/código HTTP en
    la route) para no filtrar qué emails están registrados."""
