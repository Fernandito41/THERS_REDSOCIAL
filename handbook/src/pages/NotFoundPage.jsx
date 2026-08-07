// NotFoundPage — página 404.
//
// Módulo 6 (Search + Scroll-spy): complemento arquitectónico.
//
// Se muestra cuando ninguna ruta del router coincide con la URL solicitada
// (catch-all '*' en routes/index.jsx). Usa el HomeLayout (Sidebar colapsado)
// para mantener el chrome del App Shell — el usuario puede navegar sin recargar.
//
// La URL errónea no se muestra para no generar confusión; el texto guía al
// usuario a las acciones disponibles (volver al inicio o usar la búsqueda).

import { Link } from 'react-router-dom'

function NotFoundPage() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-center">
        {/* Código de error — tipografía display, color-primary muy bajo contraste
            (primary-8 = primary al 8%) para un efecto sutil de fondo */}
        <p
          className="select-none font-mono text-8xl font-bold leading-none"
          style={{ color: 'var(--color-primary-8)' }}
          aria-hidden="true"
        >
          404
        </p>

        <h1
          className="mt-4 text-2xl font-bold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Página no encontrada
        </h1>

        <p
          className="mt-2 text-base"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          La URL solicitada no existe en el Handbook.
        </p>

        <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors"
            style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor =
                'var(--color-primary-hover)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-primary)'
            }}
          >
            Volver al inicio
          </Link>

          {/* Botón secundario que abre el buscador via Ctrl+K
              — atajos de teclado ya están registrados en Header */}
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md border px-4 py-2 text-sm font-medium transition-colors"
            style={{
              borderColor: 'var(--color-border)',
              color: 'var(--color-text-primary)',
              backgroundColor: 'transparent',
            }}
            onClick={() => {
              // Dispara el mismo evento que el listener Ctrl+K del Header
              document.dispatchEvent(
                new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true }),
              )
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-border-strong)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-border)'
            }}
          >
            Buscar en el Handbook
            <span
              className="ml-2 font-mono text-xs"
              style={{ color: 'var(--color-text-disabled)' }}
            >
              Ctrl+K
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage
