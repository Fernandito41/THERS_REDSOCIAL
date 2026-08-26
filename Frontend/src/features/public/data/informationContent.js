import capsulasVideo from "@/assets/comparte_sin_filtro.mp4";
import momentosImage from "@/assets/publicacion.jpg";

// Contenido editorial de /information -- 4 features reales de THERS (no
// "Reels" ni conceptos que el producto no tiene).
//
// "chat" y "perfil" siguen sin mediaSrc a propósito: los archivos que se
// agregaron para esos dos (conversaciones.jpg, perfil.jpg) son mockups de
// UI genéricos de otra app (uno trae el watermark "LIVEGRAM"), no contenido
// de THERS -- ver aviso en el chat. Para completarlos: importar el archivo
// real desde `src/assets/` arriba de este módulo y asignarlo a `mediaSrc`
// (`mediaPoster` además si es video). Mientras falte, MediaPlaceholder.jsx
// muestra el placeholder "próximamente".
export const INFORMATION_CARDS = [
  {
    id: "capsulas",
    tag: "#Cápsulas",
    mediaType: "video",
    mediaSrc: capsulasVideo,
    mediaAlt: "Vista previa de una Cápsula en THERS",
    title: "Comparte sin filtros",
    description:
      "Publicá fotos, videos y música en tus Cápsulas para que las personas que resuenan con vos puedan descubrirte.",
    ctaLabel: "Descubrir",
    ctaTo: "/",
  },
  {
    id: "momentos",
    tag: "#Momentos",
    mediaType: "image",
    mediaSrc: momentosImage,
    mediaAlt: "Vista previa de Momentos en THERS",
    title: "Lo que pasa hoy, se comparte hoy",
    description: "Compartí Momentos del día a día que acompañan tu perfil sin quedarse fijos para siempre.",
  },
  {
    id: "chat",
    tag: "#Chat",
    mediaType: "video",
    mediaSrc: undefined,
    mediaPoster: undefined,
    mediaAlt: "Vista previa del chat de THERS",
    title: "Conversaciones que fluyen",
    description: "Mensajes instantáneos para mantenerte cerca de las personas que realmente importan.",
  },
  {
    id: "perfil",
    tag: "#Perfil",
    mediaType: "image",
    mediaSrc: undefined,
    mediaAlt: "Vista previa de un perfil de THERS",
    title: "Creá tu identidad",
    description: "Personalizá tu perfil con tu mood y tu color, y construí una presencia única dentro de THERS.",
  },
];
