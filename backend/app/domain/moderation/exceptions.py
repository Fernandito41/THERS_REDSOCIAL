# Excepciones de dominio para los filtros de contenido
# (ADR-024-content-filters-and-privacy-preferences.md).


class MutedKeywordNotFoundError(Exception):
    """El usuario autenticado no tiene ese término filtrado -- porque nunca lo
    agregó o porque ya lo quitó. La route lo traduce a 404. No distingue "no
    existe" de "es de otra persona" porque no puede: el `user_id` del WHERE
    sale del JWT, así que un término ajeno es, desde acá, indistinguible de uno
    inexistente (mismo criterio que el resto de recursos propios,
    ADR-019/ADR-020/ADR-021)."""


class KeywordLimitReachedError(Exception):
    """Se alcanzó MAX_KEYWORDS_PER_USER. Existe un tope porque cada término se
    evalúa como un ILIKE en las consultas de lectura: una lista sin límite
    degradaría el feed de quien la tenga (ADR-024 §Riesgos). La route lo
    traduce a 409 -- el pedido es válido pero choca con el estado actual del
    recurso, mismo criterio que UsernameAlreadyExistsError (ADR-003)."""
