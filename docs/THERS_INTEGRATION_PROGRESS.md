# THERS — Checkpoint de continuidad

> Punto de reanudación. Si la sesión se interrumpe, **empezar leyendo este archivo y `THERS_REFERENCE_MANIFEST.md`**, comprobar `git status` y los cambios posteriores del equipo, y seguir desde el estado real. No reiniciar la auditoría.

---

**Última actualización:** 2026-09-15
**Rama:** `develop`, actualizada a `origin/develop` (`2fa63c1`) con `git merge --ff-only` **autorizado por el propietario**.
**Cambios locales:** sin commit. `CLAUDE.md` modificado (preexistente, no tocado por esta sesión), `THERS_IMPLEMENTACION_MAESTRA_CLAUDE.md` y `docs/desing-reference/` sin seguimiento.
**Etapa actual:** A, B, C, **D (parcial)** y **G** terminadas. Siguiente: **E — Mensajes** (bloqueada por endpoints) o el resto de D.

---

## Terminado, con evidencia

### Etapa A — Inventario y línea base
- Inventariadas las **24 pantallas** de referencia con hash, dimensiones y validez → `THERS_REFERENCE_MANIFEST.md`.
- Demostrado que los dos textos pegados son **las mismas 24 pantallas** (ratio 1.000), no material adicional.
- Confirmada **1 captura dañada** (`REF-PROFILE-03`, 28 B, `<FIFE Image failed to fetch>`).
- Descubiertas las **dos familias de render**, que explican todas las contradicciones del archivo maestro §3.2.
- Línea base: `npm run build` ✅ · `npm run lint` ✅ (ambos limpios **antes** de tocar código).

### Etapa C — Perfil propio (REF-PROFILE-01)
- `/profile` migrado a la composición de la referencia: portada, avatar superpuesto, identidad con Editar/Compartir/Más, biografía y metadatos, métricas reales, Colecciones Destacadas, las **tres** tabs de la referencia (Publicaciones / Destacadas / Me gusta) y rail de cuatro módulos.
- Componentes nuevos: `ProfileCover`, `ProfileIdentity`, `ProfileCollections`, `ProfileRail`; `ProfileTabs` reescrito de 5 a 3 pestañas.
- Verificado en 1440/1024/390 + el estado `?tab=likes` de la captura de referencia.
- **Seis defectos reales encontrados y corregidos** mirando las capturas (ver `THERS_VISUAL_QA.md` §3.1b/§3.1c), incluidos dos que afectaban a TODAS las pantallas: `rounded-th-pill` no existía en el config, y `bg-th-surface/90` no generaba CSS.

### Etapa D (parcial) — Buscar
- `/search` implementado sobre REF-SEARCH-01: tarjeta de búsqueda, 6 ámbitos, filtración avanzada, 6 chips de filtros clave, rejilla 8+4 y rail de 4 bloques.
- **Búsqueda real** sobre las publicaciones cargadas (no hay endpoint de búsqueda): filtra por contenido, nombre y usuario, sin acentos ni mayúsculas.
- `?q=`, `?scope=` y `?sort=` en la URL: la búsqueda se comparte y sobrevive a la recarga.
- `Discover.jsx` queda sin uso; `/discover` redirige a `/search`.
- **Pendiente de D:** Videos/Cortos (diseño derivado) y perfil ajeno (**bloqueado**, sin endpoint público de usuario).

### Etapa G — Configuración completa (12/12)
- `/settings/:section` sobre la variante `settings` del shell (256px, Luminous), con migas y rejilla 4+8.
- Las **12 secciones** existen y abren por URL directa.
- Renderizador único guiado por datos (`data/settingsSections.js` + `components/settings/SettingsPrimitives.jsx`): no hay doce componentes casi idénticos.
- **Conectado de verdad:** `POST /api/forgot-password` y `POST /api/send-verification-email` (ADR-009), más `email_verified` real de la sesión.
- Preferencias que sí persisten -> `localStorage` por cuenta, y **cada fila lo dice** («Se guarda en este navegador»).
- 17/17 pruebas funcionales pasadas.

### Etapa B — Tokens, shell y pantalla representativa
- `Frontend/src/shared/design/tokens.css` — fuente de verdad única; Tailwind solo la consume.
- Shell completo en `Frontend/src/app/layout/thers/` con variantes `social` / `settings` / `messages`.
- Feed (`/feed`) migrado a REF-FEED-01 y **verificado en 6 viewports** con backend real.
- Rutas nuevas: `/search`, `/videos`, `/capsules`, `/radar`; `/discover` → `/search`.
- `npm run build` ✅ · `npm run lint` ✅ tras cada cambio.

---

## Comandos ejecutados y resultado

| Comando | Directorio | Resultado |
|---|---|---|
| `git merge --ff-only origin/develop` | raíz | ✅ fast-forward limpio, cambios locales conservados |
| `npm run build` | `Frontend/` | ✅ repetido tras cada cambio |
| `npm run lint` | `Frontend/` | ✅ sin avisos |
| `docker compose up -d` (`POSTGRES_PORT=5433`) | raíz | ✅ `thers_postgres_dev` healthy |
| `pip install -r requirements-dev.txt` | `backend/` | ✅ instaló `resend`, que faltaba tras el merge |
| `flask db upgrade` | `backend/` | ✅ 4 migraciones nuevas aplicadas |
| `python run.py` | `backend/` | ✅ sirviendo en `:5000` |
| Login + captura por Playwright | — | ✅ 6 viewports, 0 errores de consola |

**No ejecutado:** `python -m pytest` (requiere la base `thers_test` aparte). **Sin línea base de tests del backend en esta sesión.**

---

## En curso / no empezado

Nada a medias. Las pantallas no migradas siguen funcionando con los tokens anteriores; no se rompió ninguna.

### Limpieza pendiente de autorización

Quedaron **sin ningún importador** tras sustituir el shell y el perfil. Son código muerto:

- `Frontend/src/app/layout/NavRail.jsx`
- `Frontend/src/app/layout/MobileNav.jsx` (el **antiguo**, no el de `layout/thers/`)
- `Frontend/src/features/feed/components/ProfileHeader.jsx`
- `Frontend/src/features/feed/components/ProfileTopBar.jsx`
- `Frontend/src/features/feed/pages/Discover.jsx` (sustituida por `Search.jsx`)
- `Frontend/src/features/feed/pages/Settings.jsx` (sustituida por `SettingsLayout` + `SettingsSectionPage`)

No se borran: `CLAUDE.md` §13 exige aprobación explícita del propietario para eliminar archivos. Están versionados, así que su borrado sería reversible. **Pendiente de decisión**; mientras tanto no afectan al build ni al bundle (Vite hace tree-shaking de módulos no importados).

---

## Referencias procesadas

- **Implementadas:** `REF-FEED-01`, `REF-PROFILE-01`, `REF-SEARCH-01`, `REF-SET-01..12`.
- **Analizadas en profundidad:** las 24 (familia, sidebar, paleta, tipografía, iconografía).
- **Pendientes de implementar:** `REF-RADAR-01/02`, `REF-PROFILE-02/03`, `REF-MSG-01..05`.

---

## Bloqueos

| # | Bloqueo | Qué hace falta |
|---|---|---|
| 1 | **Radar** sin proveedor de cartografía | Decisión del propietario. §8.8 prohíbe contratar Mapbox/Google Maps por cuenta propia |
| 2 | **Mensajería** sin endpoints | Contrato propuesto en `THERS_UI_INTEGRATION.md` §4; requiere ADR |
| 3 | Guardar/compartir, sugerencias y tendencias sin endpoint | Íd. |
| 4 | Correo real desactivado | Sin `RESEND_API_KEY`; el backend usa un `EmailSender` nulo. Correcto para pruebas |
| 5 | `REF-PROFILE-03` sin captura válida | Irrecuperable salvo que aparezca otra copia |
| 6 | Sin base `thers_test` | Impide la línea base de `pytest` |
| 7 | **Perfil ajeno sin endpoint** | No existe `GET /api/users/<username>`: el backend solo expone `/api/users/me`. Bloquea `REF-PROFILE-02/03` |
| 8 | Sin endpoint para listar «me gusta» ni «destacadas» | El like se registra (ADR-005) pero no se puede recuperar como colección |

Ninguno impide avanzar: la etapa G (Configuración) y la parte de Buscar de la etapa D no dependen de ellos. El bloqueo 7 **sí** detiene el perfil ajeno (`REF-PROFILE-02/03`) hasta que exista un endpoint público de usuario.

---

## Próximas tres acciones

1. **Etapa E — Mensajes**: unificar `REF-MSG-01..05` en bandeja/chat/contexto sobre la variante `messages` del shell (256px). La UI se puede construir entera; los datos quedan bloqueados hasta que exista el contrato de mensajería.
2. **Resto de D — perfil ajeno** (`/u/:username`): reutiliza los componentes de perfil ya construidos. **Bloqueado** hasta que exista un endpoint público de usuario.
3. **Resto de D — Videos/Cortos**: diseño derivado a partir del módulo de vídeo de `REF-SEARCH-01` y de `REF-PROFILE-03`.

---

## Arranque seguro

```bash
cd C:/Users/Escalante/Desktop/THERS_REDSOCIAL_2026
git fetch && git status                       # comprobar cambios del equipo primero

POSTGRES_PORT=5433 docker compose up -d
cd backend && ./venv/Scripts/python.exe run.py            # :5000
cd Frontend && npm run dev                                # :5173

cd Frontend && npm run build && npm run lint              # comprobación rápida
```

Cuenta sintética de QA (solo base de desarrollo): `qa.harness@example.invalid` / `qa_harness`.

---

## Decisiones vigentes que no deben revertirse sin motivo

1. **Dos familias de tokens, un shell.** Aplanar todo a una paleta contradiría la petición de máxima fidelidad (`THERS_DESIGN_SYSTEM.md` §2).
2. **288px en lo social, 256px en Configuración y Mensajes.** Medido en los HTML, no supuesto.
3. **Feed a 700px**, no los 680px de respaldo: es el valor literal de la referencia.
4. **`tokens.css` es la única fuente.** No crear `design-tokens.json`.
5. **Los tokens anteriores (`pulse`, `ink`, `canvas`…) se conservan.** Siguen en uso en auth, help, public y legal.
6. **Ninguna capacidad sin backend se presenta como activa.** Deshabilitada con explicación, o rotulada como ejemplo.
7. **Sin commit ni push** — no se han pedido.
