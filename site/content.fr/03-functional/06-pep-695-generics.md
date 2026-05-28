---
title: "03.06 — Generics PEP 695 dans Ocarina"
description: "Les generics PEP 695 dans Ocarina : classes, fonctions et alias de types paramétrés qui rendent tout l'écosystème typé sans lourdeur."
weight: 6
date: 2026-05-20
series: ["fonctionnel"]
series_order: 6
---

# 03.06&nbsp;—&nbsp;Generics PEP 695 dans Ocarina

> Ocarina exploite à fond la syntaxe générique introduite par PEP 695 (Python 3.12+). C'est ce qui rend tout l'écosystème typé _sans que ce soit le foutoir_.

## Trois formes de PEP 695

### 1. Classes génériques

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

class CliStore[TKeys: str]:  # avec bound
    ...
```

Avant PEP 695&nbsp;:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Ok(_BaseResult, Generic[T]):
    value: T
    error: None = None
```

### 2. Type aliases paramétrés

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

Avant PEP 695&nbsp;:

```python
from typing import TypeAlias, TypeVar, Callable, Sequence, Union

T = TypeVar("T")
Driver = TypeVar("Driver")

Result: TypeAlias = Union[Ok[T], Fail]    # nécessite T en scope module-level
Thunk: TypeAlias = Callable[[], T]
```

### 3. Fonctions génériques

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

Avant PEP 695, c'était plus relou.

## `bound` (TypeVar contraint)

```python
TPOM = TypeVar("TPOM", bound="POMBase")
```

Il reste quand même un cas très précis où déclarer le type avec `TypeVar` afin de `bound` sur un autre type (comme un `extends` sur un type générique en TypeScript par exemple) reste utile.

On peut aussi "bound" de cette manière, c'est selon&nbsp;:

```python
class CliStore[TKeys: str]:
    ...
```

Ici `TKeys: str` veut dire «&nbsp;_`TKeys` est un sous-type de `str`_&nbsp;» (notion de _covariance_).

## `TypeGuard` (PEP 647)

```python
def is_ok[T](result: Result[T]) -> TypeGuard[Ok[T]]:
    return isinstance(result, Ok)
```

Le `TypeGuard[Ok[T]]` annonce au checker&nbsp;: «&nbsp;_si cette fonction retourne `True`, alors `result` est de type `Ok[T]` dans la branche True_&nbsp;»&nbsp;:

```python
result = some_action()
if is_ok(result):
    print(result.value)   # ✅ mypy sait que result est Ok[T], donc result.value existe
```

Sans `TypeGuard`, `result.value` serait une erreur (mypy ne saurait pas que c'est un `Ok`).

## `Self` (PEP 673)

```python
class POMBase(ABC):
    @abstractmethod
    def verify(self, *, timeout: float | None = None) -> Self: ...

class HomePage(SeleniumTitleMixin, POMBase):
    def open(self) -> Self:                   # ← Self, pas HomePage
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

Le `Literal[...]` permet&nbsp;:

- L'**autocomplétion** dans l'IDE.
- Le **refus** de valeurs invalides à la compilation.

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

Les `Protocol` introduisent du _structural typing_ en Python&nbsp;: tout objet ayant la bonne interface est accepté, sans héritage explicite. C’est proche du _duck typing_, mais vérifié statiquement par les outils de type checking. Très pratique pour les mocks, adapters et fakes de tests.

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

`@final` annonce que la classe **ne peut pas être sous-classée**.

- Le checker refuse `class MyOk(Ok[T])`.
- Le checker peut traiter les unions comme **sealed**&nbsp;: `Result[T] = Ok[T] | Fail` est exhaustivement deux cas (puisque `Ok` est `@final` et `Fail` est `@final`).
- L'utilisateur est forcé à **composer** plutôt qu'à hériter.

## `Never` (PEP 661)

```python
class _SilentArgumentParser(ArgumentParser):
    def error(self, message: str) -> Never:
        raise ValueError(message)
```

`Never` annonce que la fonction **ne retourne jamais**, soit parce qu'elle lève directement, soit parce qu'elle entre dans une boucle infinie. Le checker peut traiter le flux _comme si_ on n'arrivait jamais après cet appel.

## `Unpack` (PEP 692)

Utilisé dans `ocarina-example`&nbsp;:

```python
# ocarina-example/lib/ext/selenium/humanize/proxy.py
class HumanizedDriver(WebDriver):
    def __init__(
        self, driver: WebDriver, **keyboard_config: Unpack[KeyboardConfig]
    ) -> None:
        ...
```

`KeyboardConfig` est un `TypedDict`. `Unpack[KeyboardConfig]` permet de typer les `**kwargs` comme étant les clés du TypedDict, _sans_ pour autant les forcer dans la signature.

## La cohérence avec la philosophie

Tiré du Holy Book (chapitre «&nbsp;_Premiers retours_&nbsp;»)&nbsp;:

> Les récentes évolutions du _système de types_ de Python, sur lequel Ocarina s'appuie profondément, font partie de la raison-même de sa faisabilité.

Sans PEP 695 + PEP 647 + PEP 673 + PEP 661 + PEP 692 + PEP 544 + PEP 586 + PEP 591, le DSL d'Ocarina serait **bancal**. L'écosystème de typage Python rend le DSL **possible**.
