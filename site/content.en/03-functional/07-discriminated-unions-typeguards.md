---
title: "03.07 — Discriminated unions + TypeGuard + @final = sealed unions"
description: "Discriminated unions, TypeGuard and final: the combo that makes Result[T] and TestResult both typed and usable without casts."
weight: 7
date: 2026-05-20
series: ["functional"]
series_order: 7
tags: ["rop"]
---

# 03.07&nbsp;—&nbsp;Discriminated unions + TypeGuard + @final = "_sealed_" unions

> The combo that makes `Result[T]` and `TestResult` both **typed** and **usable without casts**.

## Discriminated union

```python
@final
@dataclass(frozen=True)
class Ok[T](_BaseResult):
    value: T
    error: None = None

@final
@dataclass(frozen=True)
class Fail(_BaseResult):
    error: Exception = field(default_factory=lambda: Exception("Unknown error"))

type Result[T] = Ok[T] | Fail
```

- Two constructors: `Ok[T]` and `Fail`.
- _Discriminant_ is the _isinstance check_ (not a field like `tag: Literal["ok", "fail"]`).
- Both are `@final`&nbsp;—&nbsp;_no_ possible subtype. The union is **exhaustive**, i.e. "_sealed_".

## Narrowing, `TypeGuard`

```python
def is_ok[T](result: Result[T]) -> TypeGuard[Ok[T]]:
    return isinstance(result, Ok)

def is_fail[T](result: Result[T]) -> TypeGuard[Fail]:
    return isinstance(result, Fail)
```

```python
def handle_result(result: Result[int]) -> str:
    if is_ok(result):
        return f"Got: {result.value}"          # mypy: result is Ok[int], so .value exists
    if is_fail(result):
        return f"Error: {result.error}"        # mypy: result is Fail, so .error exists
    # mypy can detect this branch is unreachable (exhaustiveness)
```

## `_BaseResult`

```python
class _BaseResult:
    error: Exception | None
```

This base lets you access `result.error` **without narrowing**:

```python
def maybe_log_error(result: Result[int]) -> None:
    if result.error:                            # ok, _BaseResult has "error"
        logger.error(str(result.error))
```

But without narrowing, you can't access `result.value` (only exists on `Ok`).

## `TestResult = Result[Any] | None`

```python
# src/ocarina/custom_types/oc_test_layers.py
type TestResult = Result[Any] | None
```

Three cases: `Ok`, `Fail`, `None` (skip). Three `TypeGuard`s:

```python
# src/ocarina/aggregates/tests_layers.py
def is_test_result_ok(result: TestResult) -> TypeGuard[Ok[Any]]:
    return isinstance(result, Ok)

def is_test_result_fail(result: TestResult) -> TypeGuard[Fail]:
    return isinstance(result, Fail)

def is_test_result_skipped(result: TestResult) -> TypeGuard[None]:
    return result is None
```

In `pretty_print_results` (excerpt):

```python
for test_name, (result, steps, test_id) in suite_results.items():
    if is_test_result_skipped(result):
        print(f"  > {test_name} » SKIPPED")
    elif is_test_result_ok(result):
        print(f"  > {test_name} » PASSED")
    elif is_test_result_fail(result):
        print(f"  > {test_name} » FAILED")
        print(f"    → {result.error}")
        print(f"      ⫸ At step {steps}")
```

Every branch typed. After `is_test_result_fail`, `result.error` is `Exception`.

## `@final` across the framework

| Class                                                                                                                                                                      | File                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `Ok[T]`, `Fail`                                                                                                                                                            | `railway/result.py`                                          |
| `Test[Driver]`                                                                                                                                                             | `dsl/testing/oc_test.py`                                     |
| `Watcher[Driver]`                                                                                                                                                          | `dsl/testing/watcher.py`                                     |
| `TestCycle[Driver]`                                                                                                                                                        | `dsl/testing/oc_test_cycle.py`                               |
| `ChainRunner[T]`                                                                                                                                                           | `dsl/testing_with_railway/chain_actions.py`                  |
| `ActionStart[T]`, `ActionFailure[T]`, `ActionSuccess[T]`, `ActionChain[T]`                                                                                                 | `dsl/testing_with_railway/internals/action_chain.py`         |
| `NeutralActionStart[T]`, `NeutralActionFailure[T]`, `NeutralActionSuccess[T]`                                                                                              | id.                                                          |
| `When`                                                                                                                                                                     | `dsl/testing_with_railway/match_page.py`                     |
| `_PredicateWithMsg`, `_ValidationChain`, `_ValidationResult`, `ValidationStartBlock`, `ValidationAssertBlock`, `BusinessInvariantValidator`, `FrameworkInvariantValidator` | `dsl/invariants/{validate.py,internals/validation_chain.py}` |
| `ExecutionOutcome`, `TestExecutor[Driver]`, `TestFlow[Driver]`                                                                                                             | `dsl/testing/internals/{test_executor,test_flow}.py`         |
| `WebDriversPool[Driver]`                                                                                                                                                   | `infra/drivers_pool.py`                                      |
| `DriverDiedError`                                                                                                                                                          | `custom_errors/test_framework/driver_died.py`                |
| `Scenario[Driver]`, `TestRunner[Driver]`                                                                                                                                   | `custom_types/{scenario,test_runner}.py`                     |
| `FileLogger`                                                                                                                                                               | `opinionated/loggers/file_logger.py`                         |

**Nothing in the DSL is subclassable**. Extension always goes through composition (closures, project adapters, parameterized values).

The payoff (type safety, exhaustiveness, refactor safety) is huge.

## The compiler has the final say

The Holy Book puts it (chapter "What is Ocarina?"):

> By design, Ocarina makes itself hard to misuse: the compiler has the final say.

Here, "_the compiler has the final say_" materializes through:

- `Result[T]`
- `TypeGuard`
- `@final`
