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
| Estilos | Tailwind CSS 3 | Implementado, sin tokens/Design System propio del producto |
| Routing | React Router v7 | Implementado — 6 rutas planas, sin rutas protegidas |
| Estado global | Ninguno todavía (solo `useState` local por componente) | No implementado |
| HTTP client | Axios | Implementado — URL de API configurable vía `VITE_API_URL` |
| Backend | Flask 3 (Python) | Implementado — un único flujo end-to-end (login); dependencias fijadas en `backend/requirements.txt` |
| Base de datos | PostgreSQL (motor elegido; versión, driver y esquema sin fijar) | No implementado — sin persistencia real ni ORM instalado |
| Autenticación | JWT (flask-jwt-extended) | Implementado solo para login; sin endpoints protegidos ni registro |

## Estructura del proyecto

Estructura real del monorepo — fuente: `docs/architecture/REPOSITORY_STRUCTURE.md`, `docs/architecture/FRONTEND_ARCHITECTURE.md` y `docs/architecture/BACKEND_ARCHITECTURE.md`. La carpeta del producto se llama `Frontend/` (con mayúscula inicial), no `frontend/`.

```
THERS_REDSOCIAL_2026/
├── Frontend/                  # Producto — la red social
│   ├── src/
│   │   ├── app/
│   │   │   └── router/        # AppRouter (react-router-dom)
│   │   ├── features/
│   │   │   ├── auth/          # hooks/, pages/, index.js
│   │   │   └── legal/         # pages/, index.js
│   │   ├── shared/
│   │   │   ├── components/    # UI reutilizable transversal
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
│   │   ├── config.py
│   │   └── extensions.py
│   ├── run.py
│   └── .env.example
│
├── handbook/                  # THERS Engineering Handbook (docs-as-code interno)
├── docs/                      # Documentación oficial versionada
├── CLAUDE.md
└── README.md
```

No existen (todavía) las carpetas `context/`, `services/` del lado del Frontend ni `routes/`/`models/` planos del lado del backend — el backend sigue una organización por capas (interfaces/application/domain), no por tipo de recurso.

## Instalación local

Estado real (no aspiracional): no hay `pyproject.toml` en `backend/` ni herramienta de migraciones instalada, y no hay persistencia de datos todavía — el login solo valida contra una credencial de prueba. Los pasos siguientes reflejan lo que hoy es reproducible; lo que no lo es se marca explícitamente.

### Prerrequisitos

- Node.js (versión mínima no fijada oficialmente)
- Python 3.x (versión mínima no fijada oficialmente; `BACKEND_ARCHITECTURE.md` observó 3.14.3 en un entorno local, no es un requisito documentado)
- PostgreSQL — motor elegido (`HB-001`), sin versión, esquema ni driver fijados todavía. No es necesario para levantar el login actual, que no usa base de datos.

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd THERS_REDSOCIAL_2026
```

### 2. Frontend

```bash
cd Frontend
npm install
cp .env.example .env        # ajustar VITE_API_URL si el backend no corre en 127.0.0.1:5000
npm run dev
```

Sin `VITE_API_URL` en `.env`, `Frontend/src/shared/lib/api.js` usa `http://127.0.0.1:5000/api` por defecto y lo advierte por consola.

### 3. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate — macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # definir JWT_SECRET_KEY
python run.py
```

Sin `JWT_SECRET_KEY` en `.env`, `backend/app/config.py` usa un valor de desarrollo inseguro y lo advierte por consola — no usar ese valor fuera de desarrollo local.

### Variables de entorno

**`backend/.env`** (ver `backend/.env.example`)
```env
JWT_SECRET_KEY=
```

**`Frontend/.env`** (ver `Frontend/.env.example`)
```env
VITE_API_URL=http://127.0.0.1:5000/api
```

No existe todavía ninguna variable de conexión a base de datos (`DATABASE_URL` o equivalente) porque la persistencia no está implementada.

## API — Estado real

Fuente única del contrato de API: `docs/architecture/API_CONTRACT.md`. La tabla siguiente refleja únicamente lo implementado hoy; el resto de endpoints listados más abajo en este README (feed, posts, comentarios, follows, notificaciones, admin) son parte del alcance funcional del producto, **no** de la API existente — no hay código ni contrato que los respalde todavía.

| Método | Endpoint | Descripción | Auth | Estado |
|--------|----------|-------------|------|--------|
| POST | `/api/login` | Login → JWT (credencial de prueba, sin persistencia real) | No | Implementado |
| POST | `/api/register` | Registro de usuario | No | No implementado — el Frontend ya tiene el formulario, el backend no expone el endpoint |

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
