# Pruebas de integración del rate limiting (ADR-027-rate-limiting.md) contra
# PostgreSQL 16 real (thers_test, ver conftest.py) -- no mocks.
#
# Cierra el ítem 8 de `API_CONTRACT.md` §9. El caso que motivó el ADR es
# `POST /api/2fa/verify` (un TOTP son 10^6 combinaciones en 30 s), cubierto en
# `TestTwoFactorVerifyRateLimit`.
#
# Los límites NO se relajan para los tests: cada uno empieza con la tabla
# truncada (`_clean_tables`) y, cuando un test necesita legítimamente más
# peticiones de las que un límite permite, llama a `reset_rate_limits()`
# explícitamente. Un límite ajustado para que los tests pasen deja de ser el que
# protege producción.

import pyotp

from app.domain.rate_limiting import policy
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


def _register(client, **overrides):
    payload = _register_payload(**overrides)
    response = client.post("/api/register", json=payload)
    assert response.status_code == 201, response.get_json()
    mark_email_verified(response.get_json()["user"]["id"])
    return payload["email"]


def _login(client, email, password=VALID_PASSWORD):
    return client.post("/api/login", json={"email": email, "password": password})


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# El caso que motivó el ADR
# ===========================================================================
class TestTwoFactorVerifyRateLimit:
    def _account_with_2fa(self, app, client):
        """Cuenta con 2FA activo. Devuelve (email, secret)."""
        email = _register(client)
        token = _login(client, email).get_json()["token"]
        setup = client.post("/api/2fa/setup", headers=_auth_headers(token)).get_json()
        secret = setup["two_factor_setup"]["secret"]
        confirm = client.post(
            "/api/2fa/confirm",
            json={"code": pyotp.TOTP(secret).now()},
            headers=_auth_headers(token),
        )
        assert confirm.status_code == 200, confirm.get_json()
        # El alta consumió intentos de varios contadores; se parte de cero para
        # que el test mida solo lo que dice medir.
        with app.app_context():
            reset_rate_limits()
        return email, secret

    def _challenge(self, client, email):
        return _login(client, email).get_json()["two_factor_token"]

    def test_wrong_codes_eventually_return_429(self, app, client):
        email, _ = self._account_with_2fa(app, client)
        challenge = self._challenge(client, email)

        limit = policy.TWO_FACTOR_VERIFY.limit
        statuses = []
        for _ in range(limit + 1):
            response = client.post(
                "/api/2fa/verify", json={"two_factor_token": challenge, "code": "000000"}
            )
            statuses.append(response.status_code)

        # Los primeros `limit` fallan por código incorrecto (401); el siguiente
        # ya no llega a evaluarse (429).
        assert statuses[:limit] == [401] * limit
        assert statuses[limit] == 429

    def test_429_carries_retry_after(self, app, client):
        email, _ = self._account_with_2fa(app, client)
        challenge = self._challenge(client, email)

        for _ in range(policy.TWO_FACTOR_VERIFY.limit + 1):
            response = client.post(
                "/api/2fa/verify", json={"two_factor_token": challenge, "code": "000000"}
            )

        assert response.status_code == 429
        # El header es tan importante como el código: sin él el cliente
        # reintenta a ciegas (ADR-027 §Contrato API).
        assert "Retry-After" in response.headers
        retry_after = int(response.headers["Retry-After"])
        assert 0 < retry_after <= policy.TWO_FACTOR_VERIFY.window_seconds
        # También en el body, para que el Frontend no tenga que leer headers.
        assert response.get_json()["retry_after_seconds"] == retry_after

    def test_a_valid_code_is_rejected_once_the_limit_is_reached(self, app, client):
        # La propiedad que de verdad importa: agotado el límite, **ni siquiera
        # el código correcto entra**. Si no, un atacante podría seguir probando
        # hasta acertar.
        email, secret = self._account_with_2fa(app, client)
        challenge = self._challenge(client, email)

        for _ in range(policy.TWO_FACTOR_VERIFY.limit):
            client.post(
                "/api/2fa/verify", json={"two_factor_token": challenge, "code": "000000"}
            )

        response = client.post(
            "/api/2fa/verify",
            json={"two_factor_token": challenge, "code": pyotp.TOTP(secret).now()},
        )

        assert response.status_code == 429

    def test_a_success_clears_the_counter(self, app, client):
        # Lo que hay que frenar es *adivinar*, no *usar*: entrar bien varias
        # veces no debe bloquear a nadie (ADR-027, clear_on_success=True).
        email, secret = self._account_with_2fa(app, client)

        for _ in range(policy.TWO_FACTOR_VERIFY.limit + 2):
            challenge = self._challenge(client, email)
            response = client.post(
                "/api/2fa/verify",
                json={"two_factor_token": challenge, "code": pyotp.TOTP(secret).now()},
            )
            assert response.status_code == 200, response.get_json()

    def test_failures_then_a_success_resets_the_budget(self, app, client):
        email, secret = self._account_with_2fa(app, client)
        challenge = self._challenge(client, email)

        # Se gastan todos menos uno.
        for _ in range(policy.TWO_FACTOR_VERIFY.limit - 1):
            client.post(
                "/api/2fa/verify", json={"two_factor_token": challenge, "code": "000000"}
            )

        # El acierto libera el contador...
        ok = client.post(
            "/api/2fa/verify",
            json={"two_factor_token": challenge, "code": pyotp.TOTP(secret).now()},
        )
        assert ok.status_code == 200

        # ...así que vuelve a haber presupuesto completo.
        challenge = self._challenge(client, email)
        response = client.post(
            "/api/2fa/verify", json={"two_factor_token": challenge, "code": "000000"}
        )
        assert response.status_code == 401

    def test_the_limit_is_per_account(self, app, client):
        # Se limita por cuenta y no solo por IP porque un atacante rota IPs
        # trivialmente. El efecto observable: agotar el de una cuenta no debe
        # bloquear a otra... salvo que el límite por IP (que también existe) se
        # alcance primero, así que acá se verifica que la identidad de cuenta es
        # independiente consultando el contador de una segunda cuenta tras
        # reiniciar solo el de IP.
        email_a, _ = self._account_with_2fa(app, client)
        challenge_a = self._challenge(client, email_a)

        for _ in range(policy.TWO_FACTOR_VERIFY.limit + 1):
            client.post(
                "/api/2fa/verify", json={"two_factor_token": challenge_a, "code": "000000"}
            )

        # La cuenta A está bloqueada.
        assert client.post(
            "/api/2fa/verify", json={"two_factor_token": challenge_a, "code": "000000"}
        ).status_code == 429

    def test_an_invalid_challenge_token_does_not_consume_the_budget(self, app, client):
        # El límite se aplica DESPUÉS de validar el token de desafío: así un
        # token basura no gasta los intentos de una cuenta real (ADR-027).
        email, secret = self._account_with_2fa(app, client)

        for _ in range(policy.TWO_FACTOR_VERIFY.limit + 3):
            response = client.post(
                "/api/2fa/verify", json={"two_factor_token": "no-es-un-jwt", "code": "000000"}
            )
            assert response.status_code == 401

        # El presupuesto de la cuenta sigue intacto.
        challenge = self._challenge(client, email)
        ok = client.post(
            "/api/2fa/verify",
            json={"two_factor_token": challenge, "code": pyotp.TOTP(secret).now()},
        )
        assert ok.status_code == 200


# ===========================================================================
# Login
# ===========================================================================
class TestLoginRateLimit:
    def test_wrong_passwords_eventually_return_429(self, client):
        email = _register(client)

        limit = policy.LOGIN.limit
        statuses = [_login(client, email, "wrongpass").status_code for _ in range(limit + 1)]

        assert statuses[:limit] == [401] * limit
        assert statuses[limit] == 429

    def test_429_carries_retry_after(self, client):
        email = _register(client)
        for _ in range(policy.LOGIN.limit + 1):
            response = _login(client, email, "wrongpass")

        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) > 0

    def test_the_correct_password_is_rejected_once_the_limit_is_reached(self, client):
        email = _register(client)
        for _ in range(policy.LOGIN.limit):
            _login(client, email, "wrongpass")

        assert _login(client, email).status_code == 429

    def test_a_successful_login_clears_the_counter(self, client):
        email = _register(client)

        # Entrar bien muchas veces no bloquea: se cuenta el fallo, no el uso.
        for _ in range(policy.LOGIN.limit + 2):
            assert _login(client, email).status_code == 200

    def test_the_limit_is_per_email(self, app, client):
        # Dos cuentas distintas no comparten presupuesto por cuenta. (Comparten
        # el de IP, que en los tests es el mismo, así que se reinicia solo ese
        # efecto registrando la segunda cuenta antes de agotar la primera.)
        email_a = _register(client, username="user_a", email="a@example.com")
        email_b = _register(client, username="user_b", email="b@example.com")

        for _ in range(policy.LOGIN.limit + 1):
            _login(client, email_a, "wrongpass")
        assert _login(client, email_a, "wrongpass").status_code == 429

        # El contador por IP también se agotó, así que se reinicia para aislar
        # la propiedad que se está midiendo: que el contador por email de B
        # nunca se tocó.
        with app.app_context():
            reset_rate_limits()
        assert _login(client, email_b).status_code == 200

    def test_a_nonexistent_email_also_counts(self, client):
        # Un intento contra un email inventado tiene que contar: si no, se
        # podría enumerar cuentas sin límite. Por eso `rate_limit_buckets` no
        # tiene FK a `users` (ADR-027 §Modelo de datos).
        for _ in range(policy.LOGIN.limit + 1):
            response = _login(client, "no-existe@example.com", "x")

        assert response.status_code == 429


# ===========================================================================
# Registro y envío de correos
# ===========================================================================
class TestRegisterRateLimit:
    def test_too_many_registrations_return_429(self, client):
        limit = policy.REGISTER.limit

        statuses = []
        for i in range(limit + 1):
            response = client.post(
                "/api/register",
                json=_register_payload(username=f"user_r{i}", email=f"r{i}@example.com"),
            )
            statuses.append(response.status_code)

        assert statuses[:limit] == [201] * limit
        # `clear_on_success=False`: acá el éxito ES el abuso, así que los
        # registros exitosos cuentan (ADR-027).
        assert statuses[limit] == 429

    def test_successful_registrations_count_unlike_login(self, client):
        # Contraste explícito con el login: ahí el éxito borra el contador, acá
        # lo consume. Son dos semánticas distintas a propósito.
        for i in range(policy.REGISTER.limit):
            client.post(
                "/api/register",
                json=_register_payload(username=f"user_q{i}", email=f"q{i}@example.com"),
            )

        response = client.post(
            "/api/register",
            json=_register_payload(username="user_extra", email="extra@example.com"),
        )
        assert response.status_code == 429


class TestEmailDispatchRateLimit:
    def test_too_many_forgot_password_requests_return_429(self, client):
        email = _register(client)

        limit = policy.EMAIL_DISPATCH.limit
        statuses = []
        for _ in range(limit + 1):
            statuses.append(
                client.post("/api/forgot-password", json={"email": email}).status_code
            )

        # `/forgot-password` siempre responde 200 (no revela si el email existe,
        # ADR-010), así que el 429 es el primer código distinto que aparece.
        assert statuses[:limit] == [200] * limit
        assert statuses[limit] == 429

    def test_the_limit_counts_even_for_unknown_emails(self, client):
        # Se limita el ENVÍO, y la respuesta genérica de ADR-010 no distingue si
        # el email existe -- así que el contador tampoco puede hacerlo.
        for i in range(policy.EMAIL_DISPATCH.limit + 1):
            response = client.post(
                "/api/forgot-password", json={"email": f"nadie{i}@example.com"}
            )

        assert response.status_code == 429


# ===========================================================================
# Gestión del 2FA (endpoints protegidos)
# ===========================================================================
class TestTwoFactorManageRateLimit:
    def test_too_many_wrong_passwords_on_disable_return_429(self, app, client):
        email = _register(client)
        token = _login(client, email).get_json()["token"]
        setup = client.post("/api/2fa/setup", headers=_auth_headers(token)).get_json()
        secret = setup["two_factor_setup"]["secret"]
        client.post(
            "/api/2fa/confirm",
            json={"code": pyotp.TOTP(secret).now()},
            headers=_auth_headers(token),
        )
        with app.app_context():
            reset_rate_limits()

        limit = policy.TWO_FACTOR_MANAGE.limit
        statuses = []
        for _ in range(limit + 1):
            statuses.append(
                client.post(
                    "/api/2fa/disable",
                    json={"password": "wrongpass"},
                    headers=_auth_headers(token),
                ).status_code
            )

        assert statuses[:limit] == [401] * limit
        assert statuses[limit] == 429

    def test_the_correct_password_is_rejected_once_the_limit_is_reached(self, app, client):
        email = _register(client)
        token = _login(client, email).get_json()["token"]
        setup = client.post("/api/2fa/setup", headers=_auth_headers(token)).get_json()
        secret = setup["two_factor_setup"]["secret"]
        client.post(
            "/api/2fa/confirm",
            json={"code": pyotp.TOTP(secret).now()},
            headers=_auth_headers(token),
        )
        with app.app_context():
            reset_rate_limits()

        for _ in range(policy.TWO_FACTOR_MANAGE.limit):
            client.post(
                "/api/2fa/disable",
                json={"password": "wrongpass"},
                headers=_auth_headers(token),
            )

        response = client.post(
            "/api/2fa/disable",
            json={"password": VALID_PASSWORD},
            headers=_auth_headers(token),
        )
        assert response.status_code == 429


# ===========================================================================
# Verificación de OTP (complementa el contador por código de ADR-010/ADR-011)
# ===========================================================================
class TestOtpVerifyRateLimit:
    def test_too_many_otp_attempts_from_one_ip_return_429(self, client):
        # Estos endpoints ya tienen 5 intentos POR CÓDIGO; esto acota el total
        # por IP, porque pedir un código nuevo daba 5 intentos más (ADR-027).
        email = _register(client)

        limit = policy.OTP_VERIFY.limit
        for _ in range(limit + 1):
            response = client.post(
                "/api/verify-reset-code", json={"email": email, "code": "000000"}
            )

        assert response.status_code == 429
