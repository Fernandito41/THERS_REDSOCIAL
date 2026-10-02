# VALIDATION — Qué está probado y qué no, en la app Android de THERS

> Regla de este documento: se distinguen cuatro estados y **nunca se mezclan**
> (`THERS_PROMPT_CLAUDE_ANDROID.md` §11):
>
> 1. **código escrito** — existe en el repositorio.
> 2. **build compilado** — Gradle produjo un artefacto.
> 3. **prueba en dispositivo realizada** — se ejecutó en el Samsung A16 5G.
> 4. **integración externa verificada** — el servicio de terceros respondió de verdad.
>
> Un test con mocks no acredita una llamada, un correo ni una notificación real.
> Última actualización: 2026-10-01.

---

## 1. Estado global de la app móvil

| Estado | Resultado |
|---|---|
| Código escrito | **SÍ.** `mobile/` creada el 2026-10-01: Expo SDK 57 + RN 0.86.3 + TypeScript, Expo Router, login, perfil propio y logout contra la API real (§1.1) |
| Build compilado | **SÍ (2026-10-02).** `npm run android` (`expo run:android`) compiló con Gradle 9.3.1 + JDK 17 el APK debug de 92 MB (`arm64-v8a`), con módulos nativos y C++. Ver §1.3 por la trampa de rutas largas de Windows |
| Prueba en dispositivo | **SÍ, parcial (2026-10-02).** Probado en un **Motorola moto z3**, **no** en el Samsung A16 5G. Login, `/users/me`, SecureStore, persistencia, logout, fallo de red, `401` y caso `403` verificados (§1.3). Samsung A16 sin probar |
| Integración externa verificada | **Ninguna** (ver §4) |

### 1.1 Qué se verificó de `mobile/`, exactamente

| Verificación | Comando | Resultado |
|---|---|---|
| Tipos | `npx tsc --noEmit` | **0 errores** |
| Coherencia del proyecto Expo | `npx expo-doctor` | **21/21 checks passed** |
| Bundle de Android (prueba de que Metro resuelve los alias `@shared`/`@features`) | `npx expo export --platform android` | **OK** — `entry-*.hbc`, 2.7 MB |
| Versiones instaladas vs. las fijadas por `ADR-016` | inspección de `node_modules` | coinciden exactamente (`expo 57.0.26`, `react 19.2.3`, `react-native 0.86.3`, `expo-router 57.0.24`) |
| API alcanzable por la IP LAN que usará el teléfono | `curl http://192.168.1.69:5000/api/users/me` | `401` con el JSON esperado |
| Forma del error de credenciales que el cliente mapea | `curl -X POST .../api/login` con credenciales falsas | `401` · `{"msg":"Credenciales incorrectas"}` |

**Lo que estas verificaciones NO acreditan**, y conviene decirlo explícitamente:

- Que la app **arranque**. Un bundle que compila puede fallar en tiempo de ejecución.
- Que **SecureStore funcione**: es un módulo nativo, y no se ha ejecutado código nativo nunca.
- Que el **login real funcione**. No se completó ningún login contra una cuenta verificada.
- Que la **IP LAN sea alcanzable desde el teléfono**: el `curl` salió de la misma máquina, así que
  no atravesó el firewall. La regla del puerto 5000 sigue sin crearse
  (`ANDROID_SETUP.md` §5).
- Que el **teclado, el botón Atrás y las áreas seguras** se comporten bien: eso solo se ve en un
  dispositivo.

### 1.3 Validación en dispositivo físico (2026-10-02)

**`expo export --platform android` no equivale a ejecutar la app.** Solo valida el bundle de
JavaScript y que Metro resuelva los alias. Una build con Gradle + dispositivo físico valida además:
compilación nativa (Kotlin/C++/CMake), módulos nativos (SecureStore, reanimated, screens…), instalación
por ADB, SecureStore real, conectividad LAN y ejecución real. Antes de esta fecha solo se tenía lo primero.

Dispositivo: Motorola moto z3 (Android, `arm64-v8a`), por USB. API por Wi-Fi a `192.168.1.69:5000`;
Metro por túnel USB (`adb reverse tcp:8081`).

| Prueba | Estado | Evidencia |
|---|---|---|
| Build nativa | ✅ | `BUILD SUCCESSFUL in 15m 20s`; `app-debug.apk` 92 MB |
| Instalación y apertura | ✅ | `Installing …app-debug.apk` / `Opening exp+thers://…`; bundle servido (1421 módulos) |
| Teléfono → backend por LAN | ✅ | `curl` desde el propio teléfono (`192.168.1.52`) → `192.168.1.69:5000/api/users/me` = `401` JSON |
| Login con error | ✅ | credenciales de una cuenta sin contraseña (solo Google) → «Credenciales incorrectas» real del backend |
| Login correcto | ✅ | cuenta de pruebas con contraseña verificada y correo verificado; navega al perfil |
| SecureStore | ✅ | `SecureStore.xml` con una sola clave `key_v1-thers.access_token` (valor cifrado); sin email ni nombre en claro |
| `GET /api/users/me` | ✅ | respuesta `200` cacheada en el teléfono con sello `Date` del servidor; los campos de pantalla coinciden con la BD uno a uno |
| Persistencia | ✅ | app cerrada y reabierta (pid nuevo), sesión restaurada; el `Date` de `/users/me` avanzó |
| Logout | ✅ | `SecureStore.xml` queda `<map />`; tras cerrar y reabrir, login sin petición a `/users/me` |
| Fallo de red | ✅ | Wi-Fi apagado + refresco: mismo proceso, token intacto, sigue en el perfil; al volver el Wi-Fi, `/users/me` `200`. La alerta mostrada fue vista por el usuario, no capturada |
| `401` | ✅ (inferido) | tras la caducidad de 15 min, el refresco devolvió al login y el token se borró. El `401` en sí no quedó en ningún log: se deduce de la hora y de que el backend respondía con normalidad |
| `403` + `email_verified:false` | ✅ | cuenta de pruebas sin verificar (`qa.harness@example.invalid`, contraseña temporal puesta en la BD de desarrollo). `curl` → `403` con `{"email_verified": false}`; en el teléfono la app muestra el aviso propio de cuenta sin verificar y **no guarda token** (SecureStore vacío) |

**Defectos hallados en esta prueba:**

1. **Bug de la app, corregido.** `loadCurrentUser` trataba `GET /api/users/me` como un `User` plano; el
   contrato (`API_CONTRACT.md` §4.2) lo envuelve en `{"user": {...}}`. Tras **restaurar la sesión**
   la pantalla salía vacía («@», «Correo verificado: No»). No se veía justo después del login porque
   `POST /login` sí usa `data.user`. Corregido en `AuthContext.tsx` (`request<{ user: User }>`).
2. **Fuga menor, SIN corregir.** La caché HTTP de React Native (`cache/http-cache/`, almacenamiento
   privado de la app) guarda la respuesta de `/users/me` con el JSON del usuario, contra el criterio de
   `session.ts` de no guardarlo en disco. El JWT y `Authorization` **no** están ahí. Opciones:
   `Cache-Control: no-store` en respuestas autenticadas, o limpiar esa caché en logout.
3. **Observación de diseño, no probada.** En un arranque en frío **sin red**, `loadCurrentUser` deja
   `user = null` y la app muestra el login aunque el token siga en SecureStore: no se pierde la sesión,
   pero parece cerrada. Pendiente de decidir (ROADMAP).
4. **Backend:** con Resend sin dominio verificado, `POST /api/forgot-password` responde `500` para
   cualquier destinatario que no sea el dueño de la cuenta de Resend (`403` del proveedor). El código
   se crea igualmente. No se tocó.

### 1.2 Alcance deliberadamente excluido de `mobile/`

Implementado en el backend, **ausente en la app a propósito** (no es un olvido):

| Función | Por qué no está |
|---|---|
| Registro de cuenta | `POST /api/register` exige 8 campos + verificación por OTP (`ADR-011`). Desborda este hito |
| Recuperación de contraseña | flujo de 3 pasos (`ADR-010`) |
| "Continuar con Google" | necesita cliente OAuth de Android y prueba en dispositivo (ROADMAP fase 2) |
| Editar perfil / completar perfil | `PATCH /api/users/me` existe; la pantalla es fase 3 |
| Feed, posts, likes, comentarios, follows | fase 3 |
| Mensajes, notificaciones | fase 4 |
| Llamadas | fase 5 |

Ninguna de estas aparece como botón inerte en la interfaz: donde el usuario podría esperarlas, la
pantalla dice explícitamente que se hacen desde la web. Una función aparentada es peor que ausente.

## 2. Verificado de verdad (backend y web, 2026-10-01)

Todo lo de esta tabla se ejecutó en esta máquina y se comprobó su salida.

| Qué | Cómo | Resultado |
|---|---|---|
| Suite de integración del backend | `python -m pytest` (sin variables a mano) | **292 passed, 0 failed**, contra PostgreSQL 16 real en Docker, no mocks |
| Migraciones | `flask db current` / `flask db heads` | `a5c8e2d71f34 (head)` en `thers_dev` y en `thers_test` |
| Contenedor de base de datos | `docker compose ps` | `thers_postgres_dev` `Up (healthy)`, `0.0.0.0:5433->5432` |
| Arranque del backend | `python run.py` | sirviendo en `0.0.0.0:5000` |
| Rechazo sin credenciales | `curl /api/users/me` | `401` · `{"msg":"Falta el header de autorización"}` |
| Rechazo con token inválido | `curl -H "Authorization: Bearer basura"` | `401` · `{"msg":"Token inválido"}` |
| Formato de error global | `curl /api/no-existe` | `404` · `{"msg":"Recurso no encontrado"}` — JSON, nunca HTML |
| Expiración real del access token | `app.config["JWT_ACCESS_TOKEN_EXPIRES"]` | `0:15:00` — el default de la librería, no una decisión (ver `ADR-017`) |
| Build del Frontend web | `npm run build` | OK, 0 errores |
| Lint del Frontend web | `npm run lint` | **0 errores**, 3 warnings (ver §3) |
| Catálogo real de endpoints | `app.url_map` | 32 rutas |
| Fingerprint de la keystore de debug | `keytool -list -v` | obtenido; hace falta para el cliente OAuth de Android |

## 3. Warnings conocidos, no corregidos a propósito

`npm run lint` en `Frontend/` reporta 3 warnings de `react-hooks/exhaustive-deps`:

| Archivo | Línea | Dependencias faltantes |
|---|---|---|
| `src/app/layout/AppShell.jsx` | 97 | `t`, `toast` |
| `src/features/auth/components/GoogleSignInButton.jsx` | 85 | `onCredential`, `onError` |
| `src/features/auth/context/AuthContext.jsx` | 62 | `loadCurrentUser` |

Estaban **invisibles** hasta esta sesión: el proyecto tenía comentarios
`// eslint-disable-next-line react-hooks/exhaustive-deps` sin el plugin instalado, así que eslint
fallaba con «Definition for rule not found» en vez de evaluar la regla.

**No se corrigieron** por dos motivos: los tres archivos están entre los que el equipo tiene con
cambios sin commitear, y cambiar las dependencias de un `useEffect` altera cuándo se re-ejecuta —
es un cambio de comportamiento, no de estilo. Quedan asignables a quien tenga ese trabajo en curso.

## 4. Integraciones externas — ninguna verificada

| Integración | Lo que existe | Lo que NO está probado |
|---|---|---|
| **Google Sign-In** | `POST /api/auth/google` implementado, verificación criptográfica de ID Token (`google-auth`), `GOOGLE_CLIENT_ID` definido en ambos `.env` | Las 30 pruebas de `ADR-012` corren con **Google mockeado**. Nunca se completó un login real, ni en web ni en Android. El problema de origen que menciona el encargo **sigue sin verificar**. No existe cliente OAuth de Android registrado |
| **Resend (correo)** | Implementado; la suite usa `NullEmailSender` | No se envió ningún correo real en esta sesión, a propósito: registrar cuentas de prueba generaría correos a direcciones inventadas |
| **Push (FCM)** | Nada | No hay código, ni proyecto de Firebase, ni token de dispositivo, ni emisor en el backend |
| **Llamadas (LiveKit)** | Nada | No hay código ni servidor. Solo se verificó que `@livekit/react-native` 3.0.0 existe, está mantenido (publicado 2026-09-11) y declara peers coherentes |

**Que un proveedor acepte un envío no prueba que llegó o se mostró.** Ninguna de estas cuatro filas
puede darse por resuelta hasta que haya una prueba en dispositivo.

## 5. Criterios de aceptación de la primera entrega

- [x] **TypeScript y `expo-doctor` sin errores** — `tsc --noEmit` 0 errores, `expo-doctor` 21/21.
- [x] Compilación Android realizada: `mobile/android/app/build/outputs/apk/debug/app-debug.apk`
      (92 MB, debug, `arm64-v8a`, requiere Metro). Es el APK de **desarrollo**, no el de release.
- [x] Login válido obtiene sesión; credenciales erróneas muestran error; `/me` devuelve el usuario correcto.
- [x] Peticiones sin token o con token caducado reciben rechazo (`401` por caducidad inferido, §1.3).
- [x] Cerrar y reabrir la app respeta la estrategia de sesión; logout limpia datos privados
      (salvedad: la caché HTTP de RN conserva el JSON de `/users/me`, §1.3 defecto 2).
- [x] Desconexión no produce bucles de peticiones ni pantallas engañosas (probada con la sesión abierta;
      el arranque en frío sin red no se probó, §1.3 punto 3).
- [ ] Botón Atrás, teclado, áreas seguras y textos permiten completar el flujo. *No evaluado formalmente.*
- [ ] APK interna abre sin Metro, si se generó. *No generada: solo el APK debug.*
- [ ] Los checks de web y backend conservan su comportamiento. *`backend/` y `Frontend/` no se
      modificaron; no se re-ejecutó la suite en esta sesión.*

Pendiente además de los de arriba: repetir en el **Samsung A16 5G** (las pruebas se hicieron en un
moto z3).

**Limitación conocida que se arrastrará a la primera entrega:** mientras `ADR-017` no se implemente,
la sesión móvil muere a los 15 minutos. Es esperado, está documentado, y no debe reportarse como un
defecto descubierto durante las pruebas.

## 6. Entorno — qué falta para poder validar en el teléfono

Resuelto el 2026-10-02: JDK 17, `JAVA_HOME`, `ANDROID_HOME`, regla de firewall y un dispositivo con
depuración USB. Las trampas reales de esta máquina (rutas de más de 260 caracteres, perfil de red
Público, Metro) están en `docs/mobile/ANDROID_SETUP.md` §9.
