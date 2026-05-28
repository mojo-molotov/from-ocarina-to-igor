---
title: "02.07 — Watcher[Driver]"
description: "Watcher[Driver]: the parallelized observer running as a daemon thread alongside the scenario to catch stray toasts, popups and validations."
weight: 7
date: 2026-05-20
series: ["ocarina"]
series_order: 7
tags: ["watcher", "selenium"]
---

# 02.07&nbsp;—&nbsp;`Watcher[Driver]`

> Source file: [`src/ocarina/dsl/testing/watcher.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/watcher.py)
>
> Parallelized observer running as a _daemon thread_ alongside the `test_chain`. Built to catch **unpredictable frictions with no direct impact on the scenario** that pop up _while_ the scenario runs: random error toasts, parasitic validations, unexpected popups.

## The problem

Holy Book quote (_First real-world hurdles_):

> Even more surprisingly: apps displaying error toasts for no apparent reason, or forms flagging validation errors on inputs that are actually correct, without blocking the journey.
>
> These errors are the most annoying to detect, because they're _painless_. You can't just see a crash and add a _retry policy_ while waiting for the bug to be fixed. They're, so to speak, invisible.
>
> What's left would be to massacre the test scenarios or resort to “ninja techniques.” Ocarina refuses both options.
>
> The solution: _watchers_.

## Code

```python
@final
class Watcher[Driver]:
    def __init__(
        self,
        *,
        callback: Callable[[Watcher[Driver]], None],
        name: str,
        poll_interval: float | None = None,
    ) -> None:
        self._callback = callback
        self._poll_interval = (
            poll_interval if poll_interval is not None and poll_interval > 0.1 else 0.5
        )
        self._stop_event: threading.Event | None = None
        self._cache: set[str] = set()
        self._thread: threading.Thread | None = None
        self._logger: ILogger | None = None
        self._take_screenshot: ITakeScreenshot[Driver] | None = None
        self._driver: Driver | None = None
        self.name = name
```

| Parameter       | Type                                | Role                                                                | Default       |
| --------------- | ----------------------------------- | ------------------------------------------------------------------- | ------------- |
| `callback`      | `Callable[[Watcher[Driver]], None]` | Function called on every poll cycle. Receives the `Watcher` itself. | &nbsp;—&nbsp; |
| `name`          | `str`                               | Watcher name (for logger scoping)                                   | &nbsp;—&nbsp; |
| `poll_interval` | `float \| None`                     | Delay between two callback calls. Min 0.1s.                         | 0.5           |

## Lifecycle

```
1. Watcher(callback=..., name="cookies", poll_interval=0.8)    # construction, inert

2. watcher.start(driver, logger, take_screenshot)
       │
       ├─ stop_event = Event()                       # new event per start
       ├─ self._stop_event = stop_event              # memorized
       ├─ self._thread = Thread(target=_loop,
       │                        args=(stop_event,),
       │                        daemon=True)         # daemon: doesn't block shutdown
       └─ thread.start()

3. test_chain runs in parallel; the thread loops:
       │
       └─ _loop(stop_event) :
            while not stop_event.is_set() :
                with suppress(Exception) :
                    self._callback(self)
                stop_event.wait(self._poll_interval)

4. watcher.stop()
       │
       ├─ self._stop_event.set()                     # stop signal
       └─ self._thread.join(timeout=poll_interval * 2)
```

## `start()`

```python
def start(self, driver, logger, take_screenshot) -> None:
    # Defensively terminate any thread leaked from a previous start()
    # whose stop()/join() timed out. Its loop holds the previous Event
    # in its local frame; setting it here guarantees the leaked thread
    # exits at the end of its current callback iteration instead of
    # racing with the new thread on shared self._driver / self._logger.
    if self._stop_event is not None:
        self._stop_event.set()

    self._driver = driver
    self._logger = logger
    self._take_screenshot = take_screenshot
    stop_event = threading.Event()
    self._stop_event = stop_event
    self._thread = threading.Thread(
        target=self._loop, args=(stop_event,), daemon=True
    )
    self._thread.start()
```

### 1. `stop_event` is passed _as an argument_ to the thread, not via `self`

```python
self._thread = threading.Thread(target=self._loop, args=(stop_event,), daemon=True)
```

If a _previous_ `start()` leaked a thread (because of a `join` timeout), that thread keeps its own `stop_event`. Storing the event only in `self._stop_event` would mean the new `start()` overwrites it, while the old thread runs on with its _old_ event.

`set()` the old `self._stop_event` _before_ replacing it. Each thread accesses its event via its function argument. The old thread sees its event `set()` and exits cleanly at the end of its next poll.

### 2. `daemon=True`

The thread is a _daemon_. Python process exits → thread dies automatically. Nothing blocks shutdown.

### 3. Runtime injection

`driver`, `logger`, `take_screenshot` are **not** passed to the watcher's constructor. They get injected by `start()`&nbsp;—&nbsp;so _per attempt_ (each attempt has its own driver). Lines up with a test's lifecycle.

## `_loop`

```python
def _loop(self, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        with suppress(Exception):
            self._callback(self)
        stop_event.wait(self._poll_interval)
```

1. **`with suppress(Exception)`**: callback can raise **anything**, silently caught. _A watcher must never crash a test._
2. **`stop_event.wait(poll_interval)`**: same as `time.sleep(poll_interval)`, but wakes instantly if `stop_event.set()` fires. No 0.8s tail wait before yielding.

## `driver`, `cache`, `report` API

```python
@property
def driver(self) -> Driver:
    if self._driver is None:
        raise RuntimeError("Watcher.driver accessed before start() was called.")
    return self._driver

@property
def cache(self) -> set[str]:
    return self._cache

def report(self, message: str, *, label: str = "WATCHER") -> None:
    if (self._driver is None or self._logger is None or self._take_screenshot is None):
        return
    with suppress(Exception):
        self._logger.info(message)
        self._take_screenshot(self._driver, self._logger, label)
```

| Element                            | Description                                                                             |
| ---------------------------------- | --------------------------------------------------------------------------------------- |
| `driver` (property)                | The `WebDriver` injected at `start()`. Raises `RuntimeError` if accessed pre-`start()`. |
| `cache` (property)                 | A mutable `set[str]` for deduplicating reports.                                         |
| `report(message, label="WATCHER")` | Emits an info log + takes a screenshot.                                                 |

## Deduplication pattern

```python
def catch_me_if_you_can_cb(watcher: SeleniumWatcher) -> None:
    elements = watcher.driver.execute_script(
        "return Array.from(document.querySelectorAll('.catch-me-if-you-can'));"
    )
    if not elements:
        return

    for attrs in extract_attrs(elements):
        fingerprint = ":".join(filter(None, [
            attrs["tag"], attrs["text"], attrs["id"], attrs["cls"],
            attrs["name"], attrs["testid"],
        ]))
        if fingerprint in watcher.cache:
            continue
        watcher.cache.add(fingerprint)
        watcher.report(
            f"catch-me-if-you-can element detected: <{attrs['tag']}> {attrs['text']!r}",
            label="CATCH_ME_IF_YOU_CAN",
        )
```

See [`../07-ocarina-example/09-watcher-catch-me.md`](../07-ocarina-example/09-watcher-catch-me.md) for details.

## Why JS in the callback

The Holy Book justifies it:

> The _watcher_ is tolerant to errors: it silently swallows them. There is therefore no point using a Selenium function to capture an element of the page, beyond getting in your own way. Using Selenium's native functions would force you to deal with _implicit timeout_ questions.
>
> Going directly through _JavaScript_ allows you to bypass any internal _polling_ logic and to make the _watcher_'s execution as non-blocking as possible for the test running on the same _driver_.
>
> The sleight of hand then becomes invisible, since it only lasts a few milliseconds.

So: `driver.execute_script("...")` instead of `driver.find_element(...)`. No implicit wait, no Selenium polling, raw JS.

## "Negative only" convention (AI project side)

`ocarina-with-ai-example`'s `CLAUDE.md` formalizes it:

> **Watcher signals are negative only.** A watcher emitting "login succeeded" breaks the contract.

Meaning: a watcher catches **frictions** we didn't want to see. Not successes. Success is the `test_chain`'s job (via `log_success`), not the watcher's.

## `create_selenium_watcher`

```python
# src/ocarina/dsl/testing/selenium/create_watcher.py
type SeleniumWatcher = Watcher[WebDriver]

def create_selenium_watcher(
    *,
    callback: Callable[[SeleniumWatcher], None],
    name: str,
    poll_interval: float | None = None,
):
    return Watcher(callback=callback, name=name, poll_interval=poll_interval)
```

Same idea as `create_selenium_test`&nbsp;—&nbsp;a typed Selenium alias.

## Taxonomy of watcher loggers

When `TestExecutor._start_watchers` is called:

```python
watcher_name = (
    f"[{index + 1}] {test_name} - {watcher.name}"
    if len(watchers) > 1
    else f"{test_name} - {watcher.name}"
)
watcher_taxonomy = (*taxonomy[:-1], watcher_name)
scoped_logger = self._create_logger().set_domain_taxonomy(watcher_taxonomy)
watcher.start(driver, scoped_logger, self._take_screenshot)
```

Consequence for `FileLogger`:

```
.ocarina_logs/
  e2e/
    Randomness/
      Chaotic form/
        Send the chaotic form.log                          ← test's log
        Send the chaotic form - catch-me-if-you-can.log    ← watcher's log
```

The DOCX report can then place the watcher's log _next to_ the test's log, _like a parallel timeline_.
