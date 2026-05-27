---
title: "02.10.03 — Screenshotter[TDriver]"
weight: 3
date: 2026-05-20
series: ["infra"]
series_order: 3
tags: ["ocarina", "selenium"]
---

# 02.10.03&nbsp;—&nbsp;`Screenshotter[TDriver]`

> Fichier source&nbsp;: [`src/ocarina/infra/screenshotter.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/screenshotter.py)
>
> Utilitaire de capture d'écran générique, _thread-safe_, agnostique du driver via un `Protocol`, configurable via une `dataclass`. Supporte le burst.

## `Protocol`

```python
class ScreenshotDriver(Protocol):
    def save_screenshot(self, path: str) -> bool:
        """Save standard viewport screenshot."""
```

C'est tout. _N'importe quel objet_ qui a une méthode `save_screenshot(path: str) -> bool` est utilisable. Selenium WebDriver l'a nativement (`driver.save_screenshot`), Playwright peut être wrappé, un fake driver en test l'expose trivialement.

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

| Champ                  | Type                                      | Rôle                                                                           | Default       |
| ---------------------- | ----------------------------------------- | ------------------------------------------------------------------------------ | ------------- |
| `output_dir`           | `Path`                                    | Répertoire des screenshots                                                     | &nbsp;—&nbsp; |
| `file_ext`             | `str`                                     | Extension (`.png`, `.jpg`)                                                     | `.png`        |
| `health_check`         | `HealthCheck[TDriver] \| None`            | `(driver) -> None` qui lève si driver mort                                     | `None`        |
| `save_full_page`       | `SaveFullPageScreenshot[TDriver] \| None` | `(driver, path) -> bool` pour les screenshots pleine page (Firefox uniquement) | `None`        |
| `default_burst_delay`  | `float`                                   | Délai entre 2 shots en mode burst                                              | `0.5`s        |
| `max_filename_retries` | `int`                                     | Max essais pour générer un nom unique                                          | `500`         |
| `uuid_length`          | `int`                                     | Longueur du suffix UUID dans le nom                                            | `8`           |

Immutable. On configure une fois et on exporte.

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

Note&nbsp;: `output_dir.mkdir(parents=True, exist_ok=True)` à la construction. Pas de race condition entre threads grâce à `exist_ok=True`.

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

### 1. Healthcheck avant tout

Si `health_check` est configuré et lève, on **abandonne** le screenshot, on log l'exception, on arrête.

Côté Selenium, le healthcheck est `driver_healthcheck`&nbsp;: un simple `driver.title` qui lève si le driver est dead.

### 2. Mode `shots > 1` = burst

L'API permet un burst&nbsp;:

```python
screenshotter.take_screenshot(prefix="animation", shots=5, burst_delay=0.2)
```

→ 5 shots successifs espacés de 0.2s. Utile pour _capturer une animation_, ou pour **capturer les états éphémères au moment d'un fail** (toast d'erreur qui s'affiche puis disparaît).

```python
def _take_screenshot_on_fail(driver, logger, prefix):
    create_selenium_screenshotter(driver, logger).take_screenshot(
        prefix=prefix, burst_delay=0.350, shots=4
    )
```

→ Quand un test fail, on prend **4 shots** espacés de 350ms.

### 3. Génération de nom unique avec retry

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

UUID v4 tronqué à 8 hex chars&nbsp;→&nbsp;16⁸ ≈ 4 milliards de noms possibles. Les collisions poussant à retry sont très rares.

### 4. Fallback `save_full_page → save_screenshot`

Si `save_full_page` est configuré (par ex.&nbsp;: avec Firefox), on l'essaie d'abord. S'il retourne `False`, on retombe sur `save_screenshot` (standard viewport).

```python
success = False
if self._config.save_full_page is not None:
    success = self._config.save_full_page(self._driver, str(normalized_file_path))
if not success:
    success = self._driver.save_screenshot(str(normalized_file_path))
```

Permet d'avoir des **screenshots pleine page** quand le driver le supporte, et un fallback gracieux sinon.

## `_selenium_save_full_page`

`infra/selenium/create_screenshotter.py`&nbsp;:

```python
def _selenium_save_full_page(driver: WebDriver, path: str) -> bool:
    if hasattr(driver, "save_full_page_screenshot"):
        return cast("FirefoxWebDriver", driver).save_full_page_screenshot(path)
    return False
```

Firefox a une méthode `save_full_page_screenshot`&nbsp;; Chrome ne l'a pas. Le `hasattr` permet de tester sans crasher.

## Préfixe `"Screenshot: "`

```python
SCREENSHOT_SUCCESS_PREFIX: Final[str] = "Screenshot: "
```

Quand un screenshot est pris, on log&nbsp;:

```
Screenshot: /path/to/.screenshots/SUCCESS_a3f2b1c4.png
```

Le `"Screenshot: "` est une **needle** consommée _en aval_ par le plugin `generate_docx_proof` qui parse les logs&nbsp;:

```python
_DEFAULT_SCREENSHOT_NEEDLE = "Screenshot: "
```

Quand le plugin DOCX rencontre cette ligne, il **insère l'image** dans le document Word. Le contrat est donc&nbsp;:

> Un log `Screenshot: <path>` ⇒ une image insérée dans le DOCX au même endroit du log.

## Tests dédiés

[`tests/scenarios/test_screenshotter.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_screenshotter.py) couvre&nbsp;:

- shot simple,
- burst,
- healthcheck qui lève (abandon),
- collision de noms (retries),
- fallback `save_full_page → save_screenshot`,
- thread safety (multiple threads, vérification qu'on a bien N shots distincts).
