---
title: "Chapter 02 — Ocarina, the framework"
description: "The Ocarina framework unpacked layer by layer, from the Result[T] type up to bootstrap: Railway Oriented Programming, invariants, orchestration and reporting."
weight: 3
date: 2026-05-20
tags: ["ocarina", "rop"]
sidebar:
  open: true
---

# Chapter 02&nbsp;—&nbsp;Ocarina, the framework

> Unpacks the whole `ocarina` framework (Python 3.14+, v1.1.10) and Railway Oriented Programming straight through to the reporting plugins. Structured as a layered walk: **deepest** (the `Result[T]` type) to **most visible** (the `bootstrap` that boots everything).

## Chapter plan

|  #  | Subject                                                                           | File or folder                                           |
| :-: | --------------------------------------------------------------------------------- | -------------------------------------------------------- |
| 01  | Technical identity, dependencies, toolchain                                       | [`01-identity.md`](01-identity.md)                       |
| 02  | Full module tree + layered diagram                                                | [`02-module-tree.md`](02-module-tree.md)                 |
| 03  | **Railway Oriented Programming**                                                  | [`03-railway/`](03-railway/README.md)                    |
| 04  | **Invariants** (validate, assertions, chain_validations)                          | [`04-invariants/`](04-invariants/README.md)              |
| 05  | **Orchestration** (Test → TestSuite → TestCampaign → TestCycle)                   | [`05-orchestration/`](05-orchestration/README.md)        |
| 06  | Lifecycle of a `Scenario`                                                         | [`06-scenario.md`](06-scenario.md)                       |
| 07  | **Watcher**                                                                       | [`07-watcher.md`](07-watcher.md)                         |
| 08  | `POMBase`                                                                         | [`08-pom-base.md`](08-pom-base.md)                       |
| 09  | Ports & adapters (`ILogger`, `ITakeScreenshot`)                                   | [`09-ports.md`](09-ports.md)                             |
| 10  | **Infrastructure** (pool, builder, screenshotter, act counter, Selenium adapters) | [`10-infra/`](10-infra/README.md)                        |
| 11  | **Opinionated layer** (CLI, loggers, plugins, bootstrap)                          | [`11-opinionated/`](11-opinionated/README.md)            |
| 12  | Custom types & custom errors                                                      | [`12-custom-types-errors.md`](12-custom-types-errors.md) |

## Related reading

- Functional programming: [`../03-functional/`](../03-functional/README.md)
- How the framework tests itself: [`../04-internal-tests/`](../04-internal-tests/README.md)
- Usage examples with project adapters: [`../07-ocarina-example/`](../07-ocarina-example/README.md), [`../08-ai-example/`](../08-ai-example/README.md)
- CI: [`../10-cicd/02-ocarina-workflows.md`](../10-cicd/02-ocarina-workflows.md)
