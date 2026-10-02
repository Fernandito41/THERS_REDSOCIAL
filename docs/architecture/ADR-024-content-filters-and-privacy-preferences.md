# ADR-024 — Filtros de contenido, privacidad de mensajes y estado de actividad

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-024-content-filters-and-privacy-preferences.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea (ver §Decisión) |
| Alcance | `backend/` — entidad `muted_keywords`, `users.hide_offensive_comments`/`who_can_message`/`show_activity_status`/`last_seen_at`, filtrado de feed y comentarios, `GET`/`POST`/`DELETE /api/users/me/muted-keywords`; `Frontend/` — `MutedKeywordsRow.jsx`, controles en Configuración › Privacidad, presencia en Mensajes |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Cierra los tres controles restantes de REF-SET-02 que `ADR-022` y `ADR-023` no cubrieron. Junta cuatro preferencias en un ADR porque comparten una migración y **un único endpoint** (`PATCH /api/users/me/privacy`), cuya forma se decide acá para las siete preferencias de la pantalla.

---

## Contexto

Tras `ADR-022` (cuenta privada) y `ADR-023` (menciones), la pantalla de Privacidad tenía cuatro controles sin resolver:

| Control | Motivo que daba la pantalla |
|---|---|
| Ocultar comentarios ofensivos | "No hay moderación de comentarios en el servidor" |
| Filtros de palabras clave personalizadas | "No hay endpoint que lo aplique" |
| Mensajes directos | "No existe mensajería en el backend" |
| Estado de actividad en el radar sonoro | "No hay sistema de presencia ni canales de audio" |

**Dos de esos motivos estaban desactualizados.** La mensajería existe desde `ADR-013` (hace dos versiones del contrato) y el texto nunca se corrigió — el control no estaba bloqueado por falta de backend, sino por falta de la capa de permisos. Y "no hay sistema de presencia" era cierto, pero "ni canales de audio" señala una función de producto entera que nadie especificó.

**Un motivo sí era un hueco real:** no hay política de moderación en `/docs` (`CLAUDE.md` §15 lo registra; `DATABASE_ARCHITECTURE.md` §4.B no tiene candidata de roles/moderación ratificada). "Ofensivo" no estaba definido en ninguna parte.

## Objetivos

- Cada persona puede filtrar términos que no quiere ver, y eso se aplica en el servidor en cada consulta.
- El dueño de una publicación puede filtrar comentarios con insultos o spam evidente en su propio espacio.
- Cada persona decide quién puede escribirle por mensaje directo.
- Se puede saber cuándo alguien estuvo activo por última vez, y se puede ocultar.
- Un contador nunca contradice la lista que acompaña.

## No objetivos (explícitamente fuera de este ADR)

- **No** implementa canales de audio. No existen: ni modelo, ni endpoints, ni interfaz. Un interruptor de privacidad sobre una función inexistente no protegería nada, así que ese control **sigue siendo `pending`**, con el motivo corregido. La parte de presencia que sí tiene sentido hoy (última vez activo) se implementa; la etiqueta se reescribe para no prometer audio.
- **No** implementa moderación humana, reportes, ni revisión caso por caso. Lo que se implementa es un filtro automático por coincidencia de términos.
- **No** convierte la lista de ofensivos en una política oficial del equipo. Es un placeholder en el repositorio, explícitamente revisable (ver §Decisión).
- **No** implementa "solicitudes de mensaje" (una bandeja aparte para desconocidos, como insinuaba el texto del control). Quien no está autorizado recibe un `403`; una bandeja de pendientes es una entidad nueva y su propio ADR.
- **No** filtra mensajes directos por palabras clave. Un chat de dos personas es una conversación consentida; filtrarla en silencio rompería el hilo sin que ninguna de las dos lo sepa.
- **No** normaliza acentos ni Unicode al comparar términos: "mañana" y "manana" son distintos a propósito.
- **No** oculta los mensajes ya recibidos al cerrar la bandeja. Cambiar la preferencia afecta a lo que llega, no a lo que llegó.

## Opciones consideradas — un endpoint de privacidad o ampliar `PATCH /api/users/me`

| Opción | Trade-off |
|---|---|
| **A — `GET`/`PATCH /api/users/me/privacy` propio (elegida)** | `PATCH /api/users/me` (`ADR-003`) es el contrato del **perfil público** y tiene reglas que no aplican a nada de acá: el cooldown de 30 días del `username`, el `409` por duplicado, la regla de que `phone` y `country_code` viajan juntos. Meter las siete preferencias ahí daría una whitelist de doce campos con dos juegos de validación mezclados en la misma route |
| B — Ampliar `PATCH /api/users/me` | Un endpoint menos, pero mezcla "quién soy" con "qué permito", que evolucionan por separado |

**Elegida: A.** Va bajo `/users/me/...` y no bajo `/privacy` porque siempre opera sobre el usuario autenticado: `me` es el recurso, la privacidad es una faceta suya.

## Opciones consideradas — qué es "ofensivo"

Sin política de moderación, había tres caminos. El propietario del proyecto eligió el primero:

| Opción | Trade-off |
|---|---|
| **A — Lista base en el repositorio, revisable por el equipo (elegida)** | El interruptor funciona de verdad. La lista vive en `domain/moderation/offensive_words.py` con un encabezado que dice explícitamente que **no es una política de moderación**, y se ajusta editando una tupla — sin migración ni endpoint, porque es configuración del producto, no dato de usuario. Mismo criterio de "placeholder explícito y revisable" que `MAX_CONTENT_LENGTH` (`ADR-004`) y `MIN_AGE_YEARS` |
| B — Reutilizar solo los términos propios de cada persona | Un único mecanismo, pero el interruptor "ofensivos" no agregaría nada y habría que quitarlo de la pantalla |
| C — Dejarlo `pending` | Honesto, pero deja el control muerto por una decisión que se puede tomar con un placeholder |

**Criterio de lo que entra en la lista:** insultos y marcadores de spam inequívocos, español e inglés. **No** entra nada que dependa del contexto o de quién habla — eso exige moderación humana, que el producto no tiene.

## Opciones consideradas — a quién filtran los dos filtros

Los dos textos de la pantalla dicen cosas distintas, y se respetan:

| Filtro | Texto de REF-SET-02 | Alcance implementado |
|---|---|---|
| Palabras clave propias | "Términos que activarían moderación silenciosa **en cualquier hilo**" | **Del espectador.** Filtran lo que ÉL ve, en todas partes. No afectan a nadie más |
| Ocultar ofensivos | "Filtrar respuestas agresivas o spam **en tus cápsulas**" | **Del dueño de la publicación.** Modera su propio espacio, para todo el que lo lea |

Son semánticas distintas porque los controles prometen cosas distintas. Un filtro de términos propios que afectara a los demás sería censura; un filtro de ofensivos que solo te protegiera a vos no serviría para moderar tu espacio.

**Exención común:** a nadie se le oculta **su propio** comentario ni su propia publicación. Sin eso, alguien escribiría un comentario, lo vería desaparecer y lo reescribiría pensando que falló.

## Opciones consideradas — `muted_keywords` como tabla

Tabla y no un array/JSON en `users`: hay que poder preguntar "¿algún término de este usuario aparece en este texto?" **desde el mismo `WHERE`** que lista publicaciones y comentarios. Con un array habría que traer la lista a Python y filtrar después, que es justo lo que rompe el `LIMIT` de la página (mismo razonamiento que `ADR-022` para el feed).

## Decisión

### Tabla `muted_keywords`

`user_id` (FK, `ON DELETE CASCADE`), `keyword` (`VARCHAR(100)`, ya normalizado a minúsculas por la aplicación), `created_at`, `UNIQUE (user_id, keyword)`. Sin índice extra: la `UNIQUE` ya lidera por `user_id`, que es el único patrón de acceso real (mismo razonamiento que `likes`, `ADR-005` §Índices).

**Normalización en un solo lugar** (`domain/moderation/keyword_matching.py`): trim + minúsculas. La usan tanto el camino de escritura (guardar) como el de lectura (buscar, con `ILIKE`). Si fueran dos criterios distintos, se podría guardar un término que nunca llega a encontrarse.

**Coincidencia por subcadena**, no por palabra completa: filtrar "spoiler" también oculta "spoilers". El efecto colateral conocido es que un término corto puede coincidir dentro de otra palabra.

**Límites:** 60 caracteres por término, 100 términos por persona. El segundo existe porque cada término se evalúa como un `ILIKE` en las consultas de lectura: una lista sin tope degradaría el feed de quien la tenga. Se traduce a `409`, no a `400` — el pedido es válido, choca con el estado del recurso (mismo criterio que `UsernameAlreadyExistsError`, `ADR-003`).

### `GET`/`POST`/`DELETE /api/users/me/muted-keywords`

Las tres devuelven **la lista completa** (`{"muted_keywords": [...]}`), también el `POST` y el `DELETE`: la pantalla siempre muestra la lista entera, así que devolverla ahorra una segunda petición (mismo criterio que `PATCH /api/posts/<id>`, `ADR-021`).

- `POST` → `200`, no `201`: es idempotente, agregar un término que ya tenías devuelve el mismo estado (mismo criterio que `POST .../like`, `ADR-005`).
- `DELETE` → **lleva el término en el body**, no en la URL. Es el único `DELETE` del proyecto con body, y es por un motivo concreto: un término puede contener espacios, acentos y `/`, y meterlo en el path obligaría a *percent-encoding* en los dos lados para nada.

### El predicado de visibilidad de comentarios, compartido

`_visible_comment_predicate(viewer_id, muted_keywords)` en el adaptador de comentarios es la **única** definición del filtro, y la comparten `list_for_post` y `counts_for_posts` a propósito: si cada una tuviera la suya, el contador de la tarjeta diría 5 y el panel mostraría 3. **Un contador que no coincide con su lista es un bug visible, no una optimización.**

El filtro de ofensivos se correlaciona con el **autor de la publicación** (`EXISTS` sobre `posts`→`users`), no con el espectador — es su flag el que decide.

Para el feed, `list_recent` suma la condición de términos propios al `WHERE` que `ADR-022` ya había introducido.

### `users.who_can_message` — `VARCHAR(20) NOT NULL DEFAULT 'everyone'`

Mismo vocabulario que `who_can_mention` (`domain/privacy/audience.py`, `ADR-023`). **Dirección de `'followers'`:** quien escribe tiene que seguir al destinatario — es el destinatario el que pone la condición sobre su propia bandeja. Una solicitud pendiente (`ADR-022`) **no alcanza**.

Se traduce a **`403`, no `404`**, y es la excepción deliberada al criterio de `ADR-022`: quien escribe ya sabía que esa cuenta existe (le estaba escribiendo), así que mentirle con un `404` no protegería nada y solo lo haría reintentar. Lo que la preferencia protege es la bandeja, no la existencia de la cuenta.

### `users.show_activity_status` (`DEFAULT true`) y `users.last_seen_at` (nullable)

`show_activity_status` es la única preferencia de este ADR que nace **abierta**. Es deliberado y seguro: hasta ahora no existía ningún dato de presencia, así que activarla no expone nada retroactivo — `last_seen_at` arranca en `NULL` para todo el mundo y solo se llena con actividad posterior a la migración.

**Cómo se registra:** un hook `after_request` (`interfaces/activity_tracker.py`) marca `last_seen_at` en cualquier petición autenticada que resuelve bien. Va en el hook y no en cada caso de uso para que ningún endpoint nuevo se olvide de hacerlo — que es exactamente el tipo de cosa que se olvida al agregar el endpoint número veinte.

- `after_request` y no `before_request`: si la petición falla con `401`, no hubo actividad real que registrar.
- **Throttle de 5 minutos en el propio `WHERE` del `UPDATE`**, no en memoria del proceso: así funciona igual con varios *workers*, que es justo donde un caché en memoria fallaría. (El indicador de "escribiendo" de `ADR-014` aceptó esa limitación porque es efímero; `last_seen_at` se persiste.) Sin esto, el *polling* del chat cada 4 s generaría un `UPDATE` por petición.
- Un fallo del hook **nunca** tumba la respuesta: la presencia es cosmética.

**Dónde se expone:** en `user.last_seen_at` de `GET /api/conversations` — donde la presencia importa. Llega en `null` cuando la otra persona lo oculta **o** cuando nunca registró actividad: los dos casos son indistinguibles a propósito, porque si solo se omitiera al estar oculto, el hecho de faltar delataría que alguien lo apagó.

Acá **sí viaja el timestamp**, a diferencia de `read`/`edited` que se exponen como booleanos: "activo hace 3 horas" necesita la hora, y un booleano obligaría al servidor a decidir el umbral en vez del Frontend.

En `GET /api/users/me/privacy` se expone siempre, aunque esté oculto: lo que la preferencia oculta es que lo vean **los demás**.

### Seguridad

- Whitelist de preferencias **declarada como dato** (`_BOOLEAN_FIELDS`/`_AUDIENCE_FIELDS` en `privacy_routes.py`), no como una cadena de `if`s: agregar una preferencia es una línea, y es imposible que se cuele una columna que no esté en esas tuplas.
- Los booleanos se validan con `isinstance(value, bool)`, no por *truthiness*: aceptar el string `"false"` (que en Python es verdadero) dejaría a alguien creyendo que cerró su cuenta cuando la abrió.
- `is_allowed` **deniega por defecto**: un valor inesperado en la columna nunca abre permisos.
- `user_id` sale siempre de `get_jwt_identity()`; `muted_keyword_repository.remove` lleva `user_id` en el `WHERE`, así que nadie puede borrar un término de otra persona.

## Impacto en Frontend

- **`usePrivacySettings.js`** (nuevo): carga y actualiza las siete preferencias. Actualización optimista con rollback — un control de privacidad que parece tardar invita a tocarlo dos veces. **No pasa por `localStorage`**, a diferencia de `settingsStorage.js`: estas sí se aplican en el servidor, y guardarlas localmente sería el problema que aquel archivo documenta.
- **`MutedKeywordsRow.jsx`** (nuevo): editor de términos con chips.
- **`SettingsPrimitives.jsx`**: `SwitchRow`/`ChoiceRow` ganan `hint` configurable (el fijo "Se guarda en este navegador" dejó de ser cierto para estas filas) y `disabled`; `ChoiceRow` acepta `{value, label}` para mostrar "Cualquiera" donde el servidor entiende `'everyone'`.
- **`settingsSections.js`**: la sección de Privacidad se reescribe. El aviso pasa de `warning` ("nada se aplica en el servidor") a `info`, y el único control que queda `pending` es el de audio, con el motivo corregido.
- **`Messages.jsx`**: cabecera del hilo muestra "Activo hace X". "Escribiendo" tiene prioridad: decir las dos cosas a la vez sería contradictorio.

## Impacto en Backend

- `migrations/versions/e7b2d4f8c916_add_content_filters_dm_privacy_and_activity.py` (nueva).
- `domain/moderation/`: `keyword_matching.py`, `offensive_words.py`, `repositories.py`, `exceptions.py` (nuevos).
- `infrastructure/persistence/models.py`: modelo `MutedKeyword` y cuatro columnas en `users`.
- `infrastructure/persistence/repositories/muted_keyword_repository.py` (nuevo); el de comentarios gana el predicado compartido; `user_repository` gana `touch_last_seen`.
- `application/moderation/muted_keywords_use_case.py` (nuevo).
- `application/messages/send_message_use_case.py`: respeta `who_can_message`.
- `interfaces/activity_tracker.py` (nuevo), registrado en el *app factory*.
- `interfaces/routes/privacy_routes.py`: los cinco endpoints de este ADR y de `ADR-022`.
- Tests de integración en `tests/test_privacy.py` (`TestMutedKeywords`, `TestHideOffensiveComments`, `TestWhoCanMessage`, `TestActivityStatus`).

## Riesgos

- **La lista de ofensivos no es una política.** Tiene falsos positivos (coincidencia por subcadena) y falsos negativos (cualquier variación ortográfica la evade). Es un placeholder que funciona, no moderación. Mientras el equipo no apruebe una política, es lo que hay y está marcado como tal en el propio archivo.
- **Coste de los `ILIKE` en las consultas de lectura.** Cada término propio y cada término de la lista del sistema es un `ILIKE` adicional en el `WHERE` del feed y de los comentarios. El tope de 100 términos acota lo peor, pero no se midió con volumen real — el proyecto no tiene entorno de carga (`CLAUDE.md` §15).
- **Moderación silenciosa.** Un comentario filtrado por el flag del dueño desaparece para todos sin avisar a nadie salvo a su autor, que sí lo sigue viendo. Es lo que el control promete ("moderación silenciosa"), pero significa que alguien puede estar hablándole a una pared sin saberlo.
- **`last_seen_at` revela un patrón de uso.** Aunque se pueda ocultar, el default es visible, y "activo hace 2 minutos" es información sensible para quien no quiera ser localizable. Mitigado por el interruptor y por el `null` indistinguible, no eliminado.
- **El throttle de 5 minutos hace que la presencia sea aproximada.** "Activo hace 1 minuto" puede significar "hace 5". Es el precio de no escribir en cada petición.
- **Sin *rate limiting*** en ninguno de los endpoints nuevos, coherente con el resto del proyecto (`API_CONTRACT.md` §9).

## Decisiones pendientes (cada una es su propio ADR futuro)

- **Política de moderación real** del equipo, que reemplace la lista placeholder. Es la decisión más importante que este ADR deja abierta.
- Canales de audio como función de producto (y solo entonces, su control de privacidad).
- Bandeja de solicitudes de mensaje para desconocidos.
- Reportar contenido o personas.
- Normalización de acentos/Unicode al comparar términos.
- Filtrar `GET /api/notifications` por términos propios.
- *Rate limiting* (transversal).

## Consecuencias

- **`DATABASE_ARCHITECTURE.md` cambia** (tabla `muted_keywords`, cuatro columnas en `users`) → v0.19.
- `API_CONTRACT.md` se actualiza el mismo día (`HB-001` §15.1) → v0.23. `POST /api/users/<id>/messages` gana un `403`; `GET /api/conversations` gana `user.last_seen_at`; `comments_count` y los listados pasan a depender de quién pregunta.
- **Dos motivos desactualizados de la pantalla quedan corregidos**: la mensajería existía desde `ADR-013`, y la presencia se separa de los canales de audio.

## Referencias

- `docs/architecture/ADR-013-messages-minimal-model.md`, `ADR-014-messages-ux-improvements.md` — la mensajería que el control decía inexistente.
- `docs/architecture/ADR-006-comments-minimal-model.md` — los comentarios que este ADR filtra.
- `docs/architecture/ADR-003-profile-update-contract.md` — el `PATCH` cuyo alcance este ADR decide no ampliar.
- `docs/architecture/ADR-022-private-accounts.md`, `ADR-023-mentions.md` — los otros dos ADR de la misma pantalla; de `ADR-023` sale el vocabulario de audiencias.
- `CLAUDE.md` §15 — el hueco de política de moderación que este ADR no cierra.

---

## Cierre

La pantalla de Privacidad queda con cinco de sus seis controles aplicándose de verdad en el servidor. El sexto sigue sin soporte, pero ahora el motivo es el correcto: no falta un endpoint, falta la función de producto que gobernaría. Y la decisión de fondo que queda abierta no es técnica — es qué considera THERS que es un comentario ofensivo.
