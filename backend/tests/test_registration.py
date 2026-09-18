# Pruebas de integración del registro con verificación obligatoria de email
# mediante OTP (ADR-011-mandatory-email-verification.md): POST /api/register,
# POST /api/verify-registration-code, POST /api/resend-registration-code, y
# el bloqueo de POST /api/login mientras la cuenta no esté verificada.
# Corren contra PostgreSQL 16 real (thers_test, ver conftest.py) -- no mocks.
#
# Reemplaza a test_email_verification.py (ADR-009, flujo de enlace,
# retirado por ADR-011). Mismo criterio que test_password_reset.py para
# obtener/insertar un código conocido en las pruebas que lo requieren: se
# usan las mismas funciones de dominio que el código real
# (hash_password/generate_otp_code), nunca un atajo que la producción no
# tenga -- la API nunca devuelve el código real en ningún response.

import uuid
from datetime import datetime, timedelta, timezone

from app.domain.auth.auth_service import hash_password
from app.extensions import db
from app.infrastructure.email.null_email_sender import NullEmailSender
from app.infrastructure.persistence.models import (
    EmailVerificationToken,
    PasswordResetToken,
    User,
)
from tests.conftest import mark_email_verified

VALID_PASSWORD = "secretpass"
KNOWN_CODE = "123456"


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
    return client.post("/api/register", json=_register_payload(**overrides))


def _create_registration_code(
    app, user_id, code=KNOWN_CODE, minutes_until_expiry=10, attempts=0, used=False
):
    # POST /api/register ya deja un código activo (send_registration_code,
    # register_use_case.py) -- el índice único parcial
    # (uq_email_verification_tokens_active_user) exige a lo sumo uno por
    # usuario, así que cualquier fila activa existente se invalida primero,
    # igual que hace create_code() en producción (mismo patrón que
    # test_password_reset.py, donde /register no deja un
    # password_reset_token activo y por eso no hace falta este paso ahí).
    with app.app_context():
        db.session.query(EmailVerificationToken).filter_by(
            user_id=uuid.UUID(user_id), used_at=None
        ).update({"used_at": datetime.now(timezone.utc)})

        token = EmailVerificationToken(
            user_id=uuid.UUID(user_id),
            code_hash=hash_password(code),
            attempts=attempts,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=minutes_until_expiry),
            used_at=datetime.now(timezone.utc) if used else None,
        )
        db.session.add(token)
        db.session.commit()
        return str(token.id)


class TestRegisterSendsVerificationCode:
    def test_valid_registration_creates_unverified_user_and_pending_code(self, app, client):
        response = _register(client)

        assert response.status_code == 201
        body = response.get_json()["user"]
        user_id = body["id"]

        with app.app_context():
            user = db.session.get(User, uuid.UUID(user_id))
            assert user.email_verified is False

            codes = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=uuid.UUID(user_id))
                .all()
            )
            assert len(codes) == 1
            assert codes[0].used_at is None
            assert codes[0].attempts == 0

    def test_register_response_never_exposes_the_code(self, client):
        response = _register(client)

        raw_body = response.get_data(as_text=True)
        # El código nunca es devuelto en la respuesta -- no hay forma
        # observable desde afuera de saber qué código se generó.
        assert response.get_json()["user"].get("code") is None
        assert "email_verification" not in raw_body


class TestVerifyRegistrationCode:
    def test_correct_code_marks_email_verified(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_registration_code(app, user_id)

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        assert response.status_code == 200
        assert response.get_json()["email_verified"] is True

        with app.app_context():
            user = db.session.get(User, uuid.UUID(user_id))
            assert user.email_verified is True

    def test_correct_code_marks_request_as_used(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        request_id = _create_registration_code(app, user_id)

        client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        with app.app_context():
            row = db.session.get(EmailVerificationToken, uuid.UUID(request_id))
            assert row.used_at is not None

    def test_code_is_single_use(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_registration_code(app, user_id)

        first = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )
        second = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        assert first.status_code == 200
        assert second.status_code == 400

    def test_wrong_code_returns_400_and_increments_attempts(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        request_id = _create_registration_code(app, user_id)

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": "000000"},
        )

        assert response.status_code == 400
        assert "incorrecto" in response.get_json()["msg"].lower()
        with app.app_context():
            row = db.session.get(EmailVerificationToken, uuid.UUID(request_id))
            assert row.attempts == 1

    def test_expired_code_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_registration_code(app, user_id, minutes_until_expiry=-1)

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        assert response.status_code == 400

    def test_max_attempts_blocks_even_the_correct_code(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        # REGISTRATION_MAX_ATTEMPTS = 5 (domain/auth/token_policy.py)
        _create_registration_code(app, user_id, attempts=5)

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        assert response.status_code == 400

    def test_brute_force_exhausts_attempts_then_blocks_correct_code(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_registration_code(app, user_id)

        for _ in range(5):
            client.post(
                "/api/verify-registration-code",
                json={"email": "ada@example.com", "code": "000000"},
            )

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )
        assert response.status_code == 400

    def test_used_request_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_registration_code(app, user_id, used=True)

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        assert response.status_code == 400

    def test_nonexistent_email_returns_same_400(self, client):
        response = client.post(
            "/api/verify-registration-code",
            json={"email": "nobody@example.com", "code": KNOWN_CODE},
        )
        assert response.status_code == 400

    def test_already_verified_account_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        mark_email_verified(user_id)

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        assert response.status_code == 400

    def test_no_active_request_returns_400(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        # Consume el único código activo que /register ya generó, sin
        # dejar ninguno vigente.
        with app.app_context():
            db.session.query(EmailVerificationToken).filter_by(
                user_id=uuid.UUID(user_id)
            ).update({"used_at": datetime.now(timezone.utc)})
            db.session.commit()

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        assert response.status_code == 400

    def test_missing_email_returns_400(self, client):
        response = client.post("/api/verify-registration-code", json={"code": KNOWN_CODE})
        assert response.status_code == 400

    def test_missing_code_returns_400(self, client):
        response = client.post(
            "/api/verify-registration-code", json={"email": "ada@example.com"}
        )
        assert response.status_code == 400

    def test_empty_body_returns_400(self, client):
        response = client.post("/api/verify-registration-code")
        assert response.status_code == 400

    def test_does_not_require_authentication(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_registration_code(app, user_id)

        # Sin header Authorization -- verificar el registro no exige una
        # sesión que, de hecho, todavía no se puede obtener.
        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        assert response.status_code == 200


class TestResendRegistrationCode:
    def test_resend_returns_generic_message(self, client):
        _register(client)

        response = client.post(
            "/api/resend-registration-code", json={"email": "ada@example.com"}
        )

        assert response.status_code == 200
        assert "msg" in response.get_json()

    def test_existing_and_nonexistent_email_return_identical_response(self, client):
        _register(client)

        existing = client.post(
            "/api/resend-registration-code", json={"email": "ada@example.com"}
        )
        nonexistent = client.post(
            "/api/resend-registration-code", json={"email": "nobody@example.com"}
        )

        assert existing.status_code == nonexistent.status_code == 200
        assert existing.get_json() == nonexistent.get_json()

    def test_already_verified_account_returns_same_generic_message_without_new_code(
        self, app, client
    ):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        mark_email_verified(user_id)

        response = client.post(
            "/api/resend-registration-code", json={"email": "ada@example.com"}
        )

        assert response.status_code == 200
        with app.app_context():
            active = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=uuid.UUID(user_id), used_at=None)
                .all()
            )
            # /register ya había dejado un código activo -- una vez
            # verificada la cuenta, "Reenviar código" no lo toca ni genera
            # uno nuevo (sigue siendo el mismo, único, de antes).
            assert len(active) == 1

    def test_repeated_resend_within_cooldown_does_not_duplicate_code(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]

        client.post("/api/resend-registration-code", json={"email": "ada@example.com"})

        with app.app_context():
            codes = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=uuid.UUID(user_id))
                .all()
            )
            # El código generado por /register sigue siendo el único --
            # el reenvío inmediato cae dentro del cooldown de 60s.
            assert len(codes) == 1

    def test_resend_after_cooldown_invalidates_previous_code(self, app, client):
        # Mismo criterio que test_password_reset.py: simula que la
        # solicitud anterior ya es vieja (created_at en el pasado) en vez
        # de esperar 60 segundos reales en la suite.
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        with app.app_context():
            db.session.query(EmailVerificationToken).filter_by(
                user_id=uuid.UUID(user_id)
            ).update({"created_at": datetime.now(timezone.utc) - timedelta(minutes=5)})
            db.session.commit()
            old_request_id = (
                db.session.query(EmailVerificationToken.id)
                .filter_by(user_id=uuid.UUID(user_id))
                .scalar()
            )

        response = client.post(
            "/api/resend-registration-code", json={"email": "ada@example.com"}
        )
        assert response.status_code == 200

        with app.app_context():
            old_row = db.session.get(EmailVerificationToken, old_request_id)
            assert old_row.used_at is not None  # invalidado

            active = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=uuid.UUID(user_id), used_at=None)
                .all()
            )
            assert len(active) == 1
            assert active[0].id != old_request_id

    def test_invalid_email_format_returns_400(self, client):
        response = client.post(
            "/api/resend-registration-code", json={"email": "not-an-email"}
        )
        assert response.status_code == 400

    def test_missing_email_returns_400(self, client):
        response = client.post("/api/resend-registration-code", json={})
        assert response.status_code == 400


class TestLoginBlockedUntilVerified:
    def test_login_before_verification_returns_403_without_issuing_token(self, client):
        _register(client)

        response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": VALID_PASSWORD}
        )

        assert response.status_code == 403
        body = response.get_json()
        assert body["email_verified"] is False
        assert "token" not in body

    def test_login_after_verification_succeeds(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        mark_email_verified(user_id)

        response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": VALID_PASSWORD}
        )

        assert response.status_code == 200
        assert "token" in response.get_json()

    def test_wrong_password_returns_401_even_when_unverified(self, client):
        # La contraseña incorrecta sigue ganando (401) por sobre el estado
        # de verificación (403) -- ADR-011 §Decisión: el chequeo de
        # `email_verified` ocurre después de validar la contraseña, nunca
        # antes, para no abrir un canal lateral nuevo.
        _register(client)

        response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": "wrong-password"}
        )

        assert response.status_code == 401

    def test_full_register_then_verify_then_login_flow(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        _create_registration_code(app, user_id)

        blocked_login = client.post(
            "/api/login", json={"email": "ada@example.com", "password": VALID_PASSWORD}
        )
        assert blocked_login.status_code == 403

        verify_response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )
        assert verify_response.status_code == 200

        login_response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": VALID_PASSWORD}
        )
        assert login_response.status_code == 200
        assert "token" in login_response.get_json()


class TestDuplicateAccountsAndRetry:
    def test_registering_an_already_verified_email_returns_409(self, app, client):
        first = _register(client)
        mark_email_verified(first.get_json()["user"]["id"])

        second = _register(client, name="Otra Persona", username="otra_persona")

        assert second.status_code == 409

    def test_registering_an_already_verified_username_returns_409(self, app, client):
        first = _register(client)
        mark_email_verified(first.get_json()["user"]["id"])

        second = _register(client, email="otra@example.com")

        assert second.status_code == 409

    def test_retrying_registration_with_unverified_email_updates_same_account(
        self, app, client
    ):
        # ADR-011 §Decisión (Estrategia A): un registro nunca verificado no
        # bloquea el email para siempre -- volver a registrarse con el
        # mismo email actualiza la misma fila (incluida la contraseña) y
        # reenvía un código nuevo, en vez de un 409 o una fila duplicada.
        first = _register(client, name="Nombre Viejo")
        first_id = first.get_json()["user"]["id"]

        second = _register(
            client, name="Nombre Nuevo", password="anotherpass123", confirm_password="anotherpass123"
        )

        assert second.status_code == 201
        assert second.get_json()["user"]["id"] == first_id
        assert second.get_json()["user"]["name"] == "Nombre Nuevo"

        with app.app_context():
            users = db.session.query(User).filter_by(email="ada@example.com").all()
            assert len(users) == 1  # nunca una fila duplicada

        # La contraseña nueva es la que aplica una vez verificada la cuenta.
        mark_email_verified(first_id)
        old_password_login = client.post(
            "/api/login", json={"email": "ada@example.com", "password": VALID_PASSWORD}
        )
        assert old_password_login.status_code == 401

        new_password_login = client.post(
            "/api/login", json={"email": "ada@example.com", "password": "anotherpass123"}
        )
        assert new_password_login.status_code == 200

    def test_retrying_registration_invalidates_the_previous_code(self, app, client):
        first = _register(client)
        first_id = first.get_json()["user"]["id"]

        _register(client, name="Nombre Nuevo")

        with app.app_context():
            active = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=uuid.UUID(first_id), used_at=None)
                .all()
            )
            # Un único código activo -- el reintento invalida el anterior
            # (mismo patrón que "Reenviar código", vía create_code()).
            assert len(active) == 1


class TestResendFailureLeavesRecoverableState:
    def test_email_send_failure_returns_500_but_account_stays_recoverable(
        self, app, client, monkeypatch
    ):
        # Simula que Resend (o, acá, el NullEmailSender usado en tests)
        # falla al enviar -- EmailService no atrapa la excepción a
        # propósito (application/email/email_service.py), así que se
        # propaga hasta el manejador global de errores (500 genérico).
        # ADR-011 §Fase 16: la cuenta y el código ya se persistieron antes
        # de intentar el envío -- ni el registro queda a medias ni el email
        # queda bloqueado para siempre, la persona puede pedir un código
        # nuevo más tarde vía "Reenviar código".
        def _boom(self, to_email, subject, html_body):
            raise RuntimeError("fallo simulado de envío de correo")

        monkeypatch.setattr(NullEmailSender, "send", _boom)

        response = _register(client)

        assert response.status_code == 500
        assert response.get_json() == {"msg": "Error interno del servidor"}

        with app.app_context():
            user = db.session.query(User).filter_by(email="ada@example.com").one_or_none()
            assert user is not None
            assert user.email_verified is False

            codes = (
                db.session.query(EmailVerificationToken)
                .filter_by(user_id=user.id)
                .all()
            )
            assert len(codes) == 1  # el código se generó y persistió igual


class TestOtpPurposeSeparation:
    # ADR-011 §Decisión: un código de registro (email_verification_tokens)
    # nunca debe poder usarse para recuperar una contraseña
    # (password_reset_tokens) ni viceversa -- son tablas/repositorios
    # completamente separados, no una tabla genérica con un discriminador
    # de tipo, así que la separación es estructural, no solo de política.
    def test_registration_code_cannot_verify_a_password_reset(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        mark_email_verified(user_id)
        _create_registration_code(app, user_id)  # vive en email_verification_tokens

        response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )

        # No hay ninguna fila en password_reset_tokens -- rechazado como
        # "sin solicitud activa", mismo mensaje genérico de siempre.
        assert response.status_code == 400

    def test_password_reset_code_cannot_verify_a_registration(self, app, client):
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]

        with app.app_context():
            reset_row = PasswordResetToken(
                user_id=uuid.UUID(user_id),
                code_hash=hash_password(KNOWN_CODE),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            )
            db.session.add(reset_row)
            db.session.commit()

        response = client.post(
            "/api/verify-registration-code",
            json={"email": "ada@example.com", "code": KNOWN_CODE},
        )

        # No hay ninguna fila en email_verification_tokens -- rechazado
        # como "sin código activo" (el que sí existe está en la tabla de
        # password reset, que este endpoint nunca consulta).
        assert response.status_code == 400


class TestPasswordRecoveryStillWorksAfterVerification:
    def test_forgot_password_flow_works_for_a_verified_account(self, app, client):
        # Confirma que ADR-010 (recuperación de contraseña) sigue
        # funcionando sin cambios de comportamiento tras ADR-011 -- una
        # cuenta ya verificada puede recuperar su contraseña de punta a
        # punta con el mismo flujo de siempre.
        register_response = _register(client)
        user_id = register_response.get_json()["user"]["id"]
        mark_email_verified(user_id)

        forgot_response = client.post(
            "/api/forgot-password", json={"email": "ada@example.com"}
        )
        assert forgot_response.status_code == 200

        with app.app_context():
            reset_row = (
                db.session.query(PasswordResetToken)
                .filter_by(user_id=uuid.UUID(user_id), used_at=None)
                .one()
            )
            reset_row.code_hash = hash_password(KNOWN_CODE)
            db.session.commit()

        verify_response = client.post(
            "/api/verify-reset-code", json={"email": "ada@example.com", "code": KNOWN_CODE}
        )
        assert verify_response.status_code == 200
        reset_authorization = verify_response.get_json()["reset_authorization"]

        reset_response = client.post(
            "/api/reset-password",
            json={
                "reset_authorization": reset_authorization,
                "password": "brandnewpass123",
                "confirm_password": "brandnewpass123",
            },
        )
        assert reset_response.status_code == 200

        login_response = client.post(
            "/api/login", json={"email": "ada@example.com", "password": "brandnewpass123"}
        )
        assert login_response.status_code == 200
