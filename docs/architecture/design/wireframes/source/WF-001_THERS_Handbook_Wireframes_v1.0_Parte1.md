# WF-001 — THERS Handbook Wireframes v1.0

## Parte 1 de 2 — Planificación (sin wireframes, sin diagramas, sin código)

| Campo | Valor |
|---|---|
| Documento | WF-001 — Fase de planificación |
| Versión | 1.0 |
| Estado | Borrador para revisión — base de la Parte 2 (wireframes visuales) |
| Depende de | *Arquitectura UX del Handbook v0.1* (sitemap, navegación, arquitectura del portal) · *THERS Handbook Design System v1.0* (componentes, tokens, principios visuales) |
| No modifica | Ninguna decisión ya tomada en los documentos anteriores. Este documento traduce esas decisiones en flujos de interacción concretos, previo a dibujarlos. |

---

## 1. Introducción

WF-001 es el documento que traduce la arquitectura del Handbook (sitemap, componentes, tokens) en **cómo se mueve una persona real a través de él**. Hasta ahora se ha definido *qué existe* (categorías, componentes, colores) y *cómo se ve cada pieza* (Design System v1.0). Falta la pieza que conecta ambas cosas: *qué hace un usuario, en qué orden, y qué encuentra en cada paso*.

Esta Parte 1 es deliberadamente texto puro. Antes de dibujar una sola caja o flecha, el equipo necesita acuerdo explícito sobre la lógica de navegación — de lo contrario, cualquier wireframe que se produzca después estaría resolviendo visualmente un problema que aún no se ha pensado del todo. Dibujar antes de tiempo tiende a fijar decisiones de flujo por accidente, solo porque "ya quedó dibujado así".

La Parte 2 de WF-001 tomará cada flujo y cada plantilla de página definidos aquí y los representará como wireframes de baja fidelidad (cajas, jerarquía, disposición — sin estilo visual todavía, que corresponde a una fase posterior de prototipo).

---

## 2. Objetivos

- Definir la **lógica de interacción** del Handbook de forma independiente de su representación visual, para que la Parte 2 dibuje flujos ya validados, no flujos improvisados sobre la marcha.
- Establecer un **inventario cerrado de plantillas de página** (sección 3.2) que sirva como lista de trabajo exacta para los wireframes de la Parte 2 — ni una plantilla de más, ni una de menos.
- Garantizar que los **cinco planos de navegación** (global, local, contextual, secuencial, utilitaria — sección 5) estén definidos con precisión suficiente como para que cualquier página nueva del Handbook sepa exactamente qué mecanismos de navegación le corresponden.
- Responder, sin ambigüedad, las cinco preguntas de flujo de usuario exigidas en el alcance de este documento (sección 6): llegada de un usuario nuevo, llegada a un documento, retorno, cambio de categoría, y navegación entre documentos.
- Detectar **vacíos o contradicciones** con la Arquitectura UX v0.1 o el Design System v1.0 antes de que lleguen a un wireframe — es más barato corregir una frase en este documento que rehacer una maqueta visual.

---

## 3. Alcance

### 3.1 Qué cubre este documento

- Arquitectura de navegación a nivel de **planos e interacción** (no de estilo — eso ya está resuelto en el Design System v1.0).
- Flujos de usuario de extremo a extremo, descritos en prosa y, donde aporte claridad, en tablas de pasos.
- El inventario de plantillas de página que la Parte 2 deberá wireframear.
- Los principios UX específicos de navegación y flujo (distintos de los principios visuales ya cubiertos en el Design System, sección 2 de ese documento).

### 3.2 Inventario de plantillas (insumo directo para la Parte 2)

Toda página del Handbook pertenece a exactamente una de estas plantillas. No existen páginas "híbridas" ni excepciones de plantilla por categoría — esto es intencional: es lo que permite que el Handbook escale (Design System v1.0, sección 15) sin que cada categoría nueva invente su propia estructura.

| Plantilla | Ejemplo de página que la usa | Elemento distintivo |
|---|---|---|
| **Home / Landing** | `/` | Única página con tarjetas de categoría como navegación primaria; no tiene Sidebar de contenido ni TOC |
| **Category Index** | `/ingenieria`, `/academy` | Listado de páginas/subcategorías hijas; puede o no tener Sidebar poblado según si ya se entró a la categoría |
| **Document Page** | `/ingenieria/git/commits-y-prs` | La plantilla dominante — más del 90% del contenido del Handbook vive aquí |
| **ADR Index / ADR Detail** | `/arquitectura/decisiones` | Variante de Document Page con Timeline (Design System v1.0, sección 9.8) como elemento adicional |
| **404 / No encontrado** | cualquier ruta inválida | Sin Sidebar de contenido; ofrece buscador y accesos rápidos a categorías raíz |
| **Changelog global** | `/meta/changelog-del-handbook` | Variante de Document Page con Timeline en lugar de prosa continua |

*(El Buscador no es una plantilla de página: es un componente modal superpuesto, según Design System v1.0 sección 9.12 — no existe una URL de "página de resultados" independiente en esta versión.)*

### 3.3 Qué NO cubre este documento

- Disposición visual, cajas, jerarquía espacial o wireframes (Parte 2 de WF-001).
- Cualquier decisión de color, tipografía, espaciado o iconografía (ya cerrado en el Design System v1.0 — este documento no las reabre).
- Cualquier cambio al sitemap o a las 8 categorías raíz (ya cerrado en Arquitectura UX v0.1 — este documento asume esa estructura como dada).
- Código o implementación de cualquier tipo.

---

## 4. Principios UX

Estos principios son específicos de **navegación y flujo**. Complementan, sin repetir, los principios visuales ya definidos en el Design System v1.0 (sección 2: Claridad, Consistencia, Simplicidad, Escalabilidad, Accesibilidad, Legibilidad, Mantenibilidad).

| Principio | Qué significa para la navegación |
|---|---|
| **Orientación constante** | En cualquier punto del Handbook, el usuario puede responder sin esfuerzo tres preguntas: ¿en qué categoría estoy?, ¿en qué documento estoy?, ¿en qué parte del documento estoy? Los tres planos de navegación (sección 5) existen exactamente para sostener esto. |
| **Recuperabilidad** | Ninguna acción de navegación es un callejón sin salida. Siempre existe un camino de regreso visible sin depender de la memoria del usuario ni del botón "atrás" del navegador (aunque ese también funcione — ver sección 6.3). |
| **Predictibilidad** | El mismo tipo de acción produce el mismo resultado en cualquier parte del Handbook. Un click en el wordmark siempre va a Home; un click en un breadcrumb siempre va a esa categoría; nunca hay una excepción "solo en esta sección". |
| **Entrada no lineal** | Se asume que la mayoría de las visitas **no** empiezan en Home. Un usuario recurrente llega directo a un documento vía búsqueda, un link compartido en Slack, o un enlace desde el código (comentario con URL al Handbook). Cada Document Page debe ser completamente autosuficiente en orientación, sin depender de que el usuario "haya pasado por Home primero". |
| **Divulgación progresiva** | La navegación global (Sidebar) muestra un nivel de profundidad por defecto; el resto se revela solo cuando es relevante (rama activa). Esto evita que un usuario nuevo enfrente el árbol completo de 8 categorías × N subcategorías de una sola vez. |
| **Costo de cambio mínimo entre categorías** | Cambiar de categoría (ej. de Backend a PostgreSQL) no debe sentirse como "salir" del Handbook y "volver a entrar" — es un movimiento lateral de un click, no un regreso a Home obligatorio (detalle en sección 6.4). |
| **Consistencia de patrón entre plantillas** | Las seis plantillas de la sección 3.2 comparten el mismo lenguaje de navegación (mismos planos, sección 5); lo único que cambia es qué tan poblado está cada plano según el tipo de página. |

---

## 5. Arquitectura de navegación

Se definen **cinco planos de navegación**, cada uno respondiendo un tipo de pregunta distinto. Todo mecanismo de navegación del Handbook pertenece a exactamente uno de estos planos — si un futuro componente no encaja en ninguno, es señal de que se está mezclando responsabilidades (y debe revisarse contra el principio de Simplicidad del Design System).

| Plano | Pregunta que responde | Mecanismo(s) | Alcance |
|---|---|---|---|
| **1. Global** | ¿Qué existe en todo el Handbook? | Sidebar (árbol completo de categorías) · Wordmark (regreso a Home) | Persistente en todas las plantillas salvo Home |
| **2. Local** | ¿Dónde estoy dentro de esta categoría? | Sidebar (rama expandida) · Breadcrumbs | Persistente dentro de una categoría; cambia al cruzar a otra |
| **3. Contextual** | ¿Dónde estoy dentro de este documento? | Tabla de Contenidos (TOC) · scroll-spy | Exclusivo de Document Page y sus variantes |
| **4. Secuencial** | ¿Qué sigue o qué venía antes en este recorrido? | Prev/Next al pie del documento | Solo en categorías con orden lógico definido (`order` en frontmatter — Arquitectura UX v0.1, sección 14) |
| **5. Utilitaria** | ¿Cómo hago algo que no es "moverme por el árbol"? | Buscador · Toggle de tema · Enlace a GitHub / Editar página | Persistente, vive en el Header en todas las plantillas |

**Por qué cinco planos y no un solo "menú"**: cada uno resuelve una necesidad distinta y coexiste sin competir porque ninguno duplica al otro. El Sidebar nunca intenta mostrar "dónde estoy dentro del documento" (eso es trabajo del TOC); el TOC nunca intenta mostrar "qué otras categorías existen" (eso es trabajo del Sidebar). Esta separación es la que permite que el Handbook escale sin que la navegación se vuelva una sola estructura sobrecargada (Design System v1.0, sección 15).

**Jerarquía de persistencia**: los planos 1, 2 y 5 son visibles de forma constante (con las adaptaciones responsive ya definidas en Design System v1.0, sección 11). El plano 3 solo existe cuando hay contenido que lo justifique (una página corta sin subsecciones no muestra TOC vacío). El plano 4 solo existe cuando la categoría tiene un orden editorial explícito — no todas lo tienen (ej. Playbooks son independientes entre sí; Git sí tiene un orden pedagógico de lectura).

---

## 6. Flujo general del usuario

### 6.1 Cómo navegará un usuario nuevo

Un usuario nuevo (ej. un integrante que se incorpora al equipo THERS) entra por Home con alta probabilidad, ya sea porque se le compartió la URL raíz o porque hizo click en el wordmark desde cualquier otro punto. Home no presenta el árbol completo de navegación (Sidebar) de inmediato: presenta las 8 categorías raíz como unidades independientes, cada una con una descripción breve de una línea que responde "¿qué voy a encontrar aquí?" antes de que el usuario tenga que hacer click para averiguarlo.

El camino esperado para un usuario nuevo es: Home → identifica la categoría relevante para su necesidad inmediata (con alta probabilidad, `Academy` si es su primer día) → entra a la Category Index de esa categoría, donde ahora sí aparece el Sidebar completo, pero con la rama de esa categoría ya expandida y el resto colapsado → elige la primera Document Page relevante.

A partir de ese primer click hacia una categoría, el usuario nunca vuelve a ver el estado "sin Sidebar" salvo que regrese explícitamente a Home — es decir, la experiencia de un usuario nuevo se diferencia de la de uno recurrente únicamente en el punto de entrada (Home vs. entrada directa), no en el sistema de navegación en sí, que es idéntico para ambos desde el segundo click en adelante (principio de Predictibilidad, sección 4).

### 6.2 Cómo llegará hasta un documento

Se identifican cuatro rutas de llegada a una Document Page, sin jerarquía de preferencia entre ellas — el diseño debe soportar las cuatro igual de bien, no privilegiar una asumiendo que es "la normal":

| Ruta | Descripción | Implicación de diseño |
|---|---|---|
| **Exploración** | Home → Category Index → Document Page | La ruta del usuario nuevo (6.1). Requiere que las descripciones de categoría en Home sean lo bastante precisas para no generar clicks de "prueba y error". |
| **Búsqueda directa** | Cualquier página → `Ctrl/Cmd+K` → resultado → Document Page | La ruta dominante para usuarios recurrentes. El documento debe poder "aterrizarse" sin haber pasado por su Category Index — por eso el plano Local (breadcrumbs) es obligatorio incluso llegando por esta ruta. |
| **Enlace directo / compartido** | Un link pegado en Slack, en un comentario de código, o en otro documento del propio Handbook | Equivale a llegar "en frío": el usuario puede no tener ningún contexto previo de navegación. Esta ruta es la prueba de estrés del principio de Entrada no lineal (sección 4): la página debe explicarse a sí misma sin depender de un recorrido previo. |
| **Referencia cruzada** | Desde dentro de otro documento, vía un enlace "Ver también" en el contenido | El usuario ya está "dentro" del sistema de navegación; esta ruta no requiere reorientación adicional, solo actualización del plano Local/Contextual al nuevo documento. |

En las cuatro rutas, el resultado final es el mismo estado de página: Sidebar con la rama correcta expandida, Breadcrumbs completos, y TOC poblado — sin importar cómo se llegó. Esto es deliberado: la ruta de llegada no debe ser reconstruible ni relevante una vez que el usuario ya está en la página (no hay un estado "llegué por búsqueda" visualmente distinto de "llegué navegando").

### 6.3 Cómo regresará

Existen tres mecanismos de retorno, disponibles simultáneamente y sin que el usuario deba elegir cuál "es el correcto" para su situación:

1. **Breadcrumbs** — retorno dirigido a un nivel específico de la jerarquía (ej. saltar directo a la Category Index desde un documento profundo, sin pasar por niveles intermedios).
2. **Sidebar** — retorno lateral a cualquier otro documento de la misma categoría, sin necesidad de "subir" primero a la Category Index.
3. **Botón atrás del navegador** — dado que cada plantilla corresponde a una URL real y estable (arquitectura SSG, Arquitectura UX v0.1 sección 1), el botón atrás nativo del navegador siempre reproduce fielmente el estado anterior. Esto no es un mecanismo que el Handbook "implemente", pero sí uno que el diseño no puede romper (ninguna navegación puede depender exclusivamente de JavaScript sin URL correspondiente).

No existe un botón "Volver" explícito y genérico en la interfaz (del tipo "‹ Atrás") **porque sería ambiguo**: no está claro si "atrás" significa el documento anterior en el orden secuencial (plano 4), el nivel superior en la jerarquía (breadcrumbs), o la página previamente visitada (navegador). En lugar de resolver esa ambigüedad con un solo botón sobrecargado, se ofrecen los tres mecanismos específicos de arriba, cada uno inequívoco en lo que hace.

### 6.4 Cómo cambiará de categoría

Cambiar de categoría (ej. de `Ingeniería/Backend` a `Playbooks`) es un movimiento lateral de **un solo click**, disponible desde cualquier Document Page sin necesidad de regresar a Home primero:

- **Vía Sidebar**: el usuario hace click en otra categoría raíz directamente en el árbol global (plano 1, siempre visible). La rama de la categoría anterior se colapsa automáticamente y la nueva se expande — el Sidebar nunca muestra dos categorías expandidas a la vez, para preservar la Divulgación progresiva (sección 4).
- **Vía Breadcrumbs**: solo permite "subir" dentro de la misma categoría, no cambiar a una distinta — es una herramienta de plano Local, no Global. Se documenta aquí para dejar explícito qué mecanismo **no** sirve para este flujo, y evitar que la Parte 2 lo diseñe incorrectamente como atajo de cambio de categoría.
- **Vía Home**: siempre disponible como ruta alternativa (click en wordmark → elegir nueva categoría desde las tarjetas), preferible cuando el usuario no tiene claro a qué categoría específica quiere ir, solo que quiere "algo distinto".

Al cambiar de categoría, el plano Contextual (TOC) y el Secuencial (Prev/Next) se reinician por completo — no existe continuidad de esos dos planos entre categorías distintas, ya que ambos son propiedades del documento/categoría actual, no del usuario.

### 6.5 Cómo funcionará la navegación entre documentos

Dentro de una misma categoría, se distinguen dos formas de moverse entre documentos, correspondientes a dos planos distintos (sección 5) y usadas en momentos distintos del recorrido:

- **Navegación secuencial (plano 4)**: para categorías con un orden pedagógico claro (Academy, Git, Playbooks de un mismo flujo), el enlace Prev/Next al pie de cada documento avanza al siguiente en el orden definido por el campo `order` del frontmatter (Arquitectura UX v0.1, sección 14). Esta es la forma de navegación que se usa durante una **lectura guiada** — el usuario no decide activamente el destino, confía en el orden ya curado.
- **Navegación directa (plano 1, vía Sidebar)**: para saltar a un documento específico sin seguir el orden secuencial (ej. un usuario que ya sabe exactamente qué necesita, como "convención de commits"), el Sidebar permite ir directo a cualquier documento de la rama expandida, sin pasar por los documentos intermedios. Esta es la forma de navegación que se usa durante una **consulta puntual**.
- **Navegación cruzada (referencia dentro del contenido)**: un tercer mecanismo, ya anticipado en 6.2, permite moverse entre documentos de **distintas** categorías cuando existe una relación temática directa (ej. desde PostgreSQL hacia Backend al hablar de migraciones). Este enlace vive dentro del cuerpo del contenido, no en la navegación persistente, y es la única forma de navegación entre documentos que cruza categorías sin pasar por el Sidebar global.

En los tres casos, el documento de destino se comporta exactamente igual que si se hubiera llegado por cualquiera de las cuatro rutas de la sección 6.2: mismo estado de Sidebar, Breadcrumbs y TOC actualizados, sin distinción visual de "cómo llegué aquí".

---

*Fin de la Parte 1 de WF-001. La Parte 2 tomará el inventario de plantillas (sección 3.2), los cinco planos de navegación (sección 5) y los cinco flujos de usuario (sección 6) como especificación cerrada, y los representará como wireframes de baja fidelidad — cajas, jerarquía y disposición, sin estilo visual todavía.*
# WF-001 — THERS Handbook Wireframes v1.0

## Parte 2 de 2 — Wireframes de baja fidelidad (sin color, sin código, sin prototipo visual)

| Campo | Valor |
|---|---|
| Documento | WF-001 — Parte 2: Wireframes |
| Versión | 1.0 |
| Estado | Borrador para revisión |
| Continúa de | Parte 1 (Introducción, Objetivos, Alcance, Principios UX, Arquitectura de navegación, Flujo general del usuario) — **no modificada** |
| Valida contra | STD-001 · ARC-001 · DS-001 (ver mapeo en sección 7.1 y validación final en sección 11) |

Esta parte continúa la numeración de secciones de la Parte 1 (que cerró en la sección 6).

---

## 7. Notas de diseño previas a los wireframes

Antes de dibujar, dos elementos solicitados para esta Parte 2 no estaban explícitamente resueltos —o estaban resueltos en sentido contrario— en los documentos ya aprobados. Como Principal UX Architect, prefiero dejarlo señalado y proponer una resolución concreta, en vez de dibujarlo en silencio y generar una inconsistencia entre documentos oficiales.

### 7.1 Mapeo de códigos de documento

Para la validación de la sección 11:

| Código | Documento |
|---|---|
| **STD-001** | Manual de Organización THERS (estándar de procesos y roles del equipo) |
| **ARC-001** | Arquitectura UX del Handbook v0.1 (arquitectura del portal, sitemap, navegación) |
| **DS-001** | THERS Handbook Design System v1.0 (tokens, componentes, principios visuales) |

### 7.2 Sidebar en Home

ARC-001 y la Parte 1 de WF-001 (sección 3.2) establecen que Home **no tiene Sidebar de contenido**. DS-001 (sección 5) refuerza esto: el plano Global es *"persistente en todas las plantillas salvo Home"*.

Esta Parte 2 solicita explícitamente un Sidebar en el wireframe de Home. Resolución propuesta: Home muestra el Sidebar en su **estado colapsado a iconos** — el mismo estado ya definido como válido en DS-001 (sección 10, "colapsado a franja de solo iconos"), no el árbol expandido de contenido. Esto satisface la necesidad de tener el plano Global visible desde Home sin contradecir el rol de Home como punto de entrada limpio, orientado a las tarjetas de categoría como navegación primaria (ARC-001, WF-001 Parte 1 sección 6.1).

**Queda marcado como pendiente de ratificación** en DS-001 §5 y ARC-001, no como una modificación silenciosa de esos documentos.

### 7.3 Footer en Página de Documento

DS-001 (sección 9.3) establece que el Footer completo aparece *"solo en Home y páginas índice de categoría, no en páginas de contenido largas, donde el Footer añadiría scroll innecesario"*.

Esta Parte 2 solicita explícitamente un Footer en el wireframe de Página de Documento. Resolución propuesta: la Página de Documento incluye una **variante condensada de una sola línea** (link "Editar en GitHub" + número de versión del Handbook), distinta del Footer completo multi-columna de Home/Categoría — preserva la señal de "fin de página" sin el costo de scroll adicional que DS-001 buscaba evitar.

**Queda marcado como pendiente de ratificación** en DS-001 §9.3, vía el proceso de cambio menor ya definido en su sección 16 (Gobernanza).

Con ambos puntos señalados, se procede a los tres wireframes.

---

## 8. Wireframe — Home

```
┌────────────────────────────────────────────────────────────────────────┐
│ HEADER                                                                  │
│  [2] LOGO/WORDMARK        [3] Buscar en el Handbook... (Ctrl+K)  [⚙][↗] │
├────┬─────────────────────────────────────────────────────────────────┤
│    │                                                                 │
│    │                        [5] HERO                                │
│    │              "THERS Engineering Handbook"                      │
│    │        Tagline: qué es y para qué sirve, en una línea          │
│    │                                                                 │
│    ├─────────────────────────────────────────────────────────────────┤
│    │                    [6] CATEGORÍAS (grid 4×2)                   │
│[4] │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│SI  │  │Organización│ │Estrategia │ │Arquitectura│ │Ingeniería │      │
│DE  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
│BAR │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│(i- │  │  Academy  │ │ Playbooks │ │  Roadmap  │ │   Meta    │       │
│co- │  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
│nos │  ├─────────────────────────────────────────────────────────────┤
│co- │  │              [7] ACCESOS RÁPIDOS                            │
│la- │  │  [Cómo contribuir] [Convención de commits] [Onboarding] [+] │
│p-  │  ├─────────────────────────────────────────────────────────────┤
│sa- │  │             [8] MANUALES DESTACADOS                         │
│do) │  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│    │  │  │ HB-001         │  │ Plan Estrat.   │  │ Arquitectura   │  │
│    │  │  │ Manual de Org. │  │ IA             │  │ del Sistema    │  │
│    │  │  └───────────────┘  └───────────────┘  └───────────────┘   │
│    │  ├─────────────────────────────────────────────────────────────┤
│    │  │          [9] ÚLTIMAS ACTUALIZACIONES                        │
│    │  │  • 24 jul · Convención de commits actualizada · [Git]       │
│    │  │  • 20 jul · Nuevo Playbook de release · [Playbooks]         │
│    │  │  • 15 jul · Plan Estratégico IA revisado · [Estrategia]     │
│    │                                                                 │
├────┴─────────────────────────────────────────────────────────────────┤
│ [10] FOOTER — Versión del Handbook · Cómo contribuir · © THERS         │
└──────────────────────────────────────────────────────────────────────┘
```

### Propósito de cada sección

| # | Sección | Propósito |
|---|---|---|
| 1 | **Header** | Chrome persistente y utilitario (DS-001 §9.1). Es lo único garantizado idéntico en cualquier punto del Handbook — ancla de orientación mínima. |
| 2 | **Logo** | Identidad del sistema (DS-001 §3.2) y ancla de retorno instantáneo a Home desde cualquier página — cumple el principio de Predictibilidad (WF-001 Parte 1, §4). |
| 3 | **Buscador** | Punto de entrada al plano Utilitario (WF-001 Parte 1, §5). En Home además funciona como invitación explícita: para un usuario recurrente, buscar es más rápido que explorar tarjetas. |
| 4 | **Sidebar (icono, colapsado)** | Mantiene el plano Global accesible sin competir visualmente con el propósito de bienvenida de Home. Un click lo expande al árbol completo si el usuario prefiere navegar por estructura en vez de por tarjetas. Ver nota de reconciliación §7.2. |
| 5 | **Hero** | Primer momento de orientación para un usuario nuevo (WF-001 Parte 1, §6.1): responde "¿qué es esto?" antes de pedir cualquier decisión de navegación. |
| 6 | **Categorías** | Navegación primaria de Home, mapea 1:1 con las 8 categorías raíz del sitemap (ARC-001). Cada tarjeta responde "¿qué voy a encontrar aquí?" sin necesidad de entrar — reduce navegación de prueba y error. |
| 7 | **Accesos rápidos** | Atajo directo a páginas de alta frecuencia de consulta, evitando el recorrido completo Categoría → Documento para lo que el equipo consulta más seguido. |
| 8 | **Manuales destacados** | Curaduría editorial (no algorítmica) de documentos que el equipo decide que todos deben conocer, independientemente de en qué categoría vivan. |
| 9 | **Últimas actualizaciones** | Comunica que el Handbook es un documento vivo, ligado al Changelog global (ARC-001 §2) y a la cadencia de revisión mensual (STD-001 §6) — incentiva revisitar en vez de asumir que "ya lo leí una vez". |
| 10 | **Footer** | Metadatos de versión y gobernanza (DS-001 §9.3), consistente en todas las plantillas que lo incluyen. |

---

## 9. Wireframe — Página de Documento

*(Representando HB-001 — Manual de Organización)*

```
┌────────────────────────────────────────────────────────────────────────┐
│ [1] HEADER — Logo   Buscar (Ctrl+K)                            [⚙][↗]   │
├────────────┬───────────────────────────────────────┬───────────────────┤
│            │ [3] BREADCRUMBS                        │                   │
│            │  Home › Organización › Manual de Org.  │                   │
│            ├─────────────────────────────────────────┤                   │
│            │ [4] INFORMACIÓN DEL DOCUMENTO           │                   │
│            │  HB-001 — Manual de Organización        │                   │
│            │  [Estable]  Owner: —  Últ. act.: 26 jul │                   │
│            ├─────────────────────────────────────────┤  [5] TABLA DE    │
│ [2]        │ [6] CONTENIDO PRINCIPAL                  │  CONTENIDOS      │
│ SIDEBAR    │                                         │  "En esta página"│
│ (árbol     │  0. Propósito y alcance del documento    │  • 0. Propósito  │
│ completo,  │  Texto de cuerpo del manual...           │  • 1. Organigr.  │
│ rama       │                                         │  • 2. Roles      │
│ "Organiza- │  ┃ [6a] CALLOUT — Nota                  │  • 3. Respons. ● │
│ ción"      │  ┃  Aclaración breve relevante a la      │    3.1           │
│ expandida, │  ┃  sección anterior.                    │    3.2           │
│ página     │                                         │  • 4. Diarias    │
│ actual     │  1. Organigrama                          │  • 5. Semanales  │
│ resaltada) │  [ Figura — organigrama del equipo ]     │  • 6. Mensuales  │
│            │                                         │  ...             │
│            │  3. Responsabilidades                    │                   │
│            │  [6b] BLOQUE DE CÓDIGO                   │                   │
│            │  ┌─ ejemplo.sql ──────────── [Copiar] ─┐ │                   │
│            │  │ SELECT * FROM roles;                │ │                   │
│            │  └──────────────────────────────────────┘ │                   │
│            │  (placeholder — HB-001 no tiene código  │                   │
│            │   propio; reservado para manuales        │                   │
│            │   técnicos futuros: Backend, Git, etc.)  │                   │
│            ├─────────────────────────────────────────┴───────────────────┤
│            │ [7] ‹ Anterior: —                    Siguiente: Roles ›      │
├────────────┴───────────────────────────────────────────────────────────┤
│ [8] FOOTER (condensado) — Editar esta página en GitHub · v1.0            │
└────────────────────────────────────────────────────────────────────────┘
```

### Propósito de cada área

| # | Área | Propósito |
|---|---|---|
| 1 | **Header** | Igual que en Home — chrome persistente, garantiza que buscar y volver a Home cuesten siempre lo mismo (un click), sin importar qué tan profundo esté el usuario. |
| 2 | **Sidebar** | Plano Global + Local simultáneos (WF-001 Parte 1, §5): muestra el árbol completo con la rama de "Organización" expandida y HB-001 resaltado. Responde "¿dónde estoy dentro de todo el Handbook?" sin que el usuario tenga que mirar los breadcrumbs. |
| 3 | **Breadcrumbs** | Plano Local (DS-001 §9.4): retorno dirigido a cualquier nivel superior de la jerarquía en un click, sin pasar por niveles intermedios (WF-001 Parte 1, §6.3). |
| 4 | **Información del documento** | Confianza y contexto inmediato: el badge de estado le dice al lector si el contenido es confiable *antes* de invertir tiempo leyéndolo (DS-001 §14, convención de badge obligatorio). |
| 5 | **Tabla de contenidos** | Plano Contextual (WF-001 Parte 1, §5): responde "¿dónde estoy dentro de este documento?", con scroll-spy marcando la sección activa — crítico en un documento tan largo como HB-001. |
| 6 | **Contenido principal** | El propósito central de la plantilla; ancho limitado a la columna de lectura (DS-001 §8.1) para proteger la longitud de línea. |
| 6a | **Callouts** | Destacan información que no debe leerse "al mismo nivel" que el resto del párrafo (una aclaración, una advertencia) sin interrumpir el flujo de lectura principal (DS-001 §9.15). |
| 6b | **Bloques de código** | HB-001 no los usa hoy, pero la plantilla debe soportarlos desde el inicio: los futuros manuales de Backend, PostgreSQL, Docker y Git son, en esencia, esta misma plantilla con más bloques de código y menos prosa. |
| 7 | **Navegación Anterior/Siguiente** | Plano Secuencial (WF-001 Parte 1, §5 y §6.5): permite lectura guiada dentro de una categoría con orden editorial, sin que el usuario tenga que volver al Sidebar para avanzar. |
| 8 | **Footer condensado** | Cierre de página sin el costo de scroll de un footer completo (ver nota de reconciliación §7.3); mantiene visible el acceso de edición, que es la acción de footer más usada en un contexto de documentación técnica. |

---

## 10. Wireframe — Página de Categoría

*(Representando la categoría Ingeniería)*

```
┌────────────────────────────────────────────────────────────────────────┐
│ HEADER — Logo   Buscar global (Ctrl+K)                          [⚙][↗] │
├────────────┬─────────────────────────────────────────────────────────┤
│            │ [1] ENCABEZADO DE CATEGORÍA                              │
│            │   💻 Ingeniería                                          │
│            ├───────────────────────────────────────────────────────────┤
│            │ [2] DESCRIPCIÓN                                          │
│            │   Frontend, Backend, PostgreSQL, Docker y Git — todo lo   │
│            │   necesario para construir y mantener el producto THERS. │
│ SIDEBAR    ├───────────────────────────────────────────────────────────┤
│ (árbol,    │ [5] BUSCADOR (local)      [4] FILTROS                    │
│ rama       │  "Buscar en Ingeniería..."  [Frontend][Backend][DB][+2]  │
│ "Ingenier- ├───────────────────────────────────────────────────────────┤
│ ía"        │ [6] ETIQUETAS (tag cloud de la categoría)                │
│ expandida) │  #react  #flask  #jwt  #migraciones  #docker  #ci        │
│            ├───────────────────────────────────────────────────────────┤
│            │ [3] TARJETAS DE DOCUMENTOS (grid)                        │
│            │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│            │  │Convenciones │ │API Flask    │ │Esquema de   │           │
│            │  │React        │ │[Estable]    │ │datos        │           │
│            │  │[Estable]    │ │#backend     │ │[Draft]      │           │
│            │  │#frontend    │ │             │ │#postgresql  │           │
│            │  └────────────┘ └────────────┘ └────────────┘            │
│            │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│            │  │Entorno local│ │Ramas y      │ │Code review  │           │
│            │  │Docker       │ │convenciones │ │[Estable]    │           │
│            │  │#docker      │ │#git         │ │#git         │           │
│            │  └────────────┘ └────────────┘ └────────────┘            │
│            ├───────────────────────────────────────────────────────────┤
│            │ [7] ESTADÍSTICAS BÁSICAS                                  │
│            │  14 documentos · 2 en Draft · última act. hace 3 días     │
├────────────┴───────────────────────────────────────────────────────────┤
│ [8] FOOTER — Versión del Handbook · Cómo contribuir · © THERS            │
└──────────────────────────────────────────────────────────────────────┘
```

### Por qué existe cada componente y cómo mejora la experiencia

| # | Componente | Por qué existe / cómo mejora la experiencia |
|---|---|---|
| 1 | **Encabezado** | Confirma de inmediato, en el nivel más alto de jerarquía visual, en qué categoría está el usuario — refuerza el plano Local justo al entrar (WF-001 Parte 1, §6.4). |
| 2 | **Descripción** | Extiende la descripción de una línea que ya vio en la tarjeta de Home (§8, zona 6): un usuario que llegó por búsqueda o link directo, sin haber pasado por Home, también recibe ese contexto aquí. |
| 3 | **Tarjetas de documentos** | Reemplaza al Sidebar como forma primaria de explorar el contenido de la categoría cuando el usuario aún no sabe qué documento específico busca — más espacio para mostrar estado, etiquetas y descripción que un ítem de árbol lateral. |
| 4 | **Filtros** | Con una categoría como Ingeniería (5 subcategorías: Frontend, Backend, PostgreSQL, Docker, Git), filtrar por subcategoría evita que el usuario tenga que escanear visualmente 14+ tarjetas para encontrar las 3 relevantes. |
| 5 | **Buscador (local)** | Distinto del buscador global del Header: busca *solo* dentro de los documentos de esta categoría — más rápido y más preciso que una búsqueda global cuando el usuario ya sabe en qué categoría está parado. |
| 6 | **Etiquetas** | Ruta de descubrimiento alternativa a la jerarquía de carpetas: un documento sobre JWT vive en Backend, pero la etiqueta `#jwt` lo hace encontrable también desde una intención distinta ("quiero todo lo relacionado a autenticación"). |
| 7 | **Estadísticas básicas** | Señal rápida de salud y vigencia de la categoría — cuántos documentos hay y qué tan reciente es la información, sin tener que abrir cada uno para verificarlo. Es información operativa útil para el propio equipo, no solo para un lector externo. |
| 8 | **Footer** | Footer completo (no condensado), consistente con DS-001 §9.3: esta es una página índice, no una página de contenido largo — el costo de scroll adicional no aplica aquí. |

---

## 11. Validación de cumplimiento

| Requisito | Verificación |
|---|---|
| **STD-001** (Manual de Organización) | Los tres wireframes respetan la estructura documental ya establecida (HB-001 como ejemplo de Página de Documento) y las convenciones de badges de estado, coherentes con la cadencia de revisión y gobernanza definidas en STD-001. ✅ |
| **ARC-001** (Arquitectura UX v0.1) | Sitemap de 8 categorías raíz reflejado sin alteraciones en Home (§8) y en la categoría Ingeniería (§10); los flujos de navegación de WF-001 Parte 1 (llegada, retorno, cambio de categoría, navegación entre documentos) están representados en los tres wireframes. ✅, con una nota: el estado colapsado del Sidebar en Home (§7.2) es una especificación nueva que **debe incorporarse formalmente** a ARC-001 §14 y no debe considerarse ratificada solo por aparecer aquí. |
| **DS-001** (Design System v1.0) | Los 19 componentes oficiales (Header, Sidebar, Breadcrumbs, Cards, Badges, Callouts, Bloques de código, TOC, Filtros/Tags como extensión de Badge, Footer) se usan sin inventar variantes nuevas fuera de catálogo. ✅, con una nota: el Footer condensado de la Página de Documento (§7.3) es una variante no descrita en DS-001 §9.3 y **queda pendiente de aprobación** por el Design System Architect antes de pasar a prototipo visual. |

**Conclusión**: los tres wireframes son consistentes con STD-001, ARC-001 y DS-001, con dos excepciones puntuales y ya señaladas (§7.2 y §7.3) que se recomienda resolver formalmente —vía el proceso de gobernanza de DS-001 §16— antes de iniciar la Parte 3 (prototipo visual).

---

*Fin de la Parte 2 de WF-001. No se ha generado prototipo visual, HTML, React, Tailwind ni CSS en este documento — únicamente diagramas ASCII de baja fidelidad y su especificación funcional.*

---

# Anexo de Revisión Técnica — Comité de Arquitectura y UX

*Las secciones siguientes (12–19) enriquecen WF-001 hasta su versión oficial 1.0. No modifican, reescriben ni reestructuran ninguna sección anterior (1–11). Continúan la numeración donde cerró la Parte 2.*

---

## 12. Decision Log (Registro de Decisiones UX)

Decisiones extraídas de lo ya definido en las Partes 1 y 2 de WF-001 — ninguna es nueva, todas estaban implícitas en el documento y aquí quedan formalizadas para trazabilidad futura.

---

**UX-001**
**Título:** Cinco planos de navegación independientes
**Descripción:** La navegación se divide en cinco planos que no se superponen (Global, Local, Contextual, Secuencial, Utilitario), cada uno resolviendo una única pregunta de orientación.
**Justificación:** Evita que un solo componente (ej. un Sidebar sobrecargado) intente resolver más de un tipo de pregunta a la vez, lo que degradaría su claridad a medida que el Handbook crece.
**Impacto:** Alto — es la decisión estructural de la que dependen el resto de las decisiones de navegación.
**Prioridad:** Alta
**Documentos relacionados:** WF-001 Parte 1 §5, DS-001 §9.2/§9.13

---

**UX-002**
**Título:** Sin botón "Volver" genérico
**Descripción:** Se descarta un botón único de retorno; en su lugar, tres mecanismos específicos (Breadcrumbs, Sidebar, botón atrás del navegador) cubren cada necesidad de retorno por separado.
**Justificación:** Un botón "Volver" genérico es ambiguo entre retorno jerárquico, retorno secuencial e historial de navegación — resolverlo con tres mecanismos inequívocos elimina esa ambigüedad de raíz.
**Impacto:** Medio — afecta la confianza del usuario al navegar, no la estructura del sitemap.
**Prioridad:** Media
**Documentos relacionados:** WF-001 Parte 1 §6.3

---

**UX-003**
**Título:** Home sin árbol de Sidebar expandido
**Descripción:** Home usa tarjetas de categoría como navegación primaria en lugar del árbol completo de contenido.
**Justificación:** Un usuario nuevo enfrentado al árbol completo de 8 categorías × N subcategorías desde el primer segundo sufre sobrecarga cognitiva; las tarjetas con descripción priorizan comprensión sobre densidad de información.
**Impacto:** Alto — define la primera impresión del Handbook para todo integrante nuevo.
**Prioridad:** Alta
**Documentos relacionados:** WF-001 Parte 1 §3.2, §6.1; ARC-001

---

**UX-004**
**Título:** Inventario cerrado de plantillas de página
**Descripción:** Toda página del Handbook pertenece a exactamente una de un conjunto fijo de plantillas (Home, Category Index, Document Page, ADR Index/Detail, 404, Changelog global); no se permiten páginas híbridas.
**Justificación:** Es la condición que permite que el Handbook escale sin que cada categoría nueva invente su propia estructura de navegación o layout.
**Impacto:** Alto — condiciona directamente el trabajo de PV-001 (Prototipo Visual).
**Prioridad:** Alta
**Documentos relacionados:** WF-001 Parte 1 §3.2, §15

---

**UX-005**
**Título:** Entrada no lineal como caso por defecto
**Descripción:** Toda Document Page se diseña asumiendo que el usuario puede llegar "en frío" (link compartido, búsqueda), sin haber pasado por Home ni por la Category Index.
**Justificación:** La mayoría de las visitas reales a un handbook interno no comienzan en Home; diseñar para el caso contrario dejaría desorientada a la mayoría de las visitas.
**Impacto:** Alto — obliga a que Breadcrumbs, información del documento y Sidebar estén siempre poblados, sin excepción.
**Prioridad:** Alta
**Documentos relacionados:** WF-001 Parte 1 §4, §6.2

---

**UX-006**
**Título:** Navegación secuencial condicionada a orden editorial
**Descripción:** El componente Anterior/Siguiente solo aparece en categorías con un orden pedagógico explícito (`order` en frontmatter); no es universal a todas las categorías.
**Justificación:** Forzar un orden secuencial en categorías sin relación de lectura entre sus documentos (ej. Playbooks, independientes entre sí) generaría una falsa sensación de progreso lineal donde no existe.
**Impacto:** Medio — afecta el diseño de la plantilla de Document Page, no la arquitectura general.
**Prioridad:** Media
**Documentos relacionados:** WF-001 Parte 1 §5, §6.5; ARC-001 §14

---

**UX-007**
**Título:** Cambio de categoría en un solo click desde cualquier documento
**Descripción:** El Sidebar permite moverse a cualquier categoría raíz directamente, sin regresar a Home como paso intermedio obligatorio.
**Justificación:** Minimiza el costo de cambio entre temas distintos, coherente con el principio de "Costo de cambio mínimo entre categorías".
**Impacto:** Medio.
**Prioridad:** Media
**Documentos relacionados:** WF-001 Parte 1 §4, §6.4

---

**UX-008**
**Título:** Reinicio de planos Contextual y Secuencial al cambiar de categoría
**Descripción:** El TOC y el Anterior/Siguiente no mantienen continuidad entre categorías distintas — son propiedades del documento/categoría actual, no del recorrido del usuario.
**Justificación:** Ambos planos pierden sentido fuera de su categoría de origen; mantenerlos "vivos" entre categorías generaría estados inconsistentes difíciles de representar.
**Impacto:** Bajo — decisión de comportamiento, no de estructura visible.
**Prioridad:** Baja
**Documentos relacionados:** WF-001 Parte 1 §6.4

---

**UX-009**
**Título:** Sidebar en Home colapsado a iconos (no ausente)
**Descripción:** Home muestra el Sidebar en su estado de icono colapsado, no lo oculta por completo.
**Justificación:** Resuelve el requisito de tener el plano Global visible desde Home sin reintroducir el árbol completo, que contradiría UX-003.
**Impacto:** Medio — actualmente pendiente de ratificación formal en ARC-001 (ver Riesgo R-07, sección 14).
**Prioridad:** Media
**Documentos relacionados:** WF-001 Parte 2 §7.2; ARC-001; DS-001 §5, §10

---

**UX-010**
**Título:** Footer condensado en Document Page
**Descripción:** La Document Page usa una variante de una sola línea del Footer (editar en GitHub + versión) en lugar del Footer completo multi-columna.
**Justificación:** Preserva la señal de cierre de página sin el costo de scroll adicional que DS-001 buscaba evitar en contenido largo.
**Impacto:** Bajo — cambio de variante de componente, no de arquitectura.
**Prioridad:** Media (por estar pendiente de ratificación en DS-001)
**Documentos relacionados:** WF-001 Parte 2 §7.3; DS-001 §9.3, §16

---

**UX-011**
**Título:** Buscador local además del buscador global
**Descripción:** La Category Index incluye un campo de búsqueda que filtra solo dentro de los documentos de esa categoría, distinto del buscador global del Header.
**Justificación:** Cuando el usuario ya sabe en qué categoría está, una búsqueda acotada es más rápida y más precisa que una búsqueda global sobre todo el Handbook.
**Impacto:** Medio.
**Prioridad:** Media
**Documentos relacionados:** WF-001 Parte 2 §10

---

**UX-012**
**Título:** Soporte de bloques de código desde el primer manual
**Descripción:** La plantilla de Document Page incluye la especificación de bloques de código aunque HB-001 (su primer caso de uso) no los utilice.
**Justificación:** Los manuales técnicos futuros (Backend, PostgreSQL, Docker, Git) reutilizarán esta misma plantilla; definir el soporte ahora evita rediseñar la plantilla más adelante.
**Impacto:** Medio — impacta directamente el trabajo de contenido técnico futuro.
**Prioridad:** Media
**Documentos relacionados:** WF-001 Parte 2 §9; DS-001 §9.14

---

**UX-013**
**Título:** Estadísticas básicas visibles como señal operativa
**Descripción:** La Category Index muestra conteos simples (documentos totales, en Draft, última actualización) visibles para cualquier lector, no solo para el equipo interno.
**Justificación:** Da una señal rápida de salud y vigencia de la categoría sin que el usuario tenga que abrir cada documento para inferirlo.
**Impacto:** Bajo.
**Prioridad:** Baja
**Documentos relacionados:** WF-001 Parte 2 §10

---

## 13. Métricas UX

Cada métrica se define junto con el flujo o principio de WF-001 que busca validar. Los umbrales numéricos concretos (qué cuenta como "aceptable") no se fijan en este documento: deben establecerse mediante una línea base de pruebas de usabilidad con integrantes reales del equipo THERS, no como una cifra asumida a priori.

| Métrica | Qué mide | Por qué importa (vínculo UX) |
|---|---|---|
| **Tiempo hasta el primer documento relevante** | Desde el punto de entrada (Home, búsqueda o link directo) hasta que el usuario abre un documento que responde su necesidad. | Valida directamente las cuatro rutas de llegada definidas en WF-001 Parte 1 §6.2 — si una ruta es sistemáticamente más lenta que las otras, señala un problema de diseño en esa ruta específica. |
| **Profundidad de clics desde Home** | Cantidad de clics necesarios para llegar a cualquier documento del Handbook partiendo de Home. | Valida que el inventario cerrado de plantillas (UX-004) y el diseño del Sidebar/Breadcrumbs mantengan la navegación superficial incluso cuando el sitemap crezca. |
| **Tiempo de reorientación en entrada "en frío"** | Tiempo que le toma a un usuario que llegó por link directo entender en qué categoría/documento está, sin haber navegado antes. | Valida el principio de Entrada no lineal (UX-005) — si este tiempo es alto, significa que Breadcrumbs + Información del documento no están cumpliendo su función. |
| **Clics para regresar a un punto de referencia** | Cantidad de clics para volver a Home o a la Category Index desde cualquier profundidad. | Valida los tres mecanismos de retorno definidos en WF-001 Parte 1 §6.3. |
| **Costo de cambio entre categorías** | Cantidad de clics para pasar de un documento de una categoría a cualquier documento de otra categoría distinta. | Valida directamente la decisión UX-007 ("un solo click") — es una métrica de aceptación, no solo de referencia. |
| **Tasa de éxito de búsqueda en un primer intento** | Proporción de búsquedas donde el usuario abre un resultado sin reformular la consulta. | Señala si el ranking y agrupamiento del Buscador (DS-001 §9.12) siguen siendo efectivos a medida que el volumen de contenido indexado crece (ligado al Riesgo R-05). |
| **Facilidad de aprendizaje para un integrante nuevo** | Capacidad de un integrante que se incorpora al equipo de ubicar, sin ayuda externa, el Manual de Organización y su documento de Onboarding correspondiente. | Valida el flujo de usuario nuevo completo (WF-001 Parte 1 §6.1), de punta a punta, no un componente aislado. |
| **Profundidad máxima de niveles de navegación** | Cuántos niveles jerárquicos (categoría → subcategoría → documento → sección) debe atravesar un usuario en el peor caso. | Es un límite de diseño, no solo una medición posterior: mantiene la Divulgación progresiva (WF-001 Parte 1 §4) como una propiedad verificable, no solo aspiracional. |

---

## 14. Riesgos de Diseño

| ID | Riesgo | Descripción | Impacto | Probabilidad | Plan de mitigación | Prioridad |
|---|---|---|---|---|---|---|
| R-01 | Sidebar sobrecargada | A medida que crecen las subcategorías y documentos, el árbol de navegación se vuelve difícil de escanear visualmente. | Alto | Media | Colapso por defecto ya definido (DS-001 §10); establecer un límite recomendado de profundidad visible, análogo al límite ya aplicado al TOC (DS-001 §13). | Alta |
| R-02 | Exceso de categorías raíz | Que se agreguen categorías de primer nivel sin suficiente justificación, saturando la navegación Global. | Alto | Baja | Ya mitigado parcialmente: toda categoría raíz nueva requiere decisión de alto impacto (STD-001 §11, referenciado en ARC-001 §14). Riesgo residual si el proceso no se respeta en la práctica. | Media |
| R-03 | Contenido duplicado entre categorías | Un mismo tema (ej. autenticación) se documenta parcialmente en más de una categoría en lugar de enlazarse desde una única fuente. | Medio | Media | Convención ya establecida de "una sola fuente de verdad, enlazar no duplicar" (ARC-001 §15); las Etiquetas de la Category Index (WF-001 Parte 2 §10) ayudan a descubrir contenido relacionado sin necesidad de duplicarlo. | Media |
| R-04 | Documentación desactualizada con apariencia de vigente | Los badges de estado (Estable/Draft/Deprecado) dependen de que alguien los actualice manualmente; un documento puede lucir "Estable" y estar desactualizado. | Alto | Media | Cadencia de revisión mensual ya establecida (STD-001 §6); el CI de frontmatter (ARC-001 §17) valida estructura, no veracidad — este riesgo residual queda reconocido explícitamente, no resuelto. | Alta |
| R-05 | Búsqueda poco efectiva a gran escala | El motor de búsqueda 100% client-side puede degradar en velocidad o relevancia cuando el volumen de páginas crezca significativamente. | Medio | Media | Ruta de escalamiento ya prevista hacia un motor autohospedado (tipo Typesense/Meilisearch) sin cambiar la experiencia de usuario (ARC-001 §11). | Media |
| R-06 | Falta de paginación/agrupamiento en categorías grandes | El grid de Tarjetas de documentos (WF-001 Parte 2 §10) no define comportamiento cuando una categoría supera varias decenas de documentos. | Medio | Media | No resuelto en esta versión — se traslada explícitamente a Preguntas Abiertas (sección 15). | Media |
| R-07 | Deriva de las excepciones pendientes de ratificación | Las dos desviaciones señaladas en WF-001 Parte 2 §7.2 y §7.3 podrían asumirse como regla permanente si nunca se ratifican formalmente en ARC-001 y DS-001. | Medio | Alta si no se atiende pronto | El Checklist de Aprobación (sección 18) bloquea explícitamente la aprobación final de WF-001 hasta que ambas excepciones se resuelvan. | Alta |

---

## 15. Preguntas Abiertas

Temas que no se resuelven en esta versión de WF-001, pendientes de análisis en versiones futuras del Handbook:

- ¿Se implementará un sistema de favoritos/pins personales en el Sidebar, ya anticipado como posible fase 2 en ARC-001?
- ¿Habrá un historial de páginas visitadas recientemente dentro del propio Handbook, más allá del historial nativo del navegador?
- ¿Se ofrecerá exportación de páginas o manuales completos a PDF para lectura offline?
- ¿Se integrará algún asistente de IA dentro del Handbook para responder preguntas sobre su propio contenido?
- ¿Existirá un mecanismo de comentarios o discusión por página, más allá del widget binario "¿Te sirvió esta página?" ya definido en DS-001?
- ¿Cómo se manejará la paginación o agrupamiento cuando una categoría supere el volumen razonable de tarjetas visibles (ligado al Riesgo R-06)?
- ¿Se necesitará un selector de versión histórica del contenido del Handbook, independiente del versionado del propio Design System?
- ¿La búsqueda deberá indexar también código fuente del repositorio del producto THERS, o se mantiene estrictamente separada de él?
- ¿Se traducirá el Handbook a otro idioma en algún momento, y qué implicaría eso para el sitemap y las rutas ya definidas en ARC-001?
- ¿Quién, más allá del equipo actual de 4 integrantes, tendrá acceso al Handbook (futuros contratados, stakeholders externos) y eso debería cambiar el nivel de detalle o el tono del contenido?

---

## 16. Matriz de Trazabilidad

| Documento origen | Relación | Documento destino | Estado |
|---|---|---|---|
| STD-001 | Define el proceso de gobernanza y aprobación que rige la elaboración de WF-001 | WF-001 | Aplicado |
| ARC-001 | Define la arquitectura del portal, el sitemap y los flujos de navegación base que WF-001 traduce en plantillas y wireframes | WF-001 | Aplicado |
| DS-001 | Define los tokens, componentes y principios visuales que WF-001 utiliza (sin inventar variantes fuera de catálogo, salvo las señaladas) | WF-001 | Aplicado, con 2 excepciones pendientes de ratificación (§7.2, §7.3) |
| WF-001 | Detecta necesidad de actualización en el estado de Sidebar para la plantilla Home | ARC-001 (§14) | Pendiente de actualización |
| WF-001 | Detecta necesidad de una nueva variante de componente (Footer condensado) | DS-001 (§9.3) | Pendiente de aprobación por el Design System Architect |
| WF-001 | Especifica las plantillas, planos de navegación y flujos que servirán de base directa | PV-001 — Prototipo Visual | Dependiente de WF-001 (no iniciado) |
| WF-001 | Define la estructura de plantilla que debe aplicarse al maquetar el contenido ya existente | HB-001 — Manual de Organización | Parcialmente aplicado (el contenido existe; la maquetación bajo esta plantilla está pendiente) |
| WF-001 | Define la plantilla de Document Page que usarán los manuales técnicos aún no escritos | Futuros manuales (Backend, PostgreSQL, Docker, Git, Manual Operativo, Plan Estratégico IA) | Pendiente — dependerán de WF-001 en cuanto se redacten |

---

## 17. Validación Final

| Criterio | Evaluación |
|---|---|
| **Cumple STD-001** | Sí. WF-001 respeta el proceso de decisión por impacto (bajo/medio/alto) y el estándar de documentación ya establecido; las excepciones detectadas se canalizan por el mismo proceso de gobernanza, no por decisión unilateral. |
| **Cumple ARC-001** | Sí, con nota. El sitemap, los planos de navegación y los flujos de usuario son coherentes con la arquitectura ya aprobada. Nota: el estado colapsado del Sidebar en Home (§7.2) requiere actualización formal de ARC-001 §14 para cerrar el ciclo. |
| **Cumple DS-001** | Sí, con nota. Los 19 componentes oficiales se usan sin variantes no catalogadas, salvo el Footer condensado (§7.3), que requiere aprobación explícita del Design System Architect antes de considerarse parte del catálogo. |
| **Buenas prácticas UX** | Sí. El documento aplica principios reconocidos de arquitectura de información (planos de navegación separados, entrada no lineal, divulgación progresiva) de forma consistente en las tres plantillas desarrolladas. |
| **Escalabilidad** | Parcial. El inventario cerrado de plantillas y el sistema de tokens escalan bien en teoría, pero persisten riesgos no resueltos de escalabilidad concreta (R-01 Sidebar, R-06 grid de categorías) que deben tratarse antes de que el volumen de contenido crezca significativamente. |
| **Mantenibilidad** | Sí. El Decision Log (sección 12) y la Matriz de Trazabilidad (sección 16) dejan explícito el porqué de cada decisión, reduciendo la dependencia de memoria institucional para mantener el documento en el futuro. |
| **Consistencia** | Sí, con nota. Las tres plantillas comparten el mismo lenguaje de componentes y planos de navegación; las dos excepciones puntuales están señaladas, no ocultas, lo que preserva la consistencia documental del conjunto STD-001/ARC-001/DS-001/WF-001. |

---

## 18. Checklist Oficial de Aprobación

- [ ] Las seis secciones de la Parte 1 (Introducción a Flujo general del usuario) están completas, sin secciones marcadas como pendientes.
- [ ] Las tres plantillas de la Parte 2 (Home, Documento, Categoría) cubren el subconjunto prioritario del inventario de plantillas definido en §3.2.
- [ ] Toda decisión de diseño relevante identificada en el documento está registrada en el Decision Log (sección 12) con su justificación e impacto.
- [ ] Cada métrica UX (sección 13) está vinculada explícitamente a un flujo o principio ya documentado, no a un criterio nuevo introducido sin trazabilidad.
- [ ] Todo riesgo identificado (sección 14) tiene un plan de mitigación asignado o está correctamente derivado a Preguntas Abiertas (sección 15).
- [ ] Las excepciones señaladas en §7.2 (Sidebar en Home) y §7.3 (Footer condensado) están explícitamente marcadas como pendientes de ratificación, no como reglas definitivas del sistema.
- [ ] La Matriz de Trazabilidad (sección 16) no contiene dependencias huérfanas: todo documento de origen o destino mencionado existe o está formalmente planificado.
- [ ] El documento no contiene HTML, CSS, React ni Tailwind en ningún punto.
- [ ] El documento fue revisado por al menos un integrante distinto de quien lo redactó, siguiendo el mismo estándar de revisión aplicado al código (STD-001, sección de revisión de código).

**Estado de aprobación de WF-001 v1.0:** condicionado — la aprobación definitiva queda sujeta a que se resuelvan los dos puntos de ratificación pendientes (§7.2 y §7.3) antes de iniciar PV-001.

---

## 19. Recomendaciones para la siguiente fase (PV-001 — Prototipo Visual)

**Qué se reutiliza directamente:** las tres plantillas desarrolladas en la Parte 2 (Home, Document Page, Category Page) se convierten en la base estructural del prototipo visual; cada zona numerada de los wireframes ASCII pasa a ser una sección del prototipo, y los tokens de color, tipografía, espaciado e iconografía de DS-001 se aplican directamente sobre esa estructura ya validada — no hay necesidad de volver a diseñar la disposición desde cero.

**Qué ya no debe modificarse en PV-001:** el inventario cerrado de plantillas (§3.2), los cinco planos de navegación (§5) y las cinco rutas del flujo general del usuario (§6) son decisiones de interacción, no de estilo visual — ya fueron validadas en esta fase y cambiarlas en PV-001 invalidaría el trabajo de esta revisión. Lo mismo aplica al Decision Log completo (sección 12): ninguna decisión ahí registrada debe revertirse sin pasar de nuevo por el proceso de gobernanza de DS-001 §16.

**Qué todavía puede evolucionar:** la resolución visual definitiva de las dos excepciones pendientes (§7.2 y §7.3) debe cerrarse en PV-001 junto con el Design System Architect; el tratamiento del grid de Tarjetas de documentos cuando una categoría escala (Riesgo R-06) sigue sin una solución de diseño concreta; y, dado que PV-001 introducirá color por primera vez, el peso visual final de badges, etiquetas y estados semánticos (hoy solo descritos textualmente) es un terreno abierto de refinamiento dentro de los límites ya fijados por DS-001.

---

*Fin de WF-001 v1.0 — versión oficial. Documento compuesto por Parte 1 (secciones 1–6), Parte 2 (secciones 7–11) y este Anexo de Revisión Técnica (secciones 12–19), sin modificaciones al contenido previamente aprobado.*
