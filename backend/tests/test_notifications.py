# Pruebas de integración de GET /api/notifications, PATCH
# /api/notifications/<id>/read, y de la generación de notificaciones como
# efecto secundario de like/comment/follow (ADR-008-notifications-minimal-model.md)
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
    res = client.post("/api/register", json=payload)
    user_id = res.get_json()["user"]["id"]
    res = client.post(
        "/api/login", json={"email": payload["email"], "password": VALID_PASSWORD}
    )
    return res.get_json()["token"], user_id


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _create_post(client, token, content="hola"):
    res = client.post("/api/posts", json={"content": content}, headers=_auth_headers(token))
    return res.get_json()["post"]["id"]


class TestNotificationOnLike:
    def test_liking_another_users_post_notifies_the_author(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, _ = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)

        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        notifications = response.get_json()["notifications"]
        assert len(notifications) == 1
        assert notifications[0]["type"] == "like"
        assert notifications[0]["actor"]["username"] == "user_b"
        assert notifications[0]["post_id"] == post_id
        assert notifications[0]["read"] is False

    def test_liking_own_post_does_not_notify(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        post_id = _create_post(client, token_a)

        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_a))

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        assert response.get_json()["notifications"] == []

    def test_repeated_like_does_not_duplicate_notification(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, _ = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)

        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        assert len(response.get_json()["notifications"]) == 1

    def test_unlike_then_like_again_creates_a_second_notification(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, _ = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)

        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))
        client.delete(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        assert len(response.get_json()["notifications"]) == 2

    def test_unlike_does_not_notify(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, _ = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)
        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))

        client.delete(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        assert len(response.get_json()["notifications"]) == 1  # solo la del like, no una segunda por el unlike


class TestNotificationOnComment:
    def test_commenting_another_users_post_notifies_the_author(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, _ = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)

        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "lindo post"},
            headers=_auth_headers(token_b),
        )

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        notifications = response.get_json()["notifications"]
        assert len(notifications) == 1
        assert notifications[0]["type"] == "comment"
        assert notifications[0]["actor"]["username"] == "user_b"
        assert notifications[0]["post_id"] == post_id

    def test_commenting_own_post_does_not_notify(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        post_id = _create_post(client, token_a)

        client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "nota mental"},
            headers=_auth_headers(token_a),
        )

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        assert response.get_json()["notifications"] == []

    def test_two_comments_create_two_notifications(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, _ = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)

        client.post(
            f"/api/posts/{post_id}/comments", json={"content": "uno"}, headers=_auth_headers(token_b)
        )
        client.post(
            f"/api/posts/{post_id}/comments", json={"content": "dos"}, headers=_auth_headers(token_b)
        )

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        assert len(response.get_json()["notifications"]) == 2


class TestNotificationOnFollow:
    def test_following_a_user_notifies_them(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.get("/api/notifications", headers=_auth_headers(token_b))
        notifications = response.get_json()["notifications"]
        assert len(notifications) == 1
        assert notifications[0]["type"] == "follow"
        assert notifications[0]["actor"]["username"] == "user_a"
        assert notifications[0]["post_id"] is None

    def test_repeated_follow_does_not_duplicate_notification(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.get("/api/notifications", headers=_auth_headers(token_b))
        assert len(response.get_json()["notifications"]) == 1

    def test_unfollow_does_not_notify(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")

        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        client.delete(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.get("/api/notifications", headers=_auth_headers(token_b))
        assert len(response.get_json()["notifications"]) == 1  # solo la del follow original


class TestListNotifications:
    def test_without_token_returns_401(self, client):
        response = client.get("/api/notifications")
        assert response.status_code == 401

    def test_empty_when_no_notifications(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.get("/api/notifications", headers=_auth_headers(token_a))

        assert response.status_code == 200
        assert response.get_json() == {"notifications": []}

    def test_most_recent_first(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        post_id = _create_post(client, token_a)

        client.post(f"/api/posts/{post_id}/like", headers=_auth_headers(token_b))
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.get("/api/notifications", headers=_auth_headers(token_a))
        notifications = response.get_json()["notifications"]
        # La del like llegó primero -- debe listarse después (más reciente primero).
        assert notifications[0]["type"] == "like"

    def test_only_returns_notifications_for_the_authenticated_user(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        token_c, _ = _register_and_login(client, username="user_c", email="c@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.get("/api/notifications", headers=_auth_headers(token_c))

        assert response.get_json()["notifications"] == []


class TestMarkNotificationRead:
    def _get_first_notification_id(self, client, token):
        response = client.get("/api/notifications", headers=_auth_headers(token))
        return response.get_json()["notifications"][0]["id"]

    def test_marks_notification_as_read(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        notification_id = self._get_first_notification_id(client, token_b)

        response = client.patch(
            f"/api/notifications/{notification_id}/read", headers=_auth_headers(token_b)
        )

        assert response.status_code == 200
        assert response.get_json() == {"read": True}

        listed = client.get("/api/notifications", headers=_auth_headers(token_b)).get_json()
        assert listed["notifications"][0]["read"] is True

    def test_marking_read_twice_is_idempotent(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        notification_id = self._get_first_notification_id(client, token_b)

        client.patch(f"/api/notifications/{notification_id}/read", headers=_auth_headers(token_b))
        response = client.patch(
            f"/api/notifications/{notification_id}/read", headers=_auth_headers(token_b)
        )

        assert response.status_code == 200
        assert response.get_json() == {"read": True}

    def test_cannot_mark_another_users_notification_as_read(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, id_b = _register_and_login(client, username="user_b", email="b@example.com")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        notification_id = self._get_first_notification_id(client, token_b)

        response = client.patch(
            f"/api/notifications/{notification_id}/read", headers=_auth_headers(token_a)
        )

        assert response.status_code == 404

    def test_nonexistent_notification_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.patch(
            f"/api/notifications/{fake_id}/read", headers=_auth_headers(token_a)
        )

        assert response.status_code == 404

    def test_malformed_id_returns_404(self, client):
        token_a, _ = _register_and_login(client, username="user_a", email="a@example.com")

        response = client.patch(
            "/api/notifications/not-a-uuid/read", headers=_auth_headers(token_a)
        )

        assert response.status_code == 404

    def test_without_token_returns_401(self, client):
        fake_id = "11111111-1111-1111-1111-111111111111"

        response = client.patch(f"/api/notifications/{fake_id}/read")

        assert response.status_code == 401
