<div align="center">

# THERS

**Una red social — proyecto de un equipo autogestionado de 4 integrantes.**

![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-3-38B2AC?style=flat-square&logo=tailwindcss)
![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens)

[Reportar Bug](../../issues) · [Solicitar Feature](../../issues)

</div>

---

>  **Nota sobre este README.** Este archivo es **informativo, no una fuente de verdad oficial**. La documentación autoritativa del proyecto vive en [`docs/`](docs/); ante cualquier conflicto, `docs/` tiene prioridad (ver `HB-001` y `docs/architecture/REPOSITORY_STRUCTURE.md`). Este documento se reconcilió con la documentación oficial y el código real; las secciones marcadas como *planificado* o *pendiente de documentar* señalan aquello que todavía no está implementado ni formalmente especificado.

## ¿Qué es THERS?

THERS es **una red social**, desarrollada como monorepo por un equipo de 4 integrantes con estándares de trabajo de una empresa de software real (`HB-001`).

>  **La descripción funcional completa del producto** (audiencia objetivo y catálogo definitivo de features) **aún no está formalmente documentada** en `docs/` — solo está confirmado, por el nombre del repositorio, que se trata de una red social (`docs/architecture/REPOSITORY_STRUCTURE.md` §1). La sección de [Roadmap](#roadmap) refleja *intención de producto*, no una especificación aprobada.

## Estructura del repositorio (monorepo)

Tres aplicaciones independientes + la documentación oficial, cada una como carpeta de primer nivel (`docs/architecture/REPOSITORY_STRUCTURE.md`):

```
THERS_REDSOCIAL_2026/
├── backend/        # API Flask (JWT). Capas: domain / application / interfaces
│   ├── app/
│   │   ├── domain/auth/            # reglas de negocio puras
│   │   ├── application/auth/       # casos de uso
│   │   ├── interfaces/routes/      # adaptadores HTTP (blueprints)
│   │   ├── config.py
│   │   ├── extensions.py
│   │   └── __init__.py             # create_app()
│   └── run.py                      # punto de entrada (127.0.0.1:5000)
│
├── Frontend/       # Producto — la red social (React + Vite + Tailwind)
│   └── src/
│       ├── app/                    # providers, router, store
│       ├── features/               # organización por dominio
│       │   ├── auth/               # AuthPage, Login, Register, useAuth
│       │   └── legal/              # Terms, Privacy, Cookies
│       └── shared/                 # componentes y librerías transversales
│
├── handbook/       # THERS Engineering Handbook (React + Vite + MDX, SSG)
│
└── docs/           # Documentación oficial (fuente de verdad)
```

> La organización interna del backend está **observada en el código, no ratificada** en un documento oficial de arquitectura (`docs/architecture/REPOSITORY_STRUCTURE.md` §6). La arquitectura de base de datos se documenta en `docs/architecture/DATABASE_ARCHITECTURE.md` (borrador).

## Stack tecnológico

| Capa | Tecnología | Fuente |
|------|-----------|--------|
| Frontend | React 19 + Vite 8 | `Frontend/package.json` |
| Estilos | Tailwind CSS 3 | `Frontend/package.json` |
| Routing | React Router 7 | `Frontend/package.json` |
| HTTP client | Axios | `Frontend/package.json` |
| Iconos | react-icons | `Frontend/package.json` |
| Backend | Flask (Python) | `HB-001`, `backend/` |
| Base de datos | PostgreSQL | `HB-001` (versión y driver: pendientes, ver `DATABASE_ARCHITECTURE.md`) |
| Autenticación | JWT (`flask-jwt-extended`) | `backend/app/extensions.py` |
| Documentación | Markdown + Handbook (MDX/SSG) | `docs/`, `handbook/` |

## Estado actual (implementado)

Lo que existe hoy en el código, sin adornos:

- **Frontend — Autenticación (UI):** páginas `AuthPage`, `Login` y `Register`. El login consume el backend; el registro es todavía un stub (`console.log` + redirección).
- **Frontend — Legal:** páginas estáticas `Terms`, `Privacy`, `Cookies`.
- **Backend — Auth:** un único endpoint, `POST /api/login`, que emite un JWT. La validación de credenciales es **temporal / hardcodeada** (aún sin base de datos).
- **Handbook:** aplicación de documentación técnica interna, completa (Release Candidate).

## API — Endpoints

| Método | Endpoint | Descripción | Estado |
|--------|----------|-------------|--------|
| POST | `/api/login` | Login → JWT |  Implementado (credenciales temporales, sin BD) |

> El resto de endpoints de una red social (registro persistente, posts, likes, comentarios, follows, notificaciones, perfiles, admin) **no existen todavía** y **no están especificados** en `docs/`. Se documentará cada endpoint el mismo día de su PR (`HB-001` §15.1), no de forma retroactiva.

## Instalación local

### Prerrequisitos
- Node.js 18+
- Python 3.11+
- PostgreSQL *(aún no integrado en el backend — ver nota más abajo)*

### Frontend (`Frontend/`)
```bash
cd Frontend
npm install
npm run dev
```
> La URL de la API está fijada en `src/shared/lib/api.js` (`http://127.0.0.1:5000/api`). No hay `.env.example` ni lista oficial de variables de entorno del Frontend todavía (pendiente de documentar).

### Backend (`backend/`)
```bash
cd backend
python run.py     # arranca en http://127.0.0.1:5000
```
>  **Dependencias del backend: pendientes.** No hay `requirements.txt` ni `pyproject.toml` en el repositorio, por lo que no existe un comando de instalación documentado (`CLAUDE.md` §4). Confirmar las dependencias con el equipo antes de asumir versiones.
>
>  **Secreto JWT por entorno.** `JWT_SECRET_KEY` se lee de una variable de entorno (`backend/app/config.py`). Debe estar definida en el entorno donde corra Flask; **nunca** se sube al repositorio (`HB-001` §19.1, §20).

## Flujo de ramas (Git Flow)

Fuente vinculante: `HB-001` §7–9 (resumen en `CLAUDE.md` §6).

- **`main`** — producción/entregable estable. Sin push directo.
- **`develop`** — integración. Sin push directo.
- Ambas exigen **Pull Request + al menos 1 aprobación** (el autor no se autoaprueba).
- **Ramas:** `feature/<nombre>`, `fix/<nombre>`, `chore/<nombre>`, `docs/<nombre>`, `hotfix/<nombre>`.
- **Commits (Conventional Commits):** `feat:` · `fix:` · `docs:` · `style:` · `refactor:` · `test:` · `chore:`.
- **PR:** resuelve una sola cosa; título con el mismo prefijo que los commits; vinculado a su Issue (`Closes #N`); sin `.env`/credenciales ni código de prueba olvidado.
- **Release:** `develop` → `main` periódicamente vía PR de release.

### Flujo por integrante
```bash
git checkout develop
git pull origin develop
git checkout -b feature/NOMBRE     # o fix/ , docs/ , chore/ , hotfix/
# ...cambios...
git commit -m "feat: descripción corta"
git push origin feature/NOMBRE
# Abrir Pull Request hacia develop y esperar aprobación
```

## Documentación

La documentación oficial vive en [`docs/`](docs/) (Markdown, versionada). Documentos de referencia:

- `docs/architecture/organization/` — Manual de Organización (`HB-001`): roles, git flow, gobernanza.
- `docs/architecture/REPOSITORY_STRUCTURE.md` — mapa del monorepo.
- `docs/architecture/DATABASE_ARCHITECTURE.md` — contrato de base de datos (borrador).
- `docs/architecture/design/` y `docs/architecture/Frontend/` — Design System, wireframes, prototipo y arquitectura del Handbook.

## Roadmap

> Intención de producto — **no** especificación aprobada (ver nota de alcance arriba). El estado  refleja lo realmente implementado hoy.

- [x] Setup del monorepo (backend / Frontend / handbook / docs)
- [x] THERS Engineering Handbook (Release Candidate)
- [x] Autenticación JWT — login (credenciales temporales)
- [ ] Integración de PostgreSQL y persistencia real de usuarios
- [ ] Registro de usuario persistente
- [ ] Publicaciones (texto + imagen)
- [ ] Likes y comentarios
- [ ] Sistema de seguidores y feed personalizado
- [ ] Perfiles de usuario
- [ ] Explorar / buscar usuarios
- [ ] Notificaciones
- [ ] Panel de administración
- [ ] Estrategia de testing
- [ ] DevOps / deploy

## Equipo

Equipo autogestionado de **4 integrantes** (`HB-001` §1). Roles, responsabilidades y ownership por documento están definidos en el Manual de Organización (`docs/architecture/organization/` — `HB-001` §2–3).

## Licencia

Distribuido bajo licencia MIT. Ver `LICENSE` para más información.

---

<div align="center">
Desarrollado con propósito educativo · THERS 2026
</div>
