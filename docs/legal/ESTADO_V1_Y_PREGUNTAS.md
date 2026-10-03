# Estado de la V1 y respuestas a las 20 preguntas (2026-10-02)

> Cada afirmación técnica fue **contrastada con el código** o con la base de desarrollo. Lo que depende
> de una decisión del equipo está marcado como tal. «Sin commit» = existe en la carpeta de trabajo pero
> no está en ninguna rama ni PR todavía.

## A. Qué está terminado de lo que pide la política (12 puntos)

| # | Punto | Estado | Evidencia / qué falta |
|---|---|---|---|
| 1 | Registro y edad mínima | **Casi** | Registro correo/contraseña ✅. Google Sign-In ✅ en web y backend (hay 2 cuentas solo-Google en la base de desarrollo); **no existe en la app móvil**. Bloqueo real de menores de 18 en el servidor ✅ (**sin commit**; `develop` todavía exige 13). Fecha de nacimiento guardada ✅ |
| 2 | Seguridad de contraseñas | ✅ | `scrypt:32768:8:1` en las 18 cuentas con contraseña (consulta a la base). Nunca se guarda la original. Recuperación por código de 6 dígitos, **10 min**, **5 intentos** |
| 3 | Sesiones y registros | **Hecho en código, sin commit** | Se guarda la **IP** y el **agente de usuario crudo**. Borrado automático a **90 días** implementado y probado (`ADR-037`). **Falta:** crear el Cron Job en Render; los registros de Render/gunicorn **no verificados** |
| 4 | Eliminación de cuenta | **Hecho, sin commit** | Backend, web (`/eliminar-cuenta`) y pantalla en la app. Los mensajes se borran en las dos bandejas. 39 pruebas |
| 5 | Moderación básica | **Incompleto** | Bloquear ✅ (en `develop`). Reportar publicación/comentario/mensaje/cuenta: backend en rama **sin fusionar**, interfaz móvil lista. **Faltan:** panel de moderación, suspender cuentas y retirar contenido (`ADR-032` fases 2 a 4). **Nada de esto se hizo en el cambio de seguridad infantil** |
| 6 | Seguridad infantil | **Parcial (hecho en código, sin commit ni desplegar)** | ✅ **Categoría de reporte** `child_safety` («Explotación o abuso de menores») en el sistema existente, para los 4 tipos de objetivo. ✅ **Prioridad máxima** (`critical`) asignada por el servidor, con escalada y límite propio. ✅ **Página pública** `/child-safety` (es/en) y enlace en el pie. ✅ Contacto publicado. **Siguen pendientes:** panel de moderación, retirada y suspensión administrativas, aviso al equipo ante un reporte crítico, flujo operativo interno, interfaz de reporte en la web y registrar el contacto en Play Console. Ver `SEGURIDAD_INFANTIL_GOOGLE_PLAY.md` y `ADR-038` |
| 7 | Correos oficiales | **1 de 5** | `soporte@` funciona (probado de punta a punta). **Crear:** `privacidad@`, `apelaciones@`, `seguridad@`, `seguridadinfantil@` |
| 8 | Proveedores | **Parcial** | En uso: Resend, Google OAuth, Cloudflare. **Sin contratar:** Supabase y Render. Expo/EAS solo compila |
| 9 | V1 cerrada | **Definida aquí** | Perfiles, cuentas públicas/privadas, publicaciones de texto, comentarios, «me gusta», seguidores, **mensajería individual** de texto, reportes, bloqueos, recuperación, Google, eliminación. **Fuera de la V1:** grupos, fotos en publicaciones, vídeo, audio, historias, llamadas, ubicación, contactos, push, IA |
| 10 | Permisos Android | **Sin auditar en release** | `app.json` no declara ninguno. El manifiesto de **depuración** trae `SYSTEM_ALERT_WINDOW` y lectura/escritura de almacenamiento (del cliente de desarrollo). **Hay que revisar el AAB de producción** antes de subirlo (Play Console → explorador del paquete) |
| 11 | Páginas legales web | **Incompleto** | `/terms`, `/privacy`, `/cookies` son marcadores «en construcción». `/eliminar-cuenta` ✅. **`/child-safety` ✅ hecha** (sin commit ni desplegar). **No existe** `/community-guidelines` |
| 12 | Decisiones legales | **Pendiente** | Ver sección C |

## B. Hallazgo importante: la analítica de la web

La web **no tiene hoy** Google Analytics, Cloudflare Analytics ni Turnstile (búsqueda en el código: ninguno). Si se agregan en el lanzamiento:
- **Google Analytics** instala cookies y casi seguro exige un aviso de consentimiento previo. Contradice «THERS no usa cookies».
- **Cloudflare Web Analytics** no usa cookies; es la opción más simple.
- **Turnstile** envía datos a Cloudflare para detectar bots.

**Recomendación:** lanzar la V1 **sin** Google Analytics (y con Cloudflare Analytics si quieren métricas). Así la política sigue siendo «sin cookies».
Además, la web carga las **fuentes de Google**, que envían la IP del visitante a Google: conviene **alojarlas en el propio sitio**.

## C. Las 20 preguntas

**Verificadas por mí (con evidencia):**

| # | Respuesta |
|---|---|
| 4 | **scrypt** (`werkzeug.security`), parámetros 32768:8:1, comprobado en la base |
| 5 | **Funciona en web y backend** con el Client ID configurado. **No existe en móvil.** No probado todavía con el dominio de producción (hay que autorizarlo en Google Cloud) |
| 6 | Se recibe **correo, nombre, si el correo está verificado y el identificador `sub`**. **No se recibe ni guarda la foto.** Solo se guardan nombre y correo en la cuenta y `sub` en la identidad |
| 7 | Se guarda el **agente de usuario crudo** sin interpretarlo. Incluye el modelo (p. ej. SM-A166B) **solo cuando el navegador lo manda**; la app móvil no lo manda |
| 8 | **Sí**: `sessions.ip_address`, tomada de `X-Forwarded-For` si existe (es falsificable, solo se usa para mostrarla) |
| 9 | La aplicación **no registra correos ni IPs** (el registro de fallos de correo guarda solo tipo y código de error). El **servidor de desarrollo** imprime la IP por petición. En producción: **pendiente** de ver la configuración de gunicorn/Render |
| 11 | **No aplica a la V1:** no existe «archivar» publicaciones |
| 12 | **Hoy se eliminan** los comentarios de la cuenta eliminada (borrado en cascada). «Usuario eliminado» exigiría un cambio de esquema y un ADR |

**Solo el equipo puede decidir** (con mi recomendación):

| # | Pregunta | Recomendación |
|---|---|---|
| 1 | Nombre completo del responsable legal | Decisión del equipo. No confirmado |
| 2 | ¿Publicarlo antes de la consulta con el abogado? | Esperar a la consulta |
| 3 | Domicilio como `[PENDIENTE DE DEFINIR]` | Sí, ya está así en el borrador |
| 10 | Conservar registros de seguridad más de 90 días | Sí, definiendo **qué** y **cuánto** |
| 13 y 14 | Conservar reportes y evidencias tras eliminar la cuenta, 12 meses | Sí. **Hoy no está implementado** (`ADR-032` borra el texto reportado al resolver) |
| 15 | Sensible permitido → desenfoque; ilegal → retirada inmediata | Sí. El desenfoque ya existe; la retirada inmediata requiere el panel de moderación |
| 16 | Pornografía explícita prohibida | Sí (Play lo exige para apps con contenido de usuarios) |
| 17 | Desnudez no sexual (artística o educativa) | Decisión de producto; si se permite, hay que escribirlo con condiciones claras |
| 18 | Lenguaje ofensivo permitido salvo acoso, amenazas o ataques dirigidos | Es una decisión de comunidad; la regla debe quedar escrita en las normas |
| 19 | El Salvador como ley principal | Sí, sujeto al abogado, **sin excluir normas imperativas de otros países** |
| 20 | Lanzamiento 18+, orientado a El Salvador, sin bloquear adultos de otros países | Coherente con la política; en Play, marcar 18+ y activar la restricción para menores |

## D. Lo que más pesa antes de poder cerrar la política

1. **Seguridad infantil (punto 6):** la categoría, la prioridad y la página pública **ya están hechas en código**. Falta lo que las hace efectivas: **panel de moderación, retirada y suspensión**. Sin eso, la página promete una capacidad que el sistema aún no tiene.
2. **Moderación operativa (punto 5):** sin panel para suspender y retirar contenido, la política promete algo que el sistema no puede hacer.
3. **Fusionar y desplegar** lo que ya está hecho (hay mucho trabajo sin commit).
4. **Crear los cuatro correos** que faltan.
