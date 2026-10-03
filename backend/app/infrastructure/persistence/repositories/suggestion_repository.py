# Adaptador SQLAlchemy del puerto `SuggestionRepository`
# (domain/follows/suggestions.py), ADR-030-content-preferences.md.

from sqlalchemy import and_, func, or_, select

from app.domain.follows.follow_status import ACCEPTED
from app.domain.follows.suggestions import SuggestionRepository
from app.domain.restrictions.kinds import BLOCK
from app.extensions import db
from app.infrastructure.persistence.models import Follow, User, UserRestriction


class SQLAlchemySuggestionRepository(SuggestionRepository):
    def list_for_user(self, viewer_id, limit):
        # Cuántos seguidores ACEPTADOS tiene cada candidato. Una solicitud
        # pendiente no suma (mismo criterio que followers_count, ADR-022).
        followers_count = (
            select(func.count())
            .select_from(Follow)
            .where(Follow.followed_id == User.id, Follow.status == ACCEPTED)
            .correlate(User)
            .scalar_subquery()
        )

        # Ya lo sigo, o ya le pedí seguirlo (cualquier estado).
        already_related = (
            select(Follow.id)
            .where(Follow.follower_id == viewer_id, Follow.followed_id == User.id)
            .exists()
        )

        # Bloqueo en cualquier sentido (ADR-029).
        blocked_either_way = (
            select(UserRestriction.id)
            .where(
                UserRestriction.kind == BLOCK,
                or_(
                    and_(
                        UserRestriction.owner_id == viewer_id,
                        UserRestriction.target_id == User.id,
                    ),
                    and_(
                        UserRestriction.owner_id == User.id,
                        UserRestriction.target_id == viewer_id,
                    ),
                ),
            )
            .exists()
        )

        return (
            db.session.execute(
                select(User)
                .where(
                    User.id != viewer_id,
                    ~already_related,
                    ~blocked_either_way,
                    # Las cuentas de moderación no son para seguir ni para descubrir: se usan
                    # solo para moderar (ADR-032). Una cuenta suspendida tampoco se sugiere.
                    User.is_moderator.is_(False),
                    User.suspended_at.is_(None),
                )
                .order_by(followers_count.desc(), User.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
