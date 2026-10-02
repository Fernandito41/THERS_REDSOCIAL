# Adaptador SQLAlchemy del puerto `RestrictionRepository`
# (domain/restrictions/repositories.py), ADR-029-blocked-and-restricted-accounts.md.

from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.domain.restrictions.kinds import BLOCK
from app.domain.restrictions.repositories import RestrictionRepository
from app.extensions import db
from app.infrastructure.persistence.models import UserRestriction


class SQLAlchemyRestrictionRepository(RestrictionRepository):
    def set_kind(self, owner_id, target_id, kind):
        # UPSERT en una sola sentencia: dos peticiones simultáneas no pueden
        # dejar el par en un estado intermedio ni chocar con la UNIQUE.
        statement = pg_insert(UserRestriction).values(
            owner_id=owner_id, target_id=target_id, kind=kind
        )
        statement = statement.on_conflict_do_update(
            constraint="uq_user_restrictions_pair", set_={"kind": kind}
        )
        db.session.execute(statement)
        db.session.commit()

    def remove(self, owner_id, target_id, kind):
        row = db.session.execute(
            select(UserRestriction).where(
                UserRestriction.owner_id == owner_id,
                UserRestriction.target_id == target_id,
                UserRestriction.kind == kind,
            )
        ).scalar_one_or_none()
        if row is None:
            return False
        db.session.delete(row)
        db.session.commit()
        return True

    def get_kind(self, owner_id, target_id):
        return db.session.execute(
            select(UserRestriction.kind).where(
                UserRestriction.owner_id == owner_id,
                UserRestriction.target_id == target_id,
            )
        ).scalar_one_or_none()

    def is_blocked_between(self, user_a_id, user_b_id):
        return (
            db.session.execute(
                select(UserRestriction.id).where(
                    UserRestriction.kind == BLOCK,
                    or_(
                        (UserRestriction.owner_id == user_a_id)
                        & (UserRestriction.target_id == user_b_id),
                        (UserRestriction.owner_id == user_b_id)
                        & (UserRestriction.target_id == user_a_id),
                    ),
                )
            ).first()
            is not None
        )

    def blocked_ids_either_way(self, user_id):
        rows = db.session.execute(
            select(UserRestriction.owner_id, UserRestriction.target_id).where(
                UserRestriction.kind == BLOCK,
                or_(
                    UserRestriction.owner_id == user_id,
                    UserRestriction.target_id == user_id,
                ),
            )
        ).all()
        ids = set()
        for owner_id, target_id in rows:
            other = target_id if str(owner_id) == str(user_id) else owner_id
            ids.add(str(other))
        return ids

    def list_for_owner(self, owner_id, kind, limit):
        return (
            db.session.execute(
                select(UserRestriction)
                .where(UserRestriction.owner_id == owner_id, UserRestriction.kind == kind)
                .order_by(UserRestriction.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .unique()
            .all()
        )
