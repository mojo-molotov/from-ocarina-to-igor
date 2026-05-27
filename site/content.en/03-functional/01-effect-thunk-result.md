---
title: "03.01 — Effect, Thunk[T], Result[T]"
description: "Three lines in custom_types/ + one in railway/. The whole DSL rides on them."
weight: 1
date: 2026-05-20
series: ["functional"]
series_order: 1
tags: ["rop"]
---

# 03.01&nbsp;—&nbsp;`Effect`, `Thunk[T]`, `Result[T]`

> Three lines in `custom_types/` + one in `railway/`. The whole DSL rides on them.

## Triplet

```python
# src/ocarina/custom_types/effect.py
type Effect = Callable[[], None]
type Effects = tuple[Effect, ...]

# src/ocarina/custom_types/thunk.py
type Thunk[T] = Callable[[], T]

# src/ocarina/railway/result.py
type Result[T] = Ok[T] | Fail
```

| Type        | FP semantics                      | Definition                          |
| ----------- | --------------------------------- | ----------------------------------- |
| `Effect`    | Side effect (deferred)            | `() -> None`                        |
| `Thunk[T]`  | Deferred _computation_ with value | `() -> T` (laziness + value)        |
| `Result[T]` | _Computation_ that can fail       | Discriminated union `Ok[T] \| Fail` |

## Effect vs Thunk distinction

```python
log_msg: Effect = lambda: print("hello")        # () -> None
get_42: Thunk[int] = lambda: 42                 # () -> int
fetch:  Thunk[Result[int]] = lambda: Ok(42)     # () -> Result[int]
```

Function _returns_ something consumed elsewhere → `Thunk[T]`.  
Otherwise → `Effect`.

## `Effect`

| Use                                                           | Location                                                                      |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `Scenario.setup` / `Scenario.teardown`                        | `custom_types/scenario.py`                                                    |
| `dispose` in `BuiltWebDriver[Driver] = tuple[Driver, Effect]` | `custom_types/built_web_driver.py`                                            |
| `act_counter_effect`, `on_run_effect` in `create_act`         | `dsl/testing_with_railway/constructors/create_act.py`                         |
| CLI effects (`effects_factory` in `CliBuilder`)               | `opinionated/cli/builder.py`                                                  |
| `SuccHandler` (success handler of `act`)                      | `dsl/testing_with_railway/internals/action_chain.py` (`SuccHandler = Effect`) |
| `bootstrap` plugins (each plugin is an `Effect`)              | `opinionated/launcher/bootstrap.py`                                           |

## `Thunk[T]`

| Use                                                           | Location                                             |
| ------------------------------------------------------------- | ---------------------------------------------------- |
| `Thunk[Result[T]] = Action[T]` (the _thunk_ of an ROP action) | `dsl/testing_with_railway/internals/action_chain.py` |
| `Thunk[ActionChain[T]]` in `ChainRunner`                      | `dsl/testing_with_railway/chain_actions.py`          |
| `Thunk[bool]` for the `when` conditions of `match_page`       | `dsl/testing_with_railway/match_page.py`             |
| `Thunk[str]` for `logger.set_prefix(prefix_thunk)`            | `ports/ilogger.py`                                   |
| `Thunk[ILogger]` for logger factories                         | `dsl/testing/oc_test_suite.py`, etc.                 |
| `Thunk[bool]` in the `TestCycle` `dispatch` (mode selection)  | `dsl/testing/oc_test_cycle.py`                       |

## `Result[T]`

| Use                                                         | Location                                              |
| ----------------------------------------------------------- | ----------------------------------------------------- |
| Return of `create_act` (via `Action[T] = Thunk[Result[T]]`) | `dsl/testing_with_railway/constructors/create_act.py` |
| Result of an `ActionChain`                                  | `dsl/testing_with_railway/internals/action_chain.py`  |
| `TestResult = Result[Any] \| None`                          | `custom_types/oc_test_layers.py`                      |

## Centralization

Without these aliases, every signature that takes an effect would write `Callable[[], None]`&nbsp;—&nbsp;visual noise, harder to grep, harder to refactor.

With the aliases:

```python
def run_plugins(*plugins: Effect, exceptions_logger: ILogger) -> None: ...
def setup_fn() -> Effect: return lambda: seed_db()
def factory(...) -> tuple[Effect, ...]: ...
```

## PEP 695 for these aliases

```python
type Effect = Callable[[], None]                  # PEP 695 (Python 3.12+)
type Thunk[T] = Callable[[], T]                   # PEP 695 (parameterized)
type Result[T] = Ok[T] | Fail                     # PEP 695 (parameterized + union)
```

Before PEP 695:

```python
from typing import TypeAlias, TypeVar, Callable, Union

Effect: TypeAlias = Callable[[], None]

T = TypeVar("T")
Thunk: TypeAlias = Callable[[], T]                # type error: T isn't in scope
# You had to: Thunk[T] = ...
# But T had to be a global TypeVar

# For Result:
Result: TypeAlias = Union[Ok[T], Fail]            # same
```

## A value, not an effect

The core idea: these three aliases _decouple_ **description** from **execution**:

- Create an `Effect`, pass it as an argument → no execution.
- Create a `Thunk[T]`, compose it with others → no execution.
- Create a `Result[T]` inside a function → no exception raised.

Execution happens **explicitly** at specific points:

- `Effect()` to run an effect (the function call).
- `Thunk[T]()` same, returns the value.
- `is_fail(result)` / `is_ok(result)` to discriminate.

This **description / execution separation** is the pillar of lazy evaluation (see [`03-lazy-evaluation.md`](03-lazy-evaluation.md)).
