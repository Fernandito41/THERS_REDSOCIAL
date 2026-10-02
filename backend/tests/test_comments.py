# Pruebas de integración de POST/GET /api/posts/<id>/comments y de la
# extensión de GET/POST /api/posts (ADR-006-comments-minimal-model.md)
# contra PostgreSQL 16 real (thers_test, ver conftest.py) -- no mocks.

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
    register_response = client.post("/api/register", json=payload)
    # Verificación directa en la base -- ADR-011-mandatory-email-verification.md
    # bloquea login() para cuentas sin verificar; el código real de
    # verificación no es observable por un test (ver conftest.mark_email_verified).
    mark_email_verified(register_response.get_json()["user"]["id"])
    res = client.post(
        "/api/login", json={"email": payload["email"], "password": VALID_PASSWORD}
    )
    return res.get_json()["token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _create_post(client, token, content="post real"):
    response = client.post(
        "/api/posts", json={"content": content}, headers=_auth_headers(token)
    )
    return response.get_json()["post"]["id"]


class TestCreateComment:
    def test_create_comment_persists_and_returns_public_author(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "muy bueno tu post"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 201
        body = response.get_json()["comment"]
        assert body["content"] == "muy bueno tu post"
        assert body["post_id"] == post_id
        assert body["author"]["username"] == "ada_lovelace"
        assert "id" in body
        assert "created_at" in body
        assert "email" not in body["author"]
        assert "password_hash" not in body["author"]

    def test_create_comment_without_token_returns_401(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(f"/api/posts/{post_id}/comments", json={"content": "hola"})

        assert response.status_code == 401

    def test_create_comment_empty_body_returns_400(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(
            f"/api/posts/{post_id}/comments", json={}, headers=_auth_headers(token)
        )

        assert response.status_code == 400

    def test_create_comment_empty_content_returns_400(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "   "},
            headers=_auth_headers(token),
        )

        assert response.status_code == 400

    def test_create_comment_over_max_length_returns_400(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "a" * 1001},
            headers=_auth_headers(token),
        )

        assert response.status_code == 400

    def test_create_comment_at_max_length_is_accepted(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "a" * 1000},
            headers=_auth_headers(token),
        )

        assert response.status_code == 201

    def test_create_comment_trims_surrounding_whitespace(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "  con espacios  "},
            headers=_auth_headers(token),
        )

        assert response.get_json()["comment"]["content"] == "con espacios"

    def test_create_comment_ignores_unwhitelisted_fields(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={
                "content": "comentario real",
                "author_id": "00000000-0000-0000-0000-000000000000",
                "id": "11111111-1111-1111-1111-111111111111",
            },
            headers=_auth_headers(token),
        )

        assert response.status_code == 201
        body = response.get_json()["comment"]
        assert body["id"] != "11111111-1111-1111-1111-111111111111"
        assert body["author"]["username"] == "ada_lovelace"

    def test_comment_on_nonexistent_post_returns_404(self, client):
        token = _register_and_login(client)
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.post(
            f"/api/posts/{fake_id}/comments",
            json={"content": "hola"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 404

    def test_comment_on_malformed_post_id_returns_404(self, client):
        token = _register_and_login(client)

        response = client.post(
            "/api/posts/not-a-uuid/comments",
            json={"content": "hola"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 404

    def test_any_authenticated_user_can_comment_on_another_users_post(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)

        response = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "de B"},
            headers=_auth_headers(token_b),
        )

        assert response.status_code == 201


class TestListComments:
    def test_list_comments_without_token_returns_401(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.get(f"/api/posts/{post_id}/comments")

        assert response.status_code == 401

    def test_list_comments_returns_oldest_first(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "primero"},
            headers=_auth_headers(token),
        )
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "segundo"},
            headers=_auth_headers(token),
        )

        response = client.get(f"/api/posts/{post_id}/comments", headers=_auth_headers(token))

        assert response.status_code == 200
        contents = [c["content"] for c in response.get_json()["comments"]]
        assert contents.index("primero") < contents.index("segundo")

    def test_list_comments_empty_returns_empty_list(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.get(f"/api/posts/{post_id}/comments", headers=_auth_headers(token))

        assert response.status_code == 200
        assert response.get_json()["comments"] == []

    def test_list_comments_on_nonexistent_post_returns_404(self, client):
        token = _register_and_login(client)
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.get(f"/api/posts/{fake_id}/comments", headers=_auth_headers(token))

        assert response.status_code == 404

    def test_list_comments_only_shows_comments_for_that_post(self, client):
        token = _register_and_login(client)
        post_a = _create_post(client, token, content="post A")
        post_b = _create_post(client, token, content="post B")
        client.post(
            f"/api/posts/{post_a}/comments",
            json={"content": "en A"},
            headers=_auth_headers(token),
        )
        client.post(
            f"/api/posts/{post_b}/comments",
            json={"content": "en B"},
            headers=_auth_headers(token),
        )

        response = client.get(f"/api/posts/{post_a}/comments", headers=_auth_headers(token))

        contents = [c["content"] for c in response.get_json()["comments"]]
        assert contents == ["en A"]


class TestListPostsWithComments:
    def test_new_post_has_zero_comments(self, client):
        token = _register_and_login(client)

        response = client.post(
            "/api/posts", json={"content": "hola"}, headers=_auth_headers(token)
        )

        assert response.get_json()["post"]["comments_count"] == 0

    def test_list_posts_reflects_comments_count(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "uno"},
            headers=_auth_headers(token),
        )
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "dos"},
            headers=_auth_headers(token),
        )

        response = client.get("/api/posts", headers=_auth_headers(token))

        post = next(p for p in response.get_json()["posts"] if p["id"] == post_id)
        assert post["comments_count"] == 2


class TestDeleteComment:
    # DELETE /api/comments/<comment_id> (ADR-016-comment-deletion.md).

    def _post_and_comment(self, client, post_author_token, commenter_token, content="un comentario"):
        post_id = client.post(
            "/api/posts", json={"content": "post"}, headers=_auth_headers(post_author_token)
        ).get_json()["post"]["id"]
        comment_id = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": content},
            headers=_auth_headers(commenter_token),
        ).get_json()["comment"]["id"]
        return post_id, comment_id

    def test_author_can_delete_their_own_comment(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        _, comment_id = self._post_and_comment(client, token_a, token_b)

        response = client.delete(f"/api/comments/{comment_id}", headers=_auth_headers(token_b))

        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}

    def test_deleted_comment_disappears_from_thread_and_count(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id, comment_id = self._post_and_comment(client, token_a, token_b)

        client.delete(f"/api/comments/{comment_id}", headers=_auth_headers(token_b))

        comments = client.get(
            f"/api/posts/{post_id}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]
        assert comments == []
        posts = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]
        assert posts[0]["comments_count"] == 0

    def test_only_the_deleted_comment_is_removed(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id, first_id = self._post_and_comment(client, token_a, token_b, "primero")
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "segundo"},
            headers=_auth_headers(token_b),
        )

        client.delete(f"/api/comments/{first_id}", headers=_auth_headers(token_b))

        comments = client.get(
            f"/api/posts/{post_id}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]
        assert [c["content"] for c in comments] == ["segundo"]

    def test_another_user_cannot_delete_someone_elses_comment(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id, comment_id = self._post_and_comment(client, token_a, token_b)

        response = client.delete(f"/api/comments/{comment_id}", headers=_auth_headers(token_a))

        # Mismo 404 que un comentario inexistente (ADR-016 §Seguridad) --
        # incluso siendo A el dueño del post, no puede borrar el de B.
        assert response.status_code == 404
        comments = client.get(
            f"/api/posts/{post_id}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]
        assert len(comments) == 1

    def test_nonexistent_comment_returns_404(self, client):
        token = _register_and_login(client)

        response = client.delete(
            "/api/comments/00000000-0000-0000-0000-000000000000",
            headers=_auth_headers(token),
        )

        assert response.status_code == 404

    def test_malformed_comment_id_returns_404(self, client):
        token = _register_and_login(client)

        response = client.delete("/api/comments/no-es-un-uuid", headers=_auth_headers(token))

        assert response.status_code == 404

    def test_delete_comment_without_token_returns_401(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        _, comment_id = self._post_and_comment(client, token_a, token_b)

        response = client.delete(f"/api/comments/{comment_id}")

        assert response.status_code == 401

    def test_deleting_twice_returns_404_the_second_time(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        _, comment_id = self._post_and_comment(client, token_a, token_b)

        client.delete(f"/api/comments/{comment_id}", headers=_auth_headers(token_b))
        response = client.delete(f"/api/comments/{comment_id}", headers=_auth_headers(token_b))

        assert response.status_code == 404

    def test_deleting_a_comment_does_not_delete_the_post(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id, comment_id = self._post_and_comment(client, token_a, token_b)

        client.delete(f"/api/comments/{comment_id}", headers=_auth_headers(token_b))

        posts = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]
        assert [p["id"] for p in posts] == [post_id]


class TestUpdateComment:
    # PATCH /api/comments/<comment_id> (ADR-017-content-editing.md).

    def _post_and_comment(self, client, post_author_token, commenter_token, content="original"):
        post_id = client.post(
            "/api/posts", json={"content": "post"}, headers=_auth_headers(post_author_token)
        ).get_json()["post"]["id"]
        comment_id = client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": content},
            headers=_auth_headers(commenter_token),
        ).get_json()["comment"]["id"]
        return post_id, comment_id

    def test_author_can_edit_their_own_comment(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        _, comment_id = self._post_and_comment(client, token_a, token_b)

        response = client.patch(
            f"/api/comments/{comment_id}",
            json={"content": "ya lo corregí"},
            headers=_auth_headers(token_b),
        )

        assert response.status_code == 200
        comment = response.get_json()["comment"]
        assert comment["content"] == "ya lo corregí"
        assert comment["edited"] is True

    def test_a_comment_that_was_never_edited_reports_edited_false(self, client):
        token = _register_and_login(client)
        post_id, comment_id = self._post_and_comment(client, token, token)

        thread = client.get(
            f"/api/posts/{post_id}/comments", headers=_auth_headers(token)
        ).get_json()["comments"]

        assert thread[0]["edited"] is False

    def test_edited_content_appears_in_the_thread(self, client):
        token = _register_and_login(client)
        post_id, comment_id = self._post_and_comment(client, token, token)

        client.patch(
            f"/api/comments/{comment_id}",
            json={"content": "texto final"},
            headers=_auth_headers(token),
        )
        thread = client.get(
            f"/api/posts/{post_id}/comments", headers=_auth_headers(token)
        ).get_json()["comments"]

        assert thread[0]["content"] == "texto final"
        assert thread[0]["edited"] is True

    def test_another_user_cannot_edit_someone_elses_comment(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id, comment_id = self._post_and_comment(
            client, token_a, token_b, content="comentario de B"
        )

        response = client.patch(
            f"/api/comments/{comment_id}",
            json={"content": "editado por A"},
            headers=_auth_headers(token_a),
        )

        # El dueño de la publicación tampoco puede editar comentarios ajenos
        # en ella -- mismo criterio que el borrado (ADR-016/ADR-017 §Seguridad).
        assert response.status_code == 404
        thread = client.get(
            f"/api/posts/{post_id}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]
        assert thread[0]["content"] == "comentario de B"

    def test_nonexistent_comment_returns_404(self, client):
        token = _register_and_login(client)

        response = client.patch(
            "/api/comments/00000000-0000-0000-0000-000000000000",
            json={"content": "nada"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 404

    def test_edit_comment_without_token_returns_401(self, client):
        token = _register_and_login(client)
        _, comment_id = self._post_and_comment(client, token, token)

        response = client.patch(f"/api/comments/{comment_id}", json={"content": "sin token"})

        assert response.status_code == 401

    def test_edit_comment_empty_body_returns_400(self, client):
        token = _register_and_login(client)
        _, comment_id = self._post_and_comment(client, token, token)

        response = client.patch(
            f"/api/comments/{comment_id}", json={}, headers=_auth_headers(token)
        )

        assert response.status_code == 400

    def test_edit_comment_empty_content_returns_400(self, client):
        token = _register_and_login(client)
        _, comment_id = self._post_and_comment(client, token, token)

        response = client.patch(
            f"/api/comments/{comment_id}", json={"content": "  "}, headers=_auth_headers(token)
        )

        assert response.status_code == 400

    def test_edit_comment_over_max_length_returns_400(self, client):
        token = _register_and_login(client)
        _, comment_id = self._post_and_comment(client, token, token)

        response = client.patch(
            f"/api/comments/{comment_id}",
            json={"content": "x" * 1001},
            headers=_auth_headers(token),
        )

        # Mismo validador (y mismo límite de 1000, menor que el de posts) que
        # crear un comentario -- domain/comments/validators.py.
        assert response.status_code == 400

    def test_edit_comment_trims_surrounding_whitespace(self, client):
        token = _register_and_login(client)
        _, comment_id = self._post_and_comment(client, token, token)

        response = client.patch(
            f"/api/comments/{comment_id}",
            json={"content": "   con espacios   "},
            headers=_auth_headers(token),
        )

        assert response.get_json()["comment"]["content"] == "con espacios"

    def test_edit_comment_cannot_move_it_to_another_post(self, client):
        token = _register_and_login(client)
        post_id, comment_id = self._post_and_comment(client, token, token)
        other_post_id = client.post(
            "/api/posts", json={"content": "otro post"}, headers=_auth_headers(token)
        ).get_json()["post"]["id"]

        response = client.patch(
            f"/api/comments/{comment_id}",
            json={"content": "editado", "post_id": other_post_id},
            headers=_auth_headers(token),
        )

        # `post_id` no está en la whitelist del body (ADR-017 §Seguridad).
        assert response.get_json()["comment"]["post_id"] == post_id
        assert client.get(
            f"/api/posts/{other_post_id}/comments", headers=_auth_headers(token)
        ).get_json()["comments"] == []

    def test_editing_a_comment_does_not_change_the_count(self, client):
        token = _register_and_login(client)
        post_id, comment_id = self._post_and_comment(client, token, token)

        client.patch(
            f"/api/comments/{comment_id}",
            json={"content": "editado"},
            headers=_auth_headers(token),
        )
        feed = client.get("/api/posts", headers=_auth_headers(token)).get_json()["posts"]

        # Editar no suma ni resta: `comments_count` sigue en 1 (ADR-017).
        assert feed[0]["comments_count"] == 1

    def test_editing_a_comment_does_not_create_a_new_notification(self, client):
        # La notificación "comentó tu publicación" (ADR-008) se emite al crear
        # el comentario; editarlo no es un evento social nuevo (ADR-017).
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        _, comment_id = self._post_and_comment(client, token_a, token_b)
        before = len(
            client.get("/api/notifications", headers=_auth_headers(token_a))
            .get_json()["notifications"]
        )

        client.patch(
            f"/api/comments/{comment_id}",
            json={"content": "editado"},
            headers=_auth_headers(token_b),
        )

        after = len(
            client.get("/api/notifications", headers=_auth_headers(token_a))
            .get_json()["notifications"]
        )
        assert after == before

    def test_deleted_comment_cannot_be_edited(self, client):
        token = _register_and_login(client)
        _, comment_id = self._post_and_comment(client, token, token)

        client.delete(f"/api/comments/{comment_id}", headers=_auth_headers(token))
        response = client.patch(
            f"/api/comments/{comment_id}", json={"content": "zombi"}, headers=_auth_headers(token)
        )

        assert response.status_code == 404
