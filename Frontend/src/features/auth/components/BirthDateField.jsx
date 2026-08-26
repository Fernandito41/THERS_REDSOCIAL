import { useEffect, useId, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { IoCalendarOutline, IoChevronBack, IoChevronForward } from "react-icons/io5";
import { MONTH_NAMES, WEEKDAY_LABELS, MIN_AGE_YEARS, buildCalendarWeeks, formatDisplayDate } from "../lib/dateUtils";
import InfoTooltip from "./InfoTooltip";

const CURRENT_YEAR = new Date().getFullYear();
const MAX_YEAR = CURRENT_YEAR - MIN_AGE_YEARS;
const MIN_YEAR = CURRENT_YEAR - 100;

function parseISO(iso) {
  if (!iso) return null;
  const [year, month, day] = iso.split("-").map(Number);
  return { year, month: month - 1, day };
}

// Date picker propio (sin librería nueva) para fecha de nacimiento: trigger
// con el mismo lenguaje visual que TextField/PasswordField, popover con
// selects nativos de mes/año (accesibles por teclado sin esfuerzo extra) +
// grilla de días en una <table> semántica real, no un <div> con ARIA
// reinventado a mano.
export default function BirthDateField({ label = "Fecha de nacimiento", value, onChange, error, className = "" }) {
  const [isOpen, setIsOpen] = useState(false);
  const parsed = parseISO(value);
  const [viewYear, setViewYear] = useState(parsed?.year ?? MAX_YEAR);
  const [viewMonth, setViewMonth] = useState(parsed?.month ?? 0);

  const generatedId = useId();
  const id = generatedId;
  const errorId = `${id}-error`;
  const containerRef = useRef(null);
  const popoverRef = useRef(null);

  useEffect(() => {
    function handlePointerDown(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    function handleKeyDown(e) {
      if (e.key === "Escape") setIsOpen(false);
    }
    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  useEffect(() => {
    if (isOpen) popoverRef.current?.querySelector("select")?.focus();
  }, [isOpen]);

  const atMinBound = viewYear <= MIN_YEAR && viewMonth === 0;
  const atMaxBound = viewYear >= MAX_YEAR && viewMonth === 11;

  const goPrevMonth = () => {
    if (atMinBound) return;
    if (viewMonth === 0) {
      setViewMonth(11);
      setViewYear((y) => y - 1);
    } else {
      setViewMonth((m) => m - 1);
    }
  };

  const goNextMonth = () => {
    if (atMaxBound) return;
    if (viewMonth === 11) {
      setViewMonth(0);
      setViewYear((y) => y + 1);
    } else {
      setViewMonth((m) => m + 1);
    }
  };

  const selectDay = (day) => {
    const pad = (n) => String(n).padStart(2, "0");
    onChange(`${viewYear}-${pad(viewMonth + 1)}-${pad(day)}`);
    setIsOpen(false);
  };

  const weeks = buildCalendarWeeks(viewYear, viewMonth);
  const selectedDay = parsed && parsed.year === viewYear && parsed.month === viewMonth ? parsed.day : null;

  const yearOptions = [];
  for (let y = MAX_YEAR; y >= MIN_YEAR; y--) yearOptions.push(y);

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className="flex items-center gap-1.5 mb-1.5">
        <label htmlFor={id} className="text-xs font-medium text-muted-dark">
          {label}
        </label>
        <InfoTooltip label="Por qué pedimos tu fecha de nacimiento">
          <p>
            Usamos tu fecha de nacimiento para mostrarte una experiencia más adecuada para tu
            edad y para ayudar a que la comunidad de THERS siga siendo un lugar seguro. Esta
            fecha se guarda en la configuración de tu cuenta y no se muestra públicamente en tu
            perfil.
          </p>
          <Link to="/privacy" className="mt-1.5 inline-block text-pulse-400 hover:underline">
            Ver Política de Privacidad
          </Link>
        </InfoTooltip>
      </div>
      <button
        type="button"
        id={id}
        onClick={() => setIsOpen((v) => !v)}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-invalid={!!error}
        aria-describedby={error ? errorId : undefined}
        className={`w-full flex items-center gap-3 bg-transparent border rounded-lg px-4 py-3 text-left focus:outline-none focus:ring-2 focus:ring-pulse-500 ${
          error ? "border-ember-500" : "border-line-dark"
        }`}
      >
        <IoCalendarOutline className="text-muted-dark shrink-0" size={18} aria-hidden="true" />
        <span className={value ? "text-ink-dark" : "text-muted-dark"}>
          {value ? formatDisplayDate(value) : "Seleccionar fecha"}
        </span>
      </button>

      {error && (
        <p id={errorId} role="alert" className="mt-1.5 text-xs text-ember-400">
          {error}
        </p>
      )}

      {isOpen && (
        <div
          ref={popoverRef}
          className="absolute z-20 mt-2 w-full sm:w-80 max-w-[calc(100vw-2rem)] bg-surface-dark border border-line-dark rounded-2xl shadow-lift p-4 animate-float-in"
        >
          <div className="flex items-center justify-between gap-2 mb-3">
            <button
              type="button"
              onClick={goPrevMonth}
              disabled={atMinBound}
              aria-label="Mes anterior"
              className="p-1.5 rounded-full text-muted-dark hover:text-ink-dark hover:bg-line-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 disabled:opacity-30 disabled:pointer-events-none"
            >
              <IoChevronBack size={16} />
            </button>

            <div className="flex items-center gap-1.5">
              <label className="sr-only" htmlFor={`${id}-month`}>
                Mes
              </label>
              <select
                id={`${id}-month`}
                value={viewMonth}
                onChange={(e) => setViewMonth(Number(e.target.value))}
                className="bg-transparent text-sm font-semibold text-ink-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 rounded"
              >
                {MONTH_NAMES.map((m, i) => (
                  <option key={m} value={i} className="text-ink bg-white">
                    {m}
                  </option>
                ))}
              </select>

              <label className="sr-only" htmlFor={`${id}-year`}>
                Año
              </label>
              <select
                id={`${id}-year`}
                value={viewYear}
                onChange={(e) => setViewYear(Number(e.target.value))}
                className="bg-transparent text-sm font-semibold text-ink-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 rounded"
              >
                {yearOptions.map((y) => (
                  <option key={y} value={y} className="text-ink bg-white">
                    {y}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              onClick={goNextMonth}
              disabled={atMaxBound}
              aria-label="Mes siguiente"
              className="p-1.5 rounded-full text-muted-dark hover:text-ink-dark hover:bg-line-dark focus:outline-none focus:ring-2 focus:ring-pulse-500 disabled:opacity-30 disabled:pointer-events-none"
            >
              <IoChevronForward size={16} />
            </button>
          </div>

          <table className="w-full text-center border-collapse">
            <caption className="sr-only">
              {MONTH_NAMES[viewMonth]} {viewYear}
            </caption>
            <thead>
              <tr>
                {WEEKDAY_LABELS.map((d, i) => (
                  <th key={`${d}-${i}`} scope="col" className="text-[11px] font-medium text-muted-dark pb-2">
                    {d}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {weeks.map((week, wi) => (
                <tr key={wi}>
                  {week.map((day, di) =>
                    day ? (
                      <td key={di} className="p-0.5">
                        <button
                          type="button"
                          onClick={() => selectDay(day)}
                          aria-pressed={selectedDay === day}
                          className={`w-9 h-9 rounded-full text-sm transition focus:outline-none focus:ring-2 focus:ring-pulse-500 ${
                            selectedDay === day
                              ? "bg-pulse-600 text-white font-semibold"
                              : "text-ink-dark hover:bg-line-dark"
                          }`}
                        >
                          {day}
                        </button>
                      </td>
                    ) : (
                      <td key={di} className="p-0.5" aria-hidden="true" />
                    )
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
