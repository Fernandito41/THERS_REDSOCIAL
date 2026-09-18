# Pruebas de integración de POST/DELETE /api/posts/<id>/like y de la
# extensión de GET /api/posts (ADR-005-likes-minimal-model.md) contra
# PostgreSQL 16 real (thers_test, ver conftest.py) -- no mocks.

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


def _create_post(client, token, content="post real"):
    response = client.post(
        "/api/posts", json={"content": content}, headers=_auth_headers(token)
    )
    return response.get_json()["post"]["id"]


class TestLikePost:
    def test_like_post_returns_count_and_liked_true(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token))

        assert response.status_code == 200
        assert response.get_json() == {"likes_count": 1, "liked_by_me": True}

    def test_like_post_without_token_returns_401(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.post(f"/api/posts/{post_id}/like")

        assert response.status_code == 401

    def test_like_post_is_idempotent(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token))
        response = client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token))

        assert response.status_code == 200
        assert response.get_json() == {"likes_count": 1, "liked_by_me": True}

    def test_like_nonexistent_post_returns_404(self, client):
        token = _register_and_login(client)
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.post(f"/api/posts/{fake_id}/like", headers=_auth_headers(token))

        assert response.status_code == 404

    def test_like_post_with_malformed_id_returns_404(self, client):
        token = _register_and_login(client)

        response = client.post("/api/posts/not-a-uuid/like", headers=_auth_headers(token))

        assert response.status_code == 404

    def test_like_counts_multiple_users(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)

        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_a))
        response = client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))

        assert response.get_json()["likes_count"] == 2


class TestUnlikePost:
    def test_unlike_post_returns_count_and_liked_false(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token))

        response = client.delete(f"/api/posts/{post_id}/like", headers=_auth_headers(token))

        assert response.status_code == 200
        assert response.get_json() == {"likes_count": 0, "liked_by_me": False}

    def test_unlike_when_not_liked_is_idempotent_noop(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.delete(f"/api/posts/{post_id}/like", headers=_auth_headers(token))

        assert response.status_code == 200
        assert response.get_json() == {"likes_count": 0, "liked_by_me": False}

    def test_unlike_post_without_token_returns_401(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)

        response = client.delete(f"/api/posts/{post_id}/like")

        assert response.status_code == 401

    def test_unlike_nonexistent_post_returns_404(self, client):
        token = _register_and_login(client)
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.delete(f"/api/posts/{fake_id}/like", headers=_auth_headers(token))

        assert response.status_code == 404

    def test_unlike_only_removes_caller_own_like(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_a))
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))

        response = client.delete(f"/api/posts/{post_id}/like", headers=_auth_headers(token_a))

        assert response.get_json() == {"likes_count": 1, "liked_by_me": False}


class TestListPostsWithLikes:
    def test_new_post_has_zero_likes_and_not_liked(self, client):
        token = _register_and_login(client)

        response = client.post(
            "/api/posts", json={"content": "hola"}, headers=_auth_headers(token)
        )

        body = response.get_json()["post"]
        assert body["likes_count"] == 0
        assert body["liked_by_me"] is False

    def test_list_posts_reflects_likes_count(self, client):
        token = _register_and_login(client)
        post_id = _create_post(client, token)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token))

        response = client.get("/api/posts", headers=_auth_headers(token))

        post = next(p for p in response.get_json()["posts"] if p["id"] == post_id)
        assert post["likes_count"] == 1
        assert post["liked_by_me"] is True

    def test_list_posts_liked_by_me_is_per_user(self, client):
        token_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_a))

        response_a = client.get("/api/posts", headers=_auth_headers(token_a))
        response_b = client.get("/api/posts", headers=_auth_headers(token_b))

        post_seen_by_a = next(p for p in response_a.get_json()["posts"] if p["id"] == post_id)
        post_seen_by_b = next(p for p in response_b.get_json()["posts"] if p["id"] == post_id)
        assert post_seen_by_a["liked_by_me"] is True
        assert post_seen_by_b["liked_by_me"] is False
        assert post_seen_by_a["likes_count"] == post_seen_by_b["likes_count"] == 1
