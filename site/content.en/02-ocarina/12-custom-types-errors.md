---
title: "02.12 — Custom types & custom errors"
description: "Ocarina's shape layer: types, aliases, exceptions and protocols, with no runtime logic, making the DSL typed at no execution cost."
weight: 12
date: 2026-05-20
series: ["ocarina"]
series_order: 12
tags: ["scenarios", "selenium"]
---

# 02.12&nbsp;—&nbsp;Custom types & custom errors

> Ocarina's _shape_ layer. No logic&nbsp;—&nbsp;types, aliases, exceptions, protocols. What makes the DSL typed without adding runtime logic.

## `custom_types/`

| File                             | Contents                                                                                                 |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `effect.py`                      | `type Effect = Callable[[], None]` + `type Effects = tuple[Effect, ...]`                                 |
| `thunk.py`                       | `type Thunk[T] = Callable[[], T]`                                                                        |
| `tpom.py`                        | `TypeVar TPOM bound POMBase`                                                                             |
| `supports_write.py`              | `Protocol SupportsWrite[T]` (`write(s: T) -> Any`)                                                       |
| `built_web_driver.py`            | `type BuiltWebDriver[Driver] = tuple[Driver, Effect]`                                                    |
| `scenario.py`                    | `Scenario[Driver]` (frozen dataclass)                                                                    |
| `test_components.py`             | `TestChain`, `TestSetup`, `TestTeardown`, `TestWatchers[Driver]`                                         |
| `test_runner.py`                 | `TestRunner[Driver]` (frozen dataclass)                                                                  |
| `oc_test.py`                     | `TestName`, `TestScenario[Driver]`, `TestScenarioFragment[Driver]`                                       |
| `oc_test_layers.py`              | `TestId`, `TestResult`, `TestSuiteResult`, `TestSuiteResults`, `TestCampaignResults`, `TestCycleResults` |
| `selenium/built_web_driver.py`   | `BuiltSeleniumWebDriver = BuiltWebDriver[WebDriver]`                                                     |
| `selenium/oc_test_scenario.py`   | `SeleniumTestScenario = TestScenario[WebDriver]`                                                         |
| `selenium/supported_browsers.py` | `type SupportedSeleniumBrowser = Literal["chrome", "firefox", "edge", "safari"]`                         |
| `selenium/web_drivers_pool.py`   | `type SeleniumWebDriversPool = WebDriversPool[WebDriver]`                                                |

All these files are _excluded from coverage_ (`pyproject.toml#tool.coverage`):

```toml
"src/ocarina/custom_types/*",
```

Reason: no runtime logic to test&nbsp;—&nbsp;these are _shapes_.

## Hierarchy

```python
# src/ocarina/custom_types/oc_test_layers.py

type TestId = str
type _TestStepsCount = int
type TestResult = Result[Any] | None
type TestSuiteResult = tuple[TestResult, _TestStepsCount, TestId]
type TestSuiteResults = dict[str, TestSuiteResult]                  # {test_name: TestSuiteResult}
type TestCampaignResults = dict[str, TestSuiteResults]              # {suite_name: TestSuiteResults}
type TestCycleResults = dict[str, TestCampaignResults]              # {campaign_name: TestCampaignResults}
```

Reading:

```
TestCycleResults
  └── "Dashboard login" (campaign)
      └── "Login happy paths" (suite)
          ├── "Login - without OTP" (test) → (Ok(None), 15, "login_no_otp")
          └── "Login - with OTP"    (test) → (Fail(exc), 8, "login_otp")
```

Three levels of nesting, indexed by name. `(TestResult, steps_count, test_id)` is the leaf.

## `Scenario[Driver]`, `TestRunner[Driver]`, `TestChain`

```python
@dataclass(frozen=True)
class Scenario[Driver]:
    test_chain: TestChain
    setup: TestSetup = field(default=None)
    teardown: TestTeardown = field(default=None)
    watchers: TestWatchers[Driver] | None = field(default=None)


@dataclass(frozen=True)
class TestRunner[Driver]:
    chain_runners: list[ChainRunner[Any]]
    skipped: bool
    setup: Effect | None
    teardown: Effect | None
    watchers: Sequence[Watcher[Driver]] | None


type TestChain = Sequence[ChainRunner[Any]]
type TestSetup = Effect | None
type TestTeardown = Effect | None
type TestWatchers[Driver] = Sequence[Watcher[Driver]] | None
```

Two dataclasses + 4 type aliases. No methods, just data bags.

## `custom_errors/`

| File                                   | Exception                | Raised by                                                                                                                                                                                 |
| -------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_framework/no_matching_branch.py` | `NoMatchingBranchError`  | `match_page` when no `when` matches                                                                                                                                                       |
| `test_framework/pages.py`              | `PageVerificationError`  | Conventionally raised by `POM.verify` when the page isn't the expected one                                                                                                                |
| `test_framework/driver_died.py`        | `DriverDiedError`        | `driver_healthcheck` when the driver stops responding                                                                                                                                     |
| `test_framework/campaigns.py`          | `DuplicateTestNameError` | Raised when two tests within the same campaign share the same `name`. Subclass of `DuplicatesError` (itself `InvariantViolationError`); carries the `duplicates` sequence for the report. |

## `DriverDiedError`

```python
@final
class DriverDiedError(Exception):
    """Raised when a WebDriver instance dies or becomes unresponsive."""
```

→ Lets a caller separate "the driver is dead" from "the driver is misbehaving." Ocarina treats it as transient via project adapters (the project adds `DriverDiedError` to its `transient_errors`).

## `PageVerificationError`

Conventionally raised inside `POM.verify`:

```python
def verify(self, *, timeout: float | None = None) -> Self:
    try:
        WebDriverWait(self._driver, timeout or get_timeout()).until(...)
    except TimeoutException as exc:
        raise PageVerificationError from exc
    return self
```

Lets you tell "wrong page" apart from "Selenium error."

## `NoMatchingBranchError`

Raised by `_match_page_builder` when no `when` matches. See [`03-railway/07-match-page-when.md`](03-railway/07-match-page-when.md).

A _scenario-logic_ error: the user forgot to cover a case. It should propagate as `Fail` on the failure rail, not as `transient_errors`&nbsp;—&nbsp;retrying won't fix missing coverage.

## `custom_invariants/testing/`

| File                         | Invariant                     | Raises on                              |
| ---------------------------- | ----------------------------- | -------------------------------------- |
| `workers.py`                 | `validate_workers_amount`     | `workers < 1`                          |
| `oc_test_runners_ids.py`     | `validate_test_runners_ids`   | Duplicate IDs                          |
| `oc_test_runners_names.py`   | `validate_test_runners_names` | Duplicate OR invalid-as-filename names |
| `oc_test_suites_names.py`    | `validate_test_suites_names`  | Duplicate suite names                  |
| `oc_test_campaigns_names.py` | `validate_campaigns_names`    | Duplicate campaign names               |
| `oc_test_cycles_names.py`    | `validate_test_cycle_name`    | Invalid-as-filename name               |

All written with `FrameworkInvariantValidator.create(...)` (see [`04-invariants/05-business-vs-framework-validator.md`](04-invariants/05-business-vs-framework-validator.md)).

## `SupportsWrite[T]`

```python
from typing import Protocol, TypeVar

T_contra = TypeVar("T_contra", contravariant=True)

class SupportsWrite(Protocol[T_contra]):
    def write(self, s: T_contra, /) -> Any: ...
```

Minimal protocol: any object with `.write(s)` qualifies. Lets loggers take a `stream: SupportsWrite[str] | None` (sys.stdout, sys.stderr, file, mocked BytesIO).

Note: `contravariant=True` because `write` is an _input_ operation, hence contravariant in `T`.  
Lines up with Python's stdlib.
