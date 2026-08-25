import { createContext, useCallback, useContext, useRef, useState } from "react";
import Toast from "./Toast";

const ToastContext = createContext(null);

const DEFAULT_DURATION = { success: 4000, info: 4000, warning: 6000, error: 6000 };

// Sistema global de feedback (Fase 2) -- reemplaza a window.alert() en toda
// la app. Se monta una única vez (ver main.jsx) y cualquier feature accede
// vía el hook `useToast()` sin volver a implementar su propio mecanismo de
// notificación (Home, Perfil, Posts, etc. reutilizan este mismo componente).
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const show = useCallback(({ type = "info", title, message, duration }) => {
    const id = ++idRef.current;
    const finalDuration = duration ?? DEFAULT_DURATION[type] ?? 5000;
    setToasts((prev) => [...prev, { id, type, title, message, duration: finalDuration }]);
    return id;
  }, []);

  const toast = {
    show,
    success: (message, opts = {}) => show({ type: "success", message, ...opts }),
    error: (message, opts = {}) => show({ type: "error", message, ...opts }),
    warning: (message, opts = {}) => show({ type: "warning", message, ...opts }),
    info: (message, opts = {}) => show({ type: "info", message, ...opts }),
    dismiss,
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}

      {/* Viewport fijo, responsive: apilado abajo-centro en mobile, esquina
          inferior derecha en desktop. pointer-events-none en el contenedor
          para no bloquear clics debajo; cada Toast reactiva pointer-events. */}
      <div className="fixed inset-x-0 bottom-0 z-[100] flex flex-col items-center gap-2 p-4 sm:items-end sm:bottom-4 sm:right-4 sm:inset-x-auto sm:left-auto pointer-events-none">
        {toasts.map((t) => (
          <Toast key={t.id} {...t} onClose={() => dismiss(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast debe usarse dentro de <ToastProvider>");
  }
  return ctx;
}
