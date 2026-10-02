# Adaptador SQLAlchemy del puerto `TwoFactorRecoveryCodeRepository`
# (domain/auth/repositories.py). Único punto del backend que traduce entre
# `two_factor_recovery_codes` (PostgreSQL) y el resto de las capas
# (BACKEND_ARCHITECTURE.md §17).

from sqlalchemy import delete, func, select, update

from app.domain.auth.repositories import TwoFactorRecoveryCodeRepository
from app.extensions import db
from app.infrastructure.persistence.models import TwoFactorRecoveryCode


class SQLAlchemyTwoFactorRecoveryCodeRepository(TwoFactorRecoveryCodeRepository):
    def replace_all(self, user_id, code_hashes):
        # Regenerar los códigos invalida los anteriores en la misma operación:
        # si no, quedarían dos juegos válidos a la vez y la persona no sabría
        # cuál tiene en el papel (ADR-026 §Decisión).
        db.session.execute(
            delete(TwoFactorRecoveryCode).where(TwoFactorRecoveryCode.user_id == user_id)
        )
        for code_hash in code_hashes:
            db.session.add(TwoFactorRecoveryCode(user_id=user_id, code_hash=code_hash))
        db.session.commit()

    def delete_all(self, user_id):
        db.session.execute(
            delete(TwoFactorRecoveryCode).where(TwoFactorRecoveryCode.user_id == user_id)
        )
        db.session.commit()

    def list_unused(self, user_id):
        return (
            db.session.execute(
                select(TwoFactorRecoveryCode).where(
                    TwoFactorRecoveryCode.user_id == user_id,
                    TwoFactorRecoveryCode.used_at.is_(None),
                )
            )
            .scalars()
            .all()
        )

    def count_unused(self, user_id):
        return db.session.execute(
            select(func.count())
            .select_from(TwoFactorRecoveryCode)
            .where(
                TwoFactorRecoveryCode.user_id == user_id,
                TwoFactorRecoveryCode.used_at.is_(None),
            )
        ).scalar_one()

    def mark_used(self, code_id):
        # `used_at IS NULL` en el propio WHERE: dos peticiones simultáneas con
        # el mismo código no pueden consumirlo las dos -- la segunda no
        # matchea y devuelve False. Es lo que hace que "un solo uso" sea cierto
        # también bajo concurrencia (ADR-026 §Seguridad).
        result = db.session.execute(
            update(TwoFactorRecoveryCode)
            .where(
                TwoFactorRecoveryCode.id == code_id,
                TwoFactorRecoveryCode.used_at.is_(None),
            )
            .values(used_at=func.now())
        )
        db.session.commit()
        return result.rowcount > 0
