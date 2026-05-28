---
title: "Chapitre 02.05 — Orchestration"
description: "La chaîne d'orchestration d'Ocarina, Test vers Suite vers Campaign vers Cycle : qui gère la parallélisation, les rejeux, le skip et les invariants."
weight: 5
date: 2026-05-20
tags: ["ocarina", "invariants", "parallelisation"]
sidebar:
  open: true
---

# Chapitre 02.05&nbsp;—&nbsp;Orchestration

> Chaîne `Test → TestSuite → TestCampaign → TestCycle`&nbsp;: comment chaque niveau s'articule, qui gère la parallélisation, qui gère les rejeux, qui décide du _skip_, et où vivent les invariants pré-exécution.

## Plan

|  #  | Fichier                                                  | Sujet                                                                                                                                                      |
| :-: | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-test.md`](01-test.md)                               | La classe `Test[Driver]`&nbsp;—&nbsp;`spawn`, fragments pre/post, skip.                                                                                    |
| 02  | [`02-test-executor.md`](02-test-executor.md)             | `TestExecutor`&nbsp;—&nbsp;exécution d'**une** tentative, ordre&nbsp;: setup&nbsp;→&nbsp;watchers.start →&nbsp;chain →&nbsp;watchers.stop →&nbsp;teardown. |
| 03  | [`03-test-flow-retries.md`](03-test-flow-retries.md)     | `TestFlow`&nbsp;—&nbsp;boucle de rejeu (1+max_retries), backoff linéaire, gestion des setup-failures.                                                      |
| 04  | [`04-test-suite.md`](04-test-suite.md)                   | `TestSuite`&nbsp;—&nbsp;parallélisation avec `ThreadPoolExecutor`, filtrage IDs, garde-fous.                                                               |
| 05  | [`05-saturation.md`](05-saturation.md)                   | Saturation des workers&nbsp;: clonage aléatoire `[COPY N]`. Pourquoi et comment.                                                                           |
| 06  | [`06-test-campaign.md`](06-test-campaign.md)             | `TestCampaign`&nbsp;—&nbsp;séquence de suites, `campaign_has_failed`.                                                                                      |
| 07  | [`07-test-cycle-modes.md`](07-test-cycle-modes.md)       | `TestCycle`&nbsp;—&nbsp;smoke + main, modes `fail-fast` vs `wait-for-all`, `has_test_cycle_failed`.                                                        |
| 08  | [`08-filter-tests-by-ids.md`](08-filter-tests-by-ids.md) | `filter_tests_by_ids`&nbsp;—&nbsp;`--only`/`--exclude`, mutex, ignore les unknown IDs.                                                                     |

## Schéma

```
            ┌────────────────────────────────────────────────┐
            │                  TestCycle                     │
            │                                                │
            │  ┌──────────────────────────────────────────┐  │
            │  │ smoke_tests_campaigns                    │  │ ◄── 1er, gate
            │  │  └─ TestCampaign                         │  │     mode : fail-fast |
            │  │      └─ TestSuite                        │  │            wait-for-all
            │  │          └─ Test                         │  │
            │  └──────────────────────────────────────────┘  │
            │                                                │
            │  ┌──────────────────────────────────────────┐  │
            │  │ campaigns (main)                         │  │ ◄── skippées si
            │  │  └─ TestCampaign                         │  │     un smoke fail
            │  │      └─ TestSuite                        │  │
            │  │          └─ Test                         │  │
            │  └──────────────────────────────────────────┘  │
            └────────────────────────────────────────────────┘
```

## Qui fait quoi&nbsp;?

| Niveau         | Responsabilité unique                       | Concurrence    | Hors périmètre                     |
| -------------- | ------------------------------------------- | -------------- | ---------------------------------- |
| `Test`         | Métadonnées + `spawn(driver, logger)`       | aucune         | exécution                          |
| `TestExecutor` | Une **tentative**                           | aucune         | rejeu, acquisition de driver       |
| `TestFlow`     | Boucle de **rejeu**                         | aucune         | parallélisation, agrégation        |
| `TestSuite`    | Parallélisation + saturation + filtrage IDs | **N threads**  | séquence inter-suites              |
| `TestCampaign` | Séquence de suites                          | suite-level    | smoke vs main                      |
| `TestCycle`    | Smoke + main + mode                         | campaign-level | bootstrap /&nbsp;plugins post-exec |

Cette séparation stricte est **délibérée**&nbsp;: `TestExecutor` ne sait rien des retries, `TestFlow` ne sait rien de la concurrence, `TestSuite` ne sait rien de l'agrégation campaign-level. Chaque classe a un seul axe de responsabilité.

## Tableau des invariants pré-exécution

| Quand                                            | Invariant                                                                                                                                  | Source                                        |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| Construction `TestSuite`                         | `validate_test_runners_ids(tests).execute()`                                                                                               | `oc_test_suite.py#_guards_on_invoke`          |
| Avant exécution `TestSuite.run` (mode single)    | `validate_test_runners_names(tests).execute()` (post-saturation aussi)                                                                     | `oc_test_suite.py#_guards_with_mounted_tests` |
| Avant exécution `TestSuite.run` (mode parallèle) | `validate_test_runners_names(tests).execute()`                                                                                             | id.                                           |
| Avant exécution `TestSuite.run`                  | `validate_workers_amount(max_workers).execute()`                                                                                           | id.                                           |
| Construction `TestCampaign`                      | `validate_test_suites_names(suites).execute()`                                                                                             | `oc_test_campaign.py`                         |
| Construction `TestCycle`                         | `chain_validations(validate_test_cycle_name, validate_campaigns_names, validate_test_suites_names, validate_test_runners_names).execute()` | `oc_test_cycle.py`                            |

Tous ces invariants sont écrits avec [`validate(...)`](../04-invariants/01-validate-flow.md) et lèvent un `AggregateInvariantViolationError`.
