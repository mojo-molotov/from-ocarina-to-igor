---
title: "02.10.04 — ActCounter + ThreadsBasedActCounter"
description: "Thread-local counter of acts executed per attempt. Lets the report say 'this test made 17 steps before dying at step 18'."
weight: 4
date: 2026-05-20
series: ["infra"]
series_order: 4
tags: ["ocarina"]
---

# 02.10.04&nbsp;—&nbsp;`ActCounter` + `ThreadsBasedActCounter`

> Thread-local counter of `act` calls per attempt. Lets the report say "_this test made 17 steps before dying at step 18_."

## Interface

```python
# src/ocarina/infra/act_counter.py
class ActCounter:
    def get(self) -> int: ...
    def reset(self) -> None: ...
    def incr_act_call_count(self) -> None: ...
```

## Default implementation

```python
# src/ocarina/opinionated/infra/act_counter.py
from threading import local

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

- **`threading.local()`**: namespace where attributes are _per thread_. Each thread has its own value.
- **`_COUNTER_KEY = "ocarina_counter"`**: attribute key.
- **No lock**: each thread only writes its own value, so no race.

## Why thread-local rather than a shared counter + lock?

Ocarina's architecture says **one thread = one test**. We've got no appetite for a whole _state monad_&nbsp;—&nbsp;might as well park this "impurity" (still a piece of state) right here. That's it.

## Usage in `create_act`

```python
def run_action() -> Result[TPOM]:
    try:
        if act_counter_effect:
            act_counter_effect()
        else:
            ThreadsBasedActCounter().incr_act_call_count()
        ...
```

Every `act(pom, action)` executed ticks the current thread's counter.

## Usage in `TestFlow.run`

```python
for attempt in range(1, max_attempts + 1):
    self._act_counter.reset()                           # ◄── reset BEFORE each attempt
    with self._drivers_pool.acquire() as driver:
        outcome = self._executor.execute(...)
    ...
```

And at the end:

```python
self._act_counter.reset()                               # ◄── reset after the last attempt
return last_result, last_steps_count, test.test_id
```

## Usage in `TestExecutor.execute`

```python
steps_count = self._act_counter.get()
return ExecutionOutcome(
    result=result, skipped=False, setup_failed=False,
    should_retry=should_retry, steps_count=steps_count,
)
```

`steps_count` is read **at the end** of an attempt. Lands in `TestSuiteResult = (TestResult, steps_count, test_id)`, and in `pretty_print_results` ("_⫸ At step 3_" when a test fails).

## `act_counter_effect`&nbsp;—&nbsp;why a customizable hook

It's an **impurity** and we want to keep an eye on it from a testability angle. Exposing it costs nothing. That's it.

Default stays "increment Ocarina's thread-local counter"&nbsp;—&nbsp;covers 99% of cases.

## Why two files (`infra/` + `opinionated/infra/`)

| File                                           | Role                                                                                |
| ---------------------------------------------- | ----------------------------------------------------------------------------------- |
| `src/ocarina/infra/act_counter.py`             | **Interface** `ActCounter`. The contract. Anyone can implement it.                  |
| `src/ocarina/opinionated/infra/act_counter.py` | **Implementation** `ThreadsBasedActCounter`. Opinionated choice: `threading.local`. |
