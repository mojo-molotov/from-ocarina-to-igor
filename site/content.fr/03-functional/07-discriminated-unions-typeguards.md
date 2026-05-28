---
title: "03.07 — Unions discriminées + TypeGuard + @final = unions « sealed »"
description: "Unions discriminées, TypeGuard et final : le combo qui rend Result[T] et TestResult à la fois typés et utilisables sans cast."
weight: 7
date: 2026-05-20
series: ["fonctionnel"]
series_order: 7
tags: ["rop"]
---

# 03.07&nbsp;—&nbsp;Unions discriminées + TypeGuard + @final = unions «&nbsp;_sealed_&nbsp;»

> Le combo qui rend `Result[T]` et `TestResult` à la fois **typés** et **utilisables sans cast**.

## Union discriminée

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

- Deux constructeurs&nbsp;: `Ok[T]` et `Fail`.
- Le _discriminant_ est l'_isinstance check_ (pas un champ comme `tag: Literal["ok", "fail"]`).
- Les deux sont `@final`&nbsp;: _aucun_ sous-type possible.&nbsp;→&nbsp;l'union est **exhaustive**, donc «&nbsp;_sealed_&nbsp;».

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
        return f"Got: {result.value}"          # mypy : result est Ok[int], donc .value existe
    if is_fail(result):
        return f"Error: {result.error}"        # mypy : result est Fail, donc .error existe
    # mypy peut détecter que cette branche est inatteignable (exhaustivité)
```

## `_BaseResult`

```python
class _BaseResult:
    error: Exception | None
```

Cette base permet d'accéder à `result.error` **sans narrower**&nbsp;:

```python
def maybe_log_error(result: Result[int]) -> None:
    if result.error:                            # ok, _BaseResult a "error"
        logger.error(str(result.error))
```

Mais&nbsp;: sans narrowing, on ne peut pas accéder à `result.value` (qui n'existe que sur `Ok`).

## `TestResult = Result[Any] | None`

```python
# src/ocarina/custom_types/oc_test_layers.py
type TestResult = Result[Any] | None
```

Trois cas&nbsp;: `Ok`, `Fail`, `None` (skip). Trois `TypeGuard`&nbsp;:

```python
# src/ocarina/aggregates/tests_layers.py
def is_test_result_ok(result: TestResult) -> TypeGuard[Ok[Any]]:
    return isinstance(result, Ok)

def is_test_result_fail(result: TestResult) -> TypeGuard[Fail]:
    return isinstance(result, Fail)

def is_test_result_skipped(result: TestResult) -> TypeGuard[None]:
    return result is None
```

Dans `pretty_print_results` (extrait)&nbsp;:

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

Chaque branche est typée. `result.error` est `Exception` après `is_test_result_fail`.

## `@final` dans le framework

| Classe                                                                                                                                                                     | Fichier                                                      |
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

**Rien n'est sous-classable dans le DSL**. Toute extension passe par composition (closures, adapters projet, valeurs paramétrées).

Le bénéfice (sécurité de type, exhaustivité, refactor-safety) est immense.

## Le compilateur fait foi

Le Holy Book le dit&nbsp;:

> Ocarina rend son mésusage difficile par conception&nbsp;: le compilateur fait foi.

Ici, «&nbsp;_le compilateur fait foi_&nbsp;» se matérialise dans&nbsp;:

- `Result[T]`
- `TypeGuard`
- `@final`
