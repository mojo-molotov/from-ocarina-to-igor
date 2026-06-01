---
title: "02.10.06 — The Playwright actor: one owner thread"
description: "How Ocarina reconciles Playwright's thread-affine sync API with its threaded model: a single-thread actor, marshalling through submit, and a liveness ceiling against dead drivers."
weight: 6
date: 2026-06-01
series: ["infra"]
series_order: 6
tags: ["ocarina", "playwright", "concurrency"]
---

# 02.10.06&nbsp;—&nbsp;The Playwright actor: one owner thread

> Source folder: [`src/ocarina/infra/playwright/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/playwright)
>
> The Playwright adapter mirrors the Selenium one file for file (`create_driver`, `create_drivers_pool`, `create_screenshotter`, `driver_healthcheck`, `mixins`), with **one extra file**: [`driver.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/playwright/driver.py). That file deserves a chapter of its own. It is what reconciles Playwright's _sync_ API&nbsp;—&nbsp;inherently bound to one thread&nbsp;—&nbsp;with Ocarina's threaded model (pool, warmup, Watcher). The model has been stressed and stabilized; it holds.

## The problem: Playwright's sync API is thread-affine

Playwright's **sync** API binds every object it hands out&nbsp;—&nbsp;`Playwright`, `Browser`, `BrowserContext`, `Page`, `Locator`, …&nbsp;—&nbsp;to the thread that called `sync_playwright().start()`. Under the hood it is a _greenlet_ pinned to that thread. Touching any of them from another thread raises:

```
greenlet.error: cannot switch to a different thread
```

That collides head-on with Ocarina's threaded model, which has **three** concurrent points of contact with a single driver:

```
   ┌──────────────────┐
   │  warmup thread   │  WebDriversPool.warmup() pre-builds drivers in a
   │  (1, dedicated)  │  dedicated thread, then pushes them onto the Queue.
   └────────┬─────────┘
            │ build → Queue
            ▼
   ┌──────────────────┐
   │  worker threads  │  Workers acquire a driver from the Queue and run
   │  (N, parallel)   │  the test chain on it.
   └────────┬─────────┘
            │ + concurrently
            ▼
   ┌──────────────────┐
   │  watcher daemon  │  The Watcher polls alongside the chain, in its own
   │  (1 per test)    │  daemon thread, and reads the page.
   └──────────────────┘
```

So a driver is **built on one thread** (warmup) and **used from another** (worker), while a **third** (watcher) observes it. With Playwright's sync API as-is, that is three guaranteed `greenlet.error`s.

## The solution: an actor pinned to one thread

`PlaywrightDriver` wraps Playwright in an **actor** (_Actor model_): it owns a single _owner thread_. Every Playwright object lives on that thread, and **nobody else ever touches it directly**. Each interaction is _marshalled_ onto the owner thread via `submit()`.

```
   warmup / worker / watcher threads          owner thread (1, private)
   ─────────────────────────────────          ─────────────────────────
                                                 ┌─────────────────┐
   driver.submit(fn) ──────┐                     │  Playwright     │
                           │   Queue[(fn,fut)]   │  Browser        │
   driver.submit(fn) ──────┼────────────────────▶│  BrowserContext │
                           │                     │  Page, Locator  │
   driver.submit(fn) ──────┘                     │                 │
            ▲                                     │  fn(page) runs  │
            │         future.result()             │  HERE, and only │
            └─────────────────────────────────────│  HERE           │
                       result (plain data)        └─────────────────┘
```

The _handle_ (`PlaywrightDriver`) is therefore safe to create on one thread and use from another: only the **work** ever touches Playwright, and that work always runs on the owner thread. Ocarina's pool, warmup, and worker parallelization survive intact, without giving up the sync API.

```python
def submit[T](self, fn: Callable[[Page], T]) -> T:
    if threading.get_ident() == self._owner_ident:
        raise RuntimeError("Re-entrant submit() on the owner thread would deadlock.")
    if self._dead:
        raise DriverDiedError("PlaywrightDriver is dead: a previous call exceeded its timeout.")
    if self._closed:
        raise RuntimeError("PlaywrightDriver has been disposed.")
    future = self._owner.submit(lambda: fn(self._page))
    try:
        return future.result(timeout=self._call_timeout_s)
    except FuturesTimeoutError as exc:
        self._dead = True
        self._closed = True
        raise DriverDiedError(...) from exc
```

## Why not `ThreadPoolExecutor(max_workers=1)`

A `ThreadPoolExecutor(max_workers=1)` would _almost_ do the job: one worker, submissions handled in order. Almost. The catch is at **process exit**.

`ThreadPoolExecutor` workers are **not** daemons: they are _joined_ by an `atexit` hook. If the worker is wedged on a dead Playwright _pipe_ (the browser crashed, the transport stopped answering), it never returns and that exit-time `join` **hangs the process forever**. On a CI run, that is a job that never finishes.

So Ocarina swaps the executor for an `_OwnerThread`: a single **daemon** thread draining a `Queue` of `(callable, Future)`.

```
   _OwnerThread._run()  (daemon)
   ───────────────────────────────────────────────
   while True:
       item = queue.get()          # block until the next submission
       if item is None:            # stop sentinel
           return
       fn, future = item
       try:    future.set_result(fn())
       except: future.set_exception(...)   # any failure marshalled back to caller
```

The difference is in how thread death is handled:

| `ThreadPoolExecutor(max_workers=1)`                       | `_OwnerThread` (daemon)                                                    |
| --------------------------------------------------------- | ------------------------------------------------------------------------- |
| Non-daemon worker, joined at `atexit`                     | Daemon: **abandoned** at process exit                                     |
| Worker wedged on a dead pipe&nbsp;→&nbsp;`join` hangs exit    | Worker wedged&nbsp;→&nbsp;never joined, the process exits anyway          |
| No control over the `join`                                | We **never** join ourselves (a running future is not cancellable)         |

The accepted cost: a _per-death leak_. When a driver dies wedged, its thread, the stuck call, and its closure stay referenced until process exit. That is the deliberate trade against hanging the whole run. Better to leak a dead thread than to never finish. At process exit the leak is reclaimed anyway, since the daemon thread is torn down with the process.

## The `submit` contract

Three rules, all enforced by the code:

1. **Return plain data.** `fn` must return flat, thread-safe values (`str`, `bool`, `bytes`, `None`): never a live `Page`, `Locator`, or `ElementHandle`, which are owner-thread-bound and unusable elsewhere. `PlaywrightTitleMixin` shows the pattern: `return self._driver.submit(lambda page: page.title())`.
2. **No re-entrancy.** A `submit()` (or `quit()`) called _from_ the owner thread would await a future that same thread is meant to resolve: a deadlock. The code detects it (`threading.get_ident() == self._owner_ident`) and raises an explicit `RuntimeError` instead of freezing.
3. **The call is bounded.** `future.result(timeout=call_timeout)` puts a ceiling on it.

## `call_timeout`: a liveness ceiling, not a deadline

The subtlest point. `call_timeout` (180s default) is **not** a per-operation deadline. It is a _liveness_ ceiling: it exists only to turn an _infinite hang_ on a dead owner thread into an eventual, **bounded** failure.

It is deliberately **decoupled** from `wait_timeout` (which bounds Playwright's auto-waits) and set **generously**, well above the slowest legitimate single `submit` possible.

```
   submit(fn)
      │
      ├── future resolves before call_timeout ──────────▶ returns the result ✓
      │
      └── call_timeout exceeded
              │  the owner thread is STILL stuck on fn
              ▼
          driver marked _dead = True, _closed = True
          the running future is ABANDONED (not cancellable)
              │
              ▼
          raise DriverDiedError  ──▶  caller retries with a fresh driver
```

Raise `call_timeout` whenever a single call legitimately runs longer.  
Note: such a call can usually be split into several `submit`s instead, which remains the recommended approach above all.

## `is_dead` ≠ `is_closed`

| Property    | Meaning                                                                  | The driver is…           |
| ----------- | ------------------------------------------------------------------------ | ------------------------ |
| `is_closed` | `quit()` was called: **voluntary** disposal.                             | disposed normally |
| `is_dead`   | a call exceeded `call_timeout`: the owner thread is **stuck**.           | to be **replaced** |

`driver_healthcheck` leans on this:

```python
def playwright_driver_healthcheck(driver: PlaywrightDriver) -> None:
    if driver.is_dead:
        raise DriverDiedError(...)        # genuinely dead
    if driver.is_closed:
        return                            # voluntarily disposed → benign race, return
    try:
        driver.submit(lambda page: page.title())   # minimal ping
    except DriverDiedError:
        raise
    except Exception as exc:
        raise DriverDiedError from exc
```

## Boot is bounded too

A driver can crash **during** startup (failed launch, locked profile). So boot is marshalled like any other call, and bounded by the same `call_timeout`:

```python
boot = self._owner.submit(lambda: self._boot(...))
try:
    self._page = boot.result(timeout=self._call_timeout_s)
except FuturesTimeoutError as exc:
    raise DriverDiedError("Playwright boot did not complete…") from exc
except PlaywrightError as exc:
    raise DriverDiedError("Playwright boot failed…") from exc
finally:
    if not booted:
        self._dead = True
        self._closed = True
        self._owner.stop()
```

## The actor slots in, unchanged

Because `PlaywrightDriver` exposes `quit()` and `save_screenshot()`, it satisfies the **existing generic contracts**: the [`DriverBuilder`](02-driver-builder.md) disposal (`dispose: Effect`) and the `ScreenshotDriver` protocol of the [`Screenshotter`](03-screenshotter.md). Nothing else in `infra/` ever knows it is talking to Playwright.

```
   DriverBuilder.dispose ──▶ driver.quit()            (marshalled teardown, bounded)
   Screenshotter         ──▶ driver.save_screenshot() (submit → page.screenshot)
   healthcheck           ──▶ driver.submit(page.title)
```

`quit()` is **idempotent** and marshals its own teardown (stop tracing, close context, stop Playwright) onto the owner thread, bounded by `call_timeout`, then asks the thread to stop. If called from the owner thread it raises, since, just like a re-entrant `submit`, it would deadlock.

## Pool and warmup

`create_playwright_drivers_pool` reuses the **backend-agnostic** `WebDriversPool` with no modification:

```python
drivers_pool = WebDriversPool(
    create_driver=lambda: create_playwright_driver(browser=..., headless=..., ...),
    max_size=max_size,
    warmup_timeout=warmup_timeout,
)
atexit.register(drivers_pool.shutdown)
```

> Each driver owns a private thread, so warmup is safe: a driver created **in the warmup thread** can be consumed by **any worker** because all Playwright calls are marshalled onto the owner thread.

The thread that _creates_ the driver is never the thread that _runs_ Playwright. Warmup can pre-build ahead of time, workers pull from the Queue, and nobody trips a `greenlet.error`.

## The Watcher: observe, don't mutate

A `Watcher` polls in its own daemon thread. A Playwright watcher **MAY** read the page from its callback, via `watcher.driver.submit(...)`, marshalled like everything else, so safe across threads. But it is governed by a convention, not a ban:

- **OBSERVE, don't MUTATE.** The watcher runs concurrently with the test chain; mutating the page (click/fill) from a watcher corrupts the test's state. Read-only is the user's responsibility.
- **Always go through `submit`**, never touch `page` directly.
- **Return flat data** from the lambda (`str`/`bool`/`bytes`), never a live `Locator` or `ElementHandle`.
- **Performance caveat**: each watcher read serializes on the owner thread, alongside the test chain's own `submit` calls. Contention scales with poll frequency (`poll_interval`). Selenium watchers, sharing the driver directly, are freer here.

```python
def watch_banner(watcher: PlaywrightWatcher) -> None:
    text = watcher.driver.submit(
        lambda page: page.inner_text("#cookie-banner")
        if page.locator("#cookie-banner").count()
        else ""
    )
    if text and text not in watcher.cache:
        watcher.cache.add(text)
        watcher.report(f"Cookie banner: {text!r}", label="BANNER")
```

## Video and trace

| Option             | Effect                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------ |
| `record_video_dir` | Records a session video (must be set at context creation: Playwright cannot enable it afterwards).           |
| `trace_dir`        | Captures a Playwright trace (`trace_<id>.zip`, open with `playwright show-trace`).                           |

## Conclusion

Playwright's sync API is pinned to one thread. The actor reconciles the two by confining Playwright. The rest of the infra only ever sees an ordinary driver with `quit()` and `save_screenshot()`.
