---
title: "Chapter 00 — Big picture"
description: "An overview of the Ocarina ecosystem: repository map, stack matrix, execution flow and relations between the projects."
weight: 1
date: 2026-05-20
tags: ["big-picture"]
sidebar:
  open: true
---

# Chapter 00&nbsp;—&nbsp;Big picture

> Cartography of the ecosystem: who talks to whom, who depends on what, and which way the data flows.

## Chapter files

|  #  | File                                                         | Contents                                                                                                    |
| :-: | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| 01  | [`01-ecosystem-map.md`](01-ecosystem-map.md)                 | The six repositories on a single diagram: their role, their license, and the contract that binds them.      |
| 02  | [`02-stack-matrix.md`](02-stack-matrix.md)                   | Technical stack per repository (language, dependencies, build, deployment, version).                        |
| 03  | [`03-global-execution-flow.md`](03-global-execution-flow.md) | End-to-end execution flow of an e2e campaign: USER → CLI → Pool → Cycle → SUT → Plugins.                    |
| 04  | [`04-repo-relations.md`](04-repo-relations.md)               | Detail of bilateral relationships: who imports what, who consumes which artifact, which secrets are shared. |

## Related reading

- Philosophy of the ecosystem → [`../01-philosophy/`](../01-philosophy/README.md)
- The framework itself in detail → [`../02-ocarina/`](../02-ocarina/README.md)
- The two “example” suites → [`../07-ocarina-example/`](../07-ocarina-example/README.md), [`../08-ai-example/`](../08-ai-example/README.md)
- The public SUT → [`../05-igoristan/`](../05-igoristan/README.md)
- The OTP / Corsicadex backend → [`../06-tests-workers/`](../06-tests-workers/README.md)
