// Skeletons de carga -- respetan prefers-reduced-motion vía la utilidad
// `animate-pulse` de Tailwind, que ya se apaga con `motion-reduce:` si el
// resto de la app lo necesitara; acá se mantiene sutil (solo opacidad).
export function HelpArticleListSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4" aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="rounded-2xl border border-line dark:border-line-dark bg-surface dark:bg-surface-dark p-5 space-y-3"
        >
          <div className="h-3 w-20 rounded-full bg-line dark:bg-line-dark animate-pulse" />
          <div className="h-4 w-4/5 rounded-full bg-line dark:bg-line-dark animate-pulse" />
          <div className="h-3 w-full rounded-full bg-line dark:bg-line-dark animate-pulse" />
          <div className="h-3 w-2/3 rounded-full bg-line dark:bg-line-dark animate-pulse" />
        </div>
      ))}
    </div>
  );
}

export function HelpArticleBodySkeleton() {
  return (
    <div className="space-y-4" aria-hidden="true">
      <div className="h-3 w-32 rounded-full bg-line dark:bg-line-dark animate-pulse" />
      <div className="h-7 w-3/4 rounded-full bg-line dark:bg-line-dark animate-pulse" />
      <div className="space-y-2 pt-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-3 w-full rounded-full bg-line dark:bg-line-dark animate-pulse" />
        ))}
      </div>
    </div>
  );
}
