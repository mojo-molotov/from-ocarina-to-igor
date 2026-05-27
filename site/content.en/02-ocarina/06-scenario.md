---
title: "02.06 — Scenario[Driver]"
description: "Source file: src/ocarina/custom_types/scenario.py"
weight: 6
date: 2026-05-20
series: ["ocarina"]
series_order: 6
tags: ["watcher", "scenarios"]
---

# 02.06&nbsp;—&nbsp;`Scenario[Driver]`

> Source file: [`src/ocarina/custom_types/scenario.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/scenario.py)

## Dataclass

```python
@final
@dataclass(frozen=True)
class Scenario[Driver]:
    test_chain: TestChain
    setup: TestSetup = field(default=None)
    teardown: TestTeardown = field(default=None)
    watchers: TestWatchers[Driver] | None = field(default=None)
```

```python
# src/ocarina/custom_types/test_components.py
type TestChain = Sequence[ChainRunner[Any]]
type TestSetup = Effect | None
type TestTeardown = Effect | None
type TestWatchers[Driver] = Sequence[Watcher[Driver]] | None
```

## Lifecycle (per attempt)

```
1. setup()           — optional, free-form Effect (DB, API, …)
       → raises    :  test_chain skipped, jump to teardown,
                      return Outcome(setup_failed=True, should_retry=True)
       → ok        :  continue to test_chain

2. test_chain        — the actual chain (Sequence[ChainRunner])
       (watchers run during this time)

3. teardown()        — optional, always executed
       → raises    :  log warning + ignore (does not affect the verdict)

If EVERY attempt raises during setup:
    → test marked SKIPPED (not FAILED)
    → warning log « setup keeps failing »
```

## `setup` and `teardown`

`setup` and `teardown` are **driver-free and injection-free by design.**

Documented in the module's docstring:

> They are plain `Effect`s&nbsp;—&nbsp;`() -> None`.
> They are meant for infrastructure concerns: seeding a database, calling an API, cleaning up state. Selenium belongs in `test_chain`.
> Whatever context they need (logger, driver, config) must be **captured in the closure** at scenario construction time.

```python
def my_scenario(driver: WebDriver, logger: ILogger) -> Scenario[WebDriver]:
    return Scenario(
        setup=lambda: seed_test_user(logger=logger),                # logger captured
        teardown=lambda: delete_test_user(logger=logger),           # logger captured
        test_chain=[...],
    )
```

1. **No coupling** between infrastructure and POMs. A DB setup has no business knowing about Selenium.
2. **Symmetry with `Watcher.callback`**: same closure-based context injection (the `Watcher` injects `driver`, `logger`, `take_screenshot` _at `start()` time_).
3. **Testability**: setup tests run in isolation, no Selenium wrapper needed.

## `test_chain`

```python
type TestChain = Sequence[ChainRunner[Any]]
```

Exactly what you build by returning `[drive_page(...), drive_page(...), match_page(...), drive_page(...)]`. Each element runs sequentially via `_run_chain` (see [`05-orchestration/02-test-executor.md`](05-orchestration/02-test-executor.md)).

Subtle point: `ChainRunner[Any]` (not `ChainRunner[TPOM]`). A `test_chain` can **mix** `drive_page` calls on different pages (HomePage, LoginPage, DashboardPage…) and `match_page` calls (which return `ChainRunner[Any]`). `Any` is the _catch-all_ that makes a heterogeneous sequence typable.

## `watchers`

```python
type TestWatchers[Driver] = Sequence[Watcher[Driver]] | None
```

Watchers are _daemon threads_ watching the browser in parallel with the chain and reporting frictions via `watcher.report(...)`. See [`07-watcher.md`](07-watcher.md).

- **Started _just before_ the chain**, **stopped _just after_**. Strictly scoped to `test_chain`&nbsp;—&nbsp;they never see `setup` or `teardown`.
- **One thread per watcher**.
- **One scoped logger per watcher**: `(*taxonomy[:-1], "<test_name> - <watcher_name>")`. Produces a `.log` sibling to the test's.

## Example

```python
from ocarina.custom_types.scenario import Scenario

def my_scenario(driver: WebDriver, logger: ILogger) -> Scenario[WebDriver]:
    page = MyPage(driver=driver)

    return Scenario(
        setup=lambda: seed_test_user(logger=logger),
        test_chain=[
            drive_page(
                act(page, open_page)
                    .failure(log_error("Failed to open..."))
                    .success(log_success("Opened!")),
            ),
            drive_page(
                act(page, verify_page)
                    .failure(log_error("Failed to verify..."))
                    .success(log_success("Verified!")),
            ),
        ],
        teardown=lambda: delete_test_user(logger=logger),
        watchers=[
            MyWatcher(...),
        ],
    )
```

## Why `frozen=True` and `@final`

`@final` + `@dataclass(frozen=True)`:

| Property                                       | Consequence                                                   |
| ---------------------------------------------- | ------------------------------------------------------------- |
| `frozen=True`                                  | Can't mutate `scenario.test_chain = [...]` after construction |
| `@final`                                       | Can't subclass (`class MyScenario(Scenario[WebDriver])`)      |
| Implicit kwargs-based construction (dataclass) | Stable API                                                    |

A `Scenario` is a **value**.

## `TestRunner`

`Test.spawn(driver, logger)` returns a `TestRunner` that **aggregates**:

- `chain_runners` (concatenation `pre + scenario.test_chain + post`),
- `setup` (from `scenario.setup`),
- `teardown` (from `scenario.teardown`),
- `watchers` (from `scenario.watchers`),
- `skipped` (from `Test._skipped`).

So what's inside the `Scenario` is **strictly the scenario**. The pre/post fragments get _bolted around it_ by `spawn`.

## Related test

[`tests/scenarios/test_test_suite.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_test_suite.py) contains a test that goes through a scenario with setup + teardown:

```python
@allure.title("setup that fails on first attempt, succeeds on retry, then test passes")
def test_setup_retries_then_test_passes() -> None:
    ...
```

See [`../04-internal-tests/03-pytest-scenarios.md`](../04-internal-tests/03-pytest-scenarios.md).
