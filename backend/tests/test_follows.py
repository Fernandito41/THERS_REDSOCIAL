# Pruebas de integración de POST/DELETE /api/users/<id>/follow y de las
# extensiones de GET/PATCH /api/users/me y GET/POST /api/posts
# (ADR-007-follows-minimal-model.md) contra PostgreSQL 16 real (thers_test,
# ver conftest.py) -- no mocks.

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
    res = client.post(
        "/api/login", json={"email": payload["email"], "password": VALID_PASSWORD}
    )
    return res.get_json()["token"], user_id


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestFollowUser:
    def test_follow_user_returns_following_true(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"following": True}

    def test_follow_user_without_token_returns_401(self, client):
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.post(f"/api/users/{id_b}/follow")

        assert response.status_code == 401

    def test_follow_user_is_idempotent(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        response = client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"following": True}

    def test_follow_self_returns_400(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.post(f"/api/users/{id_a}/follow", headers=_auth_headers(token_a))

        assert response.status_code == 400

    def test_follow_nonexistent_user_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.post(f"/api/users/{fake_id}/follow", headers=_auth_headers(token_a))

        assert response.status_code == 404

    def test_follow_malformed_id_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.post("/api/users/not-a-uuid/follow", headers=_auth_headers(token_a))

        assert response.status_code == 404


class TestUnfollowUser:
    def test_unfollow_user_returns_following_false(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.delete(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"following": False}

    def test_unfollow_when_not_following_is_idempotent_noop(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.delete(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"following": False}

    def test_unfollow_without_token_returns_401(self, client):
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        response = client.delete(f"/api/users/{id_b}/follow")

        assert response.status_code == 401

    def test_unfollow_nonexistent_user_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.delete(f"/api/users/{fake_id}/follow", headers=_auth_headers(token_a))

        assert response.status_code == 404


class TestFollowCountsOnUsersMe:
    def test_new_user_has_zero_counts(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.get("/api/users/me", headers=_auth_headers(token_a))

        user = response.get_json()["user"]
        assert user["followers_count"] == 0
        assert user["following_count"] == 0

    def test_following_count_increments_for_follower(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.get("/api/users/me", headers=_auth_headers(token_a))

        assert response.get_json()["user"]["following_count"] == 1

    def test_followers_count_increments_for_followed(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.get("/api/users/me", headers=_auth_headers(token_b))

        assert response.get_json()["user"]["followers_count"] == 1

    def test_counts_reflect_unfollow(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        client.delete(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.get("/api/users/me", headers=_auth_headers(token_b))

        assert response.get_json()["user"]["followers_count"] == 0

    def test_patch_users_me_also_returns_counts(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.patch(
            "/api/users/me", json={"name": "Ada L."}, headers=_auth_headers(token_a)
        )

        assert response.get_json()["user"]["following_count"] == 1


class TestIsFollowedByMeOnPosts:
    def test_new_post_author_is_not_followed_by_me(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.post(
            "/api/posts", json={"content": "hola"}, headers=_auth_headers(token_a)
        )

        assert response.get_json()["post"]["author"]["is_followed_by_me"] is False

    def test_list_posts_reflects_follow_state_per_viewer(self, client):
        token_a, id_a = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, _ = _register_and_login(client, username="user_b", email="b@example.com")
        client.post("/api/posts", json={"content": "post de A"}, headers=_auth_headers(token_a))
        client.post(f"/api/users/{id_a}/follow", headers=_auth_headers(token_b))

        response_b = client.get("/api/posts", headers=_auth_headers(token_b))
        response_a = client.get("/api/posts", headers=_auth_headers(token_a))

        post_seen_by_b = next(
            p for p in response_b.get_json()["posts"] if p["author"]["id"] == id_a
        )
        post_seen_by_a = next(
            p for p in response_a.get_json()["posts"] if p["author"]["id"] == id_a
        )
        assert post_seen_by_b["author"]["is_followed_by_me"] is True
        assert post_seen_by_a["author"]["is_followed_by_me"] is False
