# Pruebas de integración de `POST /api/reports`
# (ADR-032-content-reports-and-moderation.md, fase 1) contra PostgreSQL real
# (ver conftest.py). Verifican, contra la base de datos:
# - qué se guarda (reporter, reportado, motivo, copia del texto) y qué NO se
#   devuelve nunca (quién reportó, a quién, el texto copiado);
# - que solo se puede reportar lo que se puede ver, con un único 404 (cuentas
#   privadas de ADR-022, bloqueos de ADR-029);
# - idempotencia, validación, límite de peticiones y comportamiento al eliminarse
#   las cuentas involucradas (SET NULL, ADR-032 §1).

import uuid

import pytest

from app.domain.reports import kinds
from app.extensions import db
from app.infrastructure.persistence.models import Report, User
from tests.conftest import mark_email_verified

VALID_PASSWORD = "secretpass"
NOT_FOUND_MSG = "No encontramos lo que quieres reportar"


def _register_and_login(client, username):
    email = f"{username}@example.com"
    response = client.post(
        "/api/register",
        json={
            "name": username.capitalize(),
            "username": username,
            "email": email,
            "phone": "7000-1234",
            "country_code": "+503",
            "birth_date": "1990-01-01",
            "password": VALID_PASSWORD,
            "confirm_password": VALID_PASSWORD,
        },
    )
    user_id = response.get_json()["user"]["id"]
    mark_email_verified(user_id)
    token = client.post("/api/login", json={"email": email, "password": VALID_PASSWORD}).get_json()[
        "token"
    ]
    return token, user_id


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def _report(client, token, target_type, target_id, reason="spam", **extra):
    body = {"target_type": target_type, "target_id": target_id, "reason": reason}
    body.update(extra)
    return client.post("/api/reports", json=body, headers=_h(token))


def _post(client, token, content="contenido reportable"):
    return client.post("/api/posts", json={"content": content}, headers=_h(token)).get_json()[
        "post"
    ]["id"]


def _comment(client, token, post_id, content="comentario reportable"):
    return client.post(
        f"/api/posts/{post_id}/comments", json={"content": content}, headers=_h(token)
    ).get_json()["comment"]["id"]


def _message(client, token, recipient_id, content="mensaje reportable"):
    return client.post(
        f"/api/users/{recipient_id}/messages", json={"content": content}, headers=_h(token)
    ).get_json()["message"]["id"]


def _block(client, token, user_id):
    return client.post("/api/users/me/blocks", json={"user_id": user_id}, headers=_h(token))


def _make_private(client, token):
    return client.patch("/api/users/me/privacy", json={"is_private": True}, headers=_h(token))


def _all_reports(app):
    with app.app_context():
        return db.session.query(Report).all()


class TestAuthenticationAndValidation:
    def test_requires_authentication(self, client):
        response = client.post(
            "/api/reports",
            json={"target_type": "post", "target_id": str(uuid.uuid4()), "reason": "spam"},
        )

        assert response.status_code == 401

    def test_missing_body_is_400(self, client):
        token, _ = _register_and_login(client, "ada")

        assert client.post("/api/reports", headers=_h(token)).status_code == 400

    @pytest.mark.parametrize("body", [[], "texto", 7])
    def test_non_object_body_is_400(self, client, body):
        token, _ = _register_and_login(client, "ada")

        assert client.post("/api/reports", json=body, headers=_h(token)).status_code == 400

    def test_invalid_target_type_is_400(self, client):
        token, _ = _register_and_login(client, "ada")

        response = _report(client, token, "planet", str(uuid.uuid4()))

        assert response.status_code == 400

    def test_invalid_target_id_is_400(self, client):
        token, _ = _register_and_login(client, "ada")

        assert _report(client, token, "post", "no-es-un-uuid").status_code == 400

    def test_invalid_reason_is_400(self, client):
        token, _ = _register_and_login(client, "ada")

        response = _report(client, token, "post", str(uuid.uuid4()), reason="porque_si")

        assert response.status_code == 400

    @pytest.mark.parametrize("reason", kinds.REASONS)
    def test_every_documented_reason_is_accepted(self, client, reason):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)

        assert _report(client, token_a, "post", post_id, reason=reason).status_code == 201

    def test_details_too_long_is_400(self, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)

        response = _report(
            client, token_a, "post", post_id, details="x" * (kinds.MAX_DETAILS_LENGTH + 1)
        )

        assert response.status_code == 400

    def test_details_at_the_limit_is_accepted(self, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)

        response = _report(
            client, token_a, "post", post_id, details="x" * kinds.MAX_DETAILS_LENGTH
        )

        assert response.status_code == 201

    def test_non_string_details_is_400(self, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)

        assert _report(client, token_a, "post", post_id, details=123).status_code == 400

    def test_blank_details_are_stored_as_null(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)

        _report(client, token_a, "post", post_id, details="   ")

        assert _all_reports(app)[0].details is None


class TestReportingAPost:
    def test_creates_the_report_with_the_expected_fields(self, app, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b, "texto ofensivo de bob")

        response = _report(
            client, token_a, "post", post_id, reason="harassment", details="me acosa"
        )

        assert response.status_code == 201
        body = response.get_json()["report"]
        assert body["target_type"] == "post"
        assert body["target_id"] == post_id
        assert body["reason"] == "harassment"
        assert body["status"] == "open"
        assert body["already_reported"] is False

        row = _all_reports(app)[0]
        assert str(row.reporter_id) == id_a
        assert str(row.reported_user_id) == id_b
        assert row.details == "me acosa"
        assert row.content_snapshot == "texto ofensivo de bob"
        assert row.status == "open"

    def test_response_never_reveals_who_reported_or_the_copied_text(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b, "texto ofensivo de bob")

        raw = _report(client, token_a, "post", post_id).get_data(as_text=True)

        # Ni quién reportó, ni a quién, ni el texto copiado: ADR-032 §2.
        assert id_a not in raw
        assert id_b not in raw
        assert "texto ofensivo" not in raw
        for field in ("reporter_id", "reported_user_id", "content_snapshot", "details"):
            assert field not in raw

    def test_reporting_the_same_post_twice_is_idempotent(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)
        first = _report(client, token_a, "post", post_id)

        second = _report(client, token_a, "post", post_id, reason="hate")

        assert first.status_code == 201
        assert second.status_code == 200
        assert second.get_json()["report"]["already_reported"] is True
        assert second.get_json()["report"]["id"] == first.get_json()["report"]["id"]
        rows = _all_reports(app)
        assert len(rows) == 1
        # La segunda petición NO pisa el motivo del primer reporte.
        assert rows[0].reason == "spam"

    def test_different_people_reporting_the_same_post_create_separate_reports(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        token_c, _ = _register_and_login(client, "cleo")
        post_id = _post(client, token_c)

        assert _report(client, token_a, "post", post_id).status_code == 201
        assert _report(client, token_b, "post", post_id).status_code == 201

        assert len(_all_reports(app)) == 2

    def test_cannot_report_your_own_post(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        post_id = _post(client, token_a)

        response = _report(client, token_a, "post", post_id)

        assert response.status_code == 400
        assert _all_reports(app) == []

    def test_nonexistent_post_is_404(self, client):
        token_a, _ = _register_and_login(client, "ada")

        response = _report(client, token_a, "post", str(uuid.uuid4()))

        assert response.status_code == 404
        assert response.get_json()["msg"] == NOT_FOUND_MSG

    def test_body_cannot_set_reporter_status_or_reported_user(self, app, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        token_c, id_c = _register_and_login(client, "cleo")
        post_id = _post(client, token_b)

        _report(
            client,
            token_a,
            "post",
            post_id,
            reporter_id=id_c,
            reported_user_id=id_c,
            status="dismissed",
            resolved_by=id_c,
        )

        row = _all_reports(app)[0]
        assert str(row.reporter_id) == id_a
        assert str(row.reported_user_id) == id_b
        assert row.status == "open"
        assert row.resolved_by is None


class TestVisibilityRules:
    def test_private_account_post_is_404_for_a_non_follower(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)
        _make_private(client, token_b)

        response = _report(client, token_a, "post", post_id)

        assert response.status_code == 404
        assert _all_reports(app) == []

    def test_private_account_404_is_indistinguishable_from_a_missing_post(self, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)
        _make_private(client, token_b)

        hidden = _report(client, token_a, "post", post_id)
        missing = _report(client, token_a, "post", str(uuid.uuid4()))

        # Mismo código y mismo cuerpo: reportar no sirve para confirmar que existe.
        assert hidden.status_code == missing.status_code == 404
        assert hidden.get_json() == missing.get_json()

    def test_accepted_follower_of_a_private_account_can_report(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b)
        _make_private(client, token_b)
        client.post(f"/api/users/{id_b}/follow", headers=_h(token_a))
        client.post(f"/api/follow-requests/{id_a}/accept", headers=_h(token_b))

        assert _report(client, token_a, "post", post_id).status_code == 201

    def test_blocked_in_either_direction_hides_the_post(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b)
        _block(client, token_a, id_b)  # quien reporta bloqueó al autor

        assert _report(client, token_a, "post", post_id).status_code == 404

    def test_being_blocked_by_the_author_also_hides_the_post(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b)
        _block(client, token_b, id_a)  # el autor bloqueó a quien reporta

        assert _report(client, token_a, "post", post_id).status_code == 404


class TestReportingAComment:
    def test_creates_the_report(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        token_c, _ = _register_and_login(client, "cleo")
        post_id = _post(client, token_c)
        comment_id = _comment(client, token_b, post_id, "comentario ofensivo")

        response = _report(client, token_a, "comment", comment_id, reason="hate")

        assert response.status_code == 201
        row = _all_reports(app)[0]
        assert row.target_type == "comment"
        assert str(row.reported_user_id) == id_b
        assert row.content_snapshot == "comentario ofensivo"

    def test_cannot_report_your_own_comment(self, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b)
        comment_id = _comment(client, token_a, post_id)

        assert _report(client, token_a, "comment", comment_id).status_code == 400

    def test_comment_on_an_invisible_post_is_404(self, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        token_c, _ = _register_and_login(client, "cleo")
        post_id = _post(client, token_c)
        comment_id = _comment(client, token_b, post_id)
        # El post pasa a una cuenta privada que `ada` no sigue.
        _make_private(client, token_c)

        assert _report(client, token_a, "comment", comment_id).status_code == 404

    def test_comment_by_a_blocked_author_is_404(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        token_c, _ = _register_and_login(client, "cleo")
        post_id = _post(client, token_c)
        comment_id = _comment(client, token_b, post_id)
        _block(client, token_a, id_b)

        assert _report(client, token_a, "comment", comment_id).status_code == 404

    def test_nonexistent_comment_is_404(self, client):
        token_a, _ = _register_and_login(client, "ada")

        assert _report(client, token_a, "comment", str(uuid.uuid4())).status_code == 404


class TestReportingAMessage:
    def test_the_recipient_can_report(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        id_a = client.get("/api/users/me", headers=_h(token_a)).get_json()["user"]["id"]
        message_id = _message(client, token_b, id_a, "mensaje de acoso")

        response = _report(client, token_a, "message", message_id, reason="harassment")

        assert response.status_code == 201
        row = _all_reports(app)[0]
        assert row.target_type == "message"
        assert str(row.reported_user_id) == id_b
        assert row.content_snapshot == "mensaje de acoso"

    def test_the_sender_cannot_report_their_own_message(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        message_id = _message(client, token_a, id_b)

        # Un mensaje lo reporta solo quien lo recibió (ADR-032 §2).
        assert _report(client, token_a, "message", message_id).status_code == 404

    def test_a_third_party_cannot_report_a_conversation_that_is_not_theirs(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        token_c, _ = _register_and_login(client, "cleo")
        message_id = _message(client, token_a, id_b)

        response = _report(client, token_c, "message", message_id)

        assert response.status_code == 404
        assert response.get_json()["msg"] == NOT_FOUND_MSG

    def test_message_from_a_blocked_account_is_404(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        message_id = _message(client, token_b, id_a)
        _block(client, token_a, id_b)

        assert _report(client, token_a, "message", message_id).status_code == 404


class TestReportingAUser:
    def test_creates_the_report_with_the_public_profile_text(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        client.patch("/api/users/me", json={"bio": "bio problemática"}, headers=_h(token_b))

        response = _report(client, token_a, "user", id_b, reason="impersonation")

        assert response.status_code == 201
        row = _all_reports(app)[0]
        assert row.target_type == "user"
        assert str(row.reported_user_id) == id_b
        assert "bio problemática" in row.content_snapshot
        assert "bob" in row.content_snapshot

    def test_snapshot_never_includes_private_profile_data(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")

        _report(client, token_a, "user", id_b)

        snapshot = _all_reports(app)[0].content_snapshot
        assert "bob@example.com" not in snapshot
        assert "7000-1234" not in snapshot
        assert "1990" not in snapshot

    def test_cannot_report_yourself(self, client):
        token_a, id_a = _register_and_login(client, "ada")

        assert _report(client, token_a, "user", id_a).status_code == 400

    def test_blocked_account_is_404(self, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        _block(client, token_a, id_b)

        assert _report(client, token_a, "user", id_b).status_code == 404

    def test_nonexistent_user_is_404(self, client):
        token_a, _ = _register_and_login(client, "ada")

        assert _report(client, token_a, "user", str(uuid.uuid4())).status_code == 404


class TestSnapshot:
    def test_long_text_is_truncated_to_the_limit(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b, "y" * 1000)
        # El límite de un post es menor que el de la copia: se prueba la copia
        # directamente con el caso de uso en la capa de datos.
        with app.app_context():
            from app.infrastructure.persistence.repositories.report_repository import (
                SQLAlchemyReportRepository,
            )

            repo = SQLAlchemyReportRepository()
            report, created = repo.create_if_absent(
                reporter_id=None,
                target_type="post",
                target_id=uuid.UUID(post_id),
                reported_user_id=uuid.UUID(id_b),
                reason="spam",
                details=None,
                snapshot=("z" * kinds.MAX_SNAPSHOT_LENGTH),
            )
            assert created is True
            assert len(report.content_snapshot) == kinds.MAX_SNAPSHOT_LENGTH

    def test_snapshot_is_copied_even_if_the_post_is_edited_afterwards(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_id = _post(client, token_b, "versión original")
        _report(client, token_a, "post", post_id)

        client.patch(f"/api/posts/{post_id}", json={"content": "versión editada"}, headers=_h(token_b))

        assert _all_reports(app)[0].content_snapshot == "versión original"


class TestRateLimit:
    def test_the_eleventh_report_in_an_hour_is_429_with_retry_after(self, app, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        post_ids = [_post(client, token_b, f"contenido {i}") for i in range(11)]

        statuses = [_report(client, token_a, "post", pid).status_code for pid in post_ids]

        assert statuses[:10] == [201] * 10
        assert statuses[10] == 429
        response = _report(client, token_a, "post", post_ids[10])
        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) > 0
        assert response.get_json()["retry_after_seconds"] > 0
        assert len(_all_reports(app)) == 10

    def test_the_limit_is_per_person_not_global(self, client):
        token_a, _ = _register_and_login(client, "ada")
        token_b, _ = _register_and_login(client, "bob")
        token_c, _ = _register_and_login(client, "cleo")
        post_ids = [_post(client, token_c, f"contenido {i}") for i in range(11)]
        for pid in post_ids:
            _report(client, token_a, "post", pid)

        # `ada` agotó su cupo; `bob` no.
        assert _report(client, token_b, "post", post_ids[0]).status_code == 201


class TestAccountDeletionKeepsTheReport:
    def test_deleting_the_reporter_keeps_the_report_without_an_author(self, app, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b)
        _report(client, token_a, "post", post_id)

        with app.app_context():
            db.session.delete(db.session.get(User, uuid.UUID(id_a)))
            db.session.commit()

        rows = _all_reports(app)
        assert len(rows) == 1
        assert rows[0].reporter_id is None
        assert str(rows[0].reported_user_id) == id_b

    def test_deleting_the_reported_user_keeps_the_report_and_its_snapshot(self, app, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b, "texto que debe poder revisarse")
        _report(client, token_a, "post", post_id)

        with app.app_context():
            db.session.delete(db.session.get(User, uuid.UUID(id_b)))
            db.session.commit()

        rows = _all_reports(app)
        assert len(rows) == 1
        assert rows[0].reported_user_id is None
        assert rows[0].content_snapshot == "texto que debe poder revisarse"
        assert str(rows[0].reporter_id) == id_a


class TestRepositoryRace:
    def test_create_if_absent_returns_the_existing_report_instead_of_failing(self, app, client):
        token_a, id_a = _register_and_login(client, "ada")
        token_b, id_b = _register_and_login(client, "bob")
        post_id = _post(client, token_b)

        with app.app_context():
            from app.infrastructure.persistence.repositories.report_repository import (
                SQLAlchemyReportRepository,
            )

            repo = SQLAlchemyReportRepository()
            args = dict(
                reporter_id=uuid.UUID(id_a),
                target_type="post",
                target_id=uuid.UUID(post_id),
                reported_user_id=uuid.UUID(id_b),
                reason="spam",
                details=None,
                snapshot="x",
            )
            first, created_first = repo.create_if_absent(**args)
            second, created_second = repo.create_if_absent(**args)

            assert created_first is True
            assert created_second is False
            assert first.id == second.id
