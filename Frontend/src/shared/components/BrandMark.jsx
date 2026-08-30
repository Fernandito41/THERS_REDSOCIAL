import logoTH from "@/assets/logo_TH.png";

// Lockup ícono + wordmark reutilizado por Footer y PublicLayout (las partes
// públicas nuevas). El PNG del logo trae su propio fondo gris no
// transparente -- se recorta a círculo para que no se note como una caja
// cuadrada sobre `surface`/`canvas`.
export default function BrandMark({ size = "text-xl", iconSize = "w-6 h-6" }) {
  return (
    <span className={`inline-flex items-center gap-2 ${size}`}>
      <img src={logoTH} alt="" className={`${iconSize} rounded-full object-cover shrink-0`} />
      <span className="font-extrabold tracking-tight text-ink dark:text-ink-dark">THERS</span>
    </span>
  );
}
