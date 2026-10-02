# Pruebas de integración de POST/GET /api/users/<id>/messages,
# GET /api/conversations (ADR-013-messages-minimal-model.md),
# DELETE /api/messages/<id> y POST/GET /api/users/<id>/typing
# (ADR-014-messages-ux-improvements.md) contra PostgreSQL 16 real
# (thers_test, ver conftest.py) -- no mocks. El indicador de "escribiendo"
# vive en memoria del proceso (no en la base), así que sus pruebas no
# dependen de `_clean_tables` de conftest.py.

from tests.conftest import mark_email_verified

VALID_PASSWORD = "secretpass"


def _register_payload(**overrides):
    payload = {
        "name": "Ada Lovelace",
        "username": "ada_lovelace",
        "email": "ada@example.com",
        "phone": "7000-1234",
        "country_code": "+503",
        "birth_date": "1990-01-01",
        "password": VALID_PASSWORD,
        "confirm_password": VALID_PASSWORD,
    }
    payload.update(overrides)
    return payload


def _register_and_login(client, **overrides):
    payload = _register_payload(**overrides)
    res = client.post("/api/register", json=payload)
    user_id = res.get_json()["user"]["id"]
    mark_email_verified(user_id)
    res = client.post(
        "/api/login", json={"email": payload["email"], "password": VALID_PASSWORD}
    )
    return res.get_json()["token"], user_id


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestSendMessage:
    def test_send_message_returns_201_with_message(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.post(
            f"/api/users/{id_b}/messages", json={"content": "Hola!"}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 201
        message = response.get_json()["message"]
        assert message["content"] == "Hola!"
        assert message["recipient_id"] == id_b
        assert message["read"] is False

    def test_send_message_without_token_returns_401(self, client):
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.post(f"/api/users/{id_b}/messages", json={"content": "Hola!"})

        assert response.status_code == 401

    def test_send_message_to_self_returns_400(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.post(
            f"/api/users/{id_a}/messages", json={"content": "Hola!"}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 400

    def test_send_message_to_nonexistent_user_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.post(
            f"/api/users/{fake_id}/messages", json={"content": "Hola!"}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 404

    def test_send_message_malformed_id_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.post(
            "/api/users/not-a-uuid/messages", json={"content": "Hola!"}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 404

    def test_send_message_without_content_returns_400(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.post(
            f"/api/users/{id_b}/messages", json={"content": ""}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 400

    def test_send_message_without_json_body_returns_400(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.post(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))

        assert response.status_code == 400

    def test_repeated_messages_are_not_deduplicated(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        client.post(f"/api/users/{id_b}/messages", json={"content": "hola"}, headers=_auth_headers(token_a))
        client.post(f"/api/users/{id_b}/messages", json={"content": "hola"}, headers=_auth_headers(token_a))

        response = client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))
        assert len(response.get_json()["messages"]) == 2


class TestListThread:
    def test_without_token_returns_401(self, client):
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.get(f"/api/users/{id_b}/messages")

        assert response.status_code == 401

    def test_empty_thread_when_no_messages(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"messages": []}

    def test_nonexistent_user_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.get(f"/api/users/{fake_id}/messages", headers=_auth_headers(token_a))

        assert response.status_code == 404

    def test_thread_includes_both_directions_in_chronological_order(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/messages", json={"content": "uno"}, headers=_auth_headers(token_a))
        client.post(f"/api/users/{id_a}/messages", json={"content": "dos"}, headers=_auth_headers(token_b))

        response = client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))

        messages = response.get_json()["messages"]
        assert [m["content"] for m in messages] == ["uno", "dos"]

    def test_thread_is_isolated_from_other_users(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        _, id_c = _register_and_login(client, username="user_c", email="c@example.com")
        client.post(f"/api/users/{id_c}/messages", json={"content": "para c"}, headers=_auth_headers(token_a))

        response = client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))

        assert response.get_json()["messages"] == []

    def test_opening_thread_marks_received_messages_as_read(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/messages", json={"content": "hola"}, headers=_auth_headers(token_a))

        client.get(f"/api/users/{id_a}/messages", headers=_auth_headers(token_b))
        response = client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))

        assert response.get_json()["messages"][0]["read"] is True

    def test_opening_thread_does_not_mark_sent_messages_as_read(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/messages", json={"content": "hola"}, headers=_auth_headers(token_a))

        response = client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))

        assert response.get_json()["messages"][0]["read"] is False


class TestListConversations:
    def test_without_token_returns_401(self, client):
        response = client.get("/api/conversations")
        assert response.status_code == 401

    def test_empty_when_no_conversations(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.get("/api/conversations", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"conversations": []}

    def test_lists_conversation_with_last_message_and_unread_count(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_a}/messages", json={"content": "uno"}, headers=_auth_headers(token_b))
        client.post(f"/api/users/{id_a}/messages", json={"content": "dos"}, headers=_auth_headers(token_b))

        response = client.get("/api/conversations", headers=_auth_headers(token_a))

        conversations = response.get_json()["conversations"]
        assert len(conversations) == 1
        assert conversations[0]["user"]["username"] == "user_b"
        assert conversations[0]["last_message"]["content"] == "dos"
        assert conversations[0]["unread_count"] == 2

    def test_reading_thread_clears_unread_count(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_a}/messages", json={"content": "hola"}, headers=_auth_headers(token_b))

        client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))
        response = client.get("/api/conversations", headers=_auth_headers(token_a))

        assert response.get_json()["conversations"][0]["unread_count"] == 0

    def test_most_recent_conversation_first(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        _, id_c = _register_and_login(client, username="user_c", email="c@example.com")
        client.post(f"/api/users/{id_b}/messages", json={"content": "a b"}, headers=_auth_headers(token_a))
        client.post(f"/api/users/{id_c}/messages", json={"content": "a c"}, headers=_auth_headers(token_a))

        response = client.get("/api/conversations", headers=_auth_headers(token_a))

        conversations = response.get_json()["conversations"]
        assert [c["user"]["username"] for c in conversations] == ["user_c", "user_b"]

    def test_does_not_include_other_peoples_conversations(self, client):
        _, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        token_c, _ = _register_and_login(client, username="user_c", email="c@example.com")
        client.post(f"/api/users/{id_a}/messages", json={"content": "hola"}, headers=_auth_headers(token_b))

        response = client.get("/api/conversations", headers=_auth_headers(token_c))

        assert response.get_json()["conversations"] == []


class TestReadFlagReflectsPreReadState:
    """ADR-014: `read` en la respuesta de GET .../messages refleja el
    estado ANTES de que esta misma llamada marque como leído, no después."""

    def test_first_view_shows_unread_false_for_just_marked_messages(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/messages", json={"content": "hola"}, headers=_auth_headers(token_a))

        response = client.get(f"/api/users/{id_a}/messages", headers=_auth_headers(token_b))

        assert response.get_json()["messages"][0]["read"] is False

    def test_second_view_shows_read_true(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/messages", json={"content": "hola"}, headers=_auth_headers(token_a))
        client.get(f"/api/users/{id_a}/messages", headers=_auth_headers(token_b))

        response = client.get(f"/api/users/{id_a}/messages", headers=_auth_headers(token_b))

        assert response.get_json()["messages"][0]["read"] is True


class TestDeleteMessage:
    def _send(self, client, token, recipient_id, content="hola"):
        res = client.post(
            f"/api/users/{recipient_id}/messages", json={"content": content}, headers=_auth_headers(token)
        )
        return res.get_json()["message"]["id"]

    def test_sender_can_delete_own_message(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        response = client.delete(f"/api/messages/{message_id}", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}

    def test_deleted_message_disappears_from_thread(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        client.delete(f"/api/messages/{message_id}", headers=_auth_headers(token_a))
        response = client.get(f"/api/users/{id_b}/messages", headers=_auth_headers(token_a))

        assert response.get_json()["messages"] == []

    def test_recipient_cannot_delete_a_message_sent_to_them(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        response = client.delete(f"/api/messages/{message_id}", headers=_auth_headers(token_b))

        assert response.status_code == 404

    def test_nonexistent_message_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.delete(f"/api/messages/{fake_id}", headers=_auth_headers(token_a))

        assert response.status_code == 404

    def test_without_token_returns_401(self, client):
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.delete(f"/api/messages/{fake_id}")

        assert response.status_code == 401


class TestTypingIndicator:
    def test_no_ping_means_not_typing(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.get(f"/api/users/{id_b}/typing", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"typing": False}

    def test_ping_makes_recipient_see_typing_true(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        ping = client.post(f"/api/users/{id_b}/typing", headers=_auth_headers(token_a))
        response = client.get(f"/api/users/{id_a}/typing", headers=_auth_headers(token_b))

        assert ping.status_code == 204
        assert response.get_json() == {"typing": True}

    def test_ping_does_not_make_sender_see_typing_from_themselves(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/typing", headers=_auth_headers(token_a))

        response = client.get(f"/api/users/{id_b}/typing", headers=_auth_headers(token_a))

        assert response.get_json() == {"typing": False}

    def test_ping_to_nonexistent_user_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.post(f"/api/users/{fake_id}/typing", headers=_auth_headers(token_a))

        assert response.status_code == 404

    def test_ping_without_token_returns_401(self, client):
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.post(f"/api/users/{id_b}/typing")

        assert response.status_code == 401

    def test_status_without_token_returns_401(self, client):
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.get(f"/api/users/{id_b}/typing")

        assert response.status_code == 401


class TestUpdateMessage:
    # PATCH /api/messages/<message_id> (ADR-021-content-editing.md).

    def _send(self, client, token, recipient_id, content="original"):
        res = client.post(
            f"/api/users/{recipient_id}/messages",
            json={"content": content},
            headers=_auth_headers(token),
        )
        return res.get_json()["message"]["id"]

    def test_sender_can_edit_own_message(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        response = client.patch(
            f"/api/messages/{message_id}",
            json={"content": "corregido"},
            headers=_auth_headers(token_a),
        )

        assert response.status_code == 200
        message = response.get_json()["message"]
        assert message["content"] == "corregido"
        assert message["edited"] is True

    def test_a_message_that_was_never_edited_reports_edited_false(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        self._send(client, token_a, id_b)

        thread = client.get(
            f"/api/users/{id_b}/messages", headers=_auth_headers(token_a)
        ).get_json()["messages"]

        assert thread[0]["edited"] is False

    def test_edited_content_appears_in_the_thread_for_both_sides(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        client.patch(
            f"/api/messages/{message_id}",
            json={"content": "lo que quise decir"},
            headers=_auth_headers(token_a),
        )

        for token, other_id in ((token_a, id_b), (token_b, id_a)):
            thread = client.get(
                f"/api/users/{other_id}/messages", headers=_auth_headers(token)
            ).get_json()["messages"]
            assert thread[0]["content"] == "lo que quise decir"
            assert thread[0]["edited"] is True

    def test_recipient_cannot_edit_a_message_sent_to_them(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b, content="lo que A dijo")

        response = client.patch(
            f"/api/messages/{message_id}",
            json={"content": "lo que B quiere que A haya dicho"},
            headers=_auth_headers(token_b),
        )

        # Mismo 404 que un mensaje inexistente -- editar es solo de quien lo
        # mandó, igual que borrar (ADR-014/ADR-021 §Seguridad).
        assert response.status_code == 404
        thread = client.get(
            f"/api/users/{id_a}/messages", headers=_auth_headers(token_b)
        ).get_json()["messages"]
        assert thread[0]["content"] == "lo que A dijo"

    def test_nonexistent_message_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.patch(
            f"/api/messages/{fake_id}", json={"content": "nada"}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 404

    def test_edit_message_without_token_returns_401(self, client):
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.patch(f"/api/messages/{fake_id}", json={"content": "sin token"})

        assert response.status_code == 401

    def test_edit_message_empty_body_returns_400(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        response = client.patch(
            f"/api/messages/{message_id}", json={}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 400

    def test_edit_message_empty_content_returns_400(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        response = client.patch(
            f"/api/messages/{message_id}", json={"content": " "}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 400

    def test_edit_message_over_max_length_returns_400(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        response = client.patch(
            f"/api/messages/{message_id}",
            json={"content": "x" * 2001},
            headers=_auth_headers(token_a),
        )

        assert response.status_code == 400

    def test_edit_message_trims_surrounding_whitespace(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        response = client.patch(
            f"/api/messages/{message_id}",
            json={"content": "   con espacios   "},
            headers=_auth_headers(token_a),
        )

        assert response.get_json()["message"]["content"] == "con espacios"

    def test_editing_a_read_message_does_not_make_it_unread_again(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)
        # B abre el hilo: el mensaje queda marcado como leído (ADR-013).
        client.get(f"/api/users/{id_a}/messages", headers=_auth_headers(token_b))

        client.patch(
            f"/api/messages/{message_id}",
            json={"content": "editado después de leído"},
            headers=_auth_headers(token_a),
        )

        # `read` sigue en true: editar no devuelve el mensaje a no leído
        # (ADR-021 §Decisión) -- el separador de no-leídos no se reordena.
        thread = client.get(
            f"/api/users/{id_b}/messages", headers=_auth_headers(token_a)
        ).get_json()["messages"]
        assert thread[0]["read"] is True

    def test_edit_message_cannot_change_recipient_or_read_state(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        _, id_c = _register_and_login(client, username="user_c", email="c@example.com")
        message_id = self._send(client, token_a, id_b)

        response = client.patch(
            f"/api/messages/{message_id}",
            json={"content": "editado", "recipient_id": id_c, "read": True},
            headers=_auth_headers(token_a),
        )

        message = response.get_json()["message"]
        # Ni el destinatario ni el estado de lectura se dejan pisar desde el
        # body (ADR-021 §Seguridad).
        assert message["recipient_id"] == id_b
        assert message["read"] is False
        assert client.get(
            f"/api/users/{id_c}/messages", headers=_auth_headers(token_a)
        ).get_json()["messages"] == []

    def test_conversation_preview_shows_the_edited_content(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        client.patch(
            f"/api/messages/{message_id}",
            json={"content": "texto final"},
            headers=_auth_headers(token_a),
        )
        conversations = client.get(
            "/api/conversations", headers=_auth_headers(token_a)
        ).get_json()["conversations"]

        # El resumen de la conversación muestra el texto vigente, no el que se
        # mandó primero. No lleva `edited` -- es una vista derivada, no el
        # mensaje (ADR-021 §Contrato API).
        assert conversations[0]["last_message"]["content"] == "texto final"

    def test_deleted_message_cannot_be_edited(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        message_id = self._send(client, token_a, id_b)

        client.delete(f"/api/messages/{message_id}", headers=_auth_headers(token_a))
        response = client.patch(
            f"/api/messages/{message_id}", json={"content": "zombi"}, headers=_auth_headers(token_a)
        )

        assert response.status_code == 404
