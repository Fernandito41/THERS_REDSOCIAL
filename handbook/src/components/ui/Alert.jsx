// Alert — DS-001 §9.10 — banner de página.
//
// Se ubica inmediatamente debajo del H1.
// Ocupa el ancho completo de container-content.
// Variantes: info | warning | danger
// (Nota: no existe variante "success" en DS-001 §9.10 — el banner de página
// siempre comunica un estado que requiere atención del lector.)
//
// Anatomía: icono semántico + texto + borde izquierdo 3px en el color semántico
// + fondo al 8% de opacidad del mismo color.
// Distinto de Callout (§9.15), que vive dentro del cuerpo del contenido.
//
// Los tokens --color-*-8 están definidos en index.css para ambos temas.

import { Info, AlertTriangle, AlertOctagon } from 'lucide-react'

const VARIANT_CONFIG = {
  info: {
    Icon: Info,
    color: 'var(--color-info)',
    bg: 'var(--color-info-8)',
  },
  warning: {
    Icon: AlertTriangle,
    color: 'var(--color-warning)',
    bg: 'var(--color-warning-8)',
  },
  danger: {
    Icon: AlertOctagon,
    color: 'var(--color-danger)',
    bg: 'var(--color-danger-8)',
  },
}

function Alert({ variant = 'info', children }) {
  const config = VARIANT_CONFIG[variant] ?? VARIANT_CONFIG.info
  const { Icon } = config

  return (
    <div
      className="flex items-start gap-3 rounded-r-md px-4 py-3"
      role="alert"
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
      <div
        className="text-sm leading-relaxed"
        style={{ color: 'var(--color-text-primary)' }}
      >
        {children}
      </div>
    </div>
  )
}

export default Alert
