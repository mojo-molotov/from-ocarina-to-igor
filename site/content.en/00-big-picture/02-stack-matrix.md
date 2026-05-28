---
title: "00.02 — Stack / responsibility / license matrix"
description: "A full per-repository matrix: language, version, main stack, tooling, distribution mode and license across the six projects."
weight: 2
date: 2026-05-20
series: ["big-picture"]
series_order: 2
tags: ["typing", "ci-cd"]
---

# 00.02&nbsp;—&nbsp;_Stack / responsibility / license_ matrix

| Repository                | Role                                                                                         | Language   |  Version  | Primary stack                                                                                                                                                                        | Tooling stack                                                                                                                                                                                                                              | Distribution                               | License |
| ------------------------- | -------------------------------------------------------------------------------------------- | ---------- | :-------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ | :-----: |
| `ocarina`                 | Browser e2e test framework                                                                   | Python     | **3.14+** | `hatchling`, `python-docx` (sole runtime dependency), `selenium` (dev only)                                                                                                          | `ruff` (ALL), `mypy` strict, `pytest`, `hypothesis`, `pytest-mypy-plugins`, `syrupy`, `prysk` (cram), `allure-pytest`, `pre-commit`, `twine`, `build`                                                                                      | PyPI, v**1.1.+**                           |   MIT   |
| `ocarina-example`         | Canonical e2e suite against the Igoristan                                                    | Python     | **3.14+** | `ocarina`, `selenium ≥ 4.40`, `python-dotenv`, `dogpile.cache`, `redis`                                                                                                              | `ruff`, `mypy`, `pre-commit`                                                                                                                                                                                                               | Source only                                |   MIT   |
| `ocarina-with-ai-example` | e2e suite against CURA Healthcare, co-written with Claude Code                               | Python     | **3.14+** | `ocarina ≥ 1.0.3`, `selenium ≥ 4.40`                                                                                                                                                 | `ruff`, `mypy`, `mypy-extensions`, `typing-extensions`, `pre-commit`                                                                                                                                                                       | Source only                                |   MIT   |
| `igoristan`               | Public SUT, deliberately chaotic web app                                                     | TypeScript | **6.0.x** | **React 19.2**, **Vike 0.4.258** (SSG), **Vite 7.3**, **TailwindCSS 4** (alpha), `valibot`, `react-hook-form`, `react-dropzone`, `usehooks-ts`, `throttleit`, `lucide-react`, `uuid` | `pnpm 11`, **Node 24**, **`wireit`** (orchestrator), `eslint 9` (flat), `prettier 3.5`, `husky`, `lint-staged`, `commitlint`, `commitizen`, `terser`, `rollup-plugin-visualizer`, `vite-plugin-compression`, `@qalisa/vike-plugin-sitemap` | GitHub Pages (`/igoristan/`)               | _none_  |
| `tests-workers`           | OTP / Corsicadex backend, the substrate that exercises **parallelization** and **API tests** | TypeScript | **5.9.3** | **Vercel Edge Functions** (`runtime: "edge"`), `@upstash/redis`, `otplib`, `next` types (`NextRequest`)                                                                              | `pnpm 11.x`, `@vercel/node` (types)                                                                                                                                                                                                        | Vercel: `https://tests-workers.vercel.app` |   ISC   |
| `ocarina-holy-book`       | Public documentation + AI skills + PDFs                                                      | TypeScript | **6.0.x** | **VitePress 2 alpha**, `@sugarat/theme`, `vue 3.5`, `pagefind`, `vitepress-plugin-image-optimize`                                                                                    | `pnpm 11`, Node 24, `eslint 9`, `prettier 3.8`, `husky`, `lint-staged`, `commitlint`, `sass-embedded`                                                                                                                                      | GitHub Pages (`/ocarina-holy-book/`)       |   MIT   |

## Python early adopter

| Python 3.12+ feature                      | Use in Ocarina                                                                                                                                   |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **PEP 695** (`class Foo[T]:`)             | Generic signatures everywhere (`TestSuite[Driver]`, `Watcher[Driver]`, `Test[Driver]`, `Result[T]`, `Ok[T]`, `Thunk[T]`, etc.)                   |
| **PEP 695 type aliases** (`type X = ...`) | Every alias: `type Result[T] = Ok[T] \| Fail`, `type Effect = Callable[[], None]`, `type Thunk[T] = Callable[[], T]`, `type Mode = Literal[...]` |
| **`TypeGuard`** (Python 3.10+)            | `is_ok`, `is_fail`, `is_test_result_ok`, `is_test_result_fail`, `is_test_result_skipped`                                                         |
| **`Self`** (3.11+)                        | Fluent returns from POMs, loggers, invariants                                                                                                    |
| **`@final`** (3.8+)                       | Locks critical classes (`Watcher`, `Test`, `TestCycle`, `ChainRunner`, `Ok`, `Fail`, …)                                                          |
| **`Unpack`** (3.11+)                      | `HumanizedDriver` signature in `ocarina-example`                                                                                                 |
| **`Protocol`** (3.8+)                     | `ScreenshotDriver`, `SupportsWrite[str]`                                                                                                         |
| **`Literal`** (3.8+)                      | All enums (`SeleniumCliStoreKeys`, `LOGGERS_CHOICES`, `Mode`)                                                                                    |
| **`Never`** (3.11+)                       | `_SilentArgumentParser.error` signature                                                                                                          |

> **Practical consequence**: there is a dedicated CI workflow `unstable_python_full_build.yml` that pushes Python **3.15-dev** monthly (`cron: "0 3 1 * *"`), because Ocarina aims to be ready for the next interpreter as soon as it ships. See [`../10-cicd/02-ocarina-workflows.md`](../10-cicd/02-ocarina-workflows.md)

## Node, pnpm, browsers

| Component        | Version used                                                                 | Where                                                                      |
| ---------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **Node**         | `^24.x`                                                                      | `igoristan/package.json#engines`, `ocarina-holy-book/package.json#engines` |
| **pnpm**         | `11.x` (Igoristan, Holy Book), `11.x` (tests-workers)                        | `package.json#engines`, `packageManager`                                   |
| **Firefox**      | latest (via `browser-actions/setup-firefox`)                                 | CI for `ocarina-with-ai-example`                                           |
| **geckodriver**  | **0.35.0** (CI `ocarina-example`), **0.36.0** (CI `ocarina-with-ai-example`) | Direct download from Mozilla's GitHub Releases                             |
| **chromedriver** | matched to the ambient Chrome version on `ubuntu-latest`                     | Downloaded from `storage.googleapis.com/chrome-for-testing-public`         |

## No dependencies

Ocarina **declares one runtime dependency** (`python-docx`). On purpose.

- Everything else (Selenium, Redis, dotenv, dogpile…) sits in the **user project**.
- Selenium isn't even a runtime dep of Ocarina. It's in the _dev_ group&nbsp;—&nbsp;used by the framework's tests, not by the library itself.
- The only plugin that "costs" a dependency is `generate_docx_proof` (the only one pulling `python-docx`). If that plugin fails to import, the rest keeps running.

Holy Book, chapter "What is Ocarina?":

> The only external dependencies live in the post-execution plugins and if one of them doesn't fit, it can be removed without breaking anything else.

See [`../11-independence/02-auditability.md`](../11-independence/02-auditability.md) for the scope of that rule.
