---
title: "10.01 — Workflow summary matrix"
description: "Synthetic overview of every ecosystem workflow."
weight: 1
date: 2026-05-20
series: ["ci-cd"]
series_order: 1
---

# 10.01&nbsp;—&nbsp;Workflow summary matrix

> Synthetic overview of every ecosystem workflow.

## Recap

| Repo                      | Workflow                         | Trigger                                | OS                                                                                        | Stack                                                                | Effect                                                                | Detail                                                     |
| ------------------------- | -------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------- |
| `ocarina`                 | `main_ci.yml`                    | push/PR main, dispatch                 | ubuntu&nbsp;+&nbsp;windows&nbsp;×&nbsp;py&nbsp;3.14 (option 3.15-dev)                     | venv cache, make install-on-ci                                       | make check-coding-style + make test + Allure history + Pages deploy   | [`02-ocarina-workflows.md`](02-ocarina-workflows.md)       |
| `ocarina`                 | `dev_ci.yml`                     | push dev/feature/fix, PR dev, dispatch | ubuntu&nbsp;×&nbsp;py&nbsp;3.14                                                           | venv cache                                                           | check-coding-style + test                                             | [`02-ocarina-workflows.md`](02-ocarina-workflows.md)       |
| `ocarina`                 | `unstable_python_full_build.yml` | cron (monthly), dispatch               | ubuntu&nbsp;+&nbsp;windows&nbsp;×&nbsp;py&nbsp;**3.15-dev**                               | `PIP_ONLY_BINARY=":all:"`                                            | full build on pre-release Python                                      | [`02-ocarina-workflows.md`](02-ocarina-workflows.md)       |
| `ocarina-example`         | `main_ci.yml`                    | push/PR main, dispatch                 | ubuntu&nbsp;+&nbsp;windows&nbsp;×&nbsp;py&nbsp;3.14                                       | venv cache                                                           | check-coding-style                                                    | [`03-example-workflows.md`](03-example-workflows.md)       |
| `ocarina-example`         | `dev_ci.yml`                     | push dev, dispatch                     | ubuntu&nbsp;×&nbsp;py&nbsp;3.14                                                           | venv cache                                                           | check-coding-style                                                    | [`03-example-workflows.md`](03-example-workflows.md)       |
| `ocarina-example`         | `e2e.yml`                        | dispatch (env `OC`)                    | ubuntu&nbsp;+&nbsp;service `redis:8.x`&nbsp;+&nbsp;Firefox&nbsp;+&nbsp;geckodriver 0.35.0 | venv cache                                                           | full run, upload traces                                               | [`03-example-workflows.md`](03-example-workflows.md)       |
| `ocarina-with-ai-example` | `ai_proof_ci.yml`                | push main, PR, dispatch                | ubuntu&nbsp;×&nbsp;py&nbsp;3.14                                                           | venv cache                                                           | ruff format check + ruff check + mypy                                 | [`04-ai-workflows.md`](04-ai-workflows.md)                 |
| `ocarina-with-ai-example` | `ai_proof_e2e.yml`               | dispatch                               | ubuntu&nbsp;×&nbsp;**firefox+chrome matrix**                                              | venv cache, geckodriver 0.36.0&nbsp;/&nbsp;auto-matched chromedriver | Heroku dyno warm-up, run, sed-filter ChromeDriver stacktraces, upload | [`04-ai-workflows.md`](04-ai-workflows.md)                 |
| `igoristan`               | `ci-pr.yml`                      | PR `**`, dispatch                      | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm 11                                       | wireit                                                               | format check + lint + typecheck (parallelized)                        | [`05-igoristan-workflows.md`](05-igoristan-workflows.md)   |
| `igoristan`               | `deploy.yml`                     | push main, dispatch                    | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm 11                                       | concurrency group `pages`                                            | `pnpm install --frozen-lockfile` + `pnpm build` + upload Pages        | [`05-igoristan-workflows.md`](05-igoristan-workflows.md)   |
| `ocarina-holy-book`       | `deploy.yml`                     | push main, PR, dispatch                | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm 11                                       | `TZ=Europe/Paris`, concurrency group `pages`                         | `pnpm install` + `pnpm build` + upload Pages                          | [`06-holy-book-workflow.md`](06-holy-book-workflow.md)     |
| `tests-workers`           | _none_                           | &nbsp;—&nbsp;                          | &nbsp;—&nbsp;                                                                             | Vercel                                                               | `vercel deploy`                                                       | [`07-tests-workers-vercel.md`](07-tests-workers-vercel.md) |

## Composite action

| Action           | Location                                            | Use                                                                         |
| ---------------- | --------------------------------------------------- | --------------------------------------------------------------------------- |
| `allure-history` | `ocarina/.github/actions/allure-history/action.yml` | Composite: Bun + Allure 2.41.0 + restore/save history on a dedicated branch |

## Patterns

### PR workflows (light, auto)

```
ocarina/main_ci.yml                                       # python 3.14
ocarina/dev_ci.yml
ocarina-example/main_ci.yml
ocarina-example/dev_ci.yml
ocarina-with-ai-example/ai_proof_ci.yml
igoristan/ci-pr.yml
```

All run fast.

### _e2e_ workflows (heavy, manual)

```
ocarina-example/e2e.yml                                   # Redis + Firefox
ocarina-with-ai-example/ai_proof_e2e.yml                  # Firefox + Chrome (matrix)
```

Manual (`workflow_dispatch`). Spin up a Redis service or warm up Heroku. Download drivers. Launch browsers. Upload traces.

### _deploy_ workflows (production)

```
igoristan/deploy.yml                                      # Pages
ocarina-holy-book/deploy.yml                              # Pages
```

On push to main, deploys to GitHub Pages.

### Monthly workflows

```
ocarina/unstable_python_full_build.yml                    # 1st of month, 03:00 UTC
```

Monthly cron on Python 3.15-dev. Keeps Ocarina ready for the next Python release.

## Manual release process

No workflow runs `twine upload` (PyPI) automatically. `ocarina/pyproject.toml#dependency-groups.dev` includes `twine>=6.2.0`, but the release process is manual.

| Auto publishing                                   | Manual publishing |
| ------------------------------------------------- | ----------------- |
| Risk of accidental release                        | Control           |
| Risk of releasing breaking changes without review | Review possible   |
| PyPI quota                                        | More peaceful     |
| Token monitoring (theft risk)                     | Ephemeral tokens  |
