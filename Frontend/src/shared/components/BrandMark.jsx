import logoTH from "@/assets/logo_TH.png";

// Lockup ícono + wordmark reutilizado por Footer y PublicLayout (las partes
// públicas nuevas). El PNG del logo trae su propio fondo gris no
// transparente -- se recorta a círculo para que no se note como una caja
// cuadrada sobre `surface`/`canvas`.
// `tone`: "auto" (por defecto) -> texto ink/ink-dark segun el modo claro/oscuro.
//         "invert" -> texto siempre blanco, para superficies oscuras en
//         cualquier modo (p. ej. el zocalo del Footer default).
export default function BrandMark({ size = "text-xl", iconSize = "w-6 h-6", tone = "auto" }) {
  const wordColor = tone === "invert" ? "text-zinc-50" : "text-ink dark:text-ink-dark";
  return (
    <span className={`inline-flex items-center gap-2 ${size}`}>
      <img src={logoTH} alt="" className={`${iconSize} rounded-full object-cover shrink-0`} />
      <span className={`font-extrabold tracking-tight ${wordColor}`}>THERS</span>
    </span>
  );
}
