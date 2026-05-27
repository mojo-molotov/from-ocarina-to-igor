---
title: "Chapter 02.04 — Invariants"
description: "Ocarina's sub-DSL for typed, composable invariants. Used everywhere: CLI, POMs, the custom_invariants/testing/ that check suite consistency before any test runs."
weight: 4
date: 2026-05-20
tags: ["ocarina", "rop", "invariants"]
sidebar:
  open: true
---

# Chapter 02.04&nbsp;—&nbsp;Invariants

> Ocarina's sub-DSL for typed, composable invariants. Used everywhere: CLI, POMs, the `custom_invariants/testing/` that check suite consistency before any test runs.

## Plan

|  #  | File                                                                             | Subject                                                                                                                              |
| :-: | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 01  | [`01-validate-flow.md`](01-validate-flow.md)                                     | The full flow `validate(value) → assert_that → execute → raise_if_invalid` + the `_ValidationChain` class.                           |
| 02  | [`02-assertions.md`](02-assertions.md)                                           | Catalog of builtin assertions (`is_str`, `is_email`, `is_positive`, `is_in`, `has_unique_elements`, `each`, `is_valid_filename`, …). |
| 03  | [`03-otherwise-any-of.md`](03-otherwise-any-of.md)                               | `.otherwise(...)` and the OR combination via `_any_of`.                                                                              |
| 04  | [`04-then-chain-of-validations.md`](04-then-chain-of-validations.md)             | `.then(new_value)` and `chain_validations(...)` for composition.                                                                     |
| 05  | [`05-business-vs-framework-validator.md`](05-business-vs-framework-validator.md) | `BusinessInvariantValidator` vs `FrameworkInvariantValidator`                                                                        |
| 06  | [`06-invariant-errors.md`](06-invariant-errors.md)                               | `InvariantViolationError`, `DuplicatesError`, `AggregateInvariantViolationError`.                                                    |

## Why the invariants DSL

1. **Pre-execution guard.** `TestSuite.__init__` checks&nbsp;—&nbsp;_before_ launching anything&nbsp;—&nbsp;that test names / IDs are unique, `max_workers >= 1`, etc.
2. **CLI validation.** Every flag carries its `validate=lambda chain: chain.assert_that(...)` inside the `CliStore`. Errors aggregate into one message.
3. **POM-side validation.** POM actions validate their parameters ("`retries` must be positive") via `validate(retries, name="retries").assert_that(is_positive).execute().raise_if_invalid()`.

The Holy Book sums it up:

> Usable in POMs, `validate` lets you express invariants as chains. Execution is **deferred**: you have to call `.execute()` explicitly.
>
> The result exposes `is_valid`, `errors`, and `validated_values`. It is inert by default. `.raise_if_invalid()` raises the exception when needed.

## Design principles

| Principle              | Realization                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Deferred execution** | `.execute()` is mandatory. Before that, the chain is composable but inert.                                        |
| **Aggregated errors**  | `_ValidationChain` runs every step and collects errors; no _fail-fast_.                                           |
| **Typed composition**  | `.then(U)` changes the type; the `T` is preserved through the chain.                                              |
| **Logical OR**         | `.otherwise(pred)` combines with the previous via `_any_of`.                                                      |
| **Type safety**        | `validate("lol").assert_that(is_positive)` raises a _mypy_ error (incompatible predicate).                        |
| **Reusability**        | `BusinessInvariantValidator.create(...)` or `FrameworkInvariantValidator.create(...)` to factor out an invariant. |

## Strong link with ROP

The invariants sub-DSL **follows the same grammar** as ROP:

| ROP                                                                           | Invariants                                                                   |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `ActionStart[T]` → `ActionFailure[T]` → `ActionSuccess[T]` → `ActionChain[T]` | `ValidationStartBlock[T]` → `ValidationAssertBlock[T]` → `_ValidationResult` |
| Flat composition via `chain_actions(*)`                                       | Flat composition via `chain_validations(*)`                                  |
| Lazy evaluation (`Thunk[ActionChain[T]]`)                                     | Lazy evaluation (`.execute()`)                                               |
| `Result[T]`                                                                   | `_ValidationResult` (with `is_valid`, `errors`, `validated_values`)          |
| Error aggregated by `Fail`                                                    | Error aggregated by `AggregateInvariantViolationError`                       |

**Same pattern**, different domain. See [`../03-railway/`](../03-railway/README.md) for the original.
