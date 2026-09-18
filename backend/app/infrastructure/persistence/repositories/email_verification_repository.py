# Adaptador SQLAlchemy del puerto `EmailVerificationTokenRepository`
# (domain/auth/email_verification_repository.py). Mismo patrón que
# password_reset_repository.py (ADR-011-mandatory-email-verification.md,
# reemplaza el flujo de enlace de ADR-009-password-reset-and-email-verification.md)
# -- incluido el reintento ante la condición de carrera de dos "Reenviar
# código" simultáneos, ver `create_code`.

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from app.domain.auth.email_verification_repository import EmailVerificationTokenRepository
from app.extensions import db
from app.infrastructure.persistence.models import EmailVerificationToken

# Mismo criterio que SQLAlchemyPasswordResetTokenRepository (ADR-010
# §Riesgos): tres reintentos alcanzan sobradamente para el nivel de
# concurrencia real de este endpoint.
_MAX_CREATE_RETRIES = 3


class SQLAlchemyEmailVerificationTokenRepository(EmailVerificationTokenRepository):
    def create_code(self, user_id, code_hash, expires_at):
        for attempt in range(_MAX_CREATE_RETRIES):
            db.session.execute(
                update(EmailVerificationToken)
                .where(
                    EmailVerificationToken.user_id == user_id,
                    EmailVerificationToken.used_at.is_(None),
                )
                .values(used_at=func.now())
            )
            token = EmailVerificationToken(
                user_id=user_id, code_hash=code_hash, expires_at=expires_at
            )
            db.session.add(token)
            try:
                db.session.commit()
            except IntegrityError:
                # uq_email_verification_tokens_active_user -- otra request
                # concurrente ya insertó su propia fila activa entre el
                # UPDATE y este commit. Se reintenta desde el principio.
                db.session.rollback()
                if attempt == _MAX_CREATE_RETRIES - 1:
                    raise
                continue
            return token

    def find_active_by_user_id(self, user_id):
        return db.session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used_at.is_(None),
            )
        ).scalar_one_or_none()

    def increment_attempts(self, token_id):
        result = db.session.execute(
            update(EmailVerificationToken)
            .where(EmailVerificationToken.id == token_id)
            .values(attempts=EmailVerificationToken.attempts + 1)
            .returning(EmailVerificationToken.attempts)
        )
        db.session.commit()
        return result.scalar_one()

    def mark_used(self, token_id):
        db.session.execute(
            update(EmailVerificationToken)
            .where(EmailVerificationToken.id == token_id)
            .values(used_at=func.now())
        )
        db.session.commit()

    def has_recent_unused_code(self, user_id, cooldown_seconds):
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
