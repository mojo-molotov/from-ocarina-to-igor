---
title: "07.02 — The 5 adapters"
description: "Every Ocarina project starts by writing five adapters on top of the framework. The ocarina-example project provides them as reference."
weight: 2
date: 2026-05-20
series: ["ocarina-example"]
series_order: 2
---

# 07.02&nbsp;—&nbsp;The 5 adapters

> Every Ocarina project starts by writing **five** adapters on top of the framework.  
> The `ocarina-example` project provides them as reference.

## Listing

| Adapter        | Status   | File                                                 | Purpose                                                      |
| -------------- | -------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| `act`          | required | `lib/ext/ocarina/adapters/agnostic/act.py`           | Project-specific `on_failure` hook                           |
| `match_page`   | optional | `lib/ext/ocarina/adapters/agnostic/match_page.py`    | Shared exception policy                                      |
| `EnvGetters`   | optional | `lib/ext/ocarina/adapters/agnostic/env_getters.py`   | Typed access to env vars                                     |
| `TestSuite`    | required | `lib/ext/ocarina/adapters/selenium/test_suite.py`    | Façade: pins `transient_errors`, `max_retries`, `autoscreen` |
| `TestCampaign` | required | `lib/ext/ocarina/adapters/selenium/test_campaign.py` | Façade: `max_workers` from CLI                               |

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

1. **`get_current_title()`**: uses `POMBase`'s mandatory method (see [`../02-ocarina/08-pom-base.md`](../02-ocarina/08-pom-base.md)).
2. **`ERROR_PAGE_REGEX`**: detects titles shaped like HTTP error pages (`^\d{3}\s.*` → `500 Internal Server Error`).
3. **`HttpErrorPageReachedError`**: project exception, included in `transient_errors`.

This adapter is what makes error-page replay **automatic**.

## `match_page`

```python
# lib/ext/ocarina/adapters/agnostic/match_page.py
from ocarina.dsl.testing_with_railway.match_page import create_match_page
from constants.sys.transient_errors import transient_errors

match_page = create_match_page(raised_exceptions=transient_errors)
```

1. Import the `create_match_page` factory.
2. Import the project's `transient_errors`.
3. Instantiation: `match_page = create_match_page(...)`.

Every `match_page(branches=[when(...)])` in the project uses this config. `transient_errors` aren't swallowed as "no match"&nbsp;—&nbsp;they bubble up and trigger the test retry.

See [`../02-ocarina/03-railway/07-match-page-when.md`](../02-ocarina/03-railway/07-match-page-when.md) for the underlying mechanics.

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

1. **`_CredsKeys = Literal["dashboard"]`**: typed enumeration of available credentials.
2. **`_ValuesKeys = Literal["igor_api_key", "redis_url"]`**: typed enumeration of simple values.
3. **`MappingProxyType`**: immutable dict&nbsp;—&nbsp;no accidental mutation of credentials.
4. **`_load_env` Effect**: runs in the constructor, reads `.env` via `python-dotenv`.
5. **`create_env_getters(effects=None)`**: public factory.

```python
env = create_env_getters()
api_key = env.get_value("igor_api_key")        # ✅ autocomplete
creds = env.get_credentials("dashboard")       # ✅ returns MappingProxyType
username = creds["login"]
```

If you type an invalid key:

```python
env.get_value("typo_key")
# error: Argument 1 to "get_value" of "EnvGetters" has incompatible type "Literal['typo_key']";
#   expected "Literal['igor_api_key', 'redis_url']"
```

mypy catches it before runtime.

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

| Parameter                        | Pinned value                 | Why                                      |
| -------------------------------- | ---------------------------- | ---------------------------------------- |
| `only_ids`                       | `get_only()` (from CLI)      | Propagates the CLI flag                  |
| `exclude_ids`                    | `get_exclude()` (from CLI)   | id.                                      |
| `max_retries_per_test`           | `8`                          | "_9 lives_" convention                   |
| `take_screenshot`                | `_take_screenshot_on_fail`   | Project helper (4 shots, 350ms delay)    |
| `transient_errors`               | `transient_errors` (project) | Includes `HttpErrorPageReachedError`, …  |
| `copy_indicator`                 | `"+"` (not `"COPY"`)         | More compact logs (`[+1]` vs `[COPY 1]`) |
| `put_space_after_copy_indicator` | `False`                      | `[+1]` (not `[+ 1]`)                     |

After adaptation:

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

Simpler: just reads `max_workers` from the CLI if not provided. Override when you want to stress a subset harder:

```python
TestCampaign(
    name="Stress login",
    suites=[suite_a],
    max_workers=16,                     # ← override
    saturate_workers=True,
)
```

## "_Façade_" and "_Narrowing_"

The Holy Book puts it (chapter "First steps"):

> This is the most important adapter to understand. `TestSuite` natively exposes a large number of parameters. The goal of this adapter is to create a **facade** around it: some values are hardcoded once and for all, others are optionally exposed with sensible defaults. _Narrowing_.

Ocarina exposes 14 parameters for `TestSuite`. The project uses the same values for 6–7 of them every time. Pin those in the adapter, expose only what varies. Smaller API surface, more opinionated defaults.
