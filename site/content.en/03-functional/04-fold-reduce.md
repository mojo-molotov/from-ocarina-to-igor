---
title: "03.04 — reduce / fold in Ocarina"
description: "One reduce in the whole code base. But it's the central reducer — it's what makes chain_actions work."
weight: 4
date: 2026-05-20
series: ["functional"]
series_order: 4
---

# 03.04&nbsp;—&nbsp;`reduce` / fold in Ocarina

> One `reduce` in the whole code base. But it's **the** central reducer&nbsp;—&nbsp;it's what makes `chain_actions` work.

## Code

```python
# src/ocarina/dsl/testing_with_railway/chain_actions.py
from functools import reduce

def chain_actions[T](
    first: ActionSuccess[T], *rest: ActionSuccess[T]
) -> ChainRunner[T]:

    def thunk() -> ActionChain[T]:
        def reducer(chain: ActionChain[T], step: ActionSuccess[T]) -> ActionChain[T]:
            if chain.has_failed():
                return chain
            return (
                chain.then(step.__action__)
                .failure(step.__failure_handler__)
                .success(step.__success_handler__)
                .execute()
            )
        return reduce(reducer, rest, first.execute())

    return ChainRunner(thunk=thunk)
```

## Anatomy

| FP concept       | Python realization                       |
| ---------------- | ---------------------------------------- |
| Accumulator type | `ActionChain[T]`                         |
| Element type     | `ActionSuccess[T]`                       |
| Reducer          | `reducer(chain, step) -> ActionChain[T]` |
| Initial value    | `first.execute()`                        |
| Iterable         | `rest` (the `*rest` tuple)               |
| Short-circuit    | `if chain.has_failed(): return chain`    |
| Result           | `ActionChain[T]` (the last one)          |

## Execution flow

```
initial = first.execute()                                          # → ActionChain(ok=True, result=Ok(...))

step 1 : reducer(<initial>, act2) :
  chain.has_failed() = False
  chain.then(act2.__action__).failure(...).success(...).execute()
  → action raises → Fail
  → failure_handler(exc)  ❌ FIRE
  → ActionChain(ok=False, result=Fail(exc))

step 2 : reducer(<failed>, act3) :
  chain.has_failed() = True
  return chain                                                     ⚠️  short-circuit

result of the reduce = <failed ActionChain>
```

## Why `reduce`

```python
# Imperative approach (equivalent)
def thunk() -> ActionChain[T]:
    chain = first.execute()
    for step in rest:
        if chain.has_failed():
            break
        chain = (
            chain.then(step.__action__)
            .failure(step.__failure_handler__)
            .success(step.__success_handler__)
            .execute()
        )
    return chain
```

| Reduce                                          | Imperative loop      |
| ----------------------------------------------- | -------------------- |
| A single **value** flows (the `chain`)          | A state + a mutation |
| Reducer = pure function (testable in isolation) | Inline logic         |
| Explicit "_accumulator_" semantics              | Implicit logic       |
| Functional standard                             | Imperative standard  |

An **expression of intent**: we _fold_ a list onto an accumulator. Semantics jump out on the first read. This is what's called a **catamorphism**.

## `break` vs `return chain` in the reducer

The reducer can't `break`&nbsp;—&nbsp;it _must_ return a value. So it returns `chain` _unchanged_ at every step after the failure.

Exactly what we want: the fold rolls over the remaining elements, each reducer call returns the _same_ failed chain. Short-circuit.

## `any` / `all` = Pythonic folds

```python
def has_test_cycle_failed(results: TestCycleResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaigns in results.values()
        for tests in campaigns.values()
        for outcome, _, _ in tests.values()
    )
```

`any(...)` is an OR-fold with short-circuit. Three nested `for`s _folded_ into a single bool.

Same conceptual mechanic as `chain_actions.reducer`, just without the explicit `reduce`.

## Why not `toolz`, `funcy`, or a homemade wrapper

The project imports **zero** third-party FP libs. `functools.reduce` has been in the stdlib for 30 years. No magic, no breaking-change risk, no audit debt.
