# Temas silenciados (ADR-026-content-preferences.md). Función pura -- sin
# Flask, sin SQLAlchemy (BACKEND_ARCHITECTURE.md §7/§17).
#
# Un «tema» es un hashtag. Se reconoce dentro del texto de la publicación; el
# producto no guarda etiquetas como entidad.

import re

MAX_TOPIC_LENGTH = 50

MAX_TOPICS_PER_USER = 50

# Letras (con acentos), dígitos y guion bajo: lo que forma un hashtag. `\w` de
# Python es Unicode, así que `#música` es válido.
_TOPIC_PATTERN = re.compile(r"^\w+$")


def normalize_topic(value):
    """Forma canónica de un tema: sin `#`, sin espacios y en minúsculas.

    Devuelve `None` si no es un tema usable (no es texto, queda vacío, excede el
    límite, o contiene algo que no puede formar parte de un hashtag, como
    espacios o signos). Quien llama lo traduce a un 400.

    Acepta con o sin `#` -- una persona escribe `#viajes` o `viajes` y quiere lo
    mismo. No se quitan acentos: `música` y `musica` son etiquetas distintas.
    """
    if not isinstance(value, str):
        return None
    trimmed = value.strip().lstrip("#").lower()
    if not trimmed or len(trimmed) > MAX_TOPIC_LENGTH:
        return None
    if not _TOPIC_PATTERN.match(trimmed):
        return None
    return trimmed
