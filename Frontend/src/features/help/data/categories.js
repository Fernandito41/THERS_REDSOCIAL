// Categorías del Centro de Ayuda -- ids usados en la ruta /help/category/:categoryId
// y como clave de agrupación en articles.js. `icon` es una clave resuelta por
// components/helpIcons.js (mismo patrón que Footer/footerLinks.js + FooterExpandableItem).
export const HELP_CATEGORIES = [
  {
    id: "cuenta",
    title: "Cuenta y perfil",
    description: "Crear tu cuenta, iniciar sesión y personalizar tu perfil.",
    icon: "account",
  },
  {
    id: "seguridad",
    title: "Seguridad",
    description: "Cómo protegemos el acceso a tu cuenta en THERS.",
    icon: "security",
  },
  {
    id: "privacidad",
    title: "Privacidad",
    description: "Quién puede ver tu actividad y cómo controlarla.",
    icon: "privacy",
  },
  {
    id: "publicaciones",
    title: "Publicaciones",
    description: "Cápsulas, Momentos y todo lo que compartís en THERS.",
    icon: "posts",
  },
  {
    id: "interacciones",
    title: "Interacciones",
    description: "Likes, comentarios, guardados y a quién seguís.",
    icon: "interactions",
  },
  {
    id: "notificaciones",
    title: "Notificaciones",
    description: "Qué te avisamos y cómo administrarlo.",
    icon: "notifications",
  },
  {
    id: "reportes",
    title: "Reportes y moderación",
    description: "Reportar contenido o cuentas que incumplen las normas.",
    icon: "reports",
  },
  {
    id: "configuracion",
    title: "Configuración",
    description: "Apariencia, cuenta y preferencias generales.",
    icon: "settings",
  },
];

export function getCategoryById(categoryId) {
  return HELP_CATEGORIES.find((category) => category.id === categoryId) || null;
}
