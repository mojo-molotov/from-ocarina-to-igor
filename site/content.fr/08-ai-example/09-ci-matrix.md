---
title: "08.09 — CI : ai_proof_ci.yml + ai_proof_e2e.yml"
description: "La CI de ocarina-with-ai-example : une PR rapide de lint et typecheck, et un e2e manuel avec matrice Firefox et Chrome, warm-up Heroku et filtrage de stacktrace."
weight: 9
date: 2026-05-20
series: ["ai-example"]
series_order: 9
tags: ["selenium"]
---

# 08.09&nbsp;—&nbsp;CI&nbsp;: `ai_proof_ci.yml` + `ai_proof_e2e.yml`

> Deux workflows. PR rapide (lint+typecheck). e2e manuel avec **matrice Firefox/Chrome** + warm-up Heroku + filtrage stacktrace ChromeDriver.

## `ai_proof_ci.yml`

```yaml
name: ai_proof CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

defaults:
  run:
    shell: bash

jobs:
  lint-and-typecheck:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
          allow-prereleases: true
      - uses: actions/cache@v4
        with:
          path: .venv
          key: venv-${{ runner.os }}-py${{ steps.setup-python.outputs.python-version }}-${{ hashFiles('pyproject.toml') }}
      - name: Install dependencies
        if: steps.cache-venv.outputs.cache-hit != 'true'
        run: |
          python -m venv .venv
          .venv/bin/pip install . ruff mypy mypy-extensions typing-extensions pre-commit

      - name: Ruff format check
        run: .venv/bin/ruff format src/ --check

      - name: Ruff lint
        run: .venv/bin/ruff check src/

      - name: Mypy
        run: .venv/bin/mypy src/
```

| Step              | Cmd                        |
| ----------------- | -------------------------- |
| Ruff format check | `ruff format src/ --check` |
| Ruff lint         | `ruff check src/`          |
| Mypy              | `mypy src/`                |

## `ai_proof_e2e.yml`

```yaml
name: ai_proof e2e

on:
  workflow_dispatch:

defaults:
  run:
    shell: bash

jobs:
  e2e:
    name: e2e (${{ matrix.browser }})
    runs-on: ubuntu-latest
    env:
      FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
      WAIT_TIMEOUT: 15
    strategy:
      fail-fast: false
      matrix:
        include:
          - browser: firefox
            driver: geckodriver
          - browser: chrome
            driver: chromedriver

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
          allow-prereleases: true
      - uses: actions/cache@v4
        with:
          path: .venv
          key: venv-${{ runner.os }}-py${{ steps.setup-python.outputs.python-version }}-${{ hashFiles('pyproject.toml') }}
      - name: Install dependencies
        if: steps.cache-venv.outputs.cache-hit != 'true'
        run: |
          python -m venv .venv
          .venv/bin/pip install . ruff mypy mypy-extensions typing-extensions pre-commit

      # --- Firefox ---

      - name: Install geckodriver
        if: matrix.browser == 'firefox'
        run: |
          GECKO_VERSION=0.36.0
          wget -q https://github.com/mozilla/geckodriver/releases/download/v$GECKO_VERSION/geckodriver-v$GECKO_VERSION-linux64.tar.gz
          tar -xzf geckodriver-v$GECKO_VERSION-linux64.tar.gz
          chmod +x geckodriver

      - name: Setup Firefox
        if: matrix.browser == 'firefox'
        uses: browser-actions/setup-firefox@fcf821c621167805dd63a29662bd7cb5676c81a8

      # --- Chrome ---

      - name: Install chromedriver
        if: matrix.browser == 'chrome'
        run: |
          CHROME_VER=$(google-chrome-stable --version | grep -oP '\d+\.\d+\.\d+\.\d+')
          wget -q -O chromedriver.zip \
            "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VER}/linux64/chromedriver-linux64.zip"
          unzip -q chromedriver.zip
          mv chromedriver-linux64/chromedriver ./chromedriver
          chmod +x ./chromedriver

      # --- Warm-up ---

      - name: Warm up Heroku dyno
        run: |
          # CURA runs on a Heroku dyno that sleeps after inactivity.
          # Tests hitting a cold dyno produce timeouts (false fails) and slow
          # confirmations (false passes on gap tests). Wake it explicitly
          # before any browser opens.
          curl -sf --retry 6 --retry-delay 5 --retry-all-errors \
            --max-time 30 https://katalon-demo-cura.herokuapp.com/ > /dev/null
          echo "Dyno is warm"

      # --- Run ---

      - name: Run e2e cycle
        run: |
          # ChromeDriver release builds ship without debug symbols. On errors it
          # dumps raw C++ stack frames ("#N 0x<addr> <unknown>") into the WebDriver
          # response, which Selenium surfaces as the exception message — polluting
          # both the live log and the pretty-print summary with unreadable hex noise.
          # No Python-side fix exists. Strip the frames with sed before they land.
          # pipefail preserves Python's exit code through the pipe.
          set -o pipefail
          .venv/bin/python -u src/main.py \
            --driver-path ./${{ matrix.driver }} \
            --browser ${{ matrix.browser }} \
            --workers 3 \
            --wait-timeout ${{ env.WAIT_TIMEOUT }} \
            --logger terminal+file \
            2>&1 | sed -u \
              -e '/Stacktrace:/{N;/\n#[0-9][0-9]* 0x[0-9a-f][0-9a-f]* <unknown>/{s/Stacktrace:\n[^\n]*/HIDDEN/;b};P;D}' \
              -e '/^#[0-9][0-9]* 0x[0-9a-f][0-9a-f]* <unknown>/d'

      - name: Enumerate traces
        if: always()
        run: |
          sync
          find $GITHUB_WORKSPACE/.screenshots -type f 2>/dev/null || true
          find $GITHUB_WORKSPACE/.ocarina_logs -type f 2>/dev/null || true
          find $GITHUB_WORKSPACE/.reports -type f 2>/dev/null || true

      - name: Upload screenshots
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: screenshots-${{ matrix.browser }}
          path: .screenshots/
          retention-days: 7

      # … upload logs, reports similar ...
```

## Analyse

### `fail-fast: false`

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - browser: firefox
      - browser: chrome
```

`fail-fast: false` = si Firefox fail, Chrome continue. **Indispensable** pour ce projet&nbsp;: la valeur du run est de voir les **deux** browsers, même si l'un fail.

### `WAIT_TIMEOUT: 15`

```yaml
env:
  WAIT_TIMEOUT: 15
```

15 secondes (au lieu du default qui est à 10) pour absorber la latence Heroku dyno.  
`--wait-timeout ${{ env.WAIT_TIMEOUT }}` propage à `main.py`.

Rappel&nbsp;: `_NOT_CONFIRMED_TIMEOUT = 10` (dans `confirmation.py`) **n'est pas affecté** par `WAIT_TIMEOUT`.

### `FORCE_..._TO_NODE24: true`

Force les GitHub Actions à utiliser Node 24 plutôt que Node 16/18. Workaround qui relève du détail ici.

### warm-up Heroku

```bash
curl -sf --retry 6 --retry-delay 5 --retry-all-errors \
  --max-time 30 https://katalon-demo-cura.herokuapp.com/ > /dev/null
```

| Flag                 | Sens                                              |
| -------------------- | ------------------------------------------------- |
| `-s`                 | silent                                            |
| `-f`                 | fail on HTTP error                                |
| `--retry 6`          | retry 6 fois sur erreur                           |
| `--retry-delay 5`    | 5 secondes entre retries                          |
| `--retry-all-errors` | retry sur _toutes_ les erreurs (pas juste réseau) |
| `--max-time 30`      | timeout 30s par tentative                         |
| `> /dev/null`        | jette la réponse                                  |

→ Au pire&nbsp;: `6 * (5 + 30) = 210 secondes` = ~3.5 min. Suffit largement pour réveiller un dyno.

### `sed` des stacktraces ChromeDriver

```bash
.venv/bin/python -u src/main.py ... 2>&1 | sed -u \
  -e '/Stacktrace:/{N;/\n#[0-9][0-9]* 0x[0-9a-f][0-9a-f]* <unknown>/{s/Stacktrace:\n[^\n]*/HIDDEN/;b};P;D}' \
  -e '/^#[0-9][0-9]* 0x[0-9a-f][0-9a-f]* <unknown>/d'
```

```
# ChromeDriver release builds ship without debug symbols. On errors it
# dumps raw C++ stack frames ("#N 0x<addr> <unknown>") into the WebDriver
# response, which Selenium surfaces as the exception message — polluting
# both the live log and the pretty-print summary with unreadable hex noise.
# No Python-side fix exists. Strip the frames with sed before they land.
# pipefail preserves Python's exit code through the pipe.
```

- ChromeDriver est shippé sans debug symbols.
- En cas d'erreur, ChromeDriver vomit des stack frames C++ illisibles (`#0 0x7f3b... <unknown>`) dans la réponse WebDriver.
- Selenium les prend en compte comme des messages d'exception, peu importe la forme que ça a.
- Ces horreurs sont alors logguées et polluent les logs et même le pretty-print (lorsqu'il affiche un test en échec).
- Rien à faire côté Python&nbsp;: c'est ChromeDriver lui-même.
- Résolution côté _sys_ directement&nbsp;: `sed` filtre ces lignes _avant_ qu'elles n'atteignent l'utilisateur.

`sed -u`&nbsp;:

- `-u`&nbsp;: unbuffered (sortie en temps réel, ne bloque pas les pipes).
- Premier `-e`&nbsp;: si on voit `Stacktrace:` suivi d'une ligne C++ frame, remplace `Stacktrace:\n[contenu]` par `HIDDEN`.
- Second `-e`&nbsp;: delete les lignes C++ frame qui restent.

`set -o pipefail` _avant_&nbsp;: préserve le exit code de Python à travers le pipe. Sans pipefail, `python ... | sed ...` retournerait le exit code de `sed` (toujours 0), masquant un fail Python.

### Upload des artefacts

```yaml
- name: Upload screenshots
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: screenshots-${{ matrix.browser }}
    path: .screenshots/
    retention-days: 7
```

`if: always()`&nbsp;: upload même si le run a fail. `name: screenshots-${{ matrix.browser }}`&nbsp;: un artefact par browser (pas de collision Firefox+Chrome).

Trois artefacts par browser&nbsp;: `screenshots`, `ocarina_logs`, `reports`. Conservés 7 jours.

## Output

| Test                              | Firefox          | Chrome           |
| --------------------------------- | ---------------- | ---------------- |
| `valid_login` (smoke gate)        | ✅               | ✅               |
| `Most happy paths`                | ✅               | ✅               |
| `Gap tests` (G-DATA-\*, G-SPEC-1) | ❌ (intentional) | ❌ (intentional) |
| `post_logout_bfcache_exposure`    | ✅               | ❌ (B-BROWSER-1) |
| `post_logout_frenetic_navigation` | ✅               | ❌ (B-BROWSER-1) |
| `post_logout_server_invalidation` | ✅               | ✅               |

## «&nbsp;_Reading the results_&nbsp;»

Le README détaille 3 catégories de résultats&nbsp;:

> - **Most tests pass on both browsers.** That is the baseline.
> - **Intentional gap fails&nbsp;—&nbsp;red on both browsers, by design.** Five tests assert a constraint a healthcare system should enforce but CURA does not (past-date booking, server-side date bypass, duplicate booking, geographic conflict, history ordering). They stay red until CURA is fixed; each is paired with a `CURA_FRD.md` §9 entry and an `IDENTIFIED_GAPS.md` row.
> - **Expected cross-browser reds&nbsp;—&nbsp;red on Chrome, green on Firefox.** Two post-logout back-button tests: Chrome's back-forward cache restores the `no-store` history page after logout. A documented browser-behaviour finding, not a regression.
>
> Anything red _outside_ those categories is a real regression or a transient network error.
