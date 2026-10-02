# Implementación del puerto `TotpProvider` (domain/auth/two_factor.py) con
# `pyotp` (ADR-026-two-factor-authentication.md).
#
# Único punto del backend que importa `pyotp` -- mismo principio que confina
# `google-auth` a google_id_token_verifier.py, `resend` a
# infrastructure/email/ y `psycopg` a infrastructure/persistence/
# (BACKEND_ARCHITECTURE.md §17). Si mañana se cambia de librería, solo este
# archivo se toca.
#
# No se implementa TOTP a mano (RFC 6238 es HMAC-SHA1 + truncado, unas veinte
# líneas): una implementación propia de un algoritmo de autenticación es
# exactamente el tipo de código que no se debe escribir sin necesidad --
# `pyotp` es la librería estándar del ecosistema y ya resuelve la ventana de
# desfase y la comparación en tiempo constante.

import pyotp

from app.domain.auth.two_factor import TOTP_VALID_WINDOW, TotpProvider


class PyotpTotpProvider(TotpProvider):
    def generate_secret(self):
        # pyotp.random_base32() usa `secrets` internamente (CSPRNG), no
        # `random` -- mismo requisito que domain/auth/token_generator.py.
        return pyotp.random_base32()

    def provisioning_uri(self, secret, account_name, issuer_name):
        return pyotp.TOTP(secret).provisioning_uri(
            name=account_name, issuer_name=issuer_name
        )

    def verify(self, secret, code):
        if not secret or not isinstance(code, str):
            return False
        # `valid_window` tolera el desfase de reloj entre el teléfono y el
        # servidor. `pyotp.TOTP.verify` compara con `hmac.compare_digest`
        # (tiempo constante), así que no filtra información por timing.
        return pyotp.TOTP(secret).verify(code.strip(), valid_window=TOTP_VALID_WINDOW)
