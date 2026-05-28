---
title: "Chapitre 02 — Ocarina, le framework"
description: "Le framework Ocarina dépilé en couches, du type Result[T] jusqu'au bootstrap : Railway Oriented Programming, invariants, orchestration et reporting."
weight: 3
date: 2026-05-20
tags: ["ocarina", "rop"]
sidebar:
  open: true
---

# Chapitre 02&nbsp;—&nbsp;Ocarina, le framework

> Ce chapitre dépile l'intégralité du framework `ocarina` (Python 3.14+, version 1.1.0) ainsi que du Railway Oriented Programming jusqu'aux plugins de reporting. Il est structuré comme un parcours en couches&nbsp;: du **plus profond** (le type `Result[T]`) vers le **plus visible** (le `bootstrap` qui démarre tout).

## Plan du chapitre

|  #  | Sujet                                                                               | Fichier ou dossier                                       |
| :-: | ----------------------------------------------------------------------------------- | -------------------------------------------------------- |
| 01  | Identité technique, dépendances, _toolchain_                                        | [`01-identity.md`](01-identity.md)                       |
| 02  | Arborescence complète du module + schéma en couches                                 | [`02-module-tree.md`](02-module-tree.md)                 |
| 03  | **Railway Oriented Programming**                                                    | [`03-railway/`](03-railway/README.md)                    |
| 04  | **Invariants** (validate, assertions, chain_validations)                            | [`04-invariants/`](04-invariants/README.md)              |
| 05  | **Orchestration** (Test&nbsp;→&nbsp;TestSuite →&nbsp;TestCampaign →&nbsp;TestCycle) | [`05-orchestration/`](05-orchestration/README.md)        |
| 06  | Cycle de vie d'un `Scenario`                                                        | [`06-scenario.md`](06-scenario.md)                       |
| 07  | **Watcher**                                                                         | [`07-watcher.md`](07-watcher.md)                         |
| 08  | `POMBase`                                                                           | [`08-pom-base.md`](08-pom-base.md)                       |
| 09  | Ports & adapters (`ILogger`, `ITakeScreenshot`)                                     | [`09-ports.md`](09-ports.md)                             |
| 10  | **Infrastructure** (pool, builder, screenshotter, act counter, adapters Selenium)   | [`10-infra/`](10-infra/README.md)                        |
| 11  | **Couche opinionated** (CLI, loggers, plugins, bootstrap)                           | [`11-opinionated/`](11-opinionated/README.md)            |
| 12  | Custom types & custom errors                                                        | [`12-custom-types-errors.md`](12-custom-types-errors.md) |

## Lectures connexes

- Programmation fonctionnelle&nbsp;: [`../03-functional/`](../03-functional/README.md)
- Comment le framework se teste lui-même&nbsp;: [`../04-internal-tests/`](../04-internal-tests/README.md)
- Exemples d'usage avec adapters projet&nbsp;: [`../07-ocarina-example/`](../07-ocarina-example/README.md), [`../08-ai-example/`](../08-ai-example/README.md)
- CI&nbsp;: [`../10-cicd/02-ocarina-workflows.md`](../10-cicd/02-ocarina-workflows.md)
