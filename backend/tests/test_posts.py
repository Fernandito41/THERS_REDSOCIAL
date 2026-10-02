# Pruebas de integración de POST/GET /api/posts (ADR-004-posts-minimal-model.md)
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
    mark_email_verified(register_response.get_json()["user"]["id"])
    res = client.post(
        "/api/login", json={"email": payload["email"], "password": VALID_PASSWORD}
    )
    return res.get_json()["token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestCreatePost:
    def test_create_post_persists_and_returns_public_author(self, client):
        token = _register_and_login(client)

        response = client.post(
            "/api/posts",
            json={"content": "Mi primer post real"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 201
        body = response.get_json()["post"]
        assert body["content"] == "Mi primer post real"
        assert body["author"]["username"] == "ada_lovelace"
        assert body["author"]["name"] == "Ada Lovelace"
        assert "id" in body
        assert "created_at" in body
        # nunca expone datos privados del autor
        assert "email" not in body["author"]
        assert "password" not in body["author"]
        assert "password_hash" not in body["author"]

    def test_create_post_without_token_returns_401(self, client):
        response = client.post("/api/posts", json={"content": "hola"})

        assert response.status_code == 401

    def test_create_post_empty_body_returns_400(self, client):
        token = _register_and_login(client)

        response = client.post("/api/posts", json={}, headers=_auth_headers(token))

        assert response.status_code == 400

    def test_create_post_empty_content_returns_400(self, client):
        token = _register_and_login(client)

        response = client.post(
            "/api/posts", json={"content": "   "}, headers=_auth_headers(token)
        )

        assert response.status_code == 400

    def test_create_post_over_max_length_returns_400(self, client):
        token = _register_and_login(client)

        response = client.post(
            "/api/posts",
            json={"content": "a" * 2001},
            headers=_auth_headers(token),
        )

        assert response.status_code == 400

    def test_create_post_at_max_length_is_accepted(self, client):
        token = _register_and_login(client)

        response = client.post(
            "/api/posts",
            json={"content": "a" * 2000},
            headers=_auth_headers(token),
        )

        assert response.status_code == 201

    def test_create_post_trims_surrounding_whitespace(self, client):
        token = _register_and_login(client)

        response = client.post(
            "/api/posts",
            json={"content": "  con espacios  "},
            headers=_auth_headers(token),
        )

        assert response.get_json()["post"]["content"] == "con espacios"

    def test_create_post_ignores_unwhitelisted_fields(self, client):
        # Mismo principio anti mass-assignment que PATCH /api/users/me
        # (ADR-003 §Seguridad) -- author_id/id nunca se leen del body.
        token = _register_and_login(client)

        response = client.post(
            "/api/posts",
            json={
                "content": "post real",
                "author_id": "00000000-0000-0000-0000-000000000000",
                "id": "11111111-1111-1111-1111-111111111111",
            },
            headers=_auth_headers(token),
        )

        assert response.status_code == 201
        body = response.get_json()["post"]
        assert body["id"] != "11111111-1111-1111-1111-111111111111"
        assert body["author"]["username"] == "ada_lovelace"


class TestListPosts:
    def test_list_posts_without_token_returns_401(self, client):
        response = client.get("/api/posts")

        assert response.status_code == 401

    def test_list_posts_returns_most_recent_first(self, client):
        token = _register_and_login(client)
        client.post(
            "/api/posts", json={"content": "primero"}, headers=_auth_headers(token)
        )
        client.post(
            "/api/posts", json={"content": "segundo"}, headers=_auth_headers(token)
        )

        response = client.get("/api/posts", headers=_auth_headers(token))

        assert response.status_code == 200
        contents = [p["content"] for p in response.get_json()["posts"]]
        assert contents.index("segundo") < contents.index("primero")

    def test_list_posts_shows_posts_from_all_authors(self, client):
        # ADR-004 §Opciones consideradas: feed global, sin filtrar por
        # `follows` (esa relación no existe todavía).
        token_a = _register_and_login(
            client, username="user_a", email="a@example.com"
        )
        token_b = _register_and_login(
            client, username="user_b", email="b@example.com"
        )
        client.post(
            "/api/posts", json={"content": "de A"}, headers=_auth_headers(token_a)
        )
        client.post(
            "/api/posts", json={"content": "de B"}, headers=_auth_headers(token_b)
        )

        response = client.get("/api/posts", headers=_auth_headers(token_b))

        contents = {p["content"] for p in response.get_json()["posts"]}
        assert contents == {"de A", "de B"}

    def test_list_posts_empty_returns_empty_list(self, client):
        token = _register_and_login(client)

        response = client.get("/api/posts", headers=_auth_headers(token))

        assert response.status_code == 200
        assert response.get_json()["posts"] == []


class TestDeletePost:
    # DELETE /api/posts/<post_id> (ADR-015-post-deletion.md).

    def _create_post(self, client, token, content="Post para borrar"):
        response = client.post(
            "/api/posts", json={"content": content}, headers=_auth_headers(token)
        )
        return response.get_json()["post"]["id"]

    def test_author_can_delete_their_own_post(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        response = client.delete(f"/api/posts/{post_id}", headers=_auth_headers(token))

        assert response.status_code == 200
        assert response.get_json() == {"deleted": True}

    def test_deleted_post_disappears_from_feed(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        client.delete(f"/api/posts/{post_id}", headers=_auth_headers(token))
        response = client.get("/api/posts", headers=_auth_headers(token))

        assert response.get_json()["posts"] == []

    def test_another_user_cannot_delete_someone_elses_post(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = self._create_post(client, token_a)

        response = client.delete(f"/api/posts/{post_id}", headers=_auth_headers(token_b))

        # Mismo 404 que un post inexistente -- no revela que el post existe
        # pero es de otra persona (ADR-015 §Seguridad).
        assert response.status_code == 404
        # y sigue estando en el feed
        contents = [p["content"] for p in client.get(
            "/api/posts", headers=_auth_headers(token_a)
        ).get_json()["posts"]]
        assert contents == ["Post para borrar"]

    def test_nonexistent_post_returns_404(self, client):
        token = _register_and_login(client)

        response = client.delete(
            "/api/posts/00000000-0000-0000-0000-000000000000",
            headers=_auth_headers(token),
        )

        assert response.status_code == 404

    def test_malformed_post_id_returns_404(self, client):
        token = _register_and_login(client)

        response = client.delete("/api/posts/no-es-un-uuid", headers=_auth_headers(token))

        assert response.status_code == 404

    def test_delete_post_without_token_returns_401(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        response = client.delete(f"/api/posts/{post_id}")

        assert response.status_code == 401

    def test_deleting_twice_returns_404_the_second_time(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        client.delete(f"/api/posts/{post_id}", headers=_auth_headers(token))
        response = client.delete(f"/api/posts/{post_id}", headers=_auth_headers(token))

        # No es idempotente a propósito (a diferencia de likes/follows,
        # ADR-005/ADR-007): borrar algo que ya no existe es un 404.
        assert response.status_code == 404

    def test_deleting_a_post_removes_its_likes_and_comments(self, client):
        # ON DELETE CASCADE sobre likes.post_id/comments.post_id
        # (ADR-005/ADR-006) -- el borrado no deja filas huérfanas.
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = self._create_post(client, token_a)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "un comentario"},
            headers=_auth_headers(token_b),
        )

        response = client.delete(f"/api/posts/{post_id}", headers=_auth_headers(token_a))

        assert response.status_code == 200
        # el post ya no existe, así que sus sub-recursos tampoco
        assert client.get(
            f"/api/posts/{post_id}/comments", headers=_auth_headers(token_a)
        ).status_code == 404
        assert client.post(
            f"/api/posts/{post_id}/like", headers=_auth_headers(token_b)
        ).status_code == 404

    def test_deleting_a_post_removes_its_notifications(self, client):
        # ON DELETE CASCADE sobre notifications.post_id (ADR-008) -- no queda
        # una notificación apuntando a un post que ya no existe.
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = self._create_post(client, token_a)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))
        assert len(
            client.get("/api/notifications", headers=_auth_headers(token_a))
            .get_json()["notifications"]
        ) == 1

        client.delete(f"/api/posts/{post_id}", headers=_auth_headers(token_a))

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        assert response.get_json()["notifications"] == []


class TestUpdatePost:
    # PATCH /api/posts/<post_id> (ADR-017-content-editing.md).

    def _create_post(self, client, token, content="Texto original"):
        return client.post(
            "/api/posts", json={"content": content}, headers=_auth_headers(token)
        ).get_json()["post"]["id"]

    def test_author_can_edit_their_own_post(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        response = client.patch(
            f"/api/posts/{post_id}",
            json={"content": "Texto corregido"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 200
        post = response.get_json()["post"]
        assert post["content"] == "Texto corregido"
        assert post["edited"] is True

    def test_a_post_that_was_never_edited_reports_edited_false(self, client):
        token = _register_and_login(client)

        created = client.post(
            "/api/posts", json={"content": "Sin editar"}, headers=_auth_headers(token)
        ).get_json()["post"]
        feed = client.get("/api/posts", headers=_auth_headers(token)).get_json()["posts"]

        # `edited` viaja tanto al crear como al listar, siempre en false hasta
        # que haya una edición real (ADR-017 §Contrato API).
        assert created["edited"] is False
        assert feed[0]["edited"] is False

    def test_edited_content_and_flag_appear_in_the_feed(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        client.patch(
            f"/api/posts/{post_id}",
            json={"content": "Lo que quedó"},
            headers=_auth_headers(token),
        )
        feed = client.get("/api/posts", headers=_auth_headers(token)).get_json()["posts"]

        assert feed[0]["content"] == "Lo que quedó"
        assert feed[0]["edited"] is True

    def test_another_user_cannot_edit_someone_elses_post(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = self._create_post(client, token_a, content="Texto de A")

        response = client.patch(
            f"/api/posts/{post_id}",
            json={"content": "Secuestrado por B"},
            headers=_auth_headers(token_b),
        )

        # Mismo 404 que un post inexistente -- no revela que el post existe
        # pero es de otra persona (ADR-017 §Seguridad).
        assert response.status_code == 404
        # y el texto original sigue intacto
        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]
        assert feed[0]["content"] == "Texto de A"
        assert feed[0]["edited"] is False

    def test_nonexistent_post_returns_404(self, client):
        token = _register_and_login(client)

        response = client.patch(
            "/api/posts/00000000-0000-0000-0000-000000000000",
            json={"content": "No hay nada acá"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 404

    def test_edit_post_without_token_returns_401(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        response = client.patch(f"/api/posts/{post_id}", json={"content": "Sin token"})

        assert response.status_code == 401

    def test_edit_post_empty_body_returns_400(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        response = client.patch(f"/api/posts/{post_id}", json={}, headers=_auth_headers(token))

        assert response.status_code == 400

    def test_edit_post_empty_content_returns_400(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        response = client.patch(
            f"/api/posts/{post_id}", json={"content": "   "}, headers=_auth_headers(token)
        )

        # `content` es obligatorio al editar, no opcional como los campos de
        # PATCH /api/users/me (ADR-003) -- es el único campo editable.
        assert response.status_code == 400

    def test_edit_post_over_max_length_returns_400(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        response = client.patch(
            f"/api/posts/{post_id}",
            json={"content": "x" * 2001},
            headers=_auth_headers(token),
        )

        # Mismo validador que POST /api/posts (domain/posts/validators.py) --
        # editar no puede saltarse el límite que crear respeta.
        assert response.status_code == 400

    def test_edit_post_trims_surrounding_whitespace(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        response = client.patch(
            f"/api/posts/{post_id}",
            json={"content": "   con espacios   "},
            headers=_auth_headers(token),
        )

        assert response.get_json()["post"]["content"] == "con espacios"

    def test_edit_post_ignores_unwhitelisted_fields(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = self._create_post(client, token_a)
        b_id = client.get(
            "/api/users/me", headers=_auth_headers(token_b)
        ).get_json()["user"]["id"]

        response = client.patch(
            f"/api/posts/{post_id}",
            json={
                "content": "Solo esto se aplica",
                "author_id": b_id,
                "id": "00000000-0000-0000-0000-000000000000",
                "created_at": "1999-01-01T00:00:00+00:00",
                "edited_at": None,
            },
            headers=_auth_headers(token_a),
        )

        post = response.get_json()["post"]
        assert post["content"] == "Solo esto se aplica"
        # Ni el autor ni el id ni las fechas se dejan pisar desde el body
        # (ADR-017 §Seguridad, mismo principio anti mass-assignment que
        # POST /api/posts).
        assert post["id"] == post_id
        assert post["author"]["id"] != b_id
        assert not post["created_at"].startswith("1999")
        assert post["edited"] is True

    def test_editing_a_post_preserves_its_likes_and_comments(self, client):
        # El `id` de la fila no cambia al editar, así que likes y comentarios
        # siguen apuntando al mismo post (ADR-017 §Consecuencias) -- y los
        # contadores que devuelve el PATCH son los reales, no 0.
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = self._create_post(client, token_a)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))
        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "comentario de B"},
            headers=_auth_headers(token_b),
        )

        response = client.patch(
            f"/api/posts/{post_id}",
            json={"content": "Texto editado"},
            headers=_auth_headers(token_a),
        )

        post = response.get_json()["post"]
        assert post["likes_count"] == 1
        assert post["comments_count"] == 1
        # El comentario sigue colgando del mismo post
        comments = client.get(
            f"/api/posts/{post_id}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]
        assert len(comments) == 1

    def test_editing_a_post_reports_liked_by_me_of_the_author(self, client):
        # El autor puede haberle dado like a su propio post -- el PATCH no
        # debe devolver liked_by_me en false por asumir un post nuevo.
        token = _register_and_login(client)
        post_id = self._create_post(client, token)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token))

        response = client.patch(
            f"/api/posts/{post_id}",
            json={"content": "Editado por su autor"},
            headers=_auth_headers(token),
        )

        assert response.get_json()["post"]["liked_by_me"] is True

    def test_editing_a_post_does_not_change_created_at(self, client):
        token = _register_and_login(client)
        created = client.post(
            "/api/posts", json={"content": "Original"}, headers=_auth_headers(token)
        ).get_json()["post"]

        edited = client.patch(
            f"/api/posts/{created['id']}",
            json={"content": "Editado"},
            headers=_auth_headers(token),
        ).get_json()["post"]

        # Editar no "revive" la publicación en el feed: su posición depende de
        # created_at, que no se toca (ADR-017 §Decisión).
        assert edited["created_at"] == created["created_at"]

    def test_editing_twice_keeps_reporting_edited(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        client.patch(
            f"/api/posts/{post_id}", json={"content": "Primera"}, headers=_auth_headers(token)
        )
        response = client.patch(
            f"/api/posts/{post_id}", json={"content": "Segunda"}, headers=_auth_headers(token)
        )

        # Sin historial de versiones (ADR-017 §No objetivos): solo queda el
        # texto final y el flag, que no "se gasta" con la segunda edición.
        assert response.get_json()["post"]["content"] == "Segunda"
        assert response.get_json()["post"]["edited"] is True

    def test_deleted_post_cannot_be_edited(self, client):
        token = _register_and_login(client)
        post_id = self._create_post(client, token)

        client.delete(f"/api/posts/{post_id}", headers=_auth_headers(token))
        response = client.patch(
            f"/api/posts/{post_id}", json={"content": "Zombi"}, headers=_auth_headers(token)
        )

        assert response.status_code == 404
