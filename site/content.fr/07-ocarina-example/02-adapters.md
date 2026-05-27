---
title: "07.02 — Les 5 adapters"
description: "Tout projet Ocarina commence par écrire cinq adapters au-dessus du framework. Le projet ocarina-example les fournit en référence."
weight: 2
date: 2026-05-20
series: ["ocarina-example"]
series_order: 2
---

# 07.02&nbsp;—&nbsp;Les 5 adapters

> Tout projet Ocarina commence par écrire **cinq** adapters au-dessus du framework.  
> Le projet `ocarina-example` les fournit en référence.

## Listing

| Adapter        | Statut     | Fichier                                              | But                                                                |
| -------------- | ---------- | ---------------------------------------------------- | ------------------------------------------------------------------ |
| `act`          | requis     | `lib/ext/ocarina/adapters/agnostic/act.py`           | Hook `on_failure` spécifique au projet                             |
| `match_page`   | facultatif | `lib/ext/ocarina/adapters/agnostic/match_page.py`    | Politique d'exceptions partagée                                    |
| `EnvGetters`   | facultatif | `lib/ext/ocarina/adapters/agnostic/env_getters.py`   | Accès typé aux env vars                                            |
| `TestSuite`    | requis     | `lib/ext/ocarina/adapters/selenium/test_suite.py`    | Façade&nbsp;: fige `transient_errors`, `max_retries`, `autoscreen` |
| `TestCampaign` | requis     | `lib/ext/ocarina/adapters/selenium/test_campaign.py` | Façade&nbsp;: `max_workers` depuis CLI                             |

## `act`

```python
# lib/ext/ocarina/adapters/agnostic/act.py
from contextlib import suppress
from ocarina.dsl.testing_with_railway.constructors.create_act import create_act
from ocarina.railway.result import Fail
from lib.custom_errors.http import HttpErrorPageReachedError
from lib.ext.ocarina.regex.error_page import ERROR_PAGE_REGEX


def act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]:
    def failure_hook(pom: TPOM, exc: Exception) -> Fail:
        with suppress(Exception):
            title = pom.get_current_title()
            is_http_error_page = title and ERROR_PAGE_REGEX.match(title.strip())
            if is_http_error_page:
                http_error = HttpErrorPageReachedError(f"HTTP error page: {title}")
                http_error.__cause__ = exc
                return Fail(error=http_error)
        return Fail(error=exc)

    return create_act(pom, action, on_failure=failure_hook)
```

1. **`get_current_title()`**&nbsp;: utilise la méthode obligatoire de `POMBase` (cf. [`../02-ocarina/08-pom-base.md`](../02-ocarina/08-pom-base.md)).
2. **`ERROR_PAGE_REGEX`**&nbsp;: regex projet qui détecte un titre type page d'erreur HTTP (par exemple `^\d{3}\s.*` pour `500 Internal Server Error`).
3. **`HttpErrorPageReachedError`**&nbsp;: exception projet&nbsp;; sous-classe d'Exception, sera dans `transient_errors`.

C'est cet adapter qui rend le rejeu **automatique** pour les pages d'erreur.

## `match_page`

```python
# lib/ext/ocarina/adapters/agnostic/match_page.py
from ocarina.dsl.testing_with_railway.match_page import create_match_page
from constants.sys.transient_errors import transient_errors

match_page = create_match_page(raised_exceptions=transient_errors)
```

1. Import du factory `create_match_page`.
2. Import des `transient_errors` projet.
3. Instanciation&nbsp;: `match_page = create_match_page(...)`.

Tout `match_page(branches=[when(...)])` du projet utilise cette configuration. Les `transient_errors` _ne sont pas avalées_ comme «&nbsp;_non match_&nbsp;» par `match_page`&nbsp;: elles remontent et déclenchent le retry du test.

Voir [`../02-ocarina/03-railway/07-match-page-when.md`](../02-ocarina/03-railway/07-match-page-when.md) pour la mécanique sous-jacente.

## `EnvGetters`

```python
# lib/ext/ocarina/adapters/agnostic/env_getters.py
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

1. **`_CredsKeys = Literal["dashboard"]`**&nbsp;: énumération typée des _credentials_ disponibles.
2. **`_ValuesKeys = Literal["igor_api_key", "redis_url"]`**&nbsp;: énumération typée des valeurs simples.
3. **`MappingProxyType`**&nbsp;: un dict _immutable_ pour empêcher la mutation accidentelle des _credentials_.
4. **`_load_env` Effect**&nbsp;: appelé au constructeur, lit `.env` via `python-dotenv`.
5. **`create_env_getters(effects=None)`**&nbsp;: factory pour l'utilisateur.

```python
env = create_env_getters()
api_key = env.get_value("igor_api_key")        # ✅ autocomplete
creds = env.get_credentials("dashboard")       # ✅ retourne MappingProxyType
username = creds["login"]
```

Si on tape une clé invalide&nbsp;:

```python
env.get_value("typo_key")
# error: Argument 1 to "get_value" of "EnvGetters" has incompatible type "Literal['typo_key']";
#   expected "Literal['igor_api_key', 'redis_url']"
```

→ Erreur _mypy_ avant runtime.

## `TestSuite`

```python
# lib/ext/ocarina/adapters/selenium/test_suite.py
@final
class TestSuite(OriginalTestSuite[WebDriver]):
    def __init__(
        self, *,
        name: str,
        tests: Sequence[Test[WebDriver]],
        drivers_pool: SeleniumWebDriversPool,
        create_logger: Thunk[ILogger] | None = None,
        copy_indicator: str = "+",
        put_space_after_copy_indicator: bool = False,
        autoscreen_on_fail: bool = True,
        saturate_workers: bool | None = None,
    ) -> None:
        if create_logger is None:
            def _create_logger():
                return create_matching_logger(get_logger_mode())
            create_logger = _create_logger

        super().__init__(
            name=name,
            tests=tests,
            only_ids=get_only(),
            exclude_ids=get_exclude(),
            max_retries_per_test=8,
            create_logger=create_logger,
            drivers_pool=drivers_pool,
            copy_indicator=copy_indicator,
            put_space_after_copy_indicator=put_space_after_copy_indicator,
            autoscreen_on_fail=autoscreen_on_fail,
            take_screenshot=_take_screenshot_on_fail,
            transient_errors=transient_errors,
            saturate_workers=saturate_workers,
        )
```

| Paramètre                        | Valeur figée                 | Pourquoi                                  |
| -------------------------------- | ---------------------------- | ----------------------------------------- |
| `only_ids`                       | `get_only()` (depuis CLI)    | Propage le flag CLI                       |
| `exclude_ids`                    | `get_exclude()` (depuis CLI) | id.                                       |
| `max_retries_per_test`           | `8`                          | Convention «&nbsp;_9 vies_&nbsp;»         |
| `take_screenshot`                | `_take_screenshot_on_fail`   | Helper projet (4 shots, 350ms delay)      |
| `transient_errors`               | `transient_errors` (projet)  | Inclut `HttpErrorPageReachedError`, etc.  |
| `copy_indicator`                 | `"+"` (et pas `"COPY"`)      | Logs plus compacts (`[+1]` vs `[COPY 1]`) |
| `put_space_after_copy_indicator` | `False`                      | `[+1]` (et pas `[+ 1]`)                   |

Après adaptation&nbsp;:

```python
TestSuite(
    name="Login happy paths",
    tests=[test_a, test_b],
    drivers_pool=drivers_pool,
)
```

## `TestCampaign`

```python
# lib/ext/ocarina/adapters/selenium/test_campaign.py
@final
class TestCampaign(OriginalTestCampaign[WebDriver]):
    def __init__(
        self, *,
        name: str,
        suites: Sequence[TestSuite[WebDriver]],
        max_workers: int | None = None,
        saturate_workers: bool | None = None,
    ) -> None:
        if max_workers is None:
            max_workers = get_max_workers()
        super().__init__(
            name=name,
            suites=suites,
            max_workers=max_workers,
            saturate_workers=saturate_workers,
        )
```

Beaucoup plus simple&nbsp;: juste lire `max_workers` depuis la CLI si pas fourni.

L'utilisateur peut overrider pour le cas où l'on veut _explicitement_ stresser un sous-ensemble avec plus de workers&nbsp;:

```python
TestCampaign(
    name="Stress login",
    suites=[suite_a],
    max_workers=16,                     # ← override
    saturate_workers=True,
)
```

## «&nbsp;_Façade_&nbsp;» et «&nbsp;_Rétrécissement_&nbsp;»

Le Holy Book le formule (chapitre «&nbsp;_Premiers pas_&nbsp;»)&nbsp;:

> C'est l'_adapter_ le plus important à comprendre. `TestSuite` expose nativement un grand nombre de paramètres. L'objectif de cet _adapter_ est de créer une **façade**&nbsp;: certaines valeurs sont figées une bonne fois pour toutes (_hard-codées_), d'autres sont exposées optionnellement avec des valeurs par défaut. C'est un _rétrécissement_.

L'idée&nbsp;: Ocarina expose 14 paramètres pour `TestSuite`. Le projet utilise systématiquement les mêmes valeurs pour 6-7 d'entre eux. On fige ces 6-7 dans l'adapter, on n'expose que les 7 qui restent. La surface API du projet devient _plus petite_ et _plus opinionated_.
