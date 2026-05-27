---
title: "02.10.03 — Screenshotter[TDriver]"
weight: 3
date: 2026-05-20
series: ["infra"]
series_order: 3
tags: ["ocarina", "selenium"]
---

# 02.10.03&nbsp;—&nbsp;`Screenshotter[TDriver]`

> Source file: [`src/ocarina/infra/screenshotter.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/screenshotter.py)
>
> Generic, _thread-safe_ screenshot utility. Driver-agnostic via a `Protocol`, configurable via a `dataclass`. Supports burst.

## `Protocol`

```python
class ScreenshotDriver(Protocol):
    def save_screenshot(self, path: str) -> bool:
        """Save standard viewport screenshot."""
```

That's it. _Any object_ with `save_screenshot(path: str) -> bool` qualifies. Selenium WebDriver has it natively (`driver.save_screenshot`), Playwright can be wrapped, a fake driver in tests exposes it trivially.

## `ScreenshotterConfig[TDriver]`

```python
@dataclass(frozen=True)
class ScreenshotterConfig[TDriver: ScreenshotDriver]:
    output_dir: Path
    file_ext: str = ".png"
    health_check: HealthCheck[TDriver] | None = None
    save_full_page: SaveFullPageScreenshot[TDriver] | None = None
    default_burst_delay: float = 0.5
    max_filename_retries: int = 500
    uuid_length: int = 8
```

| Field                  | Type                                      | Role                                                              | Default       |
| ---------------------- | ----------------------------------------- | ----------------------------------------------------------------- | ------------- |
| `output_dir`           | `Path`                                    | Screenshot directory                                              | &nbsp;—&nbsp; |
| `file_ext`             | `str`                                     | Extension (`.png`, `.jpg`)                                        | `.png`        |
| `health_check`         | `HealthCheck[TDriver] \| None`            | `(driver) -> None` that raises if the driver is dead              | `None`        |
| `save_full_page`       | `SaveFullPageScreenshot[TDriver] \| None` | `(driver, path) -> bool` for full-page screenshots (Firefox only) | `None`        |
| `default_burst_delay`  | `float`                                   | Delay between 2 shots in burst mode                               | `0.5`s        |
| `max_filename_retries` | `int`                                     | Max attempts to generate a unique name                            | `500`         |
| `uuid_length`          | `int`                                     | UUID suffix length in the name                                    | `8`           |

Immutable. Configure once, ship.

## `Screenshotter[TDriver]`

```python
class Screenshotter[TDriver: ScreenshotDriver]:
    def __init__(self, driver: TDriver, logger: ILogger, config: ScreenshotterConfig[TDriver]) -> None:
        self._driver = driver
        self._logger = logger
        self._config = config
        self._output_dir = config.output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)
```

Note: `output_dir.mkdir(parents=True, exist_ok=True)` at construction. `exist_ok=True` kills any race between threads.

## `take_screenshot`

```python
def take_screenshot(
    self,
    *,
    prefix: str = "",
    shots: int | None = None,
    burst_delay: float | None = None,
) -> None:
    dead_driver_msg = "Cannot take screenshot, driver died."

    def _check_driver_health() -> Exception | None:
        if self._config.health_check is None:
            return None
        try:
            self._config.health_check(self._driver)
        except Exception as exc:
            return exc
        return None

    dead_driver_exc = _check_driver_health()
    if dead_driver_exc:
        self._logger.exception(dead_driver_msg, exc=dead_driver_exc)
        return

    if shots is None:
        shots = 1
    if burst_delay is None:
        burst_delay = self._config.default_burst_delay
    burst = shots > 1

    with _SCREENSHOTTER_LOCK:
        for i in range(1, shots + 1):
            if burst and i > 1:
                time.sleep(burst_delay)
            normalized_file_path = self._generate_unique_file_path(prefix=prefix, counter=i if burst else -1)
            if normalized_file_path is None:
                self._logger.error(f"FAILED TO TAKE SCREENSHOT! (Can't generate unique file path for prefix '{prefix}')")
                continue

            success = False
            if self._config.save_full_page is not None:
                success = self._config.save_full_page(self._driver, str(normalized_file_path))
            if not success:
                success = self._driver.save_screenshot(str(normalized_file_path))

            if success:
                self._logger.info(f"{SCREENSHOT_SUCCESS_PREFIX}{normalized_file_path}")
            else:
                dead_driver_exc = _check_driver_health()
                if dead_driver_exc:
                    self._logger.exception(dead_driver_msg, exc=dead_driver_exc)
                    return
                self._logger.error(f"FAILED TO TAKE SCREENSHOT! ({normalized_file_path})")
```

### 1. Healthcheck first

If `health_check` is configured and raises, we **abort** the screenshot, log the exception, and stop.

On the Selenium side, the healthcheck is `driver_healthcheck`: a simple `driver.title` that raises if the driver is dead.

### 2. `shots > 1` mode = burst

The API allows a burst:

```python
screenshotter.take_screenshot(prefix="animation", shots=5, burst_delay=0.2)
```

→ 5 successive shots 0.2s apart. Handy for _capturing an animation_, or **catching ephemeral states at fail time** (an error toast that pops up then disappears).

```python
def _take_screenshot_on_fail(driver, logger, prefix):
    create_selenium_screenshotter(driver, logger).take_screenshot(
        prefix=prefix, burst_delay=0.350, shots=4
    )
```

→ Test fails → **4 shots** 350 ms apart.

### 3. Unique filename generation with retry

```python
def _generate_unique_file_path(self, *, prefix: str, counter: int) -> Path | None:
    retries = self._config.max_filename_retries  # 500
    uuid_length = self._config.uuid_length        # 8
    burst = counter != -1
    for _ in range(retries):
        unique_id = uuid.uuid4().hex[:uuid_length]
        file_name = f"{prefix}_{unique_id}" if prefix else f"{unique_id}"
        base_path = self._output_dir / file_name
        normalized_file_path = (
            f"{base_path}_{counter}{self._config.file_ext}" if burst
            else f"{base_path}{self._config.file_ext}"
        )
        if not Path(normalized_file_path).exists():
            return Path(normalized_file_path)
    return None
```

UUID v4 truncated to 8 hex chars → 16⁸ ≈ 4 billion possible names. Collisions forcing a retry are rare.

### 4. Fallback `save_full_page → save_screenshot`

If `save_full_page` is configured (e.g., with Firefox), try it first. If it returns `False`, fall back to `save_screenshot` (standard viewport).

```python
success = False
if self._config.save_full_page is not None:
    success = self._config.save_full_page(self._driver, str(normalized_file_path))
if not success:
    success = self._driver.save_screenshot(str(normalized_file_path))
```

**Full-page screenshots** when the driver supports them, graceful fallback otherwise.

## `_selenium_save_full_page`

`infra/selenium/create_screenshotter.py`:

```python
def _selenium_save_full_page(driver: WebDriver, path: str) -> bool:
    if hasattr(driver, "save_full_page_screenshot"):
        return cast("FirefoxWebDriver", driver).save_full_page_screenshot(path)
    return False
```

Firefox has `save_full_page_screenshot`; Chrome doesn't. The `hasattr` checks without crashing.

## Prefix `"Screenshot: "`

```python
SCREENSHOT_SUCCESS_PREFIX: Final[str] = "Screenshot: "
```

When a screenshot is taken, we log:

```
Screenshot: /path/to/.screenshots/SUCCESS_a3f2b1c4.png
```

`"Screenshot: "` is a **needle** consumed _downstream_ by the `generate_docx_proof` plugin, which greps the logs:

```python
_DEFAULT_SCREENSHOT_NEEDLE = "Screenshot: "
```

When the DOCX plugin hits this line, it **inserts the image** into the Word document. So the contract is:

> A `Screenshot: <path>` log ⇒ an image inserted into the DOCX at the same spot in the log.

## Dedicated tests

[`tests/scenarios/test_screenshotter.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_screenshotter.py) covers:

- single shot,
- burst,
- healthcheck that raises (abort),
- name collisions (retries),
- fallback `save_full_page → save_screenshot`,
- thread safety (multiple threads, verifying we have N distinct shots).
