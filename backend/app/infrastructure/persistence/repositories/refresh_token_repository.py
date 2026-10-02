# Implementación SQLAlchemy del puerto `RefreshTokenRepository`
# (domain/auth/refresh_token_repository.py, ADR-017-jwt-session-policy.md).
# Único lugar que conoce la tabla `refresh_tokens`.

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update

from app.domain.auth.refresh_token_repository import (
    RefreshTokenRepository,
    RotationResult,
    RotationStatus,
)
from app.extensions import db
from app.infrastructure.persistence.models import RefreshToken


class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def create(self, user_id, family_id, token_hash, expires_at):
        row = RefreshToken(
            user_id=user_id,
            family_id=family_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db.session.add(row)
        db.session.commit()
        return row

    def rotate(self, token_hash, new_token_hash, new_expires_at):
        try:
            # `FOR UPDATE`: una segunda rotación simultánea del MISMO token
            # espera aquí hasta que la primera confirme, y entonces lo ve ya
            # consumido (-> REUSED). Así nunca se emiten dos sucesores
            # (ADR-017 §4.3); el índice único parcial es la defensa de última
            # línea, no la primera.
            row = db.session.execute(
                select(RefreshToken)
                .where(RefreshToken.token_hash == token_hash)
                .with_for_update()
            ).scalar_one_or_none()

            if row is None:
                db.session.rollback()
                return RotationResult(RotationStatus.INVALID)

            now = datetime.now(timezone.utc)

            if row.revoked_at is not None or row.expires_at <= now:
                db.session.rollback()
                return RotationResult(RotationStatus.INVALID)

            if row.used_at is not None:
                # Reuso de un token ya consumido: robo probable. Se corta la
                # familia entera (ADR-017 §2, "Detección de reuso").
                db.session.execute(
                    update(RefreshToken)
                    .where(
                        RefreshToken.family_id == row.family_id,
                        RefreshToken.revoked_at.is_(None),
                    )
                    .values(revoked_at=func.now())
                )
                db.session.commit()
                return RotationResult(RotationStatus.REUSED)

            user_id, family_id = row.user_id, row.family_id
            successor_id = uuid.uuid4()

            # Orden importa: primero se marca consumido el actual, así el
            # índice único parcial no ve dos activos en la misma familia.
            row.used_at = func.now()
            row.replaced_by_id = successor_id
            db.session.flush()

            db.session.add(
                RefreshToken(
                    id=successor_id,
                    user_id=user_id,
                    family_id=family_id,
                    token_hash=new_token_hash,
                    expires_at=new_expires_at,
                )
            )
            db.session.commit()
            return RotationResult(RotationStatus.OK, user_id=user_id, family_id=family_id)
        except Exception:
            db.session.rollback()
            raise

    def revoke_family_of(self, token_hash):
        family_id = db.session.execute(
            select(RefreshToken.family_id).where(RefreshToken.token_hash == token_hash)
        ).scalar_one_or_none()

        if family_id is None:
            return False

        db.session.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=func.now())
        )
        db.session.commit()
        return True

    def revoke_all_for_user(self, user_id):
        db.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=func.now())
        )
        db.session.commit()
