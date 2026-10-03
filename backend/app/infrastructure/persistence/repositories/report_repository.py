# Implementación SQLAlchemy de `ReportRepository`
# (domain/reports/repositories.py, ADR-032-content-reports-and-moderation.md).

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.reports import kinds
from app.domain.reports.repositories import ReportRepository
from app.extensions import db
from app.infrastructure.persistence.models import Report


class SQLAlchemyReportRepository(ReportRepository):
    def _find(self, reporter_id, target_type, target_id):
        return db.session.execute(
            select(Report).where(
                Report.reporter_id == reporter_id,
                Report.target_type == target_type,
                Report.target_id == target_id,
            )
        ).scalar_one_or_none()

    @staticmethod
    def _escalate_if_more_urgent(existing, reason, details, priority):
        """Eleva el reporte existente si el nuevo es más urgente (ADR-038). Nunca degrada."""
        if not kinds.is_higher_priority(priority, existing.priority):
            return
        existing.reason = reason
        existing.priority = priority
        if details is not None:
            existing.details = details
        # Reabrir si se había descartado: lo escalado debe volver a la cola. Si está en
        # revisión o ya se actuó, el estado no se toca.
        if existing.status == kinds.STATUS_DISMISSED:
            existing.status = kinds.STATUS_OPEN
            existing.resolved_at = None
            existing.resolved_by = None
            existing.resolution_note = None

    def create_if_absent(
        self, reporter_id, target_type, target_id, reported_user_id, reason, details, snapshot,
        priority=kinds.PRIORITY_NORMAL,
    ):
        existing = self._find(reporter_id, target_type, target_id)
        if existing is not None:
            self._escalate_if_more_urgent(existing, reason, details, priority)
            db.session.commit()
            return existing, False

        report = Report(
            reporter_id=reporter_id,
            target_type=target_type,
            target_id=target_id,
            reported_user_id=reported_user_id,
            reason=reason,
            details=details,
            content_snapshot=snapshot,
            priority=priority,
        )
        db.session.add(report)

        try:
            db.session.commit()
        except IntegrityError:
            # Dos peticiones simultáneas del mismo reporte: la que perdió la
            # carrera choca con `uq_reports_reporter_target`. No es un error:
            # el reporte ya existe, que es lo que esa persona quería.
            db.session.rollback()
            existing = self._find(reporter_id, target_type, target_id)
            if existing is None:
                raise
            self._escalate_if_more_urgent(existing, reason, details, priority)
            db.session.commit()
            return existing, False

        return report, True
