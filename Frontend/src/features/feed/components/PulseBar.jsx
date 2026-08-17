import { mockPulseEvents } from "../data/mockData";

// Elemento visual exclusivo de THERS: un pulso continuo de actividad de la red,
// distinto a cualquier feed/timeline -- una cinta viva, no una lista.
export default function PulseBar() {
  const items = [...mockPulseEvents, ...mockPulseEvents];

  return (
    <div
      className="relative overflow-hidden rounded-full bg-[#14141A] dark:bg-[#1C1C28] text-white border border-white/5 py-2.5 px-4"
      role="marquee"
      aria-label="Actividad reciente en THERS"
    >
      <div className="flex items-center gap-2 shrink-0 absolute left-4 top-1/2 -translate-y-1/2 z-10 bg-[#14141A] dark:bg-[#1C1C28] pr-3">
        <span className="w-2 h-2 rounded-full bg-pulse-500 animate-mood-glow" aria-hidden="true" />
        <span className="text-[11px] font-bold uppercase tracking-wider text-pulse-400">Pulse</span>
      </div>

      <div className="flex whitespace-nowrap animate-marquee pl-24">
        {items.map((event, index) => (
          <span key={index} className="text-sm text-white/80 mx-6">
            {event}
          </span>
        ))}
      </div>
    </div>
  );
}
