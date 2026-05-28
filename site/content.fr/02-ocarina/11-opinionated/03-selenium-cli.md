---
title: "02.11.03 — Auto CLI store + flags + validation"
description: "Le store CLI Selenium prêt à l'emploi d'Ocarina : flags driver, profile, browser et headless, avec leurs valeurs par défaut et leur validation."
weight: 3
date: 2026-05-20
series: ["opinionated"]
series_order: 3
tags: ["ocarina", "selenium"]
---

# 02.11.03&nbsp;—&nbsp;Auto CLI store + flags + validation

> Fichier source&nbsp;: [`src/ocarina/opinionated/cli/selenium/create_cli_store.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/selenium/create_cli_store.py)

## Flags

| Flag                           | Default                         | Type                      | Validation                          |
| ------------------------------ | ------------------------------- | ------------------------- | ----------------------------------- |
| `--driver-path`                | `""`                            | `str`                     | `is_file` (sauf `--browser safari`) |
| `--profile-path`               | `None`                          | `str`                     | `is_none` OR `is_dir`               |
| `--browser`                    | `None` (requis)                 | `str`                     | `choices` argparse (par OS)         |
| `--not-headless`               | `False` (= headless par défaut) | `bool` (`store_true`)     | _phantom_                           |
| `--workers`                    | `5`                             | `int`                     | `is_positive` + `is_not_zero`       |
| `--logger`                     | `"terminal+file"`               | `str`                     | `choices=LOGGERS_CHOICES`           |
| `--wait-timeout`               | `10`                            | `int`                     | `≤ 60`, `> 0`                       |
| `--dont-force-delete-tmp-dirs` | `False`                         | `bool` (`store_true`)     | _phantom_                           |
| `--only`                       | `[]`                            | `list[str]` (`nargs="+"`) | _phantom_ + mutex                   |
| `--exclude`                    | `[]`                            | `list[str]` (`nargs="+"`) | _phantom_ + mutex                   |

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

Ces clés sont l'unique vocabulaire du store. Les call-sites les utilisent&nbsp;: `store.get("workers")`, `store.get("browser")`, etc.

Note&nbsp;: `"headless"` (positif) vs `--not-headless` (flag négatif)&nbsp;; idem `"force_delete_tmp_dirs"` (positif) vs `--dont-force-delete-tmp-dirs` (flag négatif). C'est volontaire&nbsp;: le store contient la valeur positive («&nbsp;_est-on headless&nbsp;? oui/non_&nbsp;»), le flag CLI utilise la formulation négative (parce que les défauts sont «&nbsp;_oui_&nbsp;»).

## Effets post-parse

Le `effects_factory=lambda ns: (...)` produit une collection `Effects` (tuple d'`Effect`).

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

Notes&nbsp;:

- **Inversions** sur `headless` et `force_delete_tmp_dirs`&nbsp;: on stocke la valeur positive.
- **`tuple(...)`** sur `only`/`exclude`&nbsp;: on convertit en tuple immuable.

### 2. "create validate only exclude mutex effect"

```python
def _create_validate_only_exclude_mutex_effect(ns: Namespace) -> Effect:
    def _validate() -> None:
        if ns.only and ns.exclude:
            raise ValueError("--only and --exclude cannot be used together")
    return _validate
```

Validation **inter-args**. Pas exprimable par `argparse` natif&nbsp;; on le fait en effet post-parse.

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

Validation conditionnelle&nbsp;:

- Si `safari`&nbsp;: refus de `--driver-path` et `--profile-path`.
- Sinon&nbsp;: exige `--driver-path` et `--browser`.

### 4. "create validate driver path"

```python
def _validate_driver_path() -> None:
    if ns.browser != "safari":
        validate(ns.driver_path).assert_that(
            is_file, msg="--driver-path should be a path to a file"
        ).execute().raise_if_invalid()
```

Si non-Safari&nbsp;: `--driver-path` doit être un fichier _existant_.

### 5. "create dont force delete tmp dirs effect"

```python
def unwrapped() -> None:
    if not dont_force_delete_tmp_dirs and platform.system() == "Windows":
        atexit.register(_clean_all_webdriver_tmp_dirs)
```

Si on est sur Windows et qu'on n'a pas désactivé&nbsp;: enregistre un `atexit` qui nettoie `tmp*\webdriver-py-profilecopy` à la sortie du process.

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

| OS      | Browsers proposés           |
| ------- | --------------------------- |
| Windows | chrome, firefox, **edge**   |
| macOS   | chrome, firefox, **safari** |
| Linux   | chrome, firefox             |

`edge` n'est pas proposé sur macOS /&nbsp;Linux. `safari` n'est proposé que sur macOS.

## "create selenium cli store"

```python
def _create_selenium_cli_store(browser_choices: list[SupportedSeleniumBrowser]) -> CliStore[SeleniumCliStoreKeys]:
    store = _create_store()
    cli = _create_cli(store, browser_choices)
    cli.parse()
    return store
```

1. **`_create_store()`**&nbsp;: crée le `CliStore[SeleniumCliStoreKeys]` avec ses `_CliField` et leurs validators.
2. **`_create_cli(store, browser_choices)`**&nbsp;: crée le `CliBuilder` avec ses `CliArg` et son `effects_factory`.
3. **`cli.parse()`**&nbsp;: déclenche le parse + validation + effets. _Si invalide_, le process quitte avec code 2.
4. **Retourne le store**, désormais **rempli**.

## Cram Tests associés

[`tests/cram/`](https://github.com/mojo-molotov/ocarina/tree/main/tests/cram)&nbsp;:

| Fichier `.t`                 | Vérifie                                      |
| ---------------------------- | -------------------------------------------- |
| `cli_help.t`                 | `--help` affiche les flags                   |
| `cli_happy_path.t`           | Combinaison valide produit la bonne sortie   |
| `cli_defaults.t`             | Defaults parsés correctement                 |
| `cli_invalid_browser.t`      | `--browser=banana` lève proprement           |
| `cli_invalid_wait_timeout.t` | `--wait-timeout=0` lève (`is_not_zero`)      |
| `cli_missing_driver_path.t`  | `--browser=chrome` sans `--driver-path` lève |
| `cli_not_headless_flag.t`    | `--not-headless` inverse le default          |
| `cli_only_flag.t`            | `--only id1 id2` parse une liste             |
| `cli_exclude_flag.t`         | id.                                          |
| `cli_only_exclude_mutex.t`   | Les deux ensemble lève                       |

Cf. [`../../04-internal-tests/02-cram-prysk.md`](../../04-internal-tests/02-cram-prysk.md)
