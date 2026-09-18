# THERS — Sistema de diseño resuelto

Última actualización: 2026-09-14 · Etapa B completada
Fuente de verdad en código: `Frontend/src/shared/design/tokens.css`
Referencias: `docs/THERS_REFERENCE_MANIFEST.md`

Este documento explica **qué se decidió y por qué**. Los valores vivos están en `tokens.css`; si algo diverge, manda el código.

---

## 1. Arquitectura de tokens: una sola fuente de verdad

```
Frontend/src/shared/design/tokens.css     ← variables CSS (ÚNICA fuente)
        ↑ importado por src/index.css
Frontend/tailwind.config.js               ← solo apunta a var(--th-*), no redefine valores
```

No hay `design-tokens.json` ni una tercera copia. El archivo maestro §11 advierte contra «tres copias que divergen»: aquí Tailwind es un consumidor, no un duplicado. Un cambio de color se hace en un único sitio.

**Prefijo `th-`.** Los tokens anteriores del proyecto (`canvas`, `surface`, `ink`, `muted`, `line`, `pulse`, `ember`, `success`, `warning`) **siguen intactos y en uso** en `auth/`, `help/`, `public/` y `legal/`. El prefijo evita colisiones y permite migrar por módulos sin un refactor masivo. Las clases nuevas se escriben `bg-th-surface`, `text-th-fg-muted`, `border-th-border`, etc.

---

## 2. La decisión central: dos familias, un shell

Las 24 referencias **no comparten un sistema visual único** (manifest §2). En vez de aplanarlas a una paleta —que habría contradicho la petición de máxima fidelidad— los **roles semánticos son los mismos** y sus **valores cambian según la variante de shell**:

```css
[data-th-shell="social"]   { --th-fg: #0f172a; --th-bg: #f8fafc; --th-brand: #7c3aed; --th-sidebar-w: 288px; }
[data-th-shell="settings"],
[data-th-shell="messages"] { --th-fg: #131b2e; --th-bg: #faf8ff; --th-brand: #630ed4; --th-sidebar-w: 256px; }
```

Consecuencia práctica: un componente escribe `bg-th-surface text-th-fg` **una sola vez** y queda correcto en Feed y en Configuración. Hay un `<ShellFrame>`, no tres copias del shell (archivo maestro §3.1).

`data-th-shell` lo decide `shellVariantFor(pathname)` en `Frontend/src/app/layout/thers/navigation.js`.

### 2.1. Los dos violetas conviven

No se hizo el reemplazo global que proponía el prompt anterior. Ambos se conservan como tokens base y se asignan por rol:

| Token base | Valor | Rol |
|---|---|---|
| `--th-violet-deep` | `#630ed4` | `--th-brand` en Configuración y Mensajes (`primary` de DESIGN.md) |
| `--th-violet-500` | `#7c3aed` | `--th-brand` en lo social (el Feed sobrescribe `primary` a este valor) |
| `--th-violet-700` | `#7e22ce` | `--th-brand-hover` social — es el `hover:bg-purple-700` literal del Feed |
| `--th-violet-600` | `#6d28d9` | reservado; valor de respaldo del archivo maestro |

---

## 3. Medidas de layout — medidas, no supuestas

Todas salen de los HTML de referencia:

| Token | Valor | Evidencia |
|---|---|---|
| `--th-sidebar-social` | **288px** | `w-72` en las 7 pantallas sociales, sin excepción |
| `--th-sidebar-luminous` | **256px** | `w-64` en 9/12 de Configuración y 5/5 de Mensajes |
| `--th-topbar-h` | **64px** | `h-16` en las 24 |
| `--th-feed-max` | **700px** | `xl:max-w-[700px]` literal de REF-FEED-01 |
| `--th-rail-w` | **340px** | comentario y ancho del rail de REF-FEED-01 |
| `--th-sidebar-compact` | 72px | respaldo del archivo maestro; aún sin uso |

> **Divergencia respecto del archivo maestro.** §6.1 propone 256px de sidebar y 680px de feed como respaldo. La referencia canónica demuestra 288px y 700px para el shell social, y §3 da prioridad a la captura sobre los valores de respaldo. Se implementa lo medido.

**Regla de offset.** El header y el contenido se desplazan con `--th-sidebar-w`, la **misma** variable que da ancho a la sidebar (`lg:left-th-sidebar`, `lg:pl-th-sidebar`). Es imposible que queden descuadrados al cambiar de variante — el problema que el archivo maestro §6.1 pide evitar expresamente.

---

## 4. Tipografía

**Plus Jakarta Sans** (400/500/600/700/800), presente en 24/24 referencias. Se carga desde Google Fonts en `Frontend/index.html`, igual que los prototipos. Fallback: `system-ui, -apple-system, "Segoe UI", sans-serif`.

Escala del cuerpo de DESIGN.md, expuesta como `text-headline-xl`, `text-body-md`, `text-label-sm`, etc. Se mantiene en **px** para conservar la equivalencia nominal exacta; el proyecto no fija un tamaño raíz propio, así que no hay conversión a rem que preservar.

`11px` (`label-sm`) queda reservado a etiquetas auxiliares, nunca a instrucciones esenciales.

> **Inter no se adopta.** Aparece en 6 de 24 referencias, todas de la familia slate. Plus Jakarta Sans está en las 24 y es la familia declarada por DESIGN.md. Añadir una segunda familia para 6 pantallas habría fragmentado la identidad sin ganancia demostrable. Registrado como desviación consciente.

---

## 5. Iconografía

**Material Symbols Outlined**, en 23 de 24 referencias. Adaptador único: `Frontend/src/shared/components/Icon.jsx`.

```jsx
<Icon name="notifications" size={20} fill={isActive ? 1 : 0} />
```

Conserva silueta, grosor y relleno originales vía `font-variation-settings`. El archivo maestro §5.7 prohíbe expresamente cambiar a otra librería «solo por conveniencia» si altera visiblemente el diseño.

`react-icons` **no se retira**: sigue instalado y en uso en `auth/`, `help/`, `public/` y `legal/`. Simplemente deja de usarse en el shell y las pantallas nuevas.

Accesibilidad: los iconos son `aria-hidden` por defecto. Cuando un icono es el único contenido de un botón, el nombre accesible lo pone el botón con su `aria-label`.

---

## 6. Radios, sombras, capas y movimiento

**Radios por rol**, no por valor suelto — resuelve la ambigüedad de `rounded-lg` (8px en prototipos, 16px en DESIGN.md) que señalaba el archivo maestro §3.2:

`--th-radius-xs` 4 · `-sm` 8 · `-input` 12 · `-card` 16 · `-dialog` 24 · `-pill` 9999

**Sombras**: `card`, `hover`, `overlay`, `focus-soft`, `compose`, transcritas del cuerpo de DESIGN.md.

**Capas** — escala central, sin `z-index: 999999`:
`content 0 < sticky 10 < nav 20 < backdrop 30 < modal 40 < toast 50`

**Movimiento**: 120ms feedback · 180ms controles · 240ms overlays. Bajo `prefers-reduced-motion: reduce` las tres pasan a `0ms` en el propio `tokens.css`.

---

## 7. Accesibilidad incorporada al sistema

Estas son correcciones deliberadas sobre los prototipos, documentadas como exige el archivo maestro §12:

| Aspecto | Qué hace el sistema | Por qué |
|---|---|---|
| Foco | `.th-focus-ring` = outline 2px **más** halo violeta | El halo solo (`--th-shadow-focus-soft`) no garantiza contraste suficiente (§5.6) |
| Zona táctil | `min-h-[44px]`/`min-w-[44px]` en controles, icono a 18–24px | §12, sin áreas invisibles superpuestas |
| Scrollbars | `.th-scrollbar-none` **solo** en carruseles horizontales | Los prototipos traen `::-webkit-scrollbar{display:none}` global; §6.4 prohíbe copiarlo |
| Estado | `aria-pressed`, `aria-expanded`, `role="status"`, texto junto al color | §12: el estado no se comunica solo por color |
| Overlays | `MobileDrawer` contiene el foco, cierra con Escape y devuelve el foco al disparador | §7.3 |

---

## 8. Componentes del shell

Todos en `Frontend/src/app/layout/thers/`:

| Archivo | Papel |
|---|---|
| `navigation.js` | Modelo único de destinos + `SETTINGS_SECTIONS` + `shellVariantFor()` |
| `Sidebar.jsx` | Sidebar de escritorio **y** contenido del drawer (`asDrawer`) — una sola implementación |
| `Topbar.jsx` | 64px, buscador funcional (`/search?q=`), menú de perfil con teclado |
| `MobileNav.jsx` | Bottom-nav — **adaptación nueva**, no reproducción (no hay referencia móvil) |
| `MobileDrawer.jsx` | Envuelve `<Sidebar asDrawer>`; no reimplementa la navegación |
| `ShellFrame.jsx` | Armazón compartido por `AppShell` (app real) y el QA visual |

---

## 9. Lo que el sistema decide NO reproducir

Conforme a los §1, §5.1 y §10 del archivo maestro, y registrado para que no parezca un olvido:

| Elemento de la maqueta | Decisión | Motivo |
|---|---|---|
| Badge `ALPHA` junto a la marca | No se dibuja | Estado de producto que el repositorio no declara |
| Badge `LIVE` en Videos | No se dibuja | Requiere señal real de directo (§10.2) |
| Indicador «En línea» | No se dibuja | No hay sistema de presencia (§10.2) |
| Distintivo `verified` | No se dibuja | El contrato no expone verificación; §8.4 prohíbe otorgarla por fixture |
| Contador «4» en Mensajes | No se dibuja | Sin endpoint de mensajes; no se inventa un número |
| «3 personas activas ahora» en PULSE | No se dibuja | Sin transporte en tiempo real |
| Chip de ubicación en publicaciones | No se dibuja | `post` no tiene campo de lugar (ADR-004) |

Los indicadores **sí** aparecen cuando hay dato real: el punto de no leídas en Notificaciones se calcula sobre `GET /api/notifications`.
