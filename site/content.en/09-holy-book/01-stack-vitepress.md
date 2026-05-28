---
title: "09.01 — VitePress + Sugar Theme + in-house plugins stack"
description: "The Holy Book stack: VitePress 2 alpha, the Sugar theme, in-house plugins and pagefind for search."
weight: 1
date: 2026-05-20
series: ["holy-book"]
series_order: 1
---

# 09.01&nbsp;—&nbsp;VitePress + Sugar Theme + in-house plugins stack

## `package.json`

```json
{
  "dependencies": {
    "@sugarat/theme": "0.5.17"
  },
  "devDependencies": {
    "@commitlint/config-conventional": "20.5.0",
    "@commitlint/cz-commitlint": "20.5.1",
    "@eslint/js": "10.0.1",
    "@types/node": "25.6.0",
    "commitizen": "4.3.1",
    "editorconfig": "3.0.2",
    "eslint": "10.2.1",
    "eslint-plugin-import-x": "4.16.2",
    "eslint-plugin-perfectionist": "5.9.0",
    "eslint-plugin-unused-imports": "4.4.1",
    "globals": "17.5.0",
    "husky": "9.1.7",
    "inquirer": "9.0.0",
    "is-ci": "4.1.0",
    "lint-staged": "16.4.0",
    "pagefind": "1.5.2",
    "prettier": "3.8.3",
    "sass-embedded": "1.99.0",
    "typescript": "6.0.3",
    "typescript-eslint": "8.59.0",
    "vitepress": "2.0.0-alpha.17",
    "vitepress-plugin-image-optimize": "1.5.1",
    "vue": "3.5.33"
  },
  "engines": {
    "node": "^24.x",
    "pnpm": "11.x"
  }
}
```

| Lib                               | Role                                                     |
| --------------------------------- | -------------------------------------------------------- |
| `vitepress 2.0.0-alpha.17`        | SSG framework, Vite-based                                |
| `@sugarat/theme`                  | First-class blog theme (templates, auto sidebar, covers) |
| `vue 3.5.33`                      | Required by VitePress                                    |
| `vitepress-plugin-image-optimize` | Build-time image optimization                            |
| `pagefind 1.5.2`                  | Static search engine (full-text, side-CDN)               |
| `sass-embedded`                   | Compiles SCSS (used by `@sugarat/theme`)                 |
| Husky / lint-staged / commitlint  | Same tools as the other repos (Conventional Commits)     |

## `docs/.vitepress/config.mts`

```typescript
import { defineConfig } from 'vitepress';
import path from 'path';
import fs from 'fs';

import { generateSkills } from './plugins/skills';
import { generateLlms } from './plugins/llm';
import { generatePub } from './plugins/pub';
import { blogTheme } from './blog-theme';
import webpConfig from './plugins/webp';

const base = process.env.GITHUB_ACTIONS === 'true' ? '/ocarina-holy-book/' : '/';

export default defineConfig({
  locales: {
    root: {
      themeConfig: {
        outline: { label: 'Table of content' },
        skipToContentLabel: 'Skip to content',
        sidebarMenuLabel: 'Related articles',
        returnToTopLabel: 'Return to top',
        lastUpdatedText: 'Last update:'
      },
      description: "Ocarina is Igor's automated web browser testing framework.",
      title: 'The Ocarina Holy Book',
      label: 'English',
      lang: 'en'
    },
    fr: {
      themeConfig: {
        outline: { label: 'Sommaire', level: [2, 3] },
        returnToTopLabel: 'Retour en haut de page',
        lastUpdatedText: 'Dernière mise à jour :',
        skipToContentLabel: 'Passer au contenu',
        sidebarMenuLabel: 'Voir aussi'
      },
      title: "Le livre sacré d'Ocarina",
      label: 'Français',
      lang: 'fr'
    }
    ru: {
      themeConfig: {
        outline: {
          label: 'Оглавление',
          level: [2, 3]
        },
        skipToContentLabel: 'Перейти к содержанию',
        lastUpdatedText: 'Последнее обновление:',
        returnToTopLabel: 'Вернуться вверх',
        sidebarMenuLabel: 'Смотрите также'
      },
      title: 'Священная Книга Ocarina',
      label: 'Русский',
      lang: 'ru'
    }
  },
  vite: { ... },
  ...
});
```

### 1. `base`

```typescript
const base =
  process.env.GITHUB_ACTIONS === "true" ? "/ocarina-holy-book/" : "/";
```

In CI (GitHub Actions): base = `/ocarina-holy-book/` (GitHub Pages prefix).
Locally: `/` (served from the dev server root).

### 2. `locales` FR + EN + RU

1. `root` (= EN): default, served from `/<page>`.
2. `fr`: served from `/fr/<page>`.
3. `ru`: served from `/ru/<page>`.

### 3. Custom labels (FR)

```typescript
fr: {
  themeConfig: {
    outline: { label: 'Sommaire', level: [2, 3] },
    returnToTopLabel: 'Retour en haut de page',
    lastUpdatedText: 'Dernière mise à jour :',
    ...
  }
}
```

Clean translation of the VitePress UI strings.

### 4. In-house plugins

```typescript
import { generateSkills } from "./plugins/skills";
import { generateLlms } from "./plugins/llm";
import { generatePub } from "./plugins/pub";
import webpConfig from "./plugins/webp";
```

| Plugin      | Role                                               |
| ----------- | -------------------------------------------------- |
| `skills.ts` | Generates public pages from `ai/skills/*/SKILL.md` |
| `llm.ts`    | Generates `llms.txt` + `llms-full.txt` at build    |
| `pub.ts`    | Serves PDFs from `pub/`                            |
| `webp.ts`   | Converts images to WebP at build                   |

### 5. `blogTheme`

```typescript
import { blogTheme } from "./blog-theme";
```

`@sugarat/theme`, wrapped in `blog-theme.ts`, adds:

- Article cards on the homepage.
- Cover images via `head.meta.og:image`.
- Auto-sidebar.
- Pagination.

## Plugin ecosystem

### `llm.ts`

Generates two files:

1. **`llms.txt`**, a minimal index for LLMs: URLs, short descriptions&nbsp;—&nbsp;https://llmstxt.org/
2. **`llms-full.txt`**: full plaintext content, scrapable in one shot.

An LLM visiting the Holy Book can retrieve **all the docs** in a few HTTP calls.

### `pub.ts`

Serves PDFs from `pub/ocarina-fr.pdf`, `pub/ocarina-ru.pdf` and `pub/ocarina-en.pdf`:

- `https://.../ocarina-fr.pdf`
- `https://.../ocarina-en.pdf`
- `https://.../ocarina-ru.pdf`

### `skills.ts`

Walks `ai/skills/*/SKILL.md` and generates public pages under `/skills/<name>`. Completes the map of exposed resources&nbsp;—&nbsp;like `sitemap.xml` but dedicated to LLMs.

### `webp.ts`

Image optimization: converts PNG/JPG to WebP at build, writes `<picture>` tags for fallback.

## `docs/.vitepress/blog-theme.ts`

Configures `@sugarat/theme`:

```typescript
export const blogTheme = getThemeConfig({
  blog: {
    name: "Le livre sacré d'Ocarina",
    minScreenAvatar: false,
    pageSize: 6,
    analysis: false,
  },
  search: 'pagefind',                              // ← Pagefind rather than Algolia
  ...
});
```

- `pageSize: 6`: at most 6 articles per page on the homepage.
- `analysis: false`: no analytics.
- `search: 'pagefind'`: **static** search engine (no Algolia, no SaaS).

## `pagefind`

```json
"scripts": {
  "build": "vitepress build docs"
}
```

VitePress `build` invokes `vitepress build`, which compiles Markdown to HTML, builds the JS/CSS bundle, and (via the Sugar plugin) runs `pagefind`&nbsp;—&nbsp;indexing the generated HTML into `pagefind/`.

Result: **fully static search**, no backend.

## build

```bash
pnpm install
pnpm build              # → docs/.vitepress/dist/
```

Output: `docs/.vitepress/dist/`  
Contains HTML, assets, `pagefind/`, `llms.txt`, `llms-full.txt`, `skills/`, PDFs (served from `public/`).

## `deploy.yml`

```yaml
name: Deploy Ocarina Holy Book

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  TZ: Europe/Paris

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with: { fetch-depth: 0 } # ← full clone (for auto Last update)
      - uses: pnpm/action-setup@fcf821c25...
        with: { version: 11 }
      - uses: actions/setup-node@v6
        with: { node-version: 24, cache: "pnpm" }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - uses: actions/upload-pages-artifact@v4
        with: { path: docs/.vitepress/dist }

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v5
```

1. **`fetch-depth: 0`**: full git clone&nbsp;—&nbsp;VitePress needs full history to compute each page's "_Last update_" from Git log.
2. **`TZ: Europe/Paris`**: dates render in Paris time ("_Last update: 05/18/2026 11h42_").
3. **`concurrency: pages, cancel-in-progress: false`**: one deploy at a time; the second waits rather than canceling.
