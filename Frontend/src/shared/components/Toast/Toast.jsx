import { useEffect, useRef } from "react";
import {
  IoCheckmarkCircle,
  IoAlertCircle,
  IoWarning,
  IoInformationCircle,
  IoClose,
} from "react-icons/io5";

const DEFAULT_TITLES = {
  success: "Éxito",
  error: "Error",
  warning: "Atención",
  info: "Información",
};

const STYLES = {
  success: { icon: IoCheckmarkCircle, iconColor: "text-success-500", border: "border-success-600/40" },
  error: { icon: IoAlertCircle, iconColor: "text-ember-500", border: "border-ember-600/40" },
  warning: { icon: IoWarning, iconColor: "text-warning-500", border: "border-warning-600/40" },
  info: { icon: IoInformationCircle, iconColor: "text-pulse-400", border: "border-pulse-600/40" },
};

// role="alert" (=> aria-live assertive implícito) para error/warning, ya que
// requieren atención inmediata; role="status" (=> aria-live polite) para
// success/info, que no deben interrumpir a quien usa lector de pantalla.
export default function Toast({ type = "info", title, message, duration = 5000, onClose }) {
  const timerRef = useRef(null);

  useEffect(() => {
    if (!duration) return undefined;
    timerRef.current = setTimeout(onClose, duration);
    return () => clearTimeout(timerRef.current);
  }, [duration, onClose]);

  const pauseTimer = () => clearTimeout(timerRef.current);
  const resumeTimer = () => {
    if (duration) timerRef.current = setTimeout(onClose, duration);
  };

  const { icon: Icon, iconColor, border } = STYLES[type] || STYLES.info;
  const resolvedTitle = title || DEFAULT_TITLES[type];
  const isUrgent = type === "error" || type === "warning";

  return (
    <div
      role={isUrgent ? "alert" : "status"}
      className={`pointer-events-auto w-full max-w-sm bg-surface-dark border ${border} rounded-xl shadow-xl p-4 flex gap-3 items-start animate-float-in`}
      onMouseEnter={pauseTimer}
      onMouseLeave={resumeTimer}
      onFocus={pauseTimer}
      onBlur={resumeTimer}
    >
      <Icon size={20} className={`shrink-0 mt-0.5 ${iconColor}`} aria-hidden="true" />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-ink-dark">{resolvedTitle}</p>
        <p className="text-sm text-muted-dark mt-0.5 break-words">{message}</p>
      </div>

      <button
        type="button"
        onClick={onClose}
        aria-label="Cerrar notificación"
        className="shrink-0 text-muted-dark hover:text-ink-dark hover:bg-line-dark rounded-full p-1 focus:outline-none focus:ring-2 focus:ring-pulse-500"
      >
        <IoClose size={16} />
      </button>
    </div>
  );
}
