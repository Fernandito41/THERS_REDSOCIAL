# THERS — QA visual

Última actualización: 2026-09-15 · Etapas A–D (parcial) y G

Evidencias: `docs/qa/screens/` (fuera de los assets de producción, según el archivo maestro §13.5).

---

## 1. Cómo se reproducen las capturas

Requisitos: Docker con `thers_postgres_dev` levantado, backend en `:5000`, Vite en `:5173`.

```bash
docker compose up -d                      # POSTGRES_PORT=5433 si 5432 está ocupado
cd backend && ./venv/Scripts/python.exe run.py
cd Frontend && npm run dev
```

El script de captura vive en el scratchpad de la sesión (no se versiona: añadiría Playwright al repositorio sin decisión del equipo). Lo que hace, y que debe conservarse si se reescribe:

1. **Entra por la UI real de login** con la cuenta sintética de QA — no inyecta el token en `localStorage`. Así la captura también prueba el flujo de autenticación.
2. Espera a que termine el **splash de 2.3 s** de `App.jsx` y a que el shell esté montado (`[data-th-shell]`).
3. Espera a que el contenido real cargue (`article` presente y sin el texto «Cargando»), no un tiempo fijo.
4. Congela animaciones, transiciones y el cursor de texto para que la captura sea determinista.
5. Mide el desbordamiento horizontal y captura a `deviceScaleFactor: 1`.

Cuenta sintética usada: `qa.harness@example.invalid` / usuario `qa_harness`. **No es una cuenta real del propietario** y vive solo en la base de desarrollo.

---

## 2. Entorno de las capturas de esta etapa

| Campo | Valor |
|---|---|
| Navegador | Chrome (canal `chrome`), Playwright 1.63 |
| Escala | `deviceScaleFactor: 1` |
| Modo de captura | `fullPage: true` |
| Datos | Backend real: 10 publicaciones, notificaciones reales, perfil real de la cuenta de QA |
| Fuentes | Plus Jakarta Sans y Material Symbols cargadas desde Google Fonts |

---

## 3. Resultados

### 3.1. `/feed` — REF-FEED-01

| Viewport | Archivo | Desbordamiento X | Errores de consola | Resultado |
|---|---|---|---|---|
| 1440×900 | `feed-1440x900.png` | 0 (ver §3.2) | ninguno | **conforme en estructura** |
| 1366×768 | `feed-1366x768.png` | 0 | ninguno | conforme en estructura |
| 1024×768 | `feed-1024x768.png` | 0 | ninguno | conforme en estructura |
| 768×1024 | `feed-768x1024.png` | 0 | ninguno | conforme en estructura |
| 390×844 | `feed-390x844.png` | 0 | ninguno | conforme en estructura |
| 360×800 | `feed-360x800.png` | 0 | ninguno | conforme en estructura |

**Comprobado visualmente y correcto:**
- Sidebar de 288px; el header arranca exactamente en 288px; ambos derivados de `--th-sidebar-w`.
- Los 7 destinos de la referencia, en su orden, con «Inicio» activo en violeta suave.
- Botón «+ Crear» y tarjeta de sesión al pie de la sidebar.
- Orden de secciones de la referencia: Momentos → PULSE → compositor → stream.
- Rail derecho de 340px con sus cuatro módulos en orden.
- Identidad tomada de la sesión real (`QA Harness` / `@qa_harness`), **no** de «Cristopher Stanley».
- Móvil: topbar con disparador de drawer, rail apilado bajo el stream, bottom-nav de 5 destinos.

### 3.1b. `/profile` — REF-PROFILE-01

| Viewport | Estado | Archivo | Desbordamiento X | Resultado |
|---|---|---|---|---|
| 1440×900 | tab Publicaciones | `profile-1440x900.png` | 0 | conforme en estructura |
| 1024×768 | tab Publicaciones | `profile-1024x768.png` | 0 | conforme en estructura |
| 390×844 | tab Publicaciones | `profile-390x844.png` | 0 | conforme en estructura |
| 1440×900 | tab **Me gusta** | `profile-tab-likes-1440x900.png` | 0 | reproduce el estado de la captura de referencia |

**Comprobado:** portada con «Cambiar portada», avatar superpuesto, identidad, los tres botones de acción, biografía y metadatos, métricas reales, Colecciones Destacadas, las tres tabs de la referencia y el rail de cuatro módulos.

**Defectos encontrados y corregidos durante esta etapa** (detectados mirando la captura, no adivinando):

| Defecto | Causa | Corrección |
|---|---|---|
| **36px de desbordamiento horizontal** | La fila identidad+acciones pasaba a horizontal en `lg` (1024px), sin ancho suficiente | Pasa a fila en `xl`; botones `shrink-0`; bloque de identidad `min-w-0` |
| **El nombre se partía en dos líneas y se montaba sobre la portada** | Alineado al fondo junto al avatar: al envolverse, la primera línea subía sobre la portada | `truncate` en nombre y handle; tamaño menor bajo `sm` |
| **Anillo rectangular alrededor del avatar circular** | El contenedor usaba `rounded-th-dialog` (24px) sobre un avatar redondo | `rounded-th-pill` |
| **Los botones de acción envolvían su texto** | Tres botones con etiqueta completa no caben a 1440 junto al rail | «Compartir perfil» muestra solo el icono por debajo de `2xl`, con `aria-label` |
| **`rounded-th-pill` no existía** (35 usos) | El token `--th-radius-pill` estaba en `tokens.css`, pero **la clave `th-pill` nunca se añadió a `borderRadius`** en `tailwind.config.js`. Tailwind descarta una clase desconocida **en silencio**: ni el build ni el lint fallan | Añadida la clave. Afectaba a botones, insignias, avatares y la franja PULSE de **todas** las pantallas |

### 3.1c. Auditoría de clases — cómo se encontró el fallo de `rounded-th-pill`

Una clase de Tailwind mal escrita no rompe nada: simplemente no genera CSS y el estilo desaparece sin aviso. Build y lint seguían en verde con 35 usos rotos.

Procedimiento, re-ejecutable: extraer toda clase `th-*` del código, compilar, y comprobar que cada una aparezca como selector en el CSS resultante (contemplando variantes, que Tailwind escribe `.lg\:clase` o `.hover\:clase:hover`).

Resultado tras las correcciones: **51 clases `th-` usadas, 51 generadas.** Los únicos restos son `th-global-search` y `th-search-input`, que son `id` de HTML, no clases.

Segundo fallo que destapó la misma auditoría:

| Fallo | Causa | Corrección |
|---|---|---|
| `bg-th-surface/90` y `/95` no generaban nada | Tailwind **no sabe aplicar un modificador de opacidad** a un color declarado como `var(--x)` con un hex dentro | Token propio `--th-surface-translucent` + clase `bg-th-surface-translucent`. Afectaba al fondo de la topbar y de la bottom-nav |
| `border-th-warning-accent/40` tampoco generaba nada (detectado en la etapa G) | Mismo motivo | Tokens propios `--th-warning-border` y `--th-danger-border` |

**Conviene automatizarlo.** Es el único control que detecta esta clase de fallo: build y lint no lo ven.

### 3.1d. `/search` — REF-SEARCH-01

| Viewport | Archivo | Desbordamiento X | Resultado |
|---|---|---|---|
| 1440×900 | `search-1440x900.png` | 0 | conforme en estructura |

Comprobado: tarjeta de búsqueda con el placeholder literal de la referencia, los **seis** selectores de ámbito en su orden, barra de filtración avanzada con «Orden» operativo y Duración/Fecha/Calidad deshabilitados, los **seis** chips de filtros clave, rejilla de 12 columnas (8 + 4) y el rail de cuatro bloques.

### 3.1e. `/settings/:section` — REF-SET-01..12

| Viewport | Estado | Archivo | Desbordamiento X | Resultado |
|---|---|---|---|---|
| 1440×900 | Privacidad | `settings-privacy-1440x900.png` | 0 | conforme en estructura |
| 1440×900 | Seguridad | `settings-security-1440x900.png` | 0 | conforme en estructura |
| 390×844 | Privacidad | `settings-privacy-390x844.png` | 0 | conforme en estructura |

Comprobado: migas de pan, rejilla de 12 columnas (menú local de 4 + panel de 8), las 12 secciones en el menú, y **la variante de shell correcta** — `data-th-shell="settings"` con `--th-sidebar-w: 256px`, medido en el navegador, frente a los 288px del shell social.

### 3.2. Nota de medición — los «5px» transitorios

El script informó `overflowX=5px` a 1440×900. Dos mediciones independientes **en estado estable** dan `scrollWidth == clientWidth == 1440`, antes y después de congelar animaciones, y ningún elemento supera el ancho del cliente.

Conclusión: los 5px eran una lectura **durante la carga**, no un desbordamiento real. El único elemento con contenido fuera de caja es la insignia «+» del avatar de «Tu momento» (4px), que es superposición intencionada y queda recortada por el `overflow-hidden` de su tarjeta.

### 3.1f. Pruebas funcionales de Buscar y Configuración

Ejecutadas contra Flask + PostgreSQL reales, entrando por el login de la interfaz. **17 de 17 comprobaciones pasadas, 0 errores de consola.**

| # | Caso | Resultado |
|---|---|---|
| 1 | Login por la UI real | ✅ |
| 2 | Buscar carga publicaciones reales | ✅ 10 artículos |
| 3 | Buscar filtra por término | ✅ 1 de 10 |
| 4 | `?q=` se sincroniza con la URL | ✅ |
| 5 | La consulta sobrevive a la recarga (deep link) | ✅ |
| 6 | Estado «sin resultados» diferenciado | ✅ |
| 7 | Ámbito sin backend muestra estado honesto | ✅ |
| 8 | `?scope=` en la URL | ✅ |
| 9 | Orden por resonancia aplicado | ✅ |
| 10 | `/settings` redirige a la primera sección | ✅ |
| 11 | Configuración usa la variante `settings` | ✅ |
| 12 | Sidebar de 256px, medida en el navegador | ✅ |
| 13 | **Las 12 secciones abren por URL directa** | ✅ 12/12 |
| 14 | Un interruptor cambia de estado | ✅ |
| 15 | **La preferencia persiste tras recargar** | ✅ |
| 16 | 2FA presente pero declarado sin soporte | ✅ 3 filas «Sin soporte» |
| 17 | Botón atrás del navegador | ✅ |

### 3.3. Lo que **no** está verificado

Declarado explícitamente, según exige el archivo maestro §13.

- **No hay comparación superpuesta (overlay/diff) contra la captura de referencia.** El viewport CSS original de las referencias **no es recuperable con confianza**: los PNG tienen anchos dispares (764, 809, 1077, 1086, 1098, 1129, 1212, 1221, 1223, 1232, 1233, 1280, 1435, 1472, 1510, 1600) y varias alturas de exactamente 1600px, lo que delata capturas escaladas o de página completa. Sin el viewport de origen no se puede afirmar una tolerancia en píxeles.
  → **La comprobación geométrica queda como PARCIAL.** No se declara ningún porcentaje de similitud (§13.3).
- La verificación de esta etapa es **estructural**: orden de secciones, anchos de shell, composición, tipografía, iconografía y estados — contrastados leyendo el HTML de referencia y la captura, no midiendo píxel a píxel.
- **Sin verificar todavía:** Buscar, Videos, Cápsulas, Radar, Mensajes, Notificaciones, Perfiles y las 12 secciones de Configuración.

---

## 4. Desviaciones deliberadas respecto de las referencias

Registradas como exige el archivo maestro §1 y §12. Ninguna es un olvido.

| # | Desviación | Referencia | Motivo |
|---|---|---|---|
| 1 | Rail derecho junto al feed solo desde 1280px; por debajo se apila | REF-FEED-01 | La captura muestra el rail **recortado**: el prototipo fuerza tres columnas antes de que quepan. 288+700+340 no cabe en 1024. §1 prohíbe reproducir un desbordamiento como si fuera requisito |
| 2 | Configuración usará 256px y paleta Luminous en **las 12** secciones | REF-SET-09/10/11 | Esas tres capturas muestran slate y 288px. Mantenerlo haría que la sidebar cambiara de ancho y color al navegar dentro del mismo menú. Estructura, grupos, orden y textos se conservan íntegros |
| 3 | Sin `Inter` | 6 de 24 referencias | Plus Jakarta Sans está en 24/24 y es la familia de DESIGN.md |
| 4 | Sin badge `ALPHA`, `LIVE`, `verified`, «En línea», contador de mensajes, «3 personas activas» | varias | Capacidades sin evidencia funcional (§10) |
| 5 | Foco = outline 2px **+** halo violeta | todas | El halo solo no garantiza contraste (§5.6) |
| 6 | Scrollbars ocultas solo en carruseles | todas | Los prototipos traen la regla global; §6.4 la prohíbe |
| 7 | Zonas táctiles de 44px | todas | §12; el icono conserva su tamaño visual |
| 8 | Bottom-nav móvil de 5 destinos | ninguna | **Diseño derivado**: no existe referencia móvil (manifest §4.3) |
| 9 | `REF-PROFILE-03` nunca se declarará «conforme» | REF-PROFILE-03 | Su captura está dañada (28 B). Verificación **parcial permanente** |
| 10 | Sin «Sincronización segura activa» ni «Nivel de blindaje 85%» | REF-SET-02 | Estados de seguridad fijos del cliente; §10.2 los prohíbe expresamente |
| 11 | Descripciones reescritas en 7 de 12 secciones de Configuración | REF-SET-02/03/05/07/08/09 y otra | Sus referencias usan **«Lorem ipsum dolor sit amet»** como relleno. Los títulos de sección y grupo se conservan literales |
| 12 | Sin badge `PRO` ni «EN VIVO» en la sidebar del perfil | REF-PROFILE-01 | Esa referencia dibuja una sidebar con variantes propias; se usa el shell social canónico (REF-FEED-01), que es el de las 7 pantallas sociales |

---

## 5. Hallazgos abiertos

| # | Hallazgo | Severidad | Estado |
|---|---|---|---|
| 1 | `App.jsx` muestra un splash de 2.3 s en **cada** montaje, también al navegar a una ruta directa | media | **Preexistente, no introducido.** Ralentiza cada carga y obliga a esperarlo en QA. No se toca: está fuera del alcance pedido |
| 2 | En desarrollo, `GET /api/posts` y `GET /api/notifications` se emiten dos veces | baja | Doble invocación de efectos de React StrictMode en dev. No ocurre en producción |
| 3 | Sin script de QA versionado | baja | Añadir Playwright al repositorio es una decisión del equipo (§11: dependencias solo si están justificadas) |
| 4 | **Vite no recarga `tailwind.config.js` en caliente** | media | Tras tocar el config hay que **reiniciar `npm run dev`**. Costó una ronda entera de QA: la clase ya estaba en el CSS compilado pero el navegador seguía sirviendo la hoja anterior. Conviene recordarlo antes de dar por buena una captura |
| 5 | La medición de desbordamiento solo es fiable **en estado estable** | baja | El script llegó a informar 5px (feed) y 36px (perfil) que no existían: se medía mientras el contenido aún se acomodaba. El script ahora lista los elementos culpables; si la lista sale vacía, la lectura era transitoria |
