# THERS — Prompt maestro Android con React Native, Expo y TypeScript

Versión 2.0 · Investigación revisada el 1 de octubre de 2026.

Este documento sustituye la recomendación móvil de la versión anterior de este mismo archivo. La propuesta principal pasa a ser React Native + Expo + TypeScript. Capacitor conserva valor como alternativa si la prioridad es aprovechar la web y reducir el tiempo hasta una primera APK.

La evaluación siguiente es una recomendación contextual, no un benchmark ni una auditoría del código actual. Claude debe contrastarla con el repositorio y con las versiones disponibles antes de implementar.

## 1. Encargo para Claude Code

Actúa como arquitecto y desarrollador sénior de aplicaciones móviles, con experiencia en React Native, Expo, Android, Flask, PostgreSQL, JWT, notificaciones y llamadas.

Quiero iniciar la aplicación Android de THERS con una base que podamos mantener como equipo pequeño. Evalúa críticamente esta propuesta: no la aceptes solo porque viene redactada como un prompt maestro.

Lee las instrucciones del repositorio, revisa el código real, contrasta las dependencias críticas y emite un veredicto fundamentado. Si React Native + Expo encaja, implementa la primera entrega definida en la sección 9. Corrige bloqueos locales pequeños dentro de ese alcance y continúa. No te limites a devolver otro plan.

Si encuentras razones materiales para cambiar de enfoque, explica el bloqueo, su evidencia, la alternativa y el trabajo adicional. No reemplaces silenciosamente el frontend ni el backend. Puedes avanzar en tareas independientes mientras queda pendiente una decisión sustancial.

No construyas toda la red social de una vez. Este documento define la arquitectura general y un primer alcance ejecutable; las demás fases permiten continuar con criterios claros.

## 2. Contexto que debes verificar

- Proyecto: THERS_REDSOCIAL; carpetas históricas backend/ y Frontend/.
- Backend reportado: Python, Flask, Flask-JWT-Extended, SQLAlchemy, Alembic y PostgreSQL, con separación por capas.
- Frontend reportado: React/Vite con JSX. Confirma framework, router, gestor de paquetes, lockfiles y estructura actual.
- Se ha trabajado en registro/login, GET/PATCH /api/users/me, recuperación/verificación con Resend y Google Sign-In. La configuración web de Google tuvo problemas de origen; no la des por resuelta.
- Chat, llamadas, publicaciones y otras funciones pueden estar planeadas, parcialmente implementadas o disponibles. Verifícalo.
- El equipo usa Windows; hay un Samsung Galaxy A16 5G para pruebas y el presupuesto es limitado.
- Android es la plataforma actual. Una posible versión iOS futura es una ventaja opcional, no un requisito que justifique complicar esta entrega.
- Supabase se ha considerado para alojar PostgreSQL; no se ha autorizado sustituir Flask/JWT por Supabase Auth ni Firebase Auth.
- SiteGround ya se paga, pero sus capacidades de ejecución y conexiones persistentes deben comprobarse antes de asignarle servicios.
- Conserva la identidad y los flujos de THERS. Si existe THERS_IMPLEMENTACION_MAESTRA_CLAUDE.md, úsalo como referencia de producto/diseño; no constituye evidencia de funciones terminadas.

Lee CLAUDE.md, AGENTS.md y documentación aplicable. Registra git status, preserva cambios del equipo y evita reset, clean, stash automático o reestructuraciones globales.

## 3. Evaluación de alternativas ya realizada

Los juicios de encaje se basan en el conocimiento de React del equipo, el trabajo web existente, Android como prioridad, el coste de mantener la app y las integraciones previstas. No son calificaciones universales.

| Alternativa | Qué aporta | Coste o límite relevante para THERS | Decisión de partida |
| --- | --- | --- | --- |
| React Native + Expo | Componentes nativos, JavaScript/TypeScript, herramientas de navegación y módulos nativos; desarrollo Android local o con servicios opcionales | Hay que adaptar las pantallas web; las dependencias nativas deben ser compatibles y las llamadas requieren integración adicional | Opción principal para la app móvil |
| React Native con proyectos nativos gestionados manualmente | Mismo modelo de UI, con control directo de Android/iOS y sus personalizaciones | Mayor mantenimiento de configuración nativa; no aporta automáticamente mejor rendimiento que usar Expo | Usarlo si una necesidad concreta lo justifica; Expo no impide código nativo |
| React web + Capacitor; Ionic opcional | Reutiliza HTML/CSS y gran parte de la interfaz web, con acceso a SDK nativos mediante plugins/código nativo | Las integraciones móviles y la experiencia de una WebView requieren validación; también puede necesitar trabajo nativo para llamadas | Mejor alternativa si domina la rapidez y la web móvil ya es adecuada |
| Flutter | UI multiplataforma con Dart y acceso a servicios nativos | Nuevo lenguaje y adaptación completa de la interfaz para este equipo; no hay una ventaja comprobada aquí que compense por sí sola ese cambio | Viable si el equipo domina Dart/Flutter o existe una integración decisiva |
| Kotlin + Jetpack Compose | Desarrollo nativo Android con acceso directo a sus APIs | Aprendizaje y mantenimiento de una interfaz Kotlin separada de la web React | Alternativa fuerte si Android exclusivo y experiencia Kotlin son prioridades reales |
| Kotlin Multiplatform / Compose Multiplatform | Permite compartir lógica y, cuando corresponde, UI entre plataformas | No reaprovecha directamente la interfaz React; agrega una tecnología distinta sin necesidad multiplataforma inmediata | Sin ventaja suficiente para elegirlo ahora |
| PWA | Aprovecha la web, con capacidades de instalación y funciones sujetas al navegador/plataforma | Las capacidades y el ciclo de vida deben probarse para cada plataforma; no la elegiría como base principal de llamadas con integración nativa profunda | Complemento de la web, no la ruta móvil preferida |

Fuentes de capacidades: [S1], [S2], [S5], [S6], [S7], [S8], [S9].

Ionic es principalmente una biblioteca de interfaz web; Capacitor es el contenedor/puente nativo. No son dos motores móviles equivalentes que deban instalarse obligatoriamente juntos.

React Native no convierte automáticamente los componentes DOM/HTML/CSS de Frontend/ en pantallas nativas. Se pueden compartir contratos API, funciones puras y algunos modelos; las pantallas, navegación, almacenamiento y dependencias del navegador necesitan adaptación. [S2]

La conclusión cambia respecto de la propuesta anterior porque ahora se prioriza la base de una aplicación móvil que crecerá con multimedia y comunicación, aceptando el coste de adaptar la UI. Capacitor sigue siendo válido para sacar una APK reutilizando más trabajo.

Ni React Native ni Expo garantizan más usuarios concurrentes o llamadas fiables por sí solos. La capacidad del backend, consultas, archivos multimedia y servicios de comunicación se evalúa separadamente. LiveKit dispone también de SDK para Flutter y Android; su existencia no demuestra superioridad exclusiva de React Native. [S10]

## 4. Hallazgos técnicos relevantes

- React Native recomienda comenzar aplicaciones nuevas con un framework como Expo. EAS es un conjunto opcional de servicios; no es una condición para usar el framework. [S1]
- Expo admite development builds y personalizaciones nativas mediante plugins/configuración o módulos propios. Expo Go no es el entorno suficiente para todas las integraciones de THERS. [S3], [S4]
- LiveKit documenta un SDK de React Native y configuración Expo; requiere código nativo y no funciona en Expo Go. [S11]
- LiveKit requiere integración adicional para mantener llamadas en segundo plano; Android restringe servicios, cámara y micrófono. “Conectar a una sala” y “recibir una llamada con pantalla bloqueada” son capacidades distintas. [S12], [S13]
- SecureStore cifra valores en Android mediante claves gestionadas por Android Keystore. Es apropiado para secretos pequeños, no para guardar todo el perfil o la base de mensajes. [S14]
- La guía actual de Expo distingue react-native-nitro-google-signin y @react-native-google-signin/google-signin. Indica soporte de Credential Manager en la primera y una oferta de pago para esa API en la segunda. Revisa mantenimiento, licencia y compatibilidad antes de elegir; no instales una integración Android obsoleta por costumbre. [S15]
- expo-notifications puede obtener tokens del dispositivo para FCM/APNs o usar el servicio push de Expo. Son rutas diferentes y sus tokens no deben confundirse. [S16], [S17]
- Para Windows, prioriza Expo CLI y Android Studio/Gradle. eas build --local no tiene soporte oficial para Windows; WSL no equivale a una ruta oficialmente soportada de ese comando. [S18]
- Una build de desarrollo normalmente usa Metro para servir JavaScript. Una APK interna de prueba puede incluir el bundle y abrir sin Metro. El AAB orientado a tienda no se instala directamente como una APK. [S19]
- Las solicitudes nativas de React Native no están sujetas al modelo CORS del navegador. Conserva la configuración web y revisa conectividad, TLS, cabeceras y autenticación antes de atribuir un fallo nativo a CORS. [S20]

Confirma las versiones exactas al implementar. No copies recetas antiguas ni combines versiones independientes de React, React Native y Expo sin comprobar su matriz.

## 5. Arquitectura propuesta

Mantén tres partes claras en el repositorio actual:

| Parte | Responsabilidad |
| --- | --- |
| Frontend/ | Aplicación web existente |
| backend/ | API, autorización, usuarios, persistencia y lógica de negocio compartida |
| mobile/ | Nueva aplicación React Native + Expo; adapta la ruta si ya existe una app móvil |
| docs/mobile/ | Decisiones, configuración, pruebas y progreso |
| Paquete compartido, solo si aporta valor | Contratos y funciones sin DOM ni dependencias de plataforma |

Respeta cualquier configuración de workspaces ya presente. No conviertas todo el repositorio en un monorepo complejo ni cambies sus lockfiles solo para añadir mobile/.

La web y la app usarán la misma API y las mismas cuentas de THERS. PostgreSQL permanece detrás del backend. Los correos los envía el servidor. Los archivos multimedia usarán el sistema existente o el que se decida en una fase específica. Audio/video en tiempo real se transportará con su SDK/infraestructura; no envíes el contenido de las llamadas por endpoints Flask ordinarios.

### Stack propuesto, con instalación incremental

| Necesidad | Elección inicial |
| --- | --- |
| App | React Native + Expo con SDK estable compatible |
| Lenguaje nuevo | TypeScript en mobile/, sin convertir toda la web |
| Navegación | Expo Router, salvo una base móvil existente que justifique conservar su navegación |
| Consultas y caché API | TanStack Query cuando aporte valor; cliente HTTP pequeño con fetch o el cliente compatible existente |
| Sesión | Contexto/estado mínimo y SecureStore; no añadir otra biblioteca global sin necesidad |
| UI | Componentes React Native, estilos y tokens de THERS; no imponer Tailwind/NativeWind ni otra biblioteca visual |
| Imágenes y selección | Módulos Expo mantenidos; ImagePicker al implementar publicaciones |
| Video del feed | Evaluar expo-video cuando corresponda |
| Google | Una integración nativa vigente con Credential Manager, elegida tras revisar la sección anterior |
| Push Android | expo-notifications con FCM directo como candidato; Expo Push Service si simplifica un requisito comprobado |
| Chat | Transporte ya existente; si es Flask-SocketIO, cliente Socket.IO compatible |
| Llamadas | LiveKit como candidato inicial, sujeto a prueba funcional, compatibilidad y coste |

Expo Router, TanStack Query, ImagePicker y expo-video tienen documentación específica: [S21], [S22], [S23], [S24]. Elige una sola estrategia por responsabilidad.

No instales todas las dependencias del roadmap en el primer commit. Comprueba la arquitectura de React Native requerida por el SDK actual y el soporte de cada biblioteca nativa; evita intentar desactivar una arquitectura que el SDK elegido ya no soporte.

## 6. Auditoría y decisión de preparación

Comprueba:

1. Framework real, estructura, scripts, versiones y herramientas disponibles.
2. Estado de Git y línea base del build web y del backend.
3. Persistencia real, migraciones y una cuenta de prueba propia.
4. Login y perfil autenticado: rutas reales, cuerpos, errores y formato del token.
5. Caducidad, logout, refresh/revocación si existen, y almacenamiento actual.
6. Registro, recuperación, OTP y Google: qué está implementado, configurado y probado.
7. Qué endpoints de feed, publicación, archivos y chat existen realmente.
8. Posibles piezas reutilizables sin DOM; referencias de diseño y funciones que necesitan adaptación.
9. Herramientas Android, Node/JDK/SDK, espacio disponible y dispositivo.
10. Estado de integraciones externas necesarias para las pruebas tempranas.

Presenta una matriz con componente, ruta/evidencia, prueba, resultado y bloqueo. Usa “no comprobado” cuando corresponda. No confundas documentación, mockups, configuraciones de ejemplo o código escrito con funcionalidad verificada.

Emite un veredicto:
- Listo para iniciar sesión/perfil móvil.
- Listo para preparar mobile/, con bloqueos concretos para la integración.
- Sin acceso o datos suficientes para confirmar: indica qué falta y avanza en lo independiente.

Para la primera entrega basta un backend de desarrollo accesible con autenticación y perfil funcionales, o bloqueos pequeños que puedas reparar. No hace falta terminar feed/chat/llamadas ni desplegar producción.

Registra un ADR: tecnología elegida, alternativas, razones, coste de adaptación, riesgos pendientes y pruebas que podrían cambiar la decisión. No inventes porcentajes de código reutilizable ni estimaciones exactas de velocidad.

## 7. Sesión, API y conectividad

### Sesión

- Conserva el JWT y las cuentas de Flask. No migres autenticación a otro proveedor por instalar una app.
- Si el contrato usa bearer tokens, utiliza una capa de sesión con acceso en memoria y secretos persistentes pequeños en SecureStore cuando proceda.
- Si existe refresh, respeta su expiración, rotación/revocación y evita renovaciones paralelas o bucles infinitos.
- Si solo hay access token, maneja su vencimiento y exige login cuando expire; no inventes un refresh endpoint.
- Si se usan cookies, revisa primero compatibilidad y el contrato. Mantén las protecciones web; cualquier variante móvil debe ser explícita y compatible.
- Al cerrar sesión limpia tokens, caché privada, conexiones y asociaciones push cuando estén implementadas.
- Una pantalla protegida no sustituye autorización del servidor. Comprueba acceso a recursos de otro usuario en las funciones implementadas.
- No guardes contraseñas ni tokens en AsyncStorage, archivos planos, logs, URLs o fixtures.
- SecureStore no reemplaza controles del servidor; errores de lectura o eliminación requieren un estado de sesión seguro y comprensible.

### API y entornos

- Centraliza la URL API y documenta variables públicas, por ejemplo EXPO_PUBLIC_API_URL si se adopta esa convención.
- Toda variable incorporada al bundle es accesible al cliente. JWT_SECRET_KEY, DATABASE_URL, RESEND_API_KEY, claves de servicio y secretos LiveKit permanecen en el servidor.
- Respeta el prefijo /api y los contratos existentes. Implementa timeout/cancelación, errores comprensibles y respuestas tipadas; no hagas reintentos ciegos de acciones que crean datos.
- localhost en el teléfono apunta al teléfono. Usa la IP LAN real del equipo o adb reverse configurado explícitamente; el emulador estándar usa 10.0.2.2 para acceder al anfitrión. [S25]
- Distingue URL de Metro, URL de la API y URL del servicio de llamadas.
- En LAN revisa escucha del backend y firewall con reglas acotadas. Si Flask está en WSL/Docker, verifica el puerto expuesto desde Windows.
- Permite HTTP local únicamente en la configuración interna de desarrollo que lo necesite. Producción usará HTTPS/WSS; no desactives validación TLS global.
- Conserva CORS para la web. No abras todos los orígenes para corregir un fallo de red nativo.
- Las pruebas locales dependen de que el backend esté accesible. Una APK instalada no convierte el backend del equipo en un servidor público.

## 8. Integraciones que hay que validar temprano

### Google

El login web no se copia sin cambios. Verifica identificador Android, certificados SHA correspondientes a las builds, clientes OAuth y audiencia esperada por el backend.

Compara las bibliotecas actuales citadas por Expo; elige una que cubra Credential Manager con mantenimiento, licencia y compatibilidad aceptables. No presupongas que el paquete más conocido incluye gratuitamente todas las APIs nuevas. No hace falta añadir Firebase Auth para usar Google.

Flask debe verificar firma, emisor, audiencia y expiración del ID token, y aplicar su política de cuentas antes de emitir la sesión THERS. No aceptes cualquier audiencia, no confíes en datos decodificados sin verificar y no vincules cuentas por coincidencia de email sin revisar la política existente.

Las claves secretas no pertenecen a la app. Configuraciones ausentes se documentan; no inventes IDs ni resultados de acceso.

### Push

La ruta propuesta es FCM para Android, usando el token nativo obtenido por expo-notifications y un emisor en el backend. Si Expo Push Service reduce trabajo sin perjudicar los requisitos, justifica su uso y mantén claro qué tipo de token recibe cada API.

El registro del dispositivo requiere usuario autenticado, actualización de tokens y desvinculación al cambiar de cuenta. Una notificación debe abrir una ruta validada y volver a comprobar autorización.

Prueba permisos aceptados/denegados, app abierta, segundo plano y proceso terminado cuando sea posible. No interpretes que el proveedor aceptó un envío como prueba de que llegó o se mostró. No prometas funcionamiento después de que el usuario haya forzado la detención.

Usar FCM no exige migrar usuarios ni datos a Firebase. El manejo de invitaciones de llamada puede requerir código/servicios nativos adicionales al manejo de avisos de chat.

### Chat

Reutiliza el backend existente. Si usa Flask-SocketIO, verifica compatibilidad de protocolos entre socket.io-client y los paquetes Python; Socket.IO no equivale a un WebSocket sin protocolo adicional. [S26]

Flask autoriza la conexión y cada conversación, persiste mensajes y define el historial. La app controla reconexión, identificadores de mensaje, confirmaciones y duplicados. Una conexión abierta no reemplaza push cuando la app no está activa.

### Llamadas

Evalúa LiveKit con desarrollo nativo Expo. Verifica las versiones conjuntas del SDK, WebRTC y config plugins. No añadas otra implementación WebRTC competidora al mismo cliente sin una necesidad concreta.

Flask autoriza usuarios/salas y emite credenciales limitadas; la app no recibe secretos del proveedor. Define señalización de invitación, aceptar, rechazar, cancelar, ocupado y finalización.

Haz una prueba pequeña de audio/video entre dos dispositivos antes de desarrollar extensamente las pantallas de llamadas. Diferencia:
- Entrar a una sala con la app abierta.
- Mantener audio al pasar a segundo plano o bloquear pantalla.
- Recibir y aceptar una llamada con la app inactiva.
- Recuperarse de cambios de red o permisos denegados.

Comprueba servicios Android, permisos, notificación de llamada, gestión de audio y, si hace falta, integración Telecom/ConnectionService mediante un módulo mantenido o código nativo. React Native y Expo permiten esa integración, pero no la entregan resuelta automáticamente.

Para redes distintas, valida conectividad y la infraestructura WebRTC necesaria; una prueba en el mismo Wi-Fi no acredita funcionamiento general. Separa costes de desarrollo, servicio de medios y transferencia. No prometas llamadas ilimitadas gratuitas ni cifrado de extremo a extremo si no se ha implementado y validado.

## 9. Primera entrega a implementar ahora

Tras la auditoría y la confirmación técnica de la arquitectura:

1. Crea o adapta mobile/ con Expo + React Native + TypeScript sin modificar innecesariamente Frontend/.
2. Usa una plantilla estable y verifica la compatibilidad de React/React Native/Expo y herramientas. Conserva lockfile; documenta las versiones realmente instaladas.
3. Configura navegación mínima, pantalla de login, perfil propio y cierre de sesión con UI nativa.
4. Conecta esos flujos a la API real, implementando carga, error, desconexión y sesión vencida.
5. Implementa almacenamiento de sesión conforme al contrato existente y limpieza de la caché al salir.
6. Añade configuración por entorno, .env.example sin secretos y scripts de desarrollo.
7. Configura una development build con expo-dev-client. No uses Expo Go como única validación de integraciones nativas.
8. Compila e instala en un dispositivo disponible; si no lo hay, registra qué verificaciones quedan pendientes.
9. Prepara una APK interna con JavaScript empaquetado cuando el entorno lo permita, y distingue sus pruebas de las de desarrollo con Metro.
10. Añade documentación reproducible para Windows/PowerShell y conserva un registro para retomar el trabajo.

La primera pantalla autenticada debe mostrar datos reales de /me o la ruta equivalente. No construyas un feed falso para aparentar que está conectado.

Registro y recuperación pueden incorporarse si sus contratos ya están disponibles y no desbordan este hito. Feed, push y llamadas completos pertenecen a fases posteriores, aunque sus riesgos y dependencias se revisan desde el comienzo.

Si ya dispones de configuración y herramientas, después de estabilizar este hito realiza una prueba técnica pequeña de una integración crítica. No bloquees todo el trabajo porque falte una credencial externa: documenta el paso manual exacto.

## 10. Compilación y mantenimiento nativo

- En Windows usa Expo CLI, Android Studio y el Gradle del proyecto. EAS Cloud es una alternativa opcional; no es obligatorio contratarlo para empezar. [S3], [S18]
- Documenta la diferencia entre development, preview/internal y production.
- La build de desarrollo puede depender de Metro. La APK interna destinada a abrirse por sí sola debe incluir su bundle; eso no elimina su dependencia del backend para los datos. [S19]
- Reserva AAB y firma de distribución para una etapa de publicación; maneja cualquier clave de firma fuera del control de versiones.
- Si eliges CNG, expresa las personalizaciones con app config, config plugins o módulos locales reproducibles.
- prebuild --clean elimina y regenera directorios nativos. No lo ejecutes sobre cambios manuales sin comprobar que están preservados/reproducibles.
- Si el proyecto ya gestiona android/ manualmente, no impongas CNG de forma destructiva. Documenta qué archivos nativos son fuente y cuáles se generan. [S4]
- Mantén Android como objetivo efectivo de esta fase; no declares iOS probado por compartir código.

## 11. Pruebas de aceptación y siguientes fases

Para la primera entrega:
- TypeScript y checks relevantes de Expo/dependencias sin errores pendientes que invaliden el hito.
- Compilación Android realizada y ruta de APK solo si existe.
- Login válido obtiene sesión; credenciales erróneas muestran error; /me devuelve el usuario correcto.
- Peticiones sin token o con token inválido/caducado reciben rechazo.
- Cerrar/reabrir respeta la estrategia de sesión y logout limpia datos privados.
- Desconexión no causa bucles de solicitudes ni pantallas engañosas.
- Botón Atrás, teclado, áreas seguras y textos permiten completar el flujo.
- Si se generó la APK interna, abre sin Metro; identifica qué funciones siguen necesitando servidor.
- Checks afectados de la web/backend conservan su comportamiento.

Registra por separado “código escrito”, “build compilado”, “prueba en dispositivo realizada” e “integración externa verificada”. Un test mock no acredita una llamada, correo o notificación real.

Roadmap:
1. Base móvil y sesión: la entrega anterior.
2. Pruebas tempranas de Google, push y llamadas para cerrar riesgos de arquitectura.
3. Feed/perfiles con paginación y caché; publicaciones e imágenes con permisos y límites de subida.
4. Chat persistente, reconexión y notificaciones; lista de mensajes eficiente.
5. Llamadas completas con ciclo de vida, audio y pruebas en redes distintas.
6. Optimización en dispositivo, builds internas y preparación de publicación.

Para listas y multimedia mide en el Samsung disponible: carga, memoria, fluidez y consumo relevante. Adapta paginación, miniaturas y reproducción; no atribuyas problemas automáticamente al framework. Evita instalar optimizaciones o bibliotecas adicionales sin un problema observado.

Añade pruebas enfocadas en contratos de sesión, autorización y transformaciones críticas. No conviertas esta entrega en una campaña de pruebas de todo el repositorio.

## 12. Coste, alcance y entregables

La elección del framework no elimina los costes de backend, base de datos, archivos o tráfico de llamadas. Expo Framework puede usarse sin contratar EAS; las licencias de paquetes y los servicios externos se verifican por separado. No introduzcas un plan pagado para resolver una tarea local que no lo necesita.

No contrates servicios, publiques, migres datos de producción ni cambies dominios como parte de esta primera entrega. Conserva Resend/Flask/PostgreSQL y el frontend web. Las correcciones locales necesarias para Android sí están dentro del alcance.

Guarda documentación concisa:
- docs/mobile/READINESS.md: evidencia, veredicto y bloqueos.
- docs/mobile/ADR_MOBILE_STACK.md: decisión y revisión de alternativas.
- docs/mobile/ANDROID_SETUP.md: herramientas, variables, comandos reales PowerShell, builds e instalación.
- docs/mobile/VALIDATION.md: resultados y pruebas pendientes.
- docs/mobile/ROADMAP.md: siguientes hitos y criterio de salida.

Responde primero con la recomendación que confirmaste o corregiste y su motivo. Después resume lo implementado, rutas, comandos ejecutados, limitaciones, APK si existe y pasos manuales indispensables.

Continúa con decisiones locales reversibles dentro del alcance. No pidas permiso por cada archivo. Ante una decisión de producto material o una operación fuera del alcance, explica el punto concreto y deja listo lo revisable. Si no tienes acceso al repositorio, dilo y no inventes la auditoría.

## Fuentes oficiales y de los mantenedores

Consulta: 1 de octubre de 2026. Las capacidades están documentadas; el ranking y la elección para THERS son juicio técnico contextual.

- [S1] React Native, uso de framework y Expo: https://reactnative.dev/docs/environment-setup
- [S2] React Native, componentes nativos: https://reactnative.dev/docs/intro-react-native-components
- [S3] Expo, development builds: https://docs.expo.dev/develop/development-builds/introduction/
- [S4] Expo, CNG y Prebuild: https://docs.expo.dev/workflow/continuous-native-generation/
- [S5] Capacitor: https://capacitorjs.com/docs
- [S6] Flutter, arquitectura: https://docs.flutter.dev/resources/architectural-overview
- [S7] Android, Jetpack Compose: https://developer.android.com/compose
- [S8] Kotlin Multiplatform, FAQ: https://kotlinlang.org/docs/multiplatform/faq.html
- [S9] web.dev, PWA: https://web.dev/learn/pwa/
- [S10] LiveKit, plataformas con SDK: https://docs.livekit.io/transport/sdk-platforms/
- [S11] LiveKit, Expo: https://docs.livekit.io/transport/sdk-platforms/expo/
- [S12] LiveKit, SDK React Native y segundo plano: https://github.com/livekit/client-sdk-react-native/blob/main/README.md
- [S13] Android, restricciones de servicios: https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start
- [S14] Expo, SecureStore: https://docs.expo.dev/versions/latest/sdk/securestore/
- [S15] Expo, Google authentication: https://docs.expo.dev/guides/google-authentication/
- [S16] Expo, Notifications: https://docs.expo.dev/versions/latest/sdk/notifications/
- [S17] Expo, FCM/APNs directos: https://docs.expo.dev/push-notifications/sending-notifications-custom/
- [S18] Expo, EAS Build local y Windows: https://docs.expo.dev/build-reference/local-builds/
- [S19] Expo, APKs: https://docs.expo.dev/build-reference/apk/
- [S20] React Native, red y CORS: https://reactnative.dev/docs/network
- [S21] Expo Router: https://docs.expo.dev/router/introduction/
- [S22] TanStack Query con React Native: https://tanstack.com/query/latest/docs/framework/react/react-native
- [S23] Expo ImagePicker: https://docs.expo.dev/versions/latest/sdk/imagepicker/
- [S24] Expo Video: https://docs.expo.dev/versions/latest/sdk/video/
- [S25] Android, red del emulador: https://developer.android.com/studio/run/emulator-networking-address
- [S26] Flask-SocketIO, compatibilidad: https://flask-socketio.readthedocs.io/en/latest/intro.html
