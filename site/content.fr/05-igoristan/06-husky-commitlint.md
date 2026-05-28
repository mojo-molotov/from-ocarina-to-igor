---
title: "05.06 — Husky + lint-staged + commitlint + commitizen"
description: "La discipline de commits de l'Igoristan : Husky, lint-staged, commitlint et commitizen pour des messages conventionnels et format-checkés."
weight: 6
date: 2026-05-20
series: ["igoristan"]
series_order: 6
---

# 05.06&nbsp;—&nbsp;Husky + lint-staged + commitlint + commitizen

> Discipline de commits stricte. Conventionnels, signés, format-checkés.

## Outils

| Outil                          | Rôle                                                       |
| ------------------------------ | ---------------------------------------------------------- |
| **Husky**                      | Installe les hooks Git locaux (`pre-commit`, `commit-msg`) |
| **lint-staged**                | Lance des outils _seulement_ sur les fichiers _staged_     |
| **commitlint**                 | Vérifie que le message de commit suit la convention        |
| **commitizen + cz-commitlint** | CLI interactive pour _composer_ un message conforme        |

## Config

### `.husky/`

Dossier contenant les hook scripts&nbsp;:

```
.husky/
├── pre-commit
└── commit-msg
```

`pre-commit`&nbsp;:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"
pnpm exec lint-staged
```

`commit-msg`&nbsp;:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"
pnpm exec commitlint --edit "$1"
```

### `.lintstagedrc.cjs`

```js
module.exports = {
  "*.{js,ts,jsx,tsx,json,md,mdx,html,css,scss,yml,yaml}": ["prettier --write"],
};
```

→ Sur chaque fichier _staged_&nbsp;: `prettier --write`. Si Prettier modifie, les modifications sont automatiquement rattachées au commit.

### `.commitlintrc.cjs`

```js
module.exports = { extends: ["@commitlint/config-conventional"] };
```

→ Hérite de `@commitlint/config-conventional`&nbsp;:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types acceptés&nbsp;: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

### `.czrc`

```
{ "path": "@commitlint/cz-commitlint" }
```

→ Indique à `commitizen` d'utiliser `@commitlint/cz-commitlint` comme adapter. La commande `pnpm commit` lance la CLI interactive.

## Chaîne de commit

```
1. Développeur : git add foo.tsx
   ↓
2. Développeur : pnpm commit
   ↓
3. commitizen (cz-commitlint) ouvre une CLI interactive :
      ? Select the type of change: feat
      ? What is the scope (optional): dashboard
      ? Write a short, imperative tense description: add OTP screen
      ? Provide a longer description: ...
      ? Are there any breaking changes? no
      ? Issues this commit closes: -
   ↓
4. Le message est validé localement contre la config conventional
   ↓
5. git-cz appelle `git commit` avec le message construit
   ↓
6. .husky/pre-commit s'exécute :
      lint-staged → prettier --write sur les fichiers staged
   ↓
7. .husky/commit-msg s'exécute :
      commitlint --edit COMMIT_EDITMSG
      → vérifie une dernière fois (au cas où l'utilisateur a fait git commit -m direct)
   ↓
8. Si tout passe : commit créé
```

## Pipeline alternatif&nbsp;: `git commit -m "..."`

Si le développeur **shortcut** via `git commit -m "fix some bug"` (sans utiliser `pnpm commit`)&nbsp;:

1. `pre-commit` lance `lint-staged` (prettier sur les staged).
2. `commit-msg` lance `commitlint --edit "$1"`.
   - «&nbsp;_fix: some bug_&nbsp;» serait OK. «&nbsp;_stuff_&nbsp;» serait rejeté.

Donc&nbsp;: on _peut_ shortcut, mais le commitlint impose la convention quand même.

## `is-ci || husky` dans `prepare`

```json
"scripts": {
  "prepare": "is-ci || husky"
}
```

→ Le script `prepare` est exécuté automatiquement par `pnpm install` (ou `npm install`).

1. Si on est en CI (`is-ci` retourne `true`), `||` court-circuite, husky n'est pas installé.
2. Si on est en local, `is-ci` retourne `false`, `husky` est installé (= les hooks `.husky/*` sont enregistrés dans `.git/hooks/*`).

## Discipline

| Bénéfice                                      | Détail                                                                                                |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Historique git lisible**                    | `git log --oneline` donne `feat(dashboard): add OTP screen`, exploitable par `gh release` (changelog) |
| **Pas de PR avec format cassé**               | Prettier auto-applique sur staged, on ne commit jamais du code non-formaté                            |
| **Plus de discussion sur le format en revue** | Le format est _décidé_ par Prettier, pas par la revue                                                 |

## Format vs contenu

Le pre-commit `lint-staged` applique Prettier mais **n'applique pas ESLint**.

- **Prettier** corrige le format _sans changer la sémantique_. Auto-safe.
- **ESLint** peut détecter des erreurs sémantiques (unused var, missing dep dans `useEffect`). Si on le lançait en pre-commit, il pourrait _bloquer_ le commit pour quelque chose qui mérite d'être discuté en revue.

→ Le lint est laissé pour la CI (`wireit lint`). Le format est immédiat.

## Pourquoi l'Igoristan a tout ça pour un projet «&nbsp;_démo_&nbsp;»

Pour avoir l'approbation de Napoléon.
