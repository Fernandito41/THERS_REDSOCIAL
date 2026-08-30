// Timeline — DS-001 §9.8.
//
// Módulo 9 (Content Components: Cards + Tablas + Timeline).
//
// Uso: Roadmap, historial de decisiones (ADR), Changelog (DS-001 §9.8).
// Línea vertical 2px en color-border, con nodos circulares de 12px:
//   completado → color-primary
//   pendiente  → color-border-strong
//   progreso   → color-warning
// Cada entrada: fecha en text-caption, título en text-h4, descripción en
// text-body-sm.
//
// Orientación exclusivamente vertical en todo el sistema (PV-001 Fase 6 §1
// — se descartó una variante horizontal para no duplicar el patrón).
//
// Uso en MDX:
//   import Timeline from '@ui/Timeline'
//   <Timeline>
//     <Timeline.Item status="completado" date="M1" title="...">...</Timeline.Item>
//   </Timeline>

const STATUS_COLOR = {
  completado: 'var(--color-primary)',
  progreso: 'var(--color-warning)',
  pendiente: 'var(--color-border-strong)',
}

function TimelineItem({ status = 'pendiente', date, title, children }) {
  const color = STATUS_COLOR[status] ?? STATUS_COLOR.pendiente

  return (
    <li className="relative pb-6 pl-6 last:pb-0">
      <span
        aria-hidden="true"
        className="absolute top-1 rounded-full"
        style={{
          left: '-7px',
          width: '12px',
          height: '12px',
          backgroundColor: color,
          border: '2px solid var(--color-bg)',
        }}
      />
      {date && (
        <p
          className="font-mono text-xs"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {date}
        </p>
      )}
      <p
        className="mt-0.5 text-base font-semibold"
        style={{ color: 'var(--color-text-primary)' }}
      >
        {title}
      </p>
      {children && (
        <div
          className="mt-1 text-sm leading-relaxed"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {children}
        </div>
      )}
    </li>
  )
}

function Timeline({ children }) {
  return (
    <ol
      className="mb-4 list-none"
      style={{ borderLeft: '2px solid var(--color-border)', marginLeft: '5px' }}
    >
      {children}
    </ol>
  )
}

Timeline.Item = TimelineItem

export default Timeline
