---
title: "Chapter 02.05 — Orchestration"
description: "Test → TestSuite → TestCampaign → TestCycle: how each level slots into the next, who owns parallelization, who owns retries, who decides skipping, and where the pre-execution invariants live."
weight: 5
date: 2026-05-20
tags: ["ocarina", "invariants", "parallelization"]
sidebar:
  open: true
---

# Chapter 02.05&nbsp;—&nbsp;Orchestration

> `Test → TestSuite → TestCampaign → TestCycle`: how each level slots into the next, who owns parallelization, who owns retries, who decides skipping, and where the pre-execution invariants live.

## Plan

|  #  | File                                                     | Subject                                                                                                                    |
| :-: | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-test.md`](01-test.md)                               | The `Test[Driver]` class&nbsp;—&nbsp;`spawn`, pre/post fragments, skip.                                                    |
| 02  | [`02-test-executor.md`](02-test-executor.md)             | `TestExecutor`&nbsp;—&nbsp;execution of **one** attempt, order: setup → watchers.start → chain → watchers.stop → teardown. |
| 03  | [`03-test-flow-retries.md`](03-test-flow-retries.md)     | `TestFlow`&nbsp;—&nbsp;retry loop (1 + max_retries), linear backoff, setup-failure handling.                               |
| 04  | [`04-test-suite.md`](04-test-suite.md)                   | `TestSuite`&nbsp;—&nbsp;parallelization with `ThreadPoolExecutor`, ID filtering, guardrails.                               |
| 05  | [`05-saturation.md`](05-saturation.md)                   | Worker saturation: random cloning `[COPY N]`. Why and how.                                                                 |
| 06  | [`06-test-campaign.md`](06-test-campaign.md)             | `TestCampaign`&nbsp;—&nbsp;sequence of suites, `campaign_has_failed`.                                                      |
| 07  | [`07-test-cycle-modes.md`](07-test-cycle-modes.md)       | `TestCycle`&nbsp;—&nbsp;smoke + main, `fail-fast` vs `wait-for-all` modes, `has_test_cycle_failed`.                        |
| 08  | [`08-filter-tests-by-ids.md`](08-filter-tests-by-ids.md) | `filter_tests_by_ids`&nbsp;—&nbsp;`--only`/`--exclude`, mutex, ignores unknown IDs.                                        |

## Diagram

```
            ┌────────────────────────────────────────────────┐
            │                  TestCycle                     │
            │                                                │
            │  ┌──────────────────────────────────────────┐  │
            │  │ smoke_tests_campaigns                    │  │ ◄── first, gate
            │  │  └─ TestCampaign                         │  │     mode: fail-fast |
            │  │      └─ TestSuite                        │  │           wait-for-all
            │  │          └─ Test                         │  │
            │  └──────────────────────────────────────────┘  │
            │                                                │
            │  ┌──────────────────────────────────────────┐  │
            │  │ campaigns (main)                         │  │ ◄── skipped if a
            │  │  └─ TestCampaign                         │  │     smoke fails
            │  │      └─ TestSuite                        │  │
            │  │          └─ Test                         │  │
            │  └──────────────────────────────────────────┘  │
            └────────────────────────────────────────────────┘
```

## Who does what?

| Level          | Single responsibility                       | Concurrency    | Out of scope                  |
| -------------- | ------------------------------------------- | -------------- | ----------------------------- |
| `Test`         | Metadata + `spawn(driver, logger)`          | none           | execution                     |
| `TestExecutor` | One **attempt**                             | none           | retries, driver acquisition   |
| `TestFlow`     | **Retry** loop                              | none           | parallelization, aggregation  |
| `TestSuite`    | Parallelization + saturation + ID filtering | **N threads**  | inter-suite sequence          |
| `TestCampaign` | Sequence of suites                          | suite-level    | smoke vs main                 |
| `TestCycle`    | Smoke + main + mode                         | campaign-level | bootstrap / post-exec plugins |

The strict separation is **deliberate**. `TestExecutor` knows nothing about retries. `TestFlow` knows nothing about concurrency. `TestSuite` knows nothing about campaign-level aggregation. One axis of responsibility per class.

## Table of pre-execution invariants

| When                                             | Invariant                                                                                                                                  | Source                                        |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| `TestSuite` construction                         | `validate_test_runners_ids(tests).execute()`                                                                                               | `oc_test_suite.py#_guards_on_invoke`          |
| Before `TestSuite.run` execution (single mode)   | `validate_test_runners_names(tests).execute()` (also post-saturation)                                                                      | `oc_test_suite.py#_guards_with_mounted_tests` |
| Before `TestSuite.run` execution (parallel mode) | `validate_test_runners_names(tests).execute()`                                                                                             | id.                                           |
| Before `TestSuite.run` execution                 | `validate_workers_amount(max_workers).execute()`                                                                                           | id.                                           |
| `TestCampaign` construction                      | `validate_test_suites_names(suites).execute()`                                                                                             | `oc_test_campaign.py`                         |
| `TestCycle` construction                         | `chain_validations(validate_test_cycle_name, validate_campaigns_names, validate_test_suites_names, validate_test_runners_names).execute()` | `oc_test_cycle.py`                            |

All these invariants ride on [`validate(...)`](../04-invariants/01-validate-flow.md) and raise an `AggregateInvariantViolationError`.
