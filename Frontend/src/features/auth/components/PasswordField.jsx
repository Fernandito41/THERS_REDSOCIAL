import { useId, useState } from "react";
import { IoEyeOutline, IoEyeOffOutline } from "react-icons/io5";
import { useLanguage } from "@shared/i18n";

// Igual que TextField pero con toggle de mostrar/ocultar contraseña --
// reutilizado por Login, Register (contraseña + confirmar) y Reset Password
// (contraseña + confirmar), sin duplicar el estado `visible` en cada form.
export default function PasswordField({ label, error, className = "", id: idProp, ...props }) {
  const generatedId = useId();
  const id = idProp || generatedId;
  const errorId = `${id}-error`;
  const [visible, setVisible] = useState(false);
  const { t } = useLanguage();

  return (
    <div className={className}>
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={visible ? "text" : "password"}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : undefined}
          className={`w-full bg-transparent border rounded-lg px-4 py-3 pr-11 text-ink-dark placeholder-muted-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 ${
            error ? "border-ember-500" : "border-line-dark"
          }`}
          {...props}
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? t("auth.hidePassword") : t("auth.showPassword")}
          aria-pressed={visible}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-dark hover:text-ink-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 rounded-full p-1"
        >
          {visible ? <IoEyeOffOutline size={18} /> : <IoEyeOutline size={18} />}
        </button>
      </div>
      {error && (
        <p id={errorId} role="alert" className="mt-1.5 text-xs text-ember-400">
          {error}
        </p>
      )}
    </div>
  );
}
