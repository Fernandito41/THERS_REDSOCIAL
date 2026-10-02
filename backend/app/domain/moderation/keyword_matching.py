# Normalización y comparación de términos filtrados
# (ADR-024-content-filters-and-privacy-preferences.md). Solo tipos nativos de
# Python -- domain/ no importa Flask ni SQLAlchemy (BACKEND_ARCHITECTURE.md
# §7/§17), mismo patrón que domain/posts/validators.py.
#
# Esta es la única definición de "normalizado" en el backend. La usan tanto el
# camino de escritura (guardar un keyword) como el de lectura (buscarlo en un
# texto, en SQL con ILIKE). Si las dos no coincidieran, alguien podría guardar
# un término que después nunca se encuentra.

#: Límite de longitud de un keyword. Placeholder de producto explícito y
#: revisable, mismo criterio que MAX_CONTENT_LENGTH en
#: domain/posts/validators.py. La columna admite 100 para dar margen.
MAX_KEYWORD_LENGTH = 60

#: Cuántos términos puede tener una persona. Sin este límite, una lista de
#: miles de keywords haría que cada lectura del feed evaluara miles de ILIKE
#: (ADR-024 §Riesgos).
MAX_KEYWORDS_PER_USER = 100


def normalize_keyword(value):
    """Forma canónica de un término: sin espacios alrededor y en minúsculas.

    Devuelve `None` si el valor no es un término usable (no es texto, queda
    vacío tras el trim, o excede el límite) -- quien llama traduce ese `None`
    a un 400, igual que `is_valid_content` devuelve False.

    No se quitan acentos ni se normaliza Unicode: "mañana" y "manana" son
    términos distintos a propósito. Hacerlo equivalentes es una decisión de
    producto que nadie tomó todavía (ADR-024 §Decisiones pendientes).
    """
    if not isinstance(value, str):
        return None
    trimmed = value.strip().lower()
    if not trimmed or len(trimmed) > MAX_KEYWORD_LENGTH:
        return None
    return trimmed


def text_matches_any(text, keywords):
    """True si alguno de los `keywords` (ya normalizados) aparece en `text`.

    Coincidencia por **subcadena**, no por palabra completa: filtrar "spoiler"
    también oculta "spoilers". El efecto colateral conocido es que un término
    corto puede coincidir dentro de otra palabra (ADR-024 §Riesgos).

    Es el equivalente en Python del `ILIKE '%' || keyword || '%'` que usan las
    consultas; existe para los caminos que ya tienen el texto en memoria y no
    necesitan volver a SQL.
    """
    if not keywords:
        return False
    haystack = (text or "").lower()
    return any(keyword in haystack for keyword in keywords)
