---
title: "Chapitre 10 — CI/CD de tout l'écosystème"
description: "La CI/CD de tout l'écosystème Ocarina : tableau récapitulatif et détail des workflows de chacun des six dépôts."
weight: 11
date: 2026-05-20
tags: ["ci-cd"]
sidebar:
  open: true
---

# Chapitre 10&nbsp;—&nbsp;CI/CD de tout l'écosystème

> Tableau récapitulatif de tous les workflows CI de l'écosystème.

## Plan

|  #  | Fichier                                                    | Sujet                                                                                       |
| :-: | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 01  | [`01-matrix.md`](01-matrix.md)                             | Tableau récapitulatif de tous les workflows.                                                |
| 02  | [`02-ocarina-workflows.md`](02-ocarina-workflows.md)       | `ocarina`&nbsp;: `main_ci.yml`, `dev_ci.yml`, `unstable_python_full_build.yml`              |
| 03  | [`03-example-workflows.md`](03-example-workflows.md)       | `ocarina-example`&nbsp;: `main_ci.yml`, `dev_ci.yml`, `e2e.yml`                             |
| 04  | [`04-ai-workflows.md`](04-ai-workflows.md)                 | `ocarina-with-ai-example`&nbsp;: `ai_proof_ci.yml`, `ai_proof_e2e.yml`                      |
| 05  | [`05-igoristan-workflows.md`](05-igoristan-workflows.md)   | `igoristan`&nbsp;: `ci-pr.yml`, `deploy.yml`                                                |
| 06  | [`06-holy-book-workflow.md`](06-holy-book-workflow.md)     | `ocarina-holy-book`&nbsp;: `deploy.yml`                                                     |
| 07  | [`07-tests-workers-vercel.md`](07-tests-workers-vercel.md) | `tests-workers`&nbsp;: pas de CI GitHub, déploiement directement pris en charge par Vercel. |

## Vue d'ensemble

| Dépôt                     | Workflows                                     | Total |
| ------------------------- | --------------------------------------------- | ----: |
| `ocarina`                 | main_ci + dev_ci + unstable_python_full_build |     3 |
| `ocarina-example`         | main_ci + dev_ci + e2e                        |     3 |
| `ocarina-with-ai-example` | ai_proof_ci + ai_proof_e2e                    |     2 |
| `igoristan`               | ci-pr + deploy                                |     2 |
| `ocarina-holy-book`       | deploy                                        |     1 |
| `tests-workers`           | _aucun_ (délégué à Vercel)                    |     0 |

\+ `ocarina/.github/actions/allure-history/action.yml`.

## Discipline transversale

| Convention                                  | Bénéfice                                                                                                                                                                                                                                        |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`workflow_dispatch` toujours présent**    | Tous les workflows peuvent être lancés manuellement                                                                                                                                                                                             |
| **Cache `.venv` /&nbsp;`node_modules`**     | Tous les workflows cachent le venv ou les deps node                                                                                                                                                                                             |
| **Stratégie "matrix"**                      | Workflows dupliqués parallélisés pour tester la compatibilité avec plusieurs OS et plusieurs navigateurs web&nbsp;: `ocarina` (ubuntu+windows). Les autres&nbsp;: ubuntu seul (suffit). `ocarina-with-ai-example`&nbsp;: matrix Firefox+Chrome. |
| **`fail-fast: false`**                      | Les workflows instanciés avec `strategy: matrix` ne se court-circuitent pas entre eux                                                                                                                                                           |
| **Artifacts upload**                        | Les tests e2e uploadent toutes les ressources qu'ils génèrent (`.screenshots/`, `.ocarina_logs/`, `.reports/`)                                                                                                                                  |
| **`if: always()`**                          | Les upload ne sont pas court-circuités en cas de fail de test e2e                                                                                                                                                                               |
| **`environment:` pour gestion des secrets** | `OC` (ocarina-example), `github-pages` (déploiements)                                                                                                                                                                                           |
| **`concurrency: pages`**                    | Sécurise les race conditions                                                                                                                                                                                                                    |
| **`defaults.run.shell: bash`**              | Standardisation du shell cross-OS                                                                                                                                                                                                               |

## Léger en PR, lourd en manuel

| Trigger                          | Charge                                               |
| -------------------------------- | ---------------------------------------------------- |
| **push/PR**                      | Lint + typecheck + tests unitaires (rapide)          |
| **`workflow_dispatch`** (manuel) | e2e complet (gourmand)                               |
| **Cron** (mensuel)               | `unstable_python_full_build.yml` sur Python 3.15-dev |
