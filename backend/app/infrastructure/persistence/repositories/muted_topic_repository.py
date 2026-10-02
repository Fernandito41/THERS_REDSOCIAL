# Adaptador SQLAlchemy del puerto `MutedTopicRepository`
# (domain/moderation/topic_repositories.py), ADR-026-content-preferences.md.

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.domain.moderation.topic_repositories import MutedTopicRepository
from app.extensions import db
from app.infrastructure.persistence.models import MutedTopic


class SQLAlchemyMutedTopicRepository(MutedTopicRepository):
    def list_for_user(self, user_id):
        return (
            db.session.execute(
                select(MutedTopic.topic)
                .where(MutedTopic.user_id == user_id)
                .order_by(MutedTopic.created_at.desc())
            )
            .scalars()
            .all()
        )

    def add(self, user_id, topic):
        db.session.add(MutedTopic(user_id=user_id, topic=topic))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return False
        return True

    def remove(self, user_id, topic):
        result = db.session.execute(
            delete(MutedTopic).where(
                MutedTopic.user_id == user_id, MutedTopic.topic == topic
            )
        )
        db.session.commit()
        return result.rowcount > 0
