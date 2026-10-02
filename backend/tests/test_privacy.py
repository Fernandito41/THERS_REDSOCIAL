# Pruebas de integración de la pantalla de Privacidad (REF-SET-02) contra
# PostgreSQL 16 real (thers_test, ver conftest.py) -- no mocks.
#
# Cubre los tres ADR que la implementan:
#   · ADR-022-private-accounts.md -- cuenta privada y solicitudes de seguimiento
#   · ADR-023-mentions.md -- menciones con @username
#   · ADR-024-content-filters-and-privacy-preferences.md -- filtros de
#     contenido, privacidad de mensajes directos y estado de actividad

from tests.conftest import mark_email_verified, reset_rate_limits

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
    """Devuelve (token, user_id) -- mismo helper que tests/test_messages.py."""
    payload = _register_payload(**overrides)
    register_response = client.post("/api/register", json=payload)
    user_id = register_response.get_json()["user"]["id"]
    mark_email_verified(user_id)
    res = client.post(
        "/api/login", json={"email": payload["email"], "password": VALID_PASSWORD}
    )
    return res.get_json()["token"], user_id


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _users(client, *tags):
    """Crea N usuarios con usernames/emails distintos, en orden."""
    return [
        _register_and_login(client, username=f"user_{tag}", email=f"{tag}@example.com")
        for tag in tags
    ]


def _set_privacy(client, token, **fields):
    return client.patch("/api/users/me/privacy", json=fields, headers=_auth_headers(token))


def _create_post(client, token, content="contenido"):
    return client.post(
        "/api/posts", json={"content": content}, headers=_auth_headers(token)
    ).get_json()["post"]


# ===========================================================================
# ADR-022 — Preferencias: lectura y escritura
# ===========================================================================
class TestPrivacySettingsEndpoint:
    def test_defaults_preserve_previous_behaviour(self, client):
        token, _ = _register_and_login(client)

        privacy = client.get(
            "/api/users/me/privacy", headers=_auth_headers(token)
        ).get_json()["privacy"]

        # Los defaults son los que replican el comportamiento anterior a estos
        # tres ADR -- nadie se vuelve privado ni filtra nada por migrar.
        assert privacy["is_private"] is False
        assert privacy["who_can_mention"] == "everyone"
        assert privacy["who_can_message"] == "everyone"
        assert privacy["hide_offensive_comments"] is False
        assert privacy["pending_follow_requests_count"] == 0
        # Única excepción: la actividad nace visible, pero sin dato previo.
        assert privacy["show_activity_status"] is True

    def test_patch_updates_only_the_fields_sent(self, client):
        token, _ = _register_and_login(client)

        privacy = _set_privacy(client, token, is_private=True).get_json()["privacy"]

        assert privacy["is_private"] is True
        # Lo que no se mandó no cambia (PATCH parcial).
        assert privacy["who_can_mention"] == "everyone"

    def test_patch_rejects_non_boolean_for_a_boolean_field(self, client):
        token, _ = _register_and_login(client)

        response = _set_privacy(client, token, is_private="true")

        # Un string "true" no se acepta: tratarlo como verdadero por truthiness
        # dejaría a alguien creyendo que cerró su cuenta cuando la abrió.
        assert response.status_code == 400

    def test_patch_rejects_unknown_audience_value(self, client):
        token, _ = _register_and_login(client)

        response = _set_privacy(client, token, who_can_mention="amigos")

        assert response.status_code == 400

    def test_patch_ignores_fields_outside_the_whitelist(self, client):
        token, user_id = _register_and_login(client)

        response = _set_privacy(client, token, is_private=True, email_verified=False, name="Hacked")

        assert response.status_code == 200
        # Ni `email_verified` ni `name` están en la whitelist de privacidad:
        # no se tocan desde este endpoint (anti mass-assignment).
        user = client.get("/api/users/me", headers=_auth_headers(token)).get_json()["user"]
        assert user["name"] == "Ada Lovelace"
        assert user["email_verified"] is True

    def test_patch_with_empty_body_returns_400(self, client):
        token, _ = _register_and_login(client)

        assert _set_privacy(client, token).status_code == 400

    def test_privacy_endpoint_requires_auth(self, client):
        assert client.get("/api/users/me/privacy").status_code == 401
        assert client.patch("/api/users/me/privacy", json={"is_private": True}).status_code == 401

    def test_is_private_also_travels_in_the_user_object(self, client):
        token, _ = _register_and_login(client)
        _set_privacy(client, token, is_private=True)

        user = client.get("/api/users/me", headers=_auth_headers(token)).get_json()["user"]

        # El Frontend lo necesita en cada arranque de sesión para saber si
        # mostrar la bandeja de solicitudes (ADR-022 §Contrato API).
        assert user["is_private"] is True


# ===========================================================================
# ADR-022 — Solicitudes de seguimiento
# ===========================================================================
class TestFollowRequests:
    def test_following_a_private_account_creates_a_pending_request(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)

        response = client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        assert response.status_code == 200
        # Pedir no es seguir: `following` sigue en false (ADR-022 §Decisión).
        assert response.get_json() == {"following": False, "follow_status": "pending"}

    def test_following_a_public_account_is_immediate(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")

        response = client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        assert response.get_json() == {"following": True, "follow_status": "accepted"}

    def test_a_pending_request_does_not_count_as_a_follower(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        user_b = client.get("/api/users/me", headers=_auth_headers(token_b)).get_json()["user"]

        # Contar pendientes como seguidores anunciaría gente que todavía no
        # tiene acceso a nada (ADR-022 §Decisión).
        assert user_b["followers_count"] == 0

    def test_owner_sees_the_pending_request(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        requests = client.get(
            "/api/follow-requests", headers=_auth_headers(token_b)
        ).get_json()["follow_requests"]

        assert len(requests) == 1
        assert requests[0]["user"]["id"] == id_a
        assert requests[0]["user"]["username"] == "user_a"
        # Nunca datos privados del solicitante.
        assert "email" not in requests[0]["user"]

    def test_pending_count_appears_in_privacy_settings(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        privacy = client.get(
            "/api/users/me/privacy", headers=_auth_headers(token_b)
        ).get_json()["privacy"]

        assert privacy["pending_follow_requests_count"] == 1

    def test_requester_does_not_see_other_peoples_requests(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        # A no tiene solicitudes dirigidas a él -- la lista es siempre la del
        # usuario autenticado (ADR-022 §Seguridad).
        requests = client.get(
            "/api/follow-requests", headers=_auth_headers(token_a)
        ).get_json()["follow_requests"]

        assert requests == []

    def test_accepting_turns_the_request_into_a_follow(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.post(
            f"/api/follow-requests/{id_a}/accept", headers=_auth_headers(token_b)
        )

        assert response.status_code == 200
        assert response.get_json() == {"accepted": True}
        user_b = client.get("/api/users/me", headers=_auth_headers(token_b)).get_json()["user"]
        assert user_b["followers_count"] == 1
        # Y ya no está pendiente.
        assert client.get(
            "/api/follow-requests", headers=_auth_headers(token_b)
        ).get_json()["follow_requests"] == []

    def test_accepting_notifies_the_requester(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        client.post(f"/api/follow-requests/{id_a}/accept", headers=_auth_headers(token_b))

        notifications = client.get(
            "/api/notifications", headers=_auth_headers(token_a)
        ).get_json()["notifications"]

        # Sin esto, el solicitante no tendría forma de saber que ya puede ver
        # el contenido (ADR-022 §Decisión).
        assert [n["type"] for n in notifications] == ["follow_accepted"]

    def test_rejecting_removes_the_request_without_notifying(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.delete(
            f"/api/follow-requests/{id_a}", headers=_auth_headers(token_b)
        )

        assert response.status_code == 200
        assert response.get_json() == {"rejected": True}
        assert client.get(
            "/api/follow-requests", headers=_auth_headers(token_b)
        ).get_json()["follow_requests"] == []
        # Rechazar NO se notifica (ADR-022 §Decisión).
        assert client.get(
            "/api/notifications", headers=_auth_headers(token_a)
        ).get_json()["notifications"] == []

    def test_rejected_requester_can_ask_again(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        client.delete(f"/api/follow-requests/{id_a}", headers=_auth_headers(token_b))

        response = client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        # Rechazar borra la fila en vez de marcarla, justamente para que se
        # pueda volver a pedir (ADR-022 §Opciones consideradas).
        assert response.get_json()["follow_status"] == "pending"

    def test_cannot_accept_a_request_directed_at_someone_else(self, client):
        (token_a, id_a), (token_b, id_b), (token_c, _) = _users(client, "a", "b", "c")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.post(
            f"/api/follow-requests/{id_a}/accept", headers=_auth_headers(token_c)
        )

        # Mismo 404 que una solicitud inexistente -- no revela que existe ni de
        # quién es (ADR-022 §Seguridad).
        assert response.status_code == 404

    def test_accepting_twice_returns_404_the_second_time(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        client.post(f"/api/follow-requests/{id_a}/accept", headers=_auth_headers(token_b))
        response = client.post(
            f"/api/follow-requests/{id_a}/accept", headers=_auth_headers(token_b)
        )

        assert response.status_code == 404

    def test_rejecting_never_removes_an_accepted_follower(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        client.post(f"/api/follow-requests/{id_a}/accept", headers=_auth_headers(token_b))

        response = client.delete(
            f"/api/follow-requests/{id_a}", headers=_auth_headers(token_b)
        )

        # El DELETE de solicitudes solo toca filas 'pending' -- rechazar no
        # puede desaparecer a alguien que ya era seguidor.
        assert response.status_code == 404
        user_b = client.get("/api/users/me", headers=_auth_headers(token_b)).get_json()["user"]
        assert user_b["followers_count"] == 1

    def test_requester_can_cancel_their_own_pending_request(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.delete(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        # El mismo DELETE sirve para dejar de seguir y para cancelar una
        # solicitud (ADR-022 §Decisión).
        assert response.get_json() == {"following": False, "follow_status": None}
        assert client.get(
            "/api/follow-requests", headers=_auth_headers(token_b)
        ).get_json()["follow_requests"] == []

    def test_follow_requests_endpooints_require_auth(self, client):
        fake = "00000000-0000-0000-0000-000000000000"
        assert client.get("/api/follow-requests").status_code == 401
        assert client.post(f"/api/follow-requests/{fake}/accept").status_code == 401
        assert client.delete(f"/api/follow-requests/{fake}").status_code == 401

    def test_turning_private_keeps_existing_followers(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        _set_privacy(client, token_b, is_private=True)

        # Volverse privado no degrada a los seguidores actuales a pendientes:
        # quien ya tenía acceso lo conserva (ADR-022 §Decisión).
        user_b = client.get("/api/users/me", headers=_auth_headers(token_b)).get_json()["user"]
        assert user_b["followers_count"] == 1
        privacy = client.get(
            "/api/users/me/privacy", headers=_auth_headers(token_b)
        ).get_json()["privacy"]
        assert privacy["pending_follow_requests_count"] == 0


# ===========================================================================
# ADR-022 — Visibilidad del contenido de una cuenta privada
# ===========================================================================
class TestPrivateAccountVisibility:
    def test_private_posts_are_hidden_from_the_feed_of_non_followers(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        _create_post(client, token_b, content="secreto de B")

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        assert feed == []

    def test_a_private_account_still_sees_its_own_posts(self, client):
        (token_b, _), = _users(client, "b")
        _set_privacy(client, token_b, is_private=True)
        _create_post(client, token_b, content="mi propio post")

        feed = client.get("/api/posts", headers=_auth_headers(token_b)).get_json()["posts"]

        # Nadie se sigue a sí mismo, así que sin el caso explícito del autor
        # una cuenta privada no vería ni su propio contenido (ADR-022).
        assert [p["content"] for p in feed] == ["mi propio post"]

    def test_accepted_follower_sees_private_posts(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        _create_post(client, token_b, content="para mis seguidores")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        client.post(f"/api/follow-requests/{id_a}/accept", headers=_auth_headers(token_b))

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        assert [p["content"] for p in feed] == ["para mis seguidores"]

    def test_pending_requester_does_not_see_private_posts(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        _create_post(client, token_b, content="todavía no")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        # Pedir no es seguir: una solicitud pendiente no concede visibilidad.
        assert feed == []

    def test_public_posts_stay_visible_to_everyone(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _create_post(client, token_b, content="post público")

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        assert [p["content"] for p in feed] == ["post público"]

    def test_cannot_read_comments_of_a_private_post(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        post = _create_post(client, token_b)

        response = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_a)
        )

        # 404, no 403: un 403 confirmaría que ese post existe y de quién es.
        assert response.status_code == 404

    def test_cannot_comment_on_a_private_post(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        post = _create_post(client, token_b)

        response = client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "hola"},
            headers=_auth_headers(token_a),
        )

        assert response.status_code == 404

    def test_cannot_like_a_private_post(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        post = _create_post(client, token_b)

        assert client.post(
            f"/api/posts/{post['id']}/like", headers=_auth_headers(token_a)
        ).status_code == 404
        assert client.delete(
            f"/api/posts/{post['id']}/like", headers=_auth_headers(token_a)
        ).status_code == 404

    def test_author_is_private_travels_with_the_post(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True)
        _create_post(client, token_b)
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))
        client.post(
            f"/api/follow-requests/{client.get('/api/users/me', headers=_auth_headers(token_a)).get_json()['user']['id']}/accept",
            headers=_auth_headers(token_b),
        )

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        # El Frontend lo necesita para saber que el botón manda una solicitud
        # y no un follow directo (ADR-022 §Contrato API).
        assert feed[0]["author"]["is_private"] is True
        assert feed[0]["author"]["follow_status"] == "accepted"
        assert feed[0]["author"]["is_followed_by_me"] is True

    def test_follow_status_is_pending_in_the_feed_for_a_requested_public_account(self, client):
        # Una cuenta pública nunca deja un follow en pending, así que el tercer
        # estado del botón solo aparece con cuentas privadas -- se comprueba
        # que `follow_status` refleja eso y no se queda siempre en accepted.
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _create_post(client, token_b, content="post público")

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        assert feed[0]["author"]["follow_status"] is None
        assert feed[0]["author"]["is_followed_by_me"] is False


# ===========================================================================
# ADR-023 — Menciones con @username
# ===========================================================================
class TestMentions:
    def test_mentioning_an_existing_user_records_the_mention(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")

        post = _create_post(client, token_a, content="hola @user_b, mirá esto")

        assert [m["username"] for m in post["mentions"]] == ["user_b"]
        assert post["mentions"][0]["id"] == id_b
        # El texto conserva el @username tal como se escribió.
        assert "@user_b" in post["content"]

    def test_mention_notifies_the_mentioned_user(self, client):
        (token_a, id_a), (token_b, _) = _users(client, "a", "b")

        _create_post(client, token_a, content="te menciono @user_b")

        notifications = client.get(
            "/api/notifications", headers=_auth_headers(token_b)
        ).get_json()["notifications"]
        assert [n["type"] for n in notifications] == ["mention"]
        assert notifications[0]["actor"]["id"] == id_a

    def test_nonexistent_username_is_not_a_mention(self, client):
        (token_a, _), = _users(client, "a")

        post = _create_post(client, token_a, content="hola @no_existe_nadie")

        # Se publica igual y el @texto queda como texto plano: nadie pierde lo
        # que escribió por etiquetar a quien no existe (ADR-023 §Decisión).
        assert post["mentions"] == []
        assert post["content"] == "hola @no_existe_nadie"

    def test_email_in_the_text_is_not_a_mention(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")

        post = _create_post(client, token_a, content="escribime a ada@user_b.com")

        # El lookbehind del parser evita este falso positivo clásico.
        assert post["mentions"] == []

    def test_mention_is_case_insensitive(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")

        post = _create_post(client, token_a, content="hola @USER_B")

        # Escribir "@USER_B" tiene que mencionar a `user_b` -- es lo que
        # cualquiera espera al teclear (ADR-023).
        assert [m["id"] for m in post["mentions"]] == [id_b]

    def test_repeated_mention_counts_once(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")

        post = _create_post(client, token_a, content="@user_b @user_b @user_b")

        assert len(post["mentions"]) == 1

    def test_mention_respects_who_can_mention_nobody(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_b, who_can_mention="nobody")

        post = _create_post(client, token_a, content="hola @user_b")

        # No autorizada: no es mención, no se persiste y no notifica.
        assert post["mentions"] == []
        assert client.get(
            "/api/notifications", headers=_auth_headers(token_b)
        ).get_json()["notifications"] == []

    def test_who_can_mention_followers_blocks_a_non_follower(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_b, who_can_mention="followers")

        post = _create_post(client, token_a, content="hola @user_b")

        assert post["mentions"] == []

    def test_who_can_mention_followers_allows_someone_they_follow(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, who_can_mention="followers")
        # A sigue a B -- la dirección correcta: B solo acepta menciones de
        # quienes LO siguen.
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        post = _create_post(client, token_a, content="hola @user_b")

        assert [m["id"] for m in post["mentions"]] == [id_b]

    def test_can_always_mention_yourself(self, client):
        (token_a, id_a), = _users(client, "a")
        _set_privacy(client, token_a, who_can_mention="nobody")

        post = _create_post(client, token_a, content="nota para mí: @user_a")

        # La preferencia protege de los demás, no de uno mismo (ADR-023).
        assert [m["id"] for m in post["mentions"]] == [id_a]
        # Pero nadie se notifica a sí mismo.
        assert client.get(
            "/api/notifications", headers=_auth_headers(token_a)
        ).get_json()["notifications"] == []

    def test_mentions_travel_in_the_feed(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")
        _create_post(client, token_a, content="hola @user_b")

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        assert [m["id"] for m in feed[0]["mentions"]] == [id_b]

    def test_editing_a_post_adds_a_new_mention_and_notifies(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        post = _create_post(client, token_a, content="sin menciones")

        edited = client.patch(
            f"/api/posts/{post['id']}",
            json={"content": "ahora sí @user_b"},
            headers=_auth_headers(token_a),
        ).get_json()["post"]

        assert [m["id"] for m in edited["mentions"]] == [id_b]
        assert [
            n["type"]
            for n in client.get(
                "/api/notifications", headers=_auth_headers(token_b)
            ).get_json()["notifications"]
        ] == ["mention"]

    def test_editing_a_post_removes_a_mention_that_is_gone(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        post = _create_post(client, token_a, content="hola @user_b")

        edited = client.patch(
            f"/api/posts/{post['id']}",
            json={"content": "ya no te menciono"},
            headers=_auth_headers(token_a),
        ).get_json()["post"]

        # Editar recalcula: quitar el @username quita la mención (ADR-023).
        assert edited["mentions"] == []

    def test_editing_without_touching_mentions_does_not_renotify(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        post = _create_post(client, token_a, content="hola @user_b")

        client.patch(
            f"/api/posts/{post['id']}",
            json={"content": "hola @user_b, corregido"},
            headers=_auth_headers(token_a),
        )

        # Una sola notificación, la de la creación -- editar no re-notifica a
        # quien ya estaba mencionado (ADR-023 §Decisión).
        notifications = client.get(
            "/api/notifications", headers=_auth_headers(token_b)
        ).get_json()["notifications"]
        assert len(notifications) == 1

    def test_mention_in_a_comment_works_and_notifies(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        post = _create_post(client, token_a)

        comment = client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "ojo @user_b"},
            headers=_auth_headers(token_a),
        ).get_json()["comment"]

        assert [m["id"] for m in comment["mentions"]] == [id_b]
        notifications = client.get(
            "/api/notifications", headers=_auth_headers(token_b)
        ).get_json()["notifications"]
        assert [n["type"] for n in notifications] == ["mention"]
        # La notificación apunta al post que contiene el comentario, porque
        # `notifications` no guarda comment_id (ADR-008/ADR-023).
        assert notifications[0]["post_id"] == post["id"]

    def test_mentions_travel_in_the_comment_thread(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")
        post = _create_post(client, token_a)
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "hola @user_b"},
            headers=_auth_headers(token_a),
        )

        thread = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]

        assert [m["id"] for m in thread[0]["mentions"]] == [id_b]

    def test_editing_a_comment_recalculates_its_mentions(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")
        post = _create_post(client, token_a)
        comment = client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "sin mencion"},
            headers=_auth_headers(token_a),
        ).get_json()["comment"]

        edited = client.patch(
            f"/api/comments/{comment['id']}",
            json={"content": "ahora @user_b"},
            headers=_auth_headers(token_a),
        ).get_json()["comment"]

        assert [m["id"] for m in edited["mentions"]] == [id_b]

    def test_mention_count_is_capped(self, app, client):
        # 11 destinatarios posibles, el tope es 10 (MAX_MENTIONS_PER_CONTENT):
        # las de más se ignoran en silencio, el post se publica igual.
        #
        # Este test registra doce cuentas, bastante más de las cinco por hora
        # que permite `policy.REGISTER` (ADR-027-rate-limiting.md): se reinician
        # los contadores en vez de relajar el límite, porque un límite ajustado
        # para que los tests pasen deja de ser el que protege producción.
        tags = [f"m{i}" for i in range(11)]
        with app.app_context():
            reset_rate_limits()
        (token_a, _), = _users(client, "a")
        with app.app_context():
            reset_rate_limits()
        for tag in tags:
            _users(client, tag)
            with app.app_context():
                reset_rate_limits()
        content = " ".join(f"@user_{tag}" for tag in tags)

        post = _create_post(client, token_a, content=content)

        assert len(post["mentions"]) == 10


# ===========================================================================
# ADR-024 — Filtros de palabras clave propias
# ===========================================================================
class TestMutedKeywords:
    def test_add_list_and_remove(self, client):
        (token, _), = _users(client, "a")

        added = client.post(
            "/api/users/me/muted-keywords",
            json={"keyword": "Spoilers"},
            headers=_auth_headers(token),
        )
        assert added.status_code == 200
        # Se normaliza a minúsculas con la misma función que después lo busca.
        assert added.get_json()["muted_keywords"] == ["spoilers"]

        listed = client.get(
            "/api/users/me/muted-keywords", headers=_auth_headers(token)
        ).get_json()
        assert listed["muted_keywords"] == ["spoilers"]

        removed = client.delete(
            "/api/users/me/muted-keywords",
            json={"keyword": "SPOILERS"},
            headers=_auth_headers(token),
        )
        assert removed.status_code == 200
        assert removed.get_json()["muted_keywords"] == []

    def test_adding_twice_is_idempotent(self, client):
        (token, _), = _users(client, "a")
        for _ in range(2):
            response = client.post(
                "/api/users/me/muted-keywords",
                json={"keyword": "spoilers"},
                headers=_auth_headers(token),
            )
        assert response.status_code == 200
        assert response.get_json()["muted_keywords"] == ["spoilers"]

    def test_empty_keyword_returns_400(self, client):
        (token, _), = _users(client, "a")
        response = client.post(
            "/api/users/me/muted-keywords",
            json={"keyword": "   "},
            headers=_auth_headers(token),
        )
        assert response.status_code == 400

    def test_removing_a_keyword_you_dont_have_returns_404(self, client):
        (token, _), = _users(client, "a")
        response = client.delete(
            "/api/users/me/muted-keywords",
            json={"keyword": "nada"},
            headers=_auth_headers(token),
        )
        assert response.status_code == 404

    def test_keywords_are_per_user(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        client.post(
            "/api/users/me/muted-keywords",
            json={"keyword": "spoilers"},
            headers=_auth_headers(token_a),
        )

        assert client.get(
            "/api/users/me/muted-keywords", headers=_auth_headers(token_b)
        ).get_json()["muted_keywords"] == []

    def test_muted_keyword_hides_a_post_from_the_feed(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _create_post(client, token_b, content="hay spoilers de la serie")
        _create_post(client, token_b, content="post inocente")
        client.post(
            "/api/users/me/muted-keywords",
            json={"keyword": "spoilers"},
            headers=_auth_headers(token_a),
        )

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        assert [p["content"] for p in feed] == ["post inocente"]

    def test_muted_keyword_never_hides_your_own_post(self, client):
        (token_a, _), = _users(client, "a")
        client.post(
            "/api/users/me/muted-keywords",
            json={"keyword": "spoilers"},
            headers=_auth_headers(token_a),
        )
        _create_post(client, token_a, content="mis propios spoilers")

        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        # Filtrar una palabra no debería hacer desaparecer lo que uno escribió.
        assert [p["content"] for p in feed] == ["mis propios spoilers"]

    def test_muted_keyword_hides_a_comment_and_adjusts_the_count(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        post = _create_post(client, token_a)
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "contiene spoilers"},
            headers=_auth_headers(token_b),
        )
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "comentario normal"},
            headers=_auth_headers(token_b),
        )
        client.post(
            "/api/users/me/muted-keywords",
            json={"keyword": "spoilers"},
            headers=_auth_headers(token_a),
        )

        thread = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]
        feed = client.get("/api/posts", headers=_auth_headers(token_a)).get_json()["posts"]

        assert [c["content"] for c in thread] == ["comentario normal"]
        # El contador tiene que coincidir con lo que el panel muestra: un
        # contador en 2 con una lista de 1 es un bug visible (ADR-024).
        assert feed[0]["comments_count"] == 1

    def test_other_viewers_still_see_the_filtered_comment(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        post = _create_post(client, token_a)
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "contiene spoilers"},
            headers=_auth_headers(token_b),
        )
        client.post(
            "/api/users/me/muted-keywords",
            json={"keyword": "spoilers"},
            headers=_auth_headers(token_a),
        )

        thread = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_b)
        ).get_json()["comments"]

        # Los términos son del espectador: filtran lo que ÉL ve, no lo que ven
        # los demás (ADR-024).
        assert len(thread) == 1

    def test_muted_keywords_endpoints_require_auth(self, client):
        assert client.get("/api/users/me/muted-keywords").status_code == 401
        assert client.post(
            "/api/users/me/muted-keywords", json={"keyword": "x"}
        ).status_code == 401


# ===========================================================================
# ADR-024 — Ocultar comentarios ofensivos (lista del sistema)
# ===========================================================================
class TestHideOffensiveComments:
    def test_offensive_comment_is_hidden_when_the_post_owner_enabled_it(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_a, hide_offensive_comments=True)
        post = _create_post(client, token_a)
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "sos un idiota"},
            headers=_auth_headers(token_b),
        )
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "buen post"},
            headers=_auth_headers(token_b),
        )

        thread = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]

        assert [c["content"] for c in thread] == ["buen post"]

    def test_offensive_comment_stays_visible_when_disabled(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        post = _create_post(client, token_a)
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "sos un idiota"},
            headers=_auth_headers(token_b),
        )

        thread = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]

        # El default es false: nadie empieza a ver su hilo filtrado sin pedirlo.
        assert len(thread) == 1

    def test_the_filter_applies_to_everyone_viewing_that_post(self, client):
        (token_a, _), (token_b, _), (token_c, _) = _users(client, "a", "b", "c")
        _set_privacy(client, token_a, hide_offensive_comments=True)
        post = _create_post(client, token_a)
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "sos un idiota"},
            headers=_auth_headers(token_b),
        )

        thread = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_c)
        ).get_json()["comments"]

        # Es moderación del espacio propio: el flag es del dueño del post y
        # vale para quien lo lea ("en tus cápsulas", REF-SET-02).
        assert thread == []

    def test_the_author_of_the_comment_still_sees_it(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_a, hide_offensive_comments=True)
        post = _create_post(client, token_a)
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "sos un idiota"},
            headers=_auth_headers(token_b),
        )

        thread = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_b)
        ).get_json()["comments"]

        # Si no, escribiría, lo vería desaparecer y lo reescribiría pensando
        # que falló (ADR-024 §Decisión).
        assert len(thread) == 1

    def test_the_filter_only_applies_to_the_owners_posts(self, client):
        (token_a, _), (token_b, _) = _users(client, "a", "b")
        _set_privacy(client, token_a, hide_offensive_comments=True)
        # El post es de B, que NO activó el filtro.
        post = _create_post(client, token_b)
        client.post(
            f"/api/posts/{post['id']}/comments",
            json={"content": "sos un idiota"},
            headers=_auth_headers(token_b),
        )

        thread = client.get(
            f"/api/posts/{post['id']}/comments", headers=_auth_headers(token_a)
        ).get_json()["comments"]

        # El flag de A no modera el espacio de B.
        assert len(thread) == 1


# ===========================================================================
# ADR-024 — Privacidad de mensajes directos
# ===========================================================================
class TestWhoCanMessage:
    def test_nobody_blocks_every_sender(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, who_can_message="nobody")

        response = client.post(
            f"/api/users/{id_b}/messages",
            json={"content": "hola"},
            headers=_auth_headers(token_a),
        )

        # 403 y no 404: quien escribe ya sabía que la cuenta existe.
        assert response.status_code == 403

    def test_followers_blocks_a_non_follower(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, who_can_message="followers")

        response = client.post(
            f"/api/users/{id_b}/messages",
            json={"content": "hola"},
            headers=_auth_headers(token_a),
        )

        assert response.status_code == 403

    def test_followers_allows_someone_who_follows_them(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, who_can_message="followers")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.post(
            f"/api/users/{id_b}/messages",
            json={"content": "hola"},
            headers=_auth_headers(token_a),
        )

        assert response.status_code == 201

    def test_a_pending_request_is_not_enough_to_write(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        _set_privacy(client, token_b, is_private=True, who_can_message="followers")
        client.post(f"/api/users/{id_b}/follow", headers=_auth_headers(token_a))

        response = client.post(
            f"/api/users/{id_b}/messages",
            json={"content": "hola"},
            headers=_auth_headers(token_a),
        )

        # Pedir no es seguir, tampoco para esto (ADR-022/ADR-024).
        assert response.status_code == 403

    def test_everyone_is_the_default_and_keeps_working(self, client):
        (token_a, _), (_, id_b) = _users(client, "a", "b")

        response = client.post(
            f"/api/users/{id_b}/messages",
            json={"content": "hola"},
            headers=_auth_headers(token_a),
        )

        assert response.status_code == 201


# ===========================================================================
# ADR-024 — Estado de actividad
# ===========================================================================
class TestActivityStatus:
    def test_last_seen_is_recorded_for_the_authenticated_user(self, client):
        (token, _), = _users(client, "a")

        # Cualquier petición autenticada que resuelve bien marca la actividad.
        client.get("/api/posts", headers=_auth_headers(token))

        privacy = client.get(
            "/api/users/me/privacy", headers=_auth_headers(token)
        ).get_json()["privacy"]
        assert privacy["last_seen_at"] is not None

    def test_conversation_exposes_the_other_persons_last_seen(self, client):
        (token_a, id_a), (token_b, id_b) = _users(client, "a", "b")
        client.post(
            f"/api/users/{id_b}/messages",
            json={"content": "hola"},
            headers=_auth_headers(token_a),
        )
        # B hace algo autenticado para tener marca propia.
        client.get("/api/posts", headers=_auth_headers(token_b))

        conversations = client.get(
            "/api/conversations", headers=_auth_headers(token_a)
        ).get_json()["conversations"]

        assert conversations[0]["user"]["last_seen_at"] is not None

    def test_hiding_activity_status_hides_it_from_others(self, client):
        (token_a, _), (token_b, id_b) = _users(client, "a", "b")
        client.post(
            f"/api/users/{id_b}/messages",
            json={"content": "hola"},
            headers=_auth_headers(token_a),
        )
        client.get("/api/posts", headers=_auth_headers(token_b))
        _set_privacy(client, token_b, show_activity_status=False)

        conversations = client.get(
            "/api/conversations", headers=_auth_headers(token_a)
        ).get_json()["conversations"]

        assert conversations[0]["user"]["last_seen_at"] is None

    def test_hiding_activity_status_still_shows_it_to_yourself(self, client):
        (token, _), = _users(client, "a")
        client.get("/api/posts", headers=_auth_headers(token))
        _set_privacy(client, token, show_activity_status=False)

        privacy = client.get(
            "/api/users/me/privacy", headers=_auth_headers(token)
        ).get_json()["privacy"]

        # Lo que oculta la preferencia es que lo vean LOS DEMÁS (ADR-024).
        assert privacy["last_seen_at"] is not None
