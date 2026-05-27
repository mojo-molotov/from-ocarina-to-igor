---
title: "02.03.01 — Le type Result[T]"
description: "Fichier source : src/ocarina/railway/result.py — zéro dépendance."
weight: 1
date: 2026-05-20
series: ["railway"]
series_order: 1
tags: ["ocarina", "rop", "typage"]
---

# 02.03.01&nbsp;—&nbsp;Le type `Result[T]`

> Fichier source&nbsp;: [`src/ocarina/railway/result.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/railway/result.py)&nbsp;—&nbsp;**zéro dépendance**.

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

## Six décisions de design à décortiquer

### 1. `_BaseResult` comme parent commun

```python
class _BaseResult:
    error: Exception | None
```

But unique&nbsp;: permettre à _mypy_ d'**accéder à `result.error` sans narrowing préalable**. Sans cette base, on devrait écrire&nbsp;:

```python
if is_fail(result):
    print(result.error)   # ok, narrowed
```

…systématiquement. Avec la base partagée, on peut écrire dans certains cas&nbsp;:

```python
print(result.error or "no error")
```

…et le checker accepte parce que les deux classes exposent `error`. C'est une concession ergonomique, _pas_ une invitation à contourner le narrowing&nbsp;: la valeur peut être `None` (Ok), donc dans 99% des cas on _veut_ narrower avant d'accéder.

### 2. `@final` partout

`@final` sur `Ok[T]` et `Fail` (et sur `ActionStart`, `ActionChain`, etc. plus loin).

- Pas d'héritage utilisateur&nbsp;—&nbsp;`class MyOk(Ok[T])` est une erreur _mypy_.
- Le _type-checker_ peut traiter `Result[T] = Ok[T] | Fail` comme une union **fermée** («&nbsp;_sealed_&nbsp;»).
- L'exhaustivité du `isinstance` est garantie.

### 3. `@dataclass(frozen=True)`

- **Immutabilité**&nbsp;: `Ok(value=42).value = 43` lève `FrozenInstanceError`.
- Génération automatique de `__init__`, `__repr__`, `__eq__`, `__hash__` (puisque frozen).
- Permet `Ok(42) == Ok(42)`

### 4. `Fail` a un `default_factory`

```python
error: Exception = field(default_factory=lambda: Exception("Unknown error"))
```

Pour pouvoir écrire `Fail()` sans argument.

### 5. `type Result[T] = Ok[T] | Fail` (PEP 695)

Syntaxe **PEP 695** introduite en Python 3.12&nbsp;:

```python
type Result[T] = Ok[T] | Fail
```

Équivalent legacy&nbsp;:

```python
from typing import TypeAlias, TypeVar, Union
T = TypeVar("T")
Result: TypeAlias = Union[Ok[T], Fail]
```

Avantages PEP 695&nbsp;:

- Lisibilité (aucun import).
- Pas de fuite du `T` dans le scope du module.
- Type check plus fin.

### 6. `TypeGuard[Ok[T]]` /&nbsp;`TypeGuard[Fail]`

```python
def is_ok[T](result: Result[T]) -> TypeGuard[Ok[T]]:
    return isinstance(result, Ok)
```

Sans `TypeGuard`&nbsp;:

```python
def is_ok(result): return isinstance(result, Ok)

r = some_action()
if is_ok(r):
    print(r.value)   # mypy ne sait pas que r est Ok[T] → error
```

Avec `TypeGuard[Ok[T]]`, _mypy_ **narrows** `r` à `Ok[T]` dans la branche `True`. C'est la pierre angulaire de l'usage typé du `Result` dans tout le reste du framework. Voir aussi `aggregates/tests_layers.py` qui décline le même pattern pour `TestResult`&nbsp;:

```python
def is_test_result_ok(result: TestResult) -> TypeGuard[Ok[Any]]:    ...
def is_test_result_fail(result: TestResult) -> TypeGuard[Fail]:     ...
def is_test_result_skipped(result: TestResult) -> TypeGuard[None]:  ...
```

## Exemples d'utilisation (extraits du framework)

### Construction directe

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

### Conversion d'une exception en `Fail`

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

Extrait de `create_act`, c'est l'**unique point** où une exception est convertie en `Fail` afin de résoudre ce problème pour tout le reste de l'exécution.

## Tests associés

Le fichier [`tests/scenarios/test_railway_and_action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_railway_and_action_chain.py) ouvre par un test direct sur ces discriminateurs&nbsp;:

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

Et un fichier `tests/dsl/testing_with_railway/test_types.yml` (cf. [`../../04-internal-tests/04-mypy-plugins-types.md`](../../04-internal-tests/04-mypy-plugins-types.md)) teste que `reveal_type(...)` retourne bien `ActionStart[<Page>]` après un `act(...)`. Le typage **est testé**.
