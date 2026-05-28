---
title: "10.05 — igoristan workflows"
description: "The Igoristan workflows: ci-pr with three parallelized jobs on PRs, and deploy for publishing to GitHub Pages."
weight: 5
date: 2026-05-20
series: ["ci-cd"]
series_order: 5
---

# 10.05&nbsp;—&nbsp;`igoristan` workflows

> See also [`../05-igoristan/07-ci-deploy.md`](../05-igoristan/07-ci-deploy.md)

## Overview

| Workflow     | Trigger             | OS                                                       | Effect                                                                             | Note       |
| ------------ | ------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------- |
| `ci-pr.yml`  | PR `**`, dispatch   | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm&nbsp;10 | 3 parallelized jobs: `wireit ci:format-check` + `wireit lint` + `wireit typecheck` | PR gate    |
| `deploy.yml` | push main, dispatch | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm&nbsp;10 | `pnpm install --frozen-lockfile` + `pnpm build` + upload Pages                     | Production |

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
      # ... same setup ...
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
      # ... same setup ...
      - name: Typecheck
        run: pnpm typecheck
```

| Job            | Additional cache                        |
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

Enables the _wireit_ cache. Subsequent runs reuse wireit artifacts.

## No tests in `ci-pr.yml`

Igoristan **has no unit tests**. See [`../05-igoristan/07-ci-deploy.md`](../05-igoristan/07-ci-deploy.md):

> Igoristan _has no unit tests_. Why?
>
> - It's a **demo app**, not a lib.
> - The random behaviors (10%, 30%, 20%) are _deliberate_.
> - The behaviors are **tested e2e** by `ocarina-example`.

Tests are elsewhere. Igoristan just validates that the code compiles and passes lint.

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

1. **`concurrency: pages, cancel-in-progress: false`**: prevents two simultaneous deploys (race condition). The second waits.
2. **`pnpm install --frozen-lockfile`**: determinism. No lockfile change. Guarantees the same build in CI as locally.
3. **`pnpm build` = `wireit build` = lint + typecheck + vike build**. If lint/typecheck fails, build fails → deploy doesn't run.

## `dist/client/`

```yaml
- uses: actions/upload-pages-artifact@v4
  with:
    path: dist/client
```

Vike's _bundle_ is produced in `dist/client/` (vs `dist/server/` which holds the SSR runtime, not used here). We upload _only_ `client/` for Pages.

## Final URL

https://mojo-molotov.github.io/igoristan/

`/igoristan` prefix configured in `vite.config.ts#base`.
