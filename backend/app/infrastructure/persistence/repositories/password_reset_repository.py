# Adaptador SQLAlchemy del puerto `PasswordResetTokenRepository`
# (domain/auth/password_reset_repository.py). Único punto del backend que
# traduce entre `password_reset_tokens` (PostgreSQL) y el resto de las capas
# -- domain/ y application/ no importan SQLAlchemy directamente
# (BACKEND_ARCHITECTURE.md §17), mismo patrón que el resto de repositorios.

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update

from app.domain.auth.password_reset_repository import PasswordResetTokenRepository
from app.extensions import db
from app.infrastructure.persistence.models import PasswordResetToken


class SQLAlchemyPasswordResetTokenRepository(PasswordResetTokenRepository):
    def create(self, user_id, token_hash, expires_at):
        token = PasswordResetToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        db.session.add(token)
        db.session.commit()
        return token

    def find_valid_by_hash(self, token_hash):
        now = datetime.now(timezone.utc)
        return db.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
        ).scalar_one_or_none()

    def mark_used(self, token_id):
        db.session.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(used_at=func.now())
        )
        db.session.commit()

    def invalidate_all_for_user(self, user_id):
        db.session.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=func.now())
        )
        db.session.commit()

    def has_recent_unused_token(self, user_id, cooldown_seconds):
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=cooldown_seconds)
        return (
            db.session.execute(
                select(PasswordResetToken.id).where(
                    PasswordResetToken.user_id == user_id,
                    PasswordResetToken.used_at.is_(None),
                    PasswordResetToken.created_at > cutoff,
                )
            ).first()
            is not None
        )
