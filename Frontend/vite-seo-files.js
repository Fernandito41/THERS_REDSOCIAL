// Plugin de Vite sin dependencias: genera `robots.txt` y `sitemap.xml` en el
// build a partir de la tabla de `src/shared/seo/seoRoutes.js`
// (ADR-033-seo-foundation.md).
//
// Ambos archivos necesitan URLs absolutas, así que dependen de `VITE_SITE_URL`.
// Sin ella (desarrollo, o antes de comprar el dominio) se genera un robots.txt
// que **no deja indexar nada** y no se genera sitemap: publicar URLs inventadas
// sería peor que no publicar ninguna.

import { buildCanonicalUrl, getIndexableRoutes } from "./src/shared/seo/seoRoutes.js";

// Rutas privadas: la app tras el login. Un robots.txt es una cortesía, no
// seguridad (la protección real es el JWT); sirve para que los rastreadores no
// pierdan presupuesto en pantallas que solo muestran el login.
const PRIVATE_PATHS = [
  "/feed",
  "/search",
  "/videos",
  "/capsules",
  "/radar",
  "/messages",
  "/notifications",
  "/profile",
  "/settings",
  "/complete-profile",
  "/two-factor",
  "/reset-password",
  "/verify-registration-code",
  "/verify-reset-code",
];

function escapeXml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export function buildRobotsTxt(siteUrl) {
  if (!siteUrl) {
    return "# Sin VITE_SITE_URL: sitio sin publicar, no indexar.\nUser-agent: *\nDisallow: /\n";
  }
  const lines = ["User-agent: *", "Allow: /", ...PRIVATE_PATHS.map((p) => `Disallow: ${p}`)];
  lines.push("", `Sitemap: ${buildCanonicalUrl(siteUrl, "/sitemap.xml")}`);
  return `${lines.join("\n")}\n`;
}

export function buildSitemapXml(siteUrl) {
  if (!siteUrl) return null;
  const urls = getIndexableRoutes().map((route) => {
    const loc = escapeXml(buildCanonicalUrl(siteUrl, route.path));
    // Solo se declara `lastmod` cuando es real (fecha del artículo): una fecha
    // inventada en todas las URLs hace que Google deje de confiar en el campo.
    const lastmod = route.lastmod ? `<lastmod>${route.lastmod}</lastmod>` : "";
    return `  <url><loc>${loc}</loc>${lastmod}</url>`;
  });
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join("\n")}\n</urlset>\n`;
}

export default function seoFiles(siteUrl) {
  const normalized = (siteUrl || "").trim().replace(/\/+$/, "");
  return {
    name: "thers-seo-files",
    apply: "build",
    generateBundle() {
      this.emitFile({ type: "asset", fileName: "robots.txt", source: buildRobotsTxt(normalized) });
      const sitemap = buildSitemapXml(normalized);
      if (sitemap) this.emitFile({ type: "asset", fileName: "sitemap.xml", source: sitemap });
    },
  };
}
