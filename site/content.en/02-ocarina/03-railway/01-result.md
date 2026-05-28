---
title: "02.03.01 — The Result[T] type"
description: "The Result[T] = Ok[T] or Fail type at Ocarina's core: a zero-dependency discriminated union, with is_ok and is_fail for narrowing."
weight: 1
date: 2026-05-20
series: ["railway"]
series_order: 1
tags: ["ocarina", "rop", "typing"]
---

# 02.03.01&nbsp;—&nbsp;The `Result[T]` type

> Source file: [`src/ocarina/railway/result.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/railway/result.py)&nbsp;—&nbsp;**zero dependencies**.

## Code

```python
from dataclasses import dataclass, field
from typing import TypeGuard, final


class _BaseResult:
    """Base class ensuring both Ok and Fail have error attribute for type narrowing."""
    error: Exception | None


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


def is_ok[T](result: Result[T]) -> TypeGuard[Ok[T]]:
    return isinstance(result, Ok)


def is_fail[T](result: Result[T]) -> TypeGuard[Fail]:
    return isinstance(result, Fail)
```

## Six design decisions, dissected

### 1. `_BaseResult` as a common parent

```python
class _BaseResult:
    error: Exception | None
```

One job: let _mypy_ **read `result.error` without narrowing first**. Without the base, you'd have to write:

```python
if is_fail(result):
    print(result.error)   # ok, narrowed
```

…every single time. With the shared base, you can sometimes go:

```python
print(result.error or "no error")
```

…and the checker waves it through because both classes expose `error`. Ergonomic shortcut, _not_ a license to skip narrowing&nbsp;—&nbsp;the value can be `None` (Ok), so 99% of the time you _should_ narrow first.

### 2. `@final` everywhere

`@final` on `Ok[T]` and `Fail` (and on `ActionStart`, `ActionChain`, etc. down the line).

- No user inheritance&nbsp;—&nbsp;`class MyOk(Ok[T])` is a _mypy_ error.
- The _type-checker_ treats `Result[T] = Ok[T] | Fail` as a **closed** ("sealed") union.
- `isinstance` exhaustiveness is locked in.

### 3. `@dataclass(frozen=True)`

- **Immutable**: `Ok(value=42).value = 43` raises `FrozenInstanceError`.
- Auto-generates `__init__`, `__repr__`, `__eq__`, `__hash__` (frozen).
- `Ok(42) == Ok(42)` just works.

### 4. `Fail` has a `default_factory`

```python
error: Exception = field(default_factory=lambda: Exception("Unknown error"))
```

So `Fail()` works with no arguments.

### 5. `type Result[T] = Ok[T] | Fail` (PEP 695)

**PEP 695** syntax, introduced in Python 3.12:

```python
type Result[T] = Ok[T] | Fail
```

Legacy equivalent:

```python
from typing import TypeAlias, TypeVar, Union
T = TypeVar("T")
Result: TypeAlias = Union[Ok[T], Fail]
```

PEP 695 wins:

- Readable, no import.
- `T` doesn't leak into module scope.
- Sharper type-checking.

### 6. `TypeGuard[Ok[T]]` / `TypeGuard[Fail]`

```python
def is_ok[T](result: Result[T]) -> TypeGuard[Ok[T]]:
    return isinstance(result, Ok)
```

Without `TypeGuard`:

```python
def is_ok(result): return isinstance(result, Ok)

r = some_action()
if is_ok(r):
    print(r.value)   # mypy doesn't know r is Ok[T] → error
```

With `TypeGuard[Ok[T]]`, _mypy_ **narrows** `r` to `Ok[T]` inside the `True` branch. This is the bedrock for typed `Result` usage everywhere else in the framework. `aggregates/tests_layers.py` mirrors the pattern for `TestResult`:

```python
def is_test_result_ok(result: TestResult) -> TypeGuard[Ok[Any]]:    ...
def is_test_result_fail(result: TestResult) -> TypeGuard[Fail]:     ...
def is_test_result_skipped(result: TestResult) -> TypeGuard[None]:  ...
```

## Usage examples (from the framework)

### Direct construction

```python
return Ok(value=42)
return Fail(error=RuntimeError("nope"))
return Fail()  # error = Exception("Unknown error")
```

### Discrimination

```python
result = run_action()
if is_fail(result):
    failure_handler(result.error)
    return ActionChain(has_failed=True, result=result)
success_handler()
return ActionChain(has_failed=False, result=result)
```

### Converting an exception into `Fail`

```python
def run_action() -> Result[TPOM]:
    try:
        result_pom = action(pom)
        return Ok(result_pom)
    except Exception as exc:  # noqa: BLE001
        if on_failure:
            return on_failure(pom, exc)
        return Fail(error=exc)
```

Excerpt from `create_act`. This is the **only place** that turns an exception into a `Fail`. Past this point, nothing else has to repeat that conversion.

## Related tests

[`tests/scenarios/test_railway_and_action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_railway_and_action_chain.py) opens with a direct hit on these discriminators:

```python
@allure.title("is_ok and is_fail discriminate Ok from Fail")
def test_result_discriminators_split_ok_and_fail() -> None:
    ok: Ok[int] = Ok(value=42)
    fail = Fail(error=RuntimeError("x"))

    assert is_ok(ok)
    assert not is_fail(ok)
    assert is_fail(fail)
    assert not is_ok(fail)
```

And `tests/dsl/testing_with_railway/test_types.yml` (see [`../../04-internal-tests/04-mypy-plugins-types.md`](../../04-internal-tests/04-mypy-plugins-types.md)) confirms `reveal_type(...)` returns `ActionStart[<Page>]` after an `act(...)`. The typing **is tested**.
