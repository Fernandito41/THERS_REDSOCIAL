# Pruebas de integración de la pantalla de Seguridad (REF-SET-03) contra
# PostgreSQL 16 real (thers_test, ver conftest.py) -- no mocks.
#
# Cubre los dos ADR que la implementan:
#   · ADR-021-session-registry.md -- sesiones activas y alertas de inicio de sesión
#   · ADR-022-two-factor-authentication.md -- 2FA con TOTP y códigos de recuperación
#
# Los dos controles que YA funcionaban antes de estos ADR (el correo de cambio de
# contraseña, ADR-010, y la verificación de email, ADR-011) tienen sus propias
# pruebas en tests/test_password_reset.py y tests/test_auth.py -- no se duplican
# acá.

import uuid
from datetime import datetime, timedelta, timezone

import pyotp

from app.domain.auth.auth_service import hash_password
from app.domain.auth.token_generator import generate_raw_token, hash_token
from app.extensions import db
from app.infrastructure.persistence.models import PasswordResetToken
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


def _register(client, **overrides):
    payload = _register_payload(**overrides)
    response = client.post("/api/register", json=payload)
    user_id = response.get_json()["user"]["id"]
    mark_email_verified(user_id)
    return payload["email"], user_id


def _login(client, email, user_agent="TestAgent/1.0"):
    """Login completo. Devuelve el body de la respuesta (puede ser un token de
    sesión o un desafío de 2FA)."""
    return client.post(
        "/api/login",
        json={"email": email, "password": VALID_PASSWORD},
        headers={"User-Agent": user_agent},
    ).get_json()


def _register_and_login(client, user_agent="TestAgent/1.0", **overrides):
    email, user_id = _register(client, **overrides)
    body = _login(client, email, user_agent)
    return body["token"], user_id, email


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _enable_two_factor(client, token):
    """Completa el alta de 2FA y devuelve (secret, recovery_codes)."""
    setup = client.post("/api/2fa/setup", headers=_auth_headers(token)).get_json()
    secret = setup["two_factor_setup"]["secret"]
    confirm = client.post(
        "/api/2fa/confirm",
        json={"code": pyotp.TOTP(secret).now()},
        headers=_auth_headers(token),
    )
    assert confirm.status_code == 200, confirm.get_json()
    return secret, confirm.get_json()["recovery_codes"]


# ===========================================================================
# ADR-021 — Sesiones activas
# ===========================================================================
class TestSessionRegistry:
    def test_login_creates_a_listable_session(self, client):
        token, _, _ = _register_and_login(client, user_agent="Firefox/130")

        sessions = client.get("/api/sessions", headers=_auth_headers(token)).get_json()["sessions"]

        assert len(sessions) == 1
        assert sessions[0]["user_agent"] == "Firefox/130"
        assert sessions[0]["is_current"] is True

    def test_session_never_exposes_the_jti(self, client):
        token, _, _ = _register_and_login(client)

        sessions = client.get("/api/sessions", headers=_auth_headers(token)).get_json()["sessions"]

        # El `jti` es lo que valida cada petición: exponerlo convertiría la
        # lista en una lista de identificadores de token (ADR-021 §Contrato API).
        assert "jti" not in sessions[0]

    def test_each_login_adds_a_session(self, client):
        email, _ = _register(client)
        first = _login(client, email, user_agent="Firefox/130")["token"]
        _login(client, email, user_agent="Safari/17")

        sessions = client.get("/api/sessions", headers=_auth_headers(first)).get_json()["sessions"]

        assert len(sessions) == 2
        agents = {s["user_agent"] for s in sessions}
        assert agents == {"Firefox/130", "Safari/17"}

    def test_only_the_current_session_is_flagged(self, client):
        email, _ = _register(client)
        first = _login(client, email, user_agent="Firefox/130")["token"]
        _login(client, email, user_agent="Safari/17")

        sessions = client.get("/api/sessions", headers=_auth_headers(first)).get_json()["sessions"]

        current = [s for s in sessions if s["is_current"]]
        assert len(current) == 1
        assert current[0]["user_agent"] == "Firefox/130"

    def test_revoking_another_session_invalidates_its_token(self, client):
        email, _ = _register(client)
        first = _login(client, email, user_agent="Firefox/130")["token"]
        second = _login(client, email, user_agent="Safari/17")["token"]

        sessions = client.get("/api/sessions", headers=_auth_headers(first)).get_json()["sessions"]
        other = next(s for s in sessions if not s["is_current"])
        response = client.delete(f"/api/sessions/{other['id']}", headers=_auth_headers(first))

        assert response.status_code == 200
        assert response.get_json() == {"revoked": True, "was_current": False}
        # El token revocado deja de servir: es justamente lo que antes de
        # ADR-021 era imposible.
        assert client.get("/api/users/me", headers=_auth_headers(second)).status_code == 401
        # Y el que revocó sigue funcionando.
        assert client.get("/api/users/me", headers=_auth_headers(first)).status_code == 200

    def test_revoked_session_disappears_from_the_list(self, client):
        email, _ = _register(client)
        first = _login(client, email, user_agent="Firefox/130")["token"]
        _login(client, email, user_agent="Safari/17")

        sessions = client.get("/api/sessions", headers=_auth_headers(first)).get_json()["sessions"]
        other = next(s for s in sessions if not s["is_current"])
        client.delete(f"/api/sessions/{other['id']}", headers=_auth_headers(first))

        remaining = client.get("/api/sessions", headers=_auth_headers(first)).get_json()["sessions"]
        assert len(remaining) == 1

    def test_revoking_your_own_session_reports_was_current(self, client):
        token, _, _ = _register_and_login(client)
        sessions = client.get("/api/sessions", headers=_auth_headers(token)).get_json()["sessions"]

        response = client.delete(
            f"/api/sessions/{sessions[0]['id']}", headers=_auth_headers(token)
        )

        # Se permite cerrar la propia, y se informa para que el Frontend
        # redirija a /login (ADR-021 §Decisión).
        assert response.get_json() == {"revoked": True, "was_current": True}
        assert client.get("/api/users/me", headers=_auth_headers(token)).status_code == 401

    def test_cannot_revoke_someone_elses_session(self, client):
        token_a, _, _ = _register_and_login(client, username="user_a", email="a@example.com")
        token_b, _, _ = _register_and_login(client, username="user_b", email="b@example.com")

        sessions_b = client.get(
            "/api/sessions", headers=_auth_headers(token_b)
        ).get_json()["sessions"]
        response = client.delete(
            f"/api/sessions/{sessions_b[0]['id']}", headers=_auth_headers(token_a)
        )

        # Mismo 404 que una sesión inexistente -- no revela que existe
        # (ADR-021 §Seguridad).
        assert response.status_code == 404
        assert client.get("/api/users/me", headers=_auth_headers(token_b)).status_code == 200

    def test_revoking_twice_returns_404_the_second_time(self, client):
        email, _ = _register(client)
        first = _login(client, email, user_agent="Firefox/130")["token"]
        _login(client, email, user_agent="Safari/17")

        sessions = client.get("/api/sessions", headers=_auth_headers(first)).get_json()["sessions"]
        other = next(s for s in sessions if not s["is_current"])
        client.delete(f"/api/sessions/{other['id']}", headers=_auth_headers(first))
        response = client.delete(f"/api/sessions/{other['id']}", headers=_auth_headers(first))

        assert response.status_code == 404

    def test_close_other_sessions_keeps_the_current_one(self, client):
        email, _ = _register(client)
        first = _login(client, email, user_agent="Firefox/130")["token"]
        second = _login(client, email, user_agent="Safari/17")["token"]
        third = _login(client, email, user_agent="Chrome/120")["token"]

        response = client.delete("/api/sessions", headers=_auth_headers(first))

        assert response.status_code == 200
        assert response.get_json() == {"revoked_count": 2}
        # La propia sobrevive: cerrar las demás no debe dejar afuera a quien lo
        # pide (ADR-021 §Decisión).
        assert client.get("/api/users/me", headers=_auth_headers(first)).status_code == 200
        assert client.get("/api/users/me", headers=_auth_headers(second)).status_code == 401
        assert client.get("/api/users/me", headers=_auth_headers(third)).status_code == 401

    def test_sessions_are_per_user(self, client):
        token_a, _, _ = _register_and_login(client, username="user_a", email="a@example.com")
        _register_and_login(client, username="user_b", email="b@example.com")

        sessions = client.get("/api/sessions", headers=_auth_headers(token_a)).get_json()["sessions"]

        assert len(sessions) == 1

    def test_sessions_endpoints_require_auth(self, client):
        fake = "00000000-0000-0000-0000-000000000000"
        assert client.get("/api/sessions").status_code == 401
        assert client.delete("/api/sessions").status_code == 401
        assert client.delete(f"/api/sessions/{fake}").status_code == 401

    def test_changing_the_password_closes_every_session(self, app, client):
        # ADR-021 §Decisión: antes del registro de sesiones esto era imposible,
        # y era un agujero -- quien restablecía su contraseña porque sospechaba
        # un acceso ajeno no echaba a ese acceso.
        #
        # La solicitud ya verificada se siembra directamente, mismo patrón que
        # tests/test_password_reset.py: el código viaja por correo y no se puede
        # leer desde el test (ADR-010 §Seguridad).
        email, user_id = _register(client)
        first = _login(client, email, user_agent="Firefox/130")["token"]
        second = _login(client, email, user_agent="Safari/17")["token"]

        raw_authorization = generate_raw_token()
        with app.app_context():
            db.session.add(
                PasswordResetToken(
                    user_id=uuid.UUID(user_id),
                    code_hash=hash_password("123456"),
                    attempts=0,
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
                    verified_at=datetime.now(timezone.utc),
                    reset_authorization_hash=hash_token(raw_authorization),
                    reset_authorization_expires_at=datetime.now(timezone.utc)
                    + timedelta(minutes=10),
                )
            )
            db.session.commit()

        reset = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": raw_authorization,
                "password": "brandnewpass",
                "confirm_password": "brandnewpass",
            },
        )

        assert reset.status_code == 200
        assert client.get("/api/users/me", headers=_auth_headers(first)).status_code == 401
        assert client.get("/api/users/me", headers=_auth_headers(second)).status_code == 401


# ===========================================================================
# ADR-021 — Alertas de inicio de sesión
# ===========================================================================
class TestLoginAlertPreference:
    def test_enabled_by_default(self, client):
        token, _, _ = _register_and_login(client)

        security = client.get(
            "/api/users/me/security", headers=_auth_headers(token)
        ).get_json()["security"]

        # Nace activada: una alerta de seguridad que hay que descubrir y
        # encender no protege a nadie (ADR-021 §Decisión).
        assert security["login_alerts_enabled"] is True

    def test_can_be_turned_off(self, client):
        token, _, _ = _register_and_login(client)

        response = client.patch(
            "/api/users/me/security",
            json={"login_alerts_enabled": False},
            headers=_auth_headers(token),
        )

        assert response.status_code == 200
        assert response.get_json()["security"]["login_alerts_enabled"] is False

    def test_rejects_a_non_boolean(self, client):
        token, _, _ = _register_and_login(client)

        response = client.patch(
            "/api/users/me/security",
            json={"login_alerts_enabled": "false"},
            headers=_auth_headers(token),
        )

        # El string "false" es verdadero en Python: aceptarlo dejaría a alguien
        # creyendo que apagó las alertas cuando las encendió.
        assert response.status_code == 400

    def test_ignores_fields_outside_the_whitelist(self, client):
        token, _, _ = _register_and_login(client)

        response = client.patch(
            "/api/users/me/security",
            json={"login_alerts_enabled": True, "two_factor_enabled": True, "name": "Hacked"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 200
        user = client.get("/api/users/me", headers=_auth_headers(token)).get_json()["user"]
        assert user["name"] == "Ada Lovelace"
        # `two_factor_enabled` no se activa desde acá: tiene su propio flujo de
        # dos pasos con verificación de código.
        two_factor = client.get("/api/2fa", headers=_auth_headers(token)).get_json()["two_factor"]
        assert two_factor["enabled"] is False

    def test_security_endpoints_require_auth(self, client):
        assert client.get("/api/users/me/security").status_code == 401
        assert client.patch(
            "/api/users/me/security", json={"login_alerts_enabled": False}
        ).status_code == 401


# ===========================================================================
# ADR-022 — 2FA con TOTP
# ===========================================================================
class TestTwoFactorSetup:
    def test_disabled_by_default(self, client):
        token, _, _ = _register_and_login(client)

        status = client.get("/api/2fa", headers=_auth_headers(token)).get_json()["two_factor"]

        assert status == {
            "enabled": False,
            "setup_pending": False,
            "recovery_codes_remaining": 0,
        }

    def test_setup_returns_a_secret_and_a_provisioning_uri(self, client):
        token, _, email = _register_and_login(client)

        response = client.post("/api/2fa/setup", headers=_auth_headers(token))

        assert response.status_code == 200
        setup = response.get_json()["two_factor_setup"]
        assert len(setup["secret"]) >= 16
        assert setup["provisioning_uri"].startswith("otpauth://totp/")
        assert "THERS" in setup["provisioning_uri"]

    def test_setup_alone_does_not_enable_it(self, client):
        token, _, _ = _register_and_login(client)
        client.post("/api/2fa/setup", headers=_auth_headers(token))

        status = client.get("/api/2fa", headers=_auth_headers(token)).get_json()["two_factor"]

        # Escanear el QR y abandonar NO debe dejar la cuenta exigiendo un código
        # (ADR-022 §Decisión): hasta confirmar, el 2FA sigue apagado.
        assert status["enabled"] is False
        assert status["setup_pending"] is True

    def test_confirm_with_a_valid_code_enables_it_and_returns_recovery_codes(self, client):
        token, _, _ = _register_and_login(client)

        secret, recovery_codes = _enable_two_factor(client, token)

        assert len(recovery_codes) == 10
        # Formato legible para transcribir, sin caracteres ambiguos.
        assert all("-" in code for code in recovery_codes)
        status = client.get("/api/2fa", headers=_auth_headers(token)).get_json()["two_factor"]
        assert status["enabled"] is True
        assert status["setup_pending"] is False
        assert status["recovery_codes_remaining"] == 10

    def test_confirm_with_a_wrong_code_returns_400_and_keeps_the_secret(self, client):
        token, _, _ = _register_and_login(client)
        client.post("/api/2fa/setup", headers=_auth_headers(token))

        response = client.post(
            "/api/2fa/confirm", json={"code": "000000"}, headers=_auth_headers(token)
        )

        # 400 y no 401: la identidad ya está probada (endpoint protegido), lo
        # que falla es el dato.
        assert response.status_code == 400
        # El secreto no se borra: se puede reintentar sin volver a escanear.
        status = client.get("/api/2fa", headers=_auth_headers(token)).get_json()["two_factor"]
        assert status["setup_pending"] is True

    def test_confirm_without_setup_returns_409(self, client):
        token, _, _ = _register_and_login(client)

        response = client.post(
            "/api/2fa/confirm", json={"code": "123456"}, headers=_auth_headers(token)
        )

        assert response.status_code == 409

    def test_setup_on_an_already_enabled_account_returns_409(self, client):
        token, _, _ = _register_and_login(client)
        _enable_two_factor(client, token)

        response = client.post("/api/2fa/setup", headers=_auth_headers(token))

        # Para cambiar de dispositivo hay que desactivar primero: regenerar el
        # secreto de un 2FA activo dejaría afuera al dispositivo que funcionaba.
        assert response.status_code == 409

    def test_two_factor_endpoints_require_auth(self, client):
        assert client.get("/api/2fa").status_code == 401
        assert client.post("/api/2fa/setup").status_code == 401
        assert client.post("/api/2fa/confirm", json={"code": "123456"}).status_code == 401
        assert client.post("/api/2fa/disable", json={"password": "x"}).status_code == 401


class TestTwoFactorLogin:
    def test_login_with_2fa_returns_a_challenge_not_a_session(self, client):
        token, _, email = _register_and_login(client)
        _enable_two_factor(client, token)

        body = _login(client, email)

        # 200 y no 4xx: nada salió mal, falta el segundo paso
        # (ADR-022 §Contrato API).
        assert body["two_factor_required"] is True
        assert "two_factor_token" in body
        # Y crucialmente NO hay token de sesión.
        assert "token" not in body

    def test_the_challenge_token_does_not_work_on_protected_endpoints(self, client):
        token, _, email = _register_and_login(client)
        _enable_two_factor(client, token)
        challenge = _login(client, email)["two_factor_token"]

        response = client.get("/api/users/me", headers=_auth_headers(challenge))

        # No tiene fila en `sessions`, así que el blocklist loader lo rechaza
        # (ADR-022 §Seguridad). Un desafío no sirve para leer el feed.
        assert response.status_code == 401

    def test_verifying_with_a_valid_totp_returns_a_session(self, client):
        token, _, email = _register_and_login(client)
        secret, _ = _enable_two_factor(client, token)
        challenge = _login(client, email)["two_factor_token"]

        response = client.post(
            "/api/2fa/verify",
            json={"two_factor_token": challenge, "code": pyotp.TOTP(secret).now()},
        )

        assert response.status_code == 200
        body = response.get_json()
        assert body["used_recovery_code"] is False
        assert client.get("/api/users/me", headers=_auth_headers(body["token"])).status_code == 200

    def test_verifying_with_a_wrong_code_returns_401(self, client):
        token, _, email = _register_and_login(client)
        _enable_two_factor(client, token)
        challenge = _login(client, email)["two_factor_token"]

        response = client.post(
            "/api/2fa/verify", json={"two_factor_token": challenge, "code": "000000"}
        )

        assert response.status_code == 401

    def test_a_session_token_cannot_be_used_as_a_challenge(self, client):
        token, _, email = _register_and_login(client)
        secret, _ = _enable_two_factor(client, token)

        response = client.post(
            "/api/2fa/verify",
            json={"two_factor_token": token, "code": pyotp.TOTP(secret).now()},
        )

        # Sin la comprobación de `purpose`, cualquiera con una sesión válida
        # podría emitirse sesiones nuevas sin el segundo factor
        # (ADR-022 §Seguridad).
        assert response.status_code == 401

    def test_recovery_code_works_and_is_single_use(self, client):
        token, _, email = _register_and_login(client)
        _, recovery_codes = _enable_two_factor(client, token)
        code = recovery_codes[0]

        challenge = _login(client, email)["two_factor_token"]
        first = client.post(
            "/api/2fa/verify", json={"two_factor_token": challenge, "code": code}
        )

        assert first.status_code == 200
        assert first.get_json()["used_recovery_code"] is True
        assert first.get_json()["recovery_codes_remaining"] == 9

        # El mismo código ya no sirve.
        challenge2 = _login(client, email)["two_factor_token"]
        second = client.post(
            "/api/2fa/verify", json={"two_factor_token": challenge2, "code": code}
        )
        assert second.status_code == 401

    def test_recovery_code_accepts_lowercase_and_no_dash(self, client):
        token, _, email = _register_and_login(client)
        _, recovery_codes = _enable_two_factor(client, token)
        messy = recovery_codes[0].lower().replace("-", "")

        challenge = _login(client, email)["two_factor_token"]
        response = client.post(
            "/api/2fa/verify", json={"two_factor_token": challenge, "code": messy}
        )

        # Que alguien lo escriba sin el guion no debería dejarlo fuera de su
        # propia cuenta (ADR-022 §Decisión).
        assert response.status_code == 200

    def test_verify_requires_both_fields(self, client):
        assert client.post("/api/2fa/verify", json={}).status_code == 400
        assert client.post("/api/2fa/verify", json={"code": "123456"}).status_code == 400

    def test_login_without_2fa_still_returns_a_session_directly(self, client):
        email, _ = _register(client)

        body = _login(client, email)

        assert "token" in body
        assert "two_factor_required" not in body


class TestTwoFactorDisableAndRecoveryCodes:
    def test_disable_requires_the_password(self, client):
        token, _, _ = _register_and_login(client)
        _enable_two_factor(client, token)

        response = client.post(
            "/api/2fa/disable", json={"password": "wrongpass"}, headers=_auth_headers(token)
        )

        assert response.status_code == 401

    def test_disable_with_the_password_turns_it_off_and_closes_sessions(self, client):
        token, _, email = _register_and_login(client)
        _enable_two_factor(client, token)

        response = client.post(
            "/api/2fa/disable", json={"password": VALID_PASSWORD}, headers=_auth_headers(token)
        )

        assert response.status_code == 200
        assert response.get_json()["enabled"] is False
        # Bajar la protección de la cuenta fuerza un login nuevo
        # (ADR-021/ADR-022 §Decisión).
        assert client.get("/api/users/me", headers=_auth_headers(token)).status_code == 401
        # Y el login vuelve a ser de un solo paso.
        assert "token" in _login(client, email)

    def test_disable_deletes_the_recovery_codes(self, client):
        token, _, email = _register_and_login(client)
        _, recovery_codes = _enable_two_factor(client, token)
        client.post(
            "/api/2fa/disable", json={"password": VALID_PASSWORD}, headers=_auth_headers(token)
        )

        # Se vuelve a activar: los códigos viejos no deben servir.
        new_token = _login(client, email)["token"]
        _, new_codes = _enable_two_factor(client, new_token)
        challenge = _login(client, email)["two_factor_token"]
        response = client.post(
            "/api/2fa/verify", json={"two_factor_token": challenge, "code": recovery_codes[0]}
        )

        assert response.status_code == 401
        assert recovery_codes[0] not in new_codes

    def test_disable_without_2fa_enabled_returns_409(self, client):
        token, _, _ = _register_and_login(client)

        response = client.post(
            "/api/2fa/disable", json={"password": VALID_PASSWORD}, headers=_auth_headers(token)
        )

        assert response.status_code == 409

    def test_regenerating_recovery_codes_invalidates_the_old_ones(self, client):
        token, _, email = _register_and_login(client)
        _, old_codes = _enable_two_factor(client, token)

        response = client.post(
            "/api/2fa/recovery-codes",
            json={"password": VALID_PASSWORD},
            headers=_auth_headers(token),
        )

        assert response.status_code == 200
        new_codes = response.get_json()["recovery_codes"]
        assert len(new_codes) == 10
        assert not set(old_codes) & set(new_codes)

        # Un código viejo ya no entra.
        challenge = _login(client, email)["two_factor_token"]
        assert client.post(
            "/api/2fa/verify", json={"two_factor_token": challenge, "code": old_codes[0]}
        ).status_code == 401

    def test_regenerating_requires_the_password(self, client):
        token, _, _ = _register_and_login(client)
        _enable_two_factor(client, token)

        response = client.post(
            "/api/2fa/recovery-codes",
            json={"password": "wrongpass"},
            headers=_auth_headers(token),
        )

        assert response.status_code == 401

    def test_regenerating_without_2fa_enabled_returns_409(self, client):
        token, _, _ = _register_and_login(client)

        response = client.post(
            "/api/2fa/recovery-codes",
            json={"password": VALID_PASSWORD},
            headers=_auth_headers(token),
        )

        assert response.status_code == 409
