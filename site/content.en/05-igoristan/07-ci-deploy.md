---
title: "05.07 — Igoristan CI/CD"
description: "Two workflows: ci-pr.yml on PR (3 parallel jobs), deploy.yml on push main (GitHub Pages)."
weight: 7
date: 2026-05-20
series: ["igoristan"]
series_order: 7
tags: ["ci-cd"]
---

# 05.07&nbsp;—&nbsp;Igoristan CI/CD

> Two workflows: `ci-pr.yml` on PR (3 parallel jobs), `deploy.yml` on push main (GitHub Pages).

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
      # ... same ...
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
      # ... same ...
      - name: Typecheck
        run: pnpm typecheck
```

| Job            | Command                                         | Cache                                   |
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

| Job      | Effect                                                                                                                      |
| -------- | --------------------------------------------------------------------------------------------------------------------------- |
| `build`  | `pnpm install --frozen-lockfile` → `pnpm build` (= `wireit build` = `lint → typecheck → vike build`) → upload `dist/client` |
| `deploy` | `actions/deploy-pages@v5` → publishes the artifact → URL = https://mojo-molotov.github.io/igoristan/                        |

## `concurrency: pages` + `cancel-in-progress: false`

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: false
```

Prevents **two simultaneous deployments** (race condition).  
The second waits (`cancel-in-progress: false` → we _don't_ cancel the running one).

## `pnpm install --frozen-lockfile`

```yaml
- name: Install dependencies
  run: pnpm install --frozen-lockfile
```

`--frozen-lockfile`:

- Reads `pnpm-lock.yaml` exactly.
- Refuses to touch the lock (even if a dep has a compatible newer version).
- Fails if a dependency is missing from the lock.

→ Determinism. CI installs **exactly** what was tested locally.

## No `lint` / `typecheck` in `deploy.yml`

Deliberate: `wireit build` _depends_ on `prebuild` which depends on `lint + typecheck`.  
They fail → `build` fails.

So `pnpm build` _includes_ lint + typecheck.  
No need to repeat them in the YAML.

## No tests in `deploy.yml`

Igoristan _has no unit tests_.

- It's a **demo app**, not a lib.
- Random behaviors (10%, 30%, 20%) are _deliberate_.
- The behaviors are **tested e2e** by `ocarina-example`.

Igoristan _is_ the SUT, so the tests live elsewhere.

## `defaults.run.shell: bash`

```yaml
defaults:
  run:
    shell: bash
```

→ Every `run: ...` step uses `bash`.

## No OS matrix

Igoristan only compiles on ubuntu-latest. No Windows / macOS. The bundle is static JS&nbsp;—&nbsp;the build OS barely matters.

Compare with `ocarina` (see [`../10-cicd/02-ocarina-workflows.md`](../10-cicd/02-ocarina-workflows.md)), which tests on ubuntu+windows to verify Python portability (filesystem path handling among other things).
