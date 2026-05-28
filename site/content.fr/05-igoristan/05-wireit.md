---
title: "05.05 — Pipelines wireit"
description: "Les pipelines wireit de l'Igoristan : enchaînement de format-check, lint, typecheck, build et dev avec un cache incrémental fin par tâche."
weight: 5
date: 2026-05-20
series: ["igoristan"]
series_order: 5
---

# 05.05&nbsp;—&nbsp;Pipelines `wireit`

> `wireit` est un orchestrateur de scripts NPM avec cache incrémental. L'Igoristan l'utilise pour _enchaîner_ `format-check`, `lint`, `typecheck`, `prebuild`, `build`, `dev`, `preview`, le tout avec un cache fin par tâche.

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

Avec `pnpm dev`&nbsp;:

1. Vérifier que `lint` est à jour (cache `--cache` d'ESLint).
2. Vérifier que `typecheck` est à jour (cache de `tsc --build`).
3. Vérifier que `prebuild` est à jour (sentinelle, pas de commande, juste un goal).
4. Lancer `vike dev`.

Si rien n'a changé&nbsp;: tout est skippé, le serveur démarre directement.

## Sémantique `wireit`

### `command`

La commande shell à exécuter.

### `files`

La liste des fichiers (glob) à _hasher_ pour décider si la tâche est à réexécuter. Si les hashes sont identiques au run précédent et que l'output existe, la tâche est skippée.

### `output`

La liste des fichiers/dossiers produits. `[]` = aucune sortie. Pour `lint`, `output` est `[]` parce qu'`eslint --cache` gère son cache _en interne_.

### `dependencies`

Liste de tâches préalables. `wireit` exécute la dépendance _et_ son retour conditionne le hash.

### `packageLocks`

Liste de lockfiles à hasher. `pnpm-lock.yaml` ici. Conséquence&nbsp;: `pnpm install` change le lockfile&nbsp;→&nbsp;re-trigger `dev` /&nbsp;`build`.

## Cache `--cache` d'ESLint

```
"lint": {
  "command": "eslint \"./{src,packages}/**/*.{js,jsx,ts,tsx}\" --max-warnings 0 --cache",
  ...
}
```

`--cache` d'ESLint&nbsp;: conserve un cache `.eslintcache` à la racine. Au prochain lancement, seuls les fichiers modifiés sont relinted. Premiers runs lents, suivants instantanés.

`--max-warnings 0`&nbsp;: un warning = erreur.

## Cache `--build` de TypeScript

```
"typecheck": {
  "command": "tsc --build --pretty tsconfig.json",
  "files": [...],
  "output": ["typecheck-dist/"]
}
```

`tsc --build`&nbsp;: mode _projects_ de TypeScript. Conserve un `.tsbuildinfo` en sortie. Cache incremental, ré-utilise les infos précédentes.

Le `--pretty` formate joliment les erreurs en couleur.

## `prebuild`

```json
"prebuild": {
  "files": [...],
  "dependencies": ["lint", "typecheck"]
}
```

Pas de `command`. Juste un _goal_ qui dépend de `lint + typecheck`. Si l'un des deux fail, `prebuild` fail. Si les deux passent, `prebuild` passe (et son hash est cached).

Cela permet à `dev` et `build` de _ne dépendre que de `prebuild`_, et donc d'hériter implicitement de la quality gate (lint + typecheck).

## `WIREIT_CACHE: github` en CI

`.github/workflows/ci-pr.yml`&nbsp;:

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

`WIREIT_CACHE: github` + l'action `google/wireit@setup-github-actions-caching/v2` activent un cache _persistant CI_ via le GitHub Actions cache. Les CI suivantes sur les mêmes fichiers source ne relancent pas inutilement les jobs déjà faits.

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

1. **`"build": "wireit"`**&nbsp;: la commande _est_ `wireit` lui-même. C'est `wireit` qui détecte qu'on l'a invoqué depuis le script `build` et qui lit la config `wireit.build`.
2. **`"prepare": "is-ci || husky"`**&nbsp;: exécuté après `pnpm install`. Si on est _hors_ CI (`is-ci` retourne false), on installe les hooks `husky` localement.
3. **`"format"` n'est PAS dans wireit**&nbsp;: `prettier --write` n'a pas besoin de cache.
