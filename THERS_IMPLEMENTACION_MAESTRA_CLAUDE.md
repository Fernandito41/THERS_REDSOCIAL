# THERS — Especificación maestra de integración para Claude Code

Versión 1.0 · 15 de septiembre de 2026 · Idioma de la interfaz: español

Objetivo: implementar el nuevo diseño de THERS con fidelidad a las referencias, dentro del repositorio existente y sin perder sus funciones reales.

Este archivo es una especificación de trabajo, no una afirmación de que el repositorio ya fue auditado ni de que las funciones descritas estén implementadas. Se preparó a partir de los HTML, textos, DESIGN.md y capturas disponibles. El usuario añadirá dos ZIP y textos a su proyecto; el inventario definitivo debe hacerse allí.

## 0. Instrucción de arranque

Claude Code: lee este archivo completo, las instrucciones aplicables del repositorio y todos los materiales de referencia pertinentes. Después inspecciona el proyecto, registra una línea base, presenta un plan breve y comienza a implementar. No te limites a devolver otro plan o una maqueta desconectada.

Trabaja incrementalmente. Continúa con decisiones locales, reversibles y justificadas sin preguntar por cada archivo. Detente y pide dirección cuando falte una decisión material de producto, autorización para un servicio externo, una credencial no configurada, una operación destructiva o una elección entre diseños realmente incompatibles sin evidencia suficiente.

Si un servicio externo bloquea una función, documenta el bloqueo y avanza en los módulos independientes. No anuncies una integración completa si solo terminaste las pantallas.

### 0.1. Uso por parte del propietario del proyecto

1. Coloca este archivo en la raíz de THERS_REDSOCIAL, junto a las carpetas reales de frontend y backend.
2. Guarda los dos ZIP, los textos, DESIGN.md, HTML y capturas en docs/design-reference/; conserva sus nombres originales.
3. Abre Claude Code desde la raíz del repositorio y pídele que lea THERS_IMPLEMENTACION_MAESTRA_CLAUDE.md y ejecute sus instrucciones.
4. No reemplaces tu CLAUDE.md existente por este archivo. Este documento complementa las instrucciones del proyecto.

Mensaje de arranque sugerido:

> Lee completo THERS_IMPLEMENTACION_MAESTRA_CLAUDE.md y analiza los dos ZIP, textos y diseños de docs/design-reference/. Implementa la integración en este repositorio siguiendo las reglas de fidelidad, seguridad y verificación. Empieza ahora, conserva mis cambios y deja documentado el avance para continuar si se termina la sesión.

## 1. Qué significa «totalmente igual»

El objetivo es reproducir la composición, identidad, densidad, proporciones, tipografía, iconos, imágenes, jerarquía, textos de interfaz y estados de las referencias seleccionadas. No es una autorización para rediseñar THERS según tus preferencias.

Reglas obligatorias:

- No convertir el producto en una landing page, dashboard genérico o plantilla administrativa.
- No sustituir la identidad violeta y clara por otra paleta, tipografía o estilo.
- No omitir paneles, tarjetas, filtros, filas o secciones porque resulten laboriosos.
- No copiar una captura como imagen de fondo para simular una aplicación.
- No incrustar los prototipos enteros en iframes ni entregar HTML aislados como integración.
- Conservar el orden de las secciones y la distribución del diseño seleccionado.
- No cambiar iconos por emojis ni fotografías por gradientes genéricos.
- Mantener el contenido demostrativo únicamente en fixtures de comparación visual, no como información del usuario real.
- No reproducir fallos de recorte, solapamiento, contraste, seguridad o datos engañosos solo porque aparezcan en el prototipo. Documentar esas excepciones.

No prometas igualdad píxel a píxel sin capturas comparativas. Fuentes, escalado, navegador, viewport y contenido deben controlarse antes de evaluar la similitud.

### 1.1. Dos ejes de aceptación independientes

| Eje | Qué verifica | Qué NO demuestra |
| --- | --- | --- |
| Fidelidad visual | Comparación con captura/HTML de referencia en estado reproducible | Que exista persistencia, autenticación o servicio externo |
| Integración funcional | Acciones reales, contrato API, autorización, persistencia y pruebas | Que la pantalla coincida con el diseño |

Una pantalla visualmente terminada y funcionalmente bloqueada debe reportarse exactamente así. Un build exitoso no demuestra ninguno de los dos ejes por sí solo.

## 2. Materiales y procedencia

### 2.1. Archivos conocidos

| Archivo | Contenido identificado | Uso |
| --- | --- | --- |
| DESIGN.md | Sistema Luminous Electric; paletas, tipografía, espacios, sombras y componentes | Base de tokens y decisiones; contiene contradicciones internas |
| Pasted text.txt | 16 bloques THERS: Radar en dos variantes, Feed, Buscar y 12 pantallas de Configuración | Recuperar pantallas y estructura completa |
| Pasted text(1).txt | 8 bloques THERS de mensajería y perfiles | Complementar el ZIP y comparar variantes |
| stitch_thers_web_design_system (2)(1).zip | 8 parejas nominales code.html/screen.png y luminous_electric/DESIGN.md | Referencias organizadas de Mensajes y Perfiles |
| Segundo ZIP que añadirá el usuario | Nombre y contenido no confirmados en este documento | Inventariar y cruzar con lo anterior antes de decidir |

El ZIP conocido tiene 27 entradas contando directorios, no 27 pantallas. Los textos son HTML concatenados, no una descripción funcional validada del backend.

### 2.2. Mapa inicial de HTML sueltos

Los nombres son los recibidos. Las parejas de captura indicadas deben confirmarse por contenido al importar; no relaciones archivos únicamente por el número del nombre.

| HTML | Pantalla | Captura candidata |
| --- | --- | --- |
| code(3).html | Configuración: Audio y reproducción | No había screen(3).png entre los archivos sueltos disponibles |
| code(4).html | Cuentas bloqueadas y restringidas | screen(4).png |
| code(5).html | Descarga de datos y archivo | screen(5).png |
| code(6).html | Editar perfil | screen(6).png |
| code(7).html | Enlaces y redes conectadas | screen(7).png |
| code(8).html | Herramientas y Resonancias / Centro de Control de Audio y Radar | screen(8).png |
| code(9).html | Preferencias de notificaciones | screen(9).png |
| code(10).html | Permisos y aplicaciones de terceros | screen(10).png |
| code(20260915-030756).html | Preferencias de contenido y feed | screen(20260915-030757).png |
| code(20260915-030804).html | Privacidad de la cuenta | screen(20260915-030805).png |
| code(20260915-030813).html | Seguridad y contraseña | Ver pareja de la siguiente fila |
| code(20260915-031007).html | Seguridad y contraseña | screen(20260915-031007).png |
| code(20260915-031019).html | Suscripción y verificación | screen(20260915-031019).png |
| code(20260915-031032).html | Feed principal | screen(20260915-031033).png |
| code(20260915-031045).html | Ubicación y Radar, modo claro | screen(20260915-031045).png |
| code(20260915-031057).html | Buscar videos y contenido sugerido | screen(20260915-031057).png |
| code(20260915-031108).html | Ubicación y Radar, profundidad funcional | screen(20260915-031108).png |

Los dos HTML de Seguridad indicados eran idénticos byte a byte en el material revisado. Verifica al importarlos; no crees dos pantallas ni dos implementaciones de esa función por tener dos nombres.

### 2.3. Directorios del ZIP conocido

Bajo stitch_thers_web_design_system/:

| Directorio | Papel en la integración |
| --- | --- |
| thers_mensajer_a_directa_y_canales_de_audio_modo_claro | Variante de mensajería de tres paneles internos |
| thers_mensajer_a_directa_y_canales_de_audio_modo_claro_organizado | Variante organizada de esa misma experiencia |
| thers_mensajes_bandeja_de_entrada_canales_de_audio | Bandeja y descubrimiento de canales |
| thers_mensajes_informaci_n_multimedia_radar | Detalles, archivos, ubicación y privacidad de una conversación |
| thers_mensajes_sala_activa_de_chat_reproductor | Conversación activa y reproducción |
| thers_mi_perfil_personal_publicaciones_destacadas_y_likes | Perfil propio, colecciones, publicaciones y likes |
| thers_perfil_de_usuario_mateo_valencia_cortos_en_video_navegaci_n_por_iconos | Perfil ajeno con cortos y navegación por iconos |
| thers_perfil_de_mateo_valencia_m_dulo_completo_de_cortos_en_video | Variante ampliada de cortos en perfil ajeno |
| luminous_electric | DESIGN.md |

Incidencia confirmada: screen.png del directorio thers_perfil_de_mateo_valencia_m_dulo_completo_de_cortos_en_video contiene el texto «<FIFE Image failed to fetch>» y ocupa 28 bytes; no es una imagen PNG válida. Usa su code.html y el texto correspondiente. Una captura compatible de la otra variante sirve como apoyo, pero no como prueba de haber visto la captura dañada. Si el segundo ZIP aporta una imagen válida, registra la sustitución.

### 2.4. Inventario obligatorio al iniciar

Crea docs/THERS_REFERENCE_MANIFEST.md. Para cada referencia registra:

- ID estable: REF-FEED-01, REF-RADAR-02, REF-MSG-01, etc.
- Archivo de origen y ruta interna si procede de ZIP.
- Pantalla, variante y estado visible: tab activa, modal abierto, selección, scroll.
- Pareja HTML/captura y recursos asociados.
- Validez real de imagen, dimensiones y hash para detectar duplicados.
- Referencia elegida como canónica y motivo.
- Partes complementarias de otras variantes.
- Conflictos, materiales ausentes o pendientes de lectura.

Lee los textos por bloques hasta cubrirlos completos; no declares revisados todos los diseños tras leer solo las primeras líneas. Preserva los originales, incluidos sus nombres, para trazabilidad. Extrae cada ZIP en su propia carpeta; no sobrescribas uno con otro. Rechaza rutas de ZIP que salgan de la carpeta de destino. No ejecutes scripts de los archivos de referencia como parte de la extracción.

## 3. Jerarquía de decisiones y variantes

Para decisiones visuales, aplica este orden:

1. Última indicación explícita del usuario sobre una pantalla concreta.
2. Captura válida seleccionada como canónica y su HTML asociado.
3. Otras referencias de la misma pantalla que completen secciones o estados.
4. DESIGN.md, interpretado junto con las referencias.
5. Valores de respaldo de este documento, solo cuando no haya evidencia específica.

Las reglas de seguridad, funcionamiento y accesibilidad no se anulan por el texto de una maqueta. Las instrucciones operativas del repositorio también deben respetarse.

Una discrepancia entre captura y HTML exige comprobar viewport, escalado, carga de fuentes y CSS computado. Para la apariencia visible manda la captura; para comportamiento no mostrado, el HTML es solo evidencia auxiliar, no contrato de producto.

### 3.1. Diferencia respecto del prompt previo

El prompt anterior proponía normalizar todas las pantallas a una paleta y una sidebar de 256px. Esos valores siguen como respaldo, pero la petición actual de máxima fidelidad tiene prioridad visual: no fuerces 256px ni sustituyas todos los violetas si la referencia canónica demuestra otra medida o tono.

Un único Design System no significa borrar variantes legítimas. Significa un catálogo central de tokens y componentes, con variantes nombradas y controladas. Ejemplo: un AppShell compartido puede tener variantes social, settings y messages; nunca tres copias independientes de su implementación.

### 3.2. Procedimiento para resolver contradicciones

- Compara pantallas equivalentes, no vistas distintas de la misma función.
- No asumas que «organizado», «completo», una fecha o un número mayor significa aprobación del usuario.
- Si son complementarias, reutiliza sus piezas en rutas/estados adecuados.
- Si difieren en el mismo estado, elige la variante más completa y compatible solo cuando la evidencia permita hacerlo; documenta la elección antes de editar.
- No mezcles a voluntad columnas de una versión, fuentes de otra y colores de una tercera.
- Conserva las variantes no elegidas como referencia; no las borres.
- Si el conflicto cambia materialmente la experiencia y no se puede resolver con evidencia, pide una elección concreta y continúa con trabajo independiente.

Ejemplos detectados que debes resolver expresamente:

| Conflicto | Regla |
| --- | --- |
| Primary #630ED4 frente a #7C3AED | Conservar ambos como colores base; asignar roles semánticos según referencia, sin reemplazo global |
| Neutrales #131B2E/#4A4455 frente a #0F172A/#64748B | Elegir por variante canónica documentada; no mezclarlos accidentalmente |
| Sidebar 256/288px en HTML y 260px en DESIGN.md | Obtener ancho real por familia y centralizarlo en tokens de layout |
| Compacta 72px frente a 88px | Unificar el comportamiento escogido y su offset, sin duplicar sidebars |
| rounded-lg significa 8px en ciertos prototipos y 16px en DESIGN.md | Resolver por valor computado; no copiar el nombre de la clase suponiendo equivalencia |
| «Carlos Silva» en sidebar y «Cristopher Stanley» en perfil | Muestras visuales, no identidades del usuario autenticado |
| Texto de cooldown de 14 días en Editar perfil | El plazo real lo determina el backend; no sustituir una regla existente por la maqueta |
| «E2EE», «2FA», «Verificado», «Lossless», «En vivo» | Mostrar como capacidades activas solo con evidencia funcional; ver sección 10 |

## 4. Auditoría del repositorio y límites de trabajo

Antes de modificar código:

1. Confirma la raíz real del repositorio y lee CLAUDE.md, AGENTS.md aplicables, README, arquitectura y contrato API.
2. Revisa git status y rama actual. No asumas que develop o una rama antigua sea la correcta.
3. Identifica cambios locales del equipo y no los sobrescribas. No hagas stash, checkout, pull, merge o rebase automáticamente sobre su trabajo.
4. Detecta el frontend real, mayúsculas de Frontend/, framework, router, lenguaje, bundler, paquetes, versiones, lockfile, estado, cliente HTTP e iconos.
5. No asumas React, TypeScript ni Tailwind solo porque los prototipos los sugieran. No migres de stack sin necesidad acordada.
6. Identifica backend, rutas, modelos, migraciones, autenticación, configuración y pruebas. El contexto previo menciona Flask, JWT, SQLAlchemy, Alembic y PostgreSQL, pero debes comprobar el estado actual.
7. Registra endpoints realmente existentes y sus contratos. No des por operativo el envío de correo o código porque haya sido solicitado antes.
8. Ejecuta los checks disponibles en entorno seguro y registra fallos previos. No pruebes contra producción ni una base con datos del usuario.
9. Presenta un resumen breve y comienza con una primera integración verificable.

Autorización de este encargo: editar localmente UI, estilos, componentes, rutas, adaptadores, pruebas y documentación para la integración. Corregir defectos directamente relacionados cuando sea necesario y verificable.

No autoriza: contratar servicios, publicar el sitio, crear infraestructura externa, usar pagos reales, enviar correos a terceros, publicar contenido, cambiar permisos de cuentas, destruir datos ni reescribir todo el backend. Los cambios de dominio amplios o una migración incompatible requieren decisión explícita.

## 5. Contrato visual de THERS

### 5.1. Identidad

- Modo claro como objetivo principal; no desarrollar un modo oscuro nuevo sin referencias o requerimiento.
- Fondos claros, lila muy suave y superficies blancas.
- Violeta en acciones, foco, selección e indicadores de marca, no como lavado de todas las superficies.
- Jerarquía editorial con Plus Jakarta Sans; tarjetas suaves, bordes finos y sombras discretas.
- Marca THERS tal como aparezca en la referencia canónica. No inventar isotipos, círculos, eslóganes o badges ALPHA/PRO que esa referencia no incluya.
- Conservar «Cápsulas», «Resonancias», «Momentos» y «Radar» donde correspondan. No redefinir su significado a partir de una sola maqueta.

### 5.2. Paleta base y roles de respaldo

Los valores de respaldo son para huecos de especificación. Los tokens base conservan los colores de origen aunque no todos se usen en cada variante.

| Rol de respaldo | Valor |
| --- | --- |
| brand.default | #7C3AED |
| brand.hover | #6D28D9 |
| brand.deep | #630ED4 |
| brand.soft | #EDE0FF |
| background.app | #FAF8FF |
| background.subtle | #F2F3FF |
| surface.default | #FFFFFF |
| surface.subtle | #F8FAFC |
| surface.recessed | #F1F5F9 |
| text.primary | #0F172A |
| text.secondary | #64748B |
| text.disabled | #94A3B8 |
| border.default | #E2E8F0 |
| border.subtle | #F1F5F9 |
| success.accent | #10B981 |
| success.text | #047857 |
| success.surface | #ECFDF5 |
| warning.accent | #F59E0B |
| warning.text | #92400E |
| warning.surface | #FFFBEB |
| error.accent | #DC2626 |
| error.surface | #FEF2F2 |

Los pares de texto y fondo deben verificarse. Un verde/ámbar de acento no debe usarse automáticamente como texto pequeño sobre blanco. #94A3B8 no es una solución general para texto esencial ni placeholders que deban leerse.

### 5.3. Paleta original Luminous Electric que debe conservarse como referencia

Este bloque transcribe el mapa de colores del encabezado de DESIGN.md. No se debe aplicar ciegamente como tema único, porque su cuerpo contiene otra familia de neutrales.

~~~yaml
surface: '#faf8ff'
surface-dim: '#d2d9f4'
surface-bright: '#faf8ff'
surface-container-lowest: '#ffffff'
surface-container-low: '#f2f3ff'
surface-container: '#eaedff'
surface-container-high: '#e2e7ff'
surface-container-highest: '#dae2fd'
on-surface: '#131b2e'
on-surface-variant: '#4a4455'
inverse-surface: '#283044'
inverse-on-surface: '#eef0ff'
outline: '#7b7487'
outline-variant: '#ccc3d8'
surface-tint: '#732ee4'
primary: '#630ed4'
on-primary: '#ffffff'
primary-container: '#7c3aed'
on-primary-container: '#ede0ff'
inverse-primary: '#d2bbff'
secondary: '#006c49'
on-secondary: '#ffffff'
secondary-container: '#6cf8bb'
on-secondary-container: '#00714d'
tertiary: '#704500'
on-tertiary: '#ffffff'
tertiary-container: '#905b00'
on-tertiary-container: '#ffe1c0'
error: '#ba1a1a'
on-error: '#ffffff'
error-container: '#ffdad6'
on-error-container: '#93000a'
primary-fixed: '#eaddff'
primary-fixed-dim: '#d2bbff'
on-primary-fixed: '#25005a'
on-primary-fixed-variant: '#5a00c6'
secondary-fixed: '#6ffbbe'
secondary-fixed-dim: '#4edea3'
on-secondary-fixed: '#002113'
on-secondary-fixed-variant: '#005236'
tertiary-fixed: '#ffddb8'
tertiary-fixed-dim: '#ffb95f'
on-tertiary-fixed: '#2a1700'
on-tertiary-fixed-variant: '#653e00'
background: '#faf8ff'
on-background: '#131b2e'
surface-variant: '#dae2fd'
~~~

### 5.4. Tipografía exacta de la referencia

Fuente principal: Plus Jakarta Sans. Fallback técnico: system-ui, sans-serif. Cargar los pesos necesarios antes de tomar capturas. El cuerpo de DESIGN.md prescribe 400/600/700/800; algunos HTML cargan 500: usarlo únicamente si la referencia seleccionada lo necesita y registrarlo.

| Token | Tamaño | Interlineado | Peso | Tracking |
| --- | --- | --- | --- | --- |
| headline-xl | 40px | 48px | 800 | -0.03em |
| headline-xl-mobile | 30px | 38px | 800 | -0.025em |
| headline-lg | 32px | 40px | 700 | -0.025em |
| headline-lg-mobile | 24px | 32px | 700 | -0.02em |
| headline-md | 24px | 32px | 700 | -0.02em |
| headline-sm | 20px | 28px | 600 | -0.015em |
| body-lg | 17px | 26px | 400 | -0.01em |
| body-md | 15px | 23px | 400 | 0em |
| body-sm | 13px | 19px | 400 | 0.005em |
| label-lg | 14px | 20px | 600 | -0.005em |
| label-md | 12px | 16px | 600 | 0.01em |
| label-sm | 11px | 14px | 700 | 0.03em |

Convertir a rem si es la convención del proyecto manteniendo la equivalencia nominal; no cambiar el tamaño raíz para comprimir una pantalla. Reservar 11px para etiquetas auxiliares, no instrucciones esenciales. Conservar saltos de línea y truncados intencionales; permitir textos largos en datos reales.

### 5.5. Espacios y radios

| Token | Valor de respaldo |
| --- | --- |
| space-1 / xs | 4px |
| space-2 / sm | 8px |
| space-3 | 12px |
| space-4 / md | 16px |
| space-6 / lg | 24px |
| space-8 | 32px |
| space-10 / xl | 40px |
| gutter | 24px |
| gutter-mobile | 16px |
| margin | 32px |
| margin-mobile | 16px |

Los nombres numéricos de este documento siguen múltiplos de 4px: space-6 = 24px. No reutilices space-5 del prompt anterior para significar 24px dentro de una escala tipo Tailwind; usa nombres inequívocos y mantén un único mapa.

Radios base: 4, 8, 12, 16, 24 y 9999px. El radio de 4px existe en DESIGN.md aunque no estuviera en la propuesta simplificada. Puede haber variantes pequeñas como checkbox de 5px si la referencia las especifica. Asigna roles (input, card, dialog, pill), no valores arbitrarios por archivo.

### 5.6. Sombras y motion

Valores tomados del cuerpo de DESIGN.md:

~~~css
/* Referencia de tokens, no instrucciones para añadir CSS global sin auditoría. */
--shadow-card: 0 1px 3px 0 rgba(15, 23, 42, 0.03), 0 1px 2px -1px rgba(15, 23, 42, 0.02);
--shadow-hover: 0 10px 25px -5px rgba(15, 23, 42, 0.05), 0 8px 10px -6px rgba(15, 23, 42, 0.02);
--shadow-overlay: 0 20px 30px -10px rgba(15, 23, 42, 0.08), 0 1px 3px rgba(15, 23, 42, 0.05);
--shadow-focus-soft: 0 0 0 3px rgba(124, 58, 237, 0.15);
--shadow-compose: 0 8px 20px -4px rgba(124, 58, 237, 0.35);
~~~

El halo violeta no sustituye por sí solo un indicador de foco con contraste suficiente. Compleméntalo si hace falta. Blur de 16px y fondo blanco al 85% solo en overlays que lo requieran, con fallback sin blur.

Si no hay duración especificada: 120ms para feedback breve, 180ms para transiciones de control y 240ms para overlays. Animar opacity/transform sin desplazar el layout. Respetar prefers-reduced-motion; congelar animaciones y pulsos durante pruebas visuales.

### 5.7. Assets e iconografía

- Inventariar imágenes, fuentes, SVG, icon fonts y recursos externos por pantalla.
- Reutilizar assets originales cuando estén disponibles y su uso esté permitido. Mantener relación de aspecto, recorte, object-fit y posición de enfoque.
- Si una imagen remota falla, no afirmar fidelidad completa. Registrar URL de origen sin credenciales y recurso faltante; usar fallback honesto solo donde sea necesario.
- No descargar arbitrariamente imágenes nuevas para reemplazar las referencias ni inventar licencias.
- Los HTML usan Material Symbols Outlined y algunas variantes SVG. Centralizar un componente Icon o adaptador que conserve la silueta, grosor, relleno y tamaño de cada icono.
- No escoger Lucide, Bootstrap Icons u otra librería solo por conveniencia si cambia visiblemente el diseño. Si ya existe una librería, evaluar equivalencias exactas y documentar excepciones.
- Mantener los emojis que sean contenido de una publicación de muestra; la prohibición de emojis se refiere a sustituir iconografía de interfaz.

## 6. Layout, navegación y responsive

### 6.1. Estructuras compartidas

AppShell contiene la navegación global, topbar y espacio de contenido. SettingsLayout, FeedLayout, MessagesLayout, ProfileLayout y RadarLayout componen ese shell, no lo duplican.

Toda medida de sidebar se refleja también en offsets de header y contenido. Usa layout de grid/flex o una variable compartida; no valores left/padding-left discrepantes por página.

Valores de respaldo: sidebar 256px, compacta 72px, topbar 64px, feed máximo 680px, rail derecho 340px, padding desktop 32px, padding móvil 16px, bottom-nav 64px más safe-area.

No impongas min-width:600px al feed en móvil. Usa min-width:0 en hijos flex/grid que deban contraerse. Las anchuras de referencia de mensajería (bandeja cercana a 340px y contexto cercano a 320px en algunas variantes) se deben contrastar con la variante elegida.

### 6.2. Breakpoints de respaldo

| Rango CSS | Comportamiento esperado cuando no exista una referencia específica |
| --- | --- |
| Menos de 768px | Una columna, bottom-nav, drawers o rutas para paneles auxiliares |
| 768–1023px | Sidebar compacta, sin rail permanente, formularios adaptables |
| 1024–1279px | Shell desktop adaptable; no forzar tres columnas si no caben |
| 1280px o más | Activar columnas extra solo cuando el cálculo de anchuras y espacios lo permita |

La regla «tres columnas desde 1024px» del prototipo puede desbordar: 256 + 600 + 340 ya supera ese ancho incluso sin márgenes. Calcula el espacio útil y usa consultas de contenedor si encajan con el stack. No comprimas el chat a una columna ilegible para mantener abierto un rail.

En móvil, limita la bottom-nav a un conjunto manejable de destinos primarios y ofrece los demás en Más/menú/perfil. Si no hay referencia móvil, documenta esta adaptación como decisión nueva, no como reproducción exacta de un diseño recibido.

### 6.3. Navegación real

- Reutilizar rutas existentes; proponer nuevas solo para vistas que lo necesiten.
- Mantener deep links, recarga directa, atrás/adelante y estado activo.
- Usar enlaces para navegar y botones para acciones. Prohibido href="#" como navegación terminada.
- Las tabs deben corresponder a una vista/estado real y conservar la selección cuando corresponda.
- Todas las pantallas deben poder abrirse desde la interfaz y desde su URL prevista.
- No confundir Preferencias de notificaciones con el Centro de notificaciones; son vistas distintas.
- No crear una segunda mensajería por cada HTML. Diferenciar bandeja, conversación e información como estados/rutas coherentes.
- Confirmar si «Cápsulas» son colecciones, audio u otro concepto según el dominio actual; conservar tipos distintos cuando la referencia los distingue.

### 6.4. Scroll y capas

- Feed/configuración/perfiles: scroll de página o del contenedor previsto, sin perder botones inferiores.
- Mensajes: historial y lista pueden desplazarse independientemente; compositor accesible con teclado móvil abierto.
- Radar: mapa y paneles no deben secuestrar el scroll de toda la aplicación.
- No copiar reglas globales que oculten todas las scrollbars o bloqueen overscroll sin justificación.
- Evitar que header, bottom-nav o teclado tapen contenido y foco; contemplar safe-area y unidades de viewport apropiadas.
- Definir escala central de capas: contenido < sticky < navegación < backdrop < modal < toast. No resolver bugs añadiendo z-index:999999.

## 7. Componentes y contratos de estado

Los nombres siguientes son orientativos: adapta carpetas y sintaxis al framework real. No instales una librería completa solo para cumplir nombres de componentes.

| Grupo | Componentes mínimos según uso real |
| --- | --- |
| Acciones | Button, IconButton, LinkButton |
| Formularios | Field, Input, SearchInput, Textarea, Select, Checkbox, Radio, Switch |
| Identidad | Avatar, AvatarGroup, PresenceIndicator, VerificationBadge |
| Estructura | Card, SectionHeader, SettingSection, SettingRow, Divider |
| Selección | Tabs, Chip, FilterChip, SegmentedControl |
| Feedback | Badge, Alert, Toast, Skeleton, EmptyState, ErrorState |
| Overlays | Modal, Drawer, Dropdown, Tooltip, ConfirmDialog |
| Social | PostCard, PostComposer, MomentCard, UserSuggestion, ProfileHeader |
| Audio/chat | AudioCapsule, AudioPlayer, Waveform, ConversationItem, MessageBubble, MessageComposer, UserContextPanel |
| Radar | RadarPlaceCard, SharedLocationCard, MapControls, RouteSummary, PlaceFilters |

### 7.1. Reglas comunes

- Variantes centralizadas: primary, secondary, ghost, danger cuando correspondan; tamaños y shape explícitos.
- No usar el mismo color para representar éxito, selección y verificación si la referencia los distingue.
- Props o parámetros de datos/eventos en vez de lógica de dominio incrustada en componentes UI.
- Componentes de bajo nivel sin llamadas HTTP directas; la feature coordina datos y acciones.
- Estados: default, hover, focus-visible, active/pressed, selected, disabled, loading, success y error según aplique.
- Loading conserva tamaño del control y evita dobles envíos; disabled tiene explicación accesible cuando sea necesaria.
- Errores junto al campo con asociación accesible, sin depender solo de color.

### 7.2. Valores de componente cuando no haya una especificación más precisa

| Componente | Base |
| --- | --- |
| Botón principal | Fondo #7C3AED, texto blanco, hover #6D28D9, padding 10px 20px, pill si la referencia usa pill |
| Botón secundario | Superficie blanca, borde #E2E8F0, texto principal, hover #F8FAFC |
| Input | Alto 44px, radio 12px, fondo #F8FAFC, borde #E2E8F0, body-md |
| PostCard | Fondo blanco, borde 1px, radio 16px, padding vertical 16px y horizontal 20px |
| Avatar de cabecera de post | 40px; fallback consistente cuando no hay imagen |
| Checkbox/radio | Marca visual 18px; zona clicable ampliada sin cambiar su apariencia |
| Estado en vivo | Acento #10B981, texto #047857, fondo verde suave y etiqueta textual |

Preserva las variantes de radio y forma de cada referencia. No conviertas todos los botones en pills si los controles de esa pantalla son rectangulares.

### 7.3. Interacciones de overlays y formularios

- Modal: nombre accesible, foco inicial, contención de foco, cierre previsto y retorno al disparador. No cerrar una acción destructiva por accidente.
- Menús/tabs: semántica y teclado correctos; no dejar atributos ARIA que describan un comportamiento inexistente.
- Guardar: validar, enviar, recibir confirmación real y luego mostrar éxito.
- Descartar: recuperar el último estado confirmado por el servidor, no vaciar todo el formulario.
- Cambios sin guardar: confirmar antes de abandonar cuando haya riesgo de pérdida.
- Toast: informa, no sustituye un error de campo ni una confirmación destructiva.
- Skeleton: conserva geometría y no sustituye permanentemente contenido que nunca se solicita.

## 8. Requisitos concretos por módulo

Para cada módulo conserva todos los elementos visibles de la referencia canónica, incluso los que no se enumeran aquí. La lista es un mínimo y no reemplaza la inspección completa de los archivos.

### 8.1. Inicio y Feed

Composición de referencia:

1. Shell con sidebar izquierda, buscador superior y acciones de usuario.
2. Carrusel Momentos con creación propia y tarjetas de usuarios.
3. Franja PULSE de actividad.
4. Compositor con avatar, texto, Foto, Cápsula, Audio, Lugar y Publicar.
5. Stream de publicaciones de texto y multimedia; ubicación/cápsula embebida según tipo.
6. Rail de perfil breve, personas sugeridas, tendencias y cápsulas recomendadas.

Conservar proporciones y recortes de Momentos, espacios entre módulos, formas de acciones, metadatos y orden de la barra social. La captura disponible del Feed contiene un panel derecho parcialmente recortado: no reproduzcas un desbordamiento global como si fuera una exigencia.

Funciones mínimas a verificar según backend existente:

- Cargar publicaciones con paginación o estrategia real del proyecto.
- Publicar con validación, estado de envío y error recuperable.
- Like/guardar/repost/seguir con estado confirmado o actualización optimista que revierta si falla.
- Abrir comentarios, perfiles, medios, ubicaciones y cápsulas asociadas.
- Evitar duplicados al reintentar o paginar.
- No mostrar contadores de muestra como reales ni actividad «en vivo» si es estática.

### 8.2. Buscar, Videos y Cortos

Conservar buscador, filtros, contenido destacado, contenido sugerido, creadores recomendados, temas y listas de comunidad presentes en las referencias.

- Mantener query y filtros en estado coherente con URL cuando corresponda.
- Diferenciar «sin resultados», «todavía no buscaste», «cargando» y «error».
- Cancelar o ignorar respuestas obsoletas si cambia la consulta; reutilizar la estrategia existente de debounce/caché.
- No mostrar resultados de una consulta anterior como si fueran nuevos.
- Conservar el ratio de miniaturas/cortos y las zonas de título, autor y métricas.
- Video: loading, play/pause, mute, controles, error y fin; no simular reproducción con una imagen.
- Evitar audio automático y pausar reproductores fuera de contexto según comportamiento definido.
- No crear rutas duplicadas de Cortos si ya es una tab de Videos/perfil; documentar la relación.

### 8.3. Perfil propio

Preservar:

- Portada panorámica y acción de cambiarla.
- Avatar superpuesto a la portada en la posición prevista.
- Nombre, handle, distintivos y categoría.
- Editar perfil, compartir y menú contextual.
- Biografía, ubicación, enlace y fecha de incorporación cuando correspondan.
- Tarjetas de publicaciones, seguidores, siguiendo y cápsulas.
- Colecciones destacadas.
- Tabs Publicaciones, Destacadas y Me gusta.
- Stream de contenido y rail de actividad, cápsulas destacadas, nodos y conexiones.

La referencia disponible muestra la tab Me gusta seleccionada y un aviso «Solo tú». Captura ese estado en QA; la pestaña inicial de la aplicación puede conservar el comportamiento del producto si está definido. La privacidad de favoritos y de ubicación debe aplicarse también en el servidor, no solo ocultando elementos.

Todos los datos de la cuenta propia deben venir de la sesión/perfil real. La maqueta de Cristopher Stanley no es una instrucción para renombrar al propietario de la cuenta.

### 8.4. Perfil ajeno y cortos modulares

- Usar datos del perfil visitado, no de /me.
- Sustituir controles de edición por seguir/mensaje según permisos reales.
- Mantener portada, avatar, bio, métricas, tabs y estructura de cortos del material.
- Diferenciar contenido público, privado, bloqueado, restringido y no encontrado.
- Respetar relaciones de follow y bloqueo; no permitir acceso a recursos privados por URL directa.
- Conservar el módulo ampliado de cortos del HTML aunque su captura original esté dañada; marcar su validación visual como parcial hasta disponer de evidencia suficiente.
- No otorgar verificación por nombre, por fixture ni desde una preferencia editable por el cliente.

### 8.5. Mensajería: bandeja y canales

- Bandeja con título, contador, nuevo mensaje, buscador y filtros equivalentes a los recibidos.
- Filas de conversación con avatar, nombre, presencia, preview, hora y no leídos.
- Selección activa visible sin cambiar altura o alineación arbitrariamente.
- Canales de audio como módulo diferenciado, sin tratarlos como llamadas ya implementadas.
- Preservar orden de conversaciones según regla real; no fijar el orden de Sofia/Mateo/etc. en producción.
- Abrir una conversación con identificador estable, manejar selección inexistente y restaurar navegación.
- Leer/marcar como leído solo conforme al contrato existente; no borrar no-leídos de otras conversaciones por abrir la bandeja.

### 8.6. Mensajería: conversación, reproductor y contexto

Estructura de escritorio: navegación global más tres paneles internos —conversaciones, chat y contexto— cuando el ancho lo permita. No confundir los tres paneles internos con el total de columnas contando la sidebar.

Conservar:

- Cabecera de chat: avatar, nombre, estado y acciones de audio/video/información.
- Separadores de fecha, burbujas entrantes/salientes, horas y estados de entrega.
- Cápsula de audio con nombre, formato, waveform, progreso y acciones.
- Tarjeta de ubicación compartida.
- Compositor y acciones de grabar audio, adjuntos y radar.
- Panel contextual con perfil, archivos/cápsulas, ubicaciones, silenciar y controles de privacidad.
- Vistas dedicadas de Información/Multimedia/Radar y Sala activa como partes de la misma experiencia.

Comportamiento obligatorio:

- Estados de mensaje enviando, enviado y fallido; reintento sin duplicar.
- No mostrar doble check/entregado/leído si no lo informa un sistema real.
- No fingir recepción de otro usuario añadiendo un mensaje fijo.
- Conservar borrador cuando sea razonable y no enviarlo al cambiar de conversación.
- Scroll al final cuando corresponde; no arrastrar al usuario hacia abajo si está leyendo historial anterior.
- Identidad y autorización del participante verificadas por backend.
- Si no existe transporte en tiempo real, usar lo disponible y reportar límites; no afirmar WebSocket/E2EE porque el diseño diga «en vivo».
- Móvil: bandeja → chat → información en vistas navegables; compositor visible al abrir teclado y botón de volver claro.
- No reproducir el estrechamiento y recortes de algunas capturas de mensajería; colapsar contexto antes de hacer ilegible el chat.

### 8.7. Audio y cápsulas sonoras

- Centralizar el estado de reproducción cuando varios componentes controlen el mismo audio.
- Usar un recurso reproducible real para una función real; un waveform de fixture solo sirve para comparación visual.
- Progreso, tiempo actual y duración proceden del reproductor, no de contadores ficticios.
- Añadir seek, mute/volumen y teclas según controles diseñados y soporte real.
- Manejar formato no soportado, error de carga, pérdida de recurso y fin de reproducción.
- Detener streams y liberar recursos/object URLs al salir; evitar grabaciones silenciosas o persistentes.
- Solicitar micrófono solo tras una acción clara, manejar rechazo y mostrar grabación activa.
- «Lossless», «48kHz», «96kHz», «binaural» y «audio espacial» solo describen capacidades/archivos reales cuando estén comprobados.
- Descargar un stem exige archivo y permiso reales; un botón que cambia de texto no constituye descarga.

### 8.8. Ubicación y Radar

Dos variantes conocidas: modo claro y profundidad funcional. Trátalas como referencias relacionadas; la variante profunda añade detalle/rutas/reportes, no implica necesariamente otra aplicación.

Preservar:

1. Identidad de ubicación, Recalibrar Radar y búsqueda de servicios.
2. Chips de restaurantes, gasolineras, farmacias, cafés/coworking y otras categorías recibidas.
3. Selector auto/moto/a pie y alternativas de ruta.
4. Ficha del establecimiento: nombre, categoría, dirección, estado, valoración, tabs y servicios.
5. Horarios, afluencia, amigos/cápsulas y reproductor de muestra cuando estén en el estado de referencia.
6. Acciones de navegación, guardar, compartir, solicitar viaje/reservar según diseño.
7. Indicaciones paso a paso.
8. Comparador de combustibles y lista de farmacias/urgencias.
9. Mapa con pins, selección, controles, capas y reporte de incidencias.
10. Cápsulas de comunidad.

Límites funcionales:

- El mapa SVG ilustrativo del HTML no equivale a cartografía, tráfico o rutas en tiempo real.
- En fixture visual puede mantenerse la ilustración original; en producción debe rotularse como demostración si no hay proveedor conectado.
- Geolocalización solo tras permiso explícito; permitir búsqueda manual si se rechaza.
- No compartir ni guardar ubicación precisa automáticamente, ni asumir que el usuario está en San Salvador por la referencia.
- Solicitar el servicio configurado mediante adaptador. Claves privadas permanecen en backend; claves públicas, si el proveedor las contempla, deben restringirse según su configuración.
- No contratar Mapbox/Google Maps u otro proveedor ni añadir facturación sin decisión del propietario.
- Precios, disponibilidad, horarios, tráfico, afluencia y tiempos de llegada requieren fuente/fecha o etiqueta clara de ejemplo.
- No ofrecer información de farmacias/urgencias simulada como orientación real actual.
- inDrive, reservas, grúa y demás botones son acciones potenciales del diseño, no integraciones concedidas. Deshabilitar con explicación o usar un enlace real permitido solo cuando corresponda.
- Enlaces de compartir ubicación deben respetar quién puede verla y durante cuánto tiempo, si el producto define expiración.
- El popover de incidencias visible en una captura debe poder abrirse como estado, no quedar pegado al mapa sin interacción.

### 8.9. Configuración: shell común

Conservar navegación global, buscador superior, breadcrumb cuando exista, menú local de ajustes, cabecera de sección, tarjetas, filas, ayuda y acciones finales.

- No crear una pantalla genérica de switches para sustituir todas las referencias.
- Mantener los grupos, orden y etiquetas de cada sección.
- Hacer explícito si un cambio se guarda con botón o automáticamente; no mezclar ambos comportamientos sin señal.
- Valores iniciales desde servidor o preferencia local explícita según naturaleza del dato.
- Manejar carga, error al cargar, guardado pendiente, éxito confirmado y error al guardar.
- Recuperar el valor previo cuando una actualización optimista falle.

### 8.10. Matriz completa de Configuración

| Pantalla | Elementos mínimos del diseño | Regla funcional |
| --- | --- | --- |
| Editar perfil | Avatar, portada, nombre, username, pronombres, categoría, visibilidad de categoría, bio/contador, enlaces, ubicación, género, sugerencias, descartar/guardar | Leer/editar perfil real; validar límites reales; no cambiar cooldown por el texto del prototipo |
| Privacidad | Visibilidad de cuenta, menciones, etiquetas, comentarios, resonancias, mensajes directos, conexiones/visibilidad | Persistencia y aplicación en backend; ocultar un control no protege datos |
| Seguridad y contraseña | Cambiar contraseña, 2FA, sesiones activas, alertas | Reutilizar auth y recuperación; no mostrar 2FA ni revocación de sesiones como operativas si faltan |
| Suscripción y verificación | Beneficios, plan/facturación, recibos, requisitos/documentos | No procesar pagos ni recoger documentos sensibles sin flujo autorizado y almacenamiento seguro |
| Herramientas y Resonancias | Radar urbano, telemetría/grabación, métricas públicas | Mostrar alcance real del permiso; no activar rastreo/grabación desde una maqueta |
| Notificaciones | Interacciones/cápsulas, radar, mensajes/llamadas, correo | Preferencias reales separadas del permiso del navegador; no enviar correo al alternar un switch |
| Audio y reproducción | Calidad, espacial/binaural, descargas/caché, autoplay | Solo opciones soportadas; identificar preferencias locales; no prometer audio que el motor no procesa |
| Enlaces y Redes | Bio link, redes vinculadas, enlaces personalizados | Distinguir enlace público de cuenta OAuth conectada; validar URL/protocolo |
| Descarga de datos | Solicitud, alcance/formato/periodo según referencia, historial, seguridad | Exportar solo datos autorizados; estados reales de trabajo; no crear ZIP de muestra como exportación real |
| Bloqueadas/restringidas | Listas, búsquedas, tabs, explicación y desbloquear | Diferenciar bloquear y restringir; confirmaciones y enforcement real |
| Permisos/aplicaciones | Aplicaciones, scopes, revocación y tokens de desarrollador | No exponer secretos; no crear tokens ficticios; revocación real o estado no disponible |
| Contenido/feed | Contenido sensible, palabras/frases, temas/etiquetas, sugerencias | Persistir y aplicar filtros cuando exista soporte; documentar controles aún no conectados |

El límite de caracteres de bio, cooldown de username, política de contraseñas, formatos de exportación, planes y precios no se definen por números ilustrativos. Inspecciona el contrato real y ajusta los textos de ayuda. Si el backend no define la regla, no inventes una regla de negocio irreversible.

### 8.11. Centro de notificaciones y módulos sin pantalla dedicada

La navegación menciona Notificaciones, Cápsulas y otros destinos; no todas las vistas tienen necesariamente un diseño dedicado en los archivos revisados.

- Buscar primero en ambos ZIP y textos.
- Reutilizar las pantallas existentes que no estén reemplazadas por una referencia.
- Si falta el diseño, implementar una composición mínima con el Design System solo cuando el alcance sea claro y marcarla como diseño derivado.
- No afirmar reproducción exacta de una pantalla no recibida.
- Si existe un asistente IA u otro módulo del proyecto, conservarlo; no contratar/modelar una nueva integración IA solo porque el proyecto la haya considerado anteriormente.

## 9. Datos, API y arquitectura de integración

### 9.1. Separación de responsabilidades

Mantener la arquitectura actual y separar, dentro de sus convenciones:

- Componentes UI: presentación y accesibilidad.
- Features/páginas: coordinación de estado, navegación y acciones.
- Servicios/adaptadores: contratos de datos, serialización y llamadas.
- Backend: autorización, reglas de negocio y persistencia.
- Fixtures: datos sintéticos solo para desarrollo/pruebas.

No es necesario imponer carpetas nuevas si el proyecto ya organiza estas responsabilidades correctamente. No mezclar lógica de mapas, correo y autenticación en componentes básicos.

### 9.2. Flujo mínimo por capacidad

1. Localizar endpoint o servicio existente y sus tests/documentación.
2. Determinar campos, tipos, IDs, permisos, paginación, errores y estados.
3. Mapear su respuesta a un modelo de UI sin alterar arbitrariamente el contrato.
4. Conectar una acción real y comprobar su persistencia/efecto.
5. Verificar errores y permisos antes de considerar terminada la función.

GET /api/users/me y PATCH /api/users/me son rutas del contexto previo que deben verificarse. Register/login/recuperación tienen que descubrirse; no inventes sus paths. Reutiliza el contrato oficial de Postman si existe.

### 9.3. Cliente HTTP y sesión

- Un cliente central, base URL por configuración, serialización consistente y manejo común de errores.
- Reutilizar el mecanismo de sesión existente; no migrar tokens a localStorage/cookies por comodidad visual.
- No exponer JWT_SECRET_KEY, DATABASE_URL, claves de correo, proveedor IA u otros secretos en bundles, fixtures, logs o documentos.
- En 401 distinguir sesión vencida de un error del propio login; cerrar/renovar según contrato, evitando loops y múltiples refresh simultáneos.
- No cerrar sesión automáticamente por errores 403, 404, 409 o un timeout.
- Manejar 400/422 de validación, 403, 404, 409, 429, fallos de red y 5xx según API real.
- IDs opacos: no convertir UUID a número ni asumir el tipo de identificador.
- Cancelar solicitudes obsoletas; no actualizar componentes desmontados.
- Limpiar caché/datos de usuario al cerrar sesión o cambiar de cuenta; no mezclar información de cuentas.
- Reintentos automáticos con cautela: no reenviar publicaciones, mensajes o acciones de pago sin idempotencia.
- No desactivar CORS, CSRF o autorización para conseguir que la interfaz «funcione».

### 9.4. Política de funciones ausentes

| Situación | Acción |
| --- | --- |
| Endpoint ya disponible | Integrarlo y probarlo; no dejar mock por rapidez |
| Endpoint existe pero tiene otro esquema | Crear mapeo/adaptador compatible; documentar campos no soportados |
| Defecto menor relacionado en backend | Corregir de forma acotada con test y sin cambio incompatible |
| Nueva capacidad de negocio o infraestructura | Documentar propuesta y pedir decisión si excede integración actual |
| Servicio externo sin configurar | Mostrar estado no disponible y registrar requisito; continuar módulos independientes |
| Solo existe la maqueta | UI implementada + fixture de desarrollo; funcionalidad pendiente, nunca «completa» |

No cambies automáticamente a mock cuando la API falle. Eso ocultaría una avería real.

### 9.5. Modo referencia para QA

Usa el harness de pruebas existente o una vista de desarrollo aislada para reproducir los mismos textos, imágenes, estados y contadores de las capturas.

- Fixtures deterministas y explícitos, sin datos reales de usuarios.
- No sembrar la base real ni crear cuentas del propietario para lograr una captura.
- Un único selector de modo si se necesita, activable solo en desarrollo/test y desactivado por defecto.
- Protección para impedir que fixtures o endpoints mock queden activos en producción.
- Documentar cómo entrar/salir del modo referencia y sus rutas.
- Un rótulo de entorno fuera del área comparada o el propio harness debe dejar claro que es una demostración.
- Datos reales y fixtures no deben mezclarse silenciosamente en una pantalla.

Las pruebas visuales usan fixtures; las pruebas de integración usan servicios/entorno de prueba controlados. No presentar el resultado de una como evidencia de la otra.

## 10. Seguridad y veracidad de funciones sensibles

### 10.1. Autenticación, correo y recuperación

- Preservar registro, login, JWT, logout, perfil, recuperación y verificación de correo tal como estén implementados.
- Auditar si el código de seis dígitos y reenvío existen realmente; no afirmar que se integraron solo por dibujar los campos.
- Si existe OTP: expiración, intentos máximos, rate limiting/reenvío e invalidación corresponden al servidor. La cuenta regresiva del frontend no sustituye protección.
- Permitir pegar el código y usar entrada accesible; no tratar verificar OTP y cambiar contraseña como pasos autenticados por un booleano manipulable del cliente.
- No revelar si un correo está registrado cuando el contrato use mensajes neutros.
- No interpretar validación de formato o dominio como prueba de propiedad de una dirección. Si el producto exige verificar correo, activar cuenta/capacidad según el flujo de confirmación real.
- No enviar correo real durante tests automáticos; usar adaptador/sandbox o destinatario de prueba autorizado.
- No modificar cooldown de username ni reglas del backend para coincidir con una frase ilustrativa.

### 10.2. Privacidad y capacidades que la maqueta no demuestra

- «Cifrado Verificado E2EE» no se puede mostrar como activo sin cifrado de extremo a extremo implementado y comprobado. HTTPS no es esa capacidad. Conservar el espacio visual con un estado honesto si falta.
- «Sincronización segura activa», «Sesión segura», presencia «En línea», badges de creador y 2FA no pueden ser estados fijos del cliente.
- No crear gestión de pagos, custodia de documentos de identidad, OAuth, API keys o llamadas en tiempo real como consecuencia implícita de copiar una tarjeta.
- Revocar una aplicación/sesión/token debe cambiar la autorización real, no solo quitar una fila del navegador.
- No guardar contraseñas, tokens privados ni coordenadas precisas de terceros en fixtures o localStorage.
- Bloqueo, perfil privado, mensajes, archivos y ubicaciones necesitan verificación de acceso en servidor.
- No descargar/exportar datos ajenos para probar un botón. Usar datos sintéticos y permisos mínimos.

### 10.3. HTML, URLs y archivos

- No ejecutar HTML no confiable de publicaciones/bios/mensajes; escapar contenido o sanitizar con solución apropiada del proyecto.
- Validar URLs y permitir protocolos necesarios; no aceptar javascript: como enlace de perfil.
- Enlaces externos con comportamiento seguro según el router y destino.
- Validar archivos en frontend para UX y en backend para seguridad: tipo, tamaño y permisos; no confiar solo en extensión.
- No exponer rutas internas ni claves en mensajes de error.
- No desactivar validadores o tests de seguridad para conservar un texto o botón de la captura.

## 11. Implementación técnica y control de cambios

- Usa el gestor de paquetes del lockfile real. No mezcles npm/yarn/pnpm ni regeneres el lockfile con otro gestor.
- Detecta la versión de Tailwind si existe. No introduzcas configuración de otra versión ni migres de versión mayor como parte del diseño.
- En un proyecto sin Tailwind, expresa los tokens con el sistema actual si satisface la referencia. Tailwind por CDN queda prohibido en el frontend integrado.
- Si se producen design-tokens.json, tokens.css y configuración de Tailwind, define una fuente de verdad y generación/validación; no tres copias que divergen.
- Reemplaza scripts inline y manipulación global de DOM de prototipos por eventos/estado del stack real.
- No uses un ID repetido para controlar todos los switches o reproductores.
- No elimines tipado, lint ni assertions de tests para conseguir un resultado verde.
- Añade dependencias solo si son necesarias, compatibles y justificadas; no introduzcas Storybook u otra plataforma completa si basta el catálogo existente.
- Haz cambios acotados. No reformatees todo el repositorio ni mezcles refactors no relacionados.
- Si reemplazas un componente, actualiza consumidores y conserva compatibilidad necesaria. No dejes dos rutas «nueva» y «vieja» sin motivo.
- No hagas commit/push/merge/deploy sin autorización. Al final puedes sugerir comandos con rutas concretas.
- No ejecutes migraciones destructivas ni contra bases del usuario. Cambios de esquema requieren diseño, tests y revisión apropiada.
- Respeta las instrucciones de agentes del repositorio; este documento no exige delegación ni autoriza edición paralela indiscriminada.

## 12. Accesibilidad y calidad de uso

La fidelidad visual debe coexistir con una interfaz utilizable. Registrar cualquier ajuste necesario y su impacto visual.

- Objetivo de contraste: texto normal al menos 4.5:1; texto grande y límites/indicadores esenciales según su función, al menos 3:1. Verificar pares concretos, no declarar conformidad global por usar una paleta.
- Zona táctil objetivo de 44×44px; el icono visual puede mantenerse a 18/20/24px. Evitar áreas invisibles superpuestas.
- Focus-visible perceptible en todos los controles y nunca oculto bajo elementos fijos.
- Orden de tabulación lógico, sin tabindex positivos para corregir desorden visual.
- Labels asociados a inputs; placeholders no sustituyen etiquetas.
- Formularios navegables con teclado; errores anunciados y vinculados al campo.
- Names accesibles para icon buttons, texto alternativo según finalidad de cada imagen, iconos decorativos ocultos a lectores.
- Estado no comunicado solo por color: checked, selected, pressed, alertas y presencia llevan semántica/texto.
- Diálogos y drawers manejan foco, Escape según contexto, bloqueo del fondo y retorno al disparador.
- Respeta reduced motion; no flash/pulsos imprescindibles.
- Mantén lectura al ampliar texto/zoom; no bloques de altura fija que corten mensajes.
- Alternativa textual/lista útil al mapa y waveform; controles de audio accesibles.
- Si se usa una herramienta automática de accesibilidad, complementarla con recorrido de teclado. No declarar certificación total a partir del escaneo.

## 13. Verificación visual obligatoria

### 13.1. Preparar una comparación válida

1. Selecciona la referencia canónica y el estado preciso: tab activa, chat abierto, modal, filtro y posición de scroll.
2. Identifica el viewport CSS original cuando sea posible mediante HTML, medidas conocidas y metadatos. Las dimensiones del PNG no prueban por sí solas el viewport: puede ser full-page, estar escalado o tener otro deviceScaleFactor.
3. Renderiza la implementación con fuente cargada, assets resueltos y fixtures equivalentes.
4. Fija navegador, viewport, escala, locale, reloj/fechas y contenido. Espera estabilidad; desactiva animaciones, cursor parpadeante y aleatoriedad.
5. Captura el mismo tipo de imagen: viewport o página completa. No compares una captura full-page con un viewport de esa altura sin comprobar el caso.
6. Revisa lado a lado y, si las herramientas lo permiten, genera overlay/diff con el mismo encuadre.
7. Corrige, recaptura y registra las diferencias restantes.

No reduzcas toda la página con zoom/transform para hacerla caber en una captura. No modifiques la referencia ni recortes diferencias de layout para mejorar artificialmente el resultado.

### 13.2. Orden de corrección

1. Estructura y orden de secciones.
2. Anchos de navegación, paneles y canvas; offsets de header.
3. Alturas, separación, padding y alineación.
4. Tipografía: familia, pesos, tamaño, interlineado y wraps.
5. Assets, recortes y relación de aspecto.
6. Color, radio, borde y sombra.
7. Iconos y microalineaciones.
8. Estados activos, focus, loading y overlays.

No intentes corregir una diferencia de tipografía añadiendo márgenes arbitrarios.

### 13.3. Criterios de fidelidad medibles

- Ninguna sección de la referencia canónica omitida sin justificación registrada.
- Misma familia y peso de fuente, mismos tokens visuales resueltos y mismos assets disponibles.
- Misma jerarquía, orden de controles y composición en el viewport de referencia.
- Objetivo operativo, cuando la escala CSS esté confirmada: desalineaciones de anclas principales no mayores de 2px CSS y diferencias de cajas principales no mayores de 4px CSS. Excluir de esa comparación solo diferencias de datos o accesibilidad expresamente documentadas.
- Sin superposiciones, contenido invisible, texto cortado accidentalmente ni desbordamiento horizontal de página.
- Las diferencias de antialiasing pueden anotarse; no usar esa excusa para ignorar tamaños, posiciones o imágenes distintas.
- No afirmar un porcentaje de similitud sin método, dimensiones y métricas reproducibles. Un porcentaje global tampoco sustituye revisión humana de secciones importantes.

Si el viewport original no puede recuperarse con suficiente confianza, declarar la limitación, priorizar valores CSS de origen y composición, y marcar la comprobación geométrica como parcial. No inventar tolerancias medidas.

### 13.4. Resoluciones de QA adicionales

Probar, además del estado/canvas de referencia, al menos:

- 360×800: móvil estrecho.
- 390×844: móvil habitual.
- 768×1024: tablet.
- 1024×768: ancho crítico sin espacio para todos los rails.
- 1366×768: laptop.
- 1440×900: escritorio.

Estas son resoluciones de prueba propuestas, no medidas de los diseños originales. Revisar también texto ampliado y contenido largo. En layouts de varios paneles, comprobar los puntos intermedios donde una columna se oculta o se convierte en drawer.

### 13.5. Evidencias

Registrar en docs/THERS_VISUAL_QA.md por pantalla/estado:

| Campo | Contenido requerido |
| --- | --- |
| Referencia | ID del manifest y archivo fuente |
| Estado | Ruta, tab, selección, modal, scroll y fixture |
| Entorno | Navegador, viewport CSS, escala y modo de captura |
| Evidencia | Captura implementada y overlay/diff si existe |
| Resultado | Conforme, parcial, fallida o no ejecutada |
| Diferencias | Descripción, causa y corrección o excepción |

Guardar evidencias en una carpeta de QA fuera de los assets de producción. No añadir cientos de capturas al repositorio sin revisar sus convenciones y tamaño; documentar ubicación y comandos de reproducción.

Si no hay navegador/herramientas de captura disponibles, ejecutar build y pruebas posibles, pero declarar «verificación visual pendiente». No afirmar que una pantalla se vio bien sin verla.

## 14. Pruebas funcionales y de regresión

### 14.1. Estrategia

- Usar herramientas ya instaladas. Descubrir los comandos en package.json, configuración Python y documentación antes de ejecutarlos.
- Registrar la línea base para separar fallos previos de regresiones introducidas.
- Después de cada cambio importante, ejecutar checks focalizados. En hitos, ejecutar suite/build completos que correspondan.
- No usar credenciales, correos ni bases de producción. No guardar secretos en capturas, trazas, fixtures o informes.
- Si se incorpora una dependencia de tests, justificarla y mantenerla compatible; no sustituir la suite del equipo.

### 14.2. Matriz mínima de pruebas

| Área | Casos que deben comprobarse |
| --- | --- |
| Arranque/build | Instalación según lockfile, build, lint/typecheck disponibles, inicio frontend/backend sin regresiones |
| Auth existente | Registro/login válidos e inválidos; logout; /me protegido; token ausente/vencido; no loops de redirección |
| Recuperación/correo existente | Flujo vigente, errores, expiración e intentos/reenvío si hay OTP; transporte de correo simulado en tests |
| Perfil | Leer, modificar campos soportados, validación, conflicto/duplicado, cooldown real, error al guardar, recarga persistente |
| Navegación | Todas las rutas enlazadas, carga directa, atrás/adelante, menú activo, 404, acceso protegido |
| Feed | Carga, vacío, paginación, publicar, acciones sociales soportadas, fallo de API y rollback |
| Buscar | Consulta, filtros, sin resultados, error y respuestas fuera de orden |
| Perfiles ajenos | Público/privado/no encontrado/bloqueado; sin controles de edición propios |
| Mensajes | Lista, abrir chat, enviar/fallar/reintentar sin duplicado, paginación, permisos, borrador y retorno móvil |
| Audio/video | Cargar, reproducir, pausar, seek si aplica, fin, error, no múltiples audios accidentales, liberar micrófono |
| Radar | Permiso concedido/denegado, búsqueda manual, proveedor ausente, filtros y detalle; demo claramente identificada |
| Configuración | Cargar valores, cambiar, guardar, descartar, persistir/recargar, error y restablecimiento de valor |
| Overlays | Abrir/cerrar, foco, teclado, retorno al disparador, modal sobre navegación |
| Responsive | Sin scroll horizontal global, sin controles tapados, chat usable, rails colapsables |
| Producción | Mocks desactivados, sin secretos en bundle, sin dependencias CDN de prototipos |

No marques como aprobado un caso cuyo endpoint no existe. Usa «bloqueado: falta X», con alcance de UI que sí fue probado.

### 14.3. Registro honesto de comandos

Por cada verificación anota comando exacto, directorio de trabajo, resultado y resumen. Distingue:

- Ejecutado y aprobado.
- Ejecutado y fallido, indicando si era previo o introducido.
- No ejecutado por falta de herramienta/entorno.
- Bloqueado por una dependencia o decisión.

No uses «debería pasar» como equivalente de «pasó». No modifiques tests para aceptar un bug. Si una prueba es obsoleta por un cambio legítimo, documenta el cambio de comportamiento y su cobertura nueva.

## 15. Secuencia de ejecución con entregas verificables

### Etapa A — Inventario y línea base

Leer instrucciones y referencias, inventariar ambos ZIP/textos, detectar duplicados/daños, elegir canónicas, auditar stack/rutas y ejecutar checks iniciales.

Salida: manifest, riesgos y plan breve. No consumir toda la sesión documentando; comenzar inmediatamente con un cambio pequeño verificable una vez exista evidencia suficiente.

### Etapa B — Tokens y estructura

Centralizar tokens, fuente, iconografía, UI base, AppShell y navegación. Adaptar una pantalla representativa sin romper rutas existentes. Comprobar fidelidad y build antes de extender.

Salida: fundamentos realmente utilizados, no archivos de tokens sin consumidores.

### Etapa C — Primer recorrido real

Conectar usuario de sesión → navegación → perfil/editar perfil, preservando login y recuperación. Es un recorrido con backend conocido potencialmente verificable; si el repositorio demuestra otro orden de menor riesgo, documentarlo.

Salida: un flujo visual y funcional completo, con prueba y persistencia.

### Etapa D — Contenido y perfiles

Integrar Feed, Buscar, Videos/Cortos, Cápsulas y perfiles. En cada módulo conectar endpoints disponibles en ese momento; no dejar toda la integración de datos para el final.

Salida por módulo: UI, datos/estados, navegación, pruebas y límites explícitos.

### Etapa E — Mensajes y audio

Unificar variantes en bandeja/chat/contexto, conectar transporte existente, audio real cuando esté disponible y navegación responsive. Validar datos privados y evitar estados de seguridad ficticios.

### Etapa F — Radar y servicios

Implementar composición y adaptadores. Conectar solo servicios disponibles/autorizados. Registrar claramente mapa demostrativo, fuentes faltantes y funciones bloqueadas.

### Etapa G — Configuración completa

Migrar las 12 secciones con sus estructuras específicas. Conectar cada preferencia soportada y documentar pendientes sin fingir persistencia.

### Etapa H — Cierre y regresiones

Recorrer rutas, casos negativos, responsive, teclado y visual QA. Corregir regresiones, revisar git diff y actualizar documentación/estado final.

Tras cada etapa: explicar brevemente qué cambió, qué se verificó y qué sigue; continuar sin pedir confirmación innecesaria. Una dependencia bloqueada no cancela el resto del plan.

## 16. Documentación y memoria de trabajo

Crear o actualizar estos documentos en las rutas equivalentes del repositorio. No duplicar documentos existentes que ya cumplan el mismo propósito.

| Archivo | Contenido y fuente de verdad |
| --- | --- |
| docs/THERS_REFERENCE_MANIFEST.md | Inventario, referencias canónicas, parejas de archivos, duplicados, variantes y daños |
| docs/THERS_DESIGN_SYSTEM.md | Tokens resueltos, componentes, estados, layouts, responsive y excepciones respecto de referencia |
| docs/THERS_UI_INTEGRATION.md | Matriz de módulos/rutas, endpoints, pruebas, dependencias y estado del trabajo |
| docs/THERS_VISUAL_QA.md | Evidencia visual por pantalla/estado y diferencias pendientes |
| docs/THERS_INTEGRATION_PROGRESS.md | Checkpoint breve y actualizado para continuar una sesión interrumpida |

La documentación debe reflejar código real. No marcar completado algo que solo está especificado en este archivo. No copiar toda esta especificación en cada informe.

### 16.1. Matriz de integración

Por pantalla/capacidad registrar:

- Módulo y ruta real.
- Referencia y variante escogida.
- Componentes/archivos responsables.
- Estado UI: no iniciada / en curso / implementada.
- Estado visual: pendiente / parcial / verificada.
- Estado de datos: fixture / local explícito / API real / bloqueado.
- Estado funcional: pendiente / parcial / verificado.
- Endpoint y permisos, cuando existan.
- Tests/evidencias.
- Pendiente preciso y siguiente acción.

### 16.2. Contratos pendientes

Para cada capacidad sin backend, registrar una propuesta separada del contrato vigente:

~~~text
Capacidad:
Pantallas consumidoras:
Endpoint existente inspeccionado: ninguno / ruta real
Propuesta de método y ruta: PROPUESTA, no implementada
Autenticación y autorización necesarias:
Request y validaciones:
Response y campos:
Errores esperados:
Paginación / concurrencia / idempotencia:
Persistencia o proveedor necesario:
Dependencia y decisión pendiente:
Comportamiento actual de la UI sin esta capacidad:
~~~

No añadas rutas propuestas a la colección oficial de producción como si ya funcionaran. Si creas ejemplos de contrato, diferenciarlos claramente.

### 16.3. Checkpoint de continuidad

Actualizar al cerrar cada hito o antes de una interrupción:

~~~text
Última actualización:
Rama y estado de cambios locales:
Instrucciones/decisiones vigentes:
Etapa actual:
Terminado y evidencia:
En curso y archivos afectados:
Referencias ya procesadas:
Referencias aún pendientes:
Comandos ejecutados y resultados:
Bloqueos y lo que falta para resolverlos:
Próximas tres acciones concretas:
Comando seguro para volver a iniciar/pruebas:
~~~

Al continuar: leer checkpoint y manifest, comprobar git status y cambios posteriores del equipo, reanudar desde el estado real. No reiniciar la auditoría completa ni deshacer lo ya terminado. No confiar ciegamente en un checkpoint si el repositorio cambió después.

## 17. Lista de prohibiciones resumida

- No afirmar que viste archivos/capturas que no pudiste abrir.
- No afirmar que los dos ZIP fueron revisados hasta inventariarlos realmente.
- No interpretar un enlace en la sidebar como una integración backend ya especificada.
- No rediseñar por gusto ni simplificar omitiendo secciones.
- No usar screenshots como aplicación, iframes de maqueta ni HTML sueltos desconectados.
- No copiar Tailwind CDN, scripts inline o reset global de scroll del prototipo a producción.
- No ocultar una caída de API con datos mock automáticos.
- No mostrar mensajes de éxito si una operación no ocurrió.
- No fingir E2EE, verificación, presencia, pagos, envío de correo, descargas o datos en tiempo real.
- No publicar contenido ni contactar a personas reales durante pruebas.
- No reemplazar el usuario autenticado por una persona de la maqueta.
- No cambiar reglas de negocio por textos o números de muestra.
- No borrar cambios del equipo, hacer reset destructivo ni sobrescribir CLAUDE.md.
- No hacer push, merge, despliegue, gasto o contratación sin autorización.
- No declarar trabajo terminado si faltan pruebas o comparaciones; reportar cada límite.

## 18. Definición de terminado y entrega final

### 18.1. Comprobaciones de cierre

- [ ] Ambos ZIP y textos realmente disponibles están inventariados; materiales ausentes identificados.
- [ ] Cada pantalla tiene referencia canónica o está marcada como diseño derivado.
- [ ] Variantes y excepciones documentadas, sin decisiones visuales silenciosas.
- [ ] Tokens centralizados y utilizados; no configuraciones contradictorias por página.
- [ ] Componentes/shell reutilizados; no duplicación de aplicación por referencia.
- [ ] Todas las pantallas dentro del alcance tienen navegación y estados coherentes.
- [ ] Endpoints existentes integrados; ninguna función real sustituida por un mock.
- [ ] Auth, perfil, correo/recuperación y otras funciones existentes no tienen regresiones introducidas.
- [ ] Funciones nuevas pendientes distinguidas de UI terminada.
- [ ] Producción sin fixtures activos, claves privadas ni afirmaciones engañosas.
- [ ] Responsive/teclado/estados negativos comprobados.
- [ ] Visual QA ejecutado o señalado explícitamente como pendiente donde no fue posible.
- [ ] Build, lint, tests disponibles ejecutados y resultados registrados.
- [ ] git diff revisado: sin archivos temporales/secretos ni cambios ajenos borrados.
- [ ] Documentación y checkpoint actualizados.

«Integración total completada» solo procede si todos los módulos acordados tienen funcionalidad real verificada y no hay bloqueos relevantes. Si faltan proveedores/endpoints, usar «integración visual terminada; integración funcional parcial» u otra descripción exacta.

### 18.2. Informe final a entregar al usuario

1. Resumen corto de lo logrado, sin prometer capacidades no implementadas.
2. Tabla de módulos con estado visual y funcional por separado.
3. Archivos principales creados/modificados y decisiones relevantes.
4. Endpoints realmente usados y capacidades pendientes.
5. Pruebas/comandos ejecutados, resultados y fallos previos conocidos.
6. Capturas/evidencias disponibles y diferencias visuales sin resolver.
7. Instrucciones exactas, verificadas, para arrancar y probar localmente.
8. Bloqueos que requieren al propietario y siguiente acción concreta.
9. Comandos Git sugeridos para guardar cambios, sin ejecutarlos ni incluir archivos sensibles.

Empieza ahora. Tu prioridad es convertir las referencias de THERS en una aplicación coherente, fiel y verificable, conservando el trabajo existente y dejando evidencia clara de lo que sí funciona y lo que todavía falta.
