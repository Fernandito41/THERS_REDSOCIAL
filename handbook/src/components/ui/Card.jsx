// Card — DS-001 §9.5 / PV-001 §2.
//
// Módulo 9 (Content Components: Cards + Tablas + Timeline).
//
// Unifica las dos implementaciones de Card que existían duplicadas
// (CategoryCard en HomePage, DocumentCard en CategoryPage) en un único
// componente reutilizable — DS-001 §9.5 exige una sola estructura base
// para todas las variantes de tarjeta del catálogo.
//
// Fondo color-surface, borde 1px color-border, radio 8px, padding space-4.
// Hover: borde a color-border-strong + sombra sutil (mismo criterio para
// ambas variantes, PV-001 §2 "Estados").
//
// variant:
//   'category' — icono arriba (24px) → título → descripción (HomePage).
//   'document' — icono a la izquierda (18px) → fila título+badge+meta →
//                descripción (CategoryPage).
//
// featured — borde izquierdo de 2px en color-primary (PV-001 §2 "Card
// destacada"), reservado a curaduría editorial explícita. El componente
// soporta la variante; ningún documento la activa automáticamente.

import { Link } from 'react-router-dom'

function Card({
  to,
  icon: Icon,
  title,
  description,
  badge,
  meta,
  variant = 'category',
  featured = false,
}) {
  const isDocument = variant === 'document'

  return (
    <Link
      to={to}
      className={
        isDocument
          ? 'flex items-start gap-3 rounded-lg p-4 transition-shadow'
          : 'group flex flex-col gap-2 rounded-lg p-4 transition-shadow'
      }
      style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderLeft: featured
          ? '2px solid var(--color-primary)'
          : '1px solid var(--color-border)',
        textDecoration: 'none',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-border-strong)'
        if (featured) e.currentTarget.style.borderLeftColor = 'var(--color-primary)'
        e.currentTarget.style.boxShadow =
          '0 1px 4px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--color-border)'
        if (featured) e.currentTarget.style.borderLeftColor = 'var(--color-primary)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {isDocument ? (
        <>
          {Icon && (
            <Icon
              size={18}
              strokeWidth={1.5}
              aria-hidden="true"
              style={{
                color: 'var(--color-text-secondary)',
                flexShrink: 0,
                marginTop: 3,
              }}
            />
          )}
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className="text-sm font-semibold"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {title}
              </span>
              {badge}
              {meta && (
                <span
                  className="font-mono text-xs"
                  style={{ color: 'var(--color-text-disabled)' }}
                >
                  {meta}
                </span>
              )}
            </div>
            {description && (
              <p
                className="mt-1 text-xs leading-relaxed"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                {description}
              </p>
            )}
          </div>
        </>
      ) : (
        <>
          {Icon && (
            <Icon
              size={24}
              strokeWidth={2}
              aria-hidden="true"
              style={{ color: 'var(--color-text-secondary)' }}
            />
          )}
          <span
            className="text-base font-semibold"
            style={{ color: 'var(--color-text-primary)' }}
          >
            {title}
          </span>
          {description && (
            <span
              className="text-sm leading-snug"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              {description}
            </span>
          )}
        </>
      )}
    </Link>
  )
}

export default Card
