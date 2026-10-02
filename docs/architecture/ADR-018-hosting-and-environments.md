# ADR-018 — Hosting, dominio y entornos

- **Estado:** **`PROPUESTO`** el 2026-10-02 — **pendiente de aprobación del equipo** (`HB-001` §11–12).
  Lo redactó Claude Code a pedido del propietario del proyecto; no es una decisión ratificada.
- **Fecha:** 2026-10-02
- **Por qué existe:** `CLAUDE.md` §5/§15 registra que **DevOps no tiene documentación oficial**
  (Docker, CI/CD, deploy, SSL, dominios, monitoreo). Contratar servicios de pago sin una decisión
  escrita sería improvisar una decisión de alto impacto (`CLAUDE.md` §6).
- **Relacionado:** `ADR-015-profile-media.md` (almacenamiento S3), `ADR-012-google-sign-in.md`,
  `ADR-009`/`ADR-011` (correo vía Resend), `ADR-016-mobile-stack.md`, `docs/LAUNCH_CHECKLIST.md`.

---

## 1. Contexto, verificado en el repositorio

| Hecho | Fuente |
|---|---|
| Backend Flask con `gunicorn==23.0.0` ya en `requirements.txt`; **no hay `Dockerfile`** | `backend/requirements.txt` |
| Almacenamiento de imágenes ya soporta S3: `STORAGE_BACKEND=local` o `s3` (`boto3`) | `backend/.env.example`, `config.py` |
| El almacenamiento `local` **no sirve en un host con disco efímero** | `.env.example` lo exige distinto de `local` fuera de desarrollo |
| CI existente: `ci.yml` y `backend-tests.yml` (sin despliegue) | `.github/workflows/` |
| Correo con Resend; sin dominio verificado, solo entrega al dueño de la cuenta de Resend | prueba real 2026-10-02 (`403`) |
| `JWT_SECRET_KEY` falla rápido si falta fuera de desarrollo | `backend/app/config.py` |

## 2. Propuesta

| Pieza | Proveedor propuesto | Por qué |
|---|---|---|
| Frontend web (Vite, estático) | **Cloudflare Pages** (plan gratuito) | CDN y HTTPS incluidos |
| Backend Flask | **Render**, servicio web **Starter** | Despliegue desde Git, sin dormirse (el plan gratuito sí se duerme a los 15 min) |
| PostgreSQL 16 | **Supabase Pro** | Copias diarias (7 días) y sin pausa por inactividad |
| Imágenes y media | **Supabase Storage** (compatible con S3) al inicio | Ya incluido en Pro; cambiar a Cloudflare R2 es solo configuración |
| Dominio y DNS | **Cloudflare Registrar** o **Porkbun** (con DNS en Cloudflare) | Un solo panel para DNS y TLS |
| Correo transaccional | Resend, con **dominio verificado** (SPF/DKIM) | Desbloquea el envío a cualquier destinatario |

Subdominios previstos: `www`/raíz → Pages, `api` → Render, y `staging.*` para el entorno de pruebas.

### 2.1 Costos verificados el 2026-10-02

| Concepto | Valor | Fuente |
|---|---|---|
| Render Starter / Standard | 7 USD/mes (512 MB) / 25 USD/mes (2 GB); Free se duerme a los 15 min | render.com/pricing |
| Supabase Pro | 25 USD/mes: 8 GB de BD, 100 GB de archivos, 250 GB de salida, copias diarias 7 días; luego 0,125 USD/GB de BD, 0,0213 USD/GB de archivos, 0,09 USD/GB de salida | supabase.com/pricing |
| Supabase Free | 500 MB de BD y 1 GB de archivos; **pausa tras 1 semana sin uso** | supabase.com/pricing |
| Cloudflare Pages Free | 500 builds/mes, 20 000 archivos/sitio, 25 MiB por archivo | developers.cloudflare.com/pages/platform/limits |
| Dominio `.com` | ≈ 11 USD/año (Porkbun, renueva al mismo precio; confirmar al comprar) | Porkbun |
| **Total base** | **≈ 32 USD/mes + dominio ≈ 395 USD/año** | suma |
| Fuera del total | Google Play (pago único), EAS Build, monitoreo, tráfico o almacenamiento extra, Resend si supera su plan gratuito | — |

Los precios cambian: **reverificar al contratar**.

## 3. Condiciones técnicas (sin cumplirlas, la propuesta no vale)

1. **Supabase + psycopg 3 + SQLAlchemy:** el pooler en modo transacción **no admite sentencias
   preparadas**. Si se usa, hay que pasar `connect_args={"prepare_threshold": None}`. La conexión
   directa es **solo IPv6** salvo el complemento IPv4; el pooler en modo sesión sirve si el host solo
   tiene IPv4. **Probar en staging cuál funciona desde Render** antes de producción.
2. **Disco de Render efímero:** `STORAGE_BACKEND=s3` es obligatorio; nunca `local`.
3. **Memoria:** Starter tiene 512 MB y el backend re-codifica imágenes con Pillow dentro de la
   petición. **No medido**; si aparece un OOM, subir a Standard (2 GB) antes que optimizar a ciegas.
4. **Región:** colocar Render y Supabase en regiones cercanas entre sí y a los usuarios.
5. **CORS:** `CORS(app)` debe limitarse a los dominios reales (web de producción y staging); hoy es
   permisivo para desarrollo.
6. **HTTPS obligatorio** en la API. La app Android de producción no puede usar HTTP.
7. **Secretos** solo en las variables de entorno del proveedor, nunca en el repositorio (`HB-001` §20).
   `JWT_SECRET_KEY`, `DATABASE_URL`, `RESEND_API_KEY`, claves S3 y `GOOGLE_CLIENT_ID` distintos por entorno.
8. **Copias de seguridad:** una **restauración probada** antes del lanzamiento, no solo "activadas".

## 4. Entornos

| Entorno | Propósito | Datos |
|---|---|---|
| Local | Desarrollo (Docker Compose, `thers_dev`) | ficticios |
| **Staging** | Probar migraciones, la app móvil con HTTPS y el cierre de pruebas de Play | ficticios |
| Producción | Usuarios reales | reales |

Migraciones (`flask db upgrade`) **siempre primero en staging**. Producción solo despliega desde `main`.

## 5. Titularidad y continuidad

El dominio, el DNS y las cuentas de hosting deben estar a nombre del **proyecto** (o de una persona
designada) con acceso compartido y 2FA, no en la cuenta personal de un solo integrante: un equipo de
4 no debe depender de que una persona esté disponible.

## 6. Opciones descartadas por ahora

| Opción | Motivo |
|---|---|
| VPS propio (p. ej. DigitalOcean) | Ustedes mantendrían actualizaciones, seguridad y despliegues; no compensa en esta etapa |
| Railway | Cobro por consumo, menos predecible para presupuestar |
| Supabase Free | Pausa por inactividad y sin copias: solo para prototipos |

## 7. Qué falta decidir (requiere al equipo)

- Aprobación formal de este ADR y quién es titular de las cuentas.
- Región concreta, y si el almacenamiento arranca en Supabase Storage o en R2.
- Monitoreo, alertas y registro de errores (no cubiertos aquí).
- Política de retención de datos y copias, y el aviso de privacidad (`docs/LAUNCH_CHECKLIST.md`).
- Un `Dockerfile` o el comando de arranque de Render para `gunicorn` (a definir al implementar).
