// Identidad visual del perfil de THERS -- monocroma por decisión de producto
// (referencia: Frontend/src/assets/ideas_perfil.jpeg). El acento morado
// (`pulse`, tailwind.config.js) deja de imponerse en esta página y pasa a ser
// una opción más entre tonos neutros, para que la jerarquía la marque el
// contraste (ink/canvas/line) y no el color.
//
// No hay backend de subida de archivos ni columnas de avatar/portada
// ratificadas (DATABASE_ARCHITECTURE.md §4.B), así que la portada es un
// degradé que la persona elige -- nunca una foto inventada. Se guardan como
// degradés en línea (no clases de Tailwind) para no depender de que el JIT
// genere valores arbitrarios construidos dinámicamente.

export const COVERS = {
  carbon: {
    label: "Carbón",
    gradient: "linear-gradient(135deg, #09090b 0%, #27272a 52%, #52525b 100%)",
  },
  granite: {
    label: "Granito",
    gradient: "linear-gradient(135deg, #52525b 0%, #a1a1aa 52%, #d4d4d8 100%)",
  },
  mist: {
    label: "Bruma",
    gradient: "linear-gradient(135deg, #d4d4d8 0%, #f4f4f5 52%, #ffffff 100%)",
  },
  linen: {
    label: "Lino",
    gradient: "linear-gradient(135deg, #d6d3d1 0%, #e7e5e4 55%, #fafaf9 100%)",
  },
  pulse: {
    label: "Pulso",
    gradient: "linear-gradient(135deg, #3b0764 0%, #7e22ce 55%, #c084fc 100%)",
  },
};

export const DEFAULT_COVER = "carbon";

// Fondo del avatar (iniciales en blanco encima). Los cuatro superan 4.5:1
// contra texto blanco -- AA para texto normal, no solo para texto grande:
// #18181b 17.4:1 | #3f3f46 10.9:1 | #52525b 7.8:1 | #9333ea 5.0:1.
export const ACCENTS = [
  { value: "#18181b", label: "Tinta" },
  { value: "#3f3f46", label: "Grafito" },
  { value: "#52525b", label: "Acero" },
  { value: "#9333ea", label: "Pulso" },
];

export const DEFAULT_ACCENT = "#18181b";

export function coverGradient(cover) {
  return (COVERS[cover] || COVERS[DEFAULT_COVER]).gradient;
}
