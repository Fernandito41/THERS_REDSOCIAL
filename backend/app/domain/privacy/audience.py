# Audiencias de una preferencia de privacidad: quién puede hacerte algo
# (ADR-023-mentions.md para `who_can_mention`,
# ADR-024-content-filters-and-privacy-preferences.md para `who_can_message`).
#
# Un único vocabulario compartido por las dos preferencias en vez de uno por
# cada una: significan lo mismo ("qué conjunto de personas está autorizado"),
# así que duplicarlo invitaría a que se desincronizaran. Solo tipos nativos de
# Python -- domain/ no importa Flask ni SQLAlchemy (BACKEND_ARCHITECTURE.md
# §7/§17).

#: Cualquier cuenta autenticada. Es el comportamiento que el producto tenía de
#: hecho antes de que estas preferencias existieran, así que es el DEFAULT de
#: las dos columnas.
EVERYONE = "everyone"

#: Solo quienes te siguen con un follow **aceptado** (ADR-022). Ojo con la
#: dirección: "me sigue a mí", no "yo lo sigo".
FOLLOWERS = "followers"

#: Nadie. Ni siquiera tus seguidores.
NOBODY = "nobody"

VALID_AUDIENCES = (EVERYONE, FOLLOWERS, NOBODY)


def is_valid_audience(value):
    return value in VALID_AUDIENCES


def is_allowed(audience, actor_is_follower, actor_is_self=False):
    """¿Puede actuar alguien con esos atributos, dada esa `audience`?

    `actor_is_self` existe porque las dos preferencias se consultan en
    contextos donde el actor puede ser el propio dueño: mencionarse a sí mismo
    en su propia publicación es legítimo aunque tenga `who_can_mention` en
    'nobody' -- la preferencia protege de los demás, no de uno mismo. (Para
    mensajes nunca se da: `ck_messages_no_self_message` ya impide mandarse un
    mensaje a sí mismo, ADR-013.)
    """
    if actor_is_self:
        return True
    if audience == EVERYONE:
        return True
    if audience == FOLLOWERS:
        return actor_is_follower
    # NOBODY, o cualquier valor que no reconozcamos: se deniega. Un valor
    # inesperado en la columna nunca debe abrir permisos por accidente.
    return False
