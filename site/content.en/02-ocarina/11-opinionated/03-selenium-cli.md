---
title: "02.11.03 — Auto CLI store + flags + validation"
description: "Ocarina's ready-made Selenium CLI store: the driver, profile, browser and headless flags, with their defaults and validation."
weight: 3
date: 2026-05-20
series: ["opinionated"]
series_order: 3
tags: ["ocarina", "selenium"]
---

# 02.11.03&nbsp;—&nbsp;Auto CLI store + flags + validation

> Source file: [`src/ocarina/opinionated/cli/selenium/create_cli_store.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/selenium/create_cli_store.py)

## Flags

| Flag                           | Default                         | Type                      | Validation                            |
| ------------------------------ | ------------------------------- | ------------------------- | ------------------------------------- |
| `--driver-path`                | `""`                            | `str`                     | `is_file` (except `--browser safari`) |
| `--profile-path`               | `None`                          | `str`                     | `is_none` OR `is_dir`                 |
| `--browser`                    | `None` (required)               | `str`                     | argparse `choices` (per OS)           |
| `--not-headless`               | `False` (= headless by default) | `bool` (`store_true`)     | _phantom_                             |
| `--workers`                    | `5`                             | `int`                     | `is_positive` + `is_not_zero`         |
| `--logger`                     | `"terminal+file"`               | `str`                     | `choices=LOGGERS_CHOICES`             |
| `--wait-timeout`               | `10`                            | `int`                     | `≤ 60`, `> 0`                         |
| `--dont-force-delete-tmp-dirs` | `False`                         | `bool` (`store_true`)     | _phantom_                             |
| `--only`                       | `[]`                            | `list[str]` (`nargs="+"`) | _phantom_ + mutex                     |
| `--exclude`                    | `[]`                            | `list[str]` (`nargs="+"`) | _phantom_ + mutex                     |

```python
_DEFAULT_WORKERS_AMOUNT = 5
_DEFAULT_LOGGER: SupportedLogger = "terminal+file"
_DEFAULT_BROWSER_AUTOMATION_TIMEOUT = 10
_MAX_BROWSER_AUTOMATION_TIMEOUT = 60
```

## `Literal[...]`

```python
type SeleniumCliStoreKeys = Literal[
    "driver_path", "profile_path", "browser", "headless", "workers",
    "logger", "wait_timeout", "force_delete_tmp_dirs", "only", "exclude",
]
```

These keys are the store's whole vocabulary. Call-sites use them: `store.get("workers")`, `store.get("browser")`, etc.

Note: `"headless"` (positive) vs `--not-headless` (negative flag); same for `"force_delete_tmp_dirs"` (positive) vs `--dont-force-delete-tmp-dirs` (negative flag). Deliberate: the store holds the positive value ("_are we headless? yes/no_"), the CLI flag uses the negative wording (because the defaults are "_yes_").

## Post-parse effects

The `effects_factory=lambda ns: (...)` produces an `Effects` collection (tuple of `Effect`).

### 1. Set

```python
lambda: store.set("driver_path", ns.driver_path),
lambda: store.set("profile_path", ns.profile_path),
lambda: store.set("browser", ns.browser),
lambda: store.set("headless", not ns.not_headless),         # ← inversion
lambda: store.set("workers", ns.workers),
lambda: store.set("logger", ns.logger),
lambda: store.set("wait_timeout", ns.wait_timeout),
lambda: store.set("force_delete_tmp_dirs", not ns.dont_force_delete_tmp_dirs),  # ← inversion
lambda: store.set("only", tuple(ns.only)),
lambda: store.set("exclude", tuple(ns.exclude)),
```

Notes:

- **Inversions** on `headless` and `force_delete_tmp_dirs`: we store the positive value.
- **`tuple(...)`** on `only`/`exclude`: convert to an immutable tuple.

### 2. "create validate only exclude mutex effect"

```python
def _create_validate_only_exclude_mutex_effect(ns: Namespace) -> Effect:
    def _validate() -> None:
        if ns.only and ns.exclude:
            raise ValueError("--only and --exclude cannot be used together")
    return _validate
```

**Inter-arg** validation. Native `argparse` can't express it; we do it as a post-parse effect.

### 3. "create validate dependent args effect"

```python
def _validate_non_safari() -> None:
    is_unset: dict[str, bool] = {
        "--driver-path": ns.driver_path is None and ns.driver_path != "",
        "--browser": ns.browser is None,
    }
    all_explicit = all(not v for v in is_unset.values())
    if not all_explicit:
        raise ValueError("These parameters must all be specified:\n" + ...)


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


def _validate() -> None:
    if ns.browser == "safari":
        _validate_safari()
    else:
        _validate_non_safari()
```

Conditional validation:

- `safari`: rejects `--driver-path` and `--profile-path`.
- Otherwise: requires `--driver-path` and `--browser`.

### 4. "create validate driver path"

```python
def _validate_driver_path() -> None:
    if ns.browser != "safari":
        validate(ns.driver_path).assert_that(
            is_file, msg="--driver-path should be a path to a file"
        ).execute().raise_if_invalid()
```

Non-Safari → `--driver-path` must be an _existing_ file.

### 5. "create dont force delete tmp dirs effect"

```python
def unwrapped() -> None:
    if not dont_force_delete_tmp_dirs and platform.system() == "Windows":
        atexit.register(_clean_all_webdriver_tmp_dirs)
```

Windows + no opt-out → registers an `atexit` that cleans `tmp*\webdriver-py-profilecopy` at process exit.

## Dispatch

```python
def create_selenium_auto_cli_store() -> CliStore[SeleniumCliStoreKeys]:
    match platform.system():
        case "Windows":
            return create_selenium_win_cli_store()
        case "Darwin":
            return create_selenium_macos_cli_store()
        case "Linux":
            return create_selenium_linux_cli_store()
        case other:
            raise RuntimeError(f"Unsupported platform: {other}")
```

## `*_cli_store` per-OS

```python
_WIN_BROWSER_CHOICES: list[SupportedSeleniumBrowser] = ["chrome", "firefox", "edge"]
_MACOS_BROWSER_CHOICES: list[SupportedSeleniumBrowser] = ["chrome", "firefox", "safari"]
_LINUX_BROWSER_CHOICES: list[SupportedSeleniumBrowser] = ["chrome", "firefox"]
```

```python
def create_selenium_win_cli_store() -> CliStore[SeleniumCliStoreKeys]:
    return _create_selenium_cli_store(_WIN_BROWSER_CHOICES)


def create_selenium_macos_cli_store() -> CliStore[SeleniumCliStoreKeys]:
    return _create_selenium_cli_store(_MACOS_BROWSER_CHOICES)


def create_selenium_linux_cli_store() -> CliStore[SeleniumCliStoreKeys]:
    return _create_selenium_cli_store(_LINUX_BROWSER_CHOICES)
```

| OS      | Browsers offered            |
| ------- | --------------------------- |
| Windows | chrome, firefox, **edge**   |
| macOS   | chrome, firefox, **safari** |
| Linux   | chrome, firefox             |

`edge` isn't offered on macOS / Linux. `safari` is macOS-only.

## "create selenium cli store"

```python
def _create_selenium_cli_store(browser_choices: list[SupportedSeleniumBrowser]) -> CliStore[SeleniumCliStoreKeys]:
    store = _create_store()
    cli = _create_cli(store, browser_choices)
    cli.parse()
    return store
```

1. **`_create_store()`**: builds the `CliStore[SeleniumCliStoreKeys]` with its `_CliField`s and validators.
2. **`_create_cli(store, browser_choices)`**: builds the `CliBuilder` with its `CliArg`s and `effects_factory`.
3. **`cli.parse()`**: fires parse + validation + effects. _Invalid_ → process exits with code 2.
4. **Returns the store**, now **populated**.

## Related Cram tests

[`tests/cram/`](https://github.com/mojo-molotov/ocarina/tree/main/tests/cram):

| `.t` file                    | Verifies                                          |
| ---------------------------- | ------------------------------------------------- |
| `cli_help.t`                 | `--help` shows the flags                          |
| `cli_happy_path.t`           | A valid combination produces the right output     |
| `cli_defaults.t`             | Defaults parsed correctly                         |
| `cli_invalid_browser.t`      | `--browser=banana` raises cleanly                 |
| `cli_invalid_wait_timeout.t` | `--wait-timeout=0` raises (`is_not_zero`)         |
| `cli_missing_driver_path.t`  | `--browser=chrome` without `--driver-path` raises |
| `cli_not_headless_flag.t`    | `--not-headless` inverts the default              |
| `cli_only_flag.t`            | `--only id1 id2` parses a list                    |
| `cli_exclude_flag.t`         | id.                                               |
| `cli_only_exclude_mutex.t`   | Both together raises                              |

See [`../../04-internal-tests/02-cram-prysk.md`](../../04-internal-tests/02-cram-prysk.md)
