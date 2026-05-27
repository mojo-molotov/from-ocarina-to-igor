---
title: "Chapter 10 — CI/CD across the whole ecosystem"
description: "Summary table of every CI workflow in the ecosystem."
weight: 11
date: 2026-05-20
tags: ["ci-cd"]
sidebar:
  open: true
---

# Chapter 10&nbsp;—&nbsp;CI/CD across the whole ecosystem

> Summary table of every CI workflow in the ecosystem.

## Outline

|  #  | File                                                       | Topic                                                                    |
| :-: | ---------------------------------------------------------- | ------------------------------------------------------------------------ |
| 01  | [`01-matrix.md`](01-matrix.md)                             | Summary table of every workflow.                                         |
| 02  | [`02-ocarina-workflows.md`](02-ocarina-workflows.md)       | `ocarina`: `main_ci.yml`, `dev_ci.yml`, `unstable_python_full_build.yml` |
| 03  | [`03-example-workflows.md`](03-example-workflows.md)       | `ocarina-example`: `main_ci.yml`, `dev_ci.yml`, `e2e.yml`                |
| 04  | [`04-ai-workflows.md`](04-ai-workflows.md)                 | `ocarina-with-ai-example`: `ai_proof_ci.yml`, `ai_proof_e2e.yml`         |
| 05  | [`05-igoristan-workflows.md`](05-igoristan-workflows.md)   | `igoristan`: `ci-pr.yml`, `deploy.yml`                                   |
| 06  | [`06-holy-book-workflow.md`](06-holy-book-workflow.md)     | `ocarina-holy-book`: `deploy.yml`                                        |
| 07  | [`07-tests-workers-vercel.md`](07-tests-workers-vercel.md) | `tests-workers`: no GitHub CI, deployment handled directly by Vercel.    |

## Overview

| Repo                      | Workflows                                     | Total |
| ------------------------- | --------------------------------------------- | ----: |
| `ocarina`                 | main_ci + dev_ci + unstable_python_full_build |     3 |
| `ocarina-example`         | main_ci + dev_ci + e2e                        |     3 |
| `ocarina-with-ai-example` | ai_proof_ci + ai_proof_e2e                    |     2 |
| `igoristan`               | ci-pr + deploy                                |     2 |
| `ocarina-holy-book`       | deploy                                        |     1 |
| `tests-workers`           | _none_ (delegated to Vercel)                  |     0 |

\+ `ocarina/.github/actions/allure-history/action.yml`.

## Cross-cutting discipline

| Convention                             | Benefit                                                                                                                                                                                                    |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`workflow_dispatch` always present** | Every workflow can be launched manually                                                                                                                                                                    |
| **`.venv` / `node_modules` cache**     | Every workflow caches the venv or node deps                                                                                                                                                                |
| **"matrix" strategy**                  | Duplicated workflows parallelized to test compatibility across multiple OSes and browsers: `ocarina` (ubuntu+windows). The others: ubuntu only (enough). `ocarina-with-ai-example`: Firefox+Chrome matrix. |
| **`fail-fast: false`**                 | `strategy: matrix` workflows don't short-circuit each other                                                                                                                                                |
| **Artifacts upload**                   | E2E tests upload everything they generate (`.screenshots/`, `.ocarina_logs/`, `.reports/`)                                                                                                                 |
| **`if: always()`**                     | Uploads aren't short-circuited on e2e test fail                                                                                                                                                            |
| **`environment:` for secrets**         | `OC` (ocarina-example), `github-pages` (deployments)                                                                                                                                                       |
| **`concurrency: pages`**               | Guards against race conditions                                                                                                                                                                             |
| **`defaults.run.shell: bash`**         | Cross-OS shell standardization                                                                                                                                                                             |

## Light on PR, heavy on manual

| Trigger                          | Load                                                |
| -------------------------------- | --------------------------------------------------- |
| **push/PR**                      | Lint + typecheck + unit tests (fast)                |
| **`workflow_dispatch`** (manual) | Full e2e (heavy)                                    |
| **Cron** (monthly)               | `unstable_python_full_build.yml` on Python 3.15-dev |
