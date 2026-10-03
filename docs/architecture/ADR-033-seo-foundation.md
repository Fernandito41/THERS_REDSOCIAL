# ADR-033 — Base de SEO del Frontend

- **Estado:** **`PROPUESTO`** el 2026-10-02 — **pendiente de aprobación del equipo** (`HB-001` §11–12).
  Lo redactó Claude Code a pedido del propietario del proyecto; no es una decisión ratificada.
- **Fecha:** 2026-10-02
- **Por qué existe:** el Frontend es una SPA sin ninguna señal para buscadores: `<title>THERS</title>`
  fijo, `lang="en"` en una app en español, sin `description`, sin `robots.txt` ni `sitemap.xml`, sin
  ruta 404 y con páginas "estamos construyendo esta sección" que Google trataría como contenido
  delgado. Se arregla la base **antes** de publicar, para no indexar basura que luego cueste retirar.
- **Relacionado:** `docs/LAUNCH_CHECKLIST.md` §3, `ADR-018-hosting-domain-environments.md` (dominio),
  `FRONTEND_ARCHITECTURE.md`.

---

## 1. Qué se implementa en esta fase

| Pieza | Dónde | Efecto |
|---|---|---|
| Tabla única de rutas indexables | `src/shared/seo/seoRoutes.js` | Una sola fuente para el navegador y para el build |
| `RouteSeo` | `src/shared/seo/RouteSeo.jsx` | Por ruta: `title`, `description`, `robots`, `canonical` |
| Ruta comodín `*` | `src/shared/seo/NotFound.jsx` | URL rota → página útil con `noindex` |
| Plugin de build sin dependencias | `Frontend/vite-seo-files.js` | Genera `robots.txt` y `sitemap.xml` |
| `index.html` | `Frontend/index.html` | `lang="es"`, `description`, `theme-color`, Open Graph base |
| Variable `VITE_SITE_URL` | `Frontend/.env.example` | Dominio público para URLs absolutas |

## 2. Reglas de diseño

1. **`noindex` por defecto.** Solo se indexa lo que está en la tabla. La app tras el login, los
   flujos de autenticación y las páginas en construcción **no** entran. Olvidarse de registrar una
   ruta nueva falla por el lado seguro.
2. **Indexables hoy:** `/`, `/information`, `/help`, las 8 categorías de ayuda y los artículos con
   `status: "available"` (19 de 29). Los `in-progress` describen funciones que aún no existen.
3. **Páginas "estamos construyendo"** (`/terms`, `/privacy`, `/cookies`, `/blog`, `/popular`,
   `/locations`, `/contacts/import`, `/information/*`): `noindex` y fuera del sitemap hasta que
   tengan contenido real. Al publicarlas, se agregan a `seoRoutes.js`.
4. **Sin `canonical` estático** en `index.html`: en una SPA todas las rutas compartirían el
   canonical de la home y Google las descartaría. Se escribe por ruta, y solo si `VITE_SITE_URL`
   existe (mejor ninguno que uno al dominio equivocado).
5. **Sin `VITE_SITE_URL` el build es seguro:** `robots.txt` con `Disallow: /` y sin sitemap. Nada se
   indexa por accidente en staging o en un preview.
6. **`lastmod` solo cuando es real** (fecha del artículo). Una fecha inventada en todas las URLs
   hace que Google ignore el campo.
7. `robots.txt` **no es seguridad**: la protección de lo privado es el JWT. Solo ahorra presupuesto
   de rastreo.

## 3. Verificado (2026-10-02)

- `npm run lint`: 0 errores (3 advertencias previas, ajenas).
- `npm run build` sin `VITE_SITE_URL`: `robots.txt` bloquea todo, no hay `sitemap.xml`.
- `npm run build` con `VITE_SITE_URL=https://thers.example/`: `sitemap.xml` válido con 30 URLs
  (3 estáticas + 8 categorías + 19 artículos), ninguna `in-progress`; `robots.txt` con `Sitemap:`.
- Resolución de rutas: `/help/` y `/help` coinciden; `/terms`, `/feed`, rutas inventadas y artículos
  inexistentes → `noindex`.

## 4. Limitaciones conocidas y decisiones abiertas (NO resueltas aquí)

| Tema | Situación | Opciones |
|---|---|---|
| **Renderizado** | Una SPA entrega `<div id="root">` vacío; Google ejecuta JS pero con retraso y Bing/redes sociales mucho menos. Las etiquetas por ruta se ponen **en el navegador** | (a) **prerender en build** de las ~30 rutas públicas (p. ej. `vite-react-ssg` o un script con Puppeteer; es la opción recomendada, añade una dependencia); (b) SSR (cambio grande, innecesario para contenido casi estático); (c) quedarse como está y aceptar la indexación diferida |
| **404 real** | Hosting estático devuelve 200 con `index.html` para cualquier ruta (*soft 404*); `noindex` mitiga, no equivale a un 404 | Lo resuelve el hosting o el prerender (ADR-018); definir al elegirlo |
| **Imagen Open Graph** | No hay recurso de marca; sin `og:image` las previas son pobres | Esperar el asset; no inventar uno |
| **Idiomas / `hreflang`** | El idioma se cambia en cliente (`LanguageContext`), con **una sola URL** por página: no se puede declarar `hreflang` honestamente | Rutas por idioma (`/en/...`) si se quiere SEO en inglés |
| **Datos estructurados** | No hay `Organization`/`WebSite` | Añadir JSON-LD a la landing cuando exista dominio y logo definitivos |
| **Core Web Vitals** | Un solo bundle de ~600 kB | `React.lazy` por ruta: PR aparte, con medición Lighthouse en staging |
| **Search Console** | Requiere dominio | Tras `ADR-018`; enviar `sitemap.xml` |

## 5. Consecuencias

- Costo: 4 archivos nuevos y 4 editados, **cero dependencias nuevas**.
- Riesgo: si alguien añade una página pública y no la registra en `seoRoutes.js`, no se indexa
  (falla segura, pero hay que saberlo). Queda escrito en el encabezado de ese archivo.
- Deuda reconocida: sin prerender, el SEO real de la landing queda limitado (§4).
