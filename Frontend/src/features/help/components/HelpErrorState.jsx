import { IoAlertCircleOutline, IoRefreshOutline } from "react-icons/io5";

export default function HelpErrorState({ onRetry }) {
  return (
    <div className="text-center py-16 px-4">
      <div className="mx-auto w-12 h-12 rounded-full bg-ember-50 dark:bg-ember-900/20 flex items-center justify-center">
        <IoAlertCircleOutline size={22} className="text-ember-500" aria-hidden="true" />
      </div>
      <p className="mt-4 text-ink dark:text-ink-dark font-semibold">No pudimos cargar el Centro de Ayuda.</p>
      <p className="mt-1.5 text-sm text-muted dark:text-muted-dark">Ocurrió un problema al mostrar este contenido.</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-5 inline-flex items-center gap-2 text-sm font-semibold px-4 py-2 rounded-full bg-pulse-600 hover:bg-pulse-700 text-white transition"
      >
        <IoRefreshOutline size={16} aria-hidden="true" />
        Intentar nuevamente
      </button>
    </div>
  );
}
