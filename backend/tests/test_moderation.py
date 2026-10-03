# Pruebas de la moderación de la plataforma (ADR-032 §3, fase 2) contra PostgreSQL
# real (ver conftest.py). Garantías verificadas:
#  - las rutas solo existen para quien es moderador: cualquier otra persona recibe el
#    MISMO 404 que una URL inexistente (no se anuncia que están ahí);
#  - la cola pone lo crítico primero y no revela quién reportó;
#  - resolver deja rastro (quién, cuándo, nota) y vacía la copia del texto;
#  - retirar contenido, descartar y suspender hacen lo que dicen, sin dejar reportes
#    huérfanos;
#  - una cuenta suspendida no puede entrar, ve el motivo (no la nota interna) y sus
#    sesiones dejan de valer de inmediato;
#  - el rol solo se concede por línea de comandos y un moderador no puede actuar sobre
#    sí mismo ni suspender a otro moderador.

import uuid

import pytest

from app.domain.platform_moderation import actions
from app.domain.reports import kinds
from app.extensions import db
from app.infrastructure.persistence.models import Post, Report, User
from tests.test_reports import (
    VALID_PASSWORD,
    _comment,
    _h,
    _message,
    _post,
    _register_and_login,
    _report,
)

UNKNOWN_ROUTE = "Recurso no encontrado"


def _make_moderator(app, user_id, value=True):
    with app.app_context():
        user = db.session.get(User, user_id)
        user.is_moderator = value
        db.session.commit()


def _setup(app, client):
    """Un moderador, una autora y una persona que reporta."""
    moderator, moderator_id = _register_and_login(client, "moderadora")
    _make_moderator(app, moderator_id)
    author, author_id = _register_and_login(client, "autora")
    reporter, reporter_id = _register_and_login(client, "reportante")
    return {
        "mod": moderator,
        "mod_id": moderator_id,
        "author": author,
        "author_id": author_id,
        "reporter": reporter,
        "reporter_id": reporter_id,
    }


def _queue(client, token, **params):
    return client.get("/api/moderation/reports", query_string=params, headers=_h(token))


def _resolve(client, token, report_id, action="dismiss", **extra):
    body = {"action": action}
    body.update(extra)
    return client.post(f"/api/moderation/reports/{report_id}/resolve", json=body, headers=_h(token))


def _report_row(app, report_id):
    with app.app_context():
        row = db.session.get(Report, report_id)
        db.session.expunge(row)
        return row


def _first_report_id(client, s, **params):
    return _queue(client, s["mod"], **params).get_json()["reports"][0]["id"]


class TestAccess:
    def test_a_regular_account_gets_the_same_404_as_an_unknown_route(self, app, client):
        s = _setup(app, client)
        unknown = client.get("/api/ruta-que-no-existe", headers=_h(s["author"]))

        listing = _queue(client, s["author"])
        resolving = _resolve(client, s["author"], str(uuid.uuid4()))

        for response in (listing, resolving):
            assert response.status_code == 404
            assert response.get_json() == unknown.get_json() == {"msg": UNKNOWN_ROUTE}

    def test_a_suspended_moderator_loses_access(self, app, client):
        s = _setup(app, client)
        with app.app_context():
            user = db.session.get(User, s["mod_id"])
            user.suspended_at = db.func.now()
            db.session.commit()

        assert _queue(client, s["mod"]).status_code == 404

    def test_the_role_is_checked_against_the_database_each_time(self, app, client):
        s = _setup(app, client)
        assert _queue(client, s["mod"]).status_code == 200

        _make_moderator(app, s["mod_id"], False)

        assert _queue(client, s["mod"]).status_code == 404

    def test_anonymous_requests_are_rejected(self, client):
        assert client.get("/api/moderation/reports").status_code == 401

    def test_the_api_cannot_grant_the_role(self, app, client):
        s = _setup(app, client)

        client.patch("/api/users/me", json={"is_moderator": True}, headers=_h(s["author"]))

        assert _queue(client, s["author"]).status_code == 404
        with app.app_context():
            assert db.session.get(User, s["author_id"]).is_moderator is False

    def test_own_user_object_says_whether_it_is_a_moderator(self, app, client):
        s = _setup(app, client)

        assert client.get("/api/users/me", headers=_h(s["mod"])).get_json()["user"]["is_moderator"] is True
        assert client.get("/api/users/me", headers=_h(s["author"])).get_json()["user"]["is_moderator"] is False


class TestQueue:
    def test_lists_open_reports_with_what_a_moderator_needs(self, app, client):
        s = _setup(app, client)
        post_id = _post(client, s["author"], "texto reportado")
        _report(client, s["reporter"], "post", post_id, "spam", details="es spam")

        body = _queue(client, s["mod"]).get_json()

        assert body["has_more"] is False
        report = body["reports"][0]
        assert report["target_type"] == "post" and report["target_id"] == post_id
        assert report["content_snapshot"] == "texto reportado"
        assert report["details"] == "es spam"
        assert report["status"] == "open" and report["priority"] == "normal"
        assert report["reported_user"]["username"] == "autora"
        assert report["reports_on_target"] == 1

    def test_never_reveals_who_reported_or_private_account_data(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "post", _post(client, s["author"]), "spam")

        text = _queue(client, s["mod"]).get_data(as_text=True)

        assert s["reporter_id"] not in text
        assert "reportante" not in text
        assert "reporter_id" not in text
        assert "@example.com" not in text

    def test_critical_reports_come_first_then_oldest_first(self, app, client):
        s = _setup(app, client)
        first = _post(client, s["author"], "primero")
        second = _post(client, s["author"], "segundo")
        third = _post(client, s["author"], "tercero")
        _report(client, s["reporter"], "post", first, "spam")
        _report(client, s["reporter"], "post", second, "spam")
        _report(client, s["reporter"], "post", third, kinds.REASON_CHILD_SAFETY)

        order = [r["target_id"] for r in _queue(client, s["mod"]).get_json()["reports"]]

        assert order == [third, first, second]

    def test_counts_how_many_reports_a_target_has(self, app, client):
        s = _setup(app, client)
        other, _ = _register_and_login(client, "otra")
        post_id = _post(client, s["author"])
        _report(client, s["reporter"], "post", post_id, "spam")
        _report(client, other, "post", post_id, "hate")

        reports = _queue(client, s["mod"]).get_json()["reports"]

        assert len(reports) == 2
        assert {r["reports_on_target"] for r in reports} == {2}

    def test_filters_by_status(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "post", _post(client, s["author"]), "spam")
        report_id = _first_report_id(client, s)
        _resolve(client, s["mod"], report_id)

        assert _queue(client, s["mod"]).get_json()["reports"] == []
        dismissed = _queue(client, s["mod"], status="dismissed").get_json()["reports"]
        assert [r["id"] for r in dismissed] == [report_id]

    def test_paginates(self, app, client):
        s = _setup(app, client)
        for i in range(3):
            _report(client, s["reporter"], "post", _post(client, s["author"], f"p{i}"), "spam")

        page = _queue(client, s["mod"], limit=2).get_json()
        rest = _queue(client, s["mod"], limit=2, offset=2).get_json()

        assert len(page["reports"]) == 2 and page["has_more"] is True
        assert len(rest["reports"]) == 1 and rest["has_more"] is False

    @pytest.mark.parametrize(
        "params",
        [{"status": "otro"}, {"limit": "0"}, {"limit": "101"}, {"limit": "x"}, {"offset": "-1"}],
    )
    def test_rejects_invalid_filters(self, app, client, params):
        s = _setup(app, client)

        assert _queue(client, s["mod"], **params).status_code == 400


class TestDismiss:
    def test_closes_the_report_leaves_a_trail_and_clears_the_copy(self, app, client):
        s = _setup(app, client)
        post_id = _post(client, s["author"])
        _report(client, s["reporter"], "post", post_id, "spam")
        report_id = _first_report_id(client, s)

        response = _resolve(client, s["mod"], report_id, "dismiss", note="no incumple")

        assert response.status_code == 200
        assert response.get_json()["report"] == {
            "id": report_id, "status": "dismissed", "action": "dismiss",
        }
        row = _report_row(app, report_id)
        assert row.status == "dismissed"
        assert str(row.resolved_by) == s["mod_id"]
        assert row.resolved_at is not None
        assert row.resolution_note == "no incumple"
        assert row.content_snapshot is None
        with app.app_context():
            assert db.session.get(Post, post_id) is not None

    def test_a_resolved_report_cannot_be_resolved_again(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "post", _post(client, s["author"]), "spam")
        report_id = _first_report_id(client, s)
        _resolve(client, s["mod"], report_id)

        assert _resolve(client, s["mod"], report_id).status_code == 409

    def test_the_client_cannot_choose_the_trail_fields(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "post", _post(client, s["author"]), "spam")
        report_id = _first_report_id(client, s)

        _resolve(client, s["mod"], report_id, "dismiss", status="actioned", resolved_by=s["author_id"])

        row = _report_row(app, report_id)
        assert row.status == "dismissed" and str(row.resolved_by) == s["mod_id"]

    @pytest.mark.parametrize("body", [{}, {"action": "borrar"}, {"action": None}, {"action": ["dismiss"]}])
    def test_rejects_an_invalid_action(self, app, client, body):
        s = _setup(app, client)
        _report(client, s["reporter"], "post", _post(client, s["author"]), "spam")
        report_id = _first_report_id(client, s)

        response = client.post(
            f"/api/moderation/reports/{report_id}/resolve", json=body, headers=_h(s["mod"])
        )

        assert response.status_code == 400
        assert _report_row(app, report_id).status == "open"

    def test_rejects_a_too_long_note(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "post", _post(client, s["author"]), "spam")
        report_id = _first_report_id(client, s)

        response = _resolve(client, s["mod"], report_id, note="x" * (actions.MAX_NOTE_LENGTH + 1))

        assert response.status_code == 400

    @pytest.mark.parametrize("report_id", [str(uuid.uuid4()), "no-es-un-uuid"])
    def test_unknown_report_is_a_404(self, app, client, report_id):
        s = _setup(app, client)

        assert _resolve(client, s["mod"], report_id).status_code == 404


class TestRemoveContent:
    def test_removes_a_post_and_closes_the_other_reports_on_it(self, app, client):
        s = _setup(app, client)
        other, _ = _register_and_login(client, "otra")
        post_id = _post(client, s["author"])
        _report(client, s["reporter"], "post", post_id, "spam")
        _report(client, other, "post", post_id, "hate")
        report_id = _first_report_id(client, s)

        response = _resolve(client, s["mod"], report_id, "remove_content")

        assert response.status_code == 200
        with app.app_context():
            assert db.session.get(Post, post_id) is None
            statuses = {r.status for r in db.session.query(Report).all()}
            snapshots = {r.content_snapshot for r in db.session.query(Report).all()}
        assert statuses == {"actioned"}
        assert snapshots == {None}
        assert _queue(client, s["mod"]).get_json()["reports"] == []

    def test_removes_a_comment(self, app, client):
        s = _setup(app, client)
        post_id = _post(client, s["reporter"])
        comment_id = _comment(client, s["author"], post_id, "comentario ofensivo")
        _report(client, s["reporter"], "comment", comment_id, "harassment")
        report_id = _first_report_id(client, s)

        _resolve(client, s["mod"], report_id, "remove_content")

        comments = client.get(f"/api/posts/{post_id}/comments", headers=_h(s["reporter"]))
        assert comments.get_json()["comments"] == []

    def test_removes_a_message_from_both_inboxes(self, app, client):
        s = _setup(app, client)
        message_id = _message(client, s["author"], s["reporter_id"], "mensaje ofensivo")
        _report(client, s["reporter"], "message", message_id, "harassment")
        report_id = _first_report_id(client, s)

        _resolve(client, s["mod"], report_id, "remove_content")

        thread = client.get(f"/api/users/{s['author_id']}/messages", headers=_h(s["reporter"]))
        assert thread.get_json()["messages"] == []

    def test_a_report_about_an_account_has_no_content_to_remove(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "user", s["author_id"], "impersonation")
        report_id = _first_report_id(client, s)

        response = _resolve(client, s["mod"], report_id, "remove_content")

        assert response.status_code == 400
        assert _report_row(app, report_id).status == "open"

    def test_content_already_deleted_by_its_author_is_not_an_error(self, app, client):
        s = _setup(app, client)
        post_id = _post(client, s["author"])
        _report(client, s["reporter"], "post", post_id, "spam")
        client.delete(f"/api/posts/{post_id}", headers=_h(s["author"]))
        report_id = _first_report_id(client, s)

        response = _resolve(client, s["mod"], report_id, "remove_content")

        assert response.status_code == 200
        assert _report_row(app, report_id).status == "actioned"

    def test_the_copy_of_the_text_survives_until_resolved(self, app, client):
        # ADR-032 §4: aunque el autor borre el contenido, quien modera ve qué se dijo.
        s = _setup(app, client)
        post_id = _post(client, s["author"], "lo que se dijo")
        _report(client, s["reporter"], "post", post_id, "spam")
        client.delete(f"/api/posts/{post_id}", headers=_h(s["author"]))

        assert _queue(client, s["mod"]).get_json()["reports"][0]["content_snapshot"] == "lo que se dijo"


class TestSuspend:
    def _suspend(self, app, client, s, **extra):
        _report(client, s["reporter"], "user", s["author_id"], "harassment")
        report_id = _first_report_id(client, s)
        return report_id, _resolve(client, s["mod"], report_id, "suspend_user", **extra)

    def _login(self, client, username="autora", password=VALID_PASSWORD):
        return client.post("/api/login", json={"email": f"{username}@example.com", "password": password})

    def test_a_suspended_account_cannot_log_in_and_sees_the_reason(self, app, client):
        s = _setup(app, client)

        report_id, response = self._suspend(app, client, s, reason="Acoso repetido")

        assert response.status_code == 200
        assert _report_row(app, report_id).status == "actioned"
        login = self._login(client)
        assert login.status_code == 403
        body = login.get_json()
        assert body["suspended"] is True
        assert body["suspension_reason"] == "Acoso repetido"
        assert "token" not in body

    def test_uses_a_standard_reason_and_never_shows_the_internal_note(self, app, client):
        s = _setup(app, client)

        self._suspend(app, client, s, note="nota interna: parece reincidente")

        body = self._login(client).get_json()
        assert body["suspension_reason"] == actions.DEFAULT_SUSPENSION_REASON
        assert "reincidente" not in str(body)

    def test_existing_sessions_stop_working_immediately(self, app, client):
        s = _setup(app, client)
        assert client.get("/api/users/me", headers=_h(s["author"])).status_code == 200

        self._suspend(app, client, s)

        assert client.get("/api/users/me", headers=_h(s["author"])).status_code == 401

    def test_refresh_tokens_stop_working_too(self, app, client):
        s = _setup(app, client)
        login = self._login(client).get_json()
        self._suspend(app, client, s)

        refresh = client.post(
            "/api/refresh", headers={"Authorization": f"Bearer {login['refresh_token']}"}
        )

        assert refresh.status_code == 401

    def test_a_wrong_password_is_still_a_401_so_suspension_is_not_an_oracle(self, app, client):
        s = _setup(app, client)
        self._suspend(app, client, s)

        assert self._login(client, password="otra-contraseña").status_code == 401

    def test_suspending_twice_keeps_the_original_reason(self, app, client):
        s = _setup(app, client)
        self._suspend(app, client, s, reason="Primera")
        other, _ = _register_and_login(client, "otra")
        _report(client, other, "user", s["author_id"], "hate")
        second = _first_report_id(client, s)

        _resolve(client, s["mod"], second, "suspend_user", reason="Segunda")

        assert self._login(client).get_json()["suspension_reason"] == "Primera"

    def test_a_moderator_cannot_be_suspended_from_the_panel(self, app, client):
        s = _setup(app, client)
        other_mod, other_mod_id = _register_and_login(client, "moderador2")
        _make_moderator(app, other_mod_id)
        _report(client, s["reporter"], "user", other_mod_id, "harassment")
        report_id = _first_report_id(client, s)

        response = _resolve(client, s["mod"], report_id, "suspend_user")

        assert response.status_code == 400
        assert _queue(client, other_mod).status_code == 200

    def test_a_moderator_cannot_resolve_a_report_about_themselves(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "user", s["mod_id"], "harassment")
        report_id = _first_report_id(client, s)

        for action in actions.ACTIONS:
            assert _resolve(client, s["mod"], report_id, action).status_code == 403
        assert _report_row(app, report_id).status == "open"

    def test_the_reason_is_only_for_suspensions(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "post", _post(client, s["author"]), "spam")
        report_id = _first_report_id(client, s)

        assert _resolve(client, s["mod"], report_id, "dismiss", reason="x").status_code == 400

    def test_an_account_that_no_longer_exists_cannot_be_suspended(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "user", s["author_id"], "harassment")
        with app.app_context():
            db.session.delete(db.session.get(User, s["author_id"]))
            db.session.commit()
        report_id = _first_report_id(client, s)

        response = _resolve(client, s["mod"], report_id, "suspend_user")

        assert response.status_code == 400

    def test_other_accounts_are_unaffected(self, app, client):
        s = _setup(app, client)

        self._suspend(app, client, s)

        assert client.get("/api/users/me", headers=_h(s["reporter"])).status_code == 200
        assert self._login(client, "reportante").status_code == 200


class TestCommandLine:
    def _run(self, app, *args):
        return app.test_cli_runner().invoke(args=list(args))

    def test_grants_and_revokes_the_role(self, app, client):
        _, user_id = _register_and_login(client, "futura")

        granted = self._run(app, "set-moderator", "futura@example.com")
        with app.app_context():
            assert db.session.get(User, user_id).is_moderator is True
        revoked = self._run(app, "set-moderator", "futura@example.com", "--revoke")

        assert granted.exit_code == 0 and "concedido" in granted.output
        assert "2FA" in granted.output  # la cuenta no tiene 2FA: se avisa
        assert revoked.exit_code == 0
        with app.app_context():
            assert db.session.get(User, user_id).is_moderator is False

    def test_an_unknown_email_fails_without_changing_anything(self, app, client):
        result = self._run(app, "set-moderator", "nadie@example.com")

        assert result.exit_code != 0
        assert "No existe una cuenta" in result.output

    def test_unsuspend_lifts_the_suspension(self, app, client):
        s = _setup(app, client)
        _report(client, s["reporter"], "user", s["author_id"], "harassment")
        _resolve(client, s["mod"], _first_report_id(client, s), "suspend_user")

        result = self._run(app, "unsuspend-user", "autora@example.com")

        assert result.exit_code == 0 and "levantada" in result.output
        login = client.post(
            "/api/login", json={"email": "autora@example.com", "password": VALID_PASSWORD}
        )
        assert login.status_code == 200

    def test_unsuspend_on_a_regular_account_changes_nothing(self, app, client):
        _register_and_login(client, "normal")

        result = self._run(app, "unsuspend-user", "normal@example.com")

        assert result.exit_code == 0 and "no estaba suspendida" in result.output
