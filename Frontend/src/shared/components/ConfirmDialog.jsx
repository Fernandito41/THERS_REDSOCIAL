import { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import Icon from "@shared/components/Icon";

// Diálogo de confirmación propio de THERS, en lugar de `window.confirm` (el
// cuadro nativo del navegador ignora el tema, el modo oscuro y la marca).
//
// Pensado para acciones que no se pueden deshacer: el botón de cancelar
// recibe el foco al abrirse (no el destructivo), así que pulsar Enter por
// reflejo nunca borra nada.
//
// Comportamiento:
//  · role="alertdialog" con título y descripción enlazados (aria-labelledby /
//    aria-describedby).
//  · Escape y clic sobre el fondo cancelan; Tab queda contenido en el panel.
//  · Bloquea el scroll de la página mientras está abierto y devuelve el foco
//    al elemento que lo tenía antes (normalmente el botón que lo abrió).
//  · Se pinta en un portal sobre <body>: ningún ancestro con `transform` o
//    `overflow` (tarjetas, hilo de mensajes) puede recortarlo ni desplazarlo.
//    Los tokens `th-` viven en `:root` / `.dark`, así que el portal conserva
//    tema y modo oscuro.
//
// Solo dibuja; el estado (`open`) y la acción real los gobierna quien lo usa.
export default function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  destructive = false,
  icon,
  onConfirm,
  onCancel,
}) {
  const uid = useId();
  const panelRef = useRef(null);
  const cancelRef = useRef(null);

  // Ref en vez de dependencia del efecto: quien lo usa suele pasar una función
  // inline, y re-ejecutar el efecto en cada render devolvería el foco al botón
  // de cancelar mientras la persona navega con Tab.
  const onCancelRef = useRef(onCancel);
  useEffect(() => {
    onCancelRef.current = onCancel;
  });

  useEffect(() => {
    if (!open) return undefined;

    const previouslyFocused = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    cancelRef.current?.focus();

    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onCancelRef.current?.();
        return;
      }
      if (event.key !== "Tab" || !panelRef.current) return;

      const focusables = panelRef.current.querySelectorAll("button:not([disabled])");
      if (!focusables.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
      previouslyFocused?.focus?.();
    };
  }, [open]);

  if (!open) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-th-modal flex items-center justify-center bg-black/55 p-4 backdrop-blur-sm"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onCancel?.();
      }}
    >
      <div
        ref={panelRef}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={`${uid}-title`}
        aria-describedby={description ? `${uid}-desc` : undefined}
        className="animate-float-in w-full max-w-sm rounded-th-dialog border border-th-border bg-th-surface p-6 shadow-th-overlay motion-reduce:animate-none"
      >
        <div className="flex items-start gap-4">
          {icon && (
            <span
              className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-th-pill ${
                destructive
                  ? "bg-th-danger-surface text-th-danger-accent"
                  : "bg-th-brand-soft text-th-brand-fg"
              }`}
            >
              <Icon name={icon} size={22} />
            </span>
          )}

          <div className="min-w-0 flex-1">
            <h2 id={`${uid}-title`} className="text-headline-sm text-th-fg-strong">
              {title}
            </h2>
            {description && (
              <p id={`${uid}-desc`} className="mt-1.5 text-body-md text-th-fg-muted">
                {description}
              </p>
            )}
          </div>
        </div>

        <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button
            ref={cancelRef}
            type="button"
            onClick={onCancel}
            className="min-h-[44px] rounded-th-pill border border-th-border bg-th-surface px-5 py-2 text-label-lg font-bold text-th-fg transition-colors th-focus-ring hover:bg-th-surface-subtle"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`min-h-[44px] rounded-th-pill px-5 py-2 text-label-lg font-bold transition-colors th-focus-ring ${
              destructive
                ? "bg-th-danger-accent text-white hover:opacity-90"
                : "bg-th-brand text-th-on-brand hover:bg-th-brand-hover"
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
