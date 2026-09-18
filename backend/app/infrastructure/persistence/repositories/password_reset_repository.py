# Adaptador SQLAlchemy del puerto `PasswordResetTokenRepository`
# (domain/auth/password_reset_repository.py). Único punto del backend que
# traduce entre `password_reset_tokens` (PostgreSQL) y el resto de las capas
# -- domain/ y application/ no importan SQLAlchemy directamente
# (BACKEND_ARCHITECTURE.md §17). Reescrito en
# ADR-010-password-reset-otp-flow.md para el flujo OTP.

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from app.domain.auth.password_reset_repository import PasswordResetTokenRepository
from app.extensions import db
from app.infrastructure.persistence.models import PasswordResetToken

# Reintentos ante la condición de carrera de dos "Reenviar código"
# simultáneos (ADR-010 §Riesgos): cada intento invalida las solicitudes
# activas que YA ve (posiblemente ninguna todavía) e inserta una nueva; si
# otra transacción concurrente insertó su propia fila activa justo antes del
# commit, la UNIQUE parcial (uq_password_reset_tokens_active_user) rechaza
# el INSERT con IntegrityError -- reintentar desde el principio, en una
# transacción nueva, ya ve esa fila recién comprometida y la invalida antes
# de insertar la propia. Tres intentos alcanzan sobradamente para el nivel
# de concurrencia real de este endpoint (un usuario pidiendo su propio
# reset, no un recurso de alto tráfico).
_MAX_CREATE_RETRIES = 3


class SQLAlchemyPasswordResetTokenRepository(PasswordResetTokenRepository):
    def create_code(self, user_id, code_hash, expires_at):
        for attempt in range(_MAX_CREATE_RETRIES):
            db.session.execute(
                update(PasswordResetToken)
                .where(
                    PasswordResetToken.user_id == user_id,
                    PasswordResetToken.used_at.is_(None),
                )
                .values(used_at=func.now())
            )
            token = PasswordResetToken(user_id=user_id, code_hash=code_hash, expires_at=expires_at)
            db.session.add(token)
            try:
                db.session.commit()
            except IntegrityError:
                # uq_password_reset_tokens_active_user -- otra request
                # concurrente ya insertó su propia fila activa entre el
                # UPDATE y este commit. Se reintenta desde el principio.
                db.session.rollback()
                if attempt == _MAX_CREATE_RETRIES - 1:
                    raise
                continue
            return token

    def find_active_by_user_id(self, user_id):
        return db.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used_at.is_(None),
            )
        ).scalar_one_or_none()

    def increment_attempts(self, token_id):
        result = db.session.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(attempts=PasswordResetToken.attempts + 1)
            .returning(PasswordResetToken.attempts)
        )
        db.session.commit()
        return result.scalar_one()

    def mark_verified(self, token_id, reset_authorization_hash, reset_authorization_expires_at):
        db.session.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(
                verified_at=func.now(),
                reset_authorization_hash=reset_authorization_hash,
                reset_authorization_expires_at=reset_authorization_expires_at,
            )
        )
        db.session.commit()

    def find_valid_by_reset_authorization_hash(self, reset_authorization_hash):
        now = datetime.now(timezone.utc)
        return db.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.reset_authorization_hash == reset_authorization_hash,
                PasswordResetToken.verified_at.is_not(None),
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.reset_authorization_expires_at > now,
            )
        ).scalar_one_or_none()

    def mark_used(self, token_id):
        db.session.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(used_at=func.now())
        )
        db.session.commit()

    def has_recent_unused_code(self, user_id, cooldown_seconds):
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
