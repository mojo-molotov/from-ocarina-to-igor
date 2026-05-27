---
title: "03.06 — PEP 695 generics in Ocarina"
description: "Ocarina leans hard on the generics syntax from PEP 695 (Python 3.12+). It's what keeps the whole typed ecosystem from being a mess."
weight: 6
date: 2026-05-20
series: ["functional"]
series_order: 6
---

# 03.06&nbsp;—&nbsp;PEP 695 generics in Ocarina

> Ocarina leans hard on the generics syntax from PEP 695 (Python 3.12+). It's what keeps the whole typed ecosystem _from being a mess_.

## Three forms of PEP 695

### 1. Generic classes

```python
@final
class Ok[T](_BaseResult):
    value: T
    error: None = None

class TestSuite[Driver]:
    ...

class Watcher[Driver]:
    ...

class ChainRunner[T]:
    ...

class ValidationStartBlock[T]:
    ...

class CliStore[TKeys: str]:  # with bound
    ...
```

Before PEP 695:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Ok(_BaseResult, Generic[T]):
    value: T
    error: None = None
```

### 2. Parameterized type aliases

```python
type Result[T] = Ok[T] | Fail
type Thunk[T] = Callable[[], T]
type Action[T] = Thunk[Result[T]]
type FailureHandler = Callable[[Exception], None]
type Predicate[T] = Callable[[T], None]
type Effect = Callable[[], None]
type TestScenario[Driver] = Callable[[Driver, ILogger], Scenario[Driver]]
type TestScenarioFragment[Driver] = Callable[[Driver, ILogger], TestChain]
type TestChain = Sequence[ChainRunner[Any]]
type TestWatchers[Driver] = Sequence[Watcher[Driver]] | None
```

Before PEP 695:

```python
from typing import TypeAlias, TypeVar, Callable, Sequence, Union

T = TypeVar("T")
Driver = TypeVar("Driver")

Result: TypeAlias = Union[Ok[T], Fail]    # requires T in module-level scope
Thunk: TypeAlias = Callable[[], T]
```

### 3. Generic functions

```python
def is_ok[T](result: Result[T]) -> TypeGuard[Ok[T]]:
    return isinstance(result, Ok)

def is_fail[T](result: Result[T]) -> TypeGuard[Fail]:
    return isinstance(result, Fail)

def chain_actions[T](first: ActionSuccess[T], *rest: ActionSuccess[T]) -> ChainRunner[T]:
    ...

def field[T](*, validate: ValidationChainBuilder[T]) -> _CliField[T]:
    ...

def bootstrap[T](*, test_cycle: TestCycle[T], ...) -> None:
    ...

def validate[T](value: T, *, name: str | None = None) -> ValidationStartBlock[T]:
    ...
```

Before PEP 695, it was a pain.

## `bound` (constrained TypeVar)

```python
TPOM = TypeVar("TPOM", bound="POMBase")
```

One very specific case where declaring the type with `TypeVar` to `bound` it on another type (like an `extends` on a generic in TypeScript) still earns its keep.

You can also "bound" inline:

```python
class CliStore[TKeys: str]:
    ...
```

`TKeys: str` means "_`TKeys` is a subtype of `str`_" (notion of _covariance_).

## `TypeGuard` (PEP 647)

```python
def is_ok[T](result: Result[T]) -> TypeGuard[Ok[T]]:
    return isinstance(result, Ok)
```

The `TypeGuard[Ok[T]]` tells the checker: "_if this function returns `True`, then `result` has type `Ok[T]` in the True branch_":

```python
result = some_action()
if is_ok(result):
    print(result.value)   # ✅ mypy knows result is Ok[T], so result.value exists
```

Without `TypeGuard`, `result.value` errors&nbsp;—&nbsp;mypy wouldn't know it's an `Ok`.

## `Self` (PEP 673)

```python
class POMBase(ABC):
    @abstractmethod
    def verify(self, *, timeout: float | None = None) -> Self: ...

class HomePage(SeleniumTitleMixin, POMBase):
    def open(self) -> Self:                   # ← Self, not HomePage
        self._driver.get(self._url)
        return self
```

## `Literal` (PEP 586)

```python
type Mode = Literal[
    "fail-fast-on-first-smoke-campaigns-sequence-fail",
    "wait-for-all-smoke-tests",
]

type SeleniumCliStoreKeys = Literal[
    "driver_path", "profile_path", "browser", "headless", "workers",
    "logger", "wait_timeout", "force_delete_tmp_dirs", "only", "exclude",
]

type SupportedSeleniumBrowser = Literal["chrome", "firefox", "edge", "safari"]
type SupportedLogger = Literal["terminal", "file", "terminal+file", "muted"]
```

`Literal[...]` enables:

- **Autocomplete** in the IDE.
- **Refusal** of invalid values at compile time.

## `Protocol` (PEP 544)

```python
class ScreenshotDriver(Protocol):
    def save_screenshot(self, path: str) -> bool:
        ...

class SupportsWrite(Protocol[T_contra]):
    def write(self, s: T_contra, /) -> Any: ...

class ITakeScreenshot[Driver](Protocol):
    def __call__(self, driver: Driver, logger: ILogger, category: str) -> None: ...
```

`Protocol` brings _structural typing_ to Python: any object with the right interface qualifies, no explicit inheritance required. Close to _duck typing_, but statically verified by type checkers. Very handy for mocks, adapters, test fakes.

## `@final` (PEP 591)

```python
@final
class Test[Driver]: ...

@final
class Watcher[Driver]: ...

@final
class ChainRunner[T]: ...

@final
@dataclass(frozen=True)
class Ok[T](_BaseResult): ...

@final
class TestCycle[Driver]: ...
```

`@final` declares the class **cannot be subclassed**.

- The checker rejects `class MyOk(Ok[T])`.
- The checker can treat unions as **sealed**: `Result[T] = Ok[T] | Fail` exhaustively covers two cases (`Ok` and `Fail` are both `@final`).
- The user is forced to **compose** instead of inherit.

## `Never` (PEP 661)

```python
class _SilentArgumentParser(ArgumentParser):
    def error(self, message: str) -> Never:
        raise ValueError(message)
```

`Never` declares that the function **never returns**&nbsp;—&nbsp;either it raises, or it loops forever. The checker can treat the flow _as if_ nothing ever happens after this call.

## `Unpack` (PEP 692)

Used in `ocarina-example`:

```python
# ocarina-example/lib/ext/selenium/humanize/proxy.py
class HumanizedDriver(WebDriver):
    def __init__(
        self, driver: WebDriver, **keyboard_config: Unpack[KeyboardConfig]
    ) -> None:
        ...
```

`KeyboardConfig` is a `TypedDict`. `Unpack[KeyboardConfig]` lets you type `**kwargs` as the TypedDict's keys _without_ forcing them into the signature.

## Consistency with the philosophy

From the Holy Book (chapter "First feedbacks"):

> The recent evolution of Python's _type system_, which Ocarina leans deeply on, is part of the very reason it's feasible at all.

Without PEP 695 + PEP 647 + PEP 673 + PEP 661 + PEP 692 + PEP 544 + PEP 586 + PEP 591, Ocarina's DSL would be **shaky**. Python's typing ecosystem is what makes the DSL **possible**.
