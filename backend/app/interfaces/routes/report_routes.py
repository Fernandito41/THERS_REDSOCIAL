# POST /api/reports (ADR-032-content-reports-and-moderation.md §2).
#
# Fase 1: solo se puede REPORTAR. Las rutas de moderación (cola, resolver,
# suspender) son de la fase 2 y no existen todavía.

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.application.rate_limiting import rate_limit_guard
from app.application.reports.report_use_cases import create_report
from app.domain.rate_limiting import policy
from app.domain.rate_limiting.exceptions import RateLimitExceededError
from app.domain.reports.exceptions import (
    CannotReportSelfError,
    InvalidReportError,
    ReportTargetNotFoundError,
)
from app.infrastructure.persistence.repositories.follow_repository import (
    SQLAlchemyFollowRepository,
)
from app.infrastructure.persistence.repositories.rate_limit_repository import (
    SQLAlchemyRateLimitRepository,
)
from app.infrastructure.persistence.repositories.report_repository import (
    SQLAlchemyReportRepository,
)
from app.infrastructure.persistence.repositories.report_target_resolver import (
    SQLAlchemyReportTargetResolver,
)
from app.infrastructure.persistence.repositories.restriction_repository import (
    SQLAlchemyRestrictionRepository,
)
from app.interfaces.rate_limited_response import rate_limited_response

reports_bp = Blueprint("reports", __name__)

_report_repository = SQLAlchemyReportRepository()
_target_resolver = SQLAlchemyReportTargetResolver()
_follow_repository = SQLAlchemyFollowRepository()
_restriction_repository = SQLAlchemyRestrictionRepository()
_rate_limit_repository = SQLAlchemyRateLimitRepository()


@reports_bp.route("/reports", methods=["POST"])
@jwt_required()
def post_report():
    reporter_id = get_jwt_identity()

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"msg": "No se enviaron datos"}), 400

    # El límite va ANTES de cualquier trabajo: reportar en bucle es una forma de
    # saturar a quien modera. Por persona, no por IP: la cuenta es lo que se
    # protege (ADR-032 §2, regla `REPORT_CREATE` de ADR-027).
    try:
        rate_limit_guard.enforce(
            policy.REPORT_CREATE, f"user:{reporter_id}", _rate_limit_repository
        )
    except RateLimitExceededError as error:
        return rate_limited_response(error)

    # Whitelist explícita: `reporter_id` sale SOLO del JWT, nunca del cuerpo, y
    # `status`, `reported_user_id` o cualquier otro campo del cuerpo se ignoran.
    try:
        report, created = create_report(
            reporter_id,
            data.get("target_type"),
            data.get("target_id"),
            data.get("reason"),
            data.get("details"),
            _target_resolver,
            _report_repository,
            _follow_repository,
            _restriction_repository,
        )
    except InvalidReportError as error:
        return jsonify({"msg": error.message}), 400
    except ReportTargetNotFoundError:
        # Un solo 404 para "no existe" y "no puedes verlo" (ADR-032 §2).
        return jsonify({"msg": "No encontramos lo que quieres reportar"}), 404
    except CannotReportSelfError:
        return jsonify({"msg": "No puedes reportar tu propio contenido ni tu cuenta"}), 400

    # 201 si es nuevo; 200 si ya lo habías reportado (idempotente).
    return jsonify({"report": report}), 201 if created else 200
