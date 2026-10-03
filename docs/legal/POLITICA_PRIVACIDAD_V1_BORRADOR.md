# Política de privacidad de THERS Social Network — V1 — BORRADOR NO PUBLICABLE

> **NO PUBLICABLE** mientras tenga `[PENDIENTE]`. Sin revisión de un abogado salvadoreño. No declara
> cumplimiento legal. Describe **solo lo que la versión 1 publicada realmente hace**: lo planeado
> (fotos, vídeo, audio, llamadas, ubicación, contactos, grupos, notificaciones push, Firebase,
> Sentry, IA) **no aparece aquí** y se agregará, junto con la actualización de esta política y de la
> declaración «Seguridad de los datos» de Google Play, **antes** de publicar la versión que lo incluya.
> Redactado el 2026-10-02. Cada dato fue contrastado con el código (ver `ESTADO_V1_Y_PREGUNTAS.md`).

**Versión:** `[PENDIENTE: fecha de publicación]`

## 1. Quién es responsable
THERS Social Network («THERS») es un proyecto operado desde El Salvador por una persona natural. **No es una sociedad constituida.**
- Responsable legal: `[PENDIENTE DE CONFIRMAR: nombre completo; decidir si se publica antes de la consulta con el abogado]`.
- Domicilio para notificaciones: `[PENDIENTE DE DEFINIR]`.
- Responsable interno de las solicitudes de privacidad: **Diego Medina**, en `privacidad@thersweb.com`.

## 2. Qué datos recopilamos
**Cuenta:** nombre, nombre de usuario, correo, teléfono con código de país, **fecha de nacimiento que tú declaras** (no la verificamos con documentos) y la contraseña, que **nunca guardamos en claro** (solo un hash irreversible).
**Si entras con Google:** recibimos tu correo, tu nombre, si Google verificó ese correo y un identificador de tu cuenta de Google. **No recibimos ni guardamos tu foto de Google.**
**Perfil (opcional):** biografía, ubicación escrita por ti, sitio web, foto y portada que tú subas.
**Contenido que creas:** publicaciones de texto, comentarios, «me gusta», a quién sigues y quién te sigue, menciones.
**Mensajes:** mensajes privados de texto entre dos personas, con fecha y estado de lectura.
**Preferencias:** cuenta pública o privada, quién puede escribirte o mencionarte, contenido sensible, palabras silenciadas, cuentas bloqueadas.
**Seguridad de tu cuenta:** sesiones abiertas (con la **dirección IP** y el **agente de usuario** del dispositivo o navegador, que puede incluir su modelo), códigos de verificación (solo su hash), y si activas la verificación en dos pasos, su secreto y códigos de recuperación (hash).
**Reportes:** si reportas contenido, guardamos el reporte y el texto reportado.
**Uso técnico:** un contador por IP, con la IP convertida en un código irreversible, para frenar el abuso.

**No recopilamos:** ubicación del dispositivo, contactos, cámara, micrófono, datos de pago ni publicidad. La app no pide esos permisos.

## 3. Para qué los usamos
| Finalidad | Datos |
|---|---|
| Crear y mantener tu cuenta, comprobar que eres mayor de 18 años | Cuenta, fecha de nacimiento |
| Mostrar tu perfil y tu contenido a quien tú permitas | Perfil, contenido, preferencias |
| Entregar tus mensajes | Mensajes |
| Proteger tu cuenta y avisarte de accesos nuevos | Sesiones, códigos, verificación en dos pasos |
| Frenar abusos y fraude | Contador por IP, sesiones |
| Moderar contenido y proteger a la comunidad | Reportes, contenido reportado |
| Enviarte correos del servicio (códigos y avisos), nunca publicidad | Correo, nombre |

No vendemos tus datos y no los usamos para publicidad.

## 4. Fundamento de cada tratamiento
`[PENDIENTE: abogado — asociar cada finalidad a una base legal de la Ley para la Protección de Datos Personales (Decreto 144/2024). No se verificaron en el texto oficial los artículos de bases de licitud.]` Propuesta de trabajo: ejecución del servicio que pides; tu consentimiento (perfil, Google, verificación en dos pasos); seguridad y prevención del abuso.

## 5. Quién más recibe tus datos
| Proveedor | Para qué | Qué datos | Dónde |
|---|---|---|---|
| **Supabase** | Base de datos y archivos | Todos los datos de la cuenta y el contenido | **Virginia, EE. UU.** |
| **Render** | Servidor de la aplicación | Todo lo que pasa por el servidor | `[PENDIENTE: región]` |
| **Cloudflare** | Dominio, DNS, alojamiento de la web y reenvío del correo de soporte | Tráfico de la web (IP, navegador); correos que escribas a nuestras direcciones | `[PENDIENTE: confirmar]` |
| **Resend** | Enviar correos del servicio | Tu correo, tu nombre y el contenido del correo (código o aviso; en el aviso de acceso nuevo, el dispositivo y la IP) | EE. UU. `[PENDIENTE: confirmar]` |
| **Google** | «Continuar con Google» y fuentes tipográficas de la web | Credencial de Google; la IP y el navegador de quien visita la web | EE. UU. |
| **Expo / EAS** | Compilar la app | Ninguno de tus datos (solo el código) | — |

Las autoridades solo recibirán datos cuando la ley lo exija. `[PENDIENTE: abogado — requisitos]`

**Analítica y protección web.** Google Analytics, Cloudflare Analytics y Turnstile **no están implementados** y por tanto **no se mencionan como activos**. Si se agregan al lanzamiento, esta sección y la de almacenamiento del dispositivo deben actualizarse **antes**, y Google Analytics probablemente exigiría un aviso de consentimiento.

## 6. Transferencias internacionales
Tus datos se tratan en servidores de **Estados Unidos** (Supabase y, probablemente, Render y Resend). `[PENDIENTE: abogado — art. 44 de la Ley (garantías equivalentes y consentimiento previo) y la mención «sin perjuicio de normas imperativas de otros países».]`

## 7. Cuánto tiempo conservamos los datos
| Dato | Plazo |
|---|---|
| Cuenta, perfil, contenido, mensajes | Mientras tengas la cuenta; se eliminan cuando la eliminas |
| **Sesiones** (IP, agente de usuario) | **90 días** desde el último uso o desde que se cierran |
| Tokens de renovación y códigos de un solo uso (hash) | Válidos 30 días y 10 minutos respectivamente; las filas se borran a los 90 días |
| Contador por IP | 24 horas |
| Archivo de descarga de tus datos | 7 días |
| **Reportes y su evidencia** | `[PENDIENTE: propuesta de 12 meses tras eliminar la cuenta, salvo obligación legal; sin decidir]` |
| **Registros de seguridad** por fraude, ataques o abuso grave | `[PENDIENTE: pueden conservarse más de 90 días si una investigación lo exige; falta definir qué y cuánto]` |
| **Copias de seguridad** del proveedor | `[PENDIENTE: hasta 7 días con el plan previsto; confirmar al contratar]` |
| **Registros del servidor** | `[PENDIENTE: depende de la configuración en producción]` |

## 8. Seguridad
- **Contraseñas:** hash irreversible con **scrypt** (parámetros 32768:8:1); nunca se guarda la contraseña original.
- **Conexiones:** HTTPS/TLS `[PENDIENTE: confirmar al desplegar]`.
- **Sesiones** de 15 minutos con renovación; códigos de 6 dígitos que vencen a los **10 minutos**, con **límite de intentos**.
- Verificación en dos pasos opcional.
- **Los mensajes privados NO están cifrados de extremo a extremo:** se almacenan en nuestros servidores.
- Si ocurre una vulneración que afecte tus datos, la notificaremos a la autoridad y a las personas afectadas dentro de las **72 horas** siguientes a conocerla (art. 25, copia consultada).

## 9. Tus derechos
Puedes pedir acceso, rectificación, supresión, oposición, portabilidad y limitación escribiendo a **privacidad@thersweb.com**. Objetivo interno de respuesta: **15 días hábiles** `[PENDIENTE: sujeto a revisión jurídica; la Ley fija 20 días hábiles prorrogables]`. Puedes descargar tus datos desde Configuración.

## 10. Eliminar tu cuenta
Dentro de la app (Configuración → Cuenta → Eliminar cuenta) o en **https://thersweb.com/eliminar-cuenta**. Te pedimos un código enviado a tu correo, que escribas tu correo y la palabra `DELETE`, y una última confirmación. **Es definitiva.** Se eliminan tu perfil, publicaciones, comentarios, «me gusta», seguidores y seguidos, sesiones, notificaciones, archivos y **tus mensajes, tanto los enviados como los recibidos**. Quienes hablaban contigo dejarán de encontrarte.
**Puede quedar:** copias de seguridad del proveedor hasta que caduquen, y `[PENDIENTE: reportes y registros de seguridad, según el apartado 7]`.

## 11. Menores de edad
THERS es **exclusivamente para personas de 18 años o más**. Al crear tu cuenta declaras tu fecha de nacimiento y que cumples ese requisito. No la verificamos con documentos. Si tenemos motivos razonables para creer que una cuenta pertenece a una persona menor de 18 años, podremos restringirla y pedir información adicional; si la edad no puede acreditarse, la cuenta podrá ser eliminada. `[PENDIENTE: el procedimiento de verificación de edad no está definido ni implementado; no prometer más hasta decidirlo.]`
Si crees que un menor tiene una cuenta, escríbenos a **seguridadinfantil@thersweb.com**.

## 12. Cambios a esta política
Si cambia de forma relevante, te avisaremos antes de que se aplique. Agregar una función que trate datos nuevos (por ejemplo, fotos, ubicación o llamadas) requiere actualizar esta política **antes** de publicarla.

## 13. Contacto
- Privacidad: **privacidad@thersweb.com**
- Soporte: **soporte@thersweb.com**
- Seguridad: **seguridad@thersweb.com**
- Seguridad infantil: **seguridadinfantil@thersweb.com**
- Apelaciones: **apelaciones@thersweb.com**
- Autoridad de control: Agencia de Ciberseguridad del Estado `[PENDIENTE: abogado — vía de reclamo]`.
