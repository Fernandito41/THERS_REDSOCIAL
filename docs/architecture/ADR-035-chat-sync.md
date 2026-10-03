# ADR-035 — Sincronización del chat

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-035-chat-sync.md` |
| Fecha | 2026-10-02 |
| Estado | **PROPUESTO** — paginación, recuperación e idempotencia **implementadas**; el transporte en tiempo real **NO está elegido** |
| Relacionado | `ADR-013`, `ADR-014`, `ADR-018` (Render, Supabase), `ADR-029` |

## Implementado

- **Envío idempotente:** `messages.client_id` (único por remitente). Reenviar con el mismo `client_id` devuelve el mensaje original (`200`) y no duplica. Resiste dos envíos simultáneos (índice único + reintento de lectura). Los permisos y bloqueos se comprueban siempre.
- **Historial paginado:** `GET .../messages?limit=&before=` por **instante** (`created_at`), no por id, porque el borrado es duro. Cursores inclusivos; el cliente deduplica por `id`.
- **Recuperación:** `?after=<instante del último mensaje confirmado>` devuelve lo posterior, por páginas, sin huecos.
- **Cliente móvil:** consulta periódica **solo con la pantalla activa y la app en primer plano**, intervalo adaptativo (3 s hasta 12 s en silencio) y retroceso exponencial tras errores (hasta 30 s). Mensajes locales con estados «enviando» y «falló», reintento con el mismo `client_id`.
- Solo las dos personas acceden (la identidad sale del JWT) y se respetan los bloqueos (`404 «Usuario no encontrado»`).

## Qué es y qué no es

Es **consulta periódica (polling)**, no tiempo real. Los mensajes **no están cifrados de extremo a extremo**. El indicador «escribiendo» vive en memoria de **un** proceso del servidor y no funcionará con varios procesos; el cliente móvil todavía no lo usa. No hay confirmaciones de lectura en vivo.

## Transporte en tiempo real: pendiente de evaluación

No se elige ni se afirma una solución sin comprobar antes, con el despliegue real:

| Criterio | Qué hay que comprobar |
|---|---|
| Compatibilidad con Render | Si el plan admite conexiones largas, el límite de conexiones simultáneas y qué pasa en cada reinicio o despliegue |
| Servidor sincrónico | `gunicorn` con trabajadores sincrónicos se bloquea con una conexión abierta por usuario; exigiría hilos o `gevent` |
| Varios procesos | Un evento nacido en un proceso debe llegar a las conexiones de otro (bus compartido: coste y operación) |
| Recuperación de eventos | Cualquier transporte debe apoyarse en `?after=` (ya existe) para no perder mensajes |
| Consumo | Conexiones abiertas, batería del teléfono y coste del plan |
| Autorización | El servidor Flask debe seguir siendo la única autoridad sobre quién ve qué |

Candidatos a evaluar, sin preferencia decidida: SSE desde Flask, Flask-SocketIO, y un servicio gestionado (p. ej. el Realtime de Supabase, ya aceptado en `ADR-018`) usado solo como aviso «hay algo nuevo» tras el cual el cliente consulta por REST. **Bloqueo externo:** no hay entorno de staging ni cuentas contratadas para medir.

## Notificaciones push

Fase posterior y **complementaria**: avisan, no guardan ni entregan el historial. Con el contenido privado oculto por defecto (decisión de producto pendiente). Requieren `expo-notifications`, credenciales FCM y una tabla de tokens de dispositivo.
