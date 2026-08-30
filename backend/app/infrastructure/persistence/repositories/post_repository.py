# Adaptador SQLAlchemy del puerto `PostRepository` (domain/posts/repositories.py).
# Único punto del backend que traduce entre `posts` (PostgreSQL) y el resto
# de las capas -- domain/ y application/ no importan SQLAlchemy directamente
# (BACKEND_ARCHITECTURE.md §17), solo reciben el objeto `Post` ya resuelto.

from sqlalchemy import select

from app.domain.posts.repositories import PostRepository
from app.extensions import db
from app.infrastructure.persistence.models import Post


class SQLAlchemyPostRepository(PostRepository):
    def create(self, author_id, content):
        post = Post(author_id=author_id, content=content)
        db.session.add(post)
        db.session.commit()
        # Refresh para traer created_at/id ya generados por PostgreSQL, y
        # accede a `post.author` para forzar la resolución del autor antes
        # de que la sesión se cierre (evita un DetachedInstanceError si el
        # presenter se llama fuera de este contexto).
        db.session.refresh(post)
        _ = post.author
        return post

    def list_recent(self, limit):
        return (
            db.session.execute(
                select(Post).order_by(Post.created_at.desc()).limit(limit)
            )
            .scalars()
            .all()
        )
