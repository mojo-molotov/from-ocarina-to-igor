---
title: "07.10 — EnvGetters"
description: "EnvGetters: ocarina-example's typed access to environment variables, rejecting unknown keys and providing autocompletion."
weight: 10
date: 2026-05-20
series: ["ocarina-example"]
series_order: 10
---

# 07.10&nbsp;—&nbsp;`EnvGetters`

> **Typed** accessor for environment variables. Avoids typos, refuses unknown keys at compile time, brings IDE autocomplete.

## Code

```python
# src/lib/ext/ocarina/adapters/agnostic/env_getters.py
from typing import Literal
from types import MappingProxyType
from ocarina.opinionated.infra.env import EnvGetters, Effects

type _CredsKeys = Literal["dashboard"]
type _ValuesKeys = Literal["igor_api_key", "redis_url"]


def _load_env() -> None:
    from dotenv import load_dotenv
    load_dotenv()


_DEFAULT_EFFECTS = (_load_env,)


class _EnvGetters(EnvGetters[_CredsKeys, _ValuesKeys]):
    def __init__(self, *, effects: Effects) -> None:
        for effect in effects:
            effect()
        super().__init__(
            credentials={
                "dashboard": MappingProxyType({
                    "login": os.environ["DASH_USERNAME"],
                    "password": os.environ["DASH_PASSWORD"],
                }),
            },
            values={
                "igor_api_key": os.environ["IGOR_API_KEY"],
                "redis_url": os.environ["REDIS_URL"],
            },
        )


def create_env_getters(*, effects: Effects | None = None) -> _EnvGetters:
    if effects is None:
        effects = _DEFAULT_EFFECTS
    return _EnvGetters(effects=effects)
```

## `_CredsKeys` and `_ValuesKeys`

```python
type _CredsKeys = Literal["dashboard"]
type _ValuesKeys = Literal["igor_api_key", "redis_url"]
```

1. **Credentials**: login/password pairs (immutable dict via `MappingProxyType`).
2. **Values**: raw values.

## `MappingProxyType`

```python
"dashboard": MappingProxyType({
    "login": os.environ["DASH_USERNAME"],
    "password": os.environ["DASH_PASSWORD"],
}),
```

`MappingProxyType` is a read-only wrapper around a dict:

```python
creds = env.get_credentials("dashboard")
creds["password"] = "N A P O L E O N  D I S A P P R O V E S"     # ❌ TypeError: 'mappingproxy' object does not support item assignment
```

Immutability enforced. Credentials can't be modified by accident.

## `Effects`

```python
_DEFAULT_EFFECTS = (_load_env,)


def create_env_getters(*, effects: Effects | None = None) -> _EnvGetters:
    if effects is None:
        effects = _DEFAULT_EFFECTS
    return _EnvGetters(effects=effects)
```

`Effects` is a `tuple[Effect, ...]`. Default: `(_load_env,)` → calls `load_dotenv()`.

Override as needed:

```python
# For tests: don't read .env
env = create_env_getters(effects=())  # zero effects
```

or:

```python
# Add an extra effect before load
env = create_env_getters(effects=(_load_secrets_from_vault, _load_env))
```

## On the scenario side

```python
env = create_env_getters()
api_key = env.get_value("igor_api_key")
creds = env.get_credentials("dashboard")
username = creds["login"]
password = creds["password"]
```

## Type safety

```python
env.get_value("typo_key")
# error: Argument 1 to "get_value" of "EnvGetters" has incompatible type "Literal['typo_key']";
#   expected "Literal['igor_api_key', 'redis_url']"

env.get_credentials("unknown")
# error: Argument 1 to "get_credentials" of "EnvGetters" has incompatible type "Literal['unknown']";
#   expected "Literal['dashboard']"
```

The type checker refuses typos&nbsp;—&nbsp;**at compile time**, not runtime.

## Holy Book reminder

```python
type _CredsKeys = Literal["dashboard"]
type _ValuesKeys = Literal["igor_xxx_key", "xxxxx_url"]
```

> **Note:** Valid keys are provided through two types: `EnvGetters[_CredsKeys, _ValuesKeys]`. If the user only wants to use `.get_value()`, it is enough to type `_CredsKeys` as `Never`. The same applies to `_ValuesKeys`, which should be typed as `Never` if the user only wants to use `.get_credentials()`.

So:

```python
type _CredsKeys = Never                          # → no get_credentials
type _ValuesKeys = Literal["api_key"]

class MyEnvGetters(EnvGetters[_CredsKeys, _ValuesKeys]): ...
```

`Never` is an empty type union&nbsp;—&nbsp;`env.get_credentials` becomes uncallable.

## Credentials

```python
credentials={
    "dashboard": MappingProxyType({
        "login": os.environ["DASH_USERNAME"],          # defaults to "SacredFigatellu"
        "password": os.environ["DASH_PASSWORD"],       # defaults to "figatellu"
    }),
}
```

`DASH_USERNAME` and `DASH_PASSWORD` are defined in `.env` (or CI env).  
Here, read in the `_EnvGetters` _constructor_.

## `ImmutableCredentialsKeys`

On the `EnvGetters` side (see `ocarina.opinionated.infra.env`):

```python
type ImmutableCredentialsKeys = Literal["login", "password"]
type ImmutableCredentials = MappingProxyType[ImmutableCredentialsKeys, str]
```

Credentials keys are always `"login"` and `"password"`.

1. `creds["login"]` types as `str`.
2. `creds["foo"]` is a mypy error.

## `os.environ[...]`

```python
"login": os.environ["DASH_USERNAME"],
```

Undefined variable → `KeyError` at runtime, in the `_EnvGetters` constructor&nbsp;—&nbsp;i.e. on the first call to `create_env_getters()`.

You can warm this up in `main.py` by calling `create_env_getters()` before bootstrapping, to surface the error as early as possible.
