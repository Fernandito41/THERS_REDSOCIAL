# Pruebas de integración de POST/GET /api/posts/<id>/comments y de la
# extensión de GET/POST /api/posts (ADR-006-comments-minimal-model.md)
# contra PostgreSQL 16 real (thers_test, ver conftest.py) -- no mocks.

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
    client.post("/api/register", json=payload)
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
