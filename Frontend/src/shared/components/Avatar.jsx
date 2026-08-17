// Variantes del morado de THERS (misma familia que `pulse` en tailwind.config.js)
// -- exclusiva de este componente, usado solo por el shell autenticado
// (@app/layout, @features/feed). No afecta Login/Register.
const PALETTE = [
  "#a855f7",
  "#9333ea",
  "#7e22ce",
  "#6b21a8",
  "#c084fc",
  "#581c87",
];

function initialsFrom(name) {
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((part) => part.charAt(0).toUpperCase()).join("");
}

function colorFrom(name) {
  const sum = name
    .split("")
    .reduce((total, char) => total + char.charCodeAt(0), 0);
  return PALETTE[sum % PALETTE.length];
}

// `photo`: solo para personas mock (Momentos, sugerencias, conversaciones,
// notificaciones) -- el usuario autenticado real nunca tiene una foto real
// disponible (sin backend de almacenamiento de archivos todavía), así que
// jamás se le pasa esta prop: se queda en iniciales, nunca en una foto inventada.
// `color`: override opcional (usado en Profile.jsx para el acento personalizable).
export default function Avatar({ name, size = "w-10 h-10", ring = false, className = "", photo, color }) {
  const initials = initialsFrom(name || "?");
  const background = color || colorFrom(name || "?");

  return (
    <div
      className={`${ring ? "p-[2px] rounded-full bg-gradient-to-tr from-pulse-600 to-pulse-300" : ""} ${className}`}
    >
      {photo ? (
        <img
          src={photo}
          alt={name}
          loading="lazy"
          className={`${size} rounded-full object-cover ${
            ring ? "ring-2 ring-surface dark:ring-surface-dark" : ""
          }`}
        />
      ) : (
        <div
          className={`${size} rounded-full flex items-center justify-center font-semibold text-white ${
            ring ? "ring-2 ring-surface dark:ring-surface-dark" : ""
          }`}
          style={{ backgroundColor: background }}
        >
          {initials}
        </div>
      )}
    </div>
  );
}
