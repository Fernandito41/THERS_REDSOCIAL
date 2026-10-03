# Pruebas del motivo de reporte `child_safety` y de su prioridad
# (ADR-038-child-safety-reports.md) contra PostgreSQL real (ver conftest.py).
#
# Garantías verificadas:
#  - el motivo existe para TODOS los tipos de objetivo que el sistema ya soporta;
#  - su prioridad es `critical` y la decide SOLO el servidor (el cliente no puede
#    fijarla, subirla ni degradarla);
#  - un reporte previo menos urgente del mismo objetivo se ESCALA (si no, el índice único
#    de ADR-032 haría perder la prioridad) y nunca se degrada;
#  - los demás motivos siguen igual (prioridad `normal`) y los inválidos se rechazan;
#  - tiene su propio límite de uso, para no bloquear una denuncia grave.

import pytest
from sqlalchemy.exc import IntegrityError

from app.domain.rate_limiting import policy
from app.domain.reports import kinds
from app.extensions import db
from app.infrastructure.persistence.models import Report
from tests.test_reports import (
    _all_reports,
    _block,
    _comment,
    _h,
    _make_private,
    _message,
    _post,
    _register_and_login,
    _report,
)

CS = "child_safety"


def _targets(client):
    """Una persona que reporta y un objetivo de cada tipo que el sistema soporta."""
    reporter, reporter_id = _register_and_login(client, "reportante")
    author, author_id = _register_and_login(client, "autora")
    post_id = _post(client, author)
    return {
        "reporter": reporter,
        "reporter_id": reporter_id,
        "author": author,
        "author_id": author_id,
        "post": post_id,
        "comment": _comment(client, author, post_id),
        "message": _message(client, author, reporter_id),
    }


class TestChildSafetyCategory:
    @pytest.mark.parametrize("target_type", ["post", "comment", "message", "user"])
    def test_it_can_be_reported_for_every_supported_target_type(self, client, target_type):
        t = _targets(client)
        target_id = t["author_id"] if target_type == "user" else t[target_type]

        response = _report(client, t["reporter"], target_type, target_id, CS)

        assert response.status_code == 201
        report = response.get_json()["report"]
        assert report["reason"] == CS
        assert report["priority"] == "critical"
        assert report["target_type"] == target_type

    def test_the_reason_and_priority_are_stored(self, app, client):
        t = _targets(client)

        _report(client, t["reporter"], "post", t["post"], CS)

        stored = _all_reports(app)
        assert len(stored) == 1
        assert stored[0].reason == CS
        assert stored[0].priority == "critical"
        assert stored[0].status == "open"

    def test_it_is_part_of_the_reason_catalog(self):
        assert kinds.REASON_CHILD_SAFETY == CS
        assert CS in kinds.REASONS

    def test_the_response_still_hides_who_reported_and_the_copied_text(self, client):
        t = _targets(client)

        report = _report(client, t["reporter"], "post", t["post"], CS).get_json()["report"]

        for hidden in ("reporter_id", "reported_user_id", "content_snapshot", "snapshot"):
            assert hidden not in report

    def test_the_visibility_guards_still_apply(self, client):
        # No se puede reportar lo que no se puede ver, ni siquiera con este motivo.
        t = _targets(client)
        _make_private(client, t["author"])

        response = _report(client, t["reporter"], "post", t["post"], CS)

        assert response.status_code == 404

    def test_a_blocked_account_cannot_be_used_to_probe_existence(self, client):
        t = _targets(client)
        _block(client, t["author"], t["reporter_id"])

        assert _report(client, t["reporter"], "user", t["author_id"], CS).status_code == 404


class TestPriorityIsDecidedByTheServer:
    def test_the_client_cannot_downgrade_a_child_safety_report(self, app, client):
        t = _targets(client)

        report = _report(
            client, t["reporter"], "post", t["post"], CS, priority="normal"
        ).get_json()["report"]

        assert report["priority"] == "critical"
        assert _all_reports(app)[0].priority == "critical"

    def test_the_client_cannot_raise_the_priority_of_another_reason(self, app, client):
        t = _targets(client)

        report = _report(
            client, t["reporter"], "post", t["post"], "spam", priority="critical"
        ).get_json()["report"]

        assert report["priority"] == "normal"
        assert _all_reports(app)[0].priority == "normal"

    @pytest.mark.parametrize("extra", [{"status": "actioned"}, {"resolved_by": "x"}, {"reporter_id": "x"}])
    def test_other_fields_are_still_ignored(self, app, client, extra):
        t = _targets(client)

        response = _report(client, t["reporter"], "post", t["post"], CS, **extra)

        assert response.status_code == 201
        assert _all_reports(app)[0].status == "open"

    @pytest.mark.parametrize("reason", [r for r in kinds.REASONS if r != CS])
    def test_every_other_reason_keeps_normal_priority(self, client, reason):
        t = _targets(client)

        report = _report(client, t["reporter"], "post", t["post"], reason).get_json()["report"]

        assert report["priority"] == "normal"

    def test_the_priority_rule_is_a_pure_function_of_the_reason(self):
        assert kinds.priority_for_reason(CS) == "critical"
        assert kinds.priority_for_reason("spam") == "normal"
        assert kinds.is_higher_priority("critical", "normal")
        assert not kinds.is_higher_priority("normal", "critical")
        assert not kinds.is_higher_priority("critical", "critical")

    def test_the_database_rejects_an_unknown_priority(self, app):
        with app.app_context():
            db.session.add(
                Report(target_type="post", target_id="00000000-0000-0000-0000-000000000001",
                       reason="spam", priority="urgent")
            )
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()


class TestValidation:
    @pytest.mark.parametrize(
        "reason", ["CHILD_SAFETY", "Child_Safety", "child-safety", "csam", "child safety", "", None, 7, ["child_safety"]]
    )
    def test_look_alike_or_invalid_reasons_are_rejected(self, app, client, reason):
        t = _targets(client)

        response = _report(client, t["reporter"], "post", t["post"], reason)

        assert response.status_code == 400
        assert _all_reports(app) == []

    def test_existing_reasons_keep_working(self, client):
        t = _targets(client)

        assert _report(client, t["reporter"], "post", t["post"], "harassment").status_code == 201


class TestEscalation:
    def test_reporting_as_child_safety_escalates_an_earlier_milder_report(self, app, client):
        # El índice único (quien reporta, tipo, objetivo) devolvería el reporte viejo y
        # perdería la prioridad: debe elevarse.
        t = _targets(client)
        first = _report(client, t["reporter"], "post", t["post"], "spam").get_json()["report"]

        second = _report(
            client, t["reporter"], "post", t["post"], CS, details="detalle nuevo"
        )

        assert second.status_code == 200  # ya existía: no se crea otro
        body = second.get_json()["report"]
        assert body["id"] == first["id"]
        assert body["priority"] == "critical"
        assert body["reason"] == CS
        assert body["already_reported"] is True
        stored = _all_reports(app)
        assert len(stored) == 1
        assert stored[0].priority == "critical" and stored[0].reason == CS
        assert stored[0].details == "detalle nuevo"

    def test_a_later_milder_report_never_downgrades_it(self, app, client):
        t = _targets(client)
        _report(client, t["reporter"], "post", t["post"], CS)

        again = _report(client, t["reporter"], "post", t["post"], "spam").get_json()["report"]

        assert again["priority"] == "critical"
        assert again["reason"] == CS
        assert _all_reports(app)[0].reason == CS

    def test_a_dismissed_report_is_reopened_when_escalated(self, app, client):
        t = _targets(client)
        _report(client, t["reporter"], "post", t["post"], "spam")
        with app.app_context():
            report = db.session.query(Report).one()
            report.status = kinds.STATUS_DISMISSED
            db.session.commit()

        _report(client, t["reporter"], "post", t["post"], CS)

        assert _all_reports(app)[0].status == "open"

    def test_a_report_under_review_keeps_its_status_when_escalated(self, app, client):
        t = _targets(client)
        _report(client, t["reporter"], "post", t["post"], "spam")
        with app.app_context():
            report = db.session.query(Report).one()
            report.status = kinds.STATUS_REVIEWING
            db.session.commit()

        _report(client, t["reporter"], "post", t["post"], CS)

        stored = _all_reports(app)[0]
        assert stored.status == "reviewing" and stored.priority == "critical"

    def test_repeating_the_same_child_safety_report_is_idempotent(self, app, client):
        t = _targets(client)

        first = _report(client, t["reporter"], "post", t["post"], CS)
        second = _report(client, t["reporter"], "post", t["post"], CS)

        assert (first.status_code, second.status_code) == (201, 200)
        assert len(_all_reports(app)) == 1

    def test_different_people_reporting_the_same_content_create_separate_critical_reports(
        self, app, client
    ):
        t = _targets(client)
        other, _ = _register_and_login(client, "otrapersona")

        _report(client, t["reporter"], "post", t["post"], CS)
        _report(client, other, "post", t["post"], CS)

        stored = _all_reports(app)
        assert len(stored) == 2
        assert {r.priority for r in stored} == {"critical"}


class TestRateLimit:
    def test_it_has_its_own_more_generous_limit(self):
        assert policy.REPORT_CHILD_SAFETY.limit > policy.REPORT_CREATE.limit
        assert policy.REPORT_CHILD_SAFETY.scope != policy.REPORT_CREATE.scope

    def test_exhausting_the_ordinary_limit_does_not_block_a_child_safety_report(self, client):
        reporter, _ = _register_and_login(client, "reportante")
        author, _ = _register_and_login(client, "autora")
        posts = [_post(client, author, f"contenido {i}") for i in range(policy.REPORT_CREATE.limit + 2)]
        for post_id in posts[: policy.REPORT_CREATE.limit]:
            assert _report(client, reporter, "post", post_id, "spam").status_code == 201

        blocked = _report(client, reporter, "post", posts[-2], "spam")
        urgent = _report(client, reporter, "post", posts[-1], CS)

        assert blocked.status_code == 429
        assert urgent.status_code == 201
        assert urgent.get_json()["report"]["priority"] == "critical"

    def test_the_child_safety_limit_still_exists(self, client):
        reporter, _ = _register_and_login(client, "reportante")
        author, _ = _register_and_login(client, "autora")
        limit = policy.REPORT_CHILD_SAFETY.limit
        posts = [_post(client, author, f"contenido {i}") for i in range(limit + 1)]
        for post_id in posts[:limit]:
            assert _report(client, reporter, "post", post_id, CS).status_code == 201

        over = _report(client, reporter, "post", posts[-1], CS)

        assert over.status_code == 429
        assert "Retry-After" in over.headers
