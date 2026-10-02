# Forma pública de una mención, embebida en `post` y en `comment`
# (ADR-023-mentions.md §Contrato API) -- centralizada acá para que las dos la
# expongan idéntica, mismo patrón que application/auth/user_presenter.py.
#
# Se expone la misma forma reducida de usuario que `post.author` y
# `notification.actor`: nunca email/phone/password_hash. Que alguien te
# mencione no revela nada tuyo que no fuera público.
#
# Para qué la necesita el Frontend: el texto guarda el @username tal como se
# escribió, pero para convertirlo en un enlace hace falta el `id`. Sin esta
# lista, el Frontend tendría que adivinar qué @algo del texto corresponde a una
# cuenta real -- y se equivocaría justamente en los casos que ADR-023 filtra
# (un @username inexistente, o uno que no autorizó la mención, NO son
# menciones y no deben enlazarse).


def to_public_mention(user):
    return {
        "id": str(user.id),
        "username": user.username,
        "name": user.name,
    }


def to_public_mentions(mentioned_users):
    """`mentioned_users` es una lista de usuarios mencionados, y puede ser None
    (contenido recién creado sin menciones, o un listado que no las resolvió)
    -- devuelve `[]`, nunca None, para que el Frontend no tenga que distinguir
    "sin menciones" de "no vinieron".

    Recibe **usuarios**, no filas de `mentions`: es lo único que el contrato
    expone, y así los dos caminos que llegan acá coinciden -- el de escritura
    (resolve_mentions, que ya tiene los usuarios resueltos para decidir el
    permiso) y el de lectura (MentionRepository.list_for_*, que los devuelve
    directamente). Si el presenter tomara filas `Mention`, el camino de
    escritura tendría que fabricarlas solo para presentarlas."""
    return [to_public_mention(user) for user in (mentioned_users or [])]
