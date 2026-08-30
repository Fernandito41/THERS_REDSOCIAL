// Fuente unica de los grupos del Footer. Enlaces planos, una sola forma
// `{ label, to }` -- ya no hay ítems con hijos ni panel desplegable dentro del
// footer (un footer es navegacion, no disclosure). Los 13 destinos existentes
// se conservan, reagrupados para una IA mas clara.
export const FOOTER_GROUPS = [
  {
    id: "product",
    title: "Producto",
    links: [
      { label: "Cómo funciona", to: "/information/how-it-works" },
      { label: "Seguridad", to: "/information/security" },
      { label: "Preguntas frecuentes", to: "/information/faq" },
    ],
  },
  {
    id: "community",
    title: "Comunidad",
    links: [
      { label: "Comunidad", to: "/information/community" },
      { label: "Popular", to: "/popular" },
      { label: "Ubicaciones", to: "/locations" },
      { label: "Importar contactos", to: "/contacts/import" },
    ],
  },
  {
    id: "resources",
    title: "Recursos",
    links: [
      { label: "Sobre THERS", to: "/information" },
      { label: "Blog", to: "/blog" },
      { label: "Centro de ayuda", to: "/help" },
    ],
  },
  {
    id: "legal",
    title: "Legal",
    links: [
      { label: "Privacidad", to: "/privacy" },
      { label: "Términos", to: "/terms" },
      { label: "Cookies", to: "/cookies" },
    ],
  },
];

// La variante `compact` (AuthPage) solo muestra los enlaces legales en linea.
export const LEGAL_LINKS = FOOTER_GROUPS.find((g) => g.id === "legal").links;
