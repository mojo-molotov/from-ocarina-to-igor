---
title: "05.06 — Husky + lint-staged + commitlint + commitizen"
description: "Strict commit discipline. Conventional, signed, format-checked."
weight: 6
date: 2026-05-20
series: ["igoristan"]
series_order: 6
---

# 05.06&nbsp;—&nbsp;Husky + lint-staged + commitlint + commitizen

> Strict commit discipline. Conventional, signed, format-checked.

## Tools

| Tool                           | Role                                                  |
| ------------------------------ | ----------------------------------------------------- |
| **Husky**                      | Installs local Git hooks (`pre-commit`, `commit-msg`) |
| **lint-staged**                | Runs tools _only_ on _staged_ files                   |
| **commitlint**                 | Verifies the commit message follows the convention    |
| **commitizen + cz-commitlint** | Interactive CLI to _compose_ a compliant message      |

## Config

### `.husky/`

Folder containing the hook scripts:

```
.husky/
├── pre-commit
└── commit-msg
```

`pre-commit`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"
pnpm exec lint-staged
```

`commit-msg`:

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

→ On each _staged_ file: `prettier --write`. If Prettier modifies anything, the changes get auto-restaged into the commit.

### `.commitlintrc.cjs`

```js
module.exports = { extends: ["@commitlint/config-conventional"] };
```

→ Inherits from `@commitlint/config-conventional`:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Accepted types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

### `.czrc`

```
{ "path": "@commitlint/cz-commitlint" }
```

→ Tells `commitizen` to use `@commitlint/cz-commitlint` as the adapter. `pnpm commit` fires the interactive CLI.

## Commit chain

```
1. Developer: git add foo.tsx
   ↓
2. Developer: pnpm commit
   ↓
3. commitizen (cz-commitlint) opens an interactive CLI:
      ? Select the type of change: feat
      ? What is the scope (optional): dashboard
      ? Write a short, imperative tense description: add OTP screen
      ? Provide a longer description: ...
      ? Are there any breaking changes? no
      ? Issues this commit closes: -
   ↓
4. The message is validated locally against the conventional config
   ↓
5. git-cz calls `git commit` with the built message
   ↓
6. .husky/pre-commit runs:
      lint-staged → prettier --write on staged files
   ↓
7. .husky/commit-msg runs:
      commitlint --edit COMMIT_EDITMSG
      → verifies one last time (in case the user did git commit -m directly)
   ↓
8. If everything passes: commit created
```

## Alternate pipeline: `git commit -m "..."`

Developer **shortcuts** via `git commit -m "fix some bug"` (without `pnpm commit`):

1. `pre-commit` runs `lint-staged` (prettier on staged files).
2. `commit-msg` runs `commitlint --edit "$1"`.
   - "_fix: some bug_" passes. "_stuff_" gets rejected.

So you _can_ shortcut, but commitlint enforces the convention anyway.

## `is-ci || husky` in `prepare`

```json
"scripts": {
  "prepare": "is-ci || husky"
}
```

→ The `prepare` script runs automatically on `pnpm install` (or `npm install`).

1. CI (`is-ci` returns `true`) → `||` short-circuits, husky isn't installed.
2. Local (`is-ci` returns `false`) → `husky` is installed (the `.husky/*` hooks get registered in `.git/hooks/*`).

## Discipline

| Benefit                                  | Detail                                                                                          |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Readable git history**                 | `git log --oneline` gives `feat(dashboard): add OTP screen`, usable by `gh release` (changelog) |
| **No PR with broken format**             | Prettier auto-applies on staged, we never commit unformatted code                               |
| **No more formatting debates in review** | Format is _decided_ by Prettier, not by review                                                  |

## Format vs content

The pre-commit `lint-staged` applies Prettier but **does not apply ESLint**.

- **Prettier** fixes the format _without changing semantics_. Auto-safe.
- **ESLint** can catch semantic errors (unused var, missing dep in `useEffect`). Running it pre-commit could _block_ a commit over something worth discussing in review.

→ Linting goes to CI (`wireit lint`). Formatting stays immediate.

## Why does Igoristan have all this for a "_demo_" project

To earn Napoleon's approval.
