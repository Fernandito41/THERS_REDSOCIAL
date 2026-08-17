// Capa decorativa de profundidad, reutilizada en las páginas de auth y en el
// shell autenticado -- un único lenguaje visual, no dos fondos distintos.
export default function AmbientGlow() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 overflow-hidden -z-10">
      <div className="absolute -top-40 -left-32 w-[34rem] h-[34rem] rounded-full bg-pulse-400/20 dark:bg-pulse-500/10 blur-3xl" />
      <div className="absolute -bottom-32 -right-20 w-[28rem] h-[28rem] rounded-full bg-pulse-700/15 dark:bg-pulse-800/20 blur-3xl" />
    </div>
  );
}
