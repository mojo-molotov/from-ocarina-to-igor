---
title: "02.09 — Ports: ILogger, ITakeScreenshot"
weight: 9
date: 2026-05-20
series: ["ocarina"]
series_order: 9
---

# 02.09&nbsp;—&nbsp;Ports: `ILogger`, `ITakeScreenshot`

> Source folder: [`src/ocarina/ports/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/ports)
>
> Two ports. That's it. Everything else (`WebDriversPool`, `Screenshotter`, etc.) lives under `infra/`, not `ports/`. The line is sharp: a _port_ is an abstraction the DSL sits on; an _infra_ is the implementation of _adapters_.

## `ILogger`

```python
class ILogger(ABC):
    @abstractmethod
    def set_prefix(self, prefix_thunk: Thunk[str]) -> Self: ...

    @abstractmethod
    def set_domain_taxonomy(self, taxonomy: tuple[str, ...]) -> Self: ...

    @abstractmethod
    def raw(self, *args: object, stream: SupportsWrite[str] | None = None, **kwargs: object) -> None: ...

    @abstractmethod
    def critical(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def error(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def warning(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def info(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def debug(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def test_name(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def success(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def exception(self, msg: str, *args, exc: Exception | None = None, **kwargs) -> None: ...

    @abstractmethod
    def cleanup(self) -> None: ...
```

| Method                                      | Semantics                                                                                                          |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `set_prefix(thunk)`                         | **Lazy** prefix applied on every log (for timestamps, threads…). Returns `Self` for chaining.                      |
| `set_domain_taxonomy(taxonomy)`             | Sets the domain hierarchy (`(cycle, campaign, suite, test)`). Critical for `FileLogger`, which builds a file tree. |
| `raw(*args, stream=None)`                   | Raw write, no format (used by the report plugins).                                                                 |
| `critical / error / warning / info / debug` | Standard levels. Every method accepts `exc=` to pass an exception and format it.                                   |
| `test_name(msg)`                            | Custom level: announces the running test (`logger.test_name(test.name)`).                                          |
| `success(msg)`                              | Custom level: passed assertion (used by the `.success(...)` handlers).                                             |
| `exception(msg, exc=)`                      | Logs an exception with the full traceback.                                                                         |
| `cleanup()`                                 | End-of-life: flush + close (for `FileLogger`). Recycles the log file between retries.                              |

## Three things that are _not_ in `ILogger`

- **No `set_level()`**: level handling is the implementation's call (e.g., `MutedLogger` filters everything).
- **No `add_handler()`**: no `logging.Logger`-style stdlib API. Composition happens by instantiating different loggers (`PrintAndFileLogger` wraps both).
- **No `child(name)`**: taxonomy is passed _as a block_ via `set_domain_taxonomy`.

## `set_prefix(thunk)`

```python
logger.set_prefix(lambda: f"[{datetime.now().isoformat()}]")
```

A `str` would be computed _at `set_prefix` time_ and frozen. A `Thunk` recomputes the prefix _on every log call_. Perfect for timestamps.

```python
exceptions_logger = PrintLogger().set_prefix(
    lambda: concat_metadata(
        format_utc_date_metadata_str,
        format_current_thread_metadata_str,
    )
)
```

The resulting prefix looks like `[UTC_DATE::2026-05-18T09:42:31.123456+00:00][THREAD::ThreadPoolExecutor-0_2]`.

`[UTC_DATE::...]` is consumed _downstream_ by the DOCX plugin, which rewrites it as a formatted local date (`[05/18/2026 | 11h42:31.123456]`). The format is a **contract** between the logger and the generation plugin.

## `set_domain_taxonomy(taxonomy)`

```python
logger.set_domain_taxonomy(("e2e", "Dashboard login", "Login happy paths", "Login - without OTP"))
```

Consequence for `FileLogger`: creates `e2e/Dashboard login/Login happy paths/Login - without OTP.log` under `base_dir`. See [`11-opinionated/04-loggers.md`](11-opinionated/04-loggers.md).

## `ITakeScreenshot[Driver]`

```python
# src/ocarina/ports/itake_screenshot.py
class ITakeScreenshot[Driver](Protocol):
    def __call__(
        self,
        driver: Driver,
        logger: ILogger,
        category: str,
    ) -> None: ...
```

- **Protocol (PEP 544)**: _structural type_&nbsp;—&nbsp;any callable with the right signature qualifies.
- **Generic on `Driver`**: `ITakeScreenshot[WebDriver]` is `(WebDriver, ILogger, str) -> None`.
- **No return**: taking a screenshot is an `Effect` (Ocarina vocabulary) that may silently fail.

```python
def take_screenshot(driver: WebDriver, logger: ILogger, category: str) -> None:
    create_selenium_screenshotter(driver, logger).take_screenshot(prefix=category)
```

→ See [`10-infra/03-screenshotter.md`](10-infra/03-screenshotter.md) for the internal mechanic.

## Why these two ports and not others?

Why no `IDriversPool`? `ITestExecutor`? `IInvariant`?

**Ocarina's extension pattern isn't inheritance**, it's **composition through typed adapters**. The DSL classes (`TestSuite`, `TestExecutor`, `TestFlow`, `WebDriversPool`) are _concrete_ and take _dependencies_ via `__init__`. Change behavior by passing different _instances_.

The only abstractions _worth_ promoting to ports:

- `ILogger`: multiple canonical implementations (`Print`, `File`, `PrintAndFile`, `Muted`)&nbsp;—&nbsp;users can write their own.
- `ITakeScreenshot[Driver]`: called _everywhere_, and you want to mock it / reroute it (e.g., in CI: screenshot to S3 instead of local disk).

Everything else is _composed_, not inherited.

## `cleanup()`

Recall ([`05-orchestration/03-test-flow-retries.md`](05-orchestration/03-test-flow-retries.md)):

```python
if outcome.should_retry and attempt < max_attempts:
    logger_with_taxonomy.cleanup()           # ◄── HERE
    time.sleep(attempt)
    continue
```

For `FileLogger`, `cleanup()` closes the current file and recycles it. The next attempt writes to a _fresh_ file.

For `PrintLogger`, `cleanup()` is a no-op.

## `cleanup()` is _not_ a context manager `__exit__`

`ILogger` is _shared_ across attempts&nbsp;—&nbsp;its lifetime is the test's, not an attempt's. The context-manager pattern (`with logger: ...`) wouldn't cleanly _reset_ between retries.
