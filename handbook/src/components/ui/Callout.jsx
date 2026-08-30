// Callout — DS-001 §9.15.
//
// Vive dentro del flujo de contenido (≠ Alert §9.10, que es banner de página).
// Cuatro variantes obligatorias:
//   nota        → info    (color-info,    icono Info)
//   tip         → success (color-success, icono Lightbulb)
//   advertencia → warning (color-warning, icono AlertTriangle)
//   peligro     → danger  (color-danger,  icono AlertOctagon)
//
// Anatomía: icono semántico + título opcional en negrita + cuerpo text-body.
// Borde izquierdo 3px en el color semántico + fondo al 6% del mismo color.
// Los tokens --color-*-6 están definidos en index.css para ambos temas
// (DS-001 §10 — dark mode solo redefine tokens, no duplica componentes).
//
// Props:
//   variant   — 'nota' | 'tip' | 'advertencia' | 'peligro'
//   title     — string opcional; en negrita encima del cuerpo
//   children  — contenido del cuerpo (texto o JSX)

import { Info, Lightbulb, AlertTriangle, AlertOctagon } from 'lucide-react'

const VARIANT_CONFIG = {
  nota: {
    Icon: Info,
    color: 'var(--color-info)',
    bg: 'var(--color-info-6)',
  },
  tip: {
    Icon: Lightbulb,
    color: 'var(--color-success)',
    bg: 'var(--color-success-6)',
  },
  advertencia: {
    Icon: AlertTriangle,
    color: 'var(--color-warning)',
    bg: 'var(--color-warning-6)',
  },
  peligro: {
    Icon: AlertOctagon,
    color: 'var(--color-danger)',
    bg: 'var(--color-danger-6)',
  },
}

function Callout({ variant = 'nota', title, children }) {
  const config = VARIANT_CONFIG[variant] ?? VARIANT_CONFIG.nota
  const { Icon } = config

  return (
    <div
      className="flex gap-3 rounded-r-md px-4 py-3"
      style={{
        borderLeft: `3px solid ${config.color}`,
        backgroundColor: config.bg,
      }}
    >
      <Icon
        size={18}
        strokeWidth={2}
        aria-hidden="true"
        style={{ color: config.color, flexShrink: 0, marginTop: '2px' }}
      />
      <div className="min-w-0">
        {title && (
          <p
            className="mb-1 text-sm font-semibold"
            style={{ color: config.color }}
          >
            {title}
          </p>
        )}
        <div
          className="text-sm leading-relaxed"
          style={{ color: 'var(--color-text-primary)' }}
        >
          {children}
        </div>
      </div>
    </div>
  )
}

export default Callout
