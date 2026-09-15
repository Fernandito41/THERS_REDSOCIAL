# Adaptador SQLAlchemy del puerto `EmailVerificationTokenRepository`
# (domain/auth/email_verification_repository.py). Mismo patrón que
# password_reset_repository.py -- sin `invalidate_all_for_user`: a
# diferencia de un reset de contraseña, verificar el email no vuelve
# inválidos otros tokens de verificación pendientes (no hay ningún otro
# efecto colateral de seguridad que proteger al consumir uno).

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update

from app.domain.auth.email_verification_repository import EmailVerificationTokenRepository
from app.extensions import db
from app.infrastructure.persistence.models import EmailVerificationToken


class SQLAlchemyEmailVerificationTokenRepository(EmailVerificationTokenRepository):
    def create(self, user_id, token_hash, expires_at):
        token = EmailVerificationToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        db.session.add(token)
        db.session.commit()
        return token

    def find_valid_by_hash(self, token_hash):
        now = datetime.now(timezone.utc)
        return db.session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_hash,
                EmailVerificationToken.used_at.is_(None),
                EmailVerificationToken.expires_at > now,
            )
        ).scalar_one_or_none()

    def mark_used(self, token_id):
        db.session.execute(
            update(EmailVerificationToken)
            .where(EmailVerificationToken.id == token_id)
            .values(used_at=db.func.now())
        )
        db.session.commit()

    def has_recent_unused_token(self, user_id, cooldown_seconds):
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=cooldown_seconds)
        return (
            db.session.execute(
                select(EmailVerificationToken.id).where(
                    EmailVerificationToken.user_id == user_id,
                    EmailVerificationToken.used_at.is_(None),
                    EmailVerificationToken.created_at > cutoff,
                )
            ).first()
            is not None
        )
