# ADR-015 — Perfil público extendido y medios: bio, ubicación, sitio web, foto de perfil y portada

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-015-profile-media.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 27/09/2026 |
| Estado | **Propuesta — pendiente de aprobación del equipo.** Existe una implementación de referencia **sin commit** en el árbol de trabajo (ver §Estado de la implementación); no se integra hasta que este ADR se apruebe |
| Alcance | `backend/` — columnas nuevas en `users`, `POST`/`DELETE /api/users/me/avatar` y `/cover`, extensión de `PATCH /api/users/me`, `GET /api/media/<ruta>` (solo desarrollo), capa de almacenamiento de objetos. `Frontend/` — edición y visualización del perfil |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> Cierra parcialmente el punto «Perfil — PENDIENTE DE DECISIÓN» de `DATABASE_ARCHITECTURE.md` §4.B: solo lo que se enumera en §Decisión. Todo lo demás del perfil sigue pendiente (§Decisiones pendientes).

---

## Contexto

`GET`/`PATCH /api/users/me` (`ADR-002`, `ADR-003`) solo maneja `name`, `username`, `phone`, `country_code` y `birth_date`. En el Frontend, la página de perfil ya muestra biografía, ubicación, sitio web, portada y avatar, pero:

- **Bio, ubicación, sitio web, mood, intereses, canción favorita, degradé de portada y color de avatar viven en `localStorage`** (`Frontend/src/features/feed/lib/profileStorage.js`). Se pierden al cambiar de navegador o dispositivo, y ninguna otra persona puede verlos.
- **No existe foto de perfil**: `Avatar.jsx` solo dibuja iniciales.
- **La portada es solo un degradé** elegido de una lista fija; no hay subida de archivos.

El equipo va a probar la red social entre varias personas reales (chat, feed, perfiles). Un perfil que solo existe en el navegador de quien lo escribe, y sin foto, no sirve para eso.

## Problema

1. Persistir en el servidor los datos de perfil que otras personas necesitan ver (bio, ubicación, sitio web).
2. Permitir foto de perfil y portada reales, y mostrarlas donde aparece una persona (feed, comentarios, chat, notificaciones, barra superior).
3. Hacerlo sin atar el código a un proveedor: en un servicio desplegado el disco es efímero, así que el almacenamiento de archivos no puede ser el disco del servidor.

## Objetivos

- `users` guarda `bio`, `location`, `website`, `avatar_path`, `cover_path` (todas opcionales).
- Una persona sube, reemplaza y quita su foto de perfil y su portada.
- El objeto público de usuario, y el resumen de autor en posts/comentarios/conversaciones/notificaciones, exponen `avatar_url` (y el usuario propio además `cover_url`, `bio`, `location`, `website`).
- El almacenamiento es intercambiable por configuración (disco local en desarrollo; S3-compatible en staging/producción).
- Cada imagen subida se valida por contenido real y se re-codifica antes de guardarse.

## No objetivos (explícitamente fuera de este ADR)

- **No** mueve a servidor `mood`, `interests`, `favoriteTrack`, degradé de portada ni color de avatar: siguen locales y pendientes de su propio ADR.
- **No** implementa recorte interactivo en el navegador: el recorte es centrado y lo hace el servidor.
- **No** genera múltiples tamaños (miniaturas) ni usa un CDN de transformación de imágenes.
- **No** implementa moderación de contenido de imágenes.
- **No** cubre imágenes dentro de publicaciones ni video (cada uno es su propio ADR).
- **No** define política de respaldo del almacenamiento de objetos (ver §Riesgos).
- **No** expone `cover_url`/`bio`/`location`/`website` de *otras* personas: todavía no existe un endpoint de perfil público (`GET /api/users/<id>`). Solo `avatar_url` viaja en los resúmenes de autor.

## Opciones consideradas — dónde guardar las imágenes

| Opción | Descripción | Trade-off |
|---|---|---|
| A — Disco del servidor | Guardar en una carpeta del backend | Simple, pero el disco de los servicios en la nube es efímero: las imágenes se pierden en cada despliegue. Válida solo para desarrollo |
| B — Bytes dentro de PostgreSQL (`bytea`) | Una columna con el contenido | Sin infraestructura extra, pero infla la base y los respaldos, y sirve los archivos a través del backend en cada petición |
| **C — Almacenamiento de objetos S3-compatible (elegida para staging/producción)** | Supabase Storage, Cloudflare R2, AWS S3 o MinIO detrás de un puerto `MediaStorage` | Escala, sirve las imágenes directo desde el proveedor y es intercambiable: solo cambian endpoint y credenciales |

**Elegida: C detrás de un puerto, con A como adaptador de desarrollo.** El dominio y los casos de uso solo conocen `MediaStorage` (`save`/`delete`); el adaptador se elige con `STORAGE_BACKEND=local|s3`. Cambiar de proveedor no toca ningún caso de uso.

## Decisión

### Modelo de datos — extensión de `users`

Migración aditiva y reversible; todas las columnas son `nullable` y sin backfill (`NULL` = la persona no lo definió).

| Columna | Tipo | Regla |
|---|---|---|
| `bio` | `VARCHAR(160)` | Texto libre, máx. 160 |
| `location` | `VARCHAR(60)` | Texto libre, máx. 60 |
| `website` | `VARCHAR(100)` | Con o sin `http(s)://`; solo esquemas `http`/`https`; sin espacios; el host debe contener un punto |
| `avatar_path` | `VARCHAR(255)` | **Clave** del objeto (p. ej. `avatars/<uuid>.webp`), nunca una URL |
| `cover_path` | `VARCHAR(255)` | Ídem (`covers/<uuid>.webp`) |

Se guarda la *clave* y no la URL porque la URL pública depende del entorno (disco local, Supabase, R2) y de una base configurable (`MEDIA_PUBLIC_BASE_URL`); cambiar de proveedor no obliga a reescribir filas.

### Contrato API (se documentará el mismo día del PR en `API_CONTRACT.md`, `HB-001` §15.1)

**`PATCH /api/users/me`** (extendido, sin endpoint nuevo). Acepta además `bio`, `location`, `website`: cadena vacía o `null` los borra (`NULL`); se recortan espacios. Errores `400` con el formato `{ "msg": "..." }` ya vigente. Cualquier otro campo (incluidos `avatar_path`/`cover_path`) sigue siendo rechazado por la lista blanca (`ADR-003` §Seguridad).

**`POST /api/users/me/avatar`** y **`POST /api/users/me/cover`** — `multipart/form-data`, campo `file`. Auth requerida; la identidad sale solo del JWT.
```json
// Response 200
{ "user": { "...": "objeto público de usuario, ahora con avatar_url y cover_url" } }
```
- `400` — falta el archivo, o no es una imagen JPEG/PNG/WebP válida.
- `413` — supera 5 MB.
- `401` estándar.

**`DELETE /api/users/me/avatar`** y **`DELETE /api/users/me/cover`** — quitan la imagen y borran el objeto. `200` con `{ "user": { ... } }`.

**Campos nuevos en las respuestas:**
- Objeto público de usuario (`register`/`login`/`GET`/`PATCH /api/users/me`): `bio`, `location`, `website`, `avatar_url`, `cover_url` (`null` si no hay).
- Resumen de autor en posts, comentarios, conversaciones y notificaciones: `avatar_url`.

**`GET /api/media/<ruta>`** — solo se registra con `STORAGE_BACKEND=local`. Sirve archivos del directorio de uploads con `Cache-Control` inmutable y `X-Content-Type-Options: nosniff`. Con `s3` no existe: el navegador pide las imágenes directamente al proveedor.

### Procesamiento de imágenes

1. Límite de 5 MiB de archivo y de 40 millones de píxeles decodificados (defensa contra *decompression bombs*).
2. Validación **por contenido** con Pillow: solo JPEG, PNG y WebP. La extensión y el `Content-Type` declarados se ignoran.
3. Se aplica la orientación EXIF, se recorta de forma centrada (avatar 512×512; portada 1600×500) y se **re-codifica a WebP**. El archivo original nunca se guarda: se descartan EXIF/GPS y cualquier carga escondida.
4. La clave del objeto es un UUID aleatorio y **cambia en cada subida**, así la URL nueva no depende de caché vieja y el nombre no revela nada de la persona.
5. Al reemplazar o quitar, el objeto anterior se elimina *best-effort*: un fallo de borrado nunca revierte una actualización ya persistida. Si falla la escritura en base tras subir el objeto nuevo, se elimina el objeto nuevo.

### Seguridad

- Identidad solo desde `get_jwt_identity()`; nadie puede modificar la imagen de otra persona.
- La ruta local resuelve la clave y rechaza cualquier ruta fuera del directorio raíz (defensa contra *path traversal*).
- Las imágenes son **públicas por diseño** (foto de perfil, como en cualquier red social): cualquiera con la URL las ve. El nombre aleatorio evita enumerarlas, pero no es un control de acceso.
- Credenciales del proveedor (`S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`) solo por variables de entorno; `backend/.env.example` documenta los nombres sin valores (`HB-001` §20).
- `MAX_CONTENT_LENGTH` de 6 MiB como techo HTTP, para cortar subidas gigantes antes de leerlas.

### Variables de entorno nuevas

`STORAGE_BACKEND` (`local` por defecto), `UPLOAD_DIR`, `MEDIA_PUBLIC_BASE_URL`, `S3_BUCKET`, `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_REGION`. Con `STORAGE_BACKEND=s3` faltando alguna obligatoria, el backend falla al arrancar (no degrada en silencio).

## Impacto en Frontend

- `AuthContext` expone `uploadProfileImage(kind, file)` y `removeProfileImage(kind)`; cada respuesta reemplaza `user` completo (misma regla que `updateProfile`).
- `EditProfileModal`: subir/cambiar/quitar foto y portada con vista previa; nada se sube hasta pulsar «Guardar». Validación previa de tipo y tamaño (el servidor vuelve a validar). Los degradés y el color del avatar quedan como respaldo sin foto.
- `Profile.jsx`: bio/ubicación/enlace vienen del servidor; el resto sigue local. **Migración única**: si el perfil del servidor está vacío y este navegador conserva bio/ubicación/enlace de la versión anterior, se envían al servidor una vez y se limpian de `localStorage`; un valor heredado inválido no rompe la página.
- `avatar_url` se muestra en barra superior, barra lateral, tarjetas de publicación, comentarios, compositor, chat, notificaciones y ajustes.
- Se retiran `ProfileHeader.jsx` y `ProfileTopBar.jsx`, sin ninguna referencia en el código.

## Impacto en Backend

- Nuevas capas de acuerdo con `BACKEND_ARCHITECTURE.md` §17: puerto `domain/media/storage.py`; casos de uso en `application/`; adaptadores `infrastructure/media/` (Pillow y boto3 confinados ahí, mismo principio que `resend`); composition root en `create_app()`.
- `to_author_summary()` centraliza el resumen de autor y su `avatar_url`.
- Dependencias nuevas: `Pillow`, `boto3` (`requirements.txt`).
- `backend/uploads/` y `backend/*.log` se agregan al `.gitignore`.

## Estado de la implementación

Existe una implementación de referencia **sin commit ni PR** en el árbol de trabajo, con 43 pruebas de integración de perfil pasando (`tests/test_profile_media.py`, `test_update_profile.py`, `test_users_me.py`) y el build del Frontend compilando. La migración `a5c8e2d71f34` ya fue aplicada en las bases de desarrollo y de pruebas locales. No se integra a `develop` hasta aprobar este ADR.

## Riesgos

- **El adaptador S3 no se ha probado contra un proveedor real** (solo el adaptador local, por pruebas automáticas). Hay que probarlo contra Supabase Storage o R2 en staging antes de darlo por bueno.
- **Respaldos**: los respaldos de PostgreSQL no incluyen los objetos del almacenamiento. Perder el bucket dejaría filas apuntando a archivos inexistentes.
- **Objetos huérfanos**: si el borrado del objeto anterior falla, queda un archivo sin referencia (costo de almacenamiento, no de correctitud). Un barrido periódico queda como mejora futura.
- **Borrado de cuenta**: cuando exista esa funcionalidad, debe eliminar también los objetos (no existe hoy).
- **Sin moderación**: cualquier imagen válida se acepta.
- **Subidas sin límite de frecuencia**: no hay *rate limiting* en el backend (sigue pendiente, como en el resto de endpoints); conviene añadirlo antes de abrir el registro a personas ajenas al equipo.
- **Recorte centrado**: puede cortar rostros en fotos con encuadre desfavorable; el recorte interactivo queda como mejora futura.

## Decisiones pendientes (cada una es su propio ADR futuro)

- Persistencia servidor de `mood`, `interests`, `favoriteTrack`.
- Endpoint de perfil público de otras personas (`GET /api/users/<id>`) y qué campos expone.
- Miniaturas / múltiples tamaños y CDN.
- Política de respaldo y limpieza del almacenamiento de objetos.
- Moderación de imágenes.
- Elección definitiva del proveedor (Supabase Storage vs. Cloudflare R2) y del entorno de despliegue — pertenece a un ADR de entorno de *staging*, no a este.

## Consecuencias

- Los perfiles dejan de ser locales al navegador y otras personas ven la foto de quien publica, comenta o escribe.
- El proyecto incorpora una capa de almacenamiento de objetos intercambiable; cualquier medio futuro (imágenes de publicaciones, adjuntos) puede reutilizar el mismo puerto.
- Se añade una dependencia operativa nueva (un bucket) para cualquier entorno desplegado.

## Referencias

- `ADR-002-user-profile-fields.md`, `ADR-003-profile-update-contract.md` — contrato de `users` y `PATCH /api/users/me`.
- `DATABASE_ARCHITECTURE.md` §4.B — perfil, pendiente de decisión.
- `BACKEND_ARCHITECTURE.md` §17 — capas y confinamiento de dependencias externas.
- `API_CONTRACT.md` — a actualizar el mismo día del PR (`HB-001` §15.1).
- `HB-001` §11–12 (proceso de ADR), §20 (secretos).
- Código: `backend/app/infrastructure/media/`, `backend/app/domain/media/`, `backend/app/application/auth/update_profile_media_use_case.py`, `backend/migrations/versions/a5c8e2d71f34_add_profile_bio_and_media_to_users.py`, `Frontend/src/features/feed/components/EditProfileModal.jsx`.

## Cierre

Este ADR queda **propuesto**. Para aprobarlo hace falta la revisión de al menos una persona del equipo distinta de quien lo redactó (`HB-001` §11–12). Aprobado, el siguiente paso es actualizar `API_CONTRACT.md` y `DATABASE_ARCHITECTURE.md`, y abrir el PR de la implementación.
