# CLAUDE.md — THERS_REDSOCIAL_2026

Instrucciones globales para Claude Code en este monorepo. Este archivo es un **índice + reglas operativas**, no una copia de la documentación oficial. Ante cualquier duda, el documento fuente citado tiene prioridad sobre lo escrito aquí.

> Generado a partir de `/docs` y de la estructura real del repositorio (2026-08). No incluye decisiones que no estuvieran ya documentadas — la sección 14 lista explícitamente lo que falta.

---

## 1. Identidad y objetivo del proyecto

THERS es un proyecto de un equipo autogestionado de 4 integrantes (`HB-001` §1) que construye **una red social** (nombre del repositorio raíz, confirmado como hipótesis en `REPOSITORY_STRUCTURE.md` §1). La descripción funcional completa del producto —audiencia, features centrales— **no está formalmente documentada**; el único texto descriptivo detallado vive en el `README.md` raíz, que **no es una fuente oficial** (no vive en `/docs`) y contiene datos que contradicen la documentación oficial (ver §14).

Stack confirmado por `HB-001` (portada): **React · Vite · Tailwind CSS · Flask · PostgreSQL · JWT**.

El repositorio aloja tres aplicaciones independientes bajo un mismo monorepo, más un THERS Engineering Handbook como plataforma de documentación técnica interna ya diseñada e implementada.

---

## 2. Estructura del monorepo

Fuente: `docs/architecture/REPOSITORY_STRUCTURE.md`.

| Carpeta | Contenido | Estado de confirmación |
|---|---|---|
| `backend/` | API Flask. Estructura real observada: `app/domain/`, `app/application/`, `app/interfaces/routes/`, `app/config.py`, `app/extensions.py`, `run.py` (capas tipo Clean/Hexagonal) | Estructura vista en el código, **no ratificada** en ningún documento oficial (`REPOSITORY_STRUCTURE.md` §6 la marca como "propuesta a confirmar") |
| `Frontend/` | Producto — la red social. `src/app/{providers,router,store}`, `src/features/{auth,legal}/{components,hooks,pages,index.js}`, `src/shared/{components,lib}` | Confirmada — árbol completo verificado contra el repositorio real |
| `handbook/` | THERS Engineering Handbook. React + Vite + MDX, SSG, sin dependencia del backend | Confirmada — implementación completa (Módulos 1–10) |
| `docs/` | Documentación oficial versionada en Markdown (+ 2 documentos en `.docx`/`.pdf` sin analizar, ver §14) | Confirmada |

Reglas de organización (`REPOSITORY_STRUCTURE.md` §2, §8–9):
- `backend/`, `Frontend/` y `handbook/` son aplicaciones independientes: sin código compartido, sin `node_modules` compartidos, cada una con su propio `package.json`.
- `docs/` y `handbook/` nunca contienen código de producto; `backend/` y `Frontend/` nunca contienen documentos oficiales fuente.
- Nombres de carpeta en minúsculas salvo `Frontend/` (excepción ya documentada, no se corrige).
- Código, nombres de carpeta/archivo en inglés; documentación oficial en español.

---

## 3. Jerarquía de fuentes de verdad

1. **`/docs` oficial** — máxima autoridad. Dentro de `/docs`, para decisiones del **Handbook**: `ARC-001` (arquitectura de información/UX) → `DS-001` (Design System) → `WF-001` (wireframes) → `PV-001` (prototipo visual, subordinado y consolidador de 1–4) → `FAS-001` (traducción técnica a React, subordinada a todo lo anterior — así lo declara su propia "Nota previa"). Para organización/proceso: `HB-001`.
2. **Estructura real observada en el código** — cuando no hay documento ratificado (p. ej. capas del backend), la estructura ya implementada es la referencia de facto, pero se trata como "observada", no como "decidida".
3. **`REPOSITORY_STRUCTURE.md`** — mapa del repositorio; él mismo se declara "borrador, parcialmente verificado" y dependiente de 1.
4. **`README.md` raíz y otros archivos fuera de `/docs`** — informativos, **no autoritativos**. Ante conflicto con `/docs`, gana `/docs` siempre (ver contradicción documentada en §14).

Ningún cambio de arquitectura o diseño se decide de forma aislada dentro de una implementación puntual — sigue el proceso de gobernanza de `DS-001` §16 (Handbook) o el de decisiones de alto impacto de `HB-001` §11 (resto del proyecto).

---

## 4. Reglas de arquitectura por área

### Backend
- Documentación oficial de arquitectura backend: **no existe**. `HB-001` §0 lo dice explícitamente: "no define arquitectura técnica profunda... esos temas se documentarán en manuales técnicos separados" (aún no escritos).
- Estructura observada (no ratificada): capas `domain/`, `application/`, `interfaces/routes/`, `config/`, `extensions/`, `run.py` — mantenerla por consistencia con lo ya escrito, sin tratarla como contrato cerrado.
- Stack confirmado: Flask + JWT (`flask_jwt_extended`) + PostgreSQL (nombre de la tecnología, sin driver instalado aún en el código ni documento de esquema).
- No hay `requirements.txt` ni `pyproject.toml` en `backend/` — instalar dependencias Python requiere confirmarlas con el equipo antes de asumir versiones.

### Frontend (producto — `Frontend/`)
- Sin documento de arquitectura propio. Usar como referencia la estructura confirmada de `REPOSITORY_STRUCTURE.md` §3/§5: organización por `features/` (`auth`, `legal`), cada una con `components/`, `hooks/`, `pages/`, `index.js` como punto de entrada; `shared/` para código transversal.
- **No existe un Design System ratificado para este Frontend.** `DS-001` es exclusivamente del Handbook — no se debe extrapolar sin verificar primero si el equipo lo aprobó también aquí.
- Stack confirmado (`Frontend/package.json`): React 19, React Router 7, Tailwind **v3** (no v4 — distinto del handbook), Axios, react-icons.

### Base de Datos
- Solo confirmado: PostgreSQL como motor elegido (`HB-001` portada). Normalización, índices, estrategia de migraciones, backups y seguridad de datos: **no documentados en ningún archivo de `/docs`**. No inventar convenciones — preguntar o proponer como ADR (`HB-001` §12) antes de decidir.

### DevOps
- **Sin documentación oficial.** Docker, CI/CD, deploy, SSL, dominios y monitoreo están fuera del alcance declarado de `HB-001` (§0) y no aparecen en ningún otro documento de `/docs`. Cualquier trabajo en esta área debe tratarse como territorio no especificado (§14) y consultarse con el equipo antes de tomar decisiones estructurales.

### Handbook (`handbook/`)
- Es la única aplicación con arquitectura completamente documentada y ya implementada (Módulos 1–10, estado Release Candidate).
- Fuente de verdad en cascada: `ARC-001` (estructura/IA) → `DS-001` (tokens y catálogo visual) → `WF-001`/`PV-001` (navegación, estados, componentes) → `FAS-001` (cómo se traduce a React/Vite).
- Catálogo de componentes cerrado (`PV-001` Parte 7 §21): antes de crear un componente nuevo, verificar si el catálogo ya lo cubre. 25 extensiones al catálogo siguen **pendientes de ratificación formal** (`PV-001`, Anexo Fase 7) — no implementarlas dándolas por aprobadas.

---

## 5. Reglas de desarrollo

- No inventar arquitectura donde no la hay: si `/docs` no cubre el caso, decirlo explícitamente (§13–14), no improvisar una decisión de alto impacto.
- No duplicar componentes ni lógica — revisar primero si ya existe (regla explícita en `PV-001` §7/§21 para el Handbook; principio general de "Reutilización" y "Bajo acoplamiento" en `FAS-001` §2 para cualquier Frontend del proyecto).
- Reutilizar código existente antes de escribir uno nuevo equivalente.
- Respetar el Design System **donde exista** (Handbook: `DS-001`, vinculante — "ningún valor de color/tipografía/espaciado fuera de sus tokens"). Para `Frontend/` del producto, no hay tokens oficiales que respetar todavía; no inventarlos, señalarlo.
- Respetar la documentación oficial por encima de la preferencia individual del implementador (`FAS-001` §1: "el código sigue a la documentación, no al revés").
- No modificar decisiones arquitectónicas ya tomadas sin justificación registrada — decisiones de impacto medio/alto se documentan como ADR (`HB-001` §11–12) antes de implementarse, no después.

---

## 6. Git Flow

Fuente: `HB-001` §7–9. Reglas vinculantes:

- **`main`** — producción/entregable estable. Sin push directo.
- **`develop`** — rama de integración. Sin push directo.
- Ambas exigen Pull Request + al menos 1 aprobación.
- **Ramas:** `feature/<nombre>`, `fix/<nombre>`, `chore/<nombre>`, `docs/<nombre>`, `hotfix/<nombre>`.
- **Commits (Conventional Commits):** `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`.
- **Pull Requests:** un PR resuelve una sola cosa; título con el mismo prefijo que los commits; vinculado a su Issue (`Closes #N`); el autor no se autoaprueba; sin `.env`/credenciales; sin código de prueba olvidado (`console.log`, `print`).
- **Release:** `develop` → `main` periódicamente vía PR de release.

---

## 7. Reglas específicas para Claude Code

1. Revisar la documentación relevante (§3) antes de implementar cualquier cambio no trivial.
2. Identificar el alcance exacto de lo solicitado antes de tocar código — no expandirlo por iniciativa propia.
3. No modificar áreas fuera del alcance pedido, salvo pequeñas inconsistencias que el usuario autorice explícitamente a corregir.
4. Ejecutar las verificaciones correspondientes tras cualquier cambio (build/lint del paquete afectado como mínimo; ver §10).
5. Reportar siempre: archivos creados, archivos modificados, componentes nuevos, verificaciones ejecutadas y su resultado.
6. No hacer commit ni push salvo que el usuario lo pida explícitamente en ese turno — una autorización previa no cubre turnos futuros.
7. El código generado por IA sigue el mismo proceso de PR/revisión humana que cualquier otro (`HB-001` §19) — nunca es el único revisor de sí mismo.
8. Nunca pegar ni loguear secretos reales (JWT secret, credenciales, datos de usuarios) — `HB-001` §19.1.

---

## 8. Reglas de trabajo por área

| Área | Reglas |
|---|---|
| **Frontend (producto)** | React 19 + Vite + Tailwind v3. Sin Design System propio ratificado — no asumir tokens de `DS-001` (es del Handbook). Seguir la organización por `features/` ya existente. |
| **Backend** | Python + Flask + API REST + JWT. Estructura de capas observada en el código (no documento ratificado) — mantenerla por consistencia, no como contrato cerrado. Seguridad: sin documento oficial; aplicar buenas prácticas estándar (validación de entrada, sin secretos hardcodeados) y señalar huecos, no llenarlos por inferencia silenciosa. |
| **Database** | PostgreSQL. Normalización, índices, migraciones, backups: no documentados — no inventar esquema ni convención sin confirmarlo. |
| **DevOps** | Sin documentación oficial (Docker, CI/CD, deploy, SSL, dominios, monitoreo). Tratar cualquier tarea de esta área como territorio no especificado. |
| **Handbook** | Tratarlo como referencia oficial ya cerrada (Release Candidate, Módulo 10). Toda decisión visual/estructural pasa por `ARC-001`/`DS-001`/`WF-001`/`PV-001`/`FAS-001` en ese orden de precedencia. |

---

## 9. Convenciones

- **Nombres:** componentes React en PascalCase, hooks en camelCase con prefijo `use`, archivos de configuración en kebab-case (`REPOSITORY_STRUCTURE.md` §8, confirmado en `Frontend/` y `handbook/`).
- **Estructura de archivos:** organización por dominio funcional (`features/<dominio>/{components,hooks,pages}` + `index.js`), no por tipo de archivo.
- **Imports:** el Handbook usa el alias `@ui` → `handbook/src/components/ui` (`vite.config.js`). El Frontend del producto no tiene alias de imports documentado — usar rutas relativas como ya hace el código existente.
- **Componentes:** en el Handbook, todo componente interactivo implementa el set completo de estados (`default/hover/focus-visible/disabled` según aplique — `PV-001` Parte 6 §8). En el Frontend del producto no hay un catálogo equivalente documentado.
- **APIs:** sin especificación formal (OpenAPI/Swagger) en `/docs`. El backend actual solo expone `auth` (`/login`) — documentar cada endpoint nuevo el mismo día del PR (`HB-001` §15.1), no retroactivamente.
- **Variables de entorno:** nunca se sube `.env` ni credenciales al repositorio (`HB-001` §20, regla innegociable). No hay lista oficial de variables requeridas — confirmarlas con el equipo, no inventarlas.
- **Testing:** no hay framework de testing configurado en ningún `package.json` del repo, ni estrategia documentada en `/docs`. No asumir Jest/Vitest/pytest sin confirmarlo primero.

---

## 10. Comandos importantes

```bash
# Handbook (handbook/)
npm run dev            # servidor de desarrollo
npm run build           # build de producción (vite build)
npm run lint             # oxlint
npm run format            # prettier --write
npm run format:check       # prettier --check
npm run preview              # sirve el build de producción

# Frontend — producto (Frontend/)
npm run dev             # servidor de desarrollo
npm run build             # build de producción
npm run preview             # sirve el build de producción
# Nota: no hay script "lint" en Frontend/package.json pese a tener @eslint/js
# como devDependency — no está cableado todavía.

# Backend (backend/)
# Sin requirements.txt/pyproject.toml en el repo — no hay comando de instalación
# de dependencias documentado. Punto de entrada observado: run.py.
```

---

## 11. Protocolo antes de implementar

**ANALIZAR → CONSULTAR DOCS → PLANIFICAR → IMPLEMENTAR → VERIFICAR → REPORTAR**

1. **Analizar** la solicitud y el código relevante ya existente (sin re-explorar todo el repo si el contexto ya lo cubre).
2. **Consultar** el documento oficial correspondiente según la jerarquía de la §3 antes de asumir cualquier decisión.
3. **Planificar** el cambio dentro del alcance exacto solicitado.
4. **Implementar** reutilizando componentes/código existente, sin duplicar.
5. **Verificar** con build/lint del paquete afectado (§10) y, si aplica, navegación/responsive/dark mode/accesibilidad.
6. **Reportar** archivos tocados y verificaciones realizadas — sin commit/push salvo pedido explícito.

---

## 12. Protocolo de seguridad

Nunca ejecutar comandos destructivos (`rm -rf`, `git reset --hard`, `git push --force`, eliminar directorios o archivos importantes) ni sobrescribir trabajo no confirmado sin aprobación explícita del usuario en ese turno. Ante duda sobre si una acción es reversible, preferir la alternativa no destructiva (mover/renombrar en vez de borrar) y preguntar.

---

## 13. Regla de alcance

Si una solicitud contradice la documentación oficial (`/docs`), **detenerse antes de implementar** y señalar la contradicción explícitamente al usuario, citando el documento y la sección. No resolver el conflicto por criterio propio ni priorizar silenciosamente una fuente sobre otra.

---

## 14. Regla de incertidumbre — qué falta documentar

Si `/docs` no tiene información suficiente, **no inventar la decisión**: señalar el hueco. Huecos ya identificados en esta revisión:

- **DevOps completo** (Docker, CI/CD, deploy, SSL, dominios, monitoreo) — `HB-001` §0 confirma que no está escrito aún.
- **Arquitectura de backend** — sin documento ratificado; solo estructura observada en el código.
- **Base de datos** — sin esquema, normalización, índices, migraciones ni política de backups documentados.
- **Design System del Frontend del producto** — no existe; `DS-001` es exclusivo del Handbook.
- **Especificación de API** (endpoints, contratos, errores) — no existe documento formal.
- **Variables de entorno requeridas** — solo la regla de no subir `.env`, sin lista oficial.
- **Estrategia de testing** — no hay framework configurado ni documento de estrategia.
- **Dos documentos oficiales sin analizar:** `Manual_Operativo/THERS_Manual_Operativo_v1.0.docx` (+ `.pdf`) y `Plan_Estrategico/Plan_Estrategico_IA_THERS.docx` (+ `.pdf`) — el entorno actual no pudo procesar `.docx` ni renderizar el `.pdf` (falta `poppler-utils`). Requieren revisión manual o una herramienta capaz de leerlos antes de asumir que no contienen reglas relevantes.
- **Contradicción detectada, no resuelta:** el `README.md` raíz describe MySQL como base de datos y una estructura `frontend/`/`backend/` distinta a la real (rutas y modelos con otros nombres) — contradice a `HB-001` (PostgreSQL) y a la estructura real verificada del repositorio. Por la jerarquía de la §3, `/docs` y el código real ganan; el `README.md` debería actualizarse, pero eso no se hizo en esta tarea (no se modifica documentación adicional sin pedido explícito).
