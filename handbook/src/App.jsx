// Punto de entrada de la aplicación — Módulo 3 (Navigation System).
//
// App.jsx delega toda la responsabilidad de routing y layout al componente
// Router (routes/index.jsx), que resuelve qué layout y qué página
// corresponden a cada URL (FAS-001 §4 — separación de responsabilidades:
// App.jsx no conoce rutas ni layouts específicos).

import Router from './routes/index'

function App() {
  return <Router />
}

export default App
