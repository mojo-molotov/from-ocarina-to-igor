---
title: "05.05 — wireit pipelines"
description: "The Igoristan's wireit pipelines: chaining format-check, lint, typecheck, build and dev with fine-grained incremental per-task caching."
weight: 5
date: 2026-05-20
series: ["igoristan"]
series_order: 5
---

# 05.05&nbsp;—&nbsp;`wireit` pipelines

> `wireit` is an NPM script orchestrator with incremental cache. Igoristan uses it to _chain_ `format-check`, `lint`, `typecheck`, `prebuild`, `build`, `dev`, `preview`, all with fine per-task caching.

## `package.json#wireit`

```json
"wireit": {
  "ci:format-check": {
    "command": "prettier . --check",
    "files": ["*.{js,ts,jsx,tsx,json,md,mdx,html,css,scss,yml,yaml}"],
    "output": []
  },
  "clean:dist": {
    "command": "rimraf dist",
    "files": ["dist/"],
    "output": []
  },
  "prebuild": {
    "files": ["src/**/*.*", "package.json", "packages/**/*.*", "packages/**/package.json", "vite.config.ts"],
    "dependencies": ["lint", "typecheck"]
  },
  "preview": {
    "command": "vike preview",
    "dependencies": ["build"]
  },
  "dev": {
    "command": "vike dev",
    "files": ["src/**/*.*", "packages/**/*.*"],
    "dependencies": ["prebuild"],
    "output": ["dist/"],
    "packageLocks": ["pnpm-lock.yaml"]
  },
  "build": {
    "command": "vike build",
    "files": ["src/**/*.*", "packages/**/*.*"],
    "dependencies": ["prebuild"],
    "output": ["dist/"],
    "packageLocks": ["pnpm-lock.yaml"]
  },
  "lint": {
    "command": "eslint \"./{src,packages}/**/*.{js,jsx,ts,tsx}\" --max-warnings 0 --cache",
    "files": ["src/**/*.*", "package.json", "packages/**/*.*", "eslint.config.ts"],
    "output": []
  },
  "typecheck": {
    "command": "tsc --build --pretty tsconfig.json",
    "files": ["src/**/*.*", "package.json", "tsconfig.app.json", "tsconfig.json", "tsconfig.node.json"],
    "output": ["typecheck-dist/"]
  }
}
```

## DAG

```
                 ┌─────────────────┐
                 │ ci:format-check │ ────► prettier . --check
                 └─────────────────┘
                 ┌─────────────────┐
                 │     lint        │ ────► eslint (max-warnings 0, --cache)
                 └─────┬───────────┘
                       │
                 ┌─────▼───────────┐
                 │   typecheck     │ ────► tsc --build --pretty
                 └─────┬───────────┘
                       │
                 ┌─────▼───────────┐
                 │   prebuild      │ ────► deps: [lint, typecheck]
                 └─────┬───────────┘
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
   ┌─────────────────┐    ┌─────────────────┐
   │   build         │    │   dev           │
   │   vike build    │    │   vike dev      │
   └────┬────────────┘    └─────────────────┘
        ▼
   ┌─────────────────┐
   │   preview       │
   │   vike preview  │
   └─────────────────┘
```

With `pnpm dev`:

1. Verify that `lint` is up to date (ESLint `--cache`).
2. Verify that `typecheck` is up to date (`tsc --build` cache).
3. Verify that `prebuild` is up to date (sentinel, no command, just a goal).
4. Launch `vike dev`.

Nothing changed → everything is skipped, the server starts immediately.

## `wireit` semantics

### `command`

The shell command to run.

### `files`

Glob list of files to _hash_ to decide whether the task needs re-running. Hashes match the previous run and output exists → task skipped.

### `output`

The list of files/folders produced. `[]` = no output. For `lint`, `output` is `[]` because `eslint --cache` handles its cache _internally_.

### `dependencies`

Prerequisite tasks. `wireit` runs the dependency _and_ its outcome feeds the hash.

### `packageLocks`

List of lockfiles to hash. `pnpm-lock.yaml` here. Consequence: `pnpm install` changes the lockfile → re-triggers `dev` / `build`.

## ESLint `--cache`

```
"lint": {
  "command": "eslint \"./{src,packages}/**/*.{js,jsx,ts,tsx}\" --max-warnings 0 --cache",
  ...
}
```

ESLint `--cache`: keeps a `.eslintcache` at the root. On the next run, only changed files get re-linted. First runs slow, later ones instant.

`--max-warnings 0`: warning = error.

## TypeScript `--build` cache

```
"typecheck": {
  "command": "tsc --build --pretty tsconfig.json",
  "files": [...],
  "output": ["typecheck-dist/"]
}
```

`tsc --build`: TypeScript's _projects_ mode. Keeps a `.tsbuildinfo` output. Incremental cache, reuses previous info.

`--pretty`: formats errors nicely in color.

## `prebuild`

```json
"prebuild": {
  "files": [...],
  "dependencies": ["lint", "typecheck"]
}
```

No `command`. Just a _goal_ depending on `lint + typecheck`. Either fails → `prebuild` fails. Both pass → `prebuild` passes (hash cached).

Lets `dev` and `build` _depend only on `prebuild`_, inheriting the quality gate (lint + typecheck) implicitly.

## `WIREIT_CACHE: github` in CI

`.github/workflows/ci-pr.yml`:

```yaml
env:
  WIREIT_CACHE: github
steps:
  - uses: actions/checkout@v6
  - uses: pnpm/action-setup@v5
  - uses: actions/setup-node@v6
  - uses: google/wireit@setup-github-actions-caching/v2
  - name: Install project
    run: make install
  - name: Formatcheck
    run: make ci:format-check
```

`WIREIT_CACHE: github` + the `google/wireit@setup-github-actions-caching/v2` action enable a _persistent CI_ cache via the GitHub Actions cache. Subsequent CIs on the same source files don't pointlessly re-run already-done jobs.

## `package.json#scripts`

```json
"scripts": {
  "wipe-wireit": "make wipe-wireit",
  "build": "wireit",
  "preview": "wireit",
  "dev": "wireit",
  "lint": "wireit",
  "typecheck": "wireit",
  "clean:dist": "wireit",
  "format": "prettier --log-level warn --write .",
  "commit": "git-cz",
  "ci:format-check": "wireit",
  "prepare": "is-ci || husky"
}
```

1. **`"build": "wireit"`**: the command _is_ `wireit` itself. `wireit` detects it was invoked from the `build` script and reads `wireit.build`.
2. **`"prepare": "is-ci || husky"`**: runs after `pnpm install`. _Outside_ CI (`is-ci` returns false) → install the `husky` hooks locally.
3. **`"format"` is NOT in wireit**: `prettier --write` doesn't need a cache.
