// Contenedor del área de contenido principal del App Shell (ARC-001 §1).
//
// Módulo 3 (Navigation System):
// - Acepta children (el <Outlet /> del layout activo) y los renderiza.
// - El placeholder del Módulo 2 se mantiene para cuando no hay children,
//   pero ahora usa tokens DS-001 en lugar de clases gray-* hardcodeadas
//   (DS-001 §4 — regla vinculante: ningún valor de color directo en componentes).
// - Overflow-y: auto para que el scroll sea de la columna de contenido,
//   no del viewport completo (sidebar y TOC permanecen fijos — DS-001 §9.2).

function MainContent({ children }) {
  return (
    <main className="flex-1 overflow-y-auto">
      {children ?? (
        // Placeholder — visible solo cuando no hay children (no hay ruta activa).
        // En uso normal con el router, el <Outlet /> siempre provee contenido.
        <div
          className="flex h-full items-center justify-center rounded-md border border-dashed m-8 text-sm"
          style={{
            borderColor: 'var(--color-border)',
            color: 'var(--color-text-disabled)',
          }}
        >
          Contenido del Handbook — Home, Categoría y Documento se renderizarán
          aquí
        </div>
      )}
    </main>
  )
}

export default MainContent
