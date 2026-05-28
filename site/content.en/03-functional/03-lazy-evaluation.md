---
title: "03.03 — Lazy evaluation"
description: "Lazy evaluation in Ocarina: nothing runs before explicit triggering, which makes scenarios composable as values."
weight: 3
date: 2026-05-20
series: ["functional"]
series_order: 3
tags: ["watcher", "scenarios"]
---

# 03.03&nbsp;—&nbsp;Lazy evaluation

> In Ocarina, **nothing is executed until you explicitly trigger it**. That's what makes scenarios composable as values.

## Zzz

| Location                                       | Form                                             | Trigger                              |
| ---------------------------------------------- | ------------------------------------------------ | ------------------------------------ |
| `ChainRunner[T]`                               | `Thunk[ActionChain[T]]`                          | `runner.run()`                       |
| `validate(...)`                                | `ValidationStartBlock` / `ValidationAssertBlock` | `.execute()`                         |
| `match_page(...)`                              | returns a `ChainRunner[Any]`                     | `.run()` (via the surrounding chain) |
| `Watcher.callback`                             | `Callable[[Watcher], None]`                      | `_loop` when `start()` is called     |
| `logger.set_prefix(thunk)`                     | `Thunk[str]`                                     | recomputed at each log call          |
| `Scenario.setup` / `teardown`                  | `Effect`                                         | called by `TestExecutor`             |
| `bootstrap(post_exec=...)`                     | `Callable[[TestCycleResults], None]`             | called after `run_plugins`           |
| `CliBuilder(effects_factory=lambda ns: (...))` | `Effects`                                        | called after the argparse parse      |
| `test_scenario: TestScenario[Driver]`          | `Callable[[Driver, ILogger], Scenario[Driver]]`  | called by `Test.spawn`               |
| `dispatch[mode]()` in `TestCycle.run_all`      | dict of `Thunk[bool]`                            | called on lookup                     |

## `ChainRunner`

```python
runner = drive_page(act1, act2, act3)        # ⚠️  nothing executed
# … later …
chain = runner.run()                         # ▶︎  execution
```

| Capability                                        | Without laziness                            | With laziness    |
| ------------------------------------------------- | ------------------------------------------- | ---------------- |
| Store a scenario in a variable                    | impossible (already executed)               | trivial          |
| Multiply `[runner] * 5`                           | executes once, you get 5 refs to the result | executes 5 times |
| Pass a `runner` to another `runner` (composition) | impossible                                  | trivial          |
| Reorder `act`s in a test refactor                 | hard                                        | trivial          |

## `validate(...).execute()`

```python
v = validate(value, name="x").assert_that(is_positive).assert_that(is_not_zero)
# … you can compose …
combined = chain_validations(v, other_validation)
# … nothing executed so far …
combined.execute().raise_if_invalid()        # ▶︎  execution + aggregation
```

That's how `_ValidationChain` **collects** every error before raising a single one (`AggregateInvariantViolationError`).

## `Watcher.callback`

```python
watcher = Watcher(callback=my_callback, name="x", poll_interval=0.5)
# nothing executed

watcher.start(driver, logger, take_screenshot)
# ▶︎  spawns a daemon thread that calls my_callback(self) every 0.5 s
```

Net: _creating_ a watcher is free. Put 10 of them in `scenario.watchers` at no cost; they only run during `test_chain`.

## `set_prefix(thunk)`

```python
logger.set_prefix(lambda: f"[{datetime.now().isoformat()}]")
```

Why a `Thunk`? Because we want **a different prefix at each log** (timestamps change). A `str` would be frozen.

## `effects_factory(ns) -> Effects`

```python
return CliBuilder(
    args=[...],
    effects_factory=lambda ns: (
        lambda: store.set("workers", ns.workers),
        lambda: store.set("browser", ns.browser),
        ...
        _create_validate_only_exclude_mutex_effect(ns),
        ...
    ),
)
```

- `effects_factory` is called _after_ the argparse parse, with `ns` complete.
- It returns a tuple of `Effect`.
- The `CliBuilder` executes them one by one.

**Separates** declaration of effects (`(lambda: ..., lambda: ...)`) from their execution.

## `TestScenario[Driver]`

```python
type TestScenario[Driver] = Callable[[Driver, ILogger], Scenario[Driver]]
```

Not a `Scenario` directly:

- `driver` doesn't exist when the test is declared (it's acquired by `TestFlow.run`).
- `logger` doesn't either (it's created by `TestSuite._create_logger`).

→ We declare the scenario _deferred_: "_here's how to build the Scenario once you have a driver and a logger_." The framework calls the factory at runtime.

## `dispatch[mode]()`

```python
dispatch: dict[Mode, Thunk[bool]] = {
    "fail-fast-on-first-smoke-campaigns-sequence-fail":
        lambda: _run_smoke(fail_fast=True),
    "wait-for-all-smoke-tests":
        lambda: _run_smoke(fail_fast=False),
}

skip_all = dispatch[self._mode]()
```

| `if/elif`                                       | dispatch table                                 |
| ----------------------------------------------- | ---------------------------------------------- |
| Imperative code                                 | Declarative code                               |
| Only one branch evaluated&nbsp;—&nbsp;that's OK | No branch evaluated until you call `()`        |
| Hard to extend                                  | Adding a mode = adding a key                   |
| Harder `Literal` exhaustiveness checking        | The checker can verify the table covers `Mode` |

## Laziness and composition

Laziness isn't an optimization, it's what makes composition **clean**.

`validate(...).assert_that(...)` running immediately would block combining it with another chain via `chain_validations`.

A `ChainRunner` running on creation would block dropping it into a `match_page` branch.
