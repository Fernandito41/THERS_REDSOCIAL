/**
 * Icon — adaptador único de Material Symbols Outlined.
 *
 * Las 23 de 24 referencias que llevan iconografía usan Material Symbols
 * Outlined (docs/THERS_REFERENCE_MANIFEST.md §2). Se conserva esa familia en
 * vez de sustituirla por react-icons, que cambiaría visiblemente silueta y
 * grosor (THERS_IMPLEMENTACION_MAESTRA_CLAUDE.md §5.7).
 *
 * react-icons sigue instalado y en uso en auth/help/public/legal: no se
 * retira nada, solo se deja de usar para el shell y las pantallas nuevas.
 *
 * Accesibilidad: un icono es decorativo por defecto (`aria-hidden`). Cuando
 * es el único contenido de un botón, el nombre accesible lo pone el botón con
 * su `aria-label`, no el icono.
 */
export default function Icon({
  name,
  size = 20,
  fill = 0,
  weight = 400,
  className = "",
  label,
  ...rest
}) {
  return (
    <span
      className={`material-symbols-outlined select-none ${className}`}
      style={{
        fontSize: `${size}px`,
        width: `${size}px`,
        height: `${size}px`,
        "--th-icon-fill": fill,
        "--th-icon-wght": weight,
      }}
      aria-hidden={label ? undefined : true}
      role={label ? "img" : undefined}
      aria-label={label}
      {...rest}
    >
      {name}
    </span>
  );
}
