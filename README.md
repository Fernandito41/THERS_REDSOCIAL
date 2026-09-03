<div align="center">

# THERS
### Bienvenidos a Thers una red social desarrollada para unir y conectar personas de todo el mundo de una manera facil y rapida.Utilizando interfaces interactivas y modernas, en Thers puedes crear,compartir publicaciones, historias y videos en tiempo real ademas de interactuar con otros usuarios.



**Conecta, comparte y descubre — la red social hecha para estudiantes**

![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite)
![Flask](https://img.shields.io/badge/Flask-3-000000?style=flat-square&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-motor%20elegido-4169E1?style=flat-square&logo=postgresql)
![TailwindCSS](https://img.shields.io/badge/Tailwind-3-38B2AC?style=flat-square&logo=tailwindcss)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

[Demo](#) · [Reportar Bug](../../issues) · [Solicitar Feature](../../issues)

</div>

---

## ¿Qué es THERS?

THERS es una red social que Permite publicar contenido (texto e imágenes), interactuar con otros usuarios mediante likes y comentarios, seguir perfiles, explorar publicaciones y recibir notificaciones — todo en un entorno pensado para todo el publico.

## Características

- Registro e inicio de sesión con JWT
- Publicaciones con texto e imágenes
- Feed personalizado con posts de personas seguidas
- Sistema de likes y comentarios
- Seguir / dejar de seguir usuarios
- Perfil de usuario con bio y posts propios
- Explorar y buscar otros estudiantes
- Notificaciones (likes, comentarios, nuevos seguidores)
- Panel de administración de usuarios
- Diseño responsive (mobile-first)

## Stack tecnológico

Fuente de verdad de esta tabla: `docs/architecture/FRONTEND_ARCHITECTURE.md`, `docs/architecture/BACKEND_ARCHITECTURE.md` y `docs/architecture/DATABASE_ARCHITECTURE.md`. Este archivo describe el proyecto, no decide su arquitectura — ante cualquier diferencia con esos documentos, ganan ellos.

| Capa | Tecnología | Estado |
|------|-----------|--------|
| Frontend | React 19 + Vite 8 | Implementado |
| Estilos | Tailwind CSS 3 (`darkMode: "class"`) | Implementado, sin tokens/Design System propio del producto |
| Routing | React Router v7 | Implementado — más de 30 rutas anidadas, con rutas protegidas (`ProtectedRoute`) |
| Estado global | React Context (`AuthContext`, `LanguageContext`, `ToastContext`) | Implementado — sin librería de estado externa (Redux/Zustand) |
| HTTP client | Axios | Implementado — URL de API configurable vía `VITE_API_URL` |
| Backend | Flask 3 (Python) | Implementado — capas `domain`/`application`/`infrastructure`/`interfaces`; dependencias fijadas en `backend/requirements.txt` |
| Base de datos | PostgreSQL 16 + SQLAlchemy + Flask-Migrate (driver `psycopg` v3) | Implementado — tablas `users` y `posts`, migraciones en `backend/migrations/`, contenedor en `docker-compose.yml` |
| Autenticación | JWT (flask-jwt-extended) | Implementado — registro, login y endpoints protegidos con `@jwt_required()` |
| Testing | pytest (backend) | Implementado — 75 pruebas de integración contra PostgreSQL real, no mocks |

## Estructura del proyecto

Estructura real del monorepo — fuente: `docs/architecture/REPOSITORY_STRUCTURE.md`, `docs/architecture/FRONTEND_ARCHITECTURE.md` y `docs/architecture/BACKEND_ARCHITECTURE.md`. La carpeta del producto se llama `Frontend/` (con mayúscula inicial), no `frontend/`.

```
THERS_REDSOCIAL_2026/
├── Frontend/                  # Producto — la red social
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout/        # AppShell, PublicLayout
│   │   │   └── router/        # router.jsx, ProtectedRoute.jsx
│   │   ├── features/          # auth/, feed/, help/, legal/, public/
│   │   ├── shared/
│   │   │   ├── components/    # UI reutilizable transversal
│   │   │   ├── hooks/
│   │   │   ├── i18n/          # LanguageContext (es/en, ADR-001)
│   │   │   └── lib/           # cliente HTTP (axios)
│   │   └── assets/
│   ├── index.html
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/                   # API Flask
│   ├── app/
│   │   ├── interfaces/routes/ # adaptadores HTTP (blueprints)
│   │   ├── application/       # casos de uso
│   │   ├── domain/            # reglas de negocio puras
│   │   ├── infrastructure/    # persistencia (modelos SQLAlchemy, repositorios)
│   │   ├── config.py
│   │   └── extensions.py
│   ├── migrations/            # Alembic / Flask-Migrate
│   ├── tests/                 # pytest (integración contra PostgreSQL real)
│   ├── run.py
│   └── .env.example
│
├── handbook/                  # THERS Engineering Handbook (docs-as-code interno)
├── docs/                      # Documentación oficial versionada
├── scripts/                   # Scripts de arranque local (dev-up / dev-test / dev-down)
├── docker/                    # Inicialización del contenedor de PostgreSQL
├── docker-compose.yml         # PostgreSQL 16 para desarrollo
├── CLAUDE.md
└── README.md
```

El backend sigue una organización por capas (`interfaces`/`application`/`domain`/`infrastructure`), no por tipo de recurso: no hay carpetas `routes/` ni `models/` planas en la raíz de `app/`. Del lado del Frontend, cada feature agrupa sus propias `pages/`, `hooks/` y (donde aplica) `context/`, en vez de tener carpetas globales por tipo de archivo.

## Instalación local

> **Guía completa y verificada: [`docs/LOCAL_DEV_SETUP.md`](docs/LOCAL_DEV_SETUP.md)** — instalación paso a paso, arranque diario, smoke test, tests y troubleshooting. Esta sección es solo el resumen.

### Prerrequisitos

- Docker Desktop (para PostgreSQL 16)
- Python 3.14 (versión usada en CI y en local; no es un mínimo ratificado formalmente)
- Node.js 24 + npm

### 1. Instalación (una sola vez)

```bash
git clone <URL_DEL_REPOSITORIO>
cd THERS_REDSOCIAL_2026

# Variables de entorno (ninguna se sube al repositorio)
cp .env.example .env                   # POSTGRES_PORT (puerto del host)
cp backend/.env.example backend/.env   # JWT_SECRET_KEY + DATABASE_URL
cp Frontend/.env.example Frontend/.env # VITE_API_URL

# Backend
cd backend
python -m venv venv
# Windows: venv\Scripts\Activate.ps1 — macOS/Linux: source venv/bin/activate
pip install -r requirements-dev.txt
cd ..

# Frontend
cd Frontend && npm ci && cd ..
```

Editar `backend/.env` antes de seguir: `DATABASE_URL` usa el driver explícito
`postgresql+psycopg://` y su puerto tiene que coincidir con el `POSTGRES_PORT` del
`.env` de la raíz. Los detalles y los errores típicos están en la guía.

### 2. Arranque

Con scripts (Windows / PowerShell) — levanta base de datos, aplica las migraciones a
`thers_dev` y `thers_test`, y abre backend y frontend:

```powershell
.\scripts\dev-up.ps1        # levanta todo
.\scripts\dev-test.ps1      # pytest del backend (-Frontend agrega lint + build)
.\scripts\dev-down.ps1      # detiene la base de datos
```

A mano, tres terminales:

```bash
docker compose up -d                                       # 1. base de datos
cd backend && flask run                                    # 2. API en :5000 (FLASK_APP=run.py)
cd Frontend && npm run dev                                 # 3. UI en :5173
```

`flask run` es el comando correcto: `python run.py` no lee `backend/.env` y aborta por
`JWT_SECRET_KEY` no definida (ver la guía, sección 8).

### Variables de entorno

| Archivo | Variables | Referencia |
|---|---|---|
| `.env` (raíz) | `POSTGRES_PORT` | `.env.example` |
| `backend/.env` | `JWT_SECRET_KEY`, `ALLOW_INSECURE_JWT_DEV_FALLBACK`, `DATABASE_URL` | `backend/.env.example` |
| `Frontend/.env` | `VITE_API_URL` | `Frontend/.env.example` |

Ningún `.env` se sube al repositorio (`HB-001` §20, regla innegociable). Sin
`VITE_API_URL`, el Frontend usa `http://127.0.0.1:5000/api` y lo advierte por consola;
sin `JWT_SECRET_KEY` ni `ALLOW_INSECURE_JWT_DEV_FALLBACK=1`, el backend no arranca.

## API — Estado real

Fuente única del contrato de API: `docs/architecture/API_CONTRACT.md`. La tabla siguiente refleja únicamente lo implementado hoy; las features listadas más arriba que no aparecen acá (comentarios, likes, follows, notificaciones, admin) son parte del alcance funcional del producto, **no** de la API existente — no hay código ni contrato que las respalde todavía.

| Método | Endpoint | Descripción | Auth | Estado |
|--------|----------|-------------|------|--------|
| POST | `/api/register` | Registro de usuario | No | Implementado |
| POST | `/api/login` | Login → JWT | No | Implementado |
| GET | `/api/users/me` | Perfil del usuario autenticado | JWT | Implementado |
| PATCH | `/api/users/me` | Actualización de perfil (`ADR-003`) | JWT | Implementado |
| POST | `/api/posts` | Crear publicación (texto, `ADR-004`) | JWT | Implementado |
| GET | `/api/posts` | Listar publicaciones del feed | JWT | Implementado |

## Flujo de ramas (Git Flow)

```
main          ← producción estable
└── develop   ← integración
    ├── feature/auth
    ├── feature/posts
    ├── feature/comments
    ├── feature/likes
    ├── feature/follow
    ├── feature/notifications
    ├── feature/explore
    ├── feature/profile
    ├── feature/admin
    └── feature/ui
```

**Convención de commits:**

```
feat:     nueva funcionalidad
fix:      corrección de bug
style:    cambios de UI/estilos
refactor: refactorización sin cambio de comportamiento
docs:     documentación
test:     pruebas
```
## Contribuir al proyecto (flujo por miembro)

### 1. Siempre trabajar desde develop
```bash
git checkout develop
git pull origin develop
```

### 3. Crear tu feature branch
```bash
git checkout -b feature/NOMBRE
# Ejemplos:
# git checkout -b feature/auth
# git checkout -b feature/posts
# git checkout -b feature/follow
```

### 4. Hacer tus cambios y commitear
```bash
git add .
git commit -m "feat: descripción corta de lo que hiciste"
```

### 5. Subir tu branch a GitHub
```bash
git push origin feature/NOMBRE
```

### 6. Abrir Pull Request en GitHub
- Ve a github.com/TU_USUARIO/thers
- Clic en **"Compare & pull request"**
- Base: `develop` ← Compare: `feature/NOMBRE`
- Describe los cambios y asigna un reviewer
- Espera aprobación antes de hacer merge

## Equipo

THERS es un equipo autogestionado de 4 integrantes, sin jerarquía de mando vertical — la dirección técnica se ejerce de forma colegiada (`HB-001` §1). Fuente de esta tabla: `HB-001` §2.

| Rol | Enfoque principal | Responsable de |
|-----|-------------------|-----------------|
| Project Owner / Scrum Master | Gestión ágil y producto | Backlog, sprints, reuniones, seguimiento de avance |
| Tech Lead Backend | Flask, PostgreSQL, JWT, API | Arquitectura de backend, endpoints, seguridad, migraciones |
| Tech Lead Frontend | React, Vite, Tailwind | UI/UX, componentes, consumo de API, estado de la app |
| QA / Documentación / DevOps de apoyo | Calidad y soporte técnico | Pruebas, documentación técnica, CI básico, GitHub |

Cada integrante tiene un rol principal, pero todos participan en revisión de código, testing y documentación; los roles rotan cada semestre académico o cada 3 meses de desarrollo (`HB-001` §2).

## Roadmap

- [x] Setup del proyecto
- [x] Autenticación JWT
- [ ] Publicaciones (texto + imagen)
- [ ] Likes y comentarios
- [ ] Sistema de seguidores
- [ ] Feed personalizado
- [ ] Perfiles de usuario
- [ ] Explorar / buscar usuarios
- [ ] Notificaciones
- [ ] Panel de administración
- [ ] UI responsive final
- [ ] Testing
- [ ] Deploy

## Licencia

Distribuido bajo licencia MIT. Ver `LICENSE` para más información.

---

<div align="center">
Desarrollado con propósito educativo · THERS 2026
</div>
