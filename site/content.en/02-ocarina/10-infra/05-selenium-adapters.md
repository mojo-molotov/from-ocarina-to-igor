---
title: "02.10.05 — Selenium adapters"
description: "Ocarina's Selenium adapters: everything that realizes POMBase, WebDriversPool and Screenshotter, outside the pure DSL and replaceable by Playwright."
weight: 5
date: 2026-05-20
series: ["infra"]
series_order: 5
tags: ["ocarina", "selenium"]
---

# 02.10.05&nbsp;—&nbsp;Selenium adapters

> Source folder: [`src/ocarina/infra/selenium/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/selenium)
>
> Everything that materializes the abstractions (`POMBase`, `WebDriversPool`, `Screenshotter`) in Selenium flavor. **Lives outside the pure DSL**&nbsp;—&nbsp;a Playwright project just swaps this folder.

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
