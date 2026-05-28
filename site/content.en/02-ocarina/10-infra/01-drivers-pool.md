---
title: "02.10.01 — WebDriversPool[Driver]"
description: "WebDriversPool[Driver]: Ocarina's thread-safe pool, concurrency bounded by a semaphore, supervised warmup and a fresh driver per acquisition."
weight: 1
date: 2026-05-20
series: ["infra"]
series_order: 1
tags: ["ocarina"]
---

# 02.10.01&nbsp;—&nbsp;`WebDriversPool[Driver]`

> Source file: [`src/ocarina/infra/drivers_pool.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/drivers_pool.py)
>
> Thread-safe driver pool, max concurrency enforced by semaphore, monitored async _warmup_, clean _shutdown_. No reuse&nbsp;—&nbsp;every `acquire()` disposes its driver on the way out (clean state).

## Constructor

```python
@final
class WebDriversPool[Driver]:
    def __init__(
        self,
        create_driver: Thunk[BuiltWebDriver[Driver]],
        max_size: int,
        warmup_timeout: float | None = None,
    ) -> None:
        self._create_driver = create_driver
        self._pool: Queue[BuiltWebDriver[Driver]] = Queue(max_size)
        self._semaphore = Semaphore(max_size)
        self._warmup_timeout = (
            warmup_timeout if warmup_timeout is not None and warmup_timeout > 0.1
            else 60.0 * 5
        )
```

| Primitive             | Role                                                                                             |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| `Queue(max_size)`     | Queue of _pre-built_ available drivers.                                                          |
| `Semaphore(max_size)` | Guarantees that **at most `max_size` drivers** live simultaneously (whether queued or acquired). |
| `warmup_timeout`      | Max no-progress delay during warmup before raising `WarmupTimeoutError`. Default 300s.           |

## `acquire()`

```python
@contextmanager
def acquire(self) -> Iterator[Driver]:
    try:
        driver, dispose = self._pool.get_nowait()
    except Empty:
        self._semaphore.acquire()
        try:
            driver, dispose = self._create_driver()
        except Exception:
            self._semaphore.release()
            raise

    try:
        yield driver
    finally:
        with suppress(Exception):
            dispose()
        self._semaphore.release()
```

```
              acquire()
                  │
                  ▼
   ┌──────────────────────────────────┐
   │ pool.get_nowait()                │── OK ─► driver, dispose         ← warmup case
   └──────────────┬───────────────────┘
                  │ Empty
                  ▼
   ┌──────────────────────────────────┐
   │ sem.acquire()                    │  ← blocks if N drivers alive
   └──────────────┬───────────────────┘
                  ▼
   ┌──────────────────────────────────┐
   │ create_driver()                  │── raises ─► sem.release(); raise
   └──────────────┬───────────────────┘
                  ▼
   ┌──────────────────────────────────┐
   │ yield driver                     │  ← caller uses it
   └──────────────┬───────────────────┘
                  ▼
                finally :
                  with suppress : dispose()       ← driver disposed
                  sem.release()                   ← release a slot
```

### 1. No reuse

`Queue.get_nowait()` _consumes_ the entry. Once pulled, the driver never goes back. At the end (`finally`), it's **disposed**.

**No driver is ever used by two tests.**

### 2. No semaphore leak

- If `pool.get_nowait()` returns a driver: we use it, dispose, release. ✅
- If `pool.get_nowait()` raises `Empty`: we acquire the sem, create, use, dispose, release. ✅
- If `create_driver()` raises: we release the sem before propagating. ✅
- If `dispose()` raises: we suppress + release. ✅

Every path releases the semaphore. No leak.

### 3. Concurrency guaranteed ≤ max_size

The semaphore is acquired **before** creation. As long as `N` drivers are alive (created or queued), the `N+1`-th caller waits.

## `warmup()`

```python
def warmup(self) -> None:
    progress = {"count": 0}
    lock = threading.Lock()
    stop_event = threading.Event()

    def worker() -> None:
        while not self._pool.full() and not stop_event.is_set():
            if not self._semaphore.acquire(blocking=False):
                break
            try:
                driver, dispose = self._create_driver()
                self._pool.put((driver, dispose))
                with lock:
                    progress["count"] += 1
            except Exception:
                self._semaphore.release()
                break

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    start_global = time.monotonic()
    last_progress = 0

    while t.is_alive():
        time.sleep(0.5)
        with lock:
            current = progress["count"]

        if current != last_progress:
            last_progress = current
            start_global = time.monotonic()

        if time.monotonic() - start_global > self._warmup_timeout:
            stop_event.set()
            msg = (
                "Warmup stalled (no progress detected)."
                " Some browser processes may still be running."
                " Please check your system (Activity Monitor / Task Manager / Dock)"
                " and close any remaining browser instances."
            )
            self.shutdown()
            raise WarmupTimeoutError(msg)

    t.join()
```

| Thread                     | Role                                                                                                                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Worker** (daemon)        | Creates drivers in a loop while the queue isn't full and `stop_event` isn't set. On every success, increments `progress["count"]`.                                                 |
| **Watchdog** (main thread) | Loops, samples `progress["count"]` every 0.5s. If the value changes, **resets** the timer. If the timer exceeds `warmup_timeout`, `stop_event.set()` + `raise WarmupTimeoutError`. |

A **progress-based** watchdog, not wall clock. 30s to create a driver is fine if progress _advances_. Creation blocking indefinitely → progress stalls → watchdog raises.

## `shutdown()`

```python
def shutdown(self) -> None:
    while not self._pool.empty():
        _, dispose = self._pool.get_nowait()
        with suppress(Exception):
            dispose()
        self._semaphore.release()
```

- Disposes every driver **in the queue** (not the _acquired_ ones&nbsp;—&nbsp;those get handled by their `acquire()` context).
- Releases the matching semaphores.
- `suppress(Exception)`: a `dispose()` that raises gets skipped, we move on.

Called:

1. By `TestSuite.run` on `WarmupTimeoutError`.
2. Via `atexit.register(pool.shutdown)` at process end (see `infra/selenium/create_drivers_pool.py`).

## `WarmupTimeoutError`

```python
class WarmupTimeoutError(Exception):
    """Raised when warmup is blocked (mostly some macOS edge cases)."""
```

"_macOS edge cases_": with headless off and you close a browser window driven by Ocarina, macOS doesn't kill the process behind the window.

That very specific case exposed the possibility of an infinite _hang_, and triggered the naive watchdog.

## Dedicated tests

[`tests/scenarios/test_drivers_pool.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_drivers_pool.py) covers:

- standard acquisition / release,
- warmup,
- WarmupTimeoutError detection when the factor stalls,
- behavior when `create_driver` raises (sem released),
- shutdown.
