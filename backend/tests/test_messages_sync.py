# Pruebas de integración de la sincronización del chat (ADR-035-chat-sync.md)
# contra PostgreSQL real (ver conftest.py): envío idempotente con `client_id`,
# paginación hacia atrás (`before`) y recuperación tras perder la conexión
# (`after`). Los cursores son instantes (`created_at`), no ids.

import uuid

import pytest

from app.extensions import db
from app.infrastructure.persistence.models import Message
from app.infrastructure.persistence.repositories.message_repository import (
    SQLAlchemyMessageRepository,
)
from tests.test_messages import _auth_headers, _register_and_login


def _two_users(client):
    token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
    token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
    return token_a, id_a, token_b, id_b


def _send(client, token, to_id, content="hola", **extra):
    return client.post(
        f"/api/users/{to_id}/messages",
        json={"content": content, **extra},
        headers=_auth_headers(token),
    )


def _thread(client, token, other_id, query=""):
    response = client.get(
        f"/api/users/{other_id}/messages{query}", headers=_auth_headers(token)
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()


def _enc(instant):
    """Un instante ISO 8601 apto para query string (el '+' de la zona va escapado)."""
    return instant.replace("+", "%2B")


# ===========================================================================
# Envío idempotente
# ===========================================================================
class TestIdempotentSend:
    def test_first_send_is_201_and_returns_the_client_id(self, client):
        token_a, _, _, id_b = _two_users(client)

        response = _send(client, token_a, id_b, client_id="m-abc123")

        assert response.status_code == 201
        assert response.get_json()["message"]["client_id"] == "m-abc123"

    def test_retrying_with_the_same_client_id_returns_the_original_and_does_not_duplicate(
        self, app, client
    ):
        token_a, _, _, id_b = _two_users(client)
        first = _send(client, token_a, id_b, "una vez", client_id="m-same").get_json()["message"]

        retry = _send(client, token_a, id_b, "una vez", client_id="m-same")

        assert retry.status_code == 200
        assert retry.get_json()["message"]["id"] == first["id"]
        with app.app_context():
            assert db.session.query(Message).count() == 1

    def test_a_retry_with_different_text_still_returns_the_original(self, app, client):
        # El id manda: reintentar no es una forma de editar lo ya enviado.
        token_a, _, _, id_b = _two_users(client)
        _send(client, token_a, id_b, "original", client_id="m-x")

        retry = _send(client, token_a, id_b, "otro texto", client_id="m-x")

        assert retry.get_json()["message"]["content"] == "original"

    def test_two_senders_can_use_the_same_client_id(self, app, client):
        token_a, id_a, token_b, id_b = _two_users(client)

        from_a = _send(client, token_a, id_b, "de a", client_id="m-dup")
        from_b = _send(client, token_b, id_a, "de b", client_id="m-dup")

        assert from_a.status_code == from_b.status_code == 201
        with app.app_context():
            assert db.session.query(Message).count() == 2

    def test_without_client_id_every_send_creates_a_new_message(self, app, client):
        token_a, _, _, id_b = _two_users(client)

        assert _send(client, token_a, id_b, "x").status_code == 201
        assert _send(client, token_a, id_b, "x").status_code == 201

        with app.app_context():
            assert db.session.query(Message).count() == 2

    @pytest.mark.parametrize("bad", ["", "a" * 65, "con espacio", "emoji😀", 123, ["x"], {"a": 1}])
    def test_an_invalid_client_id_is_rejected(self, client, bad):
        token_a, _, _, id_b = _two_users(client)

        assert _send(client, token_a, id_b, client_id=bad).status_code == 400

    def test_a_retry_does_not_bypass_a_block(self, client):
        token_a, id_a, token_b, id_b = _two_users(client)
        _send(client, token_a, id_b, "antes", client_id="m-blk")
        client.post(
            "/api/users/me/blocks", json={"user_id": id_a}, headers=_auth_headers(token_b)
        )

        retry = _send(client, token_a, id_b, "antes", client_id="m-blk")

        # B bloqueó a A: para A, B "no existe" (ADR-029). El reintento no lo salta.
        assert retry.status_code == 404

    def test_the_losing_side_of_a_race_gets_the_winning_message(self, app, client):
        """Dos envíos simultáneos con el mismo client_id: el índice único rechaza el
        segundo INSERT y el repositorio devuelve el del primero, sin duplicar."""
        token_a, id_a, _, id_b = _two_users(client)
        with app.app_context():
            repository = SQLAlchemyMessageRepository()
            winner, created = repository.create_idempotent(
                uuid.UUID(id_a), uuid.UUID(id_b), "gana", "m-race"
            )
            assert created is True

            # Simula que la comprobación previa no vio al ganador todavía.
            real_find = repository._find_by_client_id
            calls = {"n": 0}

            def blind_first(sender_id, client_id):
                calls["n"] += 1
                return None if calls["n"] == 1 else real_find(sender_id, client_id)

            repository._find_by_client_id = blind_first

            loser, created = repository.create_idempotent(
                uuid.UUID(id_a), uuid.UUID(id_b), "pierde", "m-race"
            )

            assert created is False
            assert loser.id == winner.id
            assert loser.content == "gana"
            assert db.session.query(Message).count() == 1


# ===========================================================================
# Paginación y recuperación
# ===========================================================================
def _seed(client, token_a, id_b, count):
    for index in range(count):
        assert _send(client, token_a, id_b, f"mensaje {index:02d}").status_code == 201


class TestThreadPagination:
    def test_without_parameters_the_response_keeps_its_shape_and_adds_has_more(self, client):
        token_a, _, _, id_b = _two_users(client)
        _seed(client, token_a, id_b, 3)

        body = _thread(client, token_a, id_b)

        assert [m["content"] for m in body["messages"]] == [
            "mensaje 00", "mensaje 01", "mensaje 02",
        ]
        assert body["has_more"] is False

    def test_limit_returns_the_latest_messages_in_chronological_order(self, client):
        token_a, _, _, id_b = _two_users(client)
        _seed(client, token_a, id_b, 12)

        body = _thread(client, token_a, id_b, "?limit=5")

        assert [m["content"] for m in body["messages"]] == [f"mensaje {i:02d}" for i in range(7, 12)]
        assert body["has_more"] is True

    def test_before_walks_back_through_the_whole_history_without_gaps(self, client):
        token_a, _, _, id_b = _two_users(client)
        _seed(client, token_a, id_b, 12)

        seen = {}
        page = _thread(client, token_a, id_b, "?limit=5")
        for message in page["messages"]:
            seen[message["id"]] = message["content"]
        # Cada página se pide a partir del mensaje más antiguo ya visto.
        for _ in range(5):
            if not page["has_more"]:
                break
            oldest = page["messages"][0]["created_at"]
            page = _thread(client, token_a, id_b, f"?limit=5&before={_enc(oldest)}")
            for message in page["messages"]:
                seen[message["id"]] = message["content"]

        assert sorted(seen.values()) == [f"mensaje {i:02d}" for i in range(12)]
        assert page["has_more"] is False

    def test_after_returns_only_what_arrived_since(self, client):
        token_a, _, token_b, id_b = _two_users(client)
        _seed(client, token_a, id_b, 3)
        known = _thread(client, token_a, id_b)["messages"][-1]
        _send(client, token_a, id_b, "nuevo 1")
        _send(client, token_a, id_b, "nuevo 2")

        body = _thread(client, token_a, id_b, f"?after={_enc(known['created_at'])}")

        contents = [m["content"] for m in body["messages"]]
        # Es inclusivo (nunca se pierde un mensaje por empate de instante): el
        # cliente descarta lo que ya tiene por `id`.
        assert contents == ["mensaje 02", "nuevo 1", "nuevo 2"]
        assert body["has_more"] is False

    def test_after_pages_forward_when_many_arrived_while_offline(self, client):
        token_a, _, _, id_b = _two_users(client)
        _seed(client, token_a, id_b, 1)
        cursor = _thread(client, token_a, id_b)["messages"][-1]["created_at"]
        _seed(client, token_a, id_b, 7)

        collected = {}
        for _ in range(6):
            page = _thread(client, token_a, id_b, f"?limit=3&after={_enc(cursor)}")
            for message in page["messages"]:
                collected[message["id"]] = message["created_at"]
            cursor = page["messages"][-1]["created_at"]
            if not page["has_more"]:
                break

        assert len(collected) == 8  # el mensaje del cursor + los 7 nuevos

    def test_a_cursor_from_a_deleted_message_still_works(self, client):
        # Los ids no sirven como cursor porque el borrado es duro; los instantes sí.
        token_a, _, _, id_b = _two_users(client)
        _seed(client, token_a, id_b, 2)
        last = _thread(client, token_a, id_b)["messages"][-1]
        client.delete(f"/api/messages/{last['id']}", headers=_auth_headers(token_a))
        _send(client, token_a, id_b, "despues")

        body = _thread(client, token_a, id_b, f"?after={_enc(last['created_at'])}")

        assert [m["content"] for m in body["messages"]] == ["despues"]

    @pytest.mark.parametrize("query", ["?limit=0", "?limit=101", "?limit=abc", "?limit=-1", "?limit="])
    def test_an_invalid_limit_is_400(self, client, query):
        token_a, _, _, id_b = _two_users(client)

        response = client.get(f"/api/users/{id_b}/messages{query}", headers=_auth_headers(token_a))

        assert response.status_code == 400

    def test_the_maximum_limit_is_accepted(self, client):
        token_a, _, _, id_b = _two_users(client)

        assert _thread(client, token_a, id_b, "?limit=100")["messages"] == []

    @pytest.mark.parametrize(
        "query",
        [
            "?before=hoy",
            "?after=2026-10-02",  # sin hora ni zona
            "?after=2026-10-02T10:00:00",  # sin zona horaria
            "?before=2026-10-02T10:00:00%2B00:00&after=2026-10-02T10:00:00%2B00:00",
        ],
    )
    def test_invalid_cursors_are_400(self, client, query):
        token_a, _, _, id_b = _two_users(client)

        response = client.get(f"/api/users/{id_b}/messages{query}", headers=_auth_headers(token_a))

        assert response.status_code == 400

    def test_new_incoming_messages_are_marked_as_read_when_fetched_with_after(self, client):
        token_a, _, token_b, id_b = _two_users(client)
        # B abre el chat (sin mensajes), luego A escribe.
        id_a = client.get("/api/users/me", headers=_auth_headers(token_a)).get_json()["user"]["id"]
        _send(client, token_a, id_b, "primero")
        since = _thread(client, token_b, id_a)["messages"][-1]["created_at"]
        _send(client, token_a, id_b, "segundo")

        fetched = _thread(client, token_b, id_a, f"?after={_enc(since)}")

        assert fetched["messages"][-1]["content"] == "segundo"
        conversations = client.get("/api/conversations", headers=_auth_headers(token_b)).get_json()
        assert conversations["conversations"][0]["unread_count"] == 0

    def test_a_third_person_cannot_read_someone_elses_conversation(self, client):
        token_a, _, _, id_b = _two_users(client)
        token_c, id_c = _register_and_login(client, username="user_c", email="c@example.com")
        id_a = client.get("/api/users/me", headers=_auth_headers(token_a)).get_json()["user"]["id"]
        _seed(client, token_a, id_b, 3)

        # C pide "su" hilo con A: solo ve lo que C y A se han escrito (nada).
        body = _thread(client, token_c, id_a)

        assert body["messages"] == []
        assert id_c != id_a

    def test_a_blocked_thread_is_not_found(self, client):
        token_a, id_a, token_b, id_b = _two_users(client)
        _seed(client, token_a, id_b, 2)
        client.post("/api/users/me/blocks", json={"user_id": id_b}, headers=_auth_headers(token_a))

        response = client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))

        assert response.status_code == 404
        assert response.get_json()["msg"] == "Usuario no encontrado"
