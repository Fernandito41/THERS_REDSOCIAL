import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import mdx from '@mdx-js/rollup'
import remarkGfm from 'remark-gfm'
import remarkFrontmatter from 'remark-frontmatter'
import remarkMdxFrontmatter from 'remark-mdx-frontmatter'
import rehypeSlug from 'rehype-slug'

// Módulo 5 — Content Layer (ARC-001 §1 capa 2 Build Layer).
// El plugin MDX debe ejecutarse ANTES del plugin React (enforce: 'pre'):
//   .mdx → JSX → React plugin compila el JSX resultante.
// remark-frontmatter + remark-mdx-frontmatter exportan el frontmatter YAML
//   como named export `frontmatter` desde cada módulo MDX.
// rehype-slug añade id a cada heading (H2, H3...) — necesario para el TOC.
export default defineConfig({
  plugins: [
    {
      enforce: 'pre',
      ...mdx({
        remarkPlugins: [remarkGfm, remarkFrontmatter, remarkMdxFrontmatter],
        rehypePlugins: [rehypeSlug],
      }),
    },
    // include mdx para que el plugin React procese el JSX generado por MDX
    react({ include: /\.(jsx|js|ts|tsx|mdx)$/ }),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      // Alias para importar componentes del Design System desde MDX
      // sin paths relativos frágiles (ej: import Callout from '@ui/Callout')
      '@ui': '/src/components/ui',
    },
  },
})
