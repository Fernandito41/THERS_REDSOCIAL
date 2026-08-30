# Pruebas de integración de POST/GET /api/posts (ADR-004-posts-minimal-model.md)
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
