# ADR-030 — Preferencias de contenido y feed

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-030-content-preferences.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 01/10/2026 |
| Estado | **Aceptada** — implementada en esta tarea, a pedido del propietario del proyecto. Pendiente de la revisión humana que exige `HB-001` §19 |
| Alcance | `backend/` — `posts.is_sensitive`, `users.hide_sensitive_content`, entidad `muted_topics`, filtros del feed, `GET`/`POST`/`DELETE /api/users/me/muted-topics`, `GET /api/users/suggestions`; `Frontend/` — la sección «Preferencias de contenido y feed» (REF-SET-12), el composer, la tarjeta de publicación y el panel «Personas que resuenan» |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

---

## Contexto

La sección REF-SET-12 tenía cuatro controles. Al revisarlos, **uno de los motivos que daba la pantalla ya no era cierto**:

| Control | Lo que decía la pantalla | Estado real antes de este ADR |
|---|---|---|
| Filtrar contenido sensible | «No existe clasificación de contenido en el servidor» | Cierto |
| Lista de palabras ocultas | «El feed no admite filtros: `GET /api/posts` devuelve la lista completa» | **Falso desde `ADR-024`**: `muted_keywords` existe, filtra en SQL y la pantalla de Privacidad lo usa. Solo faltaba mostrarlo acá |
| Temas silenciados | «No existe el modelo de temas ni etiquetas» | Cierto |
| Mostrar cuentas sugeridas | «Controla el panel… que hoy usa datos de ejemplo» | Era un interruptor local que **no controlaba nada**: ningún componente leía `content.suggestions`, y el panel eran cinco personas inventadas |

## Qué no se toca

**Las palabras ocultas ya funcionaban** (`ADR-024`: tabla, endpoints, filtro en el `WHERE`, componente `MutedKeywordsRow`). Este ADR **no modifica nada de eso**: solo coloca la misma fila en esta pantalla, que seguía marcándola como no disponible por un texto desactualizado.

## Objetivos

- Contenido sensible: que alguien pueda marcar lo que publica y que otros puedan elegir no verlo — aplicado en el servidor.
- Temas silenciados: poder silenciar un hashtag y que desaparezca del feed — aplicado en el servidor.
- Cuentas sugeridas: que el panel muestre cuentas reales y que el interruptor lo controle de verdad.

## No objetivos

- **No hay clasificación automática de contenido sensible.** Ni modelo de IA ni moderación: `is_sensitive` es lo que el **autor declara**. Es la única fuente honesta con lo que el producto tiene hoy, y la pantalla lo dice.
- **No hay entidad de temas ni de hashtags.** Un tema se reconoce dentro del texto de la publicación; no hay tendencias, página de un tema ni búsqueda por etiqueta.
- **«Temas en tendencia» sigue siendo de ejemplo** (otro módulo del rail, fuera de esta pantalla), y sigue rotulado así.
- **No se puede editar la marca de sensible** de una publicación ya creada (`PATCH /api/posts/<id>` solo edita `content`, `ADR-021`). Quedaría para un ADR propio.
- **No hay algoritmo de recomendación** en las sugerencias: es un orden simple y explicable (ver abajo).

## Decisión

### 1. Contenido sensible

| Cambio | Detalle |
|---|---|
| `posts.is_sensitive` | `BOOLEAN NOT NULL DEFAULT false`. Lo fija el autor en `POST /api/posts` (campo opcional `is_sensitive`, **solo booleano real**: `"false"` como texto se rechaza con `400`, porque en Python es verdadero) |
| `users.hide_sensitive_content` | `BOOLEAN NOT NULL DEFAULT false`. Se edita con `PATCH /api/users/me/privacy`, el mismo endpoint y la misma whitelist que el resto de preferencias de privacidad (`ADR-022`/`ADR-023`/`ADR-024`) |
| Filtro | `GET /api/posts` omite los posts con `is_sensitive` **si** el espectador activó el filtro. En el `WHERE`, no en Python, por el mismo motivo que `ADR-022` (filtrar después del `LIMIT` devolvería páginas cortas). La preferencia se lee con una subconsulta escalar sobre `users`, sin cambiar la firma de `list_recent` |
| Excepciones | **Su propio post nunca se le oculta a su autor**, mismo criterio que los términos filtrados (`ADR-024`) |
| `is_sensitive` en la respuesta | Se expone en cada post (`to_public_post`) |

Ambas columnas nacen en `false`: ninguna publicación existente pasa a ser sensible y a nadie se le oculta nada por efecto de la migración.

**Quien no activó el filtro** sí recibe la publicación, pero el Frontend oculta el texto detrás de «Mostrar de todos modos». El servidor no decide eso: es presentación.

### 2. Temas silenciados

Tabla `muted_topics (id, user_id → users CASCADE, topic VARCHAR(50), created_at)` con `UNIQUE (user_id, topic)`.

| Decisión | Motivo |
|---|---|
| **Tabla propia, no reutilizar `muted_keywords`** | Una palabra se busca como **subcadena** (`spoiler` oculta `spoilers`). Un tema se busca como **etiqueta completa**: silenciar `#viaje` no debe ocultar `#viajes` |
| **El tema es un hashtag reconocido en el texto** | El producto no guarda etiquetas. Reconocerlas en `content` evita una entidad, una migración de datos y un parser que mantener en sincronía al editar |
| **Regex en SQL**: `content ~* '(^\|[^[:alnum:]_])#' \|\| topic \|\| '([^[:alnum:]_]\|$)'` | Va en el `WHERE` (misma razón que arriba). Sin distinguir mayúsculas; reconoce la etiqueta al principio, en medio o al final, seguida de puntuación |
| **El tema solo puede ser `\w+`** (letras con acentos, dígitos, `_`), máx. 50 | Así la columna **no puede contener metacaracteres de regex**: no hay nada que escapar y no existe inyección de patrón |
| **Normalización**: sin `#`, minúsculas, trim | `#Viajes`, `viajes` y ` VIAJES ` son el mismo tema. No se quitan acentos: `música` ≠ `musica` |
| **Tope de 50 temas por persona**, `409` al pasarse | Cada tema es una condición más en la consulta del feed. Repetir uno existente no choca con el tope |
| **El propio post nunca se oculta** | Mismo criterio que las palabras ocultas |

Los endpoints replican la forma de `muted-keywords` (`ADR-024`): cada respuesta devuelve la lista completa, y el tema viaja en el body también en el `DELETE`.

### 3. Cuentas sugeridas

`GET /api/users/suggestions` devuelve hasta **5** cuentas reales:

- **Excluye:** la propia, a quien ya sigue **o ya le pidió seguir** (cualquier estado), y a cualquiera con un **bloqueo en cualquier sentido** (`ADR-029`) — sugerir la cuenta que bloqueaste, o a quien te bloqueó, deshace el bloqueo en la práctica.
- **Orden:** más seguidores aceptados primero; a igualdad, la más reciente. Simple y explicable; no pretende ser una recomendación personalizada.
- **Forma reducida:** `{id, name, username, is_private}`. Nunca email ni teléfono.
- **El botón de seguir actúa sobre el endpoint real** (`ADR-007`/`ADR-022`): refleja «Siguiendo» o «Solicitado» según responda el servidor.

El interruptor «Mostrar cuentas sugeridas» **sigue siendo una preferencia local** (en el navegador) y ahora sí controla el panel. Es una decisión consciente: mostrar u ocultar un panel es presentación pura, no protege ningún dato ni es una regla de servidor, así que no justifica una columna ni un endpoint.

## Opciones consideradas

| Opción | Trade-off |
|---|---|
| **Sensible: lo declara el autor (elegida)** | Honesto, sin infraestructura. Depende de que la gente marque lo suyo |
| Sensible: clasificación automática | Requiere un modelo de moderación que el proyecto no tiene, con falsos positivos que ocultarían contenido legítimo |
| **Temas: hashtag reconocido en el texto (elegida)** | Sin entidad nueva. El tema existe solo mientras aparece en algún post |
| Temas: tabla `hashtags` + `post_hashtags` | Habilitaría tendencias y páginas de tema, pero es un modelo entero que nadie pidió, y habría que mantenerlo en sincronía al editar y borrar |
| Temas: reutilizar `muted_keywords` | Subcadena en vez de etiqueta completa: `#viaje` ocultaría `#viajes` |
| **Sugerencias: orden por seguidores (elegida)** | Explicable y barato |
| Sugerencias: servicio de recomendación | No existe, y inventar una señal («amigos de amigos») sin datos que la respalden sería ruido |

## Riesgos asumidos

- **Depende de que el autor marque su contenido.** Un post sensible sin marcar se ve igual para todos. Es la limitación de no tener moderación, y la pantalla lo dice.
- **El filtro de temas es una regex por fila de `muted_topics` sobre `posts.content`.** Con 50 temas es una evaluación de hasta 50 patrones por post candidato. Acotado por el tope y por el `LIMIT` del feed; **no usa índice** (como el `ILIKE` de `ADR-024`). Si el feed crece, la salida es la tabla de hashtags de la opción descartada.
- **La clase `[[:alnum:]]` de PostgreSQL depende de la configuración regional de la base** para reconocer letras con acentos. Con la configuración por defecto del contenedor (`en_US.utf8`) las reconoce; una base creada con `C` trataría `#música` distinto. Hay una prueba que lo verifica con `#música`.
- **La marca de sensible no se puede quitar ni poner** después de publicar. Quien se equivoca tiene que borrar y volver a publicar.
- **Las sugerencias dejan a la persona ver quién existe.** Es una lista reducida de cuentas ya visibles en el feed; no expone datos privados, pero sí incluye cuentas privadas (con «Solicitar»). Se acepta: el username de una cuenta privada ya es público en la plataforma.
- **El interruptor de sugerencias es local**: no se sincroniza entre dispositivos.

## Contrato

Ver `API_CONTRACT.md` §4.15.

## Verificación

`backend/tests/test_content_preferences.py` — 32 pruebas contra PostgreSQL real, **sobre lo que devuelve el feed**, no solo sobre los endpoints:

- **Sensible:** por defecto no es sensible; el autor la marca; rechaza no-booleanos; la preferencia se guarda; sin filtro todos la ven; con filtro desaparece del feed; el autor nunca pierde la suya; desactivar la restituye.
- **Temas:** autenticación; alta, listado y baja; normalización de `#`, mayúsculas y espacios; idempotencia; rechazo de temas inválidos; `404` al quitar uno inexistente; aislamiento entre cuentas; tope de 50; el feed oculta por tema; **la etiqueta se compara completa, no por prefijo**; mayúsculas y bordes del texto; acentos; el propio post no se oculta; quitar el tema lo restituye; las palabras ocultas de `ADR-024` siguen funcionando junto a los temas.
- **Sugerencias:** autenticación; solo cuentas reales y nunca la propia; forma reducida; excluye seguidas y solicitadas (incluida una cuenta privada); excluye bloqueos en ambos sentidos; orden por seguidores; máximo 5.
