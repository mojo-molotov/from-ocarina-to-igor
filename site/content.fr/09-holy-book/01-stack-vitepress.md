---
title: "09.01 — Stack VitePress + Sugar Theme + plugins maison"
description: "La stack du Holy Book : VitePress 2 alpha, le thème Sugar, des plugins maison et pagefind pour la recherche."
weight: 1
date: 2026-05-20
series: ["holy-book"]
series_order: 1
---

# 09.01&nbsp;—&nbsp;Stack VitePress + Sugar Theme + plugins maison

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

| Lib                                        | Rôle                                                      |
| ------------------------------------------ | --------------------------------------------------------- |
| `vitepress 2.0.0-alpha.17`                 | SSG framework, basé sur Vite                              |
| `@sugarat/theme`                           | Theme blog tier-1 (templates, sidebar auto, cover images) |
| `vue 3.5.33`                               | Requis par VitePress                                      |
| `vitepress-plugin-image-optimize`          | Optimisation des images au build                          |
| `pagefind 1.5.2`                           | Moteur de recherche statique (full-text, side-CDN)        |
| `sass-embedded`                            | Compile SCSS (utilisé par `@sugarat/theme`)               |
| Husky /&nbsp;lint-staged /&nbsp;commitlint | Mêmes outils que les autres dépôts (Conventional Commits) |

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

→ En CI (GitHub Actions)&nbsp;: base = `/ocarina-holy-book/` (préfixe GitHub Pages).  
→ En local&nbsp;: `/` (sert depuis la racine du _dev server_).

### 2. `locales` FR + EN + RU

1. `root` (= EN)&nbsp;: default, sert depuis `/<page>`.
2. `fr`&nbsp;: sert depuis `/fr/<page>`.
3. `ru`&nbsp;: sert depuis `/ru/<page>`.

### 3. Labels personnalisés (FR)

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

Traduction propre des éléments d'UI VitePress.

### 4. Plugins maison

```typescript
import { generateSkills } from "./plugins/skills";
import { generateLlms } from "./plugins/llm";
import { generatePub } from "./plugins/pub";
import webpConfig from "./plugins/webp";
```

| Plugin      | Rôle                                                          |
| ----------- | ------------------------------------------------------------- |
| `skills.ts` | Génère les pages publiques à partir de `ai/skills/*/SKILL.md` |
| `llm.ts`    | Génère `llms.txt` + `llms-full.txt` au build                  |
| `pub.ts`    | Sert les PDFs depuis `pub/`                                   |
| `webp.ts`   | Convertit les images en WebP au build                         |

### 5. `blogTheme`

```typescript
import { blogTheme } from "./blog-theme";
```

`@sugarat/theme`, wrappé dans `blog-theme.ts`, ajoute&nbsp;:

- Cards des articles sur la page d'accueil.
- Cover images via `head.meta.og:image`.
- Auto-sidebar.
- Pagination.

## Écosystème de plugins

### `llm.ts`

Génère deux fichiers&nbsp;:

1. **`llms.txt`**, index minimaliste pour les LLMs&nbsp;: URLs, descriptions courtes - https://llmstxt.org/
2. **`llms-full.txt`**&nbsp;: contenu complet en plaintext, scrappable d'un coup.

Ces fichiers permettent à un LLM (Claude, ChatGPT) qui visite le Holy Book de récupérer **toute la doc** en quelques appels HTTP.

### `pub.ts`

Sert les PDFs depuis `pub/ocarina-fr.pdf`, `pub/ocarina-ru.pdf` et `pub/ocarina-en.pdf`&nbsp;:

- `https://.../ocarina-fr.pdf`
- `https://.../ocarina-en.pdf`
- `https://.../ocarina-ru.pdf`

### `skills.ts`

Traverse `ai/skills/*/SKILL.md` et génère des pages publiques sous `/skills/<name>`. Permet de compléter la cartographie dans les ressources exposées, qui est comme une extension au `sitemap.xml` mais totalement dédiée aux LLMs.

### `webp.ts`

Optimisation des images&nbsp;: convertit les PNG/JPG en WebP au build, écrit les `<picture>` tags pour fallback.

## `docs/.vitepress/blog-theme.ts`

Configure `@sugarat/theme`&nbsp;:

```typescript
export const blogTheme = getThemeConfig({
  blog: {
    name: "Le livre sacré d'Ocarina",
    minScreenAvatar: false,
    pageSize: 6,
    analysis: false,
  },
  search: 'pagefind',                              // ← Pagefind plutôt qu'Algolia
  ...
});
```

- `pageSize: 6`&nbsp;: articles affichés maximum 6 par 6 sur la page d'accueil.
- `analysis: false`&nbsp;: pas d'analytics.
- `search: 'pagefind'`&nbsp;: moteur de recherche **statique** (pas Algolia, pas de SaaS).

## `pagefind`

```json
"scripts": {
  "build": "vitepress build docs"
}
```

VitePress `build` invoque `vitepress build` qui&nbsp;:

1. Compile les Markdown en HTML.
2. Construit le bundle JS/CSS.
3. (via plugin Sugar) Lance `pagefind` qui indexe le HTML généré en `pagefind/` (CDN d'index statique).

Résultat&nbsp;: **documentation avec moteur de recherche 100% statique**, pas de backend.

## build

```bash
pnpm install
pnpm build              # → docs/.vitepress/dist/
```

Output&nbsp;: `docs/.vitepress/dist/`  
Contient HTML, assets, `pagefind/`, `llms.txt`, `llms-full.txt`, `skills/`, PDFs (servis depuis `public/`).

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
        with: { fetch-depth: 0 } # ← full clone (pour Last update auto)
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

1. **`fetch-depth: 0`**&nbsp;: full git clone&nbsp;—&nbsp;nécessaire pour que VitePress puisse calculer la date «&nbsp;_Last update_&nbsp;» de chaque page à partir du log Git.
2. **`TZ: Europe/Paris`**&nbsp;: tous les rendus de dates en heure de Paris (utile pour «&nbsp;_Dernière mise à jour&nbsp;: 18/05/2026 11h42_&nbsp;»).
3. **`concurrency: pages, cancel-in-progress: false`**&nbsp;: un seul deploy à la fois&nbsp;; le second attend (race condition).
