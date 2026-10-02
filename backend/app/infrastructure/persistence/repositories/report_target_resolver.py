# Localiza lo que se está reportando (domain/reports/repositories.py,
# ADR-032-content-reports-and-moderation.md §2).
#
# Un solo lugar que conoce las cuatro tablas posibles (posts, comentarios,
# mensajes y usuarios), para no agregar un `find_by_id` a cada repositorio
# existente. NO decide la visibilidad: eso es del caso de uso, que ya conoce las
# guardias de ADR-022 y ADR-029.

from app.domain.reports import kinds
from app.domain.reports.repositories import ReportTargetResolver, ResolvedTarget
from app.extensions import db
from app.infrastructure.persistence.models import Comment, Message, Post, User


def _profile_text(user):
    """Los campos de texto públicos de un perfil. Es lo que cualquiera ve de esa
    cuenta, no datos privados: sin correo, teléfono ni fecha de nacimiento."""
    parts = [user.username, user.name, user.bio, user.location, user.website]
    return " | ".join(part for part in parts if part)


class SQLAlchemyReportTargetResolver(ReportTargetResolver):
    def resolve(self, target_type, target_id):
        if target_type == kinds.TARGET_POST:
            post = db.session.get(Post, target_id)
            if post is None:
                return None
            return ResolvedTarget(
                target_type=target_type,
                target_id=str(post.id),
                owner_id=str(post.author_id),
                text=post.content or "",
                post=post,
            )

        if target_type == kinds.TARGET_COMMENT:
            comment = db.session.get(Comment, target_id)
            if comment is None:
                return None
            # `Comment` no tiene relación con su post: se busca por `post_id`.
            post = db.session.get(Post, comment.post_id)
            if post is None:
                return None
            return ResolvedTarget(
                target_type=target_type,
                target_id=str(comment.id),
                owner_id=str(comment.author_id),
                text=comment.content or "",
                post=post,
            )

        if target_type == kinds.TARGET_MESSAGE:
            message = db.session.get(Message, target_id)
            if message is None:
                return None
            return ResolvedTarget(
                target_type=target_type,
                target_id=str(message.id),
                owner_id=str(message.sender_id),
                text=message.content or "",
                recipient_id=str(message.recipient_id),
            )

        if target_type == kinds.TARGET_USER:
            user = db.session.get(User, target_id)
            if user is None:
                return None
            return ResolvedTarget(
                target_type=target_type,
                target_id=str(user.id),
                owner_id=str(user.id),
                text=_profile_text(user),
            )

        return None
