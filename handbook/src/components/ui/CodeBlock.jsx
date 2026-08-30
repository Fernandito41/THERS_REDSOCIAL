// CodeBlock — bloque de código con header y botón de copia (DS-001 §9.14).
//
// Módulo 7 (Responsive + Sequential Navigation).
//
// DS-001 §9.14 especificación:
//   - Fondo color-code-bg, radio 8px, padding space-4
//   - Header opcional: lenguaje/filename a la izquierda, botón Copiar a la derecha
//   - Botón Copiar: icono icon-sm, cambia a check por 2 segundos tras copiar
//
// Se usa como override del componente `pre` en el MDX (via prop `components`):
//   <Component components={{ pre: CodeBlock }} />
//
// MDX pipeline: el elemento raíz recibido por este componente es el <pre>,
// cuyo children es el elemento <code> con className="language-{lang}".
// Por tanto:
//   props.children       → el elemento <code>
//   props.children.props.className  → "language-jsx" | "language-bash" | etc.
//   props.children.props.children   → el string del código

import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

function CodeBlock({ children }) {
  const [copied, setCopied] = useState(false)

  // Extrae el string de código del elemento <code> hijo
  const rawCode = children?.props?.children
  const codeText = typeof rawCode === 'string' ? rawCode.trim() : ''

  // Extrae el lenguaje del className ("language-jsx" → "jsx")
  const className = children?.props?.className ?? ''
  const language = className.replace('language-', '').trim() || null

  const handleCopy = async () => {
    if (!codeText) return
    try {
      await navigator.clipboard.writeText(codeText)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // navigator.clipboard puede fallar sin HTTPS — silencioso en dev local
    }
  }

  return (
    // Wrapper que provee la forma visual y contiene el header + el pre
    // El border-radius solo en las esquinas externas
    <div
      className="mb-4 overflow-hidden rounded-lg"
      style={{ backgroundColor: 'var(--color-code-bg)' }}
    >
      {/* ── Header del bloque: lenguaje + botón copiar (DS-001 §9.14) ──── */}
      <div
        className="flex items-center justify-between border-b px-4 py-2"
        style={{ borderColor: 'var(--color-border)' }}
      >
        {/* Lenguaje / filename — font-mono, text-caption */}
        <span
          className="font-mono text-xs"
          style={{ color: 'var(--color-text-disabled)' }}
        >
          {language ?? 'code'}
        </span>

        {/* Botón copiar — icono icon-sm (16px), 2s feedback visual */}
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1.5 rounded px-2 py-0.5 text-xs transition-colors"
          style={{
            color: copied
              ? 'var(--color-success)'
              : 'var(--color-text-secondary)',
          }}
          aria-label={copied ? 'Código copiado' : 'Copiar código'}
          onMouseEnter={(e) => {
            if (!copied)
              e.currentTarget.style.color = 'var(--color-text-primary)'
          }}
          onMouseLeave={(e) => {
            if (!copied)
              e.currentTarget.style.color = 'var(--color-text-secondary)'
          }}
        >
          {copied ? (
            <Check size={13} strokeWidth={2} aria-hidden="true" />
          ) : (
            <Copy size={13} strokeWidth={2} aria-hidden="true" />
          )}
          <span>{copied ? 'Copiado' : 'Copiar'}</span>
        </button>
      </div>

      {/* ── Bloque de código propiamente dicho ─────────────────────────── */}
      {/* Las clases de .handbook-prose pre aplican scroll-x y font-family.
          Se sobreescribe margin y border-radius via style para que el pre
          encaje dentro del wrapper sin crear doble border-radius.           */}
      <pre
        style={{
          margin: 0,
          borderRadius: 0,
          backgroundColor: 'transparent',
          padding: '1rem',
          overflowX: 'auto',
          fontSize: '14px',
        }}
      >
        {children}
      </pre>
    </div>
  )
}

export default CodeBlock
