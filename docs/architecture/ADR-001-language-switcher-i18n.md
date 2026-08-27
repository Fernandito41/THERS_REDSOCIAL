# ADR-001 — Selector de idioma (i18n) del Frontend

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-001-language-switcher-i18n.md` |
| Tipo | Architecture Decision Record (`HB-001` §11–12) |
| Fecha | 26/08/2026 |
| Estado | **Aceptada** — implementada en Fase 1 (ver §3) |
| Alcance | Exclusivamente `Frontend/` |
| Autor | Fernando Escalante (decisión confirmada en sesión de trabajo con IA, ver §6) |
| Autoridad sobre este documento | `/docs` oficial > estructura real observada en el código > este documento (mismo orden que `CLAUDE.md` §4) |

> ⚠️ **Nota de desviación de proceso — explícita y deliberada, no silenciosa.** `HB-001` §12 especifica textualmente que los ADR se registran **en Notion**, en la página "Registro de Decisiones" — no como archivo Markdown en `docs/architecture/`. Este documento se crea aquí por pedido explícito de Fernando Escalante (26/08/2026), como excepción pragmática: un ADR versionado junto al código, con el mismo criterio de formato que ya usan `BACKEND_ARCHITECTURE.md`, `FRONTEND_ARCHITECTURE.md`, `DATABASE_ARCHITECTURE.md` y `API_CONTRACT.md` (separar explícitamente lo implementado de lo pendiente, sin autoproclamarse cerrado). No es un reemplazo silencioso del proceso oficial de `HB-001` §12: si el equipo decide que Notion debe seguir siendo la única fuente de ADRs, este archivo debería migrarse o duplicarse allí, y esta nota debe actualizarse para reflejarlo.
>
> La numeración `ADR-001` es local a este archivo — no se verificó contra el conteo real del "Registro de Decisiones" en Notion, que esta tarea no consultó por no habérselo pedido el equipo explícitamente. Si ya existen ADRs numerados en Notion, este documento podría requerir renumerarse.

---

## 1. Contexto

THERS no tenía ninguna estrategia de internacionalización (i18n) antes de esta decisión: ni librería instalada, ni estructura de traducciones, ni ningún documento en `/docs` que la cubriera — un hueco no identificado hasta esta tarea (`CLAUDE.md` §15 no lo listaba). Todo el texto de la interfaz del Frontend estaba hardcodeado en español directamente en JSX, sin ningún punto de extensión.

Se pidió agregar un selector de idioma "de manera ordenada, como una red social profesional". Por tratarse de una decisión de arquitectura nueva que afecta potencialmente a toda la superficie del Frontend (impacto medio/alto según la tabla de `HB-001` §11: "elegir una librería nueva" es impacto medio como mínimo), no se implementó por iniciativa propia — se confirmaron 3 decisiones con Fernando antes de escribir código (§2).

## 2. Opciones consideradas

### 2.1 Enfoque técnico

| Opción | Descripción | Trade-off |
|---|---|---|
| **Context propio (elegida)** | `LanguageContext` + un JSON por idioma + hook `useLanguage()` — mismo patrón que `AuthContext`, `ToastContext` y `useTheme` ya usan en el Frontend | Sin dependencia nueva; menos funcionalidad de fábrica (sin pluralización avanzada, sin interpolación compleja, detección de idioma del navegador simple) |
| `react-i18next` | Librería estándar de la industria para i18n en React | Pluralización, interpolación avanzada, ecosistema maduro; agrega una dependencia nueva inexistente hoy en `Frontend/package.json` |

### 2.2 Idiomas a soportar

| Opción | Elegida |
|---|---|
| Español (por defecto) + Inglés | ✅ |
| Español + Inglés + Portugués | — |

### 2.3 Alcance de la Fase 1

| Opción | Elegida |
|---|---|
| Infraestructura + navegación, autenticación y Configuración | ✅ |
| Toda la aplicación de una vez (incluye contenido mock del feed, páginas públicas y los 28 artículos del Centro de Ayuda) | — |

## 3. Decisión

Se implementó:

1. **`Frontend/src/shared/i18n/`** — núcleo de traducción propio, sin dependencias nuevas: `LanguageContext.jsx` (`LanguageProvider` / `useLanguage`), `translate.js` (`t(key, vars)` con notación de puntos e interpolación `{{var}}`; `tList(key)` para arrays, como nombres de mes), `languages.js`, y `locales/es.json` / `locales/en.json` con las mismas claves en ambos idiomas.
2. **`Frontend/src/shared/components/LanguageSwitcher.jsx`** — control segmentado ES/EN, reutilizado en el menú de perfil de `AppShell`, en `Settings.jsx` (nueva sección "Idioma") y en las 4 pantallas de autenticación.
3. **Persistencia** en `localStorage` (clave `thers_language`), español por defecto la primera vez que alguien entra, respetando después la elección de la persona — mismo patrón que `useTheme.js` ya usa para el tema (`theme`, oscuro por defecto).
4. **Alcance traducido en esta fase**: `AppShell`, `NavRail`, `MobileNav`; las 4 páginas de autenticación (`AuthPage`, `Login`, `Register`, `ForgotPassword`, `ResetPassword`) y sus componentes compartidos (`AuthCard`, `PasswordField`, `PasswordStrength` + `usePasswordStrength`, `PhoneField`, `BirthDateField` + `dateUtils.formatDisplayDate`, `TrustNote`); `Settings.jsx`; y `shared/lib/api.js`, donde `getErrorMessage(error, t)` ahora recibe el traductor como parámetro en vez de hardcodear español, para no acoplar ese módulo (cliente HTTP puro) a React.
5. **Explícitamente fuera de alcance de esta fase**: contenido mock del feed (`features/feed/data/mockData.js`), páginas públicas informativas (`features/public`), los 28 artículos del Centro de Ayuda (`features/help`), y los nombres de país en `PhoneField.jsx` (documentado con comentario explícito en ese mismo archivo).

## 4. Consecuencias

- Cualquier página o componente nuevo dentro del alcance ya traducido (nav/auth/settings) debe usar `useLanguage().t()` en vez de hardcodear español — no seguir este patrón sería inconsistente con el resto del Frontend ya migrado en esta fase.
- Las fases siguientes (feed, páginas públicas, Centro de Ayuda) deben heredar la misma convención de claves (`shared/i18n/locales/*.json`, notación de puntos, `t()`/`tList()`) — no introducir una segunda estructura de traducciones en paralelo.
- Adoptar `react-i18next` más adelante es una decisión de impacto medio nueva (`HB-001` §11), no una consecuencia automática de este ADR — si el equipo lo evalúa, debe registrarse como su propio ADR, no como una extensión silenciosa de este.
- `PhoneField.jsx` sigue mostrando nombres de país solo en español hasta que una fase futura los traduzca explícitamente (o decida mantenerlos en español/nombre local a propósito).
- Este documento no resuelve la contradicción de proceso señalada en la nota de desviación (encabezado) — queda pendiente que el equipo decida si los ADR de THERS viven en Notion, en `docs/architecture/`, o en ambos.

## 5. Verificación

`npm run lint` y `npm run build` limpios tras la implementación. Las 172 claves de traducción usadas en código (169 `t()` + 3 `tList()`) fueron verificadas programáticamente contra ambos `locales/*.json` sin faltantes en ninguno de los dos idiomas.

## 6. Fuentes consultadas

- `CLAUDE.md` (raíz) — jerarquía de fuentes (§4) y regla de incertidumbre (§15).
- `docs/architecture/organization/01_Manual_Organizacion/Source/HB-001-manual-organizacion.md.md` §11–12 — proceso de decisiones técnicas y plantilla de ADR.
- `docs/architecture/FRONTEND_ARCHITECTURE.md` — stack y convenciones existentes del Frontend, usado como referencia de formato para este documento.
- Código real de `Frontend/src/shared/i18n/`, `Frontend/src/shared/components/LanguageSwitcher.jsx`, y los archivos listados en §3.4.
- Confirmación explícita de Fernando Escalante sobre las 3 decisiones de §2, en la misma sesión de trabajo que produjo este documento.

---

## Cierre

Este documento registra la decisión de introducir i18n en el Frontend de THERS con el enfoque, idiomas y alcance de Fase 1 descritos en §3, y dónde queda explícitamente pendiente cada continuación (§4). No resuelve la discrepancia sobre dónde deben vivir los ADR de THERS (Notion vs. `docs/architecture/`) — esa decisión de gobernanza sigue abierta y debe tratarla el equipo, no un documento individual.
