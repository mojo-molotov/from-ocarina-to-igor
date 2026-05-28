---
title: "08.09 — CI: ai_proof_ci.yml + ai_proof_e2e.yml"
description: "The CI of ocarina-with-ai-example: a fast lint and typecheck PR, and a manual e2e with a Firefox and Chrome matrix, Heroku warm-up and stacktrace filtering."
weight: 9
date: 2026-05-20
series: ["ai-example"]
series_order: 9
tags: ["selenium"]
---

# 08.09&nbsp;—&nbsp;CI: `ai_proof_ci.yml` + `ai_proof_e2e.yml`

> Two workflows. Fast PR (lint+typecheck). Manual e2e with a **Firefox/Chrome matrix** + Heroku warm-up + ChromeDriver stacktrace filtering.

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

      # … upload logs, reports similarly ...
```

## Analysis

### `fail-fast: false`

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - browser: firefox
      - browser: chrome
```

`fail-fast: false`&nbsp;—&nbsp;if Firefox fails, Chrome continues. Essential: the point of the run is seeing **both** browsers, even when one fails.

### `WAIT_TIMEOUT: 15`

```yaml
env:
  WAIT_TIMEOUT: 15
```

15 seconds instead of the default 10, to absorb Heroku dyno latency.
`--wait-timeout ${{ env.WAIT_TIMEOUT }}` propagates to `main.py`.

`_NOT_CONFIRMED_TIMEOUT = 10` (in `confirmation.py`) is **not affected** by `WAIT_TIMEOUT`.

### `FORCE_..._TO_NODE24: true`

Forces GitHub Actions to use Node 24 instead of Node 16/18. A workaround&nbsp;—&nbsp;mostly an aside.

### Heroku warm-up

```bash
curl -sf --retry 6 --retry-delay 5 --retry-all-errors \
  --max-time 30 https://katalon-demo-cura.herokuapp.com/ > /dev/null
```

| Flag                 | Meaning                                  |
| -------------------- | ---------------------------------------- |
| `-s`                 | silent                                   |
| `-f`                 | fail on HTTP error                       |
| `--retry 6`          | retry 6 times on error                   |
| `--retry-delay 5`    | 5 seconds between retries                |
| `--retry-all-errors` | retry on _all_ errors (not just network) |
| `--max-time 30`      | 30s timeout per attempt                  |
| `> /dev/null`        | discard the response                     |

Worst case: `6 * (5 + 30) = 210 seconds` = ~3.5 min. Plenty to wake a dyno.

### `sed` of ChromeDriver stacktraces

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

ChromeDriver ships without debug symbols. On error it dumps raw C++ stack frames (`#0 0x7f3b... <unknown>`) into the WebDriver response, which Selenium surfaces as the exception message. Those frames pollute the live log and the pretty-print output. There's no Python-side fix&nbsp;—&nbsp;it's ChromeDriver's output. `sed` strips the frames before they reach the user.

`sed -u`:

- `-u`: unbuffered&nbsp;—&nbsp;real-time output, no pipe blocking.
- First `-e`: if `Stacktrace:` is followed by a C++ frame line, replace `Stacktrace:\n[content]` with `HIDDEN`.
- Second `-e`: delete the remaining C++ frame lines.

`set -o pipefail` comes first: it preserves Python's exit code through the pipe. Without it, `python ... | sed ...` returns `sed`'s exit code (always 0), masking a Python failure.

### Artifact upload

```yaml
- name: Upload screenshots
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: screenshots-${{ matrix.browser }}
    path: .screenshots/
    retention-days: 7
```

`if: always()` uploads even when the run failed. `name: screenshots-${{ matrix.browser }}` gives each browser its own artifact&nbsp;—&nbsp;no Firefox/Chrome collision.

Three artifacts per browser: `screenshots`, `ocarina_logs`, `reports`. Retained 7 days.

## Output

| Test                              | Firefox          | Chrome           |
| --------------------------------- | ---------------- | ---------------- |
| `valid_login` (smoke gate)        | ✅               | ✅               |
| `Most happy paths`                | ✅               | ✅               |
| `Gap tests` (G-DATA-\*, G-SPEC-1) | ❌ (intentional) | ❌ (intentional) |
| `post_logout_bfcache_exposure`    | ✅               | ❌ (B-BROWSER-1) |
| `post_logout_frenetic_navigation` | ✅               | ❌ (B-BROWSER-1) |
| `post_logout_server_invalidation` | ✅               | ✅               |

## "_Reading the results_"

The README defines three result categories:

> - **Most tests pass on both browsers.** That is the baseline.
> - **Intentional gap fails&nbsp;—&nbsp;red on both browsers, by design.** Five tests assert a constraint a healthcare system should enforce but CURA does not (past-date booking, server-side date bypass, duplicate booking, geographic conflict, history ordering). They stay red until CURA is fixed; each is paired with a `CURA_FRD.md` §9 entry and an `IDENTIFIED_GAPS.md` row.
> - **Expected cross-browser reds&nbsp;—&nbsp;red on Chrome, green on Firefox.** Two post-logout back-button tests: Chrome's back-forward cache restores the `no-store` history page after logout. A documented browser-behaviour finding, not a regression.
>
> Anything red _outside_ those categories is a real regression or a transient network error.
