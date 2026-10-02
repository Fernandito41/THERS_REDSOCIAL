/**
 * Tokens de diseño de THERS, portados para React Native.
 *
 * Origen: `Frontend/src/shared/design/tokens.css` (211 custom properties),
 * documentado en `docs/THERS_DESIGN_SYSTEM.md`. React Native no entiende
 * `var(--th-*)` ni CSS, así que los valores viven aquí como constantes --
 * ADR-016 §2.2 registra esta portabilidad como una de las razones de elegir
 * React Native.
 *
 * REGLAS (ADR-016, CLAUDE.md §5 "Frontend del producto"):
 * - Este archivo es un PORTE, no un Design System nuevo. No se inventan
 *   valores: cada uno existe en `tokens.css`. Si falta uno, se copia de ahí,
 *   no se improvisa.
 * - `Frontend/` sigue siendo la fuente. Si un token cambia allá, se refleja
 *   acá a mano -- son dos aplicaciones independientes, sin código compartido
 *   (CLAUDE.md §2), así que esta duplicación es deliberada y acotada.
 * - No se agrega NativeWind ni otra biblioteca visual: el encargo
 *   (THERS_PROMPT_CLAUDE_ANDROID.md §5) lo prohíbe explícitamente.
 * - El Frontend del producto NO tiene un Design System ratificado por el
 *   Comité Técnico (`DS-001` §1.2 es exclusivo del Handbook). Estos tokens
 *   están autorizados por el propietario del proyecto, no por `HB-001`
 *   §11-12. No extrapolarlos ni ampliarlos sin que el equipo lo ratifique.
 *
 * Solo se portó el subconjunto que las pantallas de esta primera entrega
 * (login, perfil) usan de verdad. Portar los 211 de una vez sería adelantar
 * trabajo sin consumidor.
 */

/** Primitivos -- `tokens.css` §paleta. */
const primitives = {
  violet50: '#faf5ff',
  violet100: '#f3e8ff',
  violet500: '#7c3aed',
  violet600: '#6d28d9',
  violet700: '#7e22ce',
  slate50: '#f8fafc',
  slate100: '#f1f5f9',
  slate200: '#e2e8f0',
  slate300: '#cbd5e1',
  slate400: '#94a3b8',
  slate500: '#64748b',
  slate600: '#475569',
  slate900: '#0f172a',
  white: '#ffffff',
} as const;

/** Semánticos -- el nivel que las pantallas deben consumir. */
export const colors = {
  bg: primitives.slate50,
  bgSubtle: primitives.slate100,
  surface: primitives.white,
  surfaceRaised: primitives.slate100,

  border: primitives.slate200,
  borderSubtle: primitives.slate100,
  borderStrong: primitives.slate300,

  brand: primitives.violet500,
  brandHover: primitives.violet700,
  brandSoft: primitives.violet50,
  brandSoftStrong: primitives.violet100,
  onBrand: primitives.white,

  fg: primitives.slate900,
  fgSecondary: primitives.slate600,
  fgMuted: primitives.slate500,
  fgDisabled: primitives.slate400,

  dangerAccent: '#dc2626',
  dangerFg: '#991b1b',
  dangerSurface: '#fef2f2',
  dangerBorder: '#fca5a5',

  successAccent: '#10b981',
  successFg: '#047857',
  successSurface: '#ecfdf5',
} as const;

/** Escala tipográfica -- `--th-text-*`. */
export const fontSize = {
  headlineXl: 40,
  headlineLg: 32,
  headlineMd: 24,
  headlineSm: 20,
  bodyLg: 17,
  bodyMd: 15,
  bodySm: 13,
  labelLg: 14,
  labelMd: 12,
  labelSm: 11,
} as const;

/** Espaciado -- `--th-space-*`. */
export const space = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  6: 24,
  8: 32,
  10: 40,
} as const;

/** Radios -- `--th-radius-*`. */
export const radius = {
  xs: 4,
  sm: 8,
  input: 12,
  card: 16,
  dialog: 24,
  pill: 9999,
} as const;
