# Casos de uso de temas silenciados (GET/POST/DELETE /api/users/me/muted-topics,
# ADR-026-content-preferences.md). Mismo patrón que muted_keywords_use_case.py:
# cada respuesta devuelve la lista completa, así la pantalla nunca tiene que
# reconstruirla ni volver a pedirla.

from app.domain.moderation.topic_exceptions import (
    MutedTopicNotFoundError,
    TopicLimitReachedError,
)
from app.domain.moderation.topic_matching import MAX_TOPICS_PER_USER


def list_muted_topics(user_id, muted_topic_repository):
    return {"muted_topics": list(muted_topic_repository.list_for_user(user_id))}


def add_muted_topic(user_id, topic, muted_topic_repository):
    # El límite solo cuenta si el tema es nuevo: repetir uno que ya tenía es
    # idempotente y nunca debe chocar con el tope.
    existing = muted_topic_repository.list_for_user(user_id)
    if topic not in existing and len(existing) >= MAX_TOPICS_PER_USER:
        raise TopicLimitReachedError()

    muted_topic_repository.add(user_id, topic)
    return {"muted_topics": list(muted_topic_repository.list_for_user(user_id))}


def remove_muted_topic(user_id, topic, muted_topic_repository):
    if not muted_topic_repository.remove(user_id, topic):
        raise MutedTopicNotFoundError()

    return {"muted_topics": list(muted_topic_repository.list_for_user(user_id))}
