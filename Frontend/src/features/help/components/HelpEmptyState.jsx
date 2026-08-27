import { IoSearchOutline } from "react-icons/io5";

export default function HelpEmptyState({
  title = "No encontramos artículos relacionados.",
  description = "Probá con otra palabra o explorá las categorías del Centro de Ayuda.",
  action,
}) {
  return (
    <div className="text-center py-16 px-4">
      <div className="mx-auto w-12 h-12 rounded-full bg-canvas dark:bg-canvas-dark border border-line dark:border-line-dark flex items-center justify-center">
        <IoSearchOutline size={20} className="text-muted dark:text-muted-dark" aria-hidden="true" />
      </div>
      <p className="mt-4 text-ink dark:text-ink-dark font-semibold">{title}</p>
      <p className="mt-1.5 text-sm text-muted dark:text-muted-dark max-w-sm mx-auto">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
