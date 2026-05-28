---
title: "05.01 — Stack de l'Igoristan"
description: "La stack de l'Igoristan : React 19, Vike en SSG, Vite 7, TailwindCSS 4 et Valibot, orchestrée par wireit et pnpm."
weight: 1
date: 2026-05-20
series: ["igoristan"]
series_order: 1
---

# 05.01&nbsp;—&nbsp;Stack de l'Igoristan

## `package.json`

```json
{
  "react": "^19.2.3",
  "react-dom": "^19.2.3",
  "vike": "^0.4.258",
  "vike-react": "^0.6.21",
  "valibot": "^1.2.0",
  "react-hook-form": "^7.71.1",
  "@hookform/resolvers": "^5.2.2",
  "react-dropzone": "^14.3.8",
  "lucide-react": "^0.562.0",
  "usehooks-ts": "^3.1.1",
  "throttleit": "^2.1.0",
  "uuid": "^13.0.0",
  "clsx": "^2.1.1",
  "class-variance-authority": "^0.7.1",
  "tailwind-merge": "^3.0.2",
  "tailwindcss-animate": "^1.0.7",
  "@radix-ui/react-slot": "^1.2.4"
}
```

| Lib                                                  | Rôle                                                                                      |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **React 19.2**                                       | UI, hooks                                                                                 |
| **Vike 0.4** + `vike-react`                          | SSG /&nbsp;SSR framework au-dessus de Vite (anciennement «&nbsp;_vite-plugin-ssr_&nbsp;») |
| **Valibot 1.2**                                      | Validation de schémas TS (alternative légère à Zod)                                       |
| **react-hook-form**                                  | Gestion de formulaires                                                                    |
| **react-dropzone**                                   | Composant drag-and-drop pour upload                                                       |
| **lucide-react**                                     | Icones                                                                                    |
| **usehooks-ts**                                      | Hooks utilitaires (`useLocalStorage`, etc.), utilisé par `useAuth`                        |
| **throttleit**                                       | Throttle                                                                                  |
| **uuid**                                             | Génération d'IDs                                                                          |
| **clsx + tailwind-merge + class-variance-authority** | Utilitaires Tailwind                                                                      |

## `devDependencies`

```json
{
  "vite": "^7.3.1",
  "@vitejs/plugin-react": "^5.1.2",
  "@tailwindcss/vite": "^4.1.3",
  "@tailwindcss/postcss": "^4.0.17",
  "tailwindcss": "^4.1.1",
  "terser": "^5.39.0",
  "vite-plugin-compression": "^0.5.1",
  "rollup-plugin-visualizer": "^5.14.0",
  "@qalisa/vike-plugin-sitemap": "^1.7.0",

  "typescript": "^6.0.3",
  "typescript-eslint": "^8.59.0",
  "eslint": "^9.18.0",
  "@eslint/js": "^9.39.2",
  "eslint-plugin-import-x": "^4.6.1",
  "eslint-plugin-perfectionist": "^4.6.0",
  "eslint-plugin-react": "^7.37.4",
  "eslint-plugin-react-hooks": "^5.2.0",
  "eslint-plugin-unused-imports": "^4.2.1",
  "globals": "^15.15.0",

  "prettier": "^3.5.3",
  "prettier-plugin-tailwindcss": "^0.6.11",

  "husky": "^9.1.7",
  "lint-staged": "^15.5.0",
  "commitizen": "^4.3.1",
  "@commitlint/config-conventional": "^19.8.0",
  "@commitlint/cz-commitlint": "^19.8.0",
  "is-ci": "^4.1.0",
  "editorconfig": "^2.0.1",
  "minimatch": "^10.1.1",
  "rimraf": "^6.0.1",
  "wireit": "^0.14.11"
}
```

## `engines`

```json
{
  "node": "^24.x",
  "pnpm": "11.x"
}
```

→ Node 24, pnpm 11. **`packageManager: pnpm@11.x`** verrouille la version.

## `vite.config.ts`

```ts
const ORIGIN = "https://mojo-molotov.github.io";
const BASE = "/igoristan";
const SITEMAP_EXCLUSIONS = ["**/igoristan/dashboard/**"] as const;

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    viteCompression({ algorithm: "gzip" }),
    viteCompression({ algorithm: "brotliCompress", ext: ".br" }),
    visualizer({ filename: "stats-sunburst.html", template: "treemap" }),
    vike(),
    sitemap({
      sitemapGenerator: (entries) =>
        entries.filter(
          (e) => !minimatch(new URL(e.loc).pathname, SITEMAP_EXCLUSIONS[0]),
        ),
      baseUrl: ORIGIN + BASE,
      pagesDir: "src/pages",
    }),
  ],
  build: {
    terserOptions: {
      compress: { drop_debugger: true, drop_console: true },
    },
    minify: "terser",
  },
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  base: BASE,
});
```

| Plugin                                           | Rôle                                                                       |
| ------------------------------------------------ | -------------------------------------------------------------------------- |
| `react()`                                        | JSX + Fast Refresh (HMR)                                                   |
| `tailwindcss()`                                  | Tailwind 4                                                                 |
| `viteCompression({gzip})` + `({brotliCompress})` | Pre-compress assets, servis par GitHub Pages                               |
| `visualizer()`                                   | Génère `stats-sunburst.html` pour analyser le bundle                       |
| `vike()`                                         | SSG/SSR framework                                                          |
| `sitemap({...})`                                 | Sitemap auto-généré, **exclut** `/dashboard/**` (pages protégées par auth) |
| `terser`                                         | Minification + `drop_console: true` + `drop_debugger: true`                |
| `@` alias                                        | `@/components/Foo`&nbsp;→&nbsp;`src/components/Foo`                        |
| `base: '/igoristan'`                             | Path prefix pour Pages                                                     |

## L'alias `@`

Courant dans l'écosystème TS.  
Tous les imports du projet utilisent `@/`&nbsp;:

```ts
import { useAutoPlayAudio } from "@/hooks/useAutoplayAudio";
import { pickRandom } from "@/lib/pickRandom";
import ROUTES from "@/config/routes";
import BRAND from "@/config/brand";
```

Convention&nbsp;: pas d'imports relatifs `../../../foo` sauf pour les assets (`../../../assets/gifs/foo.gif`).  
Alias TS dans projet "personnel" = OK. [De préférene à éviter lorsqu'il s'agit de créer une lib npm.](https://x.com/mattpocockuk/status/1737899109808255439)

## Déploiement GH Pages

`base: '/igoristan'` produit un bundle dont _toutes_ les ressources sont préfixées `/igoristan/`. C'est ce qui permet de servir depuis `https://mojo-molotov.github.io/igoristan/` sans avoir à patcher les URLs.
