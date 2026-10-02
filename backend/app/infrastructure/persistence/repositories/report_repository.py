# Implementación SQLAlchemy de `ReportRepository`
# (domain/reports/repositories.py, ADR-032-content-reports-and-moderation.md).

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

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

    def create_if_absent(
        self, reporter_id, target_type, target_id, reported_user_id, reason, details, snapshot
    ):
        existing = self._find(reporter_id, target_type, target_id)
        if existing is not None:
            return existing, False

        report = Report(
            reporter_id=reporter_id,
            target_type=target_type,
            target_id=target_id,
            reported_user_id=reported_user_id,
            reason=reason,
            details=details,
            content_snapshot=snapshot,
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
            return existing, False

        return report, True
