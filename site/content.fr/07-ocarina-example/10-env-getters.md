---
title: "07.10 — EnvGetters"
description: "Accesseur typé aux variables d'environnement. Évite les typos, autocomplète dans l'IDE, refuse les clés inconnues à la compilation."
weight: 10
date: 2026-05-20
series: ["ocarina-example"]
series_order: 10
---

# 07.10&nbsp;—&nbsp;`EnvGetters`

> Accesseur **typé** aux variables d'environnement. Évite les typos, refuse les clés inconnues à la compilation, apporte l'autocomplétion dans l'IDE.

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

## `_CredsKeys` et `_ValuesKeys`

```python
type _CredsKeys = Literal["dashboard"]
type _ValuesKeys = Literal["igor_api_key", "redis_url"]
```

1. **Credentials**&nbsp;: paires login/password (dict immutable via `MappingProxyType`).
2. **Values**&nbsp;: valeurs brutes.

## `MappingProxyType`

```python
"dashboard": MappingProxyType({
    "login": os.environ["DASH_USERNAME"],
    "password": os.environ["DASH_PASSWORD"],
}),
```

`MappingProxyType` est un wrapper read-only autour d'un dict&nbsp;:

```python
creds = env.get_credentials("dashboard")
creds["password"] = "N A P O L E O N  D I S A P P R O V E S"     # ❌ TypeError: 'mappingproxy' object does not support item assignment
```

Discipline d'immutabilité.  
Les credentials ne peuvent pas être modifiés _accidentellement_.

## `Effects`

```python
_DEFAULT_EFFECTS = (_load_env,)


def create_env_getters(*, effects: Effects | None = None) -> _EnvGetters:
    if effects is None:
        effects = _DEFAULT_EFFECTS
    return _EnvGetters(effects=effects)
```

`Effects` est un `tuple[Effect, ...]`.  
Ici, par défaut&nbsp;: `(_load_env,)` qui appelle `load_dotenv()`.

Ici, l'utilisateur peut _overrider_&nbsp;:

```python
# Pour les tests : ne pas lire .env
env = create_env_getters(effects=())  # zero effects
```

ou&nbsp;:

```python
# Ajouter un effet supplémentaire avant load
env = create_env_getters(effects=(_load_secrets_from_vault, _load_env))
```

## Côté scénario

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

env.get_credentials("inconnu")
# error: Argument 1 to "get_credentials" of "EnvGetters" has incompatible type "Literal['inconnu']";
#   expected "Literal['dashboard']"
```

Le checker refuse les typos.  
**Dès le compile-time**, pas au runtime (_tests statiques_).

## Rappel du Holy Book

```python
type _CredsKeys = Literal["dashboard"]
type _ValuesKeys = Literal["igor_xxx_key", "xxxxx_url"]
```

> Les clés valides sont à fournir à travers deux types tel que&nbsp;: `EnvGetters[_CredsKeys, _ValuesKeys]`. Dans le cas où l'utilisateur ne souhaite utiliser QUE la fonctionnalité `.get_value()`, il suffit de typer `_CredsKeys` tel que&nbsp;: `Never`. Il en va de même pour `_ValuesKeys` à typer en tant que `Never` si l'utilisateur ne souhaite utiliser QUE la fonctionnalité `.get_credentials()`.

Donc&nbsp;:

```python
type _CredsKeys = Never                          # → pas de get_credentials
type _ValuesKeys = Literal["api_key"]

class MyEnvGetters(EnvGetters[_CredsKeys, _ValuesKeys]): ...
```

`Never` représente une _union de types_ vide, donc aucune possibilité d'utilisation de `env.get_credentials` ici.

## Credentials

```python
credentials={
    "dashboard": MappingProxyType({
        "login": os.environ["DASH_USERNAME"],          # par défaut "SacredFigatellu"
        "password": os.environ["DASH_PASSWORD"],       # par défaut "figatellu"
    }),
}
```

`DASH_USERNAME` et `DASH_PASSWORD` sont définis dans `.env` (ou env CI).  
Ici, lus _au constructeur_ du `_EnvGetters`.

## `ImmutableCredentialsKeys`

Côté `EnvGetters` (cf. `ocarina.opinionated.infra.env`)&nbsp;:

```python
type ImmutableCredentialsKeys = Literal["login", "password"]
type ImmutableCredentials = MappingProxyType[ImmutableCredentialsKeys, str]
```

→ Les clés des _credentials_ sont obligatoirement `"login"` et `"password"`.

1. `creds["login"]` est typé `str`.
2. `creds["foo"]` est une erreur _mypy_.

## `os.environ[...]`

```python
"login": os.environ["DASH_USERNAME"],
```

Si la variable n'est pas définie&nbsp;: `KeyError`.  
**Ici, au runtime** au constructeur du `_EnvGetters` (donc dès le premier appel à `create_env_getters()`).

_Il est envisageable de faire un "warmup" dans `main.py` pour faire remonter l'erreur au plus tôt&nbsp;: il suffit d'appeler `create_env_getters()` au lancement du programme avant de le bootstrapper._
