import Icon from "@shared/components/Icon";

/**
 * Primitivas compartidas por las 12 secciones de Configuración.
 *
 * Una sola implementación de grupo, fila, interruptor, selector y acción, para
 * que las doce pantallas no repitan su propio maquetado (archivo maestro §3.1
 * y §6: reutilizar antes de duplicar).
 *
 * Cada fila declara su ESTADO REAL de forma visible:
 *   · `local`     — se guarda en este navegador (settingsStorage.js)
 *   · `pending`   — dibujado en la referencia, sin soporte de servidor
 *   · `server`    — conectado a un endpoint real
 */

/** Cabecera de una sección (panel derecho). */
export function SectionHeader({ title, description, badge }) {
  return (
    <header className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-headline-md text-th-fg-strong">{title}</h1>
        {badge && (
          <span className="rounded-th-pill bg-th-brand-soft px-2.5 py-0.5 text-label-sm font-bold uppercase tracking-wide text-th-brand-fg">
            {badge}
          </span>
        )}
      </div>
      {description && <p className="max-w-3xl text-body-md text-th-fg-muted">{description}</p>}
    </header>
  );
}

/** Grupo de ajustes: tarjeta blanca con título y filas. */
export function SettingGroup({ title, description, index, children }) {
  return (
    <section className="flex flex-col gap-4 rounded-th-card border border-th-border bg-th-surface p-6 shadow-th-card">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h2 className="text-headline-sm text-th-fg-strong">{title}</h2>
          {description && <p className="text-body-sm text-th-fg-muted">{description}</p>}
        </div>
        {index && (
          <span className="shrink-0 rounded-th-pill bg-th-surface-raised px-2.5 py-0.5 text-label-sm font-bold uppercase tracking-wider text-th-fg-muted">
            {index}
          </span>
        )}
      </header>
      <div className="flex flex-col divide-y divide-th-border-subtle">{children}</div>
    </section>
  );
}

/** Fila genérica: etiqueta + descripción a la izquierda, control a la derecha. */
function Row({ label, description, badge, control, hint }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-4 py-4 first:pt-0 last:pb-0">
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-label-lg font-semibold text-th-fg-strong">{label}</span>
          {badge}
        </div>
        {description && <p className="max-w-2xl text-body-sm text-th-fg-muted">{description}</p>}
        {hint && <p className="text-label-md italic text-th-fg-subtle">{hint}</p>}
      </div>
      <div className="flex shrink-0 items-center">{control}</div>
    </div>
  );
}

/**
 * Interruptor que SÍ guarda, en este navegador.
 * El archivo maestro §8.9 pide dejar explícito si un cambio se guarda solo o
 * con botón: aquí es automático, y la fila lo dice.
 */
export function SwitchRow({ label, description, checked, onChange }) {
  return (
    <Row
      label={label}
      description={description}
      hint="Se guarda en este navegador"
      control={
        <button
          type="button"
          role="switch"
          aria-checked={checked}
          aria-label={label}
          onClick={() => onChange(!checked)}
          className={`relative inline-flex h-7 w-12 shrink-0 items-center rounded-th-pill transition-colors th-focus-ring ${
            checked ? "bg-th-brand" : "bg-th-surface-raised"
          }`}
        >
          <span
            className={`inline-block h-5 w-5 rounded-th-pill bg-white shadow-th-card transition-transform ${
              checked ? "translate-x-6" : "translate-x-1"
            }`}
          />
        </button>
      }
    />
  );
}

/** Selector de opción única que guarda en este navegador. */
export function ChoiceRow({ label, description, value, options, onChange, id }) {
  return (
    <Row
      label={label}
      description={description}
      hint="Se guarda en este navegador"
      control={
        <>
          <label htmlFor={id} className="sr-only">
            {label}
          </label>
          <select
            id={id}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            className="min-h-[44px] rounded-th-input border border-th-border bg-th-surface px-3 py-2 text-body-sm font-semibold text-th-fg th-focus-ring"
          >
            {options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </>
      }
    />
  );
}

/**
 * Fila cuyo control existe en la referencia pero NO tiene soporte real.
 * Se muestra deshabilitada y explicada, nunca simulada (archivo maestro §7.1,
 * §9.4 y §10).
 */
export function PendingRow({ label, description, action = "No disponible", reason }) {
  const hintId = `pending-${label.replace(/\W+/g, "-").toLowerCase()}`;
  return (
    <Row
      label={label}
      description={description}
      badge={
        <span className="rounded-th-pill border border-th-border bg-th-surface-subtle px-2 py-0.5 text-label-sm font-bold uppercase tracking-wide text-th-fg-subtle">
          Sin soporte
        </span>
      }
      hint={reason}
      control={
        <>
          <button
            type="button"
            disabled
            aria-describedby={hintId}
            className="min-h-[44px] cursor-not-allowed rounded-th-input border border-th-border bg-th-surface-subtle px-4 py-2 text-label-lg font-semibold text-th-fg-subtle opacity-60"
          >
            {action}
          </button>
          <span id={hintId} className="sr-only">
            {reason}
          </span>
        </>
      }
    />
  );
}

/** Fila con una acción real conectada a un endpoint. */
export function ActionRow({ label, description, action, onAction, loading, variant = "secondary" }) {
  return (
    <Row
      label={label}
      description={description}
      control={
        <button
          type="button"
          onClick={onAction}
          disabled={loading}
          className={`min-h-[44px] rounded-th-input px-4 py-2 text-label-lg font-bold transition-colors th-focus-ring disabled:opacity-60 ${
            variant === "primary"
              ? "bg-th-brand text-th-on-brand hover:bg-th-brand-hover"
              : "border border-th-border bg-th-surface text-th-fg hover:bg-th-surface-subtle"
          }`}
        >
          {loading ? "Procesando…" : action}
        </button>
      }
    />
  );
}

/** Fila de solo lectura con un dato real de la sesión. */
export function InfoRow({ label, description, value }) {
  return (
    <Row
      label={label}
      description={description}
      control={
        <span className="text-label-lg font-semibold text-th-fg-strong">{value}</span>
      }
    />
  );
}

/**
 * Aviso de alcance. Se usa en las secciones cuyas decisiones son de servidor:
 * recuerda que una preferencia guardada en el navegador no es una regla
 * aplicada (archivo maestro §8.10).
 */
export function ScopeNotice({ children, tone = "info" }) {
  const tones = {
    info: "border-th-border bg-th-surface-subtle text-th-fg-muted",
    warning: "border-th-warning-border bg-th-warning-surface text-th-warning-fg",
  };
  return (
    <div className={`flex items-start gap-3 rounded-th-card border p-4 ${tones[tone]}`}>
      <Icon name={tone === "warning" ? "warning" : "info"} size={20} className="mt-0.5 shrink-0" />
      <p className="text-body-sm">{children}</p>
    </div>
  );
}
