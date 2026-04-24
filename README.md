<div align="center">

# THERS
### Bienvenidos a Thers una red social desarrollada para unir y conectar personas de todo el mundo de una manera facil y rapida.Utilizando interfaces interactivas y modernas, en Thers puedes crear,compartir publicaciones, historias y videos en tiempo real ademas de interactuar con otros usuarios.



**Conecta, comparte y descubre — la red social hecha para estudiantes**

![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite)
![Flask](https://img.shields.io/badge/Flask-3-000000?style=flat-square&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8-4479A1?style=flat-square&logo=mysql)
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

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + Vite 5 |
| Estilos | Tailwind CSS 3 |
| Routing | React Router v6 |
| Estado global | Context API + hooks |
| HTTP client | Axios |
| Backend | Flask 3 (Python) |
| Base de datos | MySQL 8 |
| Autenticación | JWT (flask-jwt-extended) |

## Estructura del proyecto

```
thers/
├── frontend/
│   ├── src/
│   │   ├── components/       # UI reutilizable (Navbar, PostCard)
│   │   ├── pages/            # Home, Login, Register, Profile, Explore
│   │   ├── routes/           # AppRouter + rutas protegidas
│   │   ├── context/          # AuthContext, PostContext
│   │   ├── services/         # authService, postService, userService…
│   │   └── assets/
│   ├── index.html
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/
│   ├── routes/               # auth, posts, users, comments, likes, follows
│   ├── models/               # User, Post, Comment, Like, Follow, Notification
│   ├── config/               # DB, JWT
│   └── app.py
│
└── README.md
```

## Instalación local

### Prerrequisitos

- Node.js 18+
- Python 3.11+
- MySQL 8+

### 1. Clonar el repositorio

```bash
git clone https://github.com/Fernandito41/THERS_REDSOCIAL
cd THERS_REDSOCIAL
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env        # configurar VITE_API_URL
npm run dev
```

### 3. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # configurar DB y JWT_SECRET
flask db upgrade
flask run
```

### Variables de entorno

**frontend/.env**
```env
VITE_API_URL=http://localhost:5000/api
```

**backend/.env**
```env
DATABASE_URL=mysql+pymysql://user:password@localhost/thers_db
JWT_SECRET_KEY=tu_clave_secreta
UPLOAD_FOLDER=uploads/
```

## API — Endpoints principales

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Registro de usuario | No |
| POST | `/api/auth/login` | Login → JWT | No |
| GET | `/api/auth/me` | Usuario autenticado | Sí |
| GET | `/api/posts` | Feed personalizado | Sí |
| POST | `/api/posts` | Crear publicación | Sí |
| DELETE | `/api/posts/:id` | Eliminar publicación | Sí |
| POST | `/api/posts/:id/like` | Like / unlike | Sí |
| GET | `/api/posts/:id/comments` | Ver comentarios | Sí |
| POST | `/api/comments` | Crear comentario | Sí |
| GET | `/api/users/:id` | Ver perfil | Sí |
| POST | `/api/users/:id/follow` | Seguir usuario | Sí |
| DELETE | `/api/users/:id/follow` | Dejar de seguir | Sí |
| GET | `/api/users/explore` | Explorar estudiantes | Sí |
| GET | `/api/notifications` | Ver notificaciones | Sí |
| GET | `/api/admin/users` | Gestión de usuarios | Admin |

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

| Rol | Responsabilidad |
|-----|----------------|
| Frontend (×2) | React, componentes, páginas, UI |
| Backend (×2) | Flask, API REST, modelos, DB |
| UI/UX (×1) | Diseño, Tailwind, assets, experiencia |
| DB / Testing (×1) | Esquema MySQL, pruebas, integración |

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
