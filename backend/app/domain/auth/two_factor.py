# Puerto (interfaz) del proveedor de TOTP y reglas puras del 2FA
# (ADR-022-two-factor-authentication.md).
#
# El puerto vive en domain/ y su implementación en infrastructure/auth/, igual
# que `GoogleIdTokenVerifier` (ADR-012): el algoritmo TOTP lo resuelve una
# librería de terceros (`pyotp`), y confinarla a infraestructura es la misma
# regla que mantiene `resend` dentro de infrastructure/email/ y `psycopg`
# dentro de infrastructure/persistence/ (BACKEND_ARCHITECTURE.md §17).
#
# Lo que sí es puro y vive acá: cuántos códigos de recuperación se generan y
# cuánta ventana de desfase horario se tolera.

from abc import ABC, abstractmethod

#: Cuántos códigos de recuperación se entregan al activar el 2FA. Diez es el
#: número que usan los servicios conocidos; es suficiente para varios años de
#: cambios de teléfono y lo bastante corto para que quepan en una captura.
#: Placeholder explícito y revisable, mismo criterio que MAX_CONTENT_LENGTH.
RECOVERY_CODES_COUNT = 10

#: Cuántos intervalos de 30 s antes y después del actual se aceptan. 1 = se
#: tolera un desfase de ±30 s entre el reloj del teléfono y el del servidor,
#: que es el valor por defecto de la mayoría de implementaciones. Subirlo
#: amplía la ventana en la que un código interceptado sigue sirviendo.
TOTP_VALID_WINDOW = 1


class TotpProvider(ABC):
    @abstractmethod
    def generate_secret(self):
        """Secreto compartido nuevo, en base32 (el formato que esperan las apps
        autenticadoras). Tiene que venir de un CSPRNG."""

    @abstractmethod
    def provisioning_uri(self, secret, account_name, issuer_name):
        """URI `otpauth://totp/...` que la app autenticadora entiende. Es lo que
        se codifica en el QR.

        **Contiene el secreto en claro**, así que solo puede viajar a quien ya
        está autenticado y nunca debe registrarse en un log
        (ADR-022 §Seguridad)."""

    @abstractmethod
    def verify(self, secret, code):
        """True si `code` es un TOTP válido para `secret` ahora mismo,
        tolerando `TOTP_VALID_WINDOW` intervalos de desfase."""
