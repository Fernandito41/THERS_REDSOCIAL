# Adaptador SQLAlchemy del puerto `SessionRepository`
# (domain/sessions/repositories.py). Único punto del backend que traduce entre
# `sessions` (PostgreSQL) y el resto de las capas -- domain/ y application/ no
# importan SQLAlchemy directamente (BACKEND_ARCHITECTURE.md §17), mismo patrón
# que follow_repository.py.

from sqlalchemy import func, or_, select, text, update

from app.domain.sessions.repositories import SessionRepository
from app.extensions import db
from app.infrastructure.persistence.models import Session


class SQLAlchemySessionRepository(SessionRepository):
    def create(self, user_id, jti, user_agent, ip_address):
        session = Session(
            user_id=user_id, jti=jti, user_agent=user_agent, ip_address=ip_address
        )
        db.session.add(session)
        db.session.commit()
        db.session.refresh(session)
        return session

    def is_active(self, jti):
        # Consulta más caliente del backend: corre en cada petición protegida.
        # Se pide solo `id` (no la fila entera) y va por uq_sessions_jti.
        return (
            db.session.execute(
                select(Session.id).where(
                    Session.jti == jti, Session.revoked_at.is_(None)
                )
            ).first()
            is not None
        )

    def list_for_user(self, user_id, limit):
        return (
            db.session.execute(
                select(Session)
                .where(Session.user_id == user_id, Session.revoked_at.is_(None))
                .order_by(Session.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )

    def revoke(self, session_id, user_id):
        # `user_id` y `revoked_at IS NULL` en el propio WHERE: confirma
        # existencia, pertenencia y que siga viva en una sola sentencia, sin
        # ventana entre comprobar y actuar (mismo principio que el resto de
        # operaciones sobre recursos propios, ADR-019/ADR-020/ADR-021).
        # RETURNING jti: el mismo UPDATE confirma que había algo que revocar
        # y dice cuál era, así que no hace falta un SELECT previo para saber si
        # la sesión cerrada era la del propio token.
        result = db.session.execute(
            update(Session)
            .where(
                Session.id == session_id,
                Session.user_id == user_id,
                Session.revoked_at.is_(None),
            )
            .values(revoked_at=func.now())
            .returning(Session.jti)
        )
        revoked_jti = result.scalar_one_or_none()
        db.session.commit()
        return revoked_jti

    def revoke_all_except(self, user_id, keep_jti):
        result = db.session.execute(
            update(Session)
            .where(
                Session.user_id == user_id,
                Session.jti != keep_jti,
                Session.revoked_at.is_(None),
            )
            .values(revoked_at=func.now())
        )
        db.session.commit()
        return result.rowcount

    def revoke_all_for_user(self, user_id):
        result = db.session.execute(
            update(Session)
            .where(Session.user_id == user_id, Session.revoked_at.is_(None))
            .values(revoked_at=func.now())
        )
        db.session.commit()
        return result.rowcount

    def touch(self, jti, min_interval_seconds):
        # Throttle en el WHERE, no en memoria del proceso -- mismo criterio y
        # mismo motivo que SQLAlchemyUserRepository.touch_last_seen (ADR-024):
        # funciona igual con varios workers.
        db.session.execute(
            update(Session)
            .where(
                Session.jti == jti,
                Session.revoked_at.is_(None),
                or_(
                    Session.last_used_at.is_(None),
                    Session.last_used_at
                    < func.now() - text(f"interval '{int(min_interval_seconds)} seconds'"),
                ),
            )
            .values(last_used_at=func.now())
        )
        db.session.commit()

    def has_seen_user_agent(self, user_id, user_agent):
        # Incluye las revocadas a propósito: un dispositivo del que ya cerraste
        # sesión sigue siendo un dispositivo conocido, y volver a entrar desde
        # él no debería generar una alerta.
        return (
            db.session.execute(
                select(Session.id).where(
                    Session.user_id == user_id, Session.user_agent == user_agent
                )
            ).first()
            is not None
        )
