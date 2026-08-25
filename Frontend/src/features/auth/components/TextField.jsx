import { useId } from "react";

// Input de texto accesible reutilizado por Login/Register/Forgot/Reset:
// label asociado por htmlFor/id (visualmente oculto para preservar el look
// original placeholder-only), error asociado vía aria-describedby, y estado
// aria-invalid para lectores de pantalla.
export default function TextField({ label, error, type = "text", className = "", id: idProp, ...props }) {
  const generatedId = useId();
  const id = idProp || generatedId;
  const errorId = `${id}-error`;

  return (
    <div className={className}>
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <input
        id={id}
        type={type}
        aria-invalid={!!error}
        aria-describedby={error ? errorId : undefined}
        className={`w-full bg-transparent border rounded-lg px-4 py-3 text-ink-dark placeholder-muted-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 ${
          error ? "border-ember-500" : "border-line-dark"
        }`}
        {...props}
      />
      {error && (
        <p id={errorId} role="alert" className="mt-1.5 text-xs text-ember-400">
          {error}
        </p>
      )}
    </div>
  );
}
