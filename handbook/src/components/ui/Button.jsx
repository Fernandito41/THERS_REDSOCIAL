// Button — DS-001 §9.6.
//
// Variantes:
//   primary   → fondo color-primary, texto blanco
//   secondary → transparente, texto y borde color-primary
//   ghost     → transparente, texto color-text-primary, sin borde
//   danger    → fondo color-danger, texto blanco
//
// Tamaños: sm (32px) | md (40px, default) | lg (48px)
// Padding horizontal mínimo space-4 (DS-001 §9.6).
//
// Estados: default, hover (darkens bg), focus-visible (anillo global DS-001 §12),
// disabled (opacidad 40%, cursor not-allowed — DS-001 §9.6).
//
// El componente acepta cualquier prop HTML de <button> vía ...props
// (type, onClick, aria-*, etc.) para máxima composabilidad (FAS-001 §5).

const VARIANT_STYLES = {
  primary: {
    backgroundColor: 'var(--color-primary)',
    color: '#fff',
    border: 'none',
  },
  secondary: {
    backgroundColor: 'transparent',
    color: 'var(--color-primary)',
    border: '1px solid var(--color-primary)',
  },
  ghost: {
    backgroundColor: 'transparent',
    color: 'var(--color-text-primary)',
    border: 'none',
  },
  danger: {
    backgroundColor: 'var(--color-danger)',
    color: '#fff',
    border: 'none',
  },
}

const SIZE_HEIGHT = { sm: '32px', md: '40px', lg: '48px' }
const SIZE_CLASS = { sm: 'px-3 text-xs', md: 'px-4 text-sm', lg: 'px-4 text-base' }

function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  type = 'button',
  children,
  ...props
}) {
  const variantStyle = VARIANT_STYLES[variant] ?? VARIANT_STYLES.primary

  return (
    <button
      type={type}
      disabled={disabled}
      className={`inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors ${SIZE_CLASS[size] ?? SIZE_CLASS.md}`}
      style={{
        height: SIZE_HEIGHT[size] ?? SIZE_HEIGHT.md,
        ...variantStyle,
        ...(disabled ? { opacity: 0.4, cursor: 'not-allowed' } : {}),
      }}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button
