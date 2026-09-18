# THERS — Matriz de integración UI ↔ datos

Última actualización: 2026-09-15 · Etapas A, B, C, D (parcial) y G completadas

Los dos ejes se reportan **por separado** (archivo maestro §1.1): que una pantalla compile no demuestra ninguno de los dos.

- **Visual**: pendiente / parcial / verificada — comparación contra la referencia canónica.
- **Funcional**: pendiente / parcial / verificado — acciones reales contra el backend.

---

## 1. Estado por módulo

| Módulo | Ruta | Referencia | UI | Visual | Datos | Funcional |
|---|---|---|---|---|---|---|
| **Shell global** | (todas) | REF-FEED-01 + 24 | implementada | **verificada** (6 viewports) | sesión real | **verificado** |
| **Inicio / Feed** | `/feed` | REF-FEED-01 | implementada | **verificada** (6 viewports) | API real + fixture rotulado | **parcial** |
| **Buscar** | `/search` | REF-SEARCH-01 | implementada | **verificada** (1440) | **API real** (filtrado en cliente) | **verificado** (9 casos) |
| **Videos / Cortos** | `/videos` | sin captura dedicada | marcador honesto | n/a | — | pendiente |
| **Cápsulas** | `/capsules` | sin captura dedicada | marcador honesto | n/a | — | pendiente |
| **Radar** | `/radar` | REF-RADAR-01/02 | marcador honesto | pendiente | — | bloqueado (sin proveedor) |
| **Mensajes** | `/messages` | REF-MSG-01..05 | heredada | pendiente | fixture | bloqueado (sin endpoints) |
| **Notificaciones** | `/notifications` | sin captura dedicada | heredada | pendiente | **API real** | **verificado** (en uso por el shell) |
| **Perfil propio** | `/profile` | REF-PROFILE-01 | implementada | **verificada** (3 viewports) | API real + local | **parcial** |
| **Perfil ajeno** | *sin ruta* | REF-PROFILE-02/03 | no iniciada | pendiente | — | pendiente |
| **Configuración** | `/settings/:section` | REF-SET-01..12 | **implementada (12/12)** | **verificada** (1440/390) | local + 2 endpoints reales | **verificado** (8 casos) |

«Heredada» = la pantalla que ya existía en el repositorio sigue funcionando con los tokens anteriores; todavía no se ha migrado al nuevo diseño.

---

## 2. Endpoints conectados

Verificados en ejecución real contra Flask + PostgreSQL 16 (Docker) durante esta sesión.

| Endpoint | Consumidor | Estado |
|---|---|---|
| `POST /api/register` | `Register.jsx` | funcionando — usuario de QA creado (201) |
| `POST /api/login` | `Login.jsx` / `AuthContext` | funcionando — login por la UI real (200) |
| `GET /api/users/me` | `AuthContext` | funcionando — alimenta identidad del shell |
| `PATCH /api/users/me` | `Profile.jsx` | sin regresión introducida; no reprobado esta sesión |
| `GET /api/posts` | `AppShell` → Feed | funcionando (200) — 10 posts renderizados |
| `POST /api/posts` | `CreateCapsuleFlow` | funcionando (201) — 2 posts creados en QA |
| `POST`/`DELETE /api/posts/<id>/like` | `CapsuleCard` | conectado, optimista con rollback |
| `GET`/`POST /api/posts/<id>/comments` | `CapsuleCard` | conectado, carga bajo demanda |
| `POST`/`DELETE /api/users/<id>/follow` | `CapsuleCard` | conectado, optimista con rollback |
| `GET /api/notifications` | `AppShell` | funcionando (200) — alimenta el punto de no leídas |
| `PATCH /api/notifications/<id>/read` | `Notifications.jsx` | conectado, optimista con rollback |
| `POST /api/forgot-password` | `ForgotPassword.jsx` + `Configuración > Seguridad` | **conectado y probado**; el correo real requiere `RESEND_API_KEY` |
| `POST /api/reset-password` | `ResetPassword.jsx` | existe; no reprobado esta sesión |
| `POST /api/send-verification-email` | `Configuración > Seguridad` | conectado: usa `email_verified` real de la sesión |
| `POST /api/verify-email` | consumido por `ResetPassword`/enlace de correo | backend listo |

**Ninguna función real fue sustituida por un mock.** Cuando falta el endpoint, la UI lo dice.

---

## 3. Capacidades sin backend — comportamiento actual

Dibujadas en las referencias, sin contrato que las respalde. Todas se muestran **deshabilitadas con explicación accesible**, nunca simuladas:

| Capacidad | Dónde aparece | Comportamiento hoy |
|---|---|---|
| Foto / Cápsula / Audio / Lugar en el compositor | Feed | Botones deshabilitados + `sr-only` explicando que falta soporte |
| Guardar (`bookmark_add`) | Tarjeta de publicación | Íd. |
| Compartir (`share`) | Tarjeta de publicación | Íd. |
| Momentos | Feed | Fixture rotulado «(ejemplo)» en pantalla |
| PULSE | Feed | Fixture rotulado «(ejemplo)»; sin contador de actividad en vivo |
| Personas sugeridas | Rail | Fixture + nota «sin endpoint de sugerencias todavía» |
| Temas en tendencia | Rail | Fixture + nota «sin endpoint de tendencias todavía» |
| Cápsulas recomendadas | Rail | Estado vacío honesto, sin recomendación inventada |
| Mensajes (contador) | Sidebar / bottom-nav | No se dibuja ningún número |
| Colecciones Destacadas | Perfil | Sección conservada con estado vacío honesto; «+ Nueva» deshabilitado |
| Tab «Destacadas» | Perfil | Estado vacío: no existe el modelo que las guardaría |
| Tab «Me gusta» | Perfil | Aviso «Solo tú» reproducido + estado vacío: el like se registra (ADR-005) pero no se puede recuperar como colección |
| Actividad del Perfil, Nodos, Conexiones Mutuas | Rail del perfil | Estado no disponible explicado en cada tarjeta |
| Portada fotográfica | Perfil | Se conserva el sistema de degradados ya existente: no hay subida de archivos |
| «Audio Espacial 48kHz · Lossless» | Portada del perfil | **No se dibuja** — §8.7 exige capacidades de audio reales |

---

## 4. Contratos que harían falta

Formato del archivo maestro §16.2. **Propuestas, no implementadas.** No se han añadido a `API_CONTRACT.md` ni a la colección de Postman.

```text
Capacidad: Guardar / marcar publicación
Pantallas consumidoras: Feed, Perfil, Buscar
Endpoint existente inspeccionado: ninguno
Propuesta: POST/DELETE /api/posts/<id>/save   ← PROPUESTA
Autenticación: JWT, usuario autenticado
Response: {saved: bool, saves_count: int}
Errores: 401, 404, idempotente como likes (ADR-005)
Comportamiento actual de la UI: botón visible y deshabilitado con explicación
```

```text
Capacidad: Mensajería directa
Pantallas consumidoras: Mensajes (REF-MSG-01..05), contador de sidebar
Endpoint existente inspeccionado: ninguno
Propuesta: GET /api/conversations · GET/POST /api/conversations/<id>/messages   ← PROPUESTA
Concurrencia: sin transporte en tiempo real; sondeo o recarga manual
Dependencia: decisión de producto sobre E2EE — hoy NO existe y no se mostrará como activo
Comportamiento actual de la UI: pantalla heredada con fixture; sin contador inventado
```

```text
Capacidad: Lugares y Radar
Pantallas consumidoras: Radar (REF-RADAR-01/02), tarjeta de ubicación en Mensajes
Endpoint existente inspeccionado: ninguno
Propuesta: GET /api/places?lat&lng&category   ← PROPUESTA
Dependencia: proveedor de cartografía NO contratado. Claves privadas en backend.
Decisión pendiente del propietario: §8.8 prohíbe contratar Mapbox/Google Maps sin su decisión
Comportamiento actual de la UI: marcador honesto con los bloqueos listados
```

```text
Capacidad: Sugerencias de personas y tendencias
Pantallas consumidoras: rail del Feed, Buscar
Endpoint existente inspeccionado: ninguno
Propuesta: GET /api/suggestions/users · GET /api/trends   ← PROPUESTA
Comportamiento actual de la UI: fixture rotulado «ejemplo» en pantalla
```

---

## 4b. Cómo se comporta Buscar sin endpoint de búsqueda

No existe `GET /api/search`. En vez de simular un buscador de servidor, `/search` **filtra en cliente sobre las publicaciones reales** que ya trajo `GET /api/posts`, y lo dice en pantalla («El buscador recorre las publicaciones ya cargadas desde el servidor»).

| Capacidad | Estado |
|---|---|
| Buscar por contenido, nombre o usuario | **Real**, sin acentos ni mayúsculas |
| Orden «Más recientes» / «Mayor resonancia» | **Real**: ambos se calculan sobre datos que ya viajan con cada post |
| `?q=`, `?scope=`, `?sort=` en la URL | **Real**: la búsqueda se comparte y sobrevive a la recarga |
| Ámbitos Videos, Sonidos, Creadores, Lugares | Estado honesto: no hay modelo de datos que indexar |
| Duración, Fecha, Calidad | Deshabilitados: describen vídeo, que no existe |
| Filtros clave (6 chips) | Deshabilitados con explicación accesible |
| Guardar búsqueda | Deshabilitado: sin endpoint |

Propuesta de contrato, **no implementada**:

```text
Capacidad: Búsqueda de servidor
Pantallas consumidoras: Buscar, buscador del topbar
Endpoint existente inspeccionado: ninguno
Propuesta: GET /api/search?q=&scope=&sort=&cursor=   ← PROPUESTA
Response: {results: [...], next_cursor}
Motivo: el filtrado en cliente solo alcanza a lo ya cargado; no escala ni pagina
Comportamiento actual de la UI: filtra en cliente y lo declara en pantalla
```

---

## 4c. Configuración — las 12 secciones

Todas existen como ruta propia (`/settings/<id>`) y abren por URL directa. Sobre la variante `settings` del shell (256px, Luminous).

| Sección | Ref | Qué funciona de verdad |
|---|---|---|
| Editar perfil | REF-SET-01 | Enlace al formulario de perfil ya existente (`PATCH /api/users/me`) |
| Privacidad | REF-SET-02 | Nada: **aviso de alcance** explicando que no hay reglas de privacidad en el servidor |
| Seguridad y contraseña | REF-SET-03 | **`POST /api/forgot-password`** y **`POST /api/send-verification-email`**, ambos reales. 2FA y sesiones: sin soporte |
| Suscripción y verificación | REF-SET-04 | Nada: sin pasarela de pagos ni recogida de documentos |
| Herramientas y Resonancias | REF-SET-05 | Nada: radar y telemetría sin servicio |
| Notificaciones | REF-SET-06 | **3 preferencias** que se guardan en el navegador |
| Audio y reproducción | REF-SET-07 | 1 preferencia (autoplay); el resto sin motor de audio |
| Enlaces y Redes | REF-SET-08 | Enlace al perfil; OAuth sin soporte |
| Descarga de datos | REF-SET-09 | Nada: no se genera ningún archivo |
| Bloqueadas y restringidas | REF-SET-10 | Nada: no existe el modelo de bloqueo |
| Permisos y aplicaciones | REF-SET-11 | Nada: no se emiten ni se muestran tokens |
| Contenido y feed | REF-SET-12 | 1 preferencia; filtros de feed sin soporte |

**Criterio de persistencia.** Las preferencias que sí se guardan van a `localStorage` por cuenta (`lib/settingsStorage.js`) y **cada fila lo dice**: «Se guarda en este navegador». Nada que dependa de una decisión de servidor —privacidad, bloqueo, 2FA, sesiones, pagos, verificación, tokens, exportación— se modela como preferencia local: guardar un booleano en el navegador no protege ningún dato (archivo maestro §8.10).

**«Lorem ipsum».** Siete de las doce referencias rellenan sus descripciones con texto de relleno. Los títulos de sección y de grupo se conservan literales; las descripciones se han escrito de verdad, explicando qué hace cada control.

---

## 5. Próximo trabajo, por etapa

- **D (resto)** — `/u/:username` para REF-PROFILE-02/03. **Bloqueado**: no existe endpoint público de usuario.
- **D (resto)** — Videos/Cortos: sin captura dedicada, será diseño derivado.
- **E** — Mensajes: unificar REF-MSG-01..05 en bandeja/chat/contexto sobre la variante `messages` del shell.
- **F** — Radar, con el mapa rotulado como demostración hasta que haya decisión de proveedor.
- **H** — QA visual del resto de pantallas y regresiones.
