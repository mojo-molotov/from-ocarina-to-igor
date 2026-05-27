---
title: "02.03.05 — create_act and its hooks"
weight: 5
date: 2026-05-20
series: ["railway"]
series_order: 5
tags: ["ocarina"]
---

# 02.03.05&nbsp;—&nbsp;`create_act` and its hooks

> Source file: [`src/ocarina/dsl/testing_with_railway/constructors/create_act.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/constructors/create_act.py)
>
> The **low-level primitive** that builds a _test step_ constructor. You call it **once** to mint a project-specific `act` verb. In theory a complex project might want several distinct `act` verbs with different hooks, but no real-world need has shown up yet&nbsp;—&nbsp;recommendation: create **one**. Not a singleton, just a convention.

## Signature

```python
def create_act(
    pom: TPOM,
    action: Callable[[TPOM], TPOM],
    *,
    on_failure: Callable[[TPOM, Exception], Fail] | None = None,
    on_run_effect: Effect | None = None,
    act_counter_effect: Effect | None = None,
) -> ActionStart[TPOM]:
```

| Parameter            | Position     | Type                                        | Role                                                                                                                                                                 |
| -------------------- | ------------ | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pom`                | positional   | `TPOM` (bound `POMBase`)                    | The page (or any `POMBase` subclass) you're acting on.                                                                                                               |
| `action`             | positional   | `Callable[[TPOM], TPOM]`                    | The function that acts on the page and returns the page (fluent). Identity-typed.                                                                                    |
| `on_failure`         | keyword-only | `Callable[[TPOM, Exception], Fail] \| None` | Hook for **refining** the `Fail`: if you reach this, you've already failed; the hook just lets you type the error more precisely (e.g. `HttpErrorPageReachedError`). |
| `on_run_effect`      | keyword-only | `Effect \| None`                            | Side effect called **before** the action (e.g.: log a step number).                                                                                                  |
| `act_counter_effect` | keyword-only | `Effect \| None`                            | _Additional_ side effect called before the action. Default: increments the act counter.                                                                              |

## Code

```python
def run_action() -> Result[TPOM]:
    try:
        if act_counter_effect:
            act_counter_effect()
        else:
            ThreadsBasedActCounter().incr_act_call_count()

        if on_run_effect:
            on_run_effect()

        result_pom = action(pom)
        return Ok(result_pom)
    except Exception as exc:  # noqa: BLE001
        if on_failure:
            return on_failure(pom, exc)
        return Fail(error=exc)

return ActionStart(run_action)
```

1. **The `try` wraps EVERYTHING**: `act_counter_effect`, `on_run_effect`, _and_ the action. If any side effect raises (say `on_run_effect` hits a dead resource), it counts as a test-step failure. Everything that runs "during the test step" IS the test step.
2. **Order is deterministic**: counter → run effect → action. The counter ticks _even if_ the action ends up failing. Intentional&nbsp;—&nbsp;we want to know how many steps were _attempted_, not how many passed.
3. **`on_failure` can return an enriched `Fail`**: that's where a `WebDriverException` becomes an `HttpErrorPageReachedError`.

## Default `ActCounter`: `ThreadsBasedActCounter`

```python
from ocarina.opinionated.infra.act_counter import ActCounter as ThreadsBasedActCounter
# ...
if act_counter_effect:
    act_counter_effect()
else:
    ThreadsBasedActCounter().incr_act_call_count()
```

Source: [`src/ocarina/opinionated/infra/act_counter.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/infra/act_counter.py)

```python
from threading import local
from ocarina.infra.act_counter import ActCounter as _ActCounter

_thread_local = local()
_COUNTER_KEY: Final[str] = "ocarina_counter"


class ActCounter(_ActCounter):
    def get(self) -> int:
        return getattr(_thread_local, _COUNTER_KEY, 0)

    def reset(self) -> None:
        setattr(_thread_local, _COUNTER_KEY, 0)

    def incr_act_call_count(self) -> None:
        if not hasattr(_thread_local, _COUNTER_KEY):
            self.reset()
        setattr(_thread_local, _COUNTER_KEY, getattr(_thread_local, _COUNTER_KEY) + 1)
```

A **thread-local** counter. **Architectural** call: one test worker = one thread, so this naive-and-fast implementation is enough. Each `TestSuite` worker keeps its own counter, no contention, no `threading.Lock`. `TestExecutor` _reads_ it at the end (`steps_count = self._act_counter.get()`).

## Recommended pattern (from the docstring)

```python
# In your project, create a wrapper with custom logic
def act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]:
    def failure_hook(pom: TPOM, exc: Exception) -> Fail:
        # Detect HTTP error pages
        title = pom.get_current_title()
        if ERROR_PAGE_REGEX.match(title):
            return Fail(error=HttpErrorPageReachedError(title))
        return Fail(error=exc)

    return create_act(
        pom, action,
        on_failure=failure_hook,
        on_run_effect=increment_step_counter
    )

# Then use your wrapper
act(page, lambda p: p.click_button())
    .failure(log_error)
    .success(log_success)
    .execute()
```

That's exactly the pattern in `ocarina-example/lib/ext/ocarina/adapters/agnostic/act.py` (see [`../../07-ocarina-example/02-adapters.md`](../../07-ocarina-example/02-adapters.md)).

## Why not just use `create_act` directly everywhere

1. **`on_failure` _should_ be project-specific.** Without it, every exception becomes a raw `Fail(exc)`. With it, you can recognize _classes_ of errors (HTTP error page, maintenance page, etc.), which sharpens `transient_errors`.
2. **`on_run_effect`** is where step-by-step logging or metrics go.
3. **The `act` counter** almost always stays default, but it can be swapped for special cases.

## `__action__` is recovered by `chain_actions`

`ActionStart(run_action)` stows `run_action` in `self.__action__`. When `chain_actions` reuses that `ActionStart` via `step.__action__`, it grabs back the exact thunk closing over `pom`, `action`, `on_failure`, `on_run_effect`, `act_counter_effect`. Nothing fires until `.execute()`.

## Hooks recap

| Hook                 | When does it fire?                        | What does it do?                                                                                          |
| -------------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `act_counter_effect` | Before the action, before `on_run_effect` | If provided: replaces the default increment. If absent: `ThreadsBasedActCounter().incr_act_call_count()`. |
| `on_run_effect`      | Before the action, after the counter      | Free-form side effect                                                                                     |
| `on_failure`         | After `except`, before returning `Fail`   | Receives `(pom, exc)`, returns a _refined_ `Fail`                                                         |
