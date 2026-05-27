---
title: "02.11.02 — CliStore[TKeys] + _CliField[T] + phantom_validate"
weight: 2
date: 2026-05-20
series: ["opinionated"]
series_order: 2
tags: ["ocarina"]
---

# 02.11.02&nbsp;—&nbsp;`CliStore[TKeys]` + `_CliField[T]` + `phantom_validate`

> Source files: [`src/ocarina/opinionated/cli/store.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/store.py), [`src/ocarina/opinionated/cli/phantoms.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/phantoms.py)
>
> **Write-once** store for parsed CLI values. Each field validates on write. `TKeys: Literal[...]` gives key autocomplete.

## `_CliField[T]`&nbsp;—&nbsp;write-once field

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

### 1. `_Unset` sentinel

```python
class _Unset:
    pass

_UNSET = _Unset()
```

Why not `None`? Because `None` can be a **legitimate value** (`--profile-path` isn't mandatory; its post-parse value can legitimately be `None`). A dedicated sentinel separates "_not set yet_" from "_set to None_".

### 2. Write-once via `isinstance(self._value, _Unset)`

Once `set()` is called, `self._value` holds a real value (not `_Unset`). On the second `set()`, `if not isinstance(self._value, _Unset)` returns `True` → we raise.

The _contract_: a CLI flag is parsed once, period.

### 3. Validation via invariants chain

```python
self._validate(_validate(value)).execute().raise_if_invalid()
```

## `field(*, validate)`

```python
def field[T](*, validate: ValidationChainBuilder[T]) -> _CliField[T]:
    return _CliField(validate=validate)
```

Syntactic sugar: we don't expose `_CliField` directly, callers go through `field(...)`.

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

### 1. `TKeys: Literal[...]` for autocomplete

```python
type SeleniumCliStoreKeys = Literal[
    "driver_path", "profile_path", "browser", "headless", "workers",
    "logger", "wait_timeout", "force_delete_tmp_dirs", "only", "exclude",
]

store = CliStore[SeleniumCliStoreKeys](fields={...})
store.set("workers", 4)        # ✅ autocomplete
store.set("typo_key", 4)       # ❌ mypy error: not assignable to SeleniumCliStoreKeys
```

### 2. Value as `Any`

> Values in CliStore are stored and returned as Any. Python has no mapped types.
> There is no value type safety at the CliStore level&nbsp;—&nbsp;the caller is responsible for casting get() results.

Python has no **mapped types** (à la TypeScript) to say "_`"workers"` returns `int`, `"browser"` returns `Literal[...]`_".

Net: `store.get("workers")` returns `Any`.  
The caller has to cast:

```python
def get_max_workers() -> int:
    return cast(int, CliStoreSingleton().get("workers"))
```

```python
def get_max_workers() -> int:
    max_workers: int = CliStoreSingleton().get("workers")
    return max_workers
```

A trade-off. The benefit (key autocomplete) beats the cost (manual cast).

## `phantom_validate`

```python
def _phantom_assertion(_: Any) -> None:
    """No-op predicate — always passes without any check."""


def phantom_validate(chain: ValidationStartBlock[Any]):
    return chain.assert_that(_phantom_assertion)
```

Why this apparent absurdity?

Because **`field()` requires a non-optional `validate=`**, but some fields need no extra validation&nbsp;—&nbsp;booleans (`headless`), enumerated choices (`browser`, already validated by argparse), lists (`only`).

`phantom_validate` is the _no-op_ that satisfies the signature without doing a thing.

```python
"browser": field(validate=phantom_validate),
"headless": field(validate=phantom_validate),
"logger": field(validate=phantom_validate),
"only": field(validate=phantom_validate),
"exclude": field(validate=phantom_validate),
"force_delete_tmp_dirs": field(validate=phantom_validate),
```

vs fields with _actual_ validation:

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

Singleton wrapper around `CliStore[SeleniumCliStoreKeys]`. Any module in the project can call `CliStoreSingleton().get("workers")` without threading the store through as a parameter.

Pattern: `CliStoreSingleton().push(create_selenium_auto_cli_store())` is called exactly once in `main.py`. Any module that needs a CLI value uses `CliStoreSingleton().get(...)`.

Convention noted in the AI project's `CLAUDE.md`:

> **Opinionated CLI keys.** Never rename keys read from `SeleniumCliStoreSingleton` (it's `"workers"`, not `"max_workers"`).
