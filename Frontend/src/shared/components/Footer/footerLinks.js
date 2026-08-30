// Fuente única de los grupos del Footer -- la usan tanto el layout desktop
// (columnas) como el mobile (accordion), para que no puedan desincronizarse.
export const FOOTER_GROUPS = [
  {
    id: "thers",
    title: "THERS",
    links: [
      {
        label: "Información",
        // Sin `to`: este ítem se expande en vez de navegar directo (ver
        // FooterExpandableItem). Sus hijos no repiten nada que ya exista en
        // otro grupo del footer (Ayuda ya está como "Centro de ayuda" aquí
        // mismo, Privacidad/Términos ya están en el grupo Legal).
        children: [
          {
            label: "Sobre THERS",
            description: "Qué es THERS y por qué existe",
            to: "/information",
            icon: "info",
          },
          {
            label: "Cómo funciona",
            description: "Un recorrido rápido por el producto",
            to: "/information/how-it-works",
            icon: "how-it-works",
          },
          {
            label: "Comunidad",
            description: "Quiénes forman parte de THERS",
            to: "/information/community",
            icon: "community",
          },
          {
            label: "Seguridad",
            description: "Cómo protegemos tu cuenta",
            to: "/information/security",
            icon: "security",
          },
          {
            label: "Preguntas frecuentes",
            description: "Respuestas rápidas a lo más común",
            to: "/information/faq",
            icon: "faq",
          },
        ],
      },
      { label: "Blog", to: "/blog" },
      { label: "Centro de ayuda", to: "/help" },
    ],
  },
  {
    id: "discover",
    title: "Descubre",
    links: [
      { label: "Popular", to: "/popular" },
      { label: "Ubicaciones", to: "/locations" },
      { label: "Importar contactos", to: "/contacts/import" },
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
