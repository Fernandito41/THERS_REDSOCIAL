# Política de la eliminación de cuenta (ADR-031-account-deletion.md). Solo tipos
# nativos de Python -- domain/ no importa Flask ni SQLAlchemy
# (BACKEND_ARCHITECTURE.md §17). Mismo criterio que domain/auth/token_policy.py:
# placeholders de producto explícitos y revisables, no variables de entorno.

# Mismo perfil de riesgo que un OTP de recuperación (ADR-010): seis dígitos,
# vigencia corta, pocos intentos. Constantes propias e independientes: el código
# de eliminación NUNCA debe servir para recuperar una contraseña ni al revés
# (mismo razonamiento que ADR-011).
ACCOUNT_DELETION_CODE_TTL_MINUTES = 10
ACCOUNT_DELETION_MAX_ATTEMPTS = 5
ACCOUNT_DELETION_REQUEST_COOLDOWN_SECONDS = 60

# Palabra que la persona escribe para confirmar (ADR-031 §Decisiones del equipo,
# A.4). Se compara tal cual: mayúsculas exactas y sin espacios, así un
# autocompletado o un clic distraído no la satisface.
ACCOUNT_DELETION_CONFIRMATION_WORD = "DELETE"
