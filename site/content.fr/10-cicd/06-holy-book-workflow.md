---
title: "10.06 — Workflow ocarina-holy-book"
description: "Le workflow unique du Holy Book, deploy.yml : sur push main, build VitePress puis publication sur GitHub Pages."
weight: 6
date: 2026-05-20
series: ["ci-cd"]
series_order: 6
---

# 10.06&nbsp;—&nbsp;Workflow `ocarina-holy-book`

> Un seul workflow&nbsp;: `deploy.yml`. Sur push main&nbsp;→&nbsp;build VitePress →&nbsp;upload Pages.

## Code

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
        with:
          fetch-depth: 0 # ← full clone

      - uses: pnpm/action-setup@fcf821c621167805dd63a29662bd7cb5676c81a8
        name: Install pnpm
        with:
          version: 11

      - name: Use Node.js
        uses: actions/setup-node@v6
        with:
          node-version: 24
          cache: "pnpm"

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build
        run: pnpm build

      - uses: actions/upload-pages-artifact@v4
        with:
          path: docs/.vitepress/dist

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

## Analyse

### 1. `TZ: Europe/Paris`

```yaml
env:
  TZ: Europe/Paris
```

Force la timezone du runner à Europe/Paris.  
Les dates rendues par VitePress («&nbsp;_Last update: 18/05/2026 11h42_&nbsp;») sont à l'heure de Paris, pas en UTC.

L'auteur habitant à Palneca, laisser en UTC provoquerait des bugs de fuseaux horaires mystérieux.

### 2. `fetch-depth: 0`

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 0
```

`fetch-depth: 0` = full git clone (vs depth 1 par défaut).

VitePress (via le theme `@sugarat/theme`) lit le **Git log** pour calculer la date «&nbsp;_Last update_&nbsp;» de chaque page. Sans full history&nbsp;:&nbsp;VitePress ne voit que le dernier commit, toutes les pages auraient la même date.

### 3. `pnpm/action-setup` épinglé par SHA

```yaml
- uses: pnpm/action-setup@fcf821c621167805dd63a29662bd7cb5676c81a8
```

Le _version pinning_ par SHA est utilisé partout pour toutes actions non-officielles (non préfixées par `actions/`) pour mitiger les risques de _Supply Chain Attack_.

### 4. `--frozen-lockfile`

Cf. [`05-igoristan-workflows.md`](05-igoristan-workflows.md)

### 5. `concurrency: pages, cancel-in-progress: false`

Empêche les deploys simultanés vers GitHub Pages (race condition).

## Build

```bash
pnpm build
# = vitepress build docs
```

VitePress produit&nbsp;:

- HTML statique par route (EN + FR + RU).
- Bundle JS/CSS.
- Index `pagefind/` pour la recherche.
- `llms.txt` + `llms-full.txt` (via plugin maison).
- PDFs servis depuis `public/`.

Output&nbsp;: `docs/.vitepress/dist/`.

## Déploiement

```yaml
- uses: actions/upload-pages-artifact@v4
  with:
    path: docs/.vitepress/dist
```

```yaml
- id: deployment
  uses: actions/deploy-pages@v5
```

## URL finale

https://mojo-molotov.github.io/ocarina-holy-book/

Préfixe `/ocarina-holy-book` configuré dans `config.mts#base`&nbsp;:

```typescript
const base =
  process.env.GITHUB_ACTIONS === "true" ? "/ocarina-holy-book/" : "/";
```

## _Trigger_ des PR

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

Le `pull_request` est inclus&nbsp;!  
Chaque PR _build_ aussi le site (pour tester que la compilation n'est pas cassée).

Mais les PR ne _deploy_ pas.

## Aucun test dynamique auto

Le Holy Book n'a **pas de tests dynamiques automatisés**.  
Il est testé manuellement.

## Cadences

| Trigger   | Fréquence                         |
| --------- | --------------------------------- |
| Push main | À chaque commit fusionné sur main |
| PR        | À chaque push sur PR              |
| Manuel    | À la demande                      |
