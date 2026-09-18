# THERS — Manifiesto de referencias de diseño

Última actualización: 2026-09-14 · Estado: Etapa A completada
Fuente: `docs/desing-reference/` (nótese el typo `desing` en el nombre real de la carpeta; el archivo maestro lo llama `design-reference`).

Este documento es el inventario obligatorio exigido por `THERS_IMPLEMENTACION_MAESTRA_CLAUDE.md` §2.4. Registra lo que **realmente se encontró y se pudo abrir**, no lo que el archivo maestro anticipaba.

---

## 1. Resumen del inventario real

| Dato | Valor medido |
|---|---|
| Archivos totales en `docs/desing-reference/` | 52 |
| Carpetas de referencia | `stitch_thers_web_design_system (1)` y `(2)` (ya extraídas; **no hay ZIP sin extraer**) |
| Pantallas únicas | **24** (16 en la carpeta (1), 8 en la (2)) |
| `code.html` | 24 |
| `screen.png` válidos | **23** |
| `screen.png` dañados | **1** (ver §4) |
| `DESIGN.md` | 2 copias, **byte a byte idénticas** (sha256 `32f41ec1a415`) — se trata como un único documento |
| `Pasted text.txt` | 16 bloques HTML |
| `Pasted text(1).txt` | 8 bloques HTML |

### 1.1. Los textos pegados NO aportan pantallas nuevas

Verificado programáticamente comparando el texto visible de cada bloque contra cada `code.html` (ratio `difflib.SequenceMatcher`):

- Los **16 bloques** de `Pasted text.txt` corresponden 1:1, con ratio **1.000**, a las 16 pantallas de la carpeta (1).
- Los **8 bloques** de `Pasted text(1).txt` corresponden 1:1, con ratio **1.000**, a las 8 pantallas de la carpeta (2).

Difieren de los `code.html` en unos 40–70 bytes de envoltorio/espaciado, no en contenido. **Conclusión: 24 pantallas únicas en total, no 40.** Los textos quedan como confirmación redundante; las carpetas son la fuente canónica porque son las únicas que traen la captura emparejada.

### 1.2. Corrección al archivo maestro

`THERS_IMPLEMENTACION_MAESTRA_CLAUDE.md` §2.2 mapea HTML sueltos (`code(3).html`, `code(20260915-030756).html`, etc.) y menciona dos HTML de "Seguridad" idénticos byte a byte. **Esos archivos sueltos no existen en este repositorio.** Solo existen las dos carpetas ya extraídas. No hay pantalla de Seguridad duplicada: hay exactamente una (`REF-SET-03`). El mapa de §2.2 debe leerse como histórico, no como el inventario de este repositorio.

---

## 2. Las dos familias de render (hallazgo decisivo)

Las 24 pantallas **no comparten un único sistema visual**. Se separan en dos familias medibles, contando las clases de color realmente aplicadas en el `<body>` frente a los tokens semánticos del `tailwind.config` embebido:

| Familia | Cómo se reconoce | Neutrales | Acento | Sidebar | Pantallas |
|---|---|---|---|---|---|
| **A — Luminous** | usa los tokens semánticos del config (`bg-surface`, `text-on-surface`); **cero** clases `slate-*` | `#131b2e` / `#4a4455` sobre `#faf8ff` | `primary #630ed4`, `primary-container #7c3aed` | **w-64 = 256px** | 13 |
| **B — Slate** | usa utilidades Tailwind por defecto; **cientos** de clases `slate-*`; casi ningún token semántico | `#0f172a` / `#64748b` sobre `slate-50` | `purple-600` / `violet-600`, algunas con `primary #7c3aed` | **w-72 = 288px** (1 excepción) | 11 |

Esto explica de forma directa las contradicciones que el archivo maestro §3.2 pedía resolver: **no son un error a normalizar, son dos generaciones del prototipo.** Ambas son evidencia legítima.

Constantes en las 24: `header h-16` (64px), `left-*` del header siempre igual al ancho de su sidebar, Plus Jakarta Sans presente en 24/24, Material Symbols Outlined en 23/24, Inter añadida en 6.

---

## 3. Catálogo de referencias

Ruta base `A` = `docs/desing-reference/stitch_thers_web_design_system (1)/stitch_thers_web_design_system/`
Ruta base `B` = `docs/desing-reference/stitch_thers_web_design_system (2)/stitch_thers_web_design_system/`

Todas las capturas están emparejadas por contenido (cada carpeta contiene su propio par), no por número de nombre.

### 3.1. Social — Feed, Buscar, Radar

| ID | Carpeta | Captura | Familia | Sidebar | Estado visible |
|---|---|---|---|---|---|
| `REF-FEED-01` | A `thers_feed_principal_modo_claro` | 1435×1600 ✅ | B (`primary` sobrescrito a `#7C3AED`) | 288px | Inicio activo; rail derecho **recortado** en la captura |
| `REF-SEARCH-01` | A `thers_buscar_videos_y_contenido_sugerido_modo_claro` | 1086×1600 ✅ | B | 288px | Resultados de búsqueda + contenido sugerido |
| `REF-RADAR-01` | A `thers_ubicaci_n_radar_san_salvador_modo_claro` | 1600×1582 ✅ | B | 288px | Radar, modo claro |
| `REF-RADAR-02` | A `thers_ubicaci_n_radar_san_salvador_profundidad_funcional` | 1129×1600 ✅ | B | 288px | Radar, profundidad funcional (rutas, incidencias, comparador) |

`REF-RADAR-01` y `REF-RADAR-02` son **complementarias**, no rivales: la segunda añade detalle funcional sobre la misma experiencia. Se implementan como una ruta con estados, no como dos aplicaciones.

### 3.2. Perfiles

| ID | Carpeta | Captura | Familia | Sidebar | Estado visible |
|---|---|---|---|---|---|
| `REF-PROFILE-01` | B `thers_mi_perfil_personal_publicaciones_destacadas_y_likes` | 809×1600 ✅ | B | 288px | Perfil propio, tab **Me gusta** activa, aviso «Solo tú» |
| `REF-PROFILE-02` | B `thers_perfil_de_usuario_mateo_valencia_cortos_en_video_navegaci_n_por_iconos` | 764×1600 ✅ | B | 288px | Perfil ajeno, cortos, navegación por iconos |
| `REF-PROFILE-03` | B `thers_perfil_de_mateo_valencia_m_dulo_completo_de_cortos_en_video` | **DAÑADA** ❌ | B | 288px | Módulo ampliado de cortos |

### 3.3. Mensajería

| ID | Carpeta | Captura | Familia | Sidebar | Estado visible |
|---|---|---|---|---|---|
| `REF-MSG-01` | B `thers_mensajes_bandeja_de_entrada_canales_de_audio` | 1280×1007 ✅ | A | 256px | Bandeja + descubrimiento de canales |
| `REF-MSG-02` | B `thers_mensajer_a_directa_y_canales_de_audio_modo_claro` | 1600×1280 ✅ | A | 256px | Tres paneles internos |
| `REF-MSG-03` | B `..._modo_claro_organizado` | 1600×1280 ✅ | **B** | 256px | Variante "organizada" de la misma experiencia |
| `REF-MSG-04` | B `thers_mensajes_sala_activa_de_chat_reproductor` | 1600×1280 ✅ | A | 256px | Conversación activa + reproductor |
| `REF-MSG-05` | B `thers_mensajes_informaci_n_multimedia_radar` | 1600×1402 ✅ | A | 256px | Panel de contexto: info, multimedia, radar |

`REF-MSG-03` es la única pantalla de mensajería de familia B, y la única de familia B con sidebar de 256px. El archivo maestro §3.2 advierte expresamente que «organizado» no equivale a aprobación del usuario. **Canónica de mensajería: familia A** (4 de 5 pantallas, sistema coherente). `REF-MSG-03` se conserva como referencia complementaria de organización de paneles, no como fuente de color.

### 3.4. Configuración — las 12 secciones

| ID | Sección | Carpeta (base A) | Captura | Familia | Sidebar |
|---|---|---|---|---|---|
| `REF-SET-01` | Editar perfil | `thers_configuraci_n_editar_perfil_modo_claro` | 1280×1760 ✅ | A | 256px |
| `REF-SET-02` | Privacidad | `thers_configuraci_n_privacidad_de_la_cuenta` | 1223×1600 ✅ | A | 256px |
| `REF-SET-03` | Seguridad y contraseña | `thers_configuraci_n_seguridad_y_contrase_a` | 1077×1600 ✅ | A | 256px |
| `REF-SET-04` | Suscripción y verificación | `thers_configuraci_n_suscripci_n_verificaci_n` | 1233×1600 ✅ | A | 256px |
| `REF-SET-05` | Herramientas y Resonancias | `thers_configuraci_n_herramientas_resonancias` | 1212×1600 ✅ | A | 256px |
| `REF-SET-06` | Notificaciones (preferencias) | `thers_configuraci_n_notificaciones` | 1098×1600 ✅ | A | 256px |
| `REF-SET-07` | Audio y reproducción | `thers_configuraci_n_audio_y_reproducci_n` | 1221×1600 ✅ | A | 256px |
| `REF-SET-08` | Enlaces y Redes | `thers_configuraci_n_enlaces_redes` | 1232×1600 ✅ | A | 256px |
| `REF-SET-09` | Descarga de datos y archivo | `thers_configuraci_n_descarga_de_datos_y_archivo_modo_claro` | 1280×1708 ✅ | **B** | **288px** |
| `REF-SET-10` | Cuentas bloqueadas y restringidas | `thers_configuraci_n_cuentas_bloqueadas_y_restringidas_modo_claro` | 1472×1600 ✅ | **B** | **288px** |
| `REF-SET-11` | Permisos y aplicaciones | `thers_configuraci_n_permisos_y_aplicaciones_modo_claro` | 1510×1600 ✅ | **B** | **288px** |
| `REF-SET-12` | Preferencias de contenido y feed | `thers_configuraci_n_preferencias_de_contenido_y_feed_modo_claro` | 1280×1844 ✅ | A | 256px |

`REF-SET-06` es **preferencias de notificaciones**, no el centro de notificaciones. Son vistas distintas (archivo maestro §6.3) y no se fusionan.

---

## 4. Incidencias y materiales ausentes

### 4.1. Captura dañada — confirmada

`B/thers_perfil_de_mateo_valencia_m_dulo_completo_de_cortos_en_video/screen.png`
- Tamaño: **28 bytes**. Contenido literal: `<FIFE Image failed to fetch>`. Sin cabecera PNG.
- Coincide exactamente con lo que anticipaba el archivo maestro §2.3.
- **Consecuencia:** `REF-PROFILE-03` se implementa desde su `code.html` (48 623 B, íntegro y legible). Su verificación visual queda marcada como **parcial permanente**: no existe evidencia de captura y no se declarará conforme.
- `REF-PROFILE-02` sirve de apoyo estructural (misma persona, mismo módulo de cortos), **no** como prueba de haber visto la captura dañada.

### 4.2. Materiales citados por el archivo maestro que no están en el repositorio

- Los HTML sueltos de §2.2 (`code(3).html` … `code(20260915-031108).html`) y sus `screen(N).png`.
- El "segundo ZIP que añadirá el usuario": ambas carpetas ya están extraídas; no hay ZIP pendiente de procesar.
- No falta ninguna pantalla por ello: las 24 del catálogo cubren los módulos enumerados en el encargo.

### 4.3. Módulos del encargo sin referencia dedicada

Buscados en las 24 pantallas y en ambos textos; **no existe diseño recibido** para:

| Módulo | Situación |
|---|---|
| **Centro de notificaciones** | La sidebar enlaza «Notificaciones» y el topbar tiene su campana, pero ninguna captura muestra la vista. `REF-SET-06` es *preferencias*, no el centro. → diseño derivado |
| **Cápsulas (vista dedicada)** | Enlace en sidebar; aparecen como tarjetas dentro de Feed/Perfil/Radar, sin pantalla propia. → diseño derivado |
| **Videos / Cortos (vista dedicada)** | Enlace «Videos» con badge LIVE; el contenido de vídeo vive dentro de `REF-SEARCH-01` y de los perfiles. → diseño derivado |
| **Crear (composer global)** | Botón «+ Crear» presente en la sidebar de las 24; ningún overlay de creación capturado. → diseño derivado |
| **Cualquier vista móvil** | Las 24 capturas son de escritorio. Bottom-nav y drawers son **adaptación nueva**, no reproducción. |

Todo lo anterior se marcará en `docs/THERS_UI_INTEGRATION.md` como **diseño derivado**, nunca como «reproducción fiel».

---

## 5. Decisiones canónicas

Aplicando la jerarquía del archivo maestro §3 (captura válida > HTML > DESIGN.md > respaldo):

| Ámbito | Canónica | Motivo |
|---|---|---|
| Shell **social** (Feed, Buscar, Radar, Perfiles) | Familia B, **288px** | Las 7 pantallas sociales son familia B con `w-72`, sin excepción |
| Shell **mensajes** | Familia A, **256px** | 4 de 5; `REF-MSG-03` es la desviación |
| Shell **configuración** | Familia A, **256px** | 9 de 12; ver excepción abajo |
| Tipografía | Plus Jakarta Sans | 24/24 |
| Iconografía | Material Symbols Outlined | 23/24 |
| Header | 64px, offset = ancho de su sidebar | 24/24 |

### 5.1. Excepción documentada: `REF-SET-09/10/11`

Sus capturas muestran neutrales slate y sidebar de 288px, mientras las otras nueve secciones de Configuración usan Luminous y 256px. Mantener esa diferencia haría que la sidebar **cambiara de ancho y de paleta al navegar entre secciones del mismo menú de ajustes** — un defecto visible, no fidelidad.

**Decisión:** las 12 secciones se implementan con el shell de Configuración canónico (familia A, 256px). Las tres pantallas conservan íntegros su estructura, grupos, filas, orden y textos; solo se alinean shell y paleta.

Registrado como **desviación deliberada** en `docs/THERS_VISUAL_QA.md`. No se declarará «conforme» la comparación píxel de esas tres contra su captura original.

### 5.2. Variantes conservadas, no descartadas

Ninguna referencia se borra. `REF-MSG-03`, `REF-RADAR-02` y `REF-PROFILE-03` permanecen como fuentes complementarias de estructura y estados.

---

## 6. Advertencias de contenido

Los siguientes valores de las referencias son **muestra ilustrativa**, nunca datos ni reglas del producto:

- Identidades: «Cristopher Stanley / @CHITO209_0», «Carlos Silva», «Mateo Valencia», «Diego Medina», «Sofia». El usuario autenticado se lee **siempre** de la sesión real.
- Contadores (4 mensajes, seguidores, likes), precios, planes, horarios, afluencia y valoraciones.
- Ubicación «San Salvador»: no se asume como posición del usuario.
- Badges `ALPHA`, `LIVE`, `E2EE`, `2FA`, `Verificado`, `Lossless`, `En vivo`: capacidades dibujadas. Solo se muestran activas con evidencia funcional (archivo maestro §10).
- El plazo de 14 días de cooldown de username en `REF-SET-01`: el backend manda, no la maqueta.

---

## 7. Reproducibilidad

Los datos de §1–§3 (hashes sha256, dimensiones PNG, familia de render, anchos de sidebar, emparejamiento texto↔carpeta) se obtuvieron con scripts deterministas sobre `docs/desing-reference/`. Son re-ejecutables: leen cabecera PNG, cuentan clases aplicadas en el `<body>` tras eliminar `<script>`/`<style>`, y comparan texto visible con `difflib`.
