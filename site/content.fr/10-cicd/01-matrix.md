---
title: "10.01 — Matrice récapitulative des workflows"
description: "Vue d'ensemble synthétique de tous les workflows de l'écosystème."
weight: 1
date: 2026-05-20
series: ["ci-cd"]
series_order: 1
---

# 10.01&nbsp;—&nbsp;Matrice récapitulative des workflows

> Vue d'ensemble synthétique de tous les workflows de l'écosystème.

## Récap.

| Dépôt                     | Workflow                         | Trigger                                     | OS                                                                                                  | Stack                                                          | Effet                                                                              | Détail                                                     |
| ------------------------- | -------------------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `ocarina`                 | `main_ci.yml`                    | push/PR main, dispatch                      | ubuntu&nbsp;+&nbsp;windows&nbsp;×&nbsp;py&nbsp;3.14 (option 3.15-dev)                               | venv cache, make install-on-ci                                 | make check-coding-style +&nbsp;make test +&nbsp;Allure history +&nbsp;Pages deploy | [`02-ocarina-workflows.md`](02-ocarina-workflows.md)       |
| `ocarina`                 | `dev_ci.yml`                     | push dev/feature/fix, PR&nbsp;dev, dispatch | ubuntu&nbsp;×&nbsp;py&nbsp;3.14                                                                     | venv cache                                                     | check-coding-style + test                                                          | [`02-ocarina-workflows.md`](02-ocarina-workflows.md)       |
| `ocarina`                 | `unstable_python_full_build.yml` | cron&nbsp;(mensuel), dispatch               | ubuntu&nbsp;+&nbsp;windows&nbsp;×&nbsp;py&nbsp;**3.15-dev**                                         | `PIP_ONLY_BINARY=":all:"`                                      | full build sur Python pré-release                                                  | [`02-ocarina-workflows.md`](02-ocarina-workflows.md)       |
| `ocarina-example`         | `main_ci.yml`                    | push/PR main, dispatch                      | ubuntu&nbsp;+&nbsp;windows&nbsp;×&nbsp;py&nbsp;3.14                                                 | venv cache                                                     | check-coding-style                                                                 | [`03-example-workflows.md`](03-example-workflows.md)       |
| `ocarina-example`         | `dev_ci.yml`                     | push dev, dispatch                          | ubuntu&nbsp;×&nbsp;py&nbsp;3.14                                                                     | venv cache                                                     | check-coding-style                                                                 | [`03-example-workflows.md`](03-example-workflows.md)       |
| `ocarina-example`         | `e2e.yml`                        | dispatch (env&nbsp;`OC`)                    | ubuntu&nbsp;+&nbsp;service&nbsp;`redis:8.x`&nbsp;+&nbsp;Firefox&nbsp;+&nbsp;geckodriver&nbsp;0.35.0 | venv cache                                                     | run complet, upload traces                                                         | [`03-example-workflows.md`](03-example-workflows.md)       |
| `ocarina-with-ai-example` | `ai_proof_ci.yml`                | push main, PR, dispatch                     | ubuntu&nbsp;×&nbsp;py&nbsp;3.14                                                                     | venv cache                                                     | ruff&nbsp;format&nbsp;check +&nbsp;ruff&nbsp;check +&nbsp;mypy                     | [`04-ai-workflows.md`](04-ai-workflows.md)                 |
| `ocarina-with-ai-example` | `ai_proof_e2e.yml`               | dispatch                                    | ubuntu&nbsp;×&nbsp;**matrice&nbsp;firefox+chrome**                                                  | venv cache, geckodriver 0.36.0 /&nbsp;chromedriver auto-matché | warm-up Heroku&nbsp;dyno, run, filtrage sed des stacktraces ChromeDriver, upload   | [`04-ai-workflows.md`](04-ai-workflows.md)                 |
| `igoristan`               | `ci-pr.yml`                      | PR `**`, dispatch                           | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm 11                                                 | wireit                                                         | format&nbsp;check&nbsp;+&nbsp;lint&nbsp;+&nbsp;typecheck&nbsp;(parallélisés)       | [`05-igoristan-workflows.md`](05-igoristan-workflows.md)   |
| `igoristan`               | `deploy.yml`                     | push main, dispatch                         | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm 11                                                 | concurrency group `pages`                                      | `pnpm install --frozen-lockfile` +&nbsp;`pnpm build` +&nbsp;upload&nbsp;Pages      | [`05-igoristan-workflows.md`](05-igoristan-workflows.md)   |
| `ocarina-holy-book`       | `deploy.yml`                     | push main, PR, dispatch                     | ubuntu&nbsp;×&nbsp;node&nbsp;24&nbsp;+&nbsp;pnpm 11                                                 | `TZ=Europe/Paris`, concurrency group `pages`                   | `pnpm install` +&nbsp;`pnpm build` +&nbsp;upload&nbsp;Pages                        | [`06-holy-book-workflow.md`](06-holy-book-workflow.md)     |
| `tests-workers`           | _aucun_                          | &nbsp;—&nbsp;                               | &nbsp;—&nbsp;                                                                                       | Vercel                                                         | `vercel deploy`                                                                    | [`07-tests-workers-vercel.md`](07-tests-workers-vercel.md) |

## Action composite

| Action           | Localisation                                        | Usage                                                                                    |
| ---------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `allure-history` | `ocarina/.github/actions/allure-history/action.yml` | Composite&nbsp;: Bun +&nbsp;Allure 2.41.0 +&nbsp;restore/save history sur branche dédiée |

## Patterns

### Workflows PR (légers, auto)

```
ocarina/main_ci.yml                                       # python 3.14
ocarina/dev_ci.yml
ocarina-example/main_ci.yml
ocarina-example/dev_ci.yml
ocarina-with-ai-example/ai_proof_ci.yml
igoristan/ci-pr.yml
```

Tous tournent rapidement.

### Workflows _e2e_ (gourmands, manuels)

```
ocarina-example/e2e.yml                                   # Redis + Firefox
ocarina-with-ai-example/ai_proof_e2e.yml                  # Firefox + Chrome (matrice)
```

Manuels (`workflow_dispatch`). Démarrent service Redis ou warm-up Heroku. Téléchargent les drivers. Lancent les navigateurs web. Uploadent traces.

### Workflows _deploy_ (production)

```
igoristan/deploy.yml                                      # Pages
ocarina-holy-book/deploy.yml                              # Pages
```

Sur push main&nbsp;→&nbsp;GitHub Pages.

### Workflows mensuels

```
ocarina/unstable_python_full_build.yml                    # 1er du mois, 03:00 UTC
```

Cron mensuel sur Python&nbsp;3.15-dev. Garde Ocarina prêt pour la prochaine release Python.

## Release process manuel

Aucun workflow ne fait `twine upload` (PyPI) automatiquement.  
`ocarina/pyproject.toml#dependency-groups.dev` contient `twine>=6.2.0` mais le _release process_ est encore manuel et fait par l'auteur.

| Publishing auto                                   | Publishing manuel |
| ------------------------------------------------- | ----------------- |
| Risque de release accidentel                      | Contrôle          |
| Risque de release de breaking changes sans review | Review possible   |
| Quota PyPI                                        | Plus paisible     |
| Surveiller ses tokens (risque de vol de token)    | Tokens éphémères  |
