---
title: "02.10.05 — Selenium adapters"
description: "Ocarina's Selenium adapters: everything that realizes POMBase, WebDriversPool and Screenshotter, outside the pure DSL and mirrored by the shipped Playwright adapter."
weight: 5
date: 2026-05-20
series: ["infra"]
series_order: 5
tags: ["ocarina", "selenium"]
---

# 02.10.05&nbsp;—&nbsp;Selenium adapters

> Source folder: [`src/ocarina/infra/selenium/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/selenium)
>
> Everything that materializes the abstractions (`POMBase`, `WebDriversPool`, `Screenshotter`) in Selenium flavor. **Lives outside the pure DSL**&nbsp;—&nbsp;and since `1.1.3` it has a twin: [`src/ocarina/infra/playwright/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/playwright) ships the exact same contracts in Playwright flavor. Swapping backend is now picking a folder, not writing one.

## Files in the folder

| File                      | Role                                                                         |
| ------------------------- | ---------------------------------------------------------------------------- |
| `create_driver.py`        | `_build_firefox`, `_build_chrome`, `_build_edge`, `_build_safari` + dispatch |
| `create_drivers_pool.py`  | `create_selenium_drivers_pool` (uses `DriverBuilder` + `WebDriversPool`)     |
| `create_screenshotter.py` | `create_selenium_screenshotter` + `_selenium_save_full_page` (Firefox-only)  |
| `driver_healthcheck.py`   | `driver_healthcheck(driver)`&nbsp;—&nbsp;pings `driver.title`                |
| `mixins.py`               | `SeleniumTitleMixin`                                                         |

## `create_driver.py`

```python
def _build_firefox(*, profile_path, driver_path, headless, wait_timeout) -> WebDriver:
    service = FirefoxService(executable_path=driver_path)
    options = FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    if profile_path:
        options.profile = FirefoxProfile(profile_path)
    driver = Firefox(service=service, options=options)
    driver.implicitly_wait(wait_timeout)
    return driver


def _build_chrome(*, profile_path, driver_path, headless, wait_timeout) -> WebDriver:
    service = ChromeService(executable_path=driver_path)
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    if profile_path:
        options.add_argument(f"--user-data-dir={profile_path}")
    driver = Chrome(service=service, options=options)
    driver.implicitly_wait(wait_timeout)
    return driver


def _build_edge(*, profile_path, driver_path, headless, wait_timeout) -> WebDriver:
    # … same as Chrome with EdgeService/EdgeOptions/Edge …


def _build_safari(*, profile_path, driver_path, headless, wait_timeout) -> WebDriver:
    # … Safari supports neither driver_path (uses macOS' native safaridriver),
    #   nor profile_path (no custom profile), nor headless …
```

### 1. `implicitly_wait` set only once

Each builder calls `driver.implicitly_wait(wait_timeout)` _once_. Any `find_element` that doesn't find the element immediately waits up to `wait_timeout` seconds before raising `NoSuchElementException`.

The AI project's `CLAUDE.md` insists:

> **Implicit wait is set by the CLI (`--wait-timeout`). Never read, modify, or work around it in POM/test code&nbsp;—&nbsp;it is framework infrastructure. No `driver.implicitly_wait(...)` outside the Ocarina driver builder.**

This discipline guarantees the whole project runs on **the same timeout**.  
Want a custom one? Go through Selenium's EC (_expected condition_) or equivalent.

### 2. Headless difference: Firefox / Chrome

```
Firefox: "-headless"          # 1 dash
Chrome:  "--headless=new"     # 2 dashes, value "new"
Edge:    "--headless=new"     # same as Chrome (Chromium engine)
Safari:  not supported
```

Historical quirk per driver. Implementation detail.

### 3. Profile per browser

- **Firefox**: `FirefoxProfile(path)`&nbsp;—&nbsp;_Profile object_ assigned to `options.profile`.
- **Chrome/Edge**: `--user-data-dir=<path>`&nbsp;—&nbsp;_CLI argument_.
- **Safari**: not supported.

### 4. Safari = no driver_path

Safari uses `safaridriver`, shipped with macOS. No separate driver binary needed. The Selenium CLI accepts and validates this in `_create_validate_dependent_args_effect`:

```python
def _validate_safari() -> None:
    forbidden: dict[str, bool] = {
        "--driver-path": ns.driver_path is not None and ns.driver_path != "",
        "--profile-path": ns.profile_path is not None,
    }
    specified = [k for k, v in forbidden.items() if v]
    if specified:
        raise ValueError(
            "Safari uses the native macOS safaridriver"
            " — these arguments are not supported:\n"
            + "\n".join(f"  • {p}" for p in specified)
        )
```

A user passing `--browser safari --driver-path /path/to/something` gets an explicit error.

## `create_drivers_pool.py`

```python
def create_selenium_drivers_pool(
    *,
    browser: SupportedSeleniumBrowser,
    driver_path: str,
    headless: bool,
    wait_timeout: int,
    max_size: int,
    profile_path: str | None = None,
    tmp_dir_prefix: str = ".webdriver_profile_",
    warmup_timeout: float | None = None,
) -> SeleniumWebDriversPool:
    drivers_pool = WebDriversPool(
        create_driver=lambda: create_selenium_driver(
            browser=browser, driver_path=driver_path, headless=headless,
            wait_timeout=wait_timeout, profile_path=profile_path,
            tmp_dir_prefix=tmp_dir_prefix,
        ),
        max_size=max_size,
        warmup_timeout=warmup_timeout,
    )
    atexit.register(drivers_pool.shutdown)
    return drivers_pool
```

1. Builds a `WebDriversPool` with `create_driver` closing over the project context (`browser`, `driver_path`, …).
2. `atexit.register(drivers_pool.shutdown)`: clean shutdown on process exit, guaranteed.
3. Returns the pool. The caller (typically `main.py`) hands it to `TestSuite`.

## `driver_healthcheck.py`

```python
def driver_healthcheck(driver: WebDriver) -> None:
    try:
        driver.title  # noqa: B018 — ping only, no assignment intended.
    except Exception as exc:
        raise DriverDiedError from exc
```

**Bare-minimum ping**: reading `driver.title` (a `@property`, so it _does_ send an instruction under the hood) forces a round-trip to the browser. Browser dead → raises, we re-wrap as `DriverDiedError`.

`DriverDiedError` is defined in [`src/ocarina/custom_errors/test_framework/driver_died.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_errors/test_framework/driver_died.py).

## `SeleniumTitleMixin`

```python
class SeleniumTitleMixin:
    _driver: WebDriver

    def get_current_title(self) -> str:
        return self._driver.title
```

### 1. The `_driver: WebDriver` typed attribute

The Holy Book calls it a **typing keyway**:

> `SeleniumTitleMixin` therefore also plays the role of a **typing keyway**. Trying to assign an incorrect value to it produces an immediate type error:
>
> ```python
> self._driver = "lol"
>
> # error: Incompatible types in assignment (expression has type "str", variable has type "WebDriver")
> ```

Without the mixin you could write `class MyPage(POMBase): def __init__(self): self._driver = SomethingElse`. With the mixin, _mypy_ rejects the assignment.

### 2. The trivial `get_current_title` implementation

`return self._driver.title`. One line. The user doesn't write it on every POM&nbsp;—&nbsp;inherited via the mixin.

## MRO

```python
@final
class HomePage(SeleniumTitleMixin, POMBase):
    ...
```

→ `SeleniumTitleMixin` first, `POMBase` second. Important for Python MRO: `get_current_title` is found in `SeleniumTitleMixin` before `POMBase` (where it's `@abstractmethod`).

The AI project's `CLAUDE.md` documents the pattern for `SeleniumBackAndForwardNavigationMixin` (project-side):

> Place before `SeleniumTitleMixin` in the MRO:
>
> ```python
> class MyPage(SeleniumBackAndForwardNavigationMixin, SeleniumTitleMixin, POMBase):
>     ...
> ```

## The Playwright twin&nbsp;—&nbsp;an actor pinned to one thread

> Source folder: [`src/ocarina/infra/playwright/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/playwright)

The Playwright adapter mirrors the Selenium one file-for-file (`create_driver`, `create_drivers_pool`, `create_screenshotter`, `driver_healthcheck`, `mixins`), with **one extra file**: `driver.py`. It exists because of a single hard constraint.

Playwright's **sync** API is _thread-affine_: every object it hands out&nbsp;—&nbsp;`Playwright`, `Browser`, `BrowserContext`, `Page`, `Locator`&nbsp;—&nbsp;is bound to the thread that called `sync_playwright().start()`. Touch one from another thread and it raises `greenlet.error: cannot switch to a different thread`.

That collides head-on with Ocarina's threaded model:

- `WebDriversPool.warmup()` pre-builds drivers in a dedicated warmup thread, then hands them to _worker_ threads through a queue;
- a `Watcher` polls alongside the test chain in its own daemon thread.

So `PlaywrightDriver` wraps Playwright in an **actor**: it owns a single-thread executor, all Playwright objects live on that one _owner thread_, and every interaction is marshalled onto it.

```python
self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ocarina-pw")
self._page = self._executor.submit(self._boot, ...).result()

def submit[T](self, fn: Callable[[Page], T]) -> T:
    ...
    return self._executor.submit(lambda: fn(self._page)).result()
```

The handle is therefore safe to **create on one thread and use from another**&nbsp;—&nbsp;only the _work_ ever touches Playwright, and that work always runs on the owner thread. Ocarina's pool, warmup and the parallélisation of the workers survive untouched, **without giving up the sync API**.

Two rules keep the actor honest:

1. **`submit(fn)` must return plain data** (`str`, `bool`, `bytes`, `None`)&nbsp;—&nbsp;never a live `Page`/`Locator`, which is owner-thread bound and unusable elsewhere. `PlaywrightTitleMixin` shows the pattern: `return self._driver.submit(lambda page: page.title())`.
2. **Re-entrancy is rejected loudly.** A `submit()` (or `quit()`) issued _from_ the owner thread would queue behind the running task and then block on its own `.result()`&nbsp;—&nbsp;a silent deadlock. `PlaywrightDriver` raises a named `RuntimeError` instead of hanging.

Because it exposes `quit()` and `save_screenshot()`, the actor slots into the generic `DriverBuilder` disposal and the `ScreenshotDriver` protocol **unchanged**&nbsp;—&nbsp;nothing else in `infra/` ever learns it is talking to Playwright. Browsers ship with Playwright (`playwright install`&nbsp;—&nbsp;no driver-path), the session always runs through a persistent context (a managed `user-data-dir`, like Selenium), and it can optionally record a video or capture a trace (`trace_<id>.zip`, opened with `playwright show-trace`).
