---
title: "03.02 — Closures as the primitive of inversion of control"
description: "No DI container. No injection framework. A closure is Ocarina's injection primitive."
weight: 2
date: 2026-05-20
series: ["functional"]
series_order: 2
---

# 03.02&nbsp;—&nbsp;Closures as the primitive of inversion of control

> No DI container. No injection framework. **A closure is Ocarina's injection primitive.**

## The idea

A closure captures values from its enclosing scope. Return a function from another function and the outer parameters are **available inside**, even after the outer function returns.

```python
def make_handler(logger: ILogger) -> Callable[[str], FailureHandler]:
    def make_failure_handler(msg: str) -> FailureHandler:
        def actual_handler(exc: Exception) -> None:
            logger.error(msg, exc=exc)
        return actual_handler
    return make_failure_handler
```

Also _currying_: `make_handler(logger)(msg)(exc)`. Each call captures a new layer of environment.

## Reminder from the Holy Book

```python
# ocarina-example/lib/ext/ocarina/adapters/selenium/logs.py
def create_just_log_error(*, logger: ILogger) -> Callable[[str], FailureHandler]:
    return lambda msg: lambda exc: logger.error(msg, exc=exc)
```

| Level | Capture  | Typical call                           |
| ----- | -------- | -------------------------------------- |
| 1     | `logger` | `create_just_log_error(logger=logger)` |
| 2     | `msg`    | `just_log_error("Failed to do X")`     |
| 3     | `exc`    | passed in as an arg by the framework   |

```python
just_log_error = create_just_log_error(logger=logger)

return [
    drive_page(
        act(on_homepage, open_homepage)
            .failure(just_log_error("Failed to open the homepage..."))    # ← level 2
            ...
    )
]
```

`just_log_error("Failed to open...")` returns a `FailureHandler` that, when the framework calls it with the exception, writes the message.

## Why not an object with methods?

BECAUSE.

## Ocarina's actual IoC

Inversion of control in Ocarina boils down to "_the framework calls your code_" instead of "_your code calls the framework_."

### 1. `create_act(on_failure=...)`

```python
def act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]:
    def failure_hook(pom: TPOM, exc: Exception) -> Fail:
        if is_http_error_page(pom):
            return Fail(error=HttpErrorPageReachedError(...))
        return Fail(error=exc)
    return create_act(pom, action, on_failure=failure_hook)
```

→ The framework calls _your_ `failure_hook` when the action raises. The hook gets `pom` (captured as an argument) and `exc`. You decide what `Fail` to return.

### 2. `Scenario.setup` / `Scenario.teardown`

```python
return Scenario(
    setup=lambda: seed_test_user(logger=logger),         # closure on logger
    teardown=lambda: delete_test_user(logger=logger),    # closure on logger
    test_chain=[...],
)
```

→ The framework calls _your_ `setup` at the right moment. Give it access to `logger` via a closure if you want.

### 3. `Watcher.callback`

```python
def my_callback(watcher: Watcher) -> None:
    elements = watcher.driver.execute_script("...")
    for el in elements:
        watcher.report(f"detected: {el}")

scenario = Scenario(
    test_chain=[...],
    watchers=[Watcher(callback=my_callback, name="cookies", poll_interval=0.8)],
)
```

→ The framework calls _your_ `my_callback` every `poll_interval` seconds, passing the `Watcher` (which hands you `driver`, `cache`, `report`).

### 4. `match_page(when(condition=...))`

```python
match_page(branches=[
    when(check.has_cookies_banner, name="A", then=[...]),
    when(check.has_not_cookies_banner, name="B", then=[...]),
])
```

→ The framework calls _your_ `condition` at runtime to choose the branch.

### 5. `bootstrap(post_exec=...)`

```python
def _post_exec(results: TestCycleResults) -> None:
    pretty_print_results(results, with_colors=True)
    if has_test_cycle_failed(results):
        sys.exit(1)

bootstrap(test_cycle=..., run_plugins=..., post_exec=_post_exec)
```

→ The framework calls _your_ `_post_exec` at the end of the cycle.

## Parameterized connectors

Pattern from the Holy Book (chapter "First real-world hurdles"):

```python
def enter_xxx_key(p: CorsicamonEnterXXXKeyPage) -> CorsicamonEnterXXXKeyPage:
    return p.enter_xxx_key()

def enter_xxx_key_with_retries(
    *, retries: int, logger: ILogger,
) -> Callable[[CorsicamonEnterXXXKeyPage], CorsicamonEnterXXXKeyPage]:

    def unwrapped(p: CorsicamonEnterXXXKeyPage) -> CorsicamonEnterXXXKeyPage:
        return p.enter_xxx_key_with_retries(retries=retries, logger=logger)

    return unwrapped
```

> Simply return the `def` with the expected signature, inside a function that captures the parameters. That's a _closure_.

- `enter_xxx_key` is a direct _connector_.
- `enter_xxx_key_with_retries(retries=3, logger=logger)` returns **a connector** that already knows the retry count and the logger. The framework gets this connector and calls it with `(p: CorsicamonEnterXXXKeyPage)`.

## Why

The Holy Book (chapter "First feedbacks"):

> _Forcing their clueless take on lazy evaluation and IoC down my throat like it's gospel._

Ocarina's IoC is **explicit, local, typed**. No magic.

| Benefit               | Comparison                                                                                   |
| --------------------- | -------------------------------------------------------------------------------------------- |
| **No global setup**   | No `inject()`, no `bind(...)` to write before testing.                                       |
| **Trivial tests**     | To test `create_just_log_error(logger=mock_logger)(msg)(exc)`, you just call it. No fixture. |
| **Type-safe**         | The checker validates the signature at every currying level.                                 |
| **Refactor-friendly** | Renaming a parameter cleanly cascades through the whole call graph.                          |

## Data → functions

The Holy Book puts it differently in the chapter "First feedbacks":

> Raw data.

In Ocarina, "_raw data_" includes **functions** as first-class values. An `Effect` is data. A `Thunk[T]` is data. A closure is enriched data. We pass them, compose them, store them. Algebraic.
