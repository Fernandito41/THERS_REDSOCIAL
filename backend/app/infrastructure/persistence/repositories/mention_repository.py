# Adaptador SQLAlchemy del puerto `MentionRepository`
# (domain/mentions/repositories.py). Único punto del backend que traduce entre
# `mentions` (PostgreSQL) y el resto de las capas -- domain/ y application/ no
# importan SQLAlchemy directamente (BACKEND_ARCHITECTURE.md §17), mismo patrón
# que follow_repository.py/comment_repository.py.

from collections import defaultdict

from sqlalchemy import delete, select

from app.domain.mentions.repositories import MentionRepository
from app.extensions import db
from app.infrastructure.persistence.models import Mention


class SQLAlchemyMentionRepository(MentionRepository):
    def replace_for_post(self, post_id, author_id, mentioned_user_ids):
        return self._replace(Mention.post_id, post_id, "post_id", author_id, mentioned_user_ids)

    def replace_for_comment(self, comment_id, author_id, mentioned_user_ids):
        return self._replace(
            Mention.comment_id, comment_id, "comment_id", author_id, mentioned_user_ids
        )

    def _replace(self, target_column, target_id, target_field, author_id, mentioned_user_ids):
        # Las dos variantes (post/comentario) difieren solo en qué columna es
        # el target, así que comparten implementación en vez de duplicarla --
        # la CHECK ck_mentions_exactly_one_target garantiza que solo una se
        # rellene, y acá se rellena siempre exactamente una.
        wanted = {str(user_id) for user_id in mentioned_user_ids}

        existing_rows = (
            db.session.execute(select(Mention).where(target_column == target_id))
            .scalars()
            .all()
        )
        existing = {str(row.mentioned_user_id) for row in existing_rows}

        to_remove = existing - wanted
        to_add = wanted - existing

        if to_remove:
            db.session.execute(
                delete(Mention).where(
                    target_column == target_id,
                    Mention.mentioned_user_id.in_(to_remove),
                )
            )

        for user_id in to_add:
            db.session.add(
                Mention(
                    mentioned_user_id=user_id,
                    author_id=author_id,
                    **{target_field: target_id},
                )
            )

        db.session.commit()

        # Solo los nuevos: editar un texto sin tocar a quién menciona no debe
        # volver a notificar a nadie (ADR-023 §Decisión).
        return to_add

    def list_for_posts(self, post_ids):
        return self._list_grouped(Mention.post_id, post_ids, lambda m: m.post_id)

    def list_for_comments(self, comment_ids):
        return self._list_grouped(Mention.comment_id, comment_ids, lambda m: m.comment_id)

    def _list_grouped(self, target_column, target_ids, key_of):
        if not target_ids:
            return {}
        # `Mention.mentioned_user` es lazy="joined" (models.py), así que el
        # usuario mencionado viene en esta misma consulta -- sin N+1 al
        # renderizar. Se devuelve el usuario y no la fila: es lo único que el
        # contrato expone (ver el puerto).
        rows = (
            db.session.execute(
                select(Mention)
                .where(target_column.in_(target_ids))
                .order_by(Mention.created_at.asc())
            )
            .scalars()
            .all()
        )
        grouped = defaultdict(list)
        for mention in rows:
            grouped[key_of(mention)].append(mention.mentioned_user)
        return dict(grouped)
