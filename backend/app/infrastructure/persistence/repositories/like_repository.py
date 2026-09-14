# Adaptador SQLAlchemy del puerto `LikeRepository` (domain/likes/repositories.py).
# Único punto del backend que traduce entre `likes` (PostgreSQL) y el resto
# de las capas -- domain/ y application/ no importan SQLAlchemy directamente
# (BACKEND_ARCHITECTURE.md §17), mismo patrón que post_repository.py.

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from app.domain.likes.repositories import LikeRepository
from app.extensions import db
from app.infrastructure.persistence.models import Like


class SQLAlchemyLikeRepository(LikeRepository):
    def add(self, post_id, user_id):
        like = Like(post_id=post_id, user_id=user_id)
        db.session.add(like)
        try:
            db.session.commit()
        except IntegrityError:
            # UNIQUE (post_id, user_id) -- ya existía el like de este
            # usuario sobre este post; idempotente por diseño (ADR-005
            # §Decisión, Opción A), no se re-lanza como error.
            db.session.rollback()
            return False
        return True

    def remove(self, post_id, user_id):
        db.session.execute(
            delete(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        )
        db.session.commit()

    def count_for_post(self, post_id):
        return db.session.execute(
            select(func.count()).select_from(Like).where(Like.post_id == post_id)
        ).scalar_one()

    def counts_for_posts(self, post_ids):
        if not post_ids:
            return {}
        rows = db.session.execute(
            select(Like.post_id, func.count())
            .where(Like.post_id.in_(post_ids))
            .group_by(Like.post_id)
        ).all()
        return {post_id: count for post_id, count in rows}

    def liked_post_ids(self, user_id, post_ids):
        if not post_ids:
            return set()
        rows = (
            db.session.execute(
                select(Like.post_id).where(
                    Like.user_id == user_id, Like.post_id.in_(post_ids)
                )
            )
            .scalars()
            .all()
        )
        return set(rows)
