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
        // Paleta dedicada del Footer (superficie piloto de la nueva direccion
        // visual -- ver propuesta). No es gris neutro plano: negro con leve
        // croma frio, hairline solido y un violeta refinado como unico acento.
        // Alcance acotado: solo la usa el Footer; el resto de la app no cambia.
        footer: {
          DEFAULT: "#0A0B0D", // zocalo -- mas profundo que canvas-dark, es "el suelo"
          line: "#21252C", // hairline solido (reemplaza al white/10 turbio)
          heading: "#F5F6F8", // wordmark -- blanco calido, no #fff puro
          link: "#9BA1AC", // enlaces / labels / copyright en reposo (>7:1 sobre DEFAULT)
          "link-hover": "#E8EAED",
          accent: "#A78BFA", // violeta refinado -- subrayado de hover (foco = regla global)
          "line-soft": "#E7E8EB", // variante compact (superficie clara)
          "link-soft": "#5B616B", // variante compact
          "link-soft-hover": "#111317",
        },
      },
      boxShadow: {
        soft: "0 1px 2px rgba(0,0,0,0.06), 0 12px 28px -14px rgba(0,0,0,0.18)",
        lift: "0 24px 48px -18px rgba(147,51,234,0.35)",
        glow: "0 0 0 4px rgba(147,51,234,0.16)",
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
      transitionTimingFunction: {
        // Misma curva "ease-out fuerte" que `capsule-in` -- se reutiliza en
        // microinteracciones (footer/disclosure) para un ritmo de motion unico.
        strong: "cubic-bezier(0.16, 1, 0.3, 1)",
      },
    },
  },
  plugins: [],
}