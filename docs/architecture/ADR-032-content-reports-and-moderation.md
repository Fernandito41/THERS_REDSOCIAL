# ADR-032 — Reportes de contenido y moderación

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-032-content-reports-and-moderation.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 02/10/2026 |
| Estado | **ACEPTADO con cambios** el 2026-10-02 (ver «Decisiones del equipo»). La fase 1 está en una rama sin fusionar; el resto **no está implementado**. Redactado por Claude Code a pedido del propietario del proyecto |
| Alcance | `backend/` — tabla `reports`, columnas nuevas en `users`, `POST /api/reports`, rutas de moderación; `Frontend/` — menú «Reportar» y una página de moderación; `mobile/` — el mismo menú cuando exista contenido de usuarios |
| Relacionado | `ADR-022` (cuentas privadas), `ADR-025` (sesiones), `ADR-027` (rate limiting), **`ADR-029` (bloqueo y restricción)**, `ADR-031` (eliminación de cuenta), `docs/LAUNCH_CHECKLIST.md` |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

---

## Decisiones del equipo (2026-10-02)

El equipo revisó este ADR y lo **acepta con lo siguiente**. Donde esta sección y el resto del documento
difieran, **manda esta sección**.

### A. Quién modera

Dos personas del equipo: **Fernando** y **Cristopher**. Son las únicas con `is_moderator = true`
(asignado por línea de comandos, nunca por la API). Se cubre la decisión 1 de «Decisiones que necesitan al
equipo»; **falta fijar el plazo de respuesta** (propuesta: revisar cada reporte en 24 a 48 horas).

### B. Qué revisan y bajo qué normas

Revisan los **reportes** y también **perfiles maliciosos** o que infrinjan las normas de seguridad, aunque
nadie los haya reportado. Esto añade una vía **sin reporte** (por ejemplo `POST /api/moderation/users/<id>/warn`
y `.../suspend`), que el diseño original no tenía. **Las normas las escribe el equipo** (términos de uso y
normas de la comunidad) y deben estar publicadas **antes** de sancionar a nadie: no se puede suspender por una
regla que el usuario nunca pudo leer.

### C. Escalera de sanciones

1. **Revisión** por un moderador.
2. **Aviso o advertencia** al usuario (acción nueva `warn`; queda registrada con quién, cuándo y por qué).
3. **Suspensión** de la cuenta, tras advertencias que no se atendieron. Las faltas graves pueden saltarse
   la advertencia; **el equipo debe escribir cuáles** (propuesta: amenazas, contenido sexual con menores,
   suplantación).

### D. Apelación

- Al suspender, la persona dispone de **48 horas** para escribir a soporte por correo con las pruebas que
  demuestren que el equipo se equivocó.
- La apelación **pasa por varios filtros** (a detallar por el equipo). Recomendación: la revise **el otro
  moderador**, no quien impuso la sanción, para que nadie sea juez y parte.
- Faltan por definir: la **dirección de correo de soporte** (no existe todavía; con Cloudflare se puede
  crear una gratis por reenvío), qué ocurre si pasan las 48 horas sin contacto y el plazo en que se responde
  la apelación.

### E. Decisiones abiertas

| # | Resultado |
|---|---|
| 1 | Resuelta en A (falta el plazo) |
| 4 | Resuelta en D (faltan los detalles indicados) |
| 2, 3, 5 | **Sin respuesta todavía.** Se mantiene la recomendación del documento |

---

## Contexto

### Por qué hace falta

Google Play exige a las apps con **contenido generado por usuarios** que ofrezcan **dentro de la app** la posibilidad de **reportar y bloquear tanto usuarios como contenido**, que exijan **aceptar unos términos de uso antes de crear contenido**, que esos términos definan y prohíban el contenido censurable, y que se **actúe sobre lo reportado a tiempo**.
(Verificado el 2026-10-02 en la ayuda de Play Console, *User Generated Content* y *Understanding moderation requirements in UGC apps*. **Reverificar al enviar la app**.)

### Qué hay hoy, verificado en `develop` (`8a213c0`)

| Requisito | Estado |
|---|---|
| **Bloquear** usuarios | ✅ Resuelto y bien: `ADR-029`, aplicado en el servidor, simétrico y sin revelárselo al bloqueado |
| **Reportar** contenido o usuarios | ❌ No existe ninguna ruta ni tabla |
| **Alguien que revise** lo reportado | ❌ No existe ningún rol: `grep` de `moderator`, `is_admin` o `role` en `backend/app` no devuelve nada, y `BACKEND_ARCHITECTURE.md` §20 ítem 10 («roles y autorización») sigue abierto |
| **Aceptar los términos antes de crear contenido** | ❌ `Register.jsx` enlaza a `/terms`, pero **el backend no guarda ninguna aceptación** (ni columna en `users` ni campo en `register`) |
| Términos que definan el contenido censurable | ⚠️ Existe la página `Terms.jsx`; **no se ha revisado** que defina y prohíba contenido censurable |
| Poder **suspender** una cuenta | ❌ No existe |

El backend **ya permite crear contenido de usuarios**: posts, comentarios, mensajes y los campos de perfil (nombre, `@usuario`, bio, ubicación, sitio web, avatar, portada). La app móvil todavía no, pero el feed móvil está en la hoja de ruta: **cada superficie nueva debe nacer con «Reportar» y «Bloquear»**.

## Objetivos

- Que cualquier persona pueda **reportar** un post, un comentario, un mensaje o un perfil, en dos toques.
- Que **alguien pueda revisar** lo reportado y **actuar**: descartar, retirar el contenido o suspender la cuenta.
- Que **quede registrado** que cada persona aceptó los términos, y cuál versión.
- Que **reportar no sea un arma**: que no sirva para hostigar a alguien ni se pueda usar para averiguar quién reportó.

## No objetivos

- **No** hay detección automática (modelos de clasificación, listas de palabras).
- **No** hay **apelaciones** en la v1.
- **No** se oculta contenido automáticamente por acumular reportes: es una vía clásica de acoso en grupo.
- **No** se resuelve el modelo general de roles (`BACKEND_ARCHITECTURE.md` §20 ítem 10): este ADR introduce **una sola bandera**, `is_moderator`.
- **No** cubre el contenido ilegal grave (por ejemplo, material de abuso sexual infantil): eso tiene **obligaciones legales de denuncia** que requieren asesoría jurídica y un procedimiento propio. Se deja señalado, no resuelto aquí.

## Opciones consideradas

### Cómo revisan los moderadores

| Opción | A favor | En contra |
|---|---|---|
| A — Solo base de datos y línea de comandos | Cero interfaz | Obliga a tocar la base de producción a mano: error humano y sin trazabilidad |
| **B — Rutas de moderación y una página oculta, protegidas por `is_moderator` (elegida)** | Trazable, usa la autenticación existente, es poco código | Hay que construir la página y cuidar su acceso |
| C — Herramienta externa alimentada por correo | Nada que mantener | Los datos personales salen del sistema; poco control |

### Qué pasa cuando alguien reporta

| Opción | A favor | En contra |
|---|---|---|
| **A — Solo se guarda y un humano decide (elegida)** | Imposible de manipular por volumen | Depende de que alguien lo revise a tiempo |
| B — Ocultar tras N reportes distintos | Reacciona sola | **Se usa para hostigar:** un grupo coordinado silencia a cualquiera |

## Decisión

### 1. Modelo de datos

**Tabla `reports`:**

| Columna | Tipo | Nota |
|---|---|---|
| `id` | UUID PK | — |
| `reporter_id` | UUID → `users.id`, **`SET NULL`** | Si quien reportó elimina su cuenta (`ADR-031`), el reporte sigue |
| `target_type` | VARCHAR(10) | `post`, `comment`, `message` o `user`, validado en la aplicación |
| `target_id` | UUID | Sin clave foránea, porque apunta a tablas distintas |
| `reported_user_id` | UUID → `users.id`, **`SET NULL`** | Autor del contenido o cuenta reportada |
| `reason` | VARCHAR(20) | `spam`, `harassment`, `hate`, `sexual`, `violence`, `self_harm`, `illegal`, `impersonation`, `other` |
| `details` | VARCHAR(500) NULL | Texto libre opcional |
| `status` | VARCHAR(10) | `open`, `reviewing`, `actioned`, `dismissed`. Por defecto `open` |
| `content_snapshot` | TEXT NULL | Copia del texto reportado (ver decisión 4) |
| `created_at`, `resolved_at` | TIMESTAMPTZ | — |
| `resolved_by` | UUID → `users.id`, `SET NULL` | Qué moderador |
| `resolution_note` | VARCHAR(500) NULL | — |

`UNIQUE (reporter_id, target_type, target_id)`: reportar lo mismo dos veces es idempotente. Índice `(status, created_at)` para la cola.

**Columnas nuevas en `users`:** `terms_accepted_at` y `terms_version` (aceptación); `suspended_at` y `suspension_reason` (suspensión); `is_moderator` (booleano, por defecto `false`).

### 2. Reportar

`POST /api/reports` `{target_type, target_id, reason, details?}` (autenticado).

- **Solo se puede reportar lo que se puede ver:** se reutilizan las mismas guardias de visibilidad (`assert_post_visible`, cuentas privadas de `ADR-022`, bloqueos de `ADR-029`). Si no lo ves, responde `404`, el mismo que un inexistente: reportar **no** debe servir para confirmar que algo existe.
- No se puede reportar lo propio (`400`).
- Responde `201` y, si ya existía el mismo reporte, `200` sin duplicar.
- Un mensaje se puede reportar **solo por quien lo recibió**; el moderador ve el texto de **ese mensaje**, no la conversación entera.
- Límite de `ADR-027`: nueva regla `REPORT_CREATE`, **10 por hora** y por persona.
- **Quien reportó nunca es visible para la persona reportada.** Ninguna respuesta pública incluye `reporter_id`.
- En la interfaz, el diálogo ofrece **«Reportar y bloquear»**, que llama además a las rutas de `ADR-029`.

### 3. Moderación

Con `is_moderator = true` (se asigna **solo por línea de comandos**, nunca por la API):

| Ruta | Qué hace |
|---|---|
| `GET /api/moderation/reports?status=` | Cola ordenada de más antiguo a más nuevo, paginada |
| `POST /api/moderation/reports/<id>/resolve` `{action, note}` | `action`: `dismiss`, `remove_content` o `suspend_user` |

- `remove_content` borra el post, comentario o mensaje con las rutas de borrado que ya existen (`ADR-019`/`ADR-020`).
- `suspend_user` fija `suspended_at`, **revoca todas las sesiones** (`ADR-025`) y el login responde `403` con un mensaje propio. La persona **ve el motivo** para poder reaccionar.
- Toda resolución queda con `resolved_by`, `resolved_at` y `resolution_note`.
- Un moderador **no puede resolver un reporte sobre sí mismo** ni suspenderse a sí mismo.
- Las rutas de moderación devuelven `404` (no `403`) a quien no es moderador, para no anunciar que existen.

### 4. Qué se conserva y por cuánto tiempo

Si el contenido reportado se borra o su autor elimina la cuenta (`ADR-031`), el moderador necesita ver **qué se dijo**. Por eso `content_snapshot` guarda una copia del texto **mientras el reporte esté abierto**.

- Al resolverlo (`actioned` o `dismissed`) la copia **se pone en `NULL`**.
- No se guardan imágenes ni nombres: solo el texto reportado.
- Esto es una **retención por seguridad** y **debe declararse en la política de privacidad** (Play lo exige para cualquier dato que se retenga tras una eliminación).

### 5. Aceptación de los términos

- El registro exige marcar la aceptación (casilla obligatoria, también en el Frontend) y el backend guarda `terms_accepted_at` y `terms_version`. Sin ella, `register` responde `400`.
- Las cuentas **ya existentes** se tratan como no aceptadas: al iniciar sesión se les pide aceptar antes de crear contenido.
- Si la versión de los términos cambia, se vuelve a pedir.
- Las cuentas nuevas por **Google** (`ADR-012`): `POST /api/auth/google` crea la cuenta en **una sola llamada**, así que no hay un paso previo. El cliente envía la aceptación junto con la credencial (casilla junto al botón) y, **sin ella, no se crea la cuenta nueva**. Iniciar sesión con una cuenta de Google que ya existe no la necesita.

### 6. Lo que NO es código y hace falta

| Entregable | Responsable |
|---|---|
| **Términos de uso y normas de la comunidad** que definan y prohíban el contenido censurable | Equipo, con asesoría legal |
| **Plazo de respuesta** a los reportes (por ejemplo, 24 h para `illegal`, `self_harm` y `sexual`; 72 h para el resto). **Hay que tener quién los atienda**: el equipo son 4 personas | Equipo |
| Procedimiento para **contenido ilegal grave** y sus obligaciones de denuncia | Asesoría legal |
| Actualizar la política de privacidad (decisión 4) | Equipo |

## Decisiones que necesitan al equipo

| # | Pregunta | Recomendación |
|---|---|---|
| 1 | ¿Quién modera y con qué plazo? | Definirlo **antes** de publicar: sin alguien que atienda la cola, el requisito de Play («actuar a tiempo») no se cumple aunque el código exista |
| 2 | ¿Se conserva `content_snapshot` solo mientras el reporte está abierto? | Sí (decisión 4): es lo mínimo útil. Una retención mayor exige asesoría legal |
| 3 | ¿Se notifica a quien reportó cuando se resuelve? | **No en la v1.** Evita crear un canal para sondear qué se hizo con cada reporte |
| 4 | ¿Se permiten **apelaciones**? | Fuera de la v1; hay que decidir cómo antes de suspender cuentas a escala |
| 5 | ¿Qué se hace con las cuentas existentes que no aceptaron los términos? | Pedirles aceptar al iniciar sesión (decisión 5) |

## Seguridad

- **Reportar no es un oráculo:** `404` ante lo que no se puede ver, igual que un inexistente.
- **Anonimato de quien reporta:** nunca se expone a la persona reportada, ni por la API ni por correo.
- **Sin acciones automáticas** por volumen de reportes (opción B descartada).
- **Moderación auditada:** quién resolvió, cuándo y con qué nota; un moderador no puede actuar sobre sí mismo.
- **`is_moderator` solo por línea de comandos:** ninguna ruta pública ni de moderación lo modifica, para que una cuenta comprometida no pueda ascenderse.
- **Límite de reportes** para impedir que se use como herramienta de hostigamiento.

## Riesgos aceptados

- **Sin moderador a tiempo, el sistema solo almacena.** Es un riesgo de **operación**, no de código, y es el más serio.
- **Una cuenta de moderador comprometida** puede retirar contenido y suspender cuentas. Mitigación mínima: activar la 2FA (`ADR-026`) en esas cuentas; exigirla es una decisión pendiente.
- **Reportes falsos coordinados** siguen siendo posibles, pero no actúan solos: un humano decide.
- **Sin apelaciones**, una suspensión errónea no tiene un camino formal de revisión.

## Implementación prevista (cuando se apruebe)

1. **Fase 1 — Backend de reportes y términos:** migración (`reports` y las columnas de `users`), `POST /api/reports`, regla `REPORT_CREATE`, aceptación en `register` y en Google, pruebas.
2. **Fase 2 — Moderación:** rutas de moderación, suspensión en el login, comando para asignar `is_moderator`, pruebas (incluida la no revelación a no moderadores).
3. **Fase 3 — Web:** menú «Reportar» en posts, comentarios, mensajes y perfiles; casilla de términos en el registro; página de moderación.
4. **Fase 4 — Móvil:** el mismo menú **en cada pantalla de contenido de usuarios en cuanto exista**. Se añade como **criterio de aceptación** de la fase 3 de la hoja de ruta móvil: no se publica una pantalla de contenido sin «Reportar» y «Bloquear».
5. **Docs el mismo día** (`HB-001` §15.1): `API_CONTRACT.md`, `DATABASE_ARCHITECTURE.md`, `BACKEND_ARCHITECTURE.md` §20 ítem 10 (se documenta que la bandera `is_moderator` no cierra el modelo de roles).

## Fuentes consultadas

- Código de `develop` (`8a213c0`): `auth_routes.py`, `models.py`, `Register.jsx`, `Terms.jsx`.
- `ADR-012`, `ADR-019`, `ADR-020`, `ADR-022`, `ADR-025` a `ADR-029`, `ADR-031`.
- Play Console Help: *User Generated Content* y *Understanding moderation requirements and incidental sexual content in UGC apps* (2026-10-02).
