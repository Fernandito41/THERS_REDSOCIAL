import Icon from "@shared/components/Icon";
import { mockPulseEvents } from "../data/mockData";

/**
 * PULSE — sección 2 de REF-FEED-01.
 *
 * La referencia la dibuja como una píldora clara sobre violeta suave
 * (`bg-purple-50/80`, borde `purple-200/80`, radio completo), con la etiqueta
 * PULSE, un texto de actividad y un botón de refresco (`cached`) a la derecha.
 * Se sustituye el marquesina oscura anterior por esa composición.
 *
 * HONESTIDAD: la maqueta dice «3 personas activas ahora». No hay sistema de
 * presencia ni transporte en tiempo real en este repositorio, así que NO se
 * muestra un contador de actividad en vivo (archivo maestro §10.2: presencia
 * y «en vivo» no pueden ser estados fijos del cliente). El contenido se rotula
 * como ejemplo y el punto animado no se presenta como señal de directo.
 */
export default function PulseBar() {
  const [firstEvent] = mockPulseEvents;

  return (
    <section
      aria-label="Pulse: actividad reciente en THERS"
      className="flex items-center justify-between gap-3 rounded-th-pill border border-th-brand-soft-strong bg-th-brand-soft px-4 py-2.5 shadow-th-card"
    >
      <div className="flex min-w-0 items-center gap-2">
        <span className="flex shrink-0 items-center gap-1.5">
          <span className="h-2 w-2 rounded-th-pill bg-th-brand" aria-hidden="true" />
          <span className="text-label-sm font-bold uppercase tracking-wider text-th-brand-fg">
            Pulse
          </span>
        </span>
        <p className="truncate text-body-sm text-th-fg-muted">
          {firstEvent}
          <span className="ml-2 italic text-th-fg-subtle">(ejemplo)</span>
        </p>
      </div>

      <span
        className="hidden shrink-0 items-center pl-2 text-th-fg-subtle sm:flex"
        aria-hidden="true"
      >
        <Icon name="cached" size={18} />
      </span>
    </section>
  );
}
