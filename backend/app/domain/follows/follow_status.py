# Estados posibles de un follow (ADR-018-private-accounts.md). Solo tipos
# nativos de Python -- domain/ no debe importar Flask ni SQLAlchemy
# (BACKEND_ARCHITECTURE.md §7/§17), mismo patrón que
# domain/posts/validators.py.
#
# Antes de ADR-018 un follow era binario: la fila de `follows` existía o no.
# Con cuentas privadas hace falta un tercer hecho ("pidió seguirme y no le
# respondí todavía"), así que el estado vive en una columna de esa misma fila
# -- no en una tabla aparte de solicitudes (ADR-018 §Opciones consideradas).

#: Relación efectiva: el seguidor ve el contenido privado del seguido.
ACCEPTED = "accepted"

#: Solicitud sin responder. Solo alcanzable hacia una cuenta `is_private`.
#: No concede ninguna visibilidad -- un pendiente no es un seguidor.
PENDING = "pending"

VALID_STATUSES = (ACCEPTED, PENDING)


def is_valid_status(value):
    return value in VALID_STATUSES
