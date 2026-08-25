// Placeholder mínimo y explícito para las páginas públicas que todavía no
// tienen contenido real (Fase 1 = solo navegación). Cada página futura
// reemplaza este componente por su propia implementación -- no reutilizar
// para contenido definitivo.
export default function ComingSoon({ title, description }) {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16 sm:py-24 text-center">
      <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-ink dark:text-ink-dark">{title}</h1>
      <p className="mt-3 text-muted dark:text-muted-dark">{description}</p>
      <span className="inline-block mt-6 text-xs font-semibold uppercase tracking-wide text-pulse-600 dark:text-pulse-300 bg-pulse-50 dark:bg-pulse-900/30 rounded-full px-3 py-1.5">
        Próximamente
      </span>
    </div>
  );
}
