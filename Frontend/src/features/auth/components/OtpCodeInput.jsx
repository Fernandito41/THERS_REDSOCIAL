import { useRef } from "react";

// Input de código de un solo uso (OTP) -- 6 casillas visuales sobre un
// único valor controlado (string de dígitos, sin espacios), pensado para
// VerifyResetCode.jsx (ADR-010-password-reset-otp-flow.md §Fase 5 de la
// tarea). Mismo criterio de accesibilidad que TextField.jsx (aria-invalid/
// aria-describedby), pero `type="text"` + `inputMode="numeric"` en vez de
// `type="number"`: evita las flechitas de spinner del navegador y el
// problema de que `type="number"` descarta ceros a la izquierda -- un
// código "012345" es válido y debe conservarlos.
export default function OtpCodeInput({ length = 6, value, onChange, onComplete, error, disabled }) {
  const inputsRef = useRef([]);
  const digits = Array.from({ length }, (_, i) => value[i] || "");

  const focusInput = (index) => {
    inputsRef.current[index]?.focus();
  };

  const commit = (nextDigits) => {
    const joined = nextDigits.join("");
    onChange(joined);
    if (joined.length === length && !joined.includes("")) {
      onComplete?.(joined);
    }
  };

  const handleChange = (index, e) => {
    // El navegador puede entregar más de un carácter si había un dígito ya
    // escrito en la casilla y el cursor estaba al final sin selección
    // (p. ej. "5" + tipear "3" -> "53") -- se queda con el último dígito
    // tipeado, ignorando cualquier no-numérico (autocompletado con
    // guiones/espacios, etc.).
    const digit = e.target.value.replace(/\D/g, "").slice(-1);
    const next = digits.slice();
    next[index] = digit;
    commit(next);
    if (digit && index < length - 1) focusInput(index + 1);
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace") {
      e.preventDefault();
      const next = digits.slice();
      if (next[index]) {
        next[index] = "";
        commit(next);
      } else if (index > 0) {
        next[index - 1] = "";
        commit(next);
        focusInput(index - 1);
      }
    } else if (e.key === "ArrowLeft" && index > 0) {
      focusInput(index - 1);
    } else if (e.key === "ArrowRight" && index < length - 1) {
      focusInput(index + 1);
    }
    // Enter: sin manejo especial -- se deja propagar al <form> que envuelve
    // este componente (submit nativo del navegador), mismo comportamiento
    // que cualquier <input> dentro de un <form>.
  };

  const handlePaste = (e) => {
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, length);
    if (!pasted) return;
    e.preventDefault();
    const next = Array.from({ length }, (_, i) => pasted[i] || "");
    commit(next);
    focusInput(Math.min(pasted.length, length - 1));
  };

  return (
    <div>
      <div className="flex justify-center gap-2" onPaste={handlePaste}>
        {digits.map((digit, index) => (
          <input
            key={index}
            ref={(el) => (inputsRef.current[index] = el)}
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            autoComplete={index === 0 ? "one-time-code" : "off"}
            maxLength={1}
            value={digit}
            onChange={(e) => handleChange(index, e)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            disabled={disabled}
            aria-label={`Dígito ${index + 1} de ${length}`}
            aria-invalid={!!error}
            className={`w-11 h-14 sm:w-12 text-center text-2xl font-semibold bg-transparent border rounded-lg text-ink-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 disabled:opacity-50 ${
              error ? "border-ember-500" : "border-line-dark"
            }`}
          />
        ))}
      </div>
      {error && (
        <p role="alert" className="mt-2 text-xs text-ember-400 text-center">
          {error}
        </p>
      )}
    </div>
  );
}
