---
title: "Chapter 02.03 — Railway Oriented Programming"
description: "Railway Oriented Programming at Ocarina's core: success and failure as two parallel rails, short-circuiting, and readable syntactic composition."
weight: 3
date: 2026-05-20
tags: ["ocarina", "rop"]
sidebar:
  open: true
---

# Chapter 02.03&nbsp;—&nbsp;Railway Oriented Programming

> Ocarina's beating heart. The whole DSL rides on this mechanic: success and failure as two _parallel rails_. A failure _switches_ the train onto the failure rail and locks it there (short-circuit), but composition stays linear so the scenario still reads top-to-bottom.

## Plan

|  #  | File                                                     | Subject                                                                               |
| :-: | -------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 01  | [`01-result.md`](01-result.md)                           | `Result[T] = Ok[T] \| Fail`, `is_ok`/`is_fail`                                        |
| 02  | [`02-action-chain-states.md`](02-action-chain-states.md) | State machine `ActionStart → ActionFailure → ActionSuccess → ActionChain`.            |
| 03  | [`03-neutral-rail.md`](03-neutral-rail.md)               | Failure rail: `NeutralActionStart` / `NeutralActionFailure` / `NeutralActionSuccess`. |
| 04  | [`04-chain-actions-fold.md`](04-chain-actions-fold.md)   | `ChainRunner[T]` (thunk) + `chain_actions` (fold).                                    |
| 05  | [`05-create-act-hooks.md`](05-create-act-hooks.md)       | `create_act` and its hooks (`on_failure`, `on_run_effect`, `act_counter_effect`).     |
| 06  | [`06-drive-page.md`](06-drive-page.md)                   | `drive_page`, a semantic alias.                                                       |
| 07  | [`07-match-page-when.md`](07-match-page-when.md)         | `match_page` / `when` + exception policy.                                             |

## Lineage

Direct inspiration: **Railway Oriented Programming**, popularized by Scott Wlaschin (F#).

> Twisting Ocarina's ROP (_Railway Oriented Programming_) implementation until it lost all meaning, since they didn't even know what ROP is.

The Python port stays **faithful**: builder state machine (_Typestate Pattern_), neutralized failure rail, lazy composition via `ChainRunner`. Mechanics laid out in [`02-action-chain-states.md`](02-action-chain-states.md).

## Metaphor taken from the module

Excerpt from the `action_chain.py` docstring:

> **Railway metaphor**:
>
> Code as railway track with two rails:
>
> - Success rail (top): Actions execute normally → Ok results
> - Failure rail (bottom): Action failed → Fail results
>
> When an action fails, the train switches to the failure rail and stays there (short-circuits). Subsequent actions become no-ops.

```
                       act1           act2           act3
                        │              │              │
                        ▼              ▼              ▼
Success rail  ─────[ EXECUTE ]────[ EXECUTE ]────[ EXECUTE ]─────┐
                        │                                        │
                        │ (fail → switch)                        ├──►  Result
                        ▼                                        │
Failure rail  ─────[  NO-OP  ]────[  NO-OP  ]────[  NO-OP  ]─────┘

Two parallel rails, same steps. If act1 fails, the train switches onto
the failure rail and stays there: the subsequent acts remain callable
(the .failure/.success/.execute API still exists), but they do nothing
(no-op).
```

## Why ROP rather than `try/except`

| Aspect                    | Classical `try/except`                              | ROP                                                  |
| ------------------------- | --------------------------------------------------- | ---------------------------------------------------- |
| Failure propagation       | Implicit (the exception bubbles)                    | Explicit (a `Fail` value flows out)                  |
| Type-checker verification | Impossible (every exception is possible everywhere) | Strong (`Result[T]` is a discriminated union)        |
| Composition               | Nesting (`try { … try { … } }`)                     | Linear (`.then().then().then()`)                     |
| Short-circuit             | Manual (`if exc: return`)                           | Automatic (failure rail)                             |
| Handlers                  | Coupled to a nearby `except`                        | Decoupled (`.failure(handler)`, `.success(handler)`) |

Net result: **`try/except` in project code collapses**. You stop reaching for one out of fear and instead pick it deliberately, in the rare spots it still earns its keep.

## The DSL's overall contract

| Primitive                          | Return type           | Reading                          |
| ---------------------------------- | --------------------- | -------------------------------- |
| `act(pom, action)`                 | `ActionStart[TPOM]`   | “I'm starting a step”            |
| `.failure(h)`                      | `ActionFailure[TPOM]` | “on failure, do h”               |
| `.success(h')`                     | `ActionSuccess[TPOM]` | “on success, do h'”              |
| `.execute()`                       | `ActionChain[TPOM]`   | “execute the step”               |
| `drive_page(act1, act2, …)`        | `ChainRunner[TPOM]`   | “I take control of a page”       |
| `match_page(branches=[when(...)])` | `ChainRunner[Any]`    | “I branch on the observed state” |

Every `scenario.test_chain` is a `Sequence[ChainRunner[Any]]`. Any user extension (new combinator, `skip_if`, whatever) has to hand back a `ChainRunner`. See [`../06-scenario.md`](../06-scenario.md) and [`../../03-functional/`](../../03-functional/README.md)
