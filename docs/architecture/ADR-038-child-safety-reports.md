# ADR-038 — Seguridad infantil en los reportes

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-038-child-safety-reports.md` |
| Fecha | 2026-10-02 |
| Estado | **PROPUESTO** — implementado por encargo del propietario del proyecto; pendiente de la revisión del equipo (`HB-001` §11–12). **Sin commit.** Depende de `ADR-032` (fase 1, rama sin fusionar) |
| Relacionado | `ADR-032` (reportes y moderación), `ADR-027` (límites de uso), `ADR-031` (eliminación), `docs/legal/SEGURIDAD_INFANTIL_GOOGLE_PLAY.md` |

## Por qué existe

Google Play exige a las apps de redes sociales **estándares públicos contra la explotación y el abuso sexual infantil, un mecanismo de comentarios dentro de la app, la retirada de ese material cuando se tiene conocimiento real y un contacto designado**, **independientemente de que haya menores usando la app** (requisito verificado en la ayuda de Play Console, 2026-10-02). THERS es solo para mayores de 18, pero la obligación aplica igual.

## Cómo funcionaba el sistema de reportes antes (auditado)

- **Qué se puede denunciar:** publicación, comentario, mensaje (solo quien lo recibió) y cuenta. Un solo endpoint: `POST /api/reports`.
- **Motivo:** texto validado en la aplicación contra 9 valores (`domain/reports/kinds.py`), sin `ENUM` de PostgreSQL.
- **Estado:** `open`, `reviewing`, `actioned`, `dismissed`; en la fase 1 todo nace `open`.
- **Prioridad:** **no existía.**
- **Roles:** no existe `is_moderator` ni ninguna ruta de moderación.
- **UI:** la web **no tiene** pantalla de reportes. La app móvil sí (reportar publicación, comentario, mensaje y cuenta).
- **Pruebas:** 54 de reportes.

## Decisión

1. **Motivo nuevo `child_safety`** («Explotación o abuso de menores» / «Child exploitation or abuse»), en el mismo catálogo y el mismo endpoint. No hay un sistema paralelo. Se escribe en minúsculas, como los demás identificadores del catálogo (`self_harm`), en vez de `CHILD_SAFETY`.
2. **Disponible para los cuatro tipos de objetivo** que ya existen, con sus guardias de visibilidad intactas.
3. **Prioridad `critical` siempre**, calculada por el servidor (`priority_for_reason`). Columna `reports.priority` (`normal` | `critical`) con `CHECK`. El cliente **no puede** fijarla, subirla ni degradarla: el campo se ignora.
4. **Escalada, no duplicado.** El índice único (quien reporta, tipo, objetivo) devolvería el reporte viejo si alguien ya lo había reportado como spam y ahora como explotación de menores, y la prioridad se perdería. Por eso el reporte existente se **eleva** (motivo, prioridad, detalle) y se reabre si estaba descartado. **Nunca se degrada.**
5. **Límite de uso propio** (`REPORT_CHILD_SAFETY`: 30/hora, frente a los 10/hora de `REPORT_CREATE`) para que quien ya hizo reportes comunes no se quede sin poder denunciar algo grave. Sigue habiendo un tope.
6. **Mensaje al reportar:** la app muestra «Gracias por tu reporte. Este tipo de denuncia recibe revisión prioritaria por nuestro equipo de moderación.» **No** afirma que el contenido sea ilegal, que la persona sea culpable ni que se suspenda automáticamente.
7. **Página pública** `/child-safety` (español e inglés), sin sesión, enlazada desde el pie de página. Afirma solo lo que existe: **no** menciona detección automática, hash matching, IA ni acuerdos con organizaciones o autoridades.

## Migración

`b6e1d9a4c2f8_add_report_priority`. **Aditiva y no destructiva:** añade una columna con valor por defecto (los reportes existentes quedan `normal`), una restricción y un índice. No borra ni recrea nada. El motivo nuevo **no** la necesita.

## Qué NO hace este cambio

| Pendiente | Consecuencia |
|---|---|
| **Panel de moderación** y cola de revisión | La prioridad queda guardada y ordenable, pero **nadie la lee todavía**: sin esta pieza un reporte crítico solo se ve consultando la base |
| **Retirada administrativa** de contenido | Declarada en la página como capacidad de THERS, pero **no hay herramienta** para hacerlo |
| **Suspensión administrativa** de cuentas | Igual |
| **Aviso al equipo** cuando llega un reporte crítico | No hay notificación ni correo a `seguridadinfantil@`. Hoy habría que revisar la base |
| **Interfaz de reporte en la web** | No existe; la página indica cómo reportar **en la app** |
| **Reporte de contenido por correo** | El correo es solo un contacto; el mecanismo es el sistema interno |
| **Plazo de conservación** de reportes y evidencia | Sin decidir (propuesta de 12 meses) |
| **Detección automática** | Fuera de alcance y no se afirma |

## Riesgos

1. **La página promete una capacidad operativa que aún no existe** (revisión prioritaria, retirada inmediata, suspensión). Recomendación: **no declarar esta URL en Play Console hasta tener al menos el panel mínimo y un proceso de guardia**.
2. **Un reporte crítico puede quedar sin leer.** No hay alerta.
3. **Abuso del motivo:** alguien podría marcar todo como `child_safety` para saturar la cola. Mitiga el límite de 30/hora; la moderación futura deberá permitir descartarlo.
4. **Texto libre `details` (500 caracteres):** una persona podría pegar un enlace a material ilegal. El texto se guarda; la moderación futura debe tratarlo con cuidado.
5. **Reporte de mensajes:** solo quien los recibió puede reportarlos. Quien presencie un abuso entre terceros no puede.

## Verificado (2026-10-02)

44 pruebas nuevas contra PostgreSQL real (`tests/test_reports_child_safety.py`), más las 54 de reportes ya existentes. Se comprobó con **mutaciones** que las pruebas detectan (a) una prioridad que siempre sale `normal` y (b) la ausencia de escalada. Frontend: 19 pruebas (`node --test`, sin dependencias nuevas) y la página abierta en un Chrome sin cabeza y sin sesión, en español e inglés.
