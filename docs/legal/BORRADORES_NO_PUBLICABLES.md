# THERS — Borradores legales (NO PUBLICABLES)

> **ESTADO: NO PUBLICABLE.** Contiene datos `[PENDIENTE: …]`, no ha sido revisado por un abogado
> salvadoreño y **no declara cumplimiento legal**. Fecha de redacción: **2026-10-02**.
> Archivo local, **sin versionar** (no está en ningún commit ni PR). Redactado por Claude Code a
> pedido del propietario del proyecto. Las recomendaciones de moderación son **propuestas**, no
> acuerdos definitivos del equipo ni obligaciones legales.

Contenido: **A** datos confirmados · **B** preguntas al equipo · **C** recomendaciones · **D** borradores ·
**E** diferencias entre el producto actual y los borradores · **F** puntos para el abogado · **Fuentes**.

Inventario verificado contra `origin/develop` en `3cb1c6c` (PR #68), 2026-10-02.

---

## A. Datos confirmados y evidencia técnica

### A.1 Datos que el producto guarda hoy (tabla → columnas, de `backend/app/infrastructure/persistence/models.py`)

| Categoría | Datos | Dónde |
|---|---|---|
| Cuenta | nombre, usuario, correo, teléfono + código de país, fecha de nacimiento **declarada** (no verificada), contraseña (solo hash), correo verificado | `users` |
| Perfil | biografía, ubicación, sitio web, foto y portada | `users` + almacenamiento de imágenes |
| Preferencias | cuenta privada, quién puede mencionar / escribir, ocultar comentarios ofensivos o contenido sensible, mostrar actividad, alertas de inicio de sesión | `users` |
| Presencia | `last_seen_at` (última vez conectado) | `users` |
| Seguridad | secreto TOTP, códigos de recuperación (hash), 2FA activada | `users`, `two_factor_recovery_codes` |
| Contenido | publicaciones, comentarios, me gusta, seguidos, menciones | `posts`, `comments`, `likes`, `follows`, `mentions` |
| **Mensajes directos** | texto, remitente, destinatario, fecha, leído, editado | `messages` |
| Notificaciones **dentro de la app** | tipo, actor, publicación | `notifications` |
| Filtros y bloqueos | palabras y temas silenciados, bloqueos y silenciados | `muted_keywords`, `muted_topics`, `user_restrictions` |
| **Sesiones** | **agente de usuario (navegador/dispositivo) y dirección IP**, fechas de uso y revocación | `sessions` |
| Tokens | refresh tokens (hash), códigos de verificación y de recuperación (hash) | `refresh_tokens`, `*_tokens` |
| Identidad externa | identificador de Google (`sub`) | `user_identities` |
| Límite de uso | hash SHA-256 de la IP o identificador, contador y ventana | `rate_limit_buckets` |
| Exportación | archivo de datos generado a pedido, guardado en la base | `data_exports` |

### A.2 Servicios externos y SDK (verificado en `package.json`, `requirements.txt`, `index.html`)

| Servicio | Para qué | Datos que recibe | Estado |
|---|---|---|---|
| **Google Identity Services** (`accounts.google.com/gsi/client`, script cargado en la web) y `google-auth` en el backend | "Continuar con Google" | credencial de Google (correo, nombre, `sub`) | **Implementado** |
| **Google Fonts** (`fonts.googleapis.com`, `fonts.gstatic.com`, cargadas desde `index.html`) | tipografía e iconos | **IP y agente de usuario de cada visitante**, aunque no tenga cuenta | **Implementado** |
| **Resend** (`resend==2.45.0`) | correos transaccionales | dirección de correo, nombre, código; en el aviso de inicio de sesión también **dispositivo e IP** | **Implementado**; la cuenta de producción **no está verificada con dominio propio** |
| **Cloudflare, Supabase, Render** | web, base de datos/almacenamiento, backend | todo lo anterior | **Planeado** (ADR-018 aceptado; **nada contratado**) |
| Almacenamiento S3-compatible (`boto3`) | foto y portada | imágenes (sin EXIF: se re-codifican con Pillow) | **Configurable**; hoy `local` en desarrollo |
| Analítica, publicidad, rastreadores, Sentry/Firebase/etc. | — | — | **No existen** (búsqueda en `Frontend/src`, `mobile/`, `backend/`: sin coincidencias reales) |
| Notificaciones push (`expo-notifications`, FCM) | — | — | **No existen** (planeadas, segunda fase) |
| WebSocket / Socket.IO | — | — | **No existen** |

### A.3 Almacenamiento en el dispositivo

**Web (`localStorage`; ninguna cookie: no hay `document.cookie` en el código):**

| Clave | Contenido | Necesaria |
|---|---|---|
| `token`, `user` | token de acceso y copia del perfil público | Sí (sesión) |
| `theme` | claro/oscuro | Preferencia |
| `thers_language` | idioma | Preferencia |
| `thers_help_feedback_<artículo>` | si marcó útil un artículo | Preferencia |
| `…<username>` (perfil extendido y ajustes locales) | ánimo, intereses, ajustes | Preferencia |

El desafío de 2FA vive en memoria del navegador, no en `localStorage`. La web **no** usa todavía refresh token (su sesión muere a los 15 min, ADR-017).

**Móvil:** `expo-secure-store` (Android Keystore) guarda token de acceso y refresh token. **Sin permisos especiales** declarados (`app.json`: solo los plugins `expo-router` y `expo-secure-store`; sin cámara, ubicación ni notificaciones).

### A.4 Mensajería: lo que existe hoy

- **Chat privado:** existe **en la web** (`Messages.jsx`) y en el backend: enviar, listar hilos, conversaciones con contador de no leídos, editar y borrar mensaje, indicador de "escribiendo", filtros `who_can_message` y bloqueo (`is_blocked_between`).
- **No es tiempo real:** la web consulta el servidor cada 4 s (hilo) y 2 s (escribiendo) (`THREAD_POLL_MS`, `TYPING_POLL_MS`). El indicador de "escribiendo" vive **en memoria del proceso** del servidor (`InMemoryTypingIndicatorRepository`): no sirve con más de un proceso.
- **La app móvil no tiene pantalla de chat** (solo login, 2FA y perfil).
- **Sin cifrado de extremo a extremo:** `messages.content` es texto plano en la base. No hay evidencia de cifrado de aplicación (búsqueda de `encrypt`/`fernet`/`aes`: nada relevante). **No debe afirmarse E2EE.**
- **Acceso del personal:** hoy **no existe ninguna ruta ni herramienta** para que un moderador lea mensajes. Quien administre la base de datos técnicamente puede leerlos. La fase 1 de reportes (rama sin fusionar) guarda **una copia del texto del mensaje reportado** y solo permite reportar al **destinatario**.
- **Sin protección contra duplicados:** el envío no lleva identificador de cliente (`client_id`), así que un reintento puede crear dos mensajes.
- **Correos transaccionales hoy:** código de registro, código de recuperación, contraseña cambiada, alerta de inicio de sesión nuevo. (Planeado: confirmación de cuenta eliminada.)

### A.5 Conservación real (lo que hace el código, no lo que se desearía)

| Dato | Plazo real |
|---|---|
| Datos de cuenta, contenido, mensajes | **Mientras exista la cuenta.** Hoy **no hay forma de eliminarla** (ADR-031 aceptado, sin implementar) |
| Sesiones (IP + agente de usuario) | **Mientras exista la cuenta.** No encontré ninguna tarea que borre sesiones vencidas o revocadas |
| Tokens de acceso / refresh | 15 min / 30 días; las filas **no se borran** solas al vencer (verificar) |
| Códigos de verificación y recuperación | caducan en minutos; limpieza de filas vencidas: **parcial** |
| `rate_limit_buckets` | se purgan a las **24 h** (`_PURGE_AFTER_SECONDS`); el hash SHA-256 **sin sal** de una IP es **seudónimo, no anónimo** |
| Exportación de datos | **7 días** (`EXPORT_TTL_DAYS`), luego se elimina |
| Copias de seguridad | `[PENDIENTE]`: ADR-018 propone 7 días con Supabase Pro; no contratado |
| Registros del servidor (stderr) | `[PENDIENTE]`: depende de Render; sin política definida |
| Registros en Resend | `[PENDIENTE: consultar retención de Resend]` |

### A.6 Edad mínima: lo que hace el código

**Actualización 2026-10-02:** decisión de producto: **18 años cumplidos o más**, web y Android. Implementado en `domain/auth/validators.py`, `dateUtils.js` y la app móvil (`ADR-034`). La fecha es **declarada**, no verificada con documentos.

### A.7 Implementado / configurado para producción / planeado

| Función | Estado |
|---|---|
| Registro, login, Google, 2FA TOTP, sesiones, recuperación de contraseña | Implementado |
| Publicaciones, comentarios, me gusta, seguidos, menciones, notificaciones en la app | Implementado |
| Chat privado por consulta periódica (web) | Implementado (**no** tiempo real, **no** en móvil) |
| Bloqueos y silenciados, filtros de contenido | Implementado |
| Exportación de datos (7 días) | Implementado |
| Reportes y aceptación de términos | Rama **sin fusionar** (esperaba la ratificación; hoy ratificado) |
| Eliminación de cuenta, suspensión voluntaria | Aceptado (ADR-031), **sin implementar** |
| Moderación, advertencias, apelaciones | Aceptado (ADR-032), **sin implementar** |
| Hosting Cloudflare/Supabase/Render, dominio, correos públicos | Aceptado (ADR-018), **nada contratado** |
| Chat en tiempo real, push, silenciar, contenido oculto en avisos | **Planeado** |
| Suscripciones | **Planeado** (hoy no hay) |

---

## B. Preguntas pendientes para el equipo (solo lo que no se puede comprobar)

1. **Responsable legal: `[PENDIENTE DE CONFIRMACIÓN]`.** No está confirmado que una sola persona (ni quién) sea responsable del tratamiento y de la operación. Domicilio para notificaciones: `[PENDIENTE]`.
2. **Entidad.** ¿Se va a constituir una sociedad antes del lanzamiento? (Cambia quién responde y quién firma los términos.)
3. **Países de lanzamiento:** `[PENDIENTE]`. Si es solo El Salvador o también otros (cambia el análisis legal y la ficha de Play).
4. **Correos públicos** de soporte, privacidad, apelaciones y seguridad infantil: `[PENDIENTE]` (y el **dominio**).
5. **Persona de contacto para seguridad infantil** (Play la pide con nombre): `[PENDIENTE]`.
6. **Edad:** la decisión vigente es 18 (ver C.1).
7. **Moderadores y plazo de respuesta.** Fernando y Cristopher figuran en el ADR-032; el plazo (propuesta 24–48 h) sigue sin fijar. Los nombres **no deberían publicarse** en los textos: usar "el equipo de moderación".
8. **Apelación:** qué ocurre si pasan las 48 h sin contacto; plazo para responder; quién revisa.
9. **Faltas graves** que permiten suspender sin advertencia previa.
10. **Mensajes de una cuenta eliminada:** confirmar que se conservan con "Usuario no encontrado" (ADR-031 §C).
11. **Región** de Supabase y Render (decide si hay transferencia internacional).
12. **Monetización:** hoy no hay; ¿qué se prevé? Se redactó como "no hay suscripciones" y se actualiza al lanzarlas.

## C. Recomendaciones, con alternativas y consecuencias

### C.1 Edad mínima
La ley salvadoreña **no fija una edad** para consentir: el art. 26 remite al *Principio de Ejercicio Progresivo de las Facultades* y el art. 42 exige informar a niñas, niños y adolescentes **y a sus progenitores o tutores**. No hay un 13/16/18 que adoptar automáticamente.

| Opción | Consecuencia |
|---|---|
| **a) 15+ con aviso claro y mención a madres/padres/tutores** (lo decidido) | Más simple; **el riesgo jurídico lo asume el equipo** hasta que un abogado lo valide |
| b) 18+ | Elimina casi todo el riesgo de menores; pierde audiencia |
| c) 15–17 con consentimiento de un tutor | Más protección; exige un flujo de verificación que no existe |

Recomiendo **a) provisionalmente**, con la revisión del abogado (F.1) **antes** de publicar, y ajustar el código a 15 (E).

### C.2 Ley aplicable y fuero
Se propone **El Salvador** para revisión. Se redactó **sin** excluir derechos u obligaciones imperativas de otros países ni de consumidores.

### C.3 Notificaciones push (segunda fase)
Contenido privado **oculto por defecto** («Tienes un mensaje nuevo», sin nombre ni texto). **Decisión de producto pendiente.** Si más adelante se permite mostrar el texto, pasaría por el proveedor de notificaciones (Google FCM) y habría que declararlo.

### C.4 Chat en tiempo real (primera fase): implementación mínima
Hoy: consulta cada 2–4 s. Opciones:

| Opción | Dependencias | Pros / contras |
|---|---|---|
| **1. Mantener la consulta periódica, mejorar** (más espaciada cuando la pestaña no está activa, `client_id`, "mensajes desde X") | Ninguna | Cero costo; **no es tiempo real estricto** |
| **2. SSE (Server-Sent Events) desde Flask** | Ninguna del lado cliente; en el servidor, `gunicorn` con hilos/gevent | Es unidireccional, suficiente para recibir; Render mantiene conexiones abiertas; con varios procesos hace falta un bus (Redis o `LISTEN/NOTIFY` de PostgreSQL) |
| **3. Supabase Realtime** (ya aceptada en ADR-018) | `@supabase/supabase-js` en web y móvil | Tiempo real sin servidor propio; **cambia el modelo de autorización** (RLS o canales con JWT) y duplica reglas de bloqueo; **verificar límites y precio vigentes** |
| 4. Flask-SocketIO | `flask-socketio`, `eventlet`/`gevent`, Redis para varios procesos | Estándar; más piezas que operar |

Recomiendo **1 + `client_id` ahora y SSE (opción 2) con `LISTEN/NOTIFY`** como paso a tiempo real, porque no agrega servicios de pago ni cambia quién autoriza (el backend sigue siendo la única puerta). **No he medido costos de Supabase Realtime ni de Render: verificar antes de decidir.**

Mínimo común a cualquiera: identificador de cliente para evitar duplicados, **recuperación por cursor** al reconectar (`GET …messages?after=<id>`), contador de no leídos ya existente, comprobación de participación en cada lectura (ya existe), y una pantalla de chat en la app móvil (**no existe**).

### C.5 Push (segunda fase)
- Dependencias: `expo-notifications`, proyecto **Firebase** (credenciales FCM V1) y `google-services.json` (documentación de Expo).
- **Costo:** Expo documenta que **enviar por su servicio de push no tiene costo** y limita a **600 notificaciones por segundo por proyecto**. Firebase/FCM: **verificar** condiciones vigentes (no las comprobé).
- Tabla nueva para guardar el *token del dispositivo* (dato personal que hay que declarar), borrado al cerrar sesión, al eliminar la cuenta y al recibir "token inválido".
- Las notificaciones **no guardan ni entregan el historial**: solo avisan.

### C.6 Cookies y banner
THERS **no usa cookies**. Solo `localStorage` (A.3). Todo es **necesario para lo que la persona pidió** (sesión) o **preferencia que ella misma elige** (tema, idioma). **No se justifica un banner de consentimiento**; sí un aviso informativo. Lo único externo es **Google Fonts**: transmite la IP a Google. Opciones: (a) declararlo; (b) **alojar las fuentes en el propio sitio** (recomendado: elimina esa transferencia y no cambia el diseño). Si se agrega analítica o publicidad algún día, **entonces** hará falta consentimiento previo.

### C.7 Delegado de protección de datos
El texto de 2024 (art. 15–16) obliga a nombrar un delegado. **Una reforma aprobada el 2026-09-17 deroga los arts. 15 y 17 para el sector privado** (ver F.2). Mientras no se confirme su publicación, **no mencionar delegado** en el aviso; mencionar un **canal de contacto**.

---

## D. Borradores

> Cada borrador es **NO PUBLICABLE** mientras tenga `[PENDIENTE]`. Se redactó para que **solo describa lo
> que existe**; lo planeado va marcado «cuando esté disponible». Debe actualizarse al activar cada función.

### D.1 Términos de uso — BORRADOR NO PUBLICABLE

**Versión:** `[PENDIENTE: fecha de publicación]` · **Última actualización:** `[PENDIENTE]`

**1. Quién ofrece THERS.** THERS es una red social operada desde El Salvador por `[PENDIENTE: responsable(s) legal(es) por confirmar]` (en adelante, «THERS», «nosotros»), con domicilio `[PENDIENTE]` y contacto `[PENDIENTE: correo de soporte]`. «THERS» es el nombre del proyecto; **no es una sociedad registrada** `[PENDIENTE: actualizar si se constituye una]`.

**2. Aceptación y edad.** THERS es **solo para personas de 18 años cumplidos o más**. Al crear tu cuenta declaras tu fecha de nacimiento; no la verificamos con documentos, y podemos suspender cuentas de quien no cumpla este requisito `[PENDIENTE: revisión jurídica]`. Al registrarte y marcar la casilla aceptas estos términos y reconoces haber leído la Política de Privacidad. Podemos cambiarlos; si el cambio es relevante te pediremos aceptarlos de nuevo.

**3. Tu cuenta.** Eres responsable de lo que ocurre con tu cuenta y de mantener segura tu contraseña. Debes darnos datos verdaderos y no suplantar a otra persona. Recomendamos activar la verificación en dos pasos.

**4. Tu contenido y la licencia que nos das.** Lo que publicas **sigue siendo tuyo**. Nos das una licencia **limitada, no exclusiva, mundial y revocable** para alojar, mostrar, reproducir técnicamente (por ejemplo, redimensionar una imagen) y distribuir tu contenido **únicamente para prestar el servicio** a ti y a las personas con quienes decidas compartirlo. **No la usamos para otros fines, no vendemos tu contenido y no adquirimos su propiedad.** La licencia termina cuando lo eliminas o eliminas tu cuenta, salvo copias técnicas y de respaldo que se borran según la Política de Privacidad, y salvo el contenido que otras personas hayan guardado o compartido por su cuenta.

**5. Reglas de la comunidad.** No está permitido: `[PENDIENTE: el equipo debe redactar la lista definitiva. Propuesta de base: acoso y amenazas; discurso de odio; contenido sexual explícito o que involucre a menores; violencia gráfica; suplantación; spam y engaño; compartir datos personales de otras personas; fraudes; contenido ilegal en El Salvador o en el país de quien lo usa]`. No se puede sancionar por una regla que aquí no esté publicada.

**6. Reportar y bloquear.** Puedes **reportar** publicaciones, comentarios, mensajes que hayas recibido y perfiles, y **bloquear** a otras cuentas. Quien reporta **no es revelado** a la persona reportada. Un reporte hecho de mala fe de forma repetida puede ser limitado.

**7. Moderación.** El equipo de moderación `[PENDIENTE: ver B.7]` revisa los reportes y puede revisar perfiles que incumplan estas reglas aunque nadie los haya reportado. Intentamos actuar `[PENDIENTE: plazo]`. Para revisar un reporte accedemos únicamente al contenido reportado y a lo necesario para entenderlo.

**8. Medidas.** Según la gravedad podemos: (a) retirar el contenido; (b) enviarte una **advertencia**; (c) **suspender** tu cuenta. En faltas graves `[PENDIENTE: definir cuáles]` podemos suspender sin advertencia previa. Te diremos el motivo.

**9. Apelación.** Si suspendemos tu cuenta, tienes **48 horas** `[PENDIENTE: confirmar y definir qué pasa al vencer]` para escribir a `[PENDIENTE: correo de apelaciones]` con las pruebas que quieras presentar. Revisaremos tu caso `[PENDIENTE: quién y en cuánto tiempo]`.

**10. Tres cosas distintas.**
- **Desactivación voluntaria** `[cuando esté disponible]`: tú decides pausar tu cuenta; tu perfil y publicaciones dejan de verse y puedes volver. No borra tus datos.
- **Suspensión por moderación:** la decidimos nosotros por incumplir las reglas; puedes apelar (punto 9).
- **Eliminación definitiva** `[cuando esté disponible]`: borra tu cuenta y sus datos, con las excepciones de la Política de Privacidad. **No se puede deshacer.**

**11. Mensajes privados.** Los mensajes se envían solo a la persona destinataria. **Los mensajes no están cifrados de extremo a extremo**: se almacenan en nuestros servidores. No leemos conversaciones de forma rutinaria; **solo podremos acceder** a un mensaje cuando la persona que lo recibió lo reporte, o cuando lo exija una autoridad competente `[PENDIENTE: confirmar con abogado y con el diseño final]`. Si una cuenta se elimina, los mensajes que envió pueden conservarse en la bandeja de las personas que los recibieron, mostrando «Usuario no encontrado».

**12. Seguridad infantil.** Prohibimos cualquier contenido de abuso o explotación sexual infantil. Lo retiramos cuando tengamos conocimiento real de él, suspendemos la cuenta y lo comunicaremos a las autoridades según la ley. Contacto: `[PENDIENTE: nombre y correo de la persona responsable]`. Normas completas: `[PENDIENTE: página pública propia para Google Play]`.

**13. Disponibilidad y responsabilidad.** THERS se ofrece «tal cual» y puede tener interrupciones. `[PENDIENTE: abogado — límites de responsabilidad válidos frente a consumidores; no se puede excluir lo que la ley no permite excluir]`.

**14. Pagos.** Actualmente **THERS no cobra ni tiene suscripciones**. Si se agregan, se informará antes y se actualizarán estos términos.

**15. Ley aplicable y contacto.** Estos términos se rigen por las leyes de **El Salvador**, **sin perjuicio de los derechos y obligaciones imperativos que correspondan a tu país de residencia**. `[PENDIENTE: abogado — fuero y resolución de conflictos]`. Contacto: `[PENDIENTE]`.

### D.2 Política de privacidad — BORRADOR NO PUBLICABLE

**Versión:** `[PENDIENTE]` · **Última actualización:** `[PENDIENTE]`

**1. Responsable del tratamiento.** `[PENDIENTE DE CONFIRMACIÓN: quién o quiénes]`, domicilio `[PENDIENTE]`, correo de privacidad `[PENDIENTE]`. THERS es el nombre del proyecto, no una sociedad registrada.

**2. Qué datos tratamos, para qué y con qué fundamento.**
> `[PENDIENTE: abogado — confirmar el fundamento de cada fila con los artículos de bases de licitud de la Ley; no los pude verificar]`

| Datos | Para qué | Fundamento (a confirmar) |
|---|---|---|
| Nombre, usuario, correo, teléfono y código de país, contraseña (guardada solo como hash), fecha de nacimiento | Crear y gestionar tu cuenta; comprobar la edad mínima | Prestarte el servicio que pides; obligación de comprobar edad |
| Foto, portada, biografía, ubicación y sitio web (opcionales) | Mostrar tu perfil | Tu consentimiento al ponerlos |
| Publicaciones, comentarios, me gusta, seguidos, menciones | Funcionamiento de la red | Prestarte el servicio |
| Mensajes privados (texto, emisor, receptor, fecha, estado de lectura) | Entregar la conversación | Prestarte el servicio |
| Preferencias de privacidad, palabras y temas silenciados, bloqueos | Aplicar tus decisiones | Prestarte el servicio |
| **Última conexión** | Mostrar actividad si tú lo permites | Tu preferencia (`show_activity_status`) |
| **IP y agente de usuario de tus sesiones** | Seguridad: mostrar tus dispositivos y avisarte de accesos nuevos | Seguridad de la cuenta; interés legítimo |
| Secreto de verificación en dos pasos y códigos de recuperación (hash) | Proteger tu cuenta | Tu consentimiento al activarla |
| Identificador de Google y tu correo de Google | «Continuar con Google» | Tu consentimiento al usarlo |
| Hash de IP o identificador | Frenar abusos (límite de intentos) | Seguridad |
| Reportes (texto reportado, motivo, quién reporta) | Moderar; proteger a la comunidad | Interés legítimo; seguridad |
| Archivo de exportación | Entregarte tus datos cuando lo pides | Tu solicitud |

No pedimos datos sensibles de forma expresa. Lo que escribas en tu biografía, publicaciones o mensajes puede contenerlos bajo tu responsabilidad.

**3. Quién recibe tus datos.**
| Proveedor | Para qué | Datos | Estado |
|---|---|---|---|
| Google (Sign-In) | Autenticación | Credencial, correo, nombre | Activo si eliges esa opción |
| **Google (fuentes)** | Cargar tipografías | IP y navegador de quien visita el sitio | Activo **[recomendado eliminar: C.6]** |
| Resend | Enviar correos | Correo, nombre, códigos; en avisos de acceso nuevo, dispositivo e IP | Activo `[PENDIENTE: país y retención]` |
| Cloudflare / Supabase / Render | Sitio, base de datos, servidor | Todos los datos | `[cuando se contraten]` |
| Autoridades | Orden legal | Lo exigido | Solo cuando la ley lo requiera |

**No vendemos tus datos ni los usamos para publicidad.** No usamos analítica ni rastreadores.

**4. Transferencias internacionales.** Los proveedores anteriores pueden tratar datos fuera de El Salvador. Región de los servidores: `[PENDIENTE]`. `[PENDIENTE: abogado — art. 44 de la Ley: transferencia solo a países con garantías equivalentes y con consentimiento previo]`.

**5. Cuánto tiempo conservamos los datos.**
| Dato | Plazo |
|---|---|
| Cuenta, contenido, mensajes | Mientras tengas la cuenta; al eliminarla se borran, salvo lo indicado abajo |
| Sesiones (IP y dispositivo) | Mientras tengas la cuenta `[PENDIENTE: el equipo debe definir un plazo máximo; hoy no se borran solas]` |
| Hash de IP para límite de intentos | 24 horas |
| Exportación | 7 días |
| Copias de seguridad | `[PENDIENTE]` (propuesta: hasta 7 días) |
| Reportes: copia del texto reportado | Solo mientras el reporte esté abierto |
| Mensajes que enviaste a otras personas | **Si eliminas tu cuenta, pueden conservarse en la bandeja de quien los recibió**, sin tu nombre («Usuario no encontrado») `[PENDIENTE: abogado]` |
| Registros del servidor | `[PENDIENTE]` |

**6. Tus derechos.** Puedes pedir **acceso, rectificación, cancelación/supresión, oposición, portabilidad, olvido y limitación** (la Ley los recoge, arts. 6 a 14 en la copia consultada). Escribe a `[PENDIENTE: correo de privacidad]`. La Ley fija un plazo de respuesta de **20 días hábiles**, prorrogable por otros 20 por causa justificada. Puedes **descargar tus datos** desde Configuración, y `[cuando esté disponible]` **eliminar tu cuenta** dentro de la app y en `[PENDIENTE: URL pública /eliminar-cuenta]`.

**7. Eliminar tu cuenta.** `[cuando esté disponible]` Te pediremos un código enviado a tu correo, que escribas tu correo y la palabra `DELETE`, y una última confirmación. Puedes **desactivarla** en lugar de eliminarla. La eliminación es definitiva y borra tu perfil, publicaciones, comentarios, me gusta, seguidos, sesiones e imágenes; **conservamos** lo señalado en el punto 5.

**8. Menores.** THERS es solo para personas de 18 años o más y no está dirigido a menores. Si crees que una persona menor de 18 años tiene una cuenta, escríbenos a `[PENDIENTE]` y la revisaremos. `[PENDIENTE: revisión jurídica de este apartado]`

**9. Seguridad.** Contraseñas con hash; sesiones de corta duración; verificación en dos pasos; conexiones cifradas `[PENDIENTE: confirmar HTTPS en producción]`. **Los mensajes no están cifrados de extremo a extremo.** Si ocurre una vulneración que afecte tus datos, la notificaremos a la autoridad y a las personas afectadas dentro de las **72 horas** siguientes a conocerla (art. 25 en la copia consultada).

**10. Mensajería.**
- **Chat privado (activo):** guardamos el texto y el historial en nuestros servidores. Los reportes pueden hacer que un moderador vea el mensaje reportado.
- **Tiempo real** `[cuando esté disponible]`: recibirás los mensajes sin recargar mientras estés conectado.
- **Notificaciones push** `[cuando esté disponible; hoy NO existen]`: guardaremos un identificador del dispositivo para avisarte. Por defecto **no mostrarán el contenido** del mensaje `[PENDIENTE: decisión de producto]`. Puedes silenciarlas. Pasan por Google (FCM) / Expo.
- **Correos transaccionales (activo):** código de registro, recuperación, cambio de contraseña y alerta de acceso nuevo.

**11. Autoridad y reclamos.** La autoridad de control es la **Agencia de Ciberseguridad del Estado** (art. 50 en la copia consultada). `[PENDIENTE: abogado — vía y procedimiento de reclamo vigentes]`.

**12. Cambios.** Si cambian de forma relevante, te avisaremos.

### D.3 Tecnologías similares a las cookies — BORRADOR NO PUBLICABLE

**THERS no usa cookies** ni rastreadores publicitarios o analíticos.

| Tecnología | Qué guarda | Para qué | Necesaria |
|---|---|---|---|
| Almacenamiento local del navegador (web) | tu sesión | Mantenerte conectado | **Sí** (se borra al cerrar sesión) |
| Almacenamiento local | tema (claro/oscuro) e idioma | Recordar tu elección | Preferencia que tú eliges |
| Almacenamiento local | si marcaste útil un artículo de ayuda; ajustes locales de perfil | Recordar tus acciones | Preferencia |
| Android Keystore (app móvil) | tu sesión | Mantenerte conectado de forma segura | **Sí** |
| Google (fuentes) | `[se eliminará si se alojan en el propio sitio]` | Cargar tipografía; Google recibe tu IP | — |

Como no usamos tecnologías no necesarias que requieran consentimiento, **no mostramos un banner de cookies**. Si algún día agregamos analítica o publicidad, te lo diremos y **pediremos tu consentimiento antes**. Puedes borrar el almacenamiento local desde los ajustes de tu navegador; tendrás que volver a iniciar sesión.

---

## E. Diferencias entre el producto actual y lo que exigirían los borradores

| # | Hoy | Lo que el borrador afirma o exige | Acción |
|---|---|---|---|
| 1 | **No se puede eliminar la cuenta** | Eliminar en la app y en una URL pública (Play lo exige) | Implementar ADR-031 |
| 2 | Edad mínima **13** en código | **15** | Cambiar `MIN_AGE_YEARS` (backend y Frontend) tras la revisión jurídica |
| 3 | La web y la app **no piden aceptar términos**; los enlaces a `/terms` y `/privacy` llevan a páginas «en construcción» | Aceptación **antes** de crear contenido | Fusionar fase 1 de ADR-032 y activar `TERMS_ACCEPTANCE_REQUIRED` junto con la casilla |
| 4 | No existen reportes en la interfaz ni moderación | Reportar, bloquear, advertir, suspender, apelar | ADR-032 fases 2 a 4 |
| 5 | **Sesiones con IP y agente de usuario sin plazo** | Un plazo máximo de conservación | Definir plazo y tarea de limpieza |
| 6 | **Google Fonts** envía la IP a Google | Evitar o declarar | Alojar las fuentes localmente |
| 7 | Chat por consulta periódica, **sin duplicados controlados**, **sin pantalla en móvil** | Tiempo real, recuperación al reconectar, sin duplicados | Ver C.4 |
| 8 | Tokens y copia del perfil en `localStorage` (web) | Declarado como necesario | Sin cambio inmediato; la web no usa refresh token |
| 9 | Resend sin dominio verificado | Correos desde dominio propio | ADR-018 |
| 10 | No hay página pública de **estándares contra la explotación infantil** ni contacto designado | Play lo exige a apps sociales | Redactar y publicar |
| 11 | No hay mecanismo de comentarios/contacto dentro de la app | Play lo exige (seguridad infantil) | Añadir enlace a soporte en la app |
| 12 | Mensajes de cuentas eliminadas: hoy se borran (FK `CASCADE`) | Se conservan como «Usuario no encontrado» | Migración `ON DELETE SET NULL` (ADR-031 §C) |

## F. Puntos que debe revisar un abogado salvadoreño antes del lanzamiento

1. **Edad y consentimiento de menores** (arts. 26 y 42 de la Ley; LEPINA y Código de Familia, **que no revisé**): validez de la edad de 15, si hace falta consentimiento de tutor y qué prueba conservar.
2. **Reforma del 2026-09-17**: confirmar publicación en el Diario Oficial, vigencia, decreto exacto y qué queda del art. 15 y del 51 (director de protección de datos).
3. **Operación sin entidad constituida**: quién responde personalmente por el tratamiento y por el contenido de terceros (**pendiente de confirmar**), y si conviene constituir una sociedad.
4. **Bases de licitud** de cada tratamiento (no las verifiqué en el texto).
5. **Transferencias internacionales** (art. 44, exige consentimiento previo y garantías equivalentes): Resend, Google, y la región de Render/Supabase.
6. **Conservación de mensajes de cuentas eliminadas** y su compatibilidad con supresión.
7. **Acceso a mensajes** por moderadores y por autoridades; requisitos de una orden.
8. **Contenido ilegal y CSAM**: obligaciones de denuncia y retención de evidencia en El Salvador.
9. **Cláusulas de responsabilidad, fuero y ley aplicable** frente a consumidores y a usuarios de otros países.
10. **Plazos de una notificación de brecha** (72 h, art. 25) y a quién se notifica (ACE, Fiscalía General, titulares).
11. **Aviso de privacidad**: contenido mínimo (art. 24) y forma de comunicarlo «por escrito al momento del consentimiento».
12. Cualquier **monetización futura**.

---

## Fuentes (consultadas el 2026-10-02)

**Ley de El Salvador** — *Decreto Legislativo n.º 144, Ley para la Protección de Datos Personales*, aprobado el 12-nov-2024, publicado en el Diario Oficial n.º 219, tomo 445, del 15-nov-2024; art. 64: vigencia ocho días después de la publicación.
- Texto con los artículos citados: [Informática Jurídica](https://www.informatica-juridica.com/ley/decreto-no-144-ley-para-la-proteccion-de-datos-personales-de-12-de-noviembre-de-2024/) (**copia secundaria**).
- Ejemplares oficiales que **no pude abrir**: [Asamblea Legislativa](https://www.asamblea.gob.sv/sites/default/files/documents/decretos/7A4FBD85-7E1B-46BE-9408-6FC549E53E00.pdf) (error de certificado) y [Diario Oficial vía Ministerio de Hacienda](https://transparencia.mh.gob.sv/downloads/pdf/700-UAIP-LY-2024-14993.pdf) (conexión cerrada). **Los números de artículo deben contrastarse con el texto oficial.**
- Fecha de aprobación y vigencia: [BLP Legal](https://blplegal.com/es/ley-para-la-proteccion-de-datos-personales-en-el-salvador/) (secundaria).
- **Reforma de septiembre de 2026** (arts. 15 y 17 derogados para el sector privado): [Infobae, 2026-09-17](https://www.infobae.com/el-salvador/2026/09/17/el-salvador-la-asamblea-legislativa-elimina-la-obligacion-del-delegado-de-proteccion-de-datos-para-las-empresas/) y [Contaportable](https://www.contaportable.com/reforma-ley-proteccion-datos-el-salvador/) — **ambas prensa; no encontré el decreto ni su publicación. Pendiente de revisión jurídica.**

**Google Play** (resúmenes de cada página, no texto íntegro):
- [Eliminación de cuentas](https://support.google.com/googleplay/android-developer/answer/13327111): ruta dentro de la app **y** recurso web; declarar la retención.
- [Contenido generado por usuarios](https://support.google.com/googleplay/android-developer/answer/9876937): aceptar términos antes de crear contenido, definir lo inaceptable, reportar y bloquear dentro de la app, moderar. (La página directa llegó truncada: se confirmó por el resultado de búsqueda sobre la misma URL.)
- [Privacidad y datos de usuario](https://support.google.com/googleplay/android-developer/answer/9888076): política en la ficha y en la app, formulario de seguridad de datos, eliminación de cuenta.
- [Estándares de seguridad infantil](https://support.google.com/googleplay/android-developer/answer/14747720): redes sociales y citas; estándares publicados, mecanismo de comentarios en la app, retirar CSAM, contacto designado. **No encontré fecha límite explícita.**

**Notificaciones push:** [Expo — configuración](https://docs.expo.dev/push-notifications/push-notifications-setup/), [credenciales FCM V1](https://docs.expo.dev/push-notifications/fcm-credentials/), [servicio de envío](https://docs.expo.dev/push-notifications/sending-notifications/).

**Código del repositorio:** `origin/develop` en `3cb1c6c`.
