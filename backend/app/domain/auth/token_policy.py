# Constantes de política para los tokens de un solo uso (recuperación de
# contraseña, verificación de email --
# ADR-009-password-reset-and-email-verification.md). Mismo criterio que
# MIN_AGE_YEARS/MIN_PASSWORD_LENGTH (domain/auth/validators.py) y
# USERNAME_CHANGE_COOLDOWN_DAYS (domain/auth/username_policy.py):
# placeholders de producto explícitos y revisables, no configurables por
# variable de entorno -- son reglas de negocio, no parámetros de despliegue.

# Recuperación de contraseña: ventana corta -- un enlace de reset es
# sensible (permite tomar la cuenta) y se espera que se use en minutos, no
# en días.
PASSWORD_RESET_TOKEN_TTL_MINUTES = 30

# Cooldown anti-spam de POST /api/forgot-password: evita que pedir el mismo
# reset repetidas veces en poco tiempo genere un correo por cada click
# (ADR-009 §Seguridad). No afecta la respuesta genérica (FASE 4) -- el
# endpoint sigue devolviendo el mismo mensaje, solo no genera un token ni un
# correo nuevo si ya hay uno reciente sin usar.
PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS = 60

# Verificación de email: ventana más larga -- confirmar el email es un paso
# de onboarding, no una acción sensible en sí misma; forzar al usuario a
# volver a pedirlo cada 30 minutos sería fricción sin beneficio de
# seguridad real.
EMAIL_VERIFICATION_TOKEN_TTL_HOURS = 24

# Mismo criterio de cooldown que el reset de contraseña, para
# POST /api/send-verification-email.
EMAIL_VERIFICATION_REQUEST_COOLDOWN_SECONDS = 60
