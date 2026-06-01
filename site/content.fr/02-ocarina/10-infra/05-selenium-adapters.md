---
title: "02.10.05 — Adapters Selenium"
description: "Les adapters Selenium d'Ocarina : tout ce qui matérialise POMBase, WebDriversPool et Screenshotter, hors du DSL pur et reflété par l'adapter Playwright livré."
weight: 5
date: 2026-05-20
series: ["infra"]
series_order: 5
tags: ["ocarina", "selenium"]
---

# 02.10.05&nbsp;—&nbsp;Adapters Selenium

> Dossier source&nbsp;: [`src/ocarina/infra/selenium/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/selenium)
>
> Tout ce qui matérialise les abstractions (`POMBase`, `WebDriversPool`, `Screenshotter`) en version Selenium. **Vit hors du DSL pur**&nbsp;—&nbsp;et depuis la `1.1.3` il a un jumeau&nbsp;: [`src/ocarina/infra/playwright/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/playwright) livre exactement les mêmes contrats en version Playwright. Changer de backend, c'est désormais choisir un dossier, pas l'écrire.

## Fichiers du dossier

| Fichier                   | Rôle                                                                         |
| ------------------------- | ---------------------------------------------------------------------------- |
| `create_driver.py`        | `_build_firefox`, `_build_chrome`, `_build_edge`, `_build_safari` + dispatch |
| `create_drivers_pool.py`  | `create_selenium_drivers_pool` (utilise `DriverBuilder` + `WebDriversPool`)  |
| `create_screenshotter.py` | `create_selenium_screenshotter` + `_selenium_save_full_page` (Firefox-only)  |
| `driver_healthcheck.py`   | `driver_healthcheck(driver)`&nbsp;—&nbsp;ping `driver.title`                 |
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
    # … identique à Chrome avec EdgeService/EdgeOptions/Edge …


def _build_safari(*, profile_path, driver_path, headless, wait_timeout) -> WebDriver:
    # … Safari ne supporte ni driver_path (utilise safaridriver natif macOS),
    #   ni profile_path (pas de profile custom), ni headless …
```

### 1. `implicitly_wait` défini une seule fois

Chaque builder appelle `driver.implicitly_wait(wait_timeout)` _une_ fois. Donc, tout `find_element` qui ne trouve pas l'élément immédiatement attend jusqu'à `wait_timeout` secondes avant de lever `NoSuchElementException`.

Le `CLAUDE.md` du projet IA insiste&nbsp;:

> **Implicit wait is set by the CLI (`--wait-timeout`). Never read, modify, or work around it in POM/test code&nbsp;—&nbsp;it is framework infrastructure. No `driver.implicitly_wait(...)` outside the Ocarina driver builder.**

Cette discipline garantit que tout le projet utilise **le même timeout**.  
Si on veut un timeout custom, on passe par EC (_expected condition_) de Selenium ou équivalent.

### 2. Différence headless Firefox /&nbsp;Chrome

```
Firefox: "-headless"          # 1 dash
Chrome:  "--headless=new"     # 2 dash, valeur "new"
Edge:    "--headless=new"     # idem Chrome (le moteur est Chromium)
Safari:  pas supporté
```

C'est une particularité historique de chaque driver. Détail d'implémentation.

### 3. Profile par browser

- **Firefox**&nbsp;: `FirefoxProfile(path)`&nbsp;—&nbsp;_objet Profile_ assigné à `options.profile`.
- **Chrome/Edge**&nbsp;: `--user-data-dir=<path>`&nbsp;—&nbsp;_argument CLI_.
- **Safari**&nbsp;: pas supporté.

### 4. Safari = aucun driver_path

Safari utilise `safaridriver` qui est livré avec macOS. Pas besoin de driver binary séparé. La CLI Selenium accepte (et valide) ce cas dans `_create_validate_dependent_args_effect`&nbsp;:

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

L'utilisateur qui passe `--browser safari --driver-path /path/to/something` reçoit une erreur explicite.

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

1. Crée un `WebDriversPool` avec `create_driver` qui ferme sur le projet (`browser`, `driver_path`, …).
2. `atexit.register(drivers_pool.shutdown)`&nbsp;: garantit le shutdown propre à la sortie du process.
3. Retourne la pool. Le caller (typiquement `main.py`) la passe à `TestSuite`.

## `driver_healthcheck.py`

```python
def driver_healthcheck(driver: WebDriver) -> None:
    try:
        driver.title  # noqa: B018 — ping only, no assignment intended.
    except Exception as exc:
        raise DriverDiedError from exc
```

**Ping minimaliste**&nbsp;: lire `driver.title` (qui est un `@property`, donc envoie bien une instruction _under-the-hood_) provoque un round-trip au navigateur. Si le navigateur est mort, ça lève, on ré-emballe en `DriverDiedError`.

`DriverDiedError` est défini dans [`src/ocarina/custom_errors/test_framework/driver_died.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_errors/test_framework/driver_died.py)

## `SeleniumTitleMixin`

```python
class SeleniumTitleMixin:
    _driver: WebDriver

    def get_current_title(self) -> str:
        return self._driver.title
```

### 1. L'attribut typé `_driver: WebDriver`

Le Holy Book parle de **détrompeur de typage**&nbsp;:

> `SeleniumTitleMixin` joue donc aussi un rôle de **détrompeur de typage**. Tenter d'y assigner une valeur incorrecte produira immédiatement une erreur de typage&nbsp;:
>
> ```python
> self._driver = "lol"
>
> # error: Incompatible types in assignment (expression has type "str", variable has type "WebDriver")
> ```

C'est-à-dire&nbsp;: sans le mixin, on pourrait écrire `class MyPage(POMBase): def __init__(self): self._driver = SomethingElse`. Avec le mixin, _mypy_ refuse l'assignation.

### 2. L'implémentation triviale de `get_current_title`

`return self._driver.title`. Une ligne. C'est tout. Mais l'utilisateur n'a pas à l'écrire pour chaque POM&nbsp;: il hérite via ce mixin.

## MRO

```python
@final
class HomePage(SeleniumTitleMixin, POMBase):
    ...
```

→ `SeleniumTitleMixin` d'abord, `POMBase` ensuite. C'est important pour le MRO Python&nbsp;: `get_current_title` est cherchée dans `SeleniumTitleMixin` avant `POMBase` (et trouvée, alors que `POMBase.get_current_title` est `@abstractmethod`).

Le `CLAUDE.md` du projet IA documente le pattern pour le `SeleniumBackAndForwardNavigationMixin` (projet-side)&nbsp;:

> Place before `SeleniumTitleMixin` in the MRO&nbsp;:
>
> ```python
> class MyPage(SeleniumBackAndForwardNavigationMixin, SeleniumTitleMixin, POMBase):
>     ...
> ```

## Le jumeau Playwright

> Dossier source&nbsp;: [`src/ocarina/infra/playwright/`](https://github.com/mojo-molotov/ocarina/tree/main/src/ocarina/infra/playwright)

L'adapter Playwright reprend la structure de l'adapter Selenium, fichier pour fichier (`create_driver`, `create_drivers_pool`, `create_screenshotter`, `driver_healthcheck`, `mixins`), avec **un fichier en plus**&nbsp;: `driver.py`. Ce fichier porte tout le travail&nbsp;: l'API _sync_ de Playwright est thread-affine, ce qui collisionne avec le modèle threadé d'Ocarina (pool, warmup, Watcher). La réponse est un acteur épinglé à un seul thread propriétaire, avec marshalling par `submit` et ceiling de liveness contre les drivers morts.

Ce modèle de concurrence a sa propre page dédiée, diagrammes à l'appui&nbsp;: [`06-playwright-actor.md`](06-playwright-actor.md).
