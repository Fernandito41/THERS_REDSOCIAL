# Adaptador SQLAlchemy del puerto `FollowRepository` (domain/follows/repositories.py).
# Único punto del backend que traduce entre `follows` (PostgreSQL) y el
# resto de las capas -- domain/ y application/ no importan SQLAlchemy
# directamente (BACKEND_ARCHITECTURE.md §17), mismo patrón que
# like_repository.py/comment_repository.py.

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from app.domain.follows.repositories import FollowRepository
from app.extensions import db
from app.infrastructure.persistence.models import Follow


class SQLAlchemyFollowRepository(FollowRepository):
    def add(self, follower_id, followed_id):
        follow = Follow(follower_id=follower_id, followed_id=followed_id)
        db.session.add(follow)
        try:
            db.session.commit()
        except IntegrityError:
            # UNIQUE (follower_id, followed_id) -- ya existía el follow;
            # idempotente por diseño (ADR-007 §Decisión).
            db.session.rollback()
            return False
        return True

    def remove(self, follower_id, followed_id):
        db.session.execute(
            delete(Follow).where(
                Follow.follower_id == follower_id, Follow.followed_id == followed_id
            )
        )
        db.session.commit()

    def is_following(self, follower_id, followed_id):
        return (
            db.session.execute(
                select(Follow.id).where(
                    Follow.follower_id == follower_id,
                    Follow.followed_id == followed_id,
                )
            ).first()
            is not None
        )

    def followers_count(self, user_id):
        return db.session.execute(
            select(func.count()).select_from(Follow).where(Follow.followed_id == user_id)
        ).scalar_one()

    def following_count(self, user_id):
        return db.session.execute(
            select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
        ).scalar_one()

    def followed_user_ids(self, follower_id, candidate_ids):
        if not candidate_ids:
            return set()
        rows = (
            db.session.execute(
                select(Follow.followed_id).where(
                    Follow.follower_id == follower_id,
                    Follow.followed_id.in_(candidate_ids),
                )
            )
            .scalars()
            .all()
        )
        return set(rows)
