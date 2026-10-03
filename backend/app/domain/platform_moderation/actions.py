# Acciones de la moderación de la plataforma (ADR-032, fase 2).
#
# OJO con los nombres: `domain/moderation` son los filtros PERSONALES de cada
# persona (palabras y temas silenciados, ADR-024). Esto es la moderación que
# hace el equipo sobre lo reportado, y por eso vive en `platform_moderation`.

ACTION_DISMISS = "dismiss"
ACTION_REMOVE_CONTENT = "remove_content"
ACTION_SUSPEND_USER = "suspend_user"

ACTIONS = (ACTION_DISMISS, ACTION_REMOVE_CONTENT, ACTION_SUSPEND_USER)

#: Estados que aparecen en la cola. `reviewing` queda reservado para una futura
#: «tomar el reporte»; hoy nada lo asigna.
QUEUE_STATUSES = ("open", "reviewing", "actioned", "dismissed")
DEFAULT_QUEUE_STATUS = "open"

MAX_NOTE_LENGTH = 500
MAX_SUSPENSION_REASON_LENGTH = 500

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

#: Lo que ve la persona suspendida si quien moderó no escribió un motivo propio.
#: La nota interna de la resolución NUNCA se le muestra: puede contener comentarios
#: del equipo que no son para ella.
DEFAULT_SUSPENSION_REASON = "Tu cuenta fue suspendida por incumplir las normas de la comunidad."
