---
title: "02.10.02 — DriverBuilder[Driver]"
weight: 2
date: 2026-05-20
series: ["infra"]
series_order: 2
tags: ["ocarina", "selenium"]
---

# 02.10.02&nbsp;—&nbsp;`DriverBuilder[Driver]`

> Source file: [`src/ocarina/infra/driver_builder.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/driver_builder.py)
>
> Encapsulates **profile** handling (often a tmp copy of a user directory) and produces the `(driver, dispose)` pair the pool expects.

## Why a builder?

Building a Selenium driver with a _profile_ requires:

1. **Copy the profile** to a temp folder (otherwise Firefox/Chrome locks the original).
2. **Start the driver** pointing at the temp folder.
3. **At the end**: `driver.quit()`, then delete the temp folder.

`DriverBuilder` factors out those three steps:

```python
class DriverBuilder[Driver]:
    def __init__(
        self,
        *,
        build_driver: Callable[[str], Driver],
        profile_path: str | None = None,
        tmp_dir_prefix: str = ".driver_profile_",
    ) -> None:
        self._build_driver = build_driver
        self._profile_path = profile_path
        self._tmp_dir_prefix = tmp_dir_prefix

    def build(self) -> BuiltWebDriver[Driver]:
        # 1. create a temporary directory (copy of the profile if provided)
        # 2. call self._build_driver(<tmp_dir_path>)
        # 3. return (driver, dispose) where dispose = lambda : driver.quit() + cleanup tmp
        ...
```

`build_driver` is a `Callable[[str], Driver]`: receives the **temp profile path**, returns a ready driver.

## Project side

The canonical example comes from [`ocarina-with-ai-example`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/lib/ext/ocarina/adapters/selenium/create_drivers_pool.py):

```python
def _build_clean_chrome(*, profile_path, driver_path, headless, wait_timeout) -> Chrome:
    service = ChromeService(executable_path=driver_path)
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    if profile_path:
        options.add_argument(f"--user-data-dir={profile_path}")
    # … disable password manager …
    return Chrome(service=service, options=options)


def _create_chrome() -> BuiltSeleniumWebDriver:
    return DriverBuilder(
        build_driver=lambda _profile_path: _build_clean_chrome(
            profile_path=_profile_path,
            driver_path=resolved_driver_path,
            headless=headless,
            wait_timeout=wait_timeout,
        ),
        profile_path=profile_path,
        tmp_dir_prefix=tmp_dir_prefix,
    ).build()
```

- `DriverBuilder(...)` is instantiated on every `_create_chrome()` call.
- `.build()` makes the tmp profile copy (if any), calls `_build_clean_chrome(...)`, returns `(chrome_driver, dispose)`.

## `dispose`

The `dispose` returned by `.build()` must:

1. Call `driver.quit()`.
2. Delete the tmp dir if created.
3. **Never raise** (all exceptions are caught).

That's what the pool uses in its `finally`:

```python
finally:
    with suppress(Exception):
        dispose()
    self._semaphore.release()
```

## Project-side signature

| Parameter        | Type                      | Role                                                      |
| ---------------- | ------------------------- | --------------------------------------------------------- |
| `build_driver`   | `Callable[[str], Driver]` | Receives the tmp profile path, returns the driver         |
| `profile_path`   | `str \| None`             | _Source_ profile path (will be copied to tmp if provided) |
| `tmp_dir_prefix` | `str`                     | Prefix of the tmp dir's name                              |

No `profile_path` → driver launches with a blank profile; `build_driver(...)` gets an empty string or a freshly-created path.

`profile_path` provided → profile gets _copied_ into `tmp_dir_prefix*` and the driver launches on the copy.

## Windows-specific `atexit` cleanup

`create_selenium_auto_cli_store` includes an effect:

```python
def _create_dont_force_delete_tmp_dirs_effect(*, dont_force_delete_tmp_dirs: bool) -> Effect:
    def _clean_all_webdriver_tmp_dirs() -> None:
        # search every /tmp/tmp*/webdriver-py-profilecopy
        # and every /tmp/rust_mozprofile*
        # and delete them
        ...
    def unwrapped() -> None:
        if not dont_force_delete_tmp_dirs and platform.system() == "Windows":
            atexit.register(_clean_all_webdriver_tmp_dirs)
    return unwrapped
```

On **Windows**, Selenium leaves `tmp*\webdriver-py-profilecopy` folders that `driver.quit()` doesn't always clean. The effect registers an `atexit` sweeper for them.

The CLI flag `--dont-force-delete-tmp-dirs` turns it off (rare case where you want to keep the tmp profiles around for inspection).

## Why `DriverBuilder` lives in `infra/`, not in `infra/selenium/`

**Agnostic**: it handles tmp profiles and dispose, knows nothing about Selenium. Could produce `(playwright_browser, dispose)` just as well. `infra/selenium/create_driver.py` is what materializes the Selenium-specific version.
