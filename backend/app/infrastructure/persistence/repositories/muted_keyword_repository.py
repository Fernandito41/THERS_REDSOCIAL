# Adaptador SQLAlchemy del puerto `MutedKeywordRepository`
# (domain/moderation/repositories.py). Único punto del backend que traduce
# entre `muted_keywords` (PostgreSQL) y el resto de las capas -- domain/ y
# application/ no importan SQLAlchemy directamente (BACKEND_ARCHITECTURE.md
# §17), mismo patrón que follow_repository.py.

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from app.domain.moderation.repositories import MutedKeywordRepository
from app.extensions import db
from app.infrastructure.persistence.models import MutedKeyword


class SQLAlchemyMutedKeywordRepository(MutedKeywordRepository):
    def list_for_user(self, user_id):
        return (
            db.session.execute(
                select(MutedKeyword.keyword)
                .where(MutedKeyword.user_id == user_id)
                .order_by(MutedKeyword.created_at.desc())
            )
            .scalars()
            .all()
        )

    def count_for_user(self, user_id):
        return db.session.execute(
            select(func.count())
            .select_from(MutedKeyword)
            .where(MutedKeyword.user_id == user_id)
        ).scalar_one()

    def add(self, user_id, keyword):
        db.session.add(MutedKeyword(user_id=user_id, keyword=keyword))
        try:
            db.session.commit()
        except IntegrityError:
            # UNIQUE (user_id, keyword) -- ya lo tenía; idempotente por diseño,
            # mismo criterio que FollowRepository.add (ADR-007).
            db.session.rollback()
            return False
        return True

    def remove(self, user_id, keyword):
        # `user_id` en el propio WHERE: nadie puede borrar un término de otra
        # persona, y eso se confirma en la misma sentencia que la existencia
        # (mismo principio que las operaciones sobre contenido propio,
        # ADR-015/ADR-016/ADR-017).
        result = db.session.execute(
            delete(MutedKeyword).where(
                MutedKeyword.user_id == user_id, MutedKeyword.keyword == keyword
            )
        )
        db.session.commit()
        return result.rowcount > 0
