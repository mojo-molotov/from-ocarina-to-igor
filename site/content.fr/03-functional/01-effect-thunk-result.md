---
title: "03.01 — Effect, Thunk[T], Result[T]"
description: "Effect, Thunk[T] et Result[T] : les quelques lignes de types sur lesquelles repose tout le DSL fonctionnel d'Ocarina."
weight: 1
date: 2026-05-20
series: ["fonctionnel"]
series_order: 1
tags: ["rop"]
---

# 03.01&nbsp;—&nbsp;`Effect`, `Thunk[T]`, `Result[T]`

> Trois lignes de code dans `custom_types/` + une dans `railway/`. Tout le DSL repose dessus.

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

| Type        | Sémantique FP                     | Définition                        |
| ----------- | --------------------------------- | --------------------------------- |
| `Effect`    | Effet de bord (déféré)            | `() -> None`                      |
| `Thunk[T]`  | _Computation_ déférée avec valeur | `() -> T` (paresse + valeur)      |
| `Result[T]` | _Computation_ qui peut échouer    | Union discriminée `Ok[T] \| Fail` |

## Distinction Effect vs Thunk

```python
log_msg: Effect = lambda: print("hello")        # () -> None
get_42: Thunk[int] = lambda: 42                 # () -> int
fetch:  Thunk[Result[int]] = lambda: Ok(42)     # () -> Result[int]
```

Si la fonction _retourne_ quelque chose qu'on va consommer ailleurs&nbsp;→&nbsp;`Thunk[T]`.  
Sinon&nbsp;→&nbsp;`Effect`.

## `Effect`

| Usage                                                         | Endroit                                                                       |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `Scenario.setup` /&nbsp;`Scenario.teardown`                   | `custom_types/scenario.py`                                                    |
| `dispose` de `BuiltWebDriver[Driver] = tuple[Driver, Effect]` | `custom_types/built_web_driver.py`                                            |
| `act_counter_effect`, `on_run_effect` dans `create_act`       | `dsl/testing_with_railway/constructors/create_act.py`                         |
| Effects du CLI (`effects_factory` de `CliBuilder`)            | `opinionated/cli/builder.py`                                                  |
| `SuccHandler` (success handler de `act`)                      | `dsl/testing_with_railway/internals/action_chain.py` (`SuccHandler = Effect`) |
| Plugins de `bootstrap` (chaque plugin est un `Effect`)        | `opinionated/launcher/bootstrap.py`                                           |

## `Thunk[T]`

| Usage                                                               | Endroit                                              |
| ------------------------------------------------------------------- | ---------------------------------------------------- |
| `Thunk[Result[T]] = Action[T]` (le _thunk_ d'une action ROP)        | `dsl/testing_with_railway/internals/action_chain.py` |
| `Thunk[ActionChain[T]]` dans `ChainRunner`                          | `dsl/testing_with_railway/chain_actions.py`          |
| `Thunk[bool]` pour les `when` conditions de `match_page`            | `dsl/testing_with_railway/match_page.py`             |
| `Thunk[str]` pour `logger.set_prefix(prefix_thunk)`                 | `ports/ilogger.py`                                   |
| `Thunk[ILogger]` pour les factories de logger                       | `dsl/testing/oc_test_suite.py`, etc.                 |
| `Thunk[bool]` dans le `dispatch` du `TestCycle` (sélection de mode) | `dsl/testing/oc_test_cycle.py`                       |

## `Result[T]`

| Usage                                                       | Endroit                                               |
| ----------------------------------------------------------- | ----------------------------------------------------- |
| Retour de `create_act` (via `Action[T] = Thunk[Result[T]]`) | `dsl/testing_with_railway/constructors/create_act.py` |
| Résultat d'une `ActionChain`                                | `dsl/testing_with_railway/internals/action_chain.py`  |
| `TestResult = Result[Any] \| None`                          | `custom_types/oc_test_layers.py`                      |

## Centralisation

Si on n'avait pas ces alias, chaque signature qui prend un effet écrirait `Callable[[], None]`&nbsp;: plus de bruit visuel, plus difficile à grepper, plus difficile à refactor.

Avec les alias&nbsp;:

```python
def run_plugins(*plugins: Effect, exceptions_logger: ILogger) -> None: ...
def setup_fn() -> Effect: return lambda: seed_db()
def factory(...) -> tuple[Effect, ...]: ...
```

## La PEP 695 pour ces alias

```python
type Effect = Callable[[], None]                  # PEP 695 (Python 3.12+)
type Thunk[T] = Callable[[], T]                   # PEP 695 (paramétré)
type Result[T] = Ok[T] | Fail                     # PEP 695 (paramétré + union)
```

Avant PEP 695&nbsp;:

```python
from typing import TypeAlias, TypeVar, Callable, Union

Effect: TypeAlias = Callable[[], None]

T = TypeVar("T")
Thunk: TypeAlias = Callable[[], T]                # type erreur : T n'est pas dans le scope
# Il fallait : Thunk[T] = ...
# Mais T devait être TypeVar global

# Pour Result :
Result: TypeAlias = Union[Ok[T], Fail]            # idem
```

## Une valeur, pas un effet

L'idée centrale&nbsp;: ces trois alias _déconnectent_ la **description** de l'**exécution**&nbsp;:

- Créer un `Effect` et le passer en argument&nbsp;→&nbsp;pas d'exécution.
- Créer un `Thunk[T]` et le composer avec d'autres&nbsp;→&nbsp;pas d'exécution.
- Créer un `Result[T]` au sein d'une fonction&nbsp;→&nbsp;pas de levée d'exception.

L'exécution arrive **explicitement** à des points précis&nbsp;:

- `Effect()` pour exécuter un effet (l'appel à la fonction).
- `Thunk[T]()` idem mais retourne la valeur.
- `is_fail(result)` /&nbsp;`is_ok(result)` pour discriminer.

Cette **séparation description /&nbsp;exécution** est le pilier de l'évaluation paresseuse (cf. [`03-lazy-evaluation.md`](03-lazy-evaluation.md)).
