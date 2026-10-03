# ADR-037 — Conservación de datos técnicos (90 días)

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-037-data-retention.md` |
| Fecha | 2026-10-02 |
| Estado | **ACEPTADO** el plazo de 90 días (decisión del equipo, 2026-10-02). **Implementado y probado en el backend, sin commit**. Puntos abiertos al final |
| Relacionado | `ADR-017`, `ADR-025` (sesiones), `ADR-027` (rate limiting), `ADR-031` (eliminación), `docs/legal/` |

## Por qué existe

La política de privacidad debe decir cuánto tiempo se conservan los datos, y **lo que dice debe ser lo que el sistema hace**. Antes de este ADR ningún dato de sesión se borraba nunca (verificado: ninguna función de borrado por antigüedad en los repositorios de sesiones y tokens). Las sesiones guardan **la IP y el agente de usuario** de cada acceso.

## Decisión

Los datos de sesión se conservan **90 días**. Una constante (`domain/retention/policy.py`, `SESSION_RETENTION_DAYS = 90`), no una variable de entorno: es una regla de negocio y debe coincidir con el texto legal.

| Dato | Se borra cuando |
|---|---|
| `sessions` (IP, agente de usuario, fechas) | sin uso hace más de 90 días, **o** cerrada hace más de 90 días |
| `refresh_tokens` | creado hace más de 90 días (vale 30) |
| `password_reset_tokens`, `email_verification_tokens` | creados hace más de 90 días (solo guardan el hash del código) |
| `rate_limit_buckets` | ya se borraban a las 24 h (`ADR-027`); sin cambio |
| `data_exports` | ya vencían a los 7 días (`ADR-028`); sin cambio |

**No se toca:** cuentas, contenido de las personas ni sesiones vigentes y usadas recientemente. Una sesión abierta hace un año pero usada ayer **se conserva**.

## Cómo se ejecuta

1. **`backend/scripts/purge_expired_data.py`**: camino principal, pensado para un trabajo programado diario (Cron Job de Render). Imprime **solo conteos**, nunca IPs ni correos.
2. **Disparo oportunista** (`interfaces/retention_trigger.py`): una de cada 50 sesiones iniciadas aprovecha para limpiar. **Nunca falla un inicio de sesión.** Es una red de seguridad por si nadie configura el trabajo programado, el mismo criterio que la purga de `ADR-027`.

## Verificado (2026-10-02)

14 pruebas contra PostgreSQL real (`tests/test_retention.py`): se borra lo vencido, el límite exacto de 90 días, sesión cerrada (el plazo corre desde que se cerró), tokens y códigos, **y lo que no se debe borrar** (cuentas, sesión usada ayer aunque sea antigua), que ejecutarlo dos veces es inocuo, que no devuelve datos personales, que el script solo imprime conteos y que un fallo de la limpieza no rompe el inicio de sesión. Pasan junto con las 71 pruebas de sesiones y tokens ya existentes.

## Qué NO cubre (abierto)

| Tema | Situación |
|---|---|
| **Registros del servidor** (Render, Flask/gunicorn) | **No verificado.** El servidor de desarrollo imprime la IP en cada petición. En producción depende de la configuración de `gunicorn` y de la retención de registros de Render. `[PENDIENTE al desplegar]` |
| **Copias de seguridad** | Supabase (Pro) conserva copias diarias 7 días (`ADR-018`); los datos borrados siguen en ellas hasta que caduquen. Hay que declararlo |
| **Registros de seguridad con otro plazo** (fraude, ataques, abuso grave) | No existe esa tabla todavía. El equipo propuso conservarlos más de 90 días cuando una investigación lo exija; falta definir **qué** se conserva y **cuánto** |
| **Reportes y evidencias tras eliminar la cuenta** | Propuesta: 12 meses, salvo obligación legal. **Sin decidir ni implementar** (`ADR-032` guarda hoy el texto reportado solo mientras el reporte está abierto) |
| **Disparo programado** | Hay que crear el Cron Job en Render al desplegar |
