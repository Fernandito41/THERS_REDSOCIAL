# Pruebas unitarias del adaptador `GoogleIdTokenVerifier`
# (infrastructure/auth/google_id_token_verifier.py, ADR-012-google-sign-in.md)
# -- deliberadamente sin red: nunca llaman a Google de verdad (FASE 24 de la
# tarea origen, "los tests automatizados NO deben depender de realizar
# llamadas reales a Google").
#
# Un credential simplemente malformado (no un JWT válido) falla en el
# parseo local de `verify_oauth2_token()`, antes de que la librería intente
# buscar las claves públicas de Google por red -- eso se prueba sin mockear
# nada. Para los casos que la librería real solo puede detectar *con* red
# (expirado, audience incorrecta, issuer inválido -- exigen validar contra
# un JWT realmente firmado por Google), se mockea la función
# `verify_oauth2_token` en sí para simular cada motivo de rechazo por
# separado y confirmar que el adaptador los traduce TODOS a
# `InvalidGoogleCredentialError`, sin dejar escapar el tipo de excepción
# real de la librería ni sus detalles internos.

import google.auth.exceptions
import pytest

from app.domain.auth.exceptions import InvalidGoogleCredentialError
from app.domain.auth.google_identity import GoogleIdentity
from app.infrastructure.auth import google_id_token_verifier as verifier_module
from app.infrastructure.auth.google_id_token_verifier import GoogleIdTokenVerifier

CLIENT_ID = "test-client-id.apps.googleusercontent.com"


def _verifier():
    return GoogleIdTokenVerifier(CLIENT_ID)


class TestMalformedCredential:
    def test_garbage_string_raises_without_network(self):
        # No es un JWT en absoluto -- verify_oauth2_token() falla al
        # decodificar el header antes de intentar ninguna llamada de red.
        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify("esto-no-es-un-jwt")

    def test_empty_credential_raises(self):
        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify("")

    def test_non_string_credential_raises(self):
        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify(None)


class TestExceptionTranslation:
    # Simula, sin red, los motivos de rechazo que la librería real solo
    # puede detectar validando un JWT genuino de Google -- FASE 24 ítems
    # 2-5 (token inválido/expirado/audience incorrecta/issuer inválido).
    # Todos deben traducirse a la misma excepción de dominio.

    def test_expired_token_raises_domain_error(self, monkeypatch):
        def _boom(*args, **kwargs):
            raise ValueError("Token expired")

        monkeypatch.setattr(verifier_module.google_id_token, "verify_oauth2_token", _boom)

        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify("cualquier-valor")

    def test_wrong_audience_raises_domain_error(self, monkeypatch):
        def _boom(*args, **kwargs):
            raise ValueError("Wrong audience")

        monkeypatch.setattr(verifier_module.google_id_token, "verify_oauth2_token", _boom)

        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify("cualquier-valor")

    def test_invalid_issuer_raises_domain_error(self, monkeypatch):
        def _boom(*args, **kwargs):
            raise google.auth.exceptions.GoogleAuthError("Wrong issuer")

        monkeypatch.setattr(verifier_module.google_id_token, "verify_oauth2_token", _boom)

        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify("cualquier-valor")

    def test_invalid_signature_raises_domain_error(self, monkeypatch):
        def _boom(*args, **kwargs):
            raise google.auth.exceptions.GoogleAuthError("Invalid signature")

        monkeypatch.setattr(verifier_module.google_id_token, "verify_oauth2_token", _boom)

        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify("cualquier-valor")

    def test_never_leaks_the_real_exception_message(self, monkeypatch):
        # El mensaje real de la librería (que podría incluir detalles
        # internos) nunca debe sobrevivir en la excepción de dominio.
        def _boom(*args, **kwargs):
            raise ValueError("detalle interno sensible de la librería")

        monkeypatch.setattr(verifier_module.google_id_token, "verify_oauth2_token", _boom)

        try:
            _verifier().verify("cualquier-valor")
            assert False, "debía lanzar InvalidGoogleCredentialError"
        except InvalidGoogleCredentialError as exc:
            assert "detalle interno sensible" not in str(exc)


class TestClaimsMissingRequiredFields:
    def test_missing_sub_raises_domain_error(self, monkeypatch):
        monkeypatch.setattr(
            verifier_module.google_id_token,
            "verify_oauth2_token",
            lambda *a, **k: {"email": "ada@example.com", "email_verified": True},
        )

        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify("cualquier-valor")

    def test_missing_email_raises_domain_error(self, monkeypatch):
        monkeypatch.setattr(
            verifier_module.google_id_token,
            "verify_oauth2_token",
            lambda *a, **k: {"sub": "1234567890", "email_verified": True},
        )

        with pytest.raises(InvalidGoogleCredentialError):
            _verifier().verify("cualquier-valor")


class TestValidClaims:
    def test_builds_google_identity_from_valid_claims(self, monkeypatch):
        monkeypatch.setattr(
            verifier_module.google_id_token,
            "verify_oauth2_token",
            lambda *a, **k: {
                "sub": "1234567890",
                "email": "ada@example.com",
                "email_verified": True,
                "name": "Ada Lovelace",
            },
        )

        identity = _verifier().verify("cualquier-valor")

        assert identity == GoogleIdentity(
            sub="1234567890", email="ada@example.com", email_verified=True, name="Ada Lovelace"
        )

    def test_defaults_email_verified_to_false_when_absent(self, monkeypatch):
        # Nunca se asume `True` por ausencia del claim -- FASE 8/14: sin la
        # garantía explícita de Google, no hay prueba de control del correo.
        monkeypatch.setattr(
            verifier_module.google_id_token,
            "verify_oauth2_token",
            lambda *a, **k: {"sub": "1234567890", "email": "ada@example.com"},
        )

        identity = _verifier().verify("cualquier-valor")

        assert identity.email_verified is False

    def test_passes_configured_client_id_as_audience(self, monkeypatch):
        # `aud` se valida contra el Client ID exacto de THERS -- nunca se
        # acepta un token válido de Google emitido para otra aplicación.
        received = {}

        def _capture(token, request, audience):
            received["audience"] = audience
            return {"sub": "1", "email": "a@example.com", "email_verified": True}

        monkeypatch.setattr(verifier_module.google_id_token, "verify_oauth2_token", _capture)

        _verifier().verify("cualquier-valor")

        assert received["audience"] == CLIENT_ID
