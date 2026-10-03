import { formatRelativeTime } from "@features/feed/lib/formatRelativeTime";
import { ACTIONS, TARGET_LABELS, reasonLabel } from "../lib/reportLabels";

function Badge({ children, tone = "neutral" }) {
  const tones = {
    neutral: "bg-canvas dark:bg-canvas-dark text-muted dark:text-muted-dark border-line dark:border-line-dark",
    critical: "bg-ember-50 dark:bg-ember-500/10 text-ember-700 dark:text-ember-300 border-ember-300 dark:border-ember-500/40",
    info: "bg-pulse-50 dark:bg-pulse-900/20 text-pulse-700 dark:text-pulse-200 border-pulse-100 dark:border-pulse-800/40",
  };
  return (
    <span className={`inline-flex items-center text-[11px] font-semibold px-2 py-0.5 rounded-full border ${tones[tone]}`}>
      {children}
    </span>
  );
}

// Un reporte de la cola. No muestra quién reportó: la API tampoco lo entrega (ADR-032 §2).
export default function ReportCard({ report, currentUserId, onAction }) {
  const open = report.status === "open" || report.status === "reviewing";
  const reported = report.reported_user;
  const isAboutMe = reported && reported.id === currentUserId;

  // Mismas reglas que el servidor; el servidor las vuelve a comprobar siempre.
  const available = {
    dismiss: !isAboutMe,
    remove_content: !isAboutMe && report.target_type !== "user",
    suspend_user: !isAboutMe && !!reported && !reported.is_moderator,
  };

  const hint = isAboutMe
    ? "Este reporte es sobre tu propia cuenta: lo debe resolver otra persona del equipo."
    : null;

  return (
    <article
      className={`bg-surface dark:bg-surface-dark border rounded-[24px] shadow-soft p-5 space-y-3 ${
        report.priority === "critical"
          ? "border-ember-300 dark:border-ember-500/50"
          : "border-line dark:border-line-dark"
      }`}
    >
      <header className="flex flex-wrap items-center gap-2">
        {report.priority === "critical" && <Badge tone="critical">Prioridad crítica</Badge>}
        <Badge tone="info">{reasonLabel(report.reason)}</Badge>
        <Badge>{TARGET_LABELS[report.target_type] || report.target_type}</Badge>
        {report.reports_on_target > 1 && <Badge>{report.reports_on_target} reportes sobre esto</Badge>}
        <span className="ml-auto text-xs text-muted dark:text-muted-dark">
          {formatRelativeTime(report.created_at)}
        </span>
      </header>

      {reported ? (
        <p className="text-sm text-ink dark:text-ink-dark">
          <span className="text-muted dark:text-muted-dark">Cuenta reportada: </span>
          <span className="font-semibold">@{reported.username}</span>
          {reported.suspended && <span className="ml-2"><Badge tone="critical">Suspendida</Badge></span>}
          {reported.is_moderator && <span className="ml-2"><Badge>Moderación</Badge></span>}
        </p>
      ) : (
        <p className="text-sm text-muted dark:text-muted-dark">La cuenta reportada ya no existe.</p>
      )}

      {report.details && (
        <p className="text-sm text-ink dark:text-ink-dark">
          <span className="text-muted dark:text-muted-dark">Detalle de quien reportó: </span>
          {report.details}
        </p>
      )}

      {report.target_type !== "user" && (
        <blockquote className="border-l-4 border-line dark:border-line-dark pl-3 text-sm text-ink dark:text-ink-dark whitespace-pre-wrap break-words">
          {report.content_snapshot ? (
            report.content_snapshot
          ) : (
            <span className="text-muted dark:text-muted-dark">
              {open ? "El texto no está disponible." : "La copia del texto se borra al resolver el reporte."}
            </span>
          )}
        </blockquote>
      )}

      {open ? (
        <div className="pt-1 space-y-2">
          <div className="flex flex-wrap gap-2">
            {Object.entries(ACTIONS).map(([action, config]) => (
              <button
                key={action}
                type="button"
                disabled={!available[action]}
                onClick={() => onAction(report, action)}
                className={`text-sm font-semibold px-4 py-2 rounded-full transition disabled:opacity-40 disabled:cursor-not-allowed ${
                  config.destructive
                    ? "bg-ember-600 hover:bg-ember-700 text-white"
                    : "border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark"
                }`}
              >
                {config.confirmLabel}
              </button>
            ))}
          </div>
          {hint && <p className="text-xs text-muted dark:text-muted-dark">{hint}</p>}
          {!hint && report.target_type === "user" && (
            <p className="text-xs text-muted dark:text-muted-dark">
              Un reporte sobre una cuenta no tiene contenido que retirar.
            </p>
          )}
          {!hint && reported?.is_moderator && (
            <p className="text-xs text-muted dark:text-muted-dark">
              Una cuenta de moderación no se suspende desde el panel: primero se le retira el rol.
            </p>
          )}
        </div>
      ) : (
        <p className="text-xs text-muted dark:text-muted-dark">
          {report.status === "actioned" ? "Con acción" : "Descartado"}
          {report.resolved_at ? ` ${formatRelativeTime(report.resolved_at).toLowerCase()}` : ""}
          {report.resolution_note ? `. Nota: ${report.resolution_note}` : ""}
        </p>
      )}
    </article>
  );
}
