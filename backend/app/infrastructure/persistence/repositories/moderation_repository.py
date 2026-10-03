# Implementación SQLAlchemy de `ModerationRepository`
# (domain/platform_moderation/repositories.py, ADR-032 fase 2).

from sqlalchemy import case, func, select, tuple_, update

from app.domain.platform_moderation.repositories import ModerationRepository
from app.domain.reports import kinds
from app.extensions import db
from app.infrastructure.persistence.models import Report, User

_OPEN_STATUSES = (kinds.STATUS_OPEN, kinds.STATUS_REVIEWING)


class SQLAlchemyModerationRepository(ModerationRepository):
    def list_reports(self, status, limit, offset):
        # Lo crítico primero (ADR-038) y, dentro de cada prioridad, lo más
        # antiguo primero (ADR-032 §3). `id` desempata para que la paginación
        # sea estable aunque dos reportes compartan la misma fecha.
        critical_first = case((Report.priority == kinds.PRIORITY_CRITICAL, 0), else_=1)
        rows = (
            db.session.execute(
                select(Report)
                .where(Report.status == status)
                .order_by(critical_first, Report.created_at.asc(), Report.id.asc())
                .limit(limit + 1)
                .offset(offset)
            )
            .scalars()
            .all()
        )
        return rows[:limit], len(rows) > limit

    def count_reports_by_target(self, targets):
        if not targets:
            return {}
        rows = db.session.execute(
            select(Report.target_type, Report.target_id, func.count(Report.id))
            .where(tuple_(Report.target_type, Report.target_id).in_(targets))
            .group_by(Report.target_type, Report.target_id)
        ).all()
        return {(target_type, str(target_id)): count for target_type, target_id, count in rows}

    def get_report_for_update(self, report_id):
        return db.session.execute(
            select(Report).where(Report.id == report_id).with_for_update()
        ).scalar_one_or_none()

    def close_report(self, report, status, moderator_id, note):
        report.status = status
        report.resolved_at = func.now()
        report.resolved_by = moderator_id
        report.resolution_note = note
        # ADR-032 §4: la copia del texto solo se conserva mientras el reporte está abierto.
        report.content_snapshot = None
        db.session.commit()

    def close_other_reports_on_target(self, report, moderator_id, note):
        result = db.session.execute(
            update(Report)
            .where(
                Report.target_type == report.target_type,
                Report.target_id == report.target_id,
                Report.id != report.id,
                Report.status.in_(_OPEN_STATUSES),
            )
            .values(
                status=kinds.STATUS_ACTIONED,
                resolved_at=func.now(),
                resolved_by=moderator_id,
                resolution_note=note,
                content_snapshot=None,
            )
        )
        db.session.commit()
        return result.rowcount

    def get_user(self, user_id):
        return db.session.get(User, user_id)

    def suspend_user(self, user_id, reason):
        # El WHERE incluye `suspended_at IS NULL`: si ya estaba suspendida se
        # conserva la fecha y el motivo originales.
        result = db.session.execute(
            update(User)
            .where(User.id == user_id, User.suspended_at.is_(None))
            .values(suspended_at=func.now(), suspension_reason=reason)
        )
        db.session.commit()
        return result.rowcount > 0

    def unsuspend_user(self, user_id):
        result = db.session.execute(
            update(User)
            .where(User.id == user_id, User.suspended_at.is_not(None))
            .values(suspended_at=None, suspension_reason=None)
        )
        db.session.commit()
        return result.rowcount > 0

    def set_moderator(self, user_id, value):
        db.session.execute(update(User).where(User.id == user_id).values(is_moderator=value))
        db.session.commit()
