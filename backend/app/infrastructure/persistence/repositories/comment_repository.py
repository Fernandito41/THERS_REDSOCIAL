# Adaptador SQLAlchemy del puerto `CommentRepository` (domain/comments/repositories.py).
# Único punto del backend que traduce entre `comments` (PostgreSQL) y el
# resto de las capas -- domain/ y application/ no importan SQLAlchemy
# directamente (BACKEND_ARCHITECTURE.md §17), mismo patrón que
# post_repository.py/like_repository.py.

from sqlalchemy import and_, delete as sa_delete, func, not_, or_, select, update

from app.domain.comments.repositories import CommentRepository
from app.domain.moderation.offensive_words import OFFENSIVE_WORDS
from app.domain.restrictions.kinds import BLOCK, RESTRICT
from app.extensions import db
from app.infrastructure.persistence.models import Comment, Post, User, UserRestriction


def _contains_any(column, terms):
    """`column ILIKE '%term%'` para cualquiera de `terms`. Devuelve None si no
    hay términos -- quien llama interpreta None como "no filtra nada", que no
    es lo mismo que `false`."""
    if not terms:
        return None
    # ilike() escapa el valor como parámetro; los `%` se concatenan en el
    # patrón, así que un término con comodines dentro se busca literalmente.
    return or_(*[column.ilike(f"%{term}%") for term in terms])


def _visible_comment_predicate(viewer_id, muted_keywords):
    """Condición SQL de "este comentario se le muestra a `viewer_id`"
    (ADR-020-content-filters-and-privacy-preferences.md).

    (Desde ADR-025 la condición nunca es None: los bloqueos y restricciones
    siempre aplican, tenga o no términos filtrados.)

    ESTA ES LA ÚNICA DEFINICIÓN del filtro, y la comparten `list_for_post` y
    `counts_for_posts` a propósito: si cada una tuviera la suya, el contador de
    la tarjeta diría 5 y el panel mostraría 3.

    Dos filtros de origen distinto se combinan acá:

      · `muted_keywords` -- términos del ESPECTADOR, se aplican a cualquier
        hilo que lea ("en cualquier hilo", REF-SET-02).
      · lista de ofensivos del sistema -- se aplica solo si el DUEÑO DE LA
        PUBLICACIÓN activó `hide_offensive_comments` ("en tus cápsulas",
        REF-SET-02). Por eso hace falta el JOIN a `posts`/`users`: el flag que
        decide no es del espectador.

    Y una exención que vale para los dos: **a nadie se le oculta su propio
    comentario**. Si no, alguien escribiría un comentario, lo vería
    desaparecer y lo volvería a escribir pensando que falló (ADR-020
    §Decisión).
    """
    # Bloqueos y restricciones (ADR-025-blocked-and-restricted-accounts.md),
    # siempre presentes -- a diferencia de los filtros de contenido de abajo,
    # no dependen de preferencias opcionales.
    #
    #   · Bloqueo en cualquier sentido entre el espectador y quien comentó:
    #     el comentario no se ve. Esto cubre tanto a quien bloqueó como a quien
    #     fue bloqueado.
    #   · Restricción: si el DUEÑO DE LA PUBLICACIÓN restringió a quien
    #     comentó, el comentario queda oculto para todos salvo para su autor
    #     ("sus comentarios quedan ocultos para los demás", REF-SET-10) y para
    #     el propio dueño de la publicación, que es quien restringió y tiene que
    #     poder ver y moderar lo que escribe esa persona.
    blocked_either_way = (
        select(UserRestriction.id)
        .where(
            UserRestriction.kind == BLOCK,
            or_(
                and_(
                    UserRestriction.owner_id == viewer_id,
                    UserRestriction.target_id == Comment.author_id,
                ),
                and_(
                    UserRestriction.owner_id == Comment.author_id,
                    UserRestriction.target_id == viewer_id,
                ),
            ),
        )
        .exists()
    )
    post_owner_restricted_commenter = (
        select(UserRestriction.id)
        .join(Post, Post.author_id == UserRestriction.owner_id)
        .where(
            Post.id == Comment.post_id,
            UserRestriction.kind == RESTRICT,
            UserRestriction.target_id == Comment.author_id,
        )
        .exists()
    )
    viewer_owns_post = (
        select(Post.id)
        .where(Post.id == Comment.post_id, Post.author_id == viewer_id)
        .exists()
    )
    relationship_filters = and_(
        not_(blocked_either_way),
        or_(
            not_(post_owner_restricted_commenter),
            Comment.author_id == viewer_id,
            viewer_owns_post,
        ),
    )

    muted_match = _contains_any(Comment.content, muted_keywords)
    offensive_match = _contains_any(Comment.content, OFFENSIVE_WORDS)

    hidden_clauses = []
    if muted_match is not None:
        hidden_clauses.append(muted_match)
    if offensive_match is not None:
        # Correlacionado con el autor de la publicación, no con el espectador.
        author_hides_offensive = (
            select(User.id)
            .join(Post, Post.author_id == User.id)
            .where(Post.id == Comment.post_id, User.hide_offensive_comments.is_(True))
            .exists()
        )
        hidden_clauses.append(and_(author_hides_offensive, offensive_match))

    if not hidden_clauses:
        return relationship_filters

    return and_(
        relationship_filters,
        or_(Comment.author_id == viewer_id, not_(or_(*hidden_clauses))),
    )


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

    def list_for_post(self, post_id, limit, viewer_id, muted_keywords=()):
        conditions = [Comment.post_id == post_id]
        visible = _visible_comment_predicate(viewer_id, muted_keywords)
        if visible is not None:
            conditions.append(visible)

        return (
            db.session.execute(
                select(Comment)
                .where(*conditions)
                .order_by(Comment.created_at.asc())
                .limit(limit)
            )
            .scalars()
            .all()
        )

    def counts_for_posts(self, post_ids, viewer_id, muted_keywords=()):
        if not post_ids:
            return {}

        # Mismo predicado que list_for_post: `comments_count` cuenta exactamente
        # lo que el panel va a mostrar a esta persona. Un contador que no
        # coincide con la lista es un bug visible, no una optimización
        # (ADR-020 §Decisión).
        conditions = [Comment.post_id.in_(post_ids)]
        visible = _visible_comment_predicate(viewer_id, muted_keywords)
        if visible is not None:
            conditions.append(visible)

        rows = db.session.execute(
            select(Comment.post_id, func.count())
            .where(*conditions)
            .group_by(Comment.post_id)
        ).all()
        return {post_id: count for post_id, count in rows}

    def delete(self, comment_id, author_id):
        # `author_id` en el propio WHERE, no un chequeo aparte después de
        # leer la fila -- confirma existencia y pertenencia en la misma
        # sentencia (mismo principio que SQLAlchemyPostRepository.delete,
        # ADR-015). `comments` no tiene tablas dependientes: no hay cascada
        # que considerar (ADR-006 §No objetivos: sin hilos de respuestas).
        result = db.session.execute(
            sa_delete(Comment).where(Comment.id == comment_id, Comment.author_id == author_id)
        )
        db.session.commit()
        return result.rowcount > 0

    def update_content(self, comment_id, author_id, content):
        # Mismo criterio que SQLAlchemyPostRepository.update_content
        # (ADR-017-content-editing.md): WHERE con author_id, `edited_at`
        # generado por PostgreSQL, y relectura de la fila para devolverla ya
        # actualizada con su autor resuelto.
        result = db.session.execute(
            update(Comment)
            .where(Comment.id == comment_id, Comment.author_id == author_id)
            .values(content=content, edited_at=func.now())
        )
        db.session.commit()
        if result.rowcount == 0:
            return None

        comment = db.session.get(Comment, comment_id)
        _ = comment.author
        return comment
