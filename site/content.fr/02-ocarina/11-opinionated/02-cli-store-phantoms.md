---
title: "02.11.02 — CliStore[TKeys] + _CliField[T] + phantom_validate"
weight: 2
date: 2026-05-20
series: ["opinionated"]
series_order: 2
tags: ["ocarina"]
---

# 02.11.02&nbsp;—&nbsp;`CliStore[TKeys]` + `_CliField[T]` + `phantom_validate`

> Fichiers source&nbsp;: [`src/ocarina/opinionated/cli/store.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/store.py), [`src/ocarina/opinionated/cli/phantoms.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/phantoms.py)
>
> Store **write-once** des valeurs CLI parsées. Chaque champ valide à l'écriture. Le `TKeys: Literal[...]` apporte de l'autocomplétion sur les clés.

## `_CliField[T]`&nbsp;—&nbsp;champ write-once

```python
class _CliField[T]:
    def __init__(self, *, validate: ValidationChainBuilder[T]) -> None:
        self._value: T | _Unset = _UNSET
        self._validate = validate

    def set(self, value: T) -> None:
        if not isinstance(self._value, _Unset):
            raise RuntimeError("Value already set.")
        self._validate(_validate(value)).execute().raise_if_invalid()
        self._value = value

    def get(self) -> T:
        if isinstance(self._value, _Unset):
            raise RuntimeError("Value not set yet.")
        return self._value
```

### 1. Sentinel `_Unset`

```python
class _Unset:
    pass

_UNSET = _Unset()
```

Pourquoi pas `None`&nbsp;? Parce que `None` peut être une **valeur légitime** (`--profile-path` n'est pas obligatoire&nbsp;; sa valeur après parse peut légitimement être `None`). Une sentinelle dédiée distingue «&nbsp;_pas encore set_&nbsp;» de «&nbsp;_set à None_&nbsp;».

### 2. Write-once via `isinstance(self._value, _Unset)`

Une fois `set()` appelé, `self._value` est une vraie valeur (pas un `_Unset`). Le `if not isinstance(self._value, _Unset)` retourne `True` au deuxième `set()`&nbsp;→&nbsp;on lève.

C'est le _contrat_&nbsp;: un flag CLI est parsé une fois, point.

### 3. Validation via chaîne d'invariants

```python
self._validate(_validate(value)).execute().raise_if_invalid()
```

## `field(*, validate)`

```python
def field[T](*, validate: ValidationChainBuilder[T]) -> _CliField[T]:
    return _CliField(validate=validate)
```

Sucre syntaxique&nbsp;: on n'expose pas `_CliField` directement, on passe par `field(...)`.

## `CliStore[TKeys: str]`

```python
class CliStore[TKeys: str]:
    def __init__(self, fields: dict[TKeys, _CliField[Any]]) -> None:
        self._fields = fields

    def set(self, k: TKeys, value: Any) -> None:
        self._fields[k].set(value)

    def get(self, k: TKeys):
        return self._fields[k].get()
```

### 1. `TKeys: Literal[...]` pour l'autocomplétion

```python
type SeleniumCliStoreKeys = Literal[
    "driver_path", "profile_path", "browser", "headless", "workers",
    "logger", "wait_timeout", "force_delete_tmp_dirs", "only", "exclude",
]

store = CliStore[SeleniumCliStoreKeys](fields={...})
store.set("workers", 4)        # ✅ autocomplete
store.set("typo_key", 4)       # ❌ mypy error: not assignable to SeleniumCliStoreKeys
```

### 2. Valeur en `Any`

> Values in CliStore are stored and returned as Any. Python has no mapped types.
> There is no value type safety at the CliStore level&nbsp;—&nbsp;the caller is responsible for casting get() results.

Python n'a pas de **mapped types** (à la TypeScript) qui permettraient de dire «&nbsp;_la clé `"workers"` retourne un `int`, la clé `"browser"` retourne un `Literal[...]`_&nbsp;».

Conséquence&nbsp;: `store.get("workers")` retourne `Any`.  
Le caller doit caster&nbsp;:

```python
def get_max_workers() -> int:
    return cast(int, CliStoreSingleton().get("workers"))
```

```python
def get_max_workers() -> int:
    max_workers: int = CliStoreSingleton().get("workers")
    return max_workers
```

C'est un compromis. Le bénéfice (autocomplétion des clés) prime sur le coût (cast manuel).

## `phantom_validate`

```python
def _phantom_assertion(_: Any) -> None:
    """No-op predicate — always passes without any check."""


def phantom_validate(chain: ValidationStartBlock[Any]):
    return chain.assert_that(_phantom_assertion)
```

Pourquoi cette aberration apparente&nbsp;?

Parce que **`field()` exige un `validate=` non-optionnel**, mais certains champs n'ont pas besoin de validation supplémentaire, par exemple les booléens (`headless`), les choix énumérés (`browser` déjà validé par argparse), ou les listes (`only`).

`phantom_validate` est le _no-op_ qui satisfait la signature sans rien faire.

```python
"browser": field(validate=phantom_validate),
"headless": field(validate=phantom_validate),
"logger": field(validate=phantom_validate),
"only": field(validate=phantom_validate),
"exclude": field(validate=phantom_validate),
"force_delete_tmp_dirs": field(validate=phantom_validate),
```

vs champs avec validation _réelle_&nbsp;:

```python
"workers": field(
    validate=lambda chain: chain.assert_that(is_positive, msg="--workers should be a positive value")
                                .assert_that(is_not_zero, msg="--workers should not be zero")
),
"wait_timeout": field(
    validate=lambda chain: (
        chain.assert_that(is_less_than_or_equal_to(60), msg="--wait-timeout maximum is: 60")
             .assert_that(is_positive, msg="--wait-timeout should be a positive value")
             .assert_that(is_not_zero, msg="--wait-timeout should not be zero")
    )
),
```

## `CliStoreSingleton`

```python
# src/ocarina/opinionated/cli/selenium/cli_store_singleton.py
class SeleniumCliStoreSingleton:
    ...
```

Wrapper singleton autour de `CliStore[SeleniumCliStoreKeys]`. Permet à n'importe quel module du projet de faire `CliStoreSingleton().get("workers")` sans avoir à propager le store par paramètre.

Pattern&nbsp;: `CliStoreSingleton().push(create_selenium_auto_cli_store())` est appelé une seule fois dans `main.py`. Tous les modules qui ont besoin d'une valeur CLI utilisent `CliStoreSingleton().get(...)`.

Convention notée dans le `CLAUDE.md` du projet IA&nbsp;:

> **Opinionated CLI keys.** Never rename keys read from `SeleniumCliStoreSingleton` (it's `"workers"`, not `"max_workers"`).
