# Constantes de política para los tokens de un solo uso (recuperación de
# contraseña, verificación de email --
# ADR-009-password-reset-and-email-verification.md). Mismo criterio que
# MIN_AGE_YEARS/MIN_PASSWORD_LENGTH (domain/auth/validators.py) y
# USERNAME_CHANGE_COOLDOWN_DAYS (domain/auth/username_policy.py):
# placeholders de producto explícitos y revisables, no configurables por
# variable de entorno -- son reglas de negocio, no parámetros de despliegue.

# Recuperación de contraseña, flujo OTP (ADR-010-password-reset-otp-flow.md,
# reemplaza el flujo de enlace de ADR-009). Ventana corta -- un código de
# reset es sensible (permite tomar la cuenta) y se espera que se use en
# minutos, no en días.
PASSWORD_RESET_CODE_TTL_MINUTES = 10

# Máximo de intentos de verificación por código (ADR-010 §Seguridad): un
# código de 6 dígitos tiene solo 10^6 combinaciones -- sin límite de
# intentos, alguien con Postman podría agotarlas en segundos. 5 intentos
# combinados con la ventana de 10 minutos de arriba deja una probabilidad de
# acierto por fuerza bruta de como mucho 5/1.000.000 (0.0005%) durante toda
# la vida útil de un código -- mismo orden de magnitud que el límite de
# intentos que usan la mayoría de flujos de OTP por SMS/email de la
# industria (bancos, 2FA). Agotar los intentos no borra el código ni
# revela nada distinto en la respuesta (mismo mensaje genérico que un
# código incorrecto) -- solo lo vuelve inutilizable, obligando a pedir uno
# nuevo.
PASSWORD_RESET_MAX_ATTEMPTS = 5

# Vigencia de la autorización temporal emitida tras verificar el código
# correctamente (ADR-010 §Decisión) -- el token opaco que el Frontend usa
# para POST /api/reset-password sin tener que reintroducir el código. Mismo
# valor que el TTL del código: tiempo de sobra para completar el formulario
# de nueva contraseña sin reabrir una ventana de ataque más larga que la que
# ya existía durante la verificación del OTP.
PASSWORD_RESET_AUTHORIZATION_TTL_MINUTES = 10

# Cooldown anti-spam de POST /api/forgot-password (también reutilizado para
# "Reenviar código", ADR-010 §Decisión): evita que pedir el mismo reset
# repetidas veces en poco tiempo genere un correo por cada click. No afecta
# la respuesta genérica -- el endpoint sigue devolviendo el mismo mensaje,
# solo no genera un código ni un correo nuevo si ya hay uno reciente sin
# usar. Impuesto en el backend (no solo en el Frontend, ADR-010 §Fase 11 de
# la tarea) -- una request directa por Postman ignorando la cuenta regresiva
# del Frontend también lo respeta.
PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS = 60

# Verificación obligatoria de email al registrarse, flujo OTP
# (ADR-011-mandatory-email-verification.md, reemplaza el flujo de enlace
# EMAIL_VERIFICATION_TOKEN_TTL_HOURS/EMAIL_VERIFICATION_REQUEST_COOLDOWN_SECONDS
# de ADR-009-password-reset-and-email-verification.md). Mismos valores que
# PASSWORD_RESET_* -- mismo perfil de riesgo (código de 6 dígitos) -- pero
# como constantes propias e independientes: un código de registro NUNCA
# debe poder usarse para recuperar una contraseña ni viceversa (ADR-011
# §Seguridad), y cada política puede divergir a futuro sin acoplar ambos
# flujos entre sí.
REGISTRATION_CODE_TTL_MINUTES = 10
REGISTRATION_MAX_ATTEMPTS = 5
REGISTRATION_CODE_REQUEST_COOLDOWN_SECONDS = 60
