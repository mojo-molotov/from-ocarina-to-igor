---
title: "05.07 — CI/CD de l'Igoristan"
description: "Deux workflows : ci-pr.yml sur PR (3 jobs parallèles), deploy.yml sur push main (GitHub Pages)."
weight: 7
date: 2026-05-20
series: ["igoristan"]
series_order: 7
tags: ["ci-cd"]
---

# 05.07&nbsp;—&nbsp;CI/CD de l'Igoristan

> Deux workflows&nbsp;: `ci-pr.yml` sur PR (3 jobs parallèles), `deploy.yml` sur push main (GitHub Pages).

## `ci-pr.yml`

```yaml
name: CI/PR

on:
  pull_request:
    branches: ["**"]
  workflow_dispatch:

defaults:
  run:
    shell: bash

jobs:
  format-check:
    runs-on: ubuntu-latest
    env:
      WIREIT_CACHE: github
    steps:
      - uses: actions/checkout@v6
      - uses: pnpm/action-setup@v5
        with: { version: 11 }
      - uses: actions/setup-node@v6
        with: { node-version: 24, cache: "pnpm" }
      - uses: google/wireit@setup-github-actions-caching/v2
      - name: Install project
        run: make install
      - name: Formatcheck
        run: make ci:format-check

  lint:
    runs-on: ubuntu-latest
    env:
      WIREIT_CACHE: github
    steps:
      # ... idem ...
      - uses: actions/cache@v5
        with:
          path: .eslintcache
          key: eslint-cache-${{ hashFiles('eslint.config.ts', 'src/**/*.*', 'package.json') }}
      - name: Lint
        run: pnpm lint

  typecheck:
    runs-on: ubuntu-latest
    env:
      WIREIT_CACHE: github
    steps:
      # ... idem ...
      - name: Typecheck
        run: pnpm typecheck
```

| Job            | Commande                                        | Cache                                   |
| -------------- | ----------------------------------------------- | --------------------------------------- |
| `format-check` | `pnpm exec prettier . --check` (via wireit)     | wireit + node_modules                   |
| `lint`         | `pnpm exec eslint ... --max-warnings 0 --cache` | wireit + `.eslintcache` (actions/cache) |
| `typecheck`    | `tsc --build --pretty tsconfig.json`            | wireit + `tsbuildinfo`                  |

```
                          PR opened / push
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                 ▼                 ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ format-check │ │     lint     │ │  typecheck   │
        │ (1-2 minutes)│ │ (1-2 minutes)│ │ (1-2 minutes)│
        └──────────────┘ └──────────────┘ └──────────────┘
                │                 │                 │
                └─────────────────┴─────────────────┘
                                  ▼
                             PR mergeable
```

## `deploy.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: pnpm/action-setup@v5
        with: { version: 11 }
      - uses: actions/setup-node@v6
        with: { node-version: 24, cache: "pnpm" }
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
      - name: Build
        run: pnpm build
      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v4
        with: { path: dist/client }

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

| Job      | Effet                                                                                                                                           |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `build`  | `pnpm install --frozen-lockfile`&nbsp;→&nbsp;`pnpm build` (= `wireit build` = `lint → typecheck → vike build`)&nbsp;→&nbsp;upload `dist/client` |
| `deploy` | `actions/deploy-pages@v5`&nbsp;→&nbsp;publie l'artifact&nbsp;→&nbsp;URL = https://mojo-molotov.github.io/igoristan/                             |

## `concurrency: pages` + `cancel-in-progress: false`

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: false
```

Empêche **deux déploiements simultanés** (race condition).  
Le second attend (`cancel-in-progress: false`&nbsp;→&nbsp;on _ne_ cancel _pas_ le run en cours).

## `pnpm install --frozen-lockfile`

```yaml
- name: Install dependencies
  run: pnpm install --frozen-lockfile
```

`--frozen-lockfile`&nbsp;:

- Lit `pnpm-lock.yaml` exactement.
- Refuse de modifier le lock (même si une dep avait une nouvelle version compatible).
- Échec si une dépendance manque dans le lock.

→ Déterminisme. La CI installe **exactement** ce qui a été testé en local.

## Pas de `lint` /&nbsp;`typecheck` dans `deploy.yml`

C'est volontaire&nbsp;: le `wireit build` _dépend_ de `prebuild` qui dépend de `lint + typecheck`.  
Si ceux-ci échouent, `build` échoue.

Donc&nbsp;: `pnpm build` _inclut_ lint+typecheck.  
Pas besoin de les répéter dans le YAML.

## Pas de tests dans `deploy.yml`

Igoristan _n'a pas de tests unitaires_.

- C'est une **app démo**, pas une lib.
- Les comportements aléatoires (10%, 30%, 20%) sont _volontaires_.
- Les comportements sont **testés en e2e** par `ocarina-example`.

L'Igoristan _est_ le SUT, donc les tests _sont_ ailleurs.

## `defaults.run.shell: bash`

```yaml
defaults:
  run:
    shell: bash
```

→ Tous les steps `run: ...` utilisent `bash`.

## Pas de matrice OS

L'Igoristan ne se compile que sur ubuntu-latest. Pas de Windows /&nbsp;macOS. Le bundle est juste du JS statique, l'OS de build importe peu.

À comparer avec `ocarina` (cf. [`../10-cicd/02-ocarina-workflows.md`](../10-cicd/02-ocarina-workflows.md)) qui teste sur ubuntu+windows pour vérifier la portabilité Python (notamment pour des raisons de manipulation de chemins de fichiers, mais pas que).
