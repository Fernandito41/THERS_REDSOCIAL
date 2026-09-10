# Adaptador SQLAlchemy del puerto `CommentRepository` (domain/comments/repositories.py).
# Único punto del backend que traduce entre `comments` (PostgreSQL) y el
# resto de las capas -- domain/ y application/ no importan SQLAlchemy
# directamente (BACKEND_ARCHITECTURE.md §17), mismo patrón que
# post_repository.py/like_repository.py.

from sqlalchemy import func, select

from app.domain.comments.repositories import CommentRepository
from app.extensions import db
from app.infrastructure.persistence.models import Comment


class SQLAlchemyCommentRepository(CommentRepository):
    def create(self, post_id, author_id, content):
        comment = Comment(post_id=post_id, author_id=author_id, content=content)
        db.session.add(comment)
        db.session.commit()
        # Refresh para traer created_at/id ya generados por PostgreSQL, y
        # accede a `comment.author` para forzar la resolución del autor
        # antes de que la sesión se cierre (mismo motivo que
        # SQLAlchemyPostRepository.create).
        db.session.refresh(comment)
        _ = comment.author
        return comment

    def list_for_post(self, post_id, limit):
        return (
            db.session.execute(
                select(Comment)
                .where(Comment.post_id == post_id)
                .order_by(Comment.created_at.asc())
                .limit(limit)
            )
            .scalars()
            .all()
        )

    def counts_for_posts(self, post_ids):
        if not post_ids:
            return {}
        rows = db.session.execute(
            select(Comment.post_id, func.count())
            .where(Comment.post_id.in_(post_ids))
            .group_by(Comment.post_id)
        ).all()
        return {post_id: count for post_id, count in rows}
