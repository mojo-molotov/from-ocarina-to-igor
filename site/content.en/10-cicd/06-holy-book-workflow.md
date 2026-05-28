---
title: "10.06 — ocarina-holy-book workflow"
description: "The Holy Book's single workflow, deploy.yml: on push to main, build VitePress then publish to GitHub Pages."
weight: 6
date: 2026-05-20
series: ["ci-cd"]
series_order: 6
---

# 10.06&nbsp;—&nbsp;`ocarina-holy-book` workflow

> A single workflow: `deploy.yml`. On push main → VitePress build → upload Pages.

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

## Analysis

### 1. `TZ: Europe/Paris`

```yaml
env:
  TZ: Europe/Paris
```

Forces the runner timezone to Europe/Paris. Dates rendered by VitePress ("_Last update: 05/18/2026 11h42_") are in Paris time, not UTC. Leaving it in UTC would cause mysterious date bugs.

### 2. `fetch-depth: 0`

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 0
```

`fetch-depth: 0` = full git clone (vs depth 1 by default).

VitePress (via the `@sugarat/theme`) reads the **Git log** to compute each page's "_Last update_" date. Without full history: VitePress only sees the last commit, every page would have the same date.

### 3. `pnpm/action-setup` SHA-pinned

```yaml
- uses: pnpm/action-setup@fcf821c621167805dd63a29662bd7cb5676c81a8
```

_Version pinning_ by SHA is used everywhere for non-official actions (not prefixed with `actions/`) to mitigate Supply Chain Attack risks.

### 4. `--frozen-lockfile`

See [`05-igoristan-workflows.md`](05-igoristan-workflows.md)

### 5. `concurrency: pages, cancel-in-progress: false`

Prevents simultaneous deploys to GitHub Pages (race condition).

## Build

```bash
pnpm build
# = vitepress build docs
```

VitePress produces:

- Static HTML per route (EN + FR + RU).
- JS/CSS bundle.
- `pagefind/` search index.
- `llms.txt` + `llms-full.txt` (via the in-house plugin).
- PDFs served from `public/`.

Output: `docs/.vitepress/dist/`.

## Deployment

```yaml
- uses: actions/upload-pages-artifact@v4
  with:
    path: docs/.vitepress/dist
```

```yaml
- id: deployment
  uses: actions/deploy-pages@v5
```

## Final URL

https://mojo-molotov.github.io/ocarina-holy-book/

`/ocarina-holy-book` prefix configured in `config.mts#base`:

```typescript
const base =
  process.env.GITHUB_ACTIONS === "true" ? "/ocarina-holy-book/" : "/";
```

## PR _trigger_

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

`pull_request` is included. Every PR builds the site to verify nothing is broken, but doesn't deploy.

## No automated dynamic tests

The Holy Book has **no automated dynamic tests**. Tested manually.

## Cadences

| Trigger   | Frequency                      |
| --------- | ------------------------------ |
| Push main | On every commit merged to main |
| PR        | On every push to a PR          |
| Manual    | On demand                      |
