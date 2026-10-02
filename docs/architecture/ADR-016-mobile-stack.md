# ADR-016 — Stack de la aplicación Android de THERS

- **Estado:** **`RATIFICADO`** por el Comité Técnico (`HB-001` §11–12) el **2026-10-01**.
  Ninguna línea de código móvil se escribió todavía: la ratificación autoriza crear `mobile/`, no
  da por hecha ninguna implementación.
- **Fecha:** 2026-10-01
- **Contexto de origen:** `THERS_PROMPT_CLAUDE_ANDROID.md` v2.0 (raíz del repositorio — fuera de
  `/docs`, por lo tanto informativo y no autoritativo, `CLAUDE.md` §4.5).
- **Evidencia de respaldo:** `docs/mobile/READINESS.md` (auditoría del 2026-10-01).

---

## 1. Decisión propuesta

Adoptar **React Native + Expo (SDK 57) + TypeScript** en una nueva aplicación `mobile/`,
independiente de `Frontend/`, `backend/` y `handbook/` (`CLAUDE.md` §2: sin código compartido, sin
`node_modules` compartidos, lockfile propio).

La recomendación del documento v2.0 **se confirma**, con dos matices que ese documento no podía
conocer porque no había auditado el repositorio (§3.1 y §4).

### 1.1 Condición resuelta en la ratificación

Esta decisión dependía de un único factor: si las llamadas de audio/vídeo siguen en el alcance del
producto. Sin llamadas, Capacitor habría sido la opción correcta (§3.1).

**Resuelto el 2026-10-01: el equipo confirma que las llamadas siguen en el roadmap.** Con eso la
asimetría de §2.3 aplica y la decisión queda firme, no condicional. Si en el futuro las llamadas se
retiraran del alcance, este ADR debería revisarse (§7).

### 1.2 Decisiones acompañantes tomadas en la misma ratificación

| Punto | Decisión | Dónde vive |
|---|---|---|
| Llamadas en el alcance | **Sí** | este ADR, §1.1 |
| TypeScript en `mobile/` | **Sí**, se mantiene | este ADR, §4 |
| Política de sesión JWT | **Refresh token rotativo** | `ADR-017-jwt-session-policy.md` |

---

## 2. Por qué, con evidencia

### 2.1 Continuidad del equipo con React (a favor, verificado)

El template oficial `expo-template-blank-typescript` pinea `react 19.2.3`; `Frontend/package.json`
declara `react ^19.2.4`. **Misma línea de React**: hooks, contexto, patrones de estado y el modelo
mental se conservan. El equipo no aprende un lenguaje nuevo (a diferencia de Flutter o Kotlin).

### 2.2 Lo que se reutiliza es real, pero modesto (verificado)

De los 39 módulos `.js` de `Frontend/src`, **33 son puros** y se portan sin cambios: validadores de
registro, utilidades de fecha, `maskEmail`, fuerza de contraseña, `formatRelativeTime`,
`mapNotification`, el sistema completo de i18n (`translate.js` + `locales/{es,en}.json`), búsqueda
de ayuda. Más `tokens.css`: **211 custom properties** que son valores planos, portables a un módulo
de constantes TypeScript.

**Los 120 archivos `.jsx` se reescriben.** React Native no convierte DOM + Tailwind en vistas
nativas. Ese es el coste dominante de esta decisión y se asume con los ojos abiertos.

### 2.3 El factor decisivo: las llamadas (verificado como asimetría real)

`@livekit/react-native` 3.0.0, publicado el 2026-09-11, con mantenimiento activo y peers coherentes
(`livekit-client ^2.19.0`, `@livekit/react-native-webrtc ^144.2.0`, que existe). LiveKit documenta
configuración para Expo con development build.

Para Capacitor **no existe un plugin oficial de LiveKit**: habría que usar el SDK web dentro del
WebView de Android, donde el WebView en segundo plano se suspende y no hay camino hacia
Telecom/ConnectionService. «Entrar a una sala con la app abierta» sería alcanzable; «recibir una
llamada con la pantalla bloqueada» no, sin escribir el módulo nativo igualmente.

Esa asimetría es comprobable y específica de la única función del roadmap que todavía no existe en
ninguna forma en el backend.

### 2.4 El producto va a crecer hacia multimedia y listas largas

El dispositivo de prueba es un Samsung A16 5G (gama media-baja). Feed con imágenes y vídeo,
historial de chat y perfiles con portada se comportan mejor con listas y reproductores nativos que
dentro de un WebView. Es un argumento de dirección, no una medición: **no se midió nada en el
dispositivo** y no se debe presentar como benchmark.

---

## 3. Alternativas — revisión con la evidencia del repositorio

| Alternativa | Veredicto tras auditar | Cambio respecto del documento v2.0 |
|---|---|---|
| **React Native + Expo** | **Elegida**, condicional (§1.1) | Confirmada |
| **React web + Capacitor** | **Segunda opción, más fuerte de lo que el documento v2.0 reconoce** | **Corrección material** (ver §3.1) |
| RN con proyectos nativos manuales | Sin justificación hoy; Expo no impide código nativo (CNG + config plugins) | Sin cambios |
| Flutter | Lenguaje nuevo + reescritura total de UI, sin ventaja comprobada para este equipo | Sin cambios |
| Kotlin + Jetpack Compose | UI separada del conocimiento React del equipo de 4 personas | Sin cambios |
| Kotlin Multiplatform | No reaprovecha la UI React; agrega tecnología sin necesidad multiplataforma | Sin cambios |
| PWA | No es base para llamadas con integración nativa profunda | Sin cambios |

### 3.1 Corrección sobre Capacitor

El documento v2.0 §3 lo describe como «mejor alternativa si domina la rapidez y la web móvil ya es
adecuada». La auditoría muestra que **la web móvil ya es adecuada**: existen
`Frontend/src/app/layout/thers/MobileNav.jsx` y `MobileDrawer.jsx`, la `Sidebar` está oculta bajo
`lg:`, y hay 137 usos de breakpoints responsive en los `.jsx`. El shell móvil no es una tarea
pendiente: está hecho.

Es decir, la condición que el propio documento pone para preferir Capacitor **se cumple**, y su
coste de adaptación de UI es mucho menor que el de React Native. Si el criterio fuera «primera APK
en el menor tiempo», Capacitor ganaría con la evidencia a la vista.

Se mantiene React Native porque el criterio elegido no es la primera APK sino el coste total del
roadmap (§2.3, §2.4). Pero conviene que el equipo decida esto sabiendo que **está pagando una
reescritura de 120 componentes por las llamadas y el rendimiento nativo**, no porque no hubiera
alternativa.

---

## 4. TypeScript — matiz

El repositorio es **100 % JavaScript**: 0 archivos `.ts`/`.tsx` en `Frontend/`, `@types/react` solo
como ayuda del editor. TypeScript es tecnología nueva para el equipo y se suma en la misma entrega
que React Native.

**Ratificado el 2026-10-01: se mantiene TypeScript.** Los motivos:
- es el template por defecto de Expo (desviarse cuesta trabajo, no lo ahorra);
- no hay código legado que migrar — el coste es de aprendizaje, no de conversión;
- con 32 endpoints y respuestas de forma estable (`API_CONTRACT.md` §5), tipar el cliente de API
  evita una clase entera de errores que en el web se descubren en runtime.

El riesgo se acepta explícitamente: si frena la primera entrega, relajar la configuración del
compilador es reversible; abandonar TypeScript después no lo es tanto.

---

## 5. Lo que esta decisión NO resuelve

Dos contratos del backend bloquean una app móvil usable **con cualquier framework**:

1. **Sesión de 15 minutos sin refresh.** `JWT_ACCESS_TOKEN_EXPIRES = 0:15:00` verificado en
   ejecución; no existe `create_refresh_token` en el código. Ya estaba registrado como pendiente en
   `BACKEND_ARCHITECTURE.md` §20 ítem 9. **Decidido el 2026-10-01 en `ADR-017-jwt-session-policy.md`
   (refresh token rotativo); implementación pendiente.** Este ADR no lo resuelve: solo depende de él.
2. **Chat por polling HTTP** (4 s de hilo, 2 s de «escribiendo»), sin Flask-SocketIO en ninguna
   parte del backend. Android detiene el polling en segundo plano, así que push se vuelve
   dependencia de la fase de chat, no de la fase 4.

---

## 6. Coste del cambio si el equipo prefiere Capacitor

Para que la comparación sea accionable y no retórica:

| | React Native + Expo | Capacitor |
|---|---|---|
| UI | 120 componentes `.jsx` reescritos | se reutiliza el shell móvil existente |
| Lenguaje | TypeScript nuevo para el equipo | el mismo JS/JSX de hoy |
| Herramientas Android | JDK 17+, SDK 36, NDK, Gradle 9.3.1 | JDK 17+, SDK, Gradle (sin NDK propio) |
| Tokens de diseño | 211 custom properties → constantes TS | `tokens.css` se usa tal cual |
| i18n, validadores, formatters | portables (33 módulos) | se usan sin tocar |
| Llamadas en segundo plano | SDK oficial de LiveKit para RN/Expo | sin plugin oficial; módulo nativo propio |
| Rendimiento del feed en el A16 | listas/vídeo nativos | WebView |
| Reversibilidad | alta al principio, cae con cada pantalla escrita | alta |

Cambiar de decisión **antes** de escribir pantallas cuesta prácticamente nada. Cambiarla después de
la fase 3 del roadmap cuesta la reescritura entera. Por eso esta decisión se ratifica ahora, no más
adelante.

---

## 7. Qué evidencia cambiaría esta decisión

Registrado explícitamente para que una revisión futura no tenga que reconstruir el razonamiento:

- Que el equipo **retire** las llamadas del alcance del producto → reconsiderar Capacitor (§1.1).
  Es la condición que la ratificación del 2026-10-01 resolvió a favor de React Native.
- Que una prueba real de LiveKit entre dos dispositivos falle de forma no resoluble con Expo
  development build → reconsiderar el transporte de llamadas, no necesariamente el framework.
- Que el coste medido de reescribir las primeras 3–4 pantallas resulte muy superior a lo previsto →
  reevaluar antes de continuar, no al final.
- Que el rendimiento del WebView en el A16 resulte aceptable en una prueba concreta con el feed
  real → debilita §2.4 (pero no §2.3).

---

## 8. Riesgos pendientes

- Ninguna integración externa está verificada: Google en Android, push y llamadas (§READINESS §1).
- JDK 25 (el JBR de Android Studio) con Gradle 9.3.1 y Kotlin 2.1.20: sin comprobar. RN documenta
  JDK 17.
- 49 GB libres en disco con SDK 36 + NDK + Gradle + node_modules por instalar: ajustado.
- El teléfono de pruebas no está conectado; hasta que lo esté, nada es verificable en dispositivo.

---

## 9. Documentos relacionados

- `docs/mobile/READINESS.md` — auditoría y evidencia de cada afirmación de este ADR.
- `docs/architecture/BACKEND_ARCHITECTURE.md` §20 ítem 9 — política de expiración/refresh de JWT.
- `docs/architecture/API_CONTRACT.md` v0.19 — contrato HTTP que la app móvil consumirá sin cambios.
- `docs/architecture/ADR-012-google-sign-in.md` — verificación de ID Token; la app Android reutiliza
  `POST /api/auth/google` y, previsiblemente, el mismo Web client ID como `serverClientId`.
- `docs/architecture/ADR-013` / `ADR-014` — modelo de mensajes y su polling.
- `docs/architecture/REPOSITORY_STRUCTURE.md` — deberá actualizarse si se aprueba `mobile/`.
