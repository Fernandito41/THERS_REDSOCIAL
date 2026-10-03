# Plan de ramas y PR (2026-10-02)

Documento operativo, **no oficial** (no es un ADR ni sustituye a `HB-001`). Ordena el trabajo
pendiente para que el equipo avance en paralelo sin pisarse. Todas las ramas parten de
`develop` (tras el PR #68) y siguen `HB-001` §7–9: un PR resuelve una sola cosa, mínimo una
aprobación humana, el autor no se autoaprueba.

## 1. Mapa de ramas

### Cadena de base de datos (se fusiona **en este orden**; comparten la cadena de migraciones)

| # | Rama | Base | Migración (hija de) | Contenido | ADR |
|---|---|---|---|---|---|
| D1 | `feature/backend-terms-and-reports` | `develop` | `a8d2f5c1b937` | Aceptación de términos y reportes de contenido | 032, 033 |
| D2 | `feature/child-safety-standards` | D1 | `b6e1d9a4c2f8` (`a8d2f5c1b937`) | Motivo `child_safety`, prioridad `critical`, página pública `/child-safety` | 038 |
| D3 | `feature/account-deletion` | D2 | `c3f7a9d2e841` (`b6e1d9a4c2f8`) | Eliminación de cuenta (web + backend) | 031 |
| D4 | `feature/chat-sync-backend` | D3 | `d4a9b6c1e275` (`c3f7a9d2e841`) | `client_id` idempotente y paginación del chat | 035 |

Cada PR de la cadena se abre contra la rama anterior hasta que esa se fusione; después se
reapunta a `develop`. **No** reordenar: las migraciones se encadenan y un orden distinto crea
dos `head`.

### Ramas independientes (cualquier orden, salvo los conflictos de §3)

| Rama | Contenido | ADR |
|---|---|---|
| `feature/minimum-age-18` | Solo mayores de 18, puerta `profile_completed` en el servidor, script de auditoría | 034 |
| `feature/mobile-feature-parity` | Toda la app móvil: pestañas, publicaciones, chat, ajustes, registro, eliminar cuenta | — |
| `feature/email-sender-and-reply-to` | `EMAIL_REPLY_TO` y `reply_to` en Resend | — |
| `feature/email-provider-failures` | Fallos del proveedor de correo (`email_sent`) | 036 (**propuesto, contradice ADR-011**) |
| `feature/data-retention` | Purga de datos de sesión a 90 días | 037 |
| `docs/legal-drafts-and-branch-plan` | Este documento y los borradores legales | — |

`integration/launch-candidate` es un **ensayo**: reúne todo lo anterior para comprobar que
encaja. No se abre PR de esa rama.

## 2. Reglas que no se negocian

- **Un solo `head` de Alembic.** Antes de abrir un PR: `python -m flask db heads` debe mostrar
  un único valor. Quien añada una migración después de D4 la cuelga de `d4a9b6c1e275`.
- **Números de ADR:** 039 en adelante están libres. Reservar el número en el PR, no después.
- **`API_CONTRACT.md` se actualiza el mismo día** (`HB-001` §15.1). Es el archivo que más
  conflictos da: ver §3.
- **Textos legales:** `docs/legal/` son **borradores NO publicables**. Los revisa un abogado
  antes de salir en la web o en Play.
- **Sin secretos** en commits, logs ni documentación. La clave de Resend que se pegó en un
  chat debe **rotarse**.

## 3. Conflictos esperados (ya ensayados en `integration/launch-candidate`)

| Archivo | Entre | Resolución |
|---|---|---|
| `docs/architecture/API_CONTRACT.md` (cabecera de versión y numeración §4.19/§4.20/§4.21) | D3, `minimum-age-18`, `email-provider-failures` | Conservar **todas** las secciones; renumerar y dejar la versión más alta |
| `backend/app/interfaces/routes/auth_routes.py` (retorno de `register`) | D1 (términos) y `email-provider-failures` | Conservar el bloque de términos **y** `email_sent` |

Ningún otro conflicto apareció al fusionar todas las ramas. Fusionar `develop` en la rama antes
de pedir revisión si otro PR entró primero (sin `force-push`).

## 4. Qué puede hacer cada persona en paralelo

| Frente | Quién | Trabajo | Toca código |
|---|---|---|---|
| Revisión de PR | quien no sea autor | Revisar D1→D4 en orden; la cadena exige 4 aprobaciones | No |
| Infra / despliegue | integrante de DevOps | Supabase, Render, Cron Job de purga (`scripts/purge_expired_data.py`), variables de entorno, SSL, `ADR-018` | No (docs/infra) |
| Legal | responsable legal | Revisión abogada de `docs/legal/`, rutas de correo de `@thersweb.com` | No |
| QA | cualquiera | Probar la app móvil en el teléfono y `integration/launch-candidate` | No |
| Diseño | diseño | UI/UX móvil pendiente de enviarse | No |
| Producto | todos | Panel de moderación (siguiente punto del plan), UI de reportes en web, guías de comunidad | Sí, ramas nuevas desde `develop` |

## 5. Zonas a no tocar sin avisar

- `backend/migrations/versions/` (cadena de D1–D4).
- `backend/app/infrastructure/persistence/models.py` (todas las ramas añaden al final).
- `API_CONTRACT.md` y `DATABASE_ARCHITECTURE.md` (cabecera de versión).
- `mobile/` mientras `feature/mobile-feature-parity` esté abierta.

## 6. Riesgos conocidos

- **ADR-036 contradice ADR-011** (respuesta cuando falla el correo): requiere decisión del
  equipo antes de fusionar `feature/email-provider-failures`.
- **`/child-safety` promete capacidades de moderación que aún no existen** (retirar contenido,
  suspender cuentas). No registrar esa URL en Google Play hasta tener el panel de moderación.
- **La verificación de edad es declarativa** (fecha de nacimiento), no documental.
- La web sigue sin usar el refresh token: su sesión muere a los 15 minutos (`ADR-017`).
