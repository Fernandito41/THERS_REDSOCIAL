import Icon from "@shared/components/Icon";

/**
 * Marcador honesto para un módulo cuya ruta ya existe en la navegación pero
 * cuya pantalla todavía no está implementada.
 *
 * Existe para cumplir el archivo maestro §6.3 ("todas las pantallas deben
 * poder abrirse desde la interfaz y desde su URL prevista") sin fingir que el
 * módulo está terminado. Declara en pantalla qué referencia canónica le
 * corresponde y qué falta, en vez de mostrar datos de muestra que parezcan
 * reales (§1, §9.4: "Solo existe la maqueta -> funcionalidad pendiente, nunca
 * completa").
 *
 * Cada módulo sustituye este componente por su implementación real en su
 * etapa correspondiente; el estado vive en docs/THERS_UI_INTEGRATION.md.
 */
export default function ModulePending({ title, reference, stage, summary, pending = [] }) {
  return (
    <div className="mx-auto flex max-w-th-feed flex-col gap-6 py-8">
      <header className="flex flex-col gap-2">
        <span className="inline-flex w-fit items-center gap-2 rounded-th-pill border border-th-border bg-th-surface-subtle px-3 py-1 text-label-sm font-bold uppercase tracking-wide text-th-fg-muted">
          <Icon name="construction" size={14} />
          Módulo en construcción
        </span>
        <h1 className="text-headline-lg text-th-fg-strong">{title}</h1>
        {summary && <p className="text-body-md text-th-fg-muted">{summary}</p>}
      </header>

      <div className="flex flex-col gap-4 rounded-th-card border border-th-border bg-th-surface p-6 shadow-th-card">
        <dl className="grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-label-md uppercase tracking-wide text-th-fg-subtle">
              Referencia canónica
            </dt>
            <dd className="mt-1 text-body-md font-semibold text-th-fg-strong">{reference}</dd>
          </div>
          <div>
            <dt className="text-label-md uppercase tracking-wide text-th-fg-subtle">Etapa</dt>
            <dd className="mt-1 text-body-md font-semibold text-th-fg-strong">{stage}</dd>
          </div>
        </dl>

        {pending.length > 0 && (
          <div className="border-t border-th-border-subtle pt-4">
            <p className="text-label-md uppercase tracking-wide text-th-fg-subtle">Pendiente</p>
            <ul className="mt-2 flex flex-col gap-1.5">
              {pending.map((item) => (
                <li key={item} className="flex items-start gap-2 text-body-md text-th-fg-muted">
                  <Icon name="radio_button_unchecked" size={16} className="mt-1 shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <p className="text-body-sm text-th-fg-subtle">
        Estado detallado por módulo en <code>docs/THERS_UI_INTEGRATION.md</code>.
      </p>
    </div>
  );
}
