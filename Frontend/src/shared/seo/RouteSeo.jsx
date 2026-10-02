import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { buildCanonicalUrl, getSeoForPath } from "./seoRoutes";

// Aplica título, descripción, robots y canonical de la ruta actual
// (ADR-033-seo-foundation.md). Se monta una sola vez dentro del Router.
//
// El canonical NUNCA vive estático en index.html: ahí todas las rutas
// declararían la home como su versión canónica y Google las desindexaría.
// `VITE_SITE_URL` es opcional: sin ella no se escribe canonical (mejor ninguno
// que uno apuntando al dominio equivocado).

const SITE_URL = import.meta.env.VITE_SITE_URL;

function upsertMeta(name, content) {
  let el = document.head.querySelector(`meta[name="${name}"]`);
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute("name", name);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function upsertCanonical(href) {
  let el = document.head.querySelector('link[rel="canonical"]');
  if (!href) {
    el?.remove();
    return;
  }
  if (!el) {
    el = document.createElement("link");
    el.setAttribute("rel", "canonical");
    document.head.appendChild(el);
  }
  el.setAttribute("href", href);
}

export default function RouteSeo() {
  const { pathname } = useLocation();

  useEffect(() => {
    const seo = getSeoForPath(pathname);
    document.title = seo.title;
    upsertMeta("description", seo.description);
    upsertMeta("robots", seo.index ? "index, follow" : "noindex, nofollow");
    upsertCanonical(seo.index ? buildCanonicalUrl(SITE_URL, seo.path) : null);
  }, [pathname]);

  return null;
}
