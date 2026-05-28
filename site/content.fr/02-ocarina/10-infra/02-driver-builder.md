---
title: "02.10.02 — DriverBuilder[Driver]"
description: "DriverBuilder[Driver] : la gestion du profil navigateur via une copie temporaire, produisant la paire driver et dispose attendue par la pool."
weight: 2
date: 2026-05-20
series: ["infra"]
series_order: 2
tags: ["ocarina", "selenium"]
---

# 02.10.02&nbsp;—&nbsp;`DriverBuilder[Driver]`

> Fichier source&nbsp;: [`src/ocarina/infra/driver_builder.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/driver_builder.py)
>
> Encapsule la gestion du **profil** (souvent une copie tmp d'un répertoire utilisateur) et produit la paire `(driver, dispose)` attendue par la pool.

## Pourquoi un builder&nbsp;?

Quand on construit un driver Selenium avec un _profil_, il faut&nbsp;:

1. **Copier le profil** dans un dossier temporaire (sinon Firefox/Chrome locked sur le profil original).
2. **Lancer le driver** en pointant vers le dossier temporaire.
3. **À la fin**&nbsp;: `driver.quit()` _puis_ supprimer le dossier temporaire.

`DriverBuilder` factorise ces trois étapes&nbsp;:

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
        # 1. crée un répertoire temporaire (copie du profil si fourni)
        # 2. appelle self._build_driver(<tmp_dir_path>)
        # 3. retourne (driver, dispose) où dispose = lambda : driver.quit() + cleanup tmp
        ...
```

Le `build_driver` est une `Callable[[str], Driver]`&nbsp;: il reçoit le **chemin du profil temporaire** et doit retourner un driver prêt.

## Côté projet

L'exemple typique vient de [`ocarina-with-ai-example`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/lib/ext/ocarina/adapters/selenium/create_drivers_pool.py)&nbsp;:

```python
def _build_clean_chrome(*, profile_path, driver_path, headless, wait_timeout) -> Chrome:
    service = ChromeService(executable_path=driver_path)
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    if profile_path:
        options.add_argument(f"--user-data-dir={profile_path}")
    # … désactivation password manager …
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

- `DriverBuilder(...)` est instancié à chaque appel `_create_chrome()`.
- `.build()` construit la copie tmp du profil (s'il y a), appelle `_build_clean_chrome(...)`, retourne `(chrome_driver, dispose)`.

## `dispose`

Le `dispose` retourné par `.build()` doit&nbsp;:

1. Appeler `driver.quit()`.
2. Supprimer le tmp dir si créé.
3. Ne **jamais lever** (toutes les exceptions sont attrapées).

C'est ce que la pool utilise dans son `finally`&nbsp;:

```python
finally:
    with suppress(Exception):
        dispose()
    self._semaphore.release()
```

## Signature côté projet

| Paramètre        | Type                      | Rôle                                                  |
| ---------------- | ------------------------- | ----------------------------------------------------- |
| `build_driver`   | `Callable[[str], Driver]` | Reçoit le path du tmp profile, retourne le driver     |
| `profile_path`   | `str \| None`             | Path du profil _source_ (sera copié en tmp si fourni) |
| `tmp_dir_prefix` | `str`                     | Préfixe du nom du tmp dir                             |

Si `profile_path is None`&nbsp;: le driver est lancé avec un profil vierge, `build_driver(...)` reçoit une string vide ou un path nouvellement créé.

Si `profile_path` est fourni&nbsp;: le profil est _copié_ dans `tmp_dir_prefix*` et le driver est lancé sur cette copie.

## `atexit` cleanup spécifique Windows

`create_selenium_auto_cli_store` inclut un effet&nbsp;:

```python
def _create_dont_force_delete_tmp_dirs_effect(*, dont_force_delete_tmp_dirs: bool) -> Effect:
    def _clean_all_webdriver_tmp_dirs() -> None:
        # cherche tous les /tmp/tmp*/webdriver-py-profilecopy
        # et tous les /tmp/rust_mozprofile*
        # et les supprime
        ...
    def unwrapped() -> None:
        if not dont_force_delete_tmp_dirs and platform.system() == "Windows":
            atexit.register(_clean_all_webdriver_tmp_dirs)
    return unwrapped
```

Sur **Windows**, Selenium laisse des `tmp*\webdriver-py-profilecopy` qui ne sont pas toujours nettoyés par `driver.quit()`. L'effet enregistre un cleanup `atexit` qui balaye ces dossiers.

Le flag CLI `--dont-force-delete-tmp-dirs` permet de désactiver ce comportement (rare cas où l'utilisateur veut conserver les profiles tmp pour inspection).

## Pourquoi `DriverBuilder` vit dans `infra/`, pas dans `infra/selenium/`

**Agnostique**&nbsp;: il sait gérer un profil tmp et un dispose, mais ne sait rien de Selenium. Il pourrait aussi bien produire un `(playwright_browser, dispose)`. C'est `infra/selenium/create_driver.py` qui matérialise la version Selenium spécifique.
