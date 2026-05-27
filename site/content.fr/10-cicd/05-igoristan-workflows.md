---
title: "10.05 — Workflows igoristan"
description: "Voir aussi ../05-igoristan/07-ci-deploy.md"
weight: 5
date: 2026-05-20
series: ["ci-cd"]
series_order: 5
---

# 10.05&nbsp;—&nbsp;Workflows `igoristan`

> Voir aussi [`../05-igoristan/07-ci-deploy.md`](../05-igoristan/07-ci-deploy.md)

## Vue d'ensemble

| Workflow     | Trigger             | OS                                                       | Effet                                                                                              | Note       |
| ------------ | ------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ---------- |
| `ci-pr.yml`  | PR `**`, dispatch   | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm&nbsp;10 | 3 jobs parallélisés&nbsp;: `wireit ci:format-check` +&nbsp;`wireit lint` +&nbsp;`wireit typecheck` | Gate PR    |
| `deploy.yml` | push main, dispatch | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm&nbsp;10 | `pnpm install --frozen-lockfile` +&nbsp;`pnpm build` +&nbsp;upload&nbsp;Pages                      | Production |

## `ci-pr.yml`

```yaml
jobs:
  format-check:
    env:
      WIREIT_CACHE: github
    steps:
      - uses: actions/checkout@v6
      - uses: pnpm/action-setup@v5
        with: { version: 11 }
      - uses: actions/setup-node@v6
        with: { node-version: 24, cache: "pnpm" }
      - uses: google/wireit@setup-github-actions-caching/v2
      - run: make install
      - name: Formatcheck
        run: make ci:format-check

  lint:
    env:
      WIREIT_CACHE: github
    steps:
      # ... idem setup ...
      - uses: actions/cache@v5
        with:
          path: .eslintcache
          key: eslint-cache-${{ hashFiles('eslint.config.ts', 'src/**/*.*', 'package.json') }}
      - name: Lint
        run: pnpm lint

  typecheck:
    env:
      WIREIT_CACHE: github
    steps:
      # ... idem setup ...
      - name: Typecheck
        run: pnpm typecheck
```

| Job            | Cache supplémentaire                    |
| -------------- | --------------------------------------- |
| `format-check` | wireit                                  |
| `lint`         | wireit + `.eslintcache` (actions/cache) |
| `typecheck`    | wireit + `tsbuildinfo` (via wireit)     |

## `WIREIT_CACHE: github`

```yaml
env:
  WIREIT_CACHE: github
steps:
  - uses: google/wireit@setup-github-actions-caching/v2
```

Active le cache _wireit_. Les runs successifs réutilisent les artefacts wireit.

## Pas de tests dans `ci-pr.yml`

Igoristan **n'a pas de tests unitaires**. Cf. [`../05-igoristan/07-ci-deploy.md`](../05-igoristan/07-ci-deploy.md)&nbsp;:

> L'Igoristan _n'a pas de tests unitaires_. Pourquoi&nbsp;?
>
> - C'est une **app démo**, pas une lib.
> - Les comportements aléatoires (10%, 30%, 20%) sont _volontaires_.
> - Les comportements sont **testés en e2e** par `ocarina-example`.

→ Les tests sont _ailleurs_. L'Igoristan se contente de valider que le code _compile_ et passe le _lint_.

## `deploy.yml`

```yaml
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
      - uses: actions/upload-pages-artifact@v4
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

1. **`concurrency: pages, cancel-in-progress: false`**&nbsp;: empêche deux deploys simultanés (race condition). Le second attend.
2. **`pnpm install --frozen-lockfile`**&nbsp;: déterminisme. Pas de modif du lock. Garantie d'avoir le même build en CI qu'en local.
3. **`pnpm build` = `wireit build` = lint + typecheck + vike build**. Si lint/typecheck fail, build fail&nbsp;→&nbsp;deploy ne tourne pas.

## `dist/client/`

```yaml
- uses: actions/upload-pages-artifact@v4
  with:
    path: dist/client
```

Le _bundle_ Vike est produit dans `dist/client/` (vs `dist/server/` qui contient le SSR runtime, non utilisé ici). On upload _juste_ `client/` pour Pages.

## URL finale

https://mojo-molotov.github.io/igoristan/

Préfixe `/igoristan` configuré dans `vite.config.ts#base`.
