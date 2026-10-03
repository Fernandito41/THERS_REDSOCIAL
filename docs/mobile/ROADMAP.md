# ROADMAP — App Android de THERS

> Hitos y **criterio de salida** de cada uno. Un hito no se cierra porque el código exista: se cierra
> cuando su criterio de salida está verificado (`docs/mobile/VALIDATION.md` define qué cuenta como
> verificado). Base: `ADR-016-mobile-stack.md` (ratificado 2026-10-01).
> Estado al 2026-10-01: **Fase 0 en curso.**

---

## Fase 0 — Entorno y decisiones (en curso)

| Ítem | Estado |
|---|---|
| `ADR-016` stack móvil | **RATIFICADO** 2026-10-01 |
| `ADR-017` política de sesión JWT | **ACEPTADO** 2026-10-01; backend y móvil **implementados y verificados en dispositivo** 2026-10-02 (pendiente de merge) |
| Base de datos, migraciones, backend sirviendo | **VERIFICADO** |
| Suite de backend verde (292/292) | **VERIFICADO** |
| Lint del Frontend sin errores | **VERIFICADO** |
| `platforms/android-36` + NDK 27.1.12297006 | instalados en esta sesión |
| JDK 17, `JAVA_HOME`, `ANDROID_HOME`, firewall | **RESUELTO** 2026-10-02 |
| Dispositivo conectado | **RESUELTO** 2026-10-02 (moto z3; el Samsung A16 5G sigue sin probarse) |
| Consolidar `backend/.venv` vs `backend/venv` | **HECHO** — `.venv` eliminado; `backend/venv` es el canónico (`CLAUDE.md` §11) |

**Criterio de salida:** `npx expo-doctor` y una compilación Gradle de prueba corren en esta máquina, y
`adb devices` lista el Samsung A16 5G.

## Fase 1 — Base móvil y sesión (código completo, sin validar en dispositivo)

Crear `mobile/` (Expo SDK 57 + RN 0.86.3 + TypeScript), navegación mínima con Expo Router, login,
perfil propio y logout contra la API real. Tokens en SecureStore, nunca en AsyncStorage. Development
build con `expo-dev-client` — **Expo Go no vale como validación** de integraciones nativas.

Estado al 2026-10-01:

| Ítem | Estado |
|---|---|
| `mobile/` creada con las versiones de `ADR-016` | **HECHO** |
| Expo Router + layout raíz + puerta de sesión | **HECHO** |
| Login contra `POST /api/login`, con el caso `403`/`email_verified` de `ADR-011` | **HECHO** |
| Perfil propio desde `GET /api/users/me` (datos reales, nada inventado) | **HECHO** |
| Logout local + limpieza de SecureStore | **HECHO** |
| Estados de carga, error, desconexión y sesión vencida | **HECHO** |
| `EXPO_PUBLIC_API_URL` + `.env.example` sin secretos | **HECHO** |
| `expo-dev-client` instalado | **HECHO** |
| Typecheck, `expo-doctor`, bundle de Android | **VERIFICADO** |
| **Build nativa e instalación en el teléfono** | **VERIFICADO** 2026-10-02 (moto z3) |
| Login, `/users/me`, SecureStore, persistencia, logout, fallo de red y `401` en dispositivo | **VERIFICADO** (`VALIDATION.md` §1.3; el `401` por inferencia) |
| Caso `403` + `email_verified:false` en dispositivo | **VERIFICADO** 2026-10-02 (aviso propio, sin token guardado) |
| Repetir en el **Samsung A16 5G** | **PENDIENTE** |
| Caché HTTP de RN guarda el JSON de `/users/me` | **CERRADO** 2026-10-02 — `Cache-Control: no-store`, verificado en el teléfono |
| Login con 2FA en la app (segundo paso: TOTP o código de recuperación) | **VERIFICADO** 2026-10-02 (`VALIDATION.md` §1.3). Configurar la 2FA sigue siendo solo de la web |
| Arranque en frío sin red | **CERRADO** 2026-10-02 — pantalla «Sin conexión» con *Reintentar*; la sesión no se cierra |
| Refresh token (renovación automática, arranque en frío, logout del servidor) | **VERIFICADO** 2026-10-02 (`VALIDATION.md` §1.3) |
| **APK interna con el bundle incluido** | **PENDIENTE** |

**Criterio de salida (casi cumplido):** la primera pantalla autenticada muestra datos reales de
`GET /api/users/me` corriendo en un teléfono real — **cumplido en un moto z3**, no aún en el Samsung
A16 5G. De los nueve criterios de `VALIDATION.md` §5, cinco están marcados; faltan Atrás/teclado/áreas
seguras, la APK interna sin Metro y la re-ejecución de los checks de backend y web.

**Dependencia:** `ADR-017` ya está implementado (backend y móvil), así que la sesión ya no muere a los
15 minutos, pendiente de que se mergeen las ramas.

## Fase 1b — Refresh token (`ADR-017`)

Implementar el refresh rotativo con revocación en el backend y adoptarlo en `mobile/`. Puede ir en
paralelo a la Fase 1 porque no toca ninguna pantalla.

**Criterio de salida:** las cinco pruebas obligatorias de `ADR-017` §4.8 pasan, el contrato está en
`API_CONTRACT.md` el mismo día del PR (`HB-001` §15.1), y la app sobrevive un cierre y reapertura
pasados más de 15 minutos sin pedir contraseña.

## Fase 2 — Cerrar riesgos de arquitectura antes de construir pantallas

Pruebas pequeñas y desechables de las tres integraciones que hoy son humo:

1. **Google en Android** — confirmar la hipótesis de que el backend no necesita cambios (el ID Token
   pedido con el Web client ID como `serverClientId` conserva la `aud` que el verificador exige).
   Requiere el cliente OAuth de Android con el SHA-1 de debug.
2. **Push FCM** — token nativo vía `expo-notifications`, emisor en el backend, registro de
   dispositivo atado a usuario autenticado y desvinculación al cambiar de cuenta.
3. **LiveKit** — audio/vídeo entre **dos** dispositivos, con development build.

**Criterio de salida:** las tres probadas en dispositivo real, o descartadas con una razón escrita.
Para las llamadas se distinguen explícitamente cuatro capacidades distintas: entrar a una sala con la
app abierta · mantener audio en segundo plano o con pantalla bloqueada · recibir y aceptar con la app
inactiva · recuperarse de cambios de red y permisos denegados. **Probar la primera no acredita las
otras tres.**

## Fase 3 — Feed, perfiles y publicaciones

Paginación y caché (TanStack Query cuando aporte valor), publicaciones con imagen vía
`expo-image-picker`, límites de subida y permisos. El backend ya tiene `POST`/`GET /api/posts`,
likes, comentarios, follows y media de perfil.

**Hueco de contrato conocido:** `API_CONTRACT.md` documenta la paginación como pendiente y
`GET /api/posts` es un **feed global** sin filtrar por seguidos (`ADR-007` §No objetivos). Ambas son
decisiones de producto que deben resolverse antes o durante esta fase, no improvisarse en el cliente.

**Criterio de salida:** feed con datos reales, paginado, medido en el Samsung A16 (carga, memoria,
fluidez). Ninguna biblioteca de optimización se instala sin un problema observado primero.

## Fase 4 — Chat

El backend es **polling HTTP** (4 s de hilo, 2 s de «escribiendo»), sin Flask-SocketIO.

**Decisión pendiente antes de empezar esta fase:** en Android el polling no sobrevive el segundo
plano (Doze). Las opciones son chat solo con la app abierta + push para el resto, o cambiar el
transporte del backend. Es una decisión de producto que necesita su propio ADR; no se resuelve dentro
de la implementación del cliente (`CLAUDE.md` §6).

Nota adicional: el estado de «escribiendo» vive en memoria del proceso del backend (`ADR-014`), así
que no sobrevive un reinicio ni funciona con varios workers.

**Criterio de salida:** historial persistente, reconexión, sin mensajes duplicados, lista eficiente
y notificación cuando la app no está activa.

## Fase 5 — Llamadas completas

Ciclo de vida completo: invitar, aceptar, rechazar, cancelar, ocupado, finalizar. Servicios Android,
permisos, notificación de llamada, gestión de audio y, si hace falta,
Telecom/ConnectionService. Flask autoriza salas y emite credenciales limitadas — **la app nunca
recibe secretos del proveedor**.

**Criterio de salida:** llamada entre dos dispositivos en **redes distintas** (una prueba en el mismo
Wi-Fi no acredita nada general), con costes de desarrollo, medios y transferencia estimados por
separado. No se promete cifrado de extremo a extremo ni llamadas ilimitadas sin haberlo implementado
y validado.

## Fase 6 — Optimización y publicación

Medición en dispositivo, APK interna con el bundle incluido, y preparación de la publicación (AAB,
keystore de release fuera del control de versiones, SHA-1 de release en Google Cloud).

**Criterio de salida:** la APK interna abre sin Metro, y está documentado qué funciones siguen
necesitando el servidor.

---

## Reglas que atraviesan todas las fases

- Cada endpoint nuevo se documenta en `API_CONTRACT.md` **el mismo día del PR** (`HB-001` §15.1).
- Cada decisión de impacto medio/alto es un ADR **antes** de implementarse, no después.
- No se contratan servicios, no se publica, no se migran datos de producción y no se cambian dominios
  como parte de estas fases.
- `Frontend/`, `backend/` y `handbook/` conservan su comportamiento: los checks de cada paquete
  afectado se ejecutan en cada cambio.
- Ninguna fase se declara cerrada con «código escrito»: hace falta su criterio de salida verificado.
