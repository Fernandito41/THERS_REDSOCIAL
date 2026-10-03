import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import {
  ACTIONS,
  DEFAULT_SUSPENSION_REASON,
  MAX_TEXT_LENGTH,
  reasonLabel,
} from "../lib/reportLabels";

// Diálogo para resolver un reporte: pide la nota interna y, al suspender, el motivo que
// verá la persona. Se monta solo mientras está abierto (el padre lo renderiza con `key`),
// así que los campos arrancan vacíos cada vez.
function DialogBody({ report, action, busy, onConfirm, onCancel }) {
  const uid = useId();
  const config = ACTIONS[action];
  const firstField = useRef(null);
  const onCancelRef = useRef(onCancel);
  const [note, setNote] = useState("");
  const [reason, setReason] = useState("");

  useEffect(() => {
    onCancelRef.current = onCancel;
  });

  useEffect(() => {
    const previouslyFocused = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    firstField.current?.focus();

    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onCancelRef.current?.();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
      previouslyFocused?.focus?.();
    };
  }, []);

  const isSuspend = action === "suspend_user";

  function submit(event) {
    event.preventDefault();
    onConfirm({ note: note.trim(), reason: isSuspend ? reason.trim() : "" });
  }

  const fieldClass =
    "w-full rounded-2xl border border-line dark:border-line-dark bg-canvas dark:bg-canvas-dark text-sm text-ink dark:text-ink-dark p-3 focus:outline-none focus:ring-2 focus:ring-pulse-500";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !busy) onCancel();
      }}
    >
      <form
        role="dialog"
        aria-modal="true"
        aria-labelledby={`${uid}-title`}
        aria-describedby={`${uid}-desc`}
        onSubmit={submit}
        className="w-full max-w-md bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-6 space-y-4 max-h-[90vh] overflow-y-auto"
      >
        <div>
          <h2 id={`${uid}-title`} className="text-lg font-extrabold text-ink dark:text-ink-dark">
            {config.title}
          </h2>
          <p id={`${uid}-desc`} className="mt-1 text-sm text-muted dark:text-muted-dark">
            {config.description}
          </p>
          <p className="mt-2 text-xs text-muted dark:text-muted-dark">
            Reporte: {reasonLabel(report.reason)}
            {report.reported_user ? ` · @${report.reported_user.username}` : ""}
          </p>
        </div>

        {isSuspend && (
          <div className="space-y-1">
            <label htmlFor={`${uid}-reason`} className="text-sm font-semibold text-ink dark:text-ink-dark">
              Motivo que verá la persona
            </label>
            <textarea
              id={`${uid}-reason`}
              ref={firstField}
              rows={3}
              maxLength={MAX_TEXT_LENGTH}
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              placeholder={DEFAULT_SUSPENSION_REASON}
              className={fieldClass}
            />
            <p className="text-xs text-muted dark:text-muted-dark">
              Si lo dejas vacío se usa el texto de ejemplo. No incluyas datos de quien reportó.
            </p>
          </div>
        )}

        <div className="space-y-1">
          <label htmlFor={`${uid}-note`} className="text-sm font-semibold text-ink dark:text-ink-dark">
            Nota interna <span className="font-normal text-muted dark:text-muted-dark">(opcional)</span>
          </label>
          <textarea
            id={`${uid}-note`}
            ref={isSuspend ? undefined : firstField}
            rows={3}
            maxLength={MAX_TEXT_LENGTH}
            value={note}
            onChange={(event) => setNote(event.target.value)}
            className={fieldClass}
          />
          <p className="text-xs text-muted dark:text-muted-dark">
            La ve solo el equipo de moderación. La persona nunca la ve.
          </p>
        </div>

        <div className="flex justify-end gap-2 pt-1">
          <button
            type="button"
            disabled={busy}
            onClick={onCancel}
            className="text-sm font-semibold px-4 py-2 rounded-full border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark transition disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={busy}
            className={`text-sm font-semibold px-4 py-2 rounded-full text-white transition disabled:opacity-50 ${
              config.destructive ? "bg-ember-600 hover:bg-ember-700" : "bg-pulse-600 hover:bg-pulse-700"
            }`}
          >
            {busy ? "Guardando…" : config.confirmLabel}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function ResolveDialog({ open, report, action, busy, onConfirm, onCancel }) {
  if (!open || !report || !action) return null;
  return createPortal(
    <DialogBody
      key={`${report.id}:${action}`}
      report={report}
      action={action}
      busy={busy}
      onConfirm={onConfirm}
      onCancel={onCancel}
    />,
    document.body
  );
}
