# ADR-036 — Fallos del proveedor de correo

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-036-email-provider-failures.md` |
| Fecha | 2026-10-02 |
| Estado | **ACEPTADO con cambios** (2026-10-02) — el propietario del proyecto pidió resolverlo para avanzar; la ratificación del equipo es la aprobación del PR (`HB-001` §11–12). **Enmienda en parte `ADR-011` (Aceptada)**: solo la respuesta HTTP, ver abajo. El código está commiteado en `feature/email-provider-failures` |
| Relacionado | `ADR-009`, `ADR-010`, `ADR-011` (§ «Resend fallando durante el registro»), `ADR-027` |

## Por qué existe

Con Resend real en uso apareció el caso que `ADR-011` solo había reproducido en pruebas: el proveedor puede fallar (dominio sin verificar, clave de otro equipo, o el **límite de 100 correos al día** del plan gratuito). Con el comportamiento actual:

| Flujo | Qué pasa hoy si falla el envío | Problema |
|---|---|---|
| `POST /register` | La cuenta se crea y luego responde `500` | La persona cree que no se registró; si reintenta, la web puede dar otro error |
| `POST /forgot-password` | `500` **solo si la cuenta existe**; `200` si no existe | **Revela qué correos están registrados**, lo que `ADR-010` quiere evitar |
| `POST /resend-registration-code` | Igual que el anterior para cuentas pendientes | Misma filtración |
| `POST /reset-password` | `500` aunque la contraseña **ya cambió** | La persona cree que no cambió y la repite |

## Qué dice `ADR-011` y qué se propone

`ADR-011` §«Resend fallando durante el registro» decide que `EmailService` no atrape excepciones y que el fallo se propague a un `500` genérico, con la cuenta y el código ya persistidos (estado recuperable). **Esa propiedad se conserva.** Lo que se propone cambiar es la respuesta HTTP:

- **Registro:** `201` con `email_sent: false` (campo aditivo; `true` si salió). La cuenta existe; se pide otro código con «Reenviar».
- **`forgot-password` y `resend-registration-code`:** siempre el mensaje genérico `200`, exista o no la cuenta y falle o no el envío (el texto ya es condicional: «Si existe una cuenta...»).
- **`reset-password`:** si falla solo el aviso posterior, `200` (la contraseña ya cambió).
- **Registro del fallo** (`application/email/safe_delivery.py`): tipo de correo, clase del error y `code`/`type` del proveedor. **Nunca** el cuerpo, el código de 6 dígitos, el destinatario ni el mensaje del proveedor (puede incluir direcciones).
- El aviso de acceso nuevo ya toleraba fallos (`issue_session_use_case.py`); no cambia.

## Contrapartida que hay que aceptar

La persona **no se entera** de que el correo no salió salvo en el registro (`email_sent`). Si Resend queda caído, quien pide recuperar su contraseña no recibe nada y no ve un error. Mitigación: vigilar el consumo del plan y los registros del servidor (aviso `No se pudo enviar el correo`). Los clientes web y móvil todavía **no muestran** `email_sent: false`; es un cambio de interfaz pendiente.

## Decisión

1. **Se enmienda `ADR-011`** únicamente en la respuesta HTTP cuando falla el envío del código de registro (`500` → `201` con `email_sent: false`). Se conservan sin cambios su estado recuperable (cuenta y código ya persistidos) y que `EmailService` no atrape excepciones. La enmienda queda anotada en `ADR-011`.
2. **Pendiente (no bloquea el merge):** web y móvil deben avisar «no pudimos enviar el correo, usa Reenviar» cuando `email_sent` sea `false`. Hasta entonces la persona ve el flujo normal y puede pedir otro código con «Reenviar».
3. **Operación:** vigilar el consumo del plan gratuito de Resend (100 correos/día) y el aviso `No se pudo enviar el correo` en los registros del servidor. Con el plan gratuito, el cupo de un día de pruebas intensas puede agotarse.
4. **Si el equipo rechaza esta decisión en el PR**, se revierten los archivos listados abajo y se mantiene el `500` de `ADR-011`.

## Archivos afectados

`app/application/email/safe_delivery.py` (nuevo), `send_registration_code_use_case.py`, `register_use_case.py`, `forgot_password_use_case.py`, `reset_password_use_case.py`, `interfaces/routes/auth_routes.py`; pruebas `tests/test_email_failures.py` (nuevo) y `tests/test_registration.py` (una prueba actualizada); contrato `API_CONTRACT.md` §4.1 (campo `email_sent`).
