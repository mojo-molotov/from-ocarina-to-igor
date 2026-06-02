---
title: "00.02 — Matrice stack / responsabilité / licence"
description: "Matrice complète par dépôt : langage, version, stack principale, outillage, mode de distribution et licence pour les six projets."
weight: 2
date: 2026-05-20
series: ["big-picture"]
series_order: 2
tags: ["typage", "ci-cd"]
---

# 00.02&nbsp;—&nbsp;Matrice _stack /&nbsp;responsabilité /&nbsp;licence_

| Dépôt                     | Rôle                                                                                               | Langage    |  Version  | Stack principale                                                                                                                                                                     | Stack outillage                                                                                                                                                                                                                             | Distribution                                     | Licence  |
| ------------------------- | -------------------------------------------------------------------------------------------------- | ---------- | :-------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | :------: |
| `ocarina`                 | Framework de test e2e navigateur                                                                   | Python     | **3.14+** | `hatchling`, `python-docx` (seule dépendance d'exécution), `selenium` + `playwright` (dev seulement)                                                                                  | `ruff` (ALL), `mypy` strict, `pytest`, `hypothesis`, `pytest-mypy-plugins`, `syrupy`, `prysk` (cram), `allure-pytest`, `pre-commit`, `twine`, `build`                                                                                       | PyPI, v**1.1.9**                                 |   MIT    |
| `ocarina-example`         | Suite canonique e2e contre l'Igoristan                                                             | Python     | **3.14+** | `ocarina`, `selenium ≥ 4.40`, `python-dotenv`, `dogpile.cache`, `redis`                                                                                                              | `ruff`, `mypy`, `pre-commit`                                                                                                                                                                                                                | Source uniquement                                |   MIT    |
| `ocarina-with-ai-example` | Suite e2e CURA Healthcare co-écrite par Claude Code                                                | Python     | **3.14+** | `ocarina ≥ 1.0.3`, `selenium ≥ 4.40`                                                                                                                                                 | `ruff`, `mypy`, `mypy-extensions`, `typing-extensions`, `pre-commit`                                                                                                                                                                        | Source uniquement                                |   MIT    |
| `igoristan`               | SUT public, application web volontairement chaotique                                               | TypeScript | **6.0.x** | **React 19.2**, **Vike 0.4.258** (SSG), **Vite 7.3**, **TailwindCSS 4** (alpha), `valibot`, `react-hook-form`, `react-dropzone`, `usehooks-ts`, `throttleit`, `lucide-react`, `uuid` | `pnpm 11`, **Node 24**, **`wireit`** (orchestrateur), `eslint 9` (flat), `prettier 3.5`, `husky`, `lint-staged`, `commitlint`, `commitizen`, `terser`, `rollup-plugin-visualizer`, `vite-plugin-compression`, `@qalisa/vike-plugin-sitemap` | GitHub Pages (`/igoristan/`)                     | _aucune_ |
| `tests-workers`           | Backend OTP /&nbsp;Corsicadex pour exercer la **parallélisation** et les **tests avec appels API** | TypeScript | **5.9.3** | **Vercel Edge Functions** (`runtime: "edge"`), `@upstash/redis`, `otplib`, types `next` (`NextRequest`)                                                                              | `pnpm 11.x`, `@vercel/node` (types)                                                                                                                                                                                                         | Vercel&nbsp;: `https://tests-workers.vercel.app` |   ISC    |
| `ocarina-holy-book`       | Documentation publique + skills IA + PDF                                                           | TypeScript | **6.0.x** | **VitePress 2 alpha**, theme `@sugarat/theme`, `vue 3.5`, `pagefind`, `vitepress-plugin-image-optimize`                                                                              | `pnpm 11`, Node 24, `eslint 9`, `prettier 3.8`, `husky`, `lint-staged`, `commitlint`, `sass-embedded`                                                                                                                                       | GitHub Pages (`/ocarina-holy-book/`)             |   MIT    |

## Python early adopter

| Apport Python 3.12+                       | Utilisation dans Ocarina                                                                                                                                  |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PEP 695** (`class Foo[T]:`)             | Signature générique partout (`TestSuite[Driver]`, `Watcher[Driver]`, `Test[Driver]`, `Result[T]`, `Ok[T]`, `Thunk[T]`, etc.)                              |
| **PEP 695 type aliases** (`type X = ...`) | Tous les alias&nbsp;: `type Result[T] = Ok[T] \| Fail`, `type Effect = Callable[[], None]`, `type Thunk[T] = Callable[[], T]`, `type Mode = Literal[...]` |
| **`TypeGuard`** (Python 3.10+)            | `is_ok`, `is_fail`, `is_test_result_ok`, `is_test_result_fail`, `is_test_result_skipped`                                                                  |
| **`Self`** (3.11+)                        | Retours fluides des POMs, des loggers, des invariants                                                                                                     |
| **`@final`** (3.8+)                       | Verrouille les classes critiques (`Watcher`, `Test`, `TestCycle`, `ChainRunner`, `Ok`, `Fail`, …)                                                         |
| **`Unpack`** (3.11+)                      | Signature de `HumanizedDriver` côté `ocarina-example`                                                                                                     |
| **`Protocol`** (3.8+)                     | `ScreenshotDriver`, `SupportsWrite[str]`                                                                                                                  |
| **`Literal`** (3.8+)                      | Toutes les énumérations (`SeleniumCliStoreKeys`, `LOGGERS_CHOICES`, `Mode`)                                                                               |
| **`Never`** (3.11+)                       | Signature de `_SilentArgumentParser.error`                                                                                                                |

> **Conséquence pratique**&nbsp;: il existe un workflow CI dédié `unstable_python_full_build.yml` qui pousse Python **3.15-dev** mensuellement (`cron: "0 3 1 * *"`), parce qu'Ocarina veut être prêt pour le prochain interpréteur dès qu'il sort. Voir [`../10-cicd/02-ocarina-workflows.md`](../10-cicd/02-ocarina-workflows.md)

## Node, pnpm, navigateurs

| Composant        | Version utilisée                                                             | Où                                                                         |
| ---------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **Node**         | `^24.x`                                                                      | `igoristan/package.json#engines`, `ocarina-holy-book/package.json#engines` |
| **pnpm**         | `11.x` (Igoristan, Holy Book), `11.x` (tests-workers)                        | `package.json#engines`, `packageManager`                                   |
| **Firefox**      | dernière (via `browser-actions/setup-firefox`)                               | CI `ocarina-with-ai-example`                                               |
| **geckodriver**  | **0.35.0** (CI `ocarina-example`), **0.36.0** (CI `ocarina-with-ai-example`) | Téléchargement direct depuis GitHub Releases Mozilla                       |
| **chromedriver** | matché à la version Chrome ambient sur ubuntu-latest                         | Téléchargement depuis `storage.googleapis.com/chrome-for-testing-public`   |

## Pas de dépendances

Le fait qu'Ocarina **ne déclare qu'une seule dépendance d'exécution** (`python-docx`) est un choix.

- Tout le reste (Selenium, Redis, dotenv, dogpile…) appartient au **projet utilisateur**.
- Ni Selenium ni Playwright (ajouté en `1.1.3`) n'est une dépendance d'exécution d'Ocarina&nbsp;: les deux sont dans le _groupe `dev`_ (utilisés par les tests et les adapters livrés, pas par le cœur de la lib).
- Le seul plugin qui «&nbsp;_coûte_&nbsp;» une dépendance est `generate_docx_proof` (le seul à utiliser `python-docx`). Si ce plugin échoue à s'importer, le reste tourne.

Ce point est revendiqué dans le Holy Book&nbsp;:

> Les seules dépendances externes sont dans les plugins post-exécution et si l'une d'elles ne passe pas, elle se retire sans que le reste ne casse.

Voir [`../11-independence/02-auditability.md`](../11-independence/02-auditability.md) pour la portée de cette règle.
