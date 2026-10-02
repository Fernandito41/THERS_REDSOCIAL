class MutedTopicNotFoundError(Exception):
    """El usuario autenticado no tiene ese tema silenciado. La route lo traduce a
    404. No distingue «no existe» de «es de otra persona» porque no puede: el
    `user_id` del WHERE sale del JWT (mismo criterio que MutedKeywordNotFoundError)."""


class TopicLimitReachedError(Exception):
    """Se alcanzó MAX_TOPICS_PER_USER. Cada tema es una condición más en la
    consulta del feed: una lista sin tope degradaría el feed de quien la tenga.
    La route lo traduce a 409."""
