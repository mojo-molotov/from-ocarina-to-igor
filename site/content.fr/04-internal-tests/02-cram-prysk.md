---
title: "04.02 — Cram tests (prysk)"
description: "Les tests CLI d'Ocarina au format cram : des fichiers .t décrivant commandes shell et sortie attendue, exécutés via prysk."
weight: 2
date: 2026-05-20
series: ["tests-internes"]
series_order: 2
---

# 04.02&nbsp;—&nbsp;Cram tests (`prysk`)

> Tests CLI au format _cram_&nbsp;: un fichier `.t` contient des commandes shell et leur sortie attendue. Outil utilisé&nbsp;: `prysk` (réécriture moderne de `cram`).

## Fichier `.t`

```
Valid args produce a deterministic parsed config

  $ touch driver
  $ "$PYTHON" "$TESTDIR/_demo_cli.py" --browser firefox --driver-path driver --workers 3 --wait-timeout 20 --logger terminal
  browser=firefox
  driver_path=driver
  headless=True
  workers=3
  wait_timeout=20
  logger=terminal
  only=()
  exclude=()
```

- Première ligne&nbsp;: titre (commentaire pour l'humain).
- Ligne vide.
- Lignes commençant par ` $`&nbsp;: commande shell exécutée.
- Lignes suivantes (indent 2)&nbsp;: sortie attendue.

Si la sortie réelle diffère&nbsp;: le test fail.

## `_demo_cli.py`

```python
# tests/cram/_demo_cli.py
"""Tiny CLI that pushes a SeleniumCliStoreSingleton and prints its content."""

from ocarina.opinionated.cli.selenium.cli_store_singleton import (
    SeleniumCliStoreSingleton as CliStoreSingleton,
)
from ocarina.opinionated.cli.selenium.create_cli_store import (
    create_selenium_auto_cli_store,
)

if __name__ == "__main__":
    CliStoreSingleton().push(create_selenium_auto_cli_store())
    for key in ("browser", "driver_path", "headless", "workers", "wait_timeout", "logger", "only", "exclude"):
        print(f"{key}={CliStoreSingleton().get(key)}")
```

→ Imprime _déterministiquement_ le contenu du store. Cram peut comparer cet output ligne par ligne.

## Fichiers `.t`

| Fichier                      | Vérifie                                                          |
| ---------------------------- | ---------------------------------------------------------------- |
| `cli_happy_path.t`           | Combinaison valide produit la bonne sortie                       |
| `cli_defaults.t`             | Defaults sont parsés correctement                                |
| `cli_help.t`                 | `--help` affiche les _n_ flags                                   |
| `cli_invalid_browser.t`      | `--browser=banana` lève proprement                               |
| `cli_invalid_wait_timeout.t` | `--wait-timeout=0` lève (`is_not_zero`)                          |
| `cli_missing_driver_path.t`  | `--browser=chrome` sans `--driver-path` lève                     |
| `cli_not_headless_flag.t`    | `--not-headless` inverse le default (stored as `headless=False`) |
| `cli_only_flag.t`            | `--only id1 id2` parse une liste                                 |
| `cli_exclude_flag.t`         | `--exclude id1 id2` parse une liste                              |
| `cli_only_exclude_mutex.t`   | `--only` et `--exclude` ensemble lève                            |

## `cli_help.t`

```
CLI --help lists every declared flag

Pipe through grep to stay resilient to unrelated wording changes in argparse's
help output. Sorted unique output → alphabetical by first-differing character.

  $ "$PYTHON" "$TESTDIR/_demo_cli.py" --help 2>&1 | grep -o -- '--\(driver-path\|profile-path\|browser\|not-headless\|workers\|logger\|wait-timeout\|dont-force-delete-tmp-dirs\|only\|exclude\)' | sort -u
  --browser
  --dont-force-delete-tmp-dirs
  --driver-path
  --exclude
  --logger
  --not-headless
  --only
  --profile-path
  --wait-timeout
  --workers
```

On ne teste pas la **sortie complète** de `--help` (qui change avec les versions d'argparse), juste qu'**au minimum** les flags listés apparaissent. On `grep` chaque flag, on `sort -u`. Si un flag manque&nbsp;: la sortie est différente, le test fail.

On teste ce qui compte, pas plus.

## Les fichiers `.t` Playwright

Le launcher Playwright a sa propre CLI (`PlaywrightCliStoreSingleton`), donc son propre runner cram&nbsp;: `_demo_pw_cli.py`, qui écrit (_print_) le store Playwright au lieu du store Selenium.

```python
# tests/cram/_demo_pw_cli.py
from ocarina.opinionated.cli.playwright.cli_store_singleton import (
    PlaywrightCliStoreSingleton as CliStoreSingleton,
)
from ocarina.opinionated.cli.playwright.create_cli_store import create_playwright_cli_store

CliStoreSingleton().push(create_playwright_cli_store())
store = CliStoreSingleton()
for key in ("browser", "profile_path", "headless", "workers", "wait_timeout",
            "logger", "video_dir", "trace_dir", "only", "exclude"):
    print(f"{key}={store.get(key)}")
```

Cinq fichiers `.t` dédiés, qui reflètent la surface Selenium **en retirant** `--driver-path` (Playwright est livré avec ses propres navigateurs directement) et **en ajoutant** `--video-dir` /&nbsp;`--trace-dir`&nbsp;:

| Fichier                         | Vérifie                                                                       |
| ------------------------------- | ----------------------------------------------------------------------------- |
| `pw_cli_defaults.t`             | Defaults Playwright parsés (`workers=5`, `wait_timeout=10`, `video_dir=None`) |
| `pw_cli_help.t`                 | `--help` liste les flags&nbsp;: **pas** de `--driver-path`, mais `--video-dir` /&nbsp;`--trace-dir` |
| `pw_cli_invalid_browser.t`      | `--browser=banana` lève (seuls `chromium`/`firefox`/`webkit` sont valides)                 |
| `pw_cli_invalid_wait_timeout.t` | `--wait-timeout=0` lève                                                        |
| `pw_cli_only_exclude_mutex.t`   | `--only` et `--exclude` ensemble lève                                          |

Même philosophie que côté Selenium&nbsp;: on `grep` les flags, on `sort -u`, on ne teste pas la sortie complète d'argparse. La CLI est une surface utilisateur donc cram est l'outil naturel, quel que soit le backend.

## `Makefile`

```makefile
.PHONY: cram-test
cram-test:
ifeq ($(OS),Windows_NT)
	@echo "N A P O L E O N  D I S A P P R O V E S  W I N D O W S"
else
	@echo "Running cram tests..."
	PYTHON="$(CURDIR)/$(VENV_PYTHON)" "$(CURDIR)/$(VENV_BIN)/prysk" tests/cram/
endif
```

1. **Skip sur Windows**. Prysk n'a pas le même support shell sur Windows&nbsp;; Napoléon a dit à l'auteur de préférer skipper proprement plutôt que de se battre avec.
2. **`PYTHON` injecté**&nbsp;: Prysk substitue `$PYTHON` dans les fichiers `.t` par le chemin du venv Python.
3. **`prysk tests/cram/`**&nbsp;: exécute tous les `.t` du dossier.

## Pourquoi cram plutôt que pytest pour la CLI

| Cram                                          | pytest                                                         |
| --------------------------------------------- | -------------------------------------------------------------- |
| Test = commande shell + sortie attendue (1-1) | Test = code Python qui appelle, capture stdout/stderr, asserte |
| Lisible par non-Python                        | Demande de comprendre Python                                   |
| Capture stderr inclus naturellement           | `capsys` à configurer                                          |
| Pas de mock à mettre en place                 | Souvent des mocks                                              |
| Échec lisible (diff line-by-line)             | Plus de bruit                                                  |

La CLI est une _interface utilisateur_, pas du code Python. Cram est l'outil naturel. C'est le "test système" le plus approprié ici.

## `make test`

```makefile
.PHONY: test
test: cram-test
	@echo "Running tests..."
	-pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
```

→ `make test` enchaîne&nbsp;:

1. `cram-test` (les `.t`).
2. `pytest` avec sortie Allure + `--hypothesis-show-statistics`.

Si `cram-test` fail, `pytest` ne tourne pas (dépendance de cible Makefile). Le `-` devant `pytest` permet de continuer même si pytest échoue (pour produire le rapport Allure quand même).
