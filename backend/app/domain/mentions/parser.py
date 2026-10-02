# Extracción de @username del texto de una publicación o comentario
# (ADR-019-mentions.md). Función pura sobre strings -- domain/ no importa
# Flask ni SQLAlchemy (BACKEND_ARCHITECTURE.md §7/§17), mismo patrón que
# domain/posts/validators.py.
#
# Solo *extrae candidatos*: no sabe si esos usernames existen ni si quien los
# escribió tiene permiso para mencionarlos. Eso lo resuelve
# application/mentions/resolve_mentions.py, que es el único que habla con
# repositorios.

import re

#: El patrón de username tiene que coincidir con `is_valid_username`
#: (domain/auth/validators.py): 3–20 caracteres alfanuméricos o guion bajo.
#: Si aquel cambia, este tiene que cambiar con él -- si no, se podrían
#: mencionar usernames que el registro no permite crear, o al revés.
#:
#: `(?<![A-Za-z0-9_@])` evita falsos positivos en dos casos reales: una
#: dirección de correo (`ada@example.com` no menciona a nadie) y un @ pegado
#: a texto previo. `\b` al final corta el username antes de la puntuación, así
#: que "¿viste, @ada?" sí menciona a `ada`.
_MENTION_PATTERN = re.compile(r"(?<![A-Za-z0-9_@])@([A-Za-z0-9_]{3,20})\b")

#: Cuántas menciones se aceptan por publicación/comentario. Sin un límite, un
#: solo post podría generar cientos de notificaciones -- es el vector de spam
#: obvio de esta función (ADR-019 §Riesgos). Placeholder explícito y revisable,
#: mismo criterio que MAX_CONTENT_LENGTH.
MAX_MENTIONS_PER_CONTENT = 10


def extract_usernames(content):
    """Usernames mencionados en `content`, en minúsculas, sin repetir y en el
    orden en que aparecen.

    Se normaliza a minúsculas porque es la forma en que se comparan contra
    `users.username` (que es *case-sensitive* en el esquema, ADR-002 §3, pero
    cuya búsqueda para mencionar se hace sin distinguir mayúsculas: escribir
    "@Ada" debe mencionar a `ada`, que es lo que cualquiera espera al teclear).

    Trunca a `MAX_MENTIONS_PER_CONTENT`: las menciones de más se ignoran en
    silencio, no hacen fallar la publicación -- nadie debería perder lo que
    escribió por haber etiquetado a demasiada gente.
    """
    if not isinstance(content, str):
        return []

    seen = []
    for match in _MENTION_PATTERN.finditer(content):
        username = match.group(1).lower()
        if username not in seen:
            seen.append(username)
        if len(seen) == MAX_MENTIONS_PER_CONTENT:
            break
    return seen
