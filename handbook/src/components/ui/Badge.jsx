// Badge — DS-001 §9.11.
//
// Variantes semánticas obligatorias:
//   estable   → color-success  (verde)
//   draft     → color-warning  (naranja/amarillo)
//   deprecado → color-danger   (rojo)
//   beta      → color-secondary (teal)
//
// Anatomía: texto text-caption (12px) peso 500, altura 20px,
// padding horizontal space-2 (8px), radio 4px (DS-001 §9.11).
// Sin icono salvo excepción documentada (DS-001 §9.11).
//
// Uso:
//   <Badge variant="estable" />      → muestra label por defecto "Estable"
//   <Badge variant="draft">WIP</Badge> → muestra children

const VARIANT_STYLES = {
  estable: { backgroundColor: 'var(--color-success)', color: '#fff' },
  draft: { backgroundColor: 'var(--color-warning)', color: '#fff' },
  deprecado: { backgroundColor: 'var(--color-danger)', color: '#fff' },
  beta: { backgroundColor: 'var(--color-secondary)', color: '#fff' },
}

const VARIANT_LABELS = {
  estable: 'Estable',
  draft: 'Draft',
  deprecado: 'Deprecado',
  beta: 'Beta',
}

function Badge({ variant = 'draft', children }) {
  const style = VARIANT_STYLES[variant] ?? VARIANT_STYLES.draft
  const label = children ?? VARIANT_LABELS[variant] ?? variant

  return (
    <span
      className="inline-flex items-center rounded px-2 text-xs font-medium"
      style={{ height: '20px', ...style }}
    >
      {label}
    </span>
  )
}

export default Badge
