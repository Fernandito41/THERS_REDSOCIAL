# Excepciones de dominio para el flujo de autenticación (BACKEND_ARCHITECTURE.md
# §11 marca "no existen excepciones de dominio propias" como hueco — este
# módulo lo resuelve para register/login, sin depender de Flask ni SQLAlchemy).


class EmailAlreadyExistsError(Exception):
    """Se intentó registrar un email que ya existe en `users` (comparación
    case-insensitive vía CITEXT, ver DATABASE_ARCHITECTURE.md §5)."""


class UsernameAlreadyExistsError(Exception):
    """Se intentó registrar un username que ya existe en `users` (columna
    agregada en ADR-002 — docs/architecture/ADR-002-user-profile-fields.md)."""


class InvalidCredentialsError(Exception):
    """Login con email inexistente o password incorrecta. Deliberadamente no
    se distingue cuál de los dos casos ocurrió (mismo mensaje/código HTTP en
    la route) para no filtrar qué emails están registrados."""


class UserNotFoundError(Exception):
    """El `id` del JWT (get_jwt_identity()) no corresponde a ningún usuario
    real -- p. ej. la cuenta fue eliminada después de emitirse el token
    (GET /api/users/me, ver ADR-002 §3)."""


class UsernameChangeNotAllowedError(Exception):
    """Se intentó cambiar `username` antes de cumplirse la ventana de 30
    días desde el último cambio (regla ratificada en ADR-003
    §Evolución futura — "Cambios de username" —
    docs/architecture/ADR-003-profile-update-contract.md). El código HTTP
    quedaba "a definir en la implementación" en ese ADR (§Impacto en
    Backend); se traduce a 400 en la route para mantenerse dentro del
    catálogo de códigos que ADR-003 §Contrato PATCH ya documenta (no
    introduce 429, fuera de ese catálogo)."""
