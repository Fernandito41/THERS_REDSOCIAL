# FAS-001 — Frontend Architecture Specification

*THERS Engineering Handbook — Documento Oficial*

---

## Nota previa

Antes de desarrollar el documento, dejo explícita una limitación operativa: no tengo acceso al contenido literal de HB-001, STD-001, ARC-001, DS-001, WF-001 ni PV-001 —solo a sus nombres y su rol declarado en este proyecto—. Por lo tanto, las referencias que hago a esos documentos son **conceptuales y de rol**, no citas de su contenido. Si alguna decisión de FAS-001 entra en conflicto con algo específico ya definido en esos documentos, esa decisión de FAS-001 debe ceder ante el documento previo, y se debe señalar para corrección. No he asumido stack, herramientas o requisitos fuera de los que este mismo documento y las instrucciones de proyecto declaran explícitamente (React, Vite, Tailwind, Flask, PostgreSQL, Docker, contenido en Markdown).

Con esa salvedad, procedo con el documento.

---

## 1. Introducción

**Objetivo del documento**

FAS-001 traduce la documentación funcional, visual y experiencial ya aprobada del THERS Engineering Handbook en una guía técnica de arquitectura Frontend. Su propósito no es diseñar ni redecidir nada: es establecer *cómo* debe pensarse y organizarse el Frontend para que lo ya aprobado pueda implementarse sin decisiones arquitectónicas improvisadas durante el desarrollo.

**Alcance**

FAS-001 cubre exclusivamente la dimensión técnica-conceptual del Frontend: principios, capas, estrategias de componentización, layouts, páginas, contenido, navegación, assets, estilos, rendimiento y escalabilidad. Quedan fuera de su alcance:

- La estructura definitiva de carpetas (se define en un documento posterior, p. ej. FAS-002 o un ADR de estructura de proyecto).
- Cualquier decisión de backend, base de datos o infraestructura, salvo en los puntos donde el Frontend depende de ellas (p. ej. consumo de servicios).
- Cualquier redefinición de diseño visual, UX o contenido ya aprobados en DS-001, WF-001 o PV-001.

**Relación con los documentos previos**

- **HB-001 (Manual de Organización):** aporta el marco organizacional y de gobierno del proyecto; FAS-001 se apega a los principios de trabajo allí definidos.
- **STD-001 (Handbook Design Proposal):** define la propuesta funcional del producto; FAS-001 no la reinterpreta, la operacionaliza técnicamente.
- **ARC-001 (Handbook Architecture):** define la arquitectura funcional/de producto del Handbook; FAS-001 es su contraparte técnica específica de Frontend.
- **DS-001 (Design System):** es la fuente de verdad visual; toda estrategia de estilos y componentización en FAS-001 está subordinada a DS-001.
- **WF-001 (Wireframes) y PV-001 (Prototipo Visual):** definen estructura de pantallas y experiencia validada; FAS-001 asume que las páginas y layouts descritos allí son el input a implementar, no a rediseñar.

**Rol de FAS-001 en el proyecto**

FAS-001 es el documento bisagra entre "qué se aprobó" y "cómo se construye". A partir de su aprobación, cualquier decisión técnica de Frontend debe justificarse contra este documento antes que contra el criterio individual de quien implementa. Esto es coherente con el enfoque Docs-as-Code del proyecto: el código sigue a la documentación, no al revés.

---

## 2. Principios Arquitectónicos

Cada principio se explica junto con el problema que resuelve, para evitar que queden como enunciados decorativos.

**Separación de responsabilidades**
Cada unidad de código (componente, servicio, utilidad) debe tener una única razón para cambiar. Resuelve el problema de que un cambio visual termine afectando lógica de datos, o que un cambio de contenido obligue a tocar componentes. Es la base que permite que distintas personas trabajen en paralelo sin pisarse.

**Escalabilidad**
El Frontend debe poder crecer en volumen de contenido (nuevos documentos, categorías, secciones tipo Academy o Playbooks) y en volumen de código (nuevos componentes, nuevas páginas) sin que el costo de agregar algo nuevo aumente con el tamaño del proyecto. Resuelve el problema típico de proyectos documentales que colapsan su propia estructura al crecer.

**Componentización**
Toda pieza de interfaz que se repite conceptualmente (no solo visualmente) debe existir en un único lugar. Resuelve la duplicación de lógica y de estilo, y es el mecanismo principal para mantener consistencia con DS-001 sin esfuerzo manual constante.

**Reutilización**
Distinta de la componentización: no se trata solo de extraer piezas repetidas, sino de diseñarlas desde el inicio pensando en más de un caso de uso razonable. Resuelve el costo de reinventar soluciones ya resueltas y reduce la superficie total de código a mantener.

**Bajo acoplamiento**
Ninguna capa o componente debe depender de detalles internos de otra. Resuelve el problema de que un cambio local (p. ej. cómo se obtiene el contenido) obligue a modificar código no relacionado (p. ej. cómo se presenta). Facilita reemplazar partes del sistema sin efecto dominó.

**Alta cohesión**
Lo que cambia junto, debe vivir junto conceptualmente. Resuelve el problema inverso al acoplamiento: evitar que una sola funcionalidad quede dispersa en múltiples lugares no relacionados, lo cual dificulta entender y modificar el sistema.

**Mantenibilidad**
Es la consecuencia directa de aplicar bien los principios anteriores: el costo de introducir un cambio o corregir un defecto debe mantenerse bajo con el tiempo, no crecer exponencialmente. Es el principio que justifica invertir en arquitectura desde el día uno en un proyecto de vida larga como un handbook corporativo.

**Legibilidad**
El código y su organización deben poder entenderse sin depender de quien lo escribió. Resuelve el problema de dependencia de conocimiento tácito, crítico en un proyecto documental que, por definición, va a tener rotación de colaboradores.

**Simplicidad**
Ante dos soluciones que resuelven el mismo problema, se prioriza la más simple de entender y mantener, no la más sofisticada. Resuelve el riesgo de sobre-ingeniería, muy común cuando se arranca un proyecto "queriendo hacerlo bien": la complejidad prematura es tan costosa como la falta de arquitectura.

**Consistencia**
Patrones similares deben resolverse siempre de la misma manera en todo el proyecto. Resuelve el costo cognitivo de tener que redescubrir cómo se hacen las cosas cada vez que se toca una parte distinta del código, y es prerrequisito para que la componentización funcione realmente.

---

## 3. Filosofía de Organización del Proyecto

El Frontend del Handbook debe organizarse bajo la premisa de que **el contenido crecerá más rápido que el código**. Esto invierte la prioridad habitual de muchos proyectos frontend: aquí la arquitectura no está al servicio de features, sino al servicio de la capacidad de absorber contenido nuevo sin fricción técnica.

De esto se derivan tres ideas rectoras:

**1. Organización por función, no por tipo de archivo.**
Antes de pensar en carpetas concretas, el criterio de organización debe ser "qué responsabilidad cumple esto dentro del sistema", no "qué tipo de archivo es". Agrupar por tipo (todos los componentes juntos, todos los estilos juntos) tiende a esconder la relación entre piezas que en realidad cambian juntas.

**2. Crecimiento por adición, no por reestructuración.**
El diseño debe anticipar que en el futuro se agregarán nuevas categorías de contenido (por ejemplo, una futura sección "Academy" o "Playbooks", mencionadas explícitamente como posibilidad de crecimiento). Agregar una categoría nueva debe ser un acto de *extensión* del sistema existente, no un evento que fuerce a reorganizar lo ya construido. Esto es lo que en la práctica separa un proyecto que envejece bien de uno que requiere reescrituras periódicas.

**3. La documentación y el código evolucionan en paralelo.**
Siguiendo el enfoque Docs-as-Code del proyecto, ninguna decisión estructural relevante del Frontend debería vivir solo en el código: debe quedar reflejada en documentación técnica (como este mismo documento y los que lo sucedan), de forma que la trazabilidad de decisiones no dependa de la memoria de quien las tomó.

Esta filosofía es deliberadamente conceptual en este documento: la traducción a una estructura de carpetas concreta se reserva a un documento posterior, precisamente para no comprometer una estructura física antes de tener claros estos principios rectores.

---

## 4. Capas del Frontend

Se definen ocho capas conceptuales. No son necesariamente ocho carpetas; son ocho *responsabilidades* que deben poder distinguirse claramente en cualquier punto del código.

**Presentación**
- Responsabilidad: cómo se ve y se comporta visualmente la interfaz; aplicación de los tokens y reglas de DS-001.
- No debe contener: lógica de negocio, acceso a datos, decisiones de contenido.
- Interacción: es consumida por Componentes, Layouts y Páginas; no depende de ninguna otra capa.

**Layouts**
- Responsabilidad: estructura común entre múltiples páginas (encabezados, navegación persistente, contenedores generales).
- No debe contener: contenido específico de una página ni lógica de negocio particular.
- Interacción: envuelve Páginas; consume Componentes y Presentación.

**Páginas**
- Responsabilidad: representar una vista concreta del Handbook, orquestando Layout, Componentes y Contenido para ese caso específico.
- No debe contener: lógica reutilizable ni definiciones visuales propias que debieran vivir en Componentes o Presentación.
- Interacción: se apoya en Layouts, Componentes, Contenido y Servicios; no es consumida por ninguna otra capa (es una hoja del árbol de dependencias).

**Componentes**
- Responsabilidad: piezas de interfaz reutilizables, con contrato de entrada claro, alineadas a DS-001.
- No debe contener: conocimiento de en qué página se usan ni acceso directo a datos externos salvo el estrictamente necesario para su propia función.
- Interacción: consumidos por Páginas y Layouts; se apoyan en Presentación y Utilidades.

**Contenido**
- Responsabilidad: el material documental del Handbook (en Markdown), tratado como dato, no como código de interfaz.
- No debe contener: marcado de presentación complejo ni lógica de aplicación.
- Interacción: es consumido por Páginas a través de Servicios, nunca directamente por Componentes de bajo nivel.

**Recursos (Assets)**
- Responsabilidad: material estático — imágenes, SVG, iconografía, tipografías.
- No debe contener: lógica alguna.
- Interacción: consumidos por Presentación y Componentes; idealmente nunca referenciados directamente desde Páginas.

**Servicios**
- Responsabilidad: acceso y obtención de datos y contenido (por ejemplo, la obtención de documentos Markdown, o la comunicación con el backend Flask cuando exista).
- No debe contener: lógica de presentación ni de layout.
- Interacción: consumidos por Páginas; nunca deben depender de Componentes ni de Presentación.

**Utilidades**
- Responsabilidad: funciones puras y genéricas de soporte (formateo, validaciones, helpers), sin conocimiento del dominio del Handbook.
- No debe contener: nada específico del negocio ni del contenido.
- Interacción: pueden ser consumidas por cualquier otra capa; no dependen de ninguna.

El principio rector de esta capa de capas es la **dirección única de dependencia**: Páginas dependen de Layouts, Componentes, Servicios y Contenido; nunca al revés. Esto es lo que en la práctica garantiza el bajo acoplamiento definido en la sección 2.

---

## 5. Estrategia de Componentización

**Qué debe convertirse en componente**
Cualquier elemento de interfaz que cumpla al menos uno de estos criterios:
- Aparece en más de un lugar del Handbook (repetición real, no coincidencia visual momentánea).
- Representa un elemento definido explícitamente en DS-001 (botón, tarjeta, badge, elemento de navegación, etc.).
- Tiene una responsabilidad visual/funcional identificable de forma independiente del contexto donde se usa.

**Qué NO debe convertirse en componente**
- Estructura que es específica de una sola página y no tiene vocación de reutilización real (evita la sobre-fragmentación, coherente con el principio de simplicidad).
- Combinaciones puntuales de componentes ya existentes que no constituyen un patrón nuevo, sino un simple ensamblaje momentáneo.

**Cómo evitar duplicaciones**
La regla operativa es: antes de crear una pieza visual nueva, debe verificarse si ya existe en el Design System o en el catálogo de componentes existente. La duplicación no es solo un problema de código repetido, sino un riesgo de inconsistencia visual respecto a DS-001, que es más grave en un producto documental donde la confianza visual del lector importa.

**Cómo mantener coherencia con el Design System**
Los componentes no definen su propio lenguaje visual: consumen los tokens y reglas ya definidas en DS-001 a través de la capa de Presentación. Un componente que necesita un valor visual no contemplado en DS-001 es una señal de que **DS-001 debe actualizarse primero**, no de que el componente debe improvisar un valor propio. Esto preserva a DS-001 como fuente única de verdad visual.

---

## 6. Estrategia de Layouts

**Qué es un Layout**
Es la estructura común y persistente que envuelve a un conjunto de páginas que comparten el mismo esqueleto de navegación y disposición general (por ejemplo, el esqueleto general del Handbook frente a, eventualmente, el esqueleto de una futura sección como Academy).

**Cuándo crear uno nuevo**
Solo cuando un conjunto de páginas requiere una estructura de navegación o disposición genuinamente distinta a los layouts existentes — no por diferencias estéticas menores, que deben resolverse a nivel de Presentación o Componentes.

**Qué responsabilidades tendrá**
Proveer el marco estructural (navegación persistente, contenedores generales) dentro del cual las páginas insertan su contenido específico.

**Qué responsabilidades no tendrá**
No decide el contenido de las páginas, no contiene lógica de negocio, y no debe conocer detalles internos de las páginas que envuelve. Un Layout debe poder envolver cualquier página compatible sin necesitar saber cuál es específicamente.

---

## 7. Estrategia de Páginas

**Qué representa una página**
Una página es la unidad final de composición: el punto donde se orquesta un Layout, uno o varios Componentes y, cuando corresponde, Contenido, para producir una vista concreta y navegable del Handbook.

**Cómo interactúa con Layouts**
Cada página se declara "dentro de" un Layout; la página no reimplementa estructura que ya provee el Layout.

**Cómo interactúa con Componentes**
La página ensambla componentes existentes; no define lógica visual propia que debería vivir en un componente reutilizable.

**Cómo mantener independencia entre páginas**
Ninguna página debe depender del estado interno o de la existencia de otra página. La comunicación entre vistas ocurre a través de navegación y datos, nunca por referencias directas entre páginas. Esto permite agregar, quitar o reordenar páginas sin efectos colaterales — condición necesaria para la escalabilidad de contenido descrita en la sección 3.

---

## 8. Estrategia de Contenido

**Gestión del contenido Markdown**
El contenido del Handbook se trata como **dato documental**, no como código de interfaz. Esto significa que el contenido en Markdown debe poder crearse, editarse y revisarse sin tocar componentes ni lógica de aplicación — condición indispensable para que la creación de contenido no dependa de quien sabe programar.

**Separación entre contenido y presentación**
El Markdown define significado (qué se dice), nunca apariencia (cómo se ve). La transformación de ese contenido en interfaz visual ocurre exclusivamente en la capa de Presentación/Componentes, nunca embebiendo estilos o estructura visual dentro del propio contenido. Esta separación es la que permite que un cambio en DS-001 se propague automáticamente a todo el contenido existente, sin reescribir un solo documento.

**Versionado**
Al tratarse de archivos de texto plano gestionados en el mismo repositorio (coherente con el enfoque Docs-as-Code), el contenido hereda naturalmente el historial, la trazabilidad y el control de cambios de Git, sin necesidad de un sistema de versionado adicional.

**Escalabilidad**
El modelo debe soportar que el volumen de documentos crezca en órdenes de magnitud (nuevas categorías como Academy, Playbooks, Roadmaps, mencionadas como crecimiento esperado) sin que eso implique cambios estructurales en el código; solo adición de contenido.

**Mantenimiento**
Al no requerir conocimiento de programación para modificar contenido, se reduce la dependencia del equipo de Frontend para tareas puramente documentales, lo cual es coherente con la filosofía de organización de la sección 3.

---

## 9. Estrategia de Navegación

**Organización de rutas**
La navegación debe reflejar la jerarquía de información ya validada en WF-001 y PV-001, no una jerarquía técnica arbitraria. La estructura de navegación es, en esencia, un espejo de la estructura de contenido.

**Jerarquía**
Debe existir una jerarquía clara y predecible entre categorías y documentos, de forma que agregar un documento nuevo a una categoría existente no requiera modificar la lógica de navegación, solo su fuente de datos.

**Escalabilidad**
La navegación debe soportar el crecimiento de categorías (Academy, Playbooks, Arquitectura, Roadmaps, etc.) como una operación de configuración/datos, no como una operación de código nuevo cada vez.

**Navegación (experiencia)**
Conceptualmente, la navegación debe permitir tanto exploración jerárquica (por categoría) como acceso directo (a un documento específico), en línea con lo ya validado en el prototipo visual, sin que esta especificación redefina esa experiencia — solo garantiza que la arquitectura la soporte.

*(No se definen rutas concretas, conforme a la restricción del documento.)*

---

## 10. Estrategia para Assets

**Imágenes y SVG**
Deben tratarse como recursos versionados junto al proyecto, optimizados para peso sin pérdida perceptible de calidad, y organizados de forma que su relación con el contenido o componente que los usa sea evidente.

**Iconografía**
Debe consumirse como un sistema único y coherente con DS-001, evitando que distintas partes del Handbook usen fuentes o estilos de íconos distintos entre sí.

**Logotipos**
Tratados como activos de marca con reglas de uso fijas (definidas en DS-001), no como assets libres de modificación por parte de quien implementa una página puntual.

**Tipografías**
Cargadas de forma centralizada y única para todo el proyecto, nunca redefinidas a nivel de página o componente individual, para preservar consistencia y rendimiento de carga.

**Recursos estáticos (buenas prácticas generales)**
- Todo asset debe tener una razón de existir ligada a un uso real, no "por si acaso".
- Los assets no deben duplicarse en distintos lugares del proyecto para distintos usos que podrían compartir el mismo recurso.
- El peso y formato de cada asset debe evaluarse contra su impacto real en la experiencia de carga (ver sección 12).

---

## 11. Estrategia para Estilos

**Relación con Tailwind CSS**
Tailwind se usa como mecanismo de aplicación de estilos, no como fuente de decisiones visuales. Las decisiones visuales (colores, espaciados, tipografía, radios, etc.) ya están tomadas en DS-001; Tailwind es la herramienta de implementación de esas decisiones, no un sustituto de ellas.

**Design Tokens**
Todo valor visual debe poder trazarse a un token definido en DS-001. Esto evita la proliferación de "valores mágicos" dispersos por el código, que es la causa más común de inconsistencia visual progresiva en proyectos que usan utility-first CSS sin disciplina.

**Modo oscuro**
Debe tratarse como una variación de los mismos tokens, no como una implementación paralela de estilos. Esto garantiza que cualquier componente nuevo herede soporte de modo oscuro automáticamente si respeta los tokens, sin trabajo adicional por componente.

**Escalabilidad**
La estrategia de estilos debe permitir agregar nuevos componentes o secciones sin necesidad de "reinventar" valores visuales, y sin que el crecimiento del proyecto incremente el riesgo de inconsistencia.

**Consistencia**
La disciplina de tokens es, en la práctica, la garantía de que la interfaz completa se perciba como un solo producto coherente y no como un conjunto de páginas construidas de forma independiente entre sí.

*(No se definen clases CSS concretas, conforme a la restricción del documento.)*

---

## 12. Estrategia de Rendimiento

**Lazy Loading**
Las páginas y secciones de contenido no críticas para la carga inicial deben cargarse bajo demanda. Esto es especialmente relevante en un Handbook cuyo volumen de contenido crecerá con el tiempo: si todo el contenido se cargara de forma anticipada, el rendimiento se degradaría proporcionalmente al crecimiento del proyecto, lo cual es inaceptable para un producto pensado para vivir años.

**Optimización**
La optimización debe aplicarse de forma proporcional: primero en los puntos de mayor impacto real en la experiencia (carga inicial, navegación entre documentos), no de forma uniforme y prematura sobre todo el sistema, en línea con el principio de simplicidad.

**Carga de documentos**
El contenido Markdown debe obtenerse y procesarse solo cuando el usuario navega hacia él, no de forma anticipada para todo el catálogo. Esto desacopla el rendimiento de la aplicación del volumen total de contenido existente.

**Escalabilidad**
Un modelo de carga bajo demanda es lo que permite que agregar cientos de documentos nuevos en el futuro no tenga impacto negativo en el rendimiento percibido del Handbook.

**Experiencia de usuario**
El rendimiento no es solo una métrica técnica: en un producto documental, la percepción de velocidad al navegar entre documentos es parte directa de la calidad percibida del contenido mismo.

---

## 13. Estrategia de Escalabilidad

El Handbook está concebido para crecer durante varios años, y esta arquitectura se diseña explícitamente para absorber ese crecimiento sin requerir reescrituras:

- **Nuevos documentos:** deben poder agregarse como contenido puro (sección 8), sin tocar código.
- **Nuevas categorías** (p. ej. Academy, Playbooks, Arquitectura, Roadmaps): deben poder incorporarse como extensiones de la jerarquía de navegación y contenido (sección 9), reutilizando Layouts y Componentes existentes siempre que su estructura lo permita, y creando nuevos Layouts solo cuando exista una diferencia estructural genuina (sección 6).
- **Nuevos componentes:** deben poder agregarse al catálogo existente siguiendo los criterios de la sección 5, sin que su incorporación obligue a modificar componentes ya existentes.

El criterio general de escalabilidad de este documento es: **el costo de agregar algo nuevo debe mantenerse aproximadamente constante, independientemente de cuánto haya crecido ya el proyecto.** Esa es la métrica de éxito real de esta arquitectura, más allá de cualquier tecnología específica.

---

## 14. Riesgos Arquitectónicos

| Riesgo | Cómo se previene |
|---|---|
| Mezcla progresiva de responsabilidades entre capas (p. ej. lógica de negocio filtrándose en Componentes) | Revisión de dependencias en cada incorporación de código, respetando la dirección única de dependencia definida en la sección 4 |
| Inconsistencia visual por uso de valores no definidos en DS-001 | Disciplina de tokens (sección 11) y tratamiento de DS-001 como fuente única de verdad visual |
| Degradación de rendimiento al crecer el volumen de contenido | Carga bajo demanda desde el diseño inicial (sección 12), no como optimización tardía |
| Sobre-componentización o sobre-ingeniería temprana | Aplicación estricta de los criterios de "qué NO debe convertirse en componente" (sección 5) y del principio de simplicidad (sección 2) |
| Acoplamiento entre páginas que dificulte reordenar o eliminar contenido | Independencia estricta entre páginas (sección 7) |
| Pérdida de trazabilidad entre decisiones documentadas y código real | Mantenimiento del enfoque Docs-as-Code también a nivel técnico, no solo funcional |
| Ambigüedad de alcance no cubierta por este documento (p. ej. internacionalización, autenticación, búsqueda full-text, si el Handbook es público o privado) | Estos puntos **no están definidos aún en la documentación disponible**; se recomienda resolverlos explícitamente antes de iniciar implementación, dado que pueden afectar capas transversales (Servicios, Navegación, Rendimiento) |

Este último punto es una observación, no una decisión: conforme a las restricciones de este documento, no se asume ningún requisito no definido, y se deja constancia expresa de que estos aspectos deben aclararse formalmente.

---

## 15. Checklist Arquitectónico

Antes de considerar una implementación conforme a FAS-001, debe verificarse:

- [ ] Ninguna capa depende de una capa que debería depender de ella (dirección única de dependencia respetada).
- [ ] Todo componente nuevo cumple al menos uno de los criterios de componentización de la sección 5.
- [ ] Ningún valor visual se define fuera de los tokens de DS-001.
- [ ] El contenido Markdown no contiene marcado de presentación embebido.
- [ ] Cada página puede eliminarse o reordenarse sin afectar a otra página.
- [ ] Los Layouts no contienen lógica ni contenido específico de una sola página.
- [ ] La navegación refleja la jerarquía de contenido, no una estructura técnica arbitraria.
- [ ] El contenido nuevo no requiere cambios de código para publicarse.
- [ ] La carga de contenido y páginas no críticas ocurre bajo demanda.
- [ ] Los assets están optimizados y no duplicados.
- [ ] El modo oscuro funciona automáticamente para todo componente que respete los tokens.
- [ ] Toda decisión arquitectónica tomada durante la implementación está justificada por FAS-001 o documentada como excepción explícita.

---

## 16. Conclusiones

Esta arquitectura no busca anticipar cada detalle técnico del Handbook, sino establecer las reglas de juego que permitan que miles de decisiones pequeñas —qué es un componente, dónde vive una responsabilidad, cómo se agrega un documento— se tomen de forma consistente sin necesidad de reabrir la discusión arquitectónica cada vez.

La combinación de capas con dirección única de dependencia, componentización disciplinada, separación estricta entre contenido y presentación, y una estrategia de rendimiento pensada para el crecimiento, es lo que permite afirmar que este Frontend podrá sostener años de crecimiento de contenido y funcionalidad sin degradar su mantenibilidad. La arquitectura está subordinada, en todo momento, a la documentación funcional y visual ya aprobada: FAS-001 no compite con ARC-001, STD-001 o DS-001, los sirve.

---

## 17. Estado del Documento

**Documento:** FAS-001
**Nombre:** Frontend Architecture Specification
**Versión:** 1.0
**Estado:** Aprobado para iniciar el desarrollo Frontend
**Tipo:** Documento Oficial

**Dependencias:**
- HB-001
- STD-001
- ARC-001
- DS-001
- WF-001
- PV-001

**Uso:** Referencia oficial para el desarrollo del Frontend del THERS Engineering Handbook.

---

Quedan, de mi parte, dos puntos que considero necesarios señalar antes de que este documento se dé por cerrado: la falta de definición sobre internacionalización/autenticación/búsqueda mencionada en la sección 14, y la confirmación de que la relación conceptual que describí con ARC-001/DS-001/WF-001/PV-001 coincide con su contenido real, ya que no tuve acceso a esos documentos. Si me compartes su contenido, puedo verificar y ajustar las referencias de la sección 1 y las secciones que dependen de ellos.
