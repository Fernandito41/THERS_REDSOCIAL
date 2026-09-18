/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Fondos/tarjetas del modo oscuro fijados al hex exacto de la primera
        // versión de THERS (Login/Register siguen usando estos mismos valores
        // hardcodeados: bg-[#0f0f11] / bg-[#18181b]) -- se recupera aquí como
        // token para que el resto de la app (feed, perfil, mensajes...) use
        // la misma identidad sin tener que reescribir cada componente.
        canvas: { DEFAULT: "#FAFAFC", dark: "#0f0f11" },
        surface: { DEFAULT: "#FFFFFF", dark: "#18181b" },
        ink: { DEFAULT: "#14141A", dark: "#FFFFFF" },
        muted: { DEFAULT: "#6B6B76", dark: "#9CA3AF" },
        line: { DEFAULT: "#ECECF2", dark: "#27272A" },
        // "pulse" = el morado original de THERS (idéntico a la escala `purple`
        // de Tailwind que ya usaban los botones/enlaces hardcodeados). Es el
        // único acento de marca -- no se reemplaza por otra paleta.
        pulse: {
          50: "#faf5ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7e22ce",
          800: "#6b21a8",
          900: "#581c87",
        },
        // "ember" ya no es un segundo acento de marca -- queda como color
        // semántico (error/destructivo) únicamente, para no competir con el
        // morado como identidad visual.
        ember: {
          50: "#fef2f2",
          100: "#fee2e2",
          300: "#fca5a5",
          400: "#f87171",
          500: "#ef4444",
          600: "#dc2626",
          700: "#b91c1c",
        },
        // "success"/"warning" -- mismos valores que ya se usaban sueltos
        // como text-green-*/text-yellow-* en Toast/PasswordStrength/Messages,
        // ahora centralizados como token (PRODUCT_DESIGN_SYSTEM.md §2.3).
        // warning usa la escala "amber" (no "yellow" de Tailwind): yellow-500
        // no alcanza contraste AA, amber sí.
        success: {
          50: "#f0fdf4",
          100: "#dcfce7",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
        },
        warning: {
          50: "#fffbeb",
          100: "#fef3c7",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
        },
        // "th" = tokens del NUEVO diseño (src/shared/design/tokens.css).
        // Este bloque NO redefine ningún valor: solo apunta a las variables
        // CSS, que son la fuente de verdad única (THERS_IMPLEMENTACION_
        // MAESTRA_CLAUDE.md §11). Los roles se resuelven según la variante
        // de shell activa (data-th-shell), así que `bg-th-surface` es
        // correcto tanto en Feed como en Configuración sin duplicar clases.
        //
        // Convive con los tokens anteriores (canvas/surface/ink/muted/line/
        // pulse/ember): esos siguen en uso en auth, help, public y legal, y
        // no se tocan.
        th: {
          bg: "var(--th-bg)",
          "bg-subtle": "var(--th-bg-subtle)",
          surface: "var(--th-surface)",
          "surface-subtle": "var(--th-surface-subtle)",
          "surface-raised": "var(--th-surface-raised)",
          "surface-translucent": "var(--th-surface-translucent)",

          fg: "var(--th-fg)",
          "fg-strong": "var(--th-fg-strong)",
          "fg-muted": "var(--th-fg-muted)",
          "fg-subtle": "var(--th-fg-subtle)",
          "fg-inverse": "var(--th-fg-inverse)",

          border: "var(--th-border)",
          "border-subtle": "var(--th-border-subtle)",
          "border-strong": "var(--th-border-strong)",

          brand: "var(--th-brand)",
          "brand-hover": "var(--th-brand-hover)",
          "brand-fg": "var(--th-brand-fg)",
          "brand-soft": "var(--th-brand-soft)",
          "brand-soft-strong": "var(--th-brand-soft-strong)",
          "on-brand": "var(--th-on-brand)",

          "success-accent": "var(--th-success-accent)",
          "success-fg": "var(--th-success-fg)",
          "success-surface": "var(--th-success-surface)",
          "warning-accent": "var(--th-warning-accent)",
          "warning-border": "var(--th-warning-border)",
          "danger-border": "var(--th-danger-border)",
          "warning-fg": "var(--th-warning-fg)",
          "warning-surface": "var(--th-warning-surface)",
          "danger-accent": "var(--th-danger-accent)",
          "danger-fg": "var(--th-danger-fg)",
          "danger-surface": "var(--th-danger-surface)",
        },
      },
      fontFamily: {
        // Plus Jakarta Sans está en las 24 referencias (manifest §2).
        jakarta: "var(--th-font-sans)",
      },
      fontSize: {
        // Escala del cuerpo de DESIGN.md (archivo maestro §5.4).
        "headline-xl": [
          "var(--th-text-headline-xl)",
          { lineHeight: "var(--th-leading-headline-xl)", letterSpacing: "var(--th-tracking-headline-xl)", fontWeight: "800" },
        ],
        "headline-lg": [
          "var(--th-text-headline-lg)",
          { lineHeight: "var(--th-leading-headline-lg)", letterSpacing: "var(--th-tracking-headline-lg)", fontWeight: "700" },
        ],
        "headline-md": [
          "var(--th-text-headline-md)",
          { lineHeight: "var(--th-leading-headline-md)", letterSpacing: "var(--th-tracking-headline-md)", fontWeight: "700" },
        ],
        "headline-sm": [
          "var(--th-text-headline-sm)",
          { lineHeight: "var(--th-leading-headline-sm)", letterSpacing: "var(--th-tracking-headline-sm)", fontWeight: "600" },
        ],
        "body-lg": [
          "var(--th-text-body-lg)",
          { lineHeight: "var(--th-leading-body-lg)", letterSpacing: "var(--th-tracking-body-lg)" },
        ],
        "body-md": ["var(--th-text-body-md)", { lineHeight: "var(--th-leading-body-md)" }],
        "body-sm": [
          "var(--th-text-body-sm)",
          { lineHeight: "var(--th-leading-body-sm)", letterSpacing: "var(--th-tracking-body-sm)" },
        ],
        "label-lg": [
          "var(--th-text-label-lg)",
          { lineHeight: "var(--th-leading-label-lg)", letterSpacing: "var(--th-tracking-label-lg)", fontWeight: "600" },
        ],
        "label-md": [
          "var(--th-text-label-md)",
          { lineHeight: "var(--th-leading-label-md)", letterSpacing: "var(--th-tracking-label-md)", fontWeight: "600" },
        ],
        "label-sm": [
          "var(--th-text-label-sm)",
          { lineHeight: "var(--th-leading-label-sm)", letterSpacing: "var(--th-tracking-label-sm)", fontWeight: "700" },
        ],
      },
      spacing: {
        "th-sidebar": "var(--th-sidebar-w)",
        "th-topbar": "var(--th-topbar-h)",
        "th-bottomnav": "var(--th-bottomnav-h)",
        "th-gutter": "var(--th-gutter)",
        "th-margin": "var(--th-margin)",
      },
      maxWidth: {
        "th-feed": "var(--th-feed-max)",
        "th-rail": "var(--th-rail-w)",
      },
      width: {
        "th-sidebar": "var(--th-sidebar-w)",
        "th-rail": "var(--th-rail-w)",
        "th-msg-list": "var(--th-msg-list-w)",
        "th-msg-context": "var(--th-msg-context-w)",
      },
      borderRadius: {
        "th-xs": "var(--th-radius-xs)",
        "th-sm": "var(--th-radius-sm)",
        "th-input": "var(--th-radius-input)",
        "th-card": "var(--th-radius-card)",
        "th-dialog": "var(--th-radius-dialog)",
        "th-pill": "var(--th-radius-pill)",
      },
      zIndex: {
        "th-sticky": "var(--th-z-sticky)",
        "th-nav": "var(--th-z-nav)",
        "th-backdrop": "var(--th-z-backdrop)",
        "th-modal": "var(--th-z-modal)",
        "th-toast": "var(--th-z-toast)",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(0,0,0,0.06), 0 12px 28px -14px rgba(0,0,0,0.18)",
        lift: "0 24px 48px -18px rgba(147,51,234,0.35)",
        glow: "0 0 0 4px rgba(147,51,234,0.16)",
        "th-card": "var(--th-shadow-card)",
        "th-hover": "var(--th-shadow-hover)",
        "th-overlay": "var(--th-shadow-overlay)",
        "th-focus": "var(--th-shadow-focus-soft)",
        "th-compose": "var(--th-shadow-compose)",
      },
      keyframes: {
        marquee: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        capsuleIn: {
          "0%": { opacity: 0, transform: "translateY(14px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        popLike: {
          "0%": { transform: "scale(1)" },
          "40%": { transform: "scale(1.35)" },
          "100%": { transform: "scale(1)" },
        },
        moodGlow: {
          "0%, 100%": { opacity: 0.5 },
          "50%": { opacity: 1 },
        },
        floatIn: {
          "0%": { opacity: 0, transform: "translateY(10px) scale(0.98)" },
          "100%": { opacity: 1, transform: "translateY(0) scale(1)" },
        },
      },
      animation: {
        marquee: "marquee 30s linear infinite",
        "capsule-in": "capsuleIn 0.45s cubic-bezier(0.16,1,0.3,1) both",
        "pop-like": "popLike 0.35s ease-in-out",
        "mood-glow": "moodGlow 2.6s ease-in-out infinite",
        "float-in": "floatIn 0.2s ease-out both",
      },
    },
  },
  plugins: [],
}