# ADR-034 — Edad mínima de 18 años

| Campo | Valor |
|---|---|
| Documento | `docs/architecture/ADR-034-minimum-age-18.md` |
| Fecha | 2026-10-02 |
| Estado | **ACEPTADO** por decisión de producto del equipo (2026-10-02). Implementado en backend y web. La app móvil (rama `feature/mobile-feature-parity`) lleva su propia validación |
| Alcance | `backend/` (validación y compuerta), `Frontend/`, `mobile/` |

## Decisión

THERS es **solo para personas de 18 años cumplidos o más**, en la web y en Android. Sustituye al valor provisional de 13 años de `ADR-002` §3.

## Qué se implementó

- `MIN_AGE_YEARS = 18` en `domain/auth/validators.py`, `Frontend/.../dateUtils.js` y `mobile/.../age.ts`. La edad se calcula por **fecha completa** (año, mes y día); quien nació un 29 de febrero cumple el 1 de marzo en un año no bisiesto.
- El servidor valida en `POST /api/register` y en `PATCH /api/users/me` (completar perfil). Una cuenta de Google **no demuestra la edad**: nace sin fecha y sin perfil completo.
- **Compuerta de perfil completo** (`interfaces/profile_gate.py`): sin `profile_completed`, la API rechaza publicar, comentar, dar me gusta, seguir y escribir. Antes, la redirección a «Completar perfil» era solo de interfaz.
- Es la fecha que la persona **declara**. **No** se piden documentos ni hay proveedor de verificación: sería una decisión aparte. Los textos no deben llamarla «verificación».

## Cuentas existentes: estrategia (NO ejecutada)

No se borra, bloquea ni se inventa nada. `backend/scripts/audit_minimum_age.py` (solo lectura) cuenta tres categorías sin imprimir datos personales: `mayores_de_edad`, `menores_declarados` (fecha declarada < 18) y `sin_fecha` (cuentas de Google sin completar). Opciones para `menores_declarados`, que el equipo debe decidir con el número real:

| Opción | Consecuencia |
|---|---|
| A. Dejarlas como están | Sin fricción; mantiene menores de 18 en un servicio que dice ser +18 |
| B. Pedir confirmar la fecha al iniciar sesión | Respeta a quien se equivocó; quien miente puede repetir la mentira |
| C. Suspender hasta confirmar | Cumple la regla; **riesgo de pérdida de usuarios y de reclamos**; requiere comunicación y revisión legal |
| D. Eliminar | Irreversible; no recomendado sin aviso previo ni asesoría |

`sin_fecha` no se asume: la compuerta ya les impide actuar hasta completar el perfil.

## Límites y advertencias

- Restringir a 18+ **no elimina** las obligaciones de Google Play sobre seguridad infantil para apps sociales (estándares publicados, canal de comentarios en la app, contacto designado): se aplican con independencia de que haya menores. Ver `docs/LAUNCH_CHECKLIST.md`.
- Los textos legales siguen **pendientes de revisión jurídica**.
