# Tipos de objetivo, motivos y estados de un reporte
# (ADR-032-content-reports-and-moderation.md §1). Solo tipos nativos de Python
# -- domain/ no importa Flask ni SQLAlchemy (BACKEND_ARCHITECTURE.md §7/§17).
#
# Se validan en la aplicación, no con un ENUM de PostgreSQL: agregar un motivo
# nuevo no debería exigir una migración (mismo criterio que
# `domain/restrictions/kinds.py`, ADR-029).

TARGET_POST = "post"
TARGET_COMMENT = "comment"
TARGET_MESSAGE = "message"
TARGET_USER = "user"

TARGET_TYPES = (TARGET_POST, TARGET_COMMENT, TARGET_MESSAGE, TARGET_USER)

REASON_SPAM = "spam"
REASON_HARASSMENT = "harassment"
REASON_HATE = "hate"
REASON_SEXUAL = "sexual"
REASON_VIOLENCE = "violence"
REASON_SELF_HARM = "self_harm"
REASON_ILLEGAL = "illegal"
REASON_IMPERSONATION = "impersonation"
REASON_OTHER = "other"

REASONS = (
    REASON_SPAM,
    REASON_HARASSMENT,
    REASON_HATE,
    REASON_SEXUAL,
    REASON_VIOLENCE,
    REASON_SELF_HARM,
    REASON_ILLEGAL,
    REASON_IMPERSONATION,
    REASON_OTHER,
)

STATUS_OPEN = "open"
STATUS_REVIEWING = "reviewing"
STATUS_ACTIONED = "actioned"
STATUS_DISMISSED = "dismissed"

#: Límite del texto libre. Placeholder de producto explícito y revisable
#: (ADR-032 §1), mismo criterio que `MAX_CONTENT_LENGTH` en `domain/posts`.
MAX_DETAILS_LENGTH = 500

#: Máximo de texto que se copia del contenido reportado (ADR-032 §4). La copia
#: existe para que quien modera vea *qué se dijo* aunque el contenido se borre;
#: no es un archivo, y se vacía al resolver el reporte (fase 2).
MAX_SNAPSHOT_LENGTH = 2000
