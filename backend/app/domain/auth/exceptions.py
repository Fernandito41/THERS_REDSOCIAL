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


class InvalidOrExpiredResetTokenError(Exception):
    """La autorización temporal de POST /api/reset-password (ADR-010-password-reset-otp-flow.md,
    reemplaza el token de enlace de ADR-009) no existe, ya expiró, o ya fue
    usada -- los tres casos se tratan igual (mismo mensaje/código 400 en la
    route) para no revelar cuál de los tres ocurrió."""


class InvalidResetCodeError(Exception):
    """POST /api/verify-reset-code (ADR-010-password-reset-otp-flow.md)
    rechazó el código -- cubre, sin distinguirlos en la respuesta: email que
    no corresponde a ningún usuario, sin solicitud activa, código incorrecto,
    código expirado, y intentos agotados. Unificar todos estos casos en el
    mismo mensaje evita tanto la enumeración de usuarios (§Seguridad) como
    un canal lateral que revelara "intentos agotados" solo para emails
    reales -- agotar los intentos bloquea la solicitud igual, sin que el
    mensaje lo distinga de un código simplemente incorrecto."""


class InvalidRegistrationCodeError(Exception):
    """POST /api/verify-registration-code (ADR-011-mandatory-email-verification.md)
    rechazó el código -- cubre, sin distinguirlos en la respuesta: email que
    no corresponde a ningún usuario, cuenta ya verificada, sin código activo,
    código incorrecto, código expirado, e intentos agotados. Mismo criterio
    que InvalidResetCodeError (ADR-010) -- unificar evita tanto enumeración
    de usuarios como un canal lateral que revelara "intentos agotados" solo
    para cuentas reales."""


class EmailNotVerifiedError(Exception):
    """POST /api/login con credenciales correctas mostraría que la cuenta
    todavía no completó la verificación obligatoria de email
    (ADR-011-mandatory-email-verification.md §Decisión) -- se distingue de
    InvalidCredentialsError porque la contraseña sí era correcta: la route
    responde 403 (no 401) y, deliberadamente, nunca emite un JWT de sesión
    normal mientras la cuenta siga sin verificar."""


class InvalidGoogleCredentialError(Exception):
    """POST /api/auth/google (ADR-012-google-sign-in.md) recibió un
    `credential` que `GoogleIdentityVerifier` no pudo validar
    criptográficamente -- firma inválida, `iss`/`aud` incorrectos, expirado,
    o simplemente no es un JWT bien formado. Se traduce a 400 en la route,
    sin distinguir el motivo exacto en el mensaje (nunca hay una cuenta de
    THERS involucrada todavía en este punto, así que no hay enumeración que
    proteger -- es simplemente "esta credencial de Google no es válida")."""


class GoogleEmailNotVerifiedError(Exception):
    """El propio Google, en el claim `email_verified` del ID Token, indica
    que esa dirección de correo no está verificada de su lado (caso raro --
    la inmensa mayoría de cuentas de Google normales sí lo tienen en `true`,
    ver ADR-012 §Decisión, FASE 8). THERS nunca trata ese email como
    confiable en ese caso: no crea cuenta, no vincula, no inicia sesión."""


class IdentityAlreadyLinkedError(Exception):
    """Se intentó vincular una identidad externa (`provider`,
    `provider_subject`) que ya está vinculada a otro usuario de THERS --
    en la práctica, solo posible por una condición de carrera (dos requests
    simultáneas del mismo `POST /api/auth/google` para una cuenta de Google
    que todavía no existía en THERS), ya que `find_by_provider_and_subject`
    ya se consulta antes de intentar crear (`ADR-012` §Seguridad)."""
