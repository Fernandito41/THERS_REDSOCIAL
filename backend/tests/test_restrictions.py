# Pruebas de integración de bloqueo y restricción de cuentas (REF-SET-10,
# ADR-029-blocked-and-restricted-accounts.md) contra PostgreSQL real
# (thers_test) -- no mocks.
#
# Lo importante no es que los endpoints respondan, sino que el bloqueo
# realmente CORTE el acceso en el servidor: feed, comentarios, likes, follows,
# mensajes, notificaciones y menciones.

from tests.conftest import mark_email_verified

VALID_PASSWORD = "secretpass"


def _register_and_login(client, username, email=None):
    email = email or f"{username}@example.com"
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
    token = client.post(
        "/api/login", json={"email": email, "password": VALID_PASSWORD}
    ).get_json()["token"]
    return token, user_id


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def _two_users(client):
    token_a, id_a = _register_and_login(client, "ada")
    token_b, id_b = _register_and_login(client, "bob")
    return (token_a, id_a), (token_b, id_b)


def _block(client, token, user_id):
    return client.post("/api/users/me/blocks", json={"user_id": user_id}, headers=_h(token))


def _restrict(client, token, user_id):
    return client.post(
        "/api/users/me/restrictions", json={"user_id": user_id}, headers=_h(token)
    )


def _post(client, token, content="hola mundo"):
    return client.post("/api/posts", json={"content": content}, headers=_h(token)).get_json()[
        "post"
    ]["id"]


def _feed_contents(client, token):
    return [p["content"] for p in client.get("/api/posts", headers=_h(token)).get_json()["posts"]]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
class TestEndpoints:
    def test_all_require_authentication(self, client):
        assert client.get("/api/users/me/blocks").status_code == 401
        assert client.post("/api/users/me/blocks", json={}).status_code == 401
        assert client.get("/api/users/me/restrictions").status_code == 401
        assert client.post("/api/users/me/restrictions", json={}).status_code == 401

    def test_block_by_user_id_and_list(self, client):
        (ta, _), (_, id_b) = _two_users(client)
        assert _block(client, ta, id_b).status_code == 200

        blocks = client.get("/api/users/me/blocks", headers=_h(ta)).get_json()["blocks"]
        assert len(blocks) == 1
        assert blocks[0]["user"]["username"] == "bob"
        assert blocks[0]["user"]["id"] == id_b

    def test_block_by_username(self, client):
        (ta, _), _ = _two_users(client)
        response = client.post(
            "/api/users/me/blocks", json={"username": "@Bob"}, headers=_h(ta)
        )
        assert response.status_code == 200
        assert len(client.get("/api/users/me/blocks", headers=_h(ta)).get_json()["blocks"]) == 1

    def test_unknown_user_is_404(self, client):
        (ta, _), _ = _two_users(client)
        response = client.post(
            "/api/users/me/blocks", json={"username": "nadie_existe"}, headers=_h(ta)
        )
        assert response.status_code == 404

    def test_cannot_block_or_restrict_self(self, client):
        (ta, id_a), _ = _two_users(client)
        assert _block(client, ta, id_a).status_code == 400
        assert _restrict(client, ta, id_a).status_code == 400

    def test_missing_target_is_400(self, client):
        (ta, _), _ = _two_users(client)
        assert client.post("/api/users/me/blocks", json={}, headers=_h(ta)).status_code == 400
        assert (
            client.post(
                "/api/users/me/blocks", json={"user_id": "no-es-uuid"}, headers=_h(ta)
            ).status_code
            == 400
        )

    def test_block_is_idempotent_and_unblock_works(self, client):
        (ta, _), (_, id_b) = _two_users(client)
        _block(client, ta, id_b)
        _block(client, ta, id_b)
        assert len(client.get("/api/users/me/blocks", headers=_h(ta)).get_json()["blocks"]) == 1

        assert client.delete(f"/api/users/me/blocks/{id_b}", headers=_h(ta)).status_code == 200
        assert client.get("/api/users/me/blocks", headers=_h(ta)).get_json()["blocks"] == []
        # Desbloquear a quien no está bloqueado no falla.
        assert client.delete(f"/api/users/me/blocks/{id_b}", headers=_h(ta)).status_code == 200

    def test_lists_are_private_to_the_owner(self, client):
        (ta, _), (tb, id_b) = _two_users(client)
        _block(client, ta, id_b)
        assert client.get("/api/users/me/blocks", headers=_h(tb)).get_json()["blocks"] == []

    def test_block_replaces_restriction(self, client):
        (ta, _), (_, id_b) = _two_users(client)
        _restrict(client, ta, id_b)
        _block(client, ta, id_b)

        assert client.get("/api/users/me/restrictions", headers=_h(ta)).get_json()[
            "restrictions"
        ] == []
        assert len(client.get("/api/users/me/blocks", headers=_h(ta)).get_json()["blocks"]) == 1

    def test_cannot_restrict_a_blocked_account(self, client):
        (ta, _), (_, id_b) = _two_users(client)
        _block(client, ta, id_b)
        assert _restrict(client, ta, id_b).status_code == 409

    def test_unblock_does_not_remove_a_restriction(self, client):
        (ta, _), (_, id_b) = _two_users(client)
        _restrict(client, ta, id_b)
        client.delete(f"/api/users/me/blocks/{id_b}", headers=_h(ta))
        assert len(
            client.get("/api/users/me/restrictions", headers=_h(ta)).get_json()["restrictions"]
        ) == 1

    def test_restrict_list_and_remove(self, client):
        (ta, _), (_, id_b) = _two_users(client)
        assert _restrict(client, ta, id_b).status_code == 200
        items = client.get("/api/users/me/restrictions", headers=_h(ta)).get_json()["restrictions"]
        assert [i["user"]["username"] for i in items] == ["bob"]

        client.delete(f"/api/users/me/restrictions/{id_b}", headers=_h(ta))
        assert client.get("/api/users/me/restrictions", headers=_h(ta)).get_json()[
            "restrictions"
        ] == []


# ---------------------------------------------------------------------------
# Bloqueo: corta el acceso en el servidor, en AMBOS sentidos
# ---------------------------------------------------------------------------
class TestBlockEnforcement:
    def test_blocked_user_does_not_see_blockers_posts_and_vice_versa(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        _post(client, ta, "post de ada")
        _post(client, tb, "post de bob")

        assert set(_feed_contents(client, ta)) == {"post de ada", "post de bob"}

        _block(client, ta, id_b)

        assert _feed_contents(client, ta) == ["post de ada"]
        assert _feed_contents(client, tb) == ["post de bob"]

    def test_unblock_restores_the_feed(self, client):
        (ta, _), (tb, id_b) = _two_users(client)
        _post(client, tb, "post de bob")
        _block(client, ta, id_b)
        assert _feed_contents(client, ta) == []

        client.delete(f"/api/users/me/blocks/{id_b}", headers=_h(ta))
        assert _feed_contents(client, ta) == ["post de bob"]

    def test_blocked_user_cannot_like_or_comment_on_blockers_post(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        post_id = _post(client, ta)
        _block(client, ta, id_b)

        assert client.post(f"/api/posts/{post_id}/like", headers=_h(tb)).status_code == 404
        assert (
            client.post(
                f"/api/posts/{post_id}/comments", json={"content": "hola"}, headers=_h(tb)
            ).status_code
            == 404
        )
        assert client.get(f"/api/posts/{post_id}/comments", headers=_h(tb)).status_code == 404

    def test_blocker_cannot_interact_with_blocked_users_post_either(self, client):
        (ta, _), (tb, id_b) = _two_users(client)
        post_id = _post(client, tb)
        _block(client, ta, id_b)

        assert client.post(f"/api/posts/{post_id}/like", headers=_h(ta)).status_code == 404

    def test_blocked_comments_disappear_from_the_thread_of_a_third_party(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        tc, id_c = _register_and_login(client, "carol")
        post_id = _post(client, tc)
        client.post(f"/api/posts/{post_id}/comments", json={"content": "de bob"}, headers=_h(tb))
        client.post(f"/api/posts/{post_id}/comments", json={"content": "de ada"}, headers=_h(ta))

        _block(client, ta, id_b)

        thread_a = client.get(f"/api/posts/{post_id}/comments", headers=_h(ta)).get_json()
        assert [c["content"] for c in thread_a["comments"]] == ["de ada"]
        thread_b = client.get(f"/api/posts/{post_id}/comments", headers=_h(tb)).get_json()
        assert [c["content"] for c in thread_b["comments"]] == ["de bob"]
        # Y una tercera persona sin relación sigue viendo los dos.
        thread_c = client.get(f"/api/posts/{post_id}/comments", headers=_h(tc)).get_json()
        assert [c["content"] for c in thread_c["comments"]] == ["de bob", "de ada"]

    def test_comment_counter_matches_what_the_panel_shows(self, client):
        (ta, _), (tb, id_b) = _two_users(client)
        tc, _ = _register_and_login(client, "carol")
        post_id = _post(client, tc)
        client.post(f"/api/posts/{post_id}/comments", json={"content": "de bob"}, headers=_h(tb))
        _block(client, ta, id_b)

        post = client.get("/api/posts", headers=_h(ta)).get_json()["posts"][0]
        assert post["comments_count"] == 0

    def test_block_removes_follows_in_both_directions(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        client.post(f"/api/users/{id_b}/follow", headers=_h(ta))
        client.post(f"/api/users/{id_a}/follow", headers=_h(tb))

        _block(client, ta, id_b)

        me_a = client.get("/api/users/me", headers=_h(ta)).get_json()["user"]
        me_b = client.get("/api/users/me", headers=_h(tb)).get_json()["user"]
        assert me_a["following_count"] == 0 and me_a["followers_count"] == 0
        assert me_b["following_count"] == 0 and me_b["followers_count"] == 0

    def test_cannot_follow_in_either_direction(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        _block(client, ta, id_b)

        # El bloqueado ve una cuenta inexistente: no se le revela el bloqueo.
        assert client.post(f"/api/users/{id_a}/follow", headers=_h(tb)).status_code == 404
        # Quien bloqueó sí recibe una explicación.
        assert client.post(f"/api/users/{id_b}/follow", headers=_h(ta)).status_code == 409

    def test_cannot_message_in_either_direction(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        _block(client, ta, id_b)

        assert (
            client.post(
                f"/api/users/{id_a}/messages", json={"content": "hola"}, headers=_h(tb)
            ).status_code
            == 404
        )
        assert (
            client.post(
                f"/api/users/{id_b}/messages", json={"content": "hola"}, headers=_h(ta)
            ).status_code
            == 409
        )

    def test_existing_conversation_is_hidden_and_thread_inaccessible(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        client.post(f"/api/users/{id_a}/messages", json={"content": "hola"}, headers=_h(tb))
        assert len(client.get("/api/conversations", headers=_h(ta)).get_json()["conversations"]) == 1

        _block(client, ta, id_b)

        assert client.get("/api/conversations", headers=_h(ta)).get_json()["conversations"] == []
        assert client.get("/api/conversations", headers=_h(tb)).get_json()["conversations"] == []
        assert client.get(f"/api/users/{id_b}/messages", headers=_h(ta)).status_code == 404
        assert client.get(f"/api/users/{id_a}/messages", headers=_h(tb)).status_code == 404

    def test_messages_reappear_after_unblock(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        client.post(f"/api/users/{id_a}/messages", json={"content": "hola"}, headers=_h(tb))
        _block(client, ta, id_b)
        client.delete(f"/api/users/me/blocks/{id_b}", headers=_h(ta))

        assert len(client.get("/api/conversations", headers=_h(ta)).get_json()["conversations"]) == 1

    def test_notifications_from_blocked_accounts_are_hidden(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        post_id = _post(client, ta)
        client.post(f"/api/posts/{post_id}/like", headers=_h(tb))
        assert len(client.get("/api/notifications", headers=_h(ta)).get_json()["notifications"]) == 1

        _block(client, ta, id_b)
        assert client.get("/api/notifications", headers=_h(ta)).get_json()["notifications"] == []

        client.delete(f"/api/users/me/blocks/{id_b}", headers=_h(ta))
        assert len(client.get("/api/notifications", headers=_h(ta)).get_json()["notifications"]) == 1

    def test_mention_of_a_blocked_account_is_dropped(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        _block(client, tb, id_a)  # bob bloquea a ada

        post = client.post(
            "/api/posts", json={"content": "hola @bob"}, headers=_h(ta)
        ).get_json()["post"]

        assert post["mentions"] == []
        assert client.get("/api/notifications", headers=_h(tb)).get_json()["notifications"] == []


# ---------------------------------------------------------------------------
# Restricción: sus comentarios quedan ocultos para los demás
# ---------------------------------------------------------------------------
class TestRestrictEnforcement:
    def test_restricted_users_comments_are_hidden_from_others(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        tc, _ = _register_and_login(client, "carol")
        post_id = _post(client, ta)  # el post es de ada
        client.post(f"/api/posts/{post_id}/comments", json={"content": "de bob"}, headers=_h(tb))
        client.post(f"/api/posts/{post_id}/comments", json={"content": "de carol"}, headers=_h(tc))

        _restrict(client, ta, id_b)  # ada restringe a bob

        # Una tercera persona ya no ve el comentario de bob.
        thread_c = client.get(f"/api/posts/{post_id}/comments", headers=_h(tc)).get_json()
        assert [c["content"] for c in thread_c["comments"]] == ["de carol"]

    def test_restricted_user_still_sees_own_comment_and_the_post(self, client):
        (ta, _), (tb, id_b) = _two_users(client)
        post_id = _post(client, ta)
        client.post(f"/api/posts/{post_id}/comments", json={"content": "de bob"}, headers=_h(tb))
        _restrict(client, ta, id_b)

        # Bob no nota nada: sigue viendo el post y su propio comentario.
        assert "hola mundo" in _feed_contents(client, tb)
        thread_b = client.get(f"/api/posts/{post_id}/comments", headers=_h(tb)).get_json()
        assert [c["content"] for c in thread_b["comments"]] == ["de bob"]

    def test_restrictor_still_sees_the_comment_to_moderate_it(self, client):
        (ta, _), (tb, id_b) = _two_users(client)
        post_id = _post(client, ta)
        client.post(f"/api/posts/{post_id}/comments", json={"content": "de bob"}, headers=_h(tb))
        _restrict(client, ta, id_b)

        thread_a = client.get(f"/api/posts/{post_id}/comments", headers=_h(ta)).get_json()
        assert [c["content"] for c in thread_a["comments"]] == ["de bob"]

    def test_restriction_is_scoped_to_the_restrictors_own_posts(self, client):
        # Bob comenta en el post de Carol; Ada lo restringió, pero eso solo
        # afecta a los posts de Ada, no a los de Carol.
        (ta, _), (tb, id_b) = _two_users(client)
        tc, _ = _register_and_login(client, "carol")
        post_c = _post(client, tc)
        client.post(f"/api/posts/{post_c}/comments", json={"content": "de bob"}, headers=_h(tb))
        _restrict(client, ta, id_b)

        thread_a = client.get(f"/api/posts/{post_c}/comments", headers=_h(ta)).get_json()
        assert [c["content"] for c in thread_a["comments"]] == ["de bob"]

    def test_restricted_user_can_still_interact_normally_otherwise(self, client):
        (ta, id_a), (tb, id_b) = _two_users(client)
        post_id = _post(client, ta)
        _restrict(client, ta, id_b)

        assert client.post(f"/api/posts/{post_id}/like", headers=_h(tb)).status_code == 200
        assert client.post(f"/api/users/{id_a}/follow", headers=_h(tb)).status_code == 200
        assert (
            client.post(
                f"/api/users/{id_a}/messages", json={"content": "hola"}, headers=_h(tb)
            ).status_code
            == 201
        )

    def test_unrestrict_makes_comments_visible_again(self, client):
        (ta, _), (tb, id_b) = _two_users(client)
        tc, _ = _register_and_login(client, "carol")
        post_id = _post(client, ta)
        client.post(f"/api/posts/{post_id}/comments", json={"content": "de bob"}, headers=_h(tb))
        _restrict(client, ta, id_b)
        client.delete(f"/api/users/me/restrictions/{id_b}", headers=_h(ta))

        thread_c = client.get(f"/api/posts/{post_id}/comments", headers=_h(tc)).get_json()
        assert [c["content"] for c in thread_c["comments"]] == ["de bob"]
