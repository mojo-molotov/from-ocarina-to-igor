---
title: "10.04 — ocarina-with-ai-example workflows"
description: "The ocarina-with-ai-example workflows: ai_proof_ci for the fast PR gate and a manual ai_proof_e2e with a Firefox and Chrome matrix."
weight: 4
date: 2026-05-20
series: ["ci-cd"]
series_order: 4
tags: ["selenium"]
---

# 10.04&nbsp;—&nbsp;`ocarina-with-ai-example` workflows

> See also [`../08-ai-example/09-ci-matrix.md`](../08-ai-example/09-ci-matrix.md)

## Overview

| Workflow           | Trigger                 | OS                                           | Effect                                                             | Note          |
| ------------------ | ----------------------- | -------------------------------------------- | ------------------------------------------------------------------ | ------------- |
| `ai_proof_ci.yml`  | push main, PR, dispatch | ubuntu&nbsp;×&nbsp;py&nbsp;3.14              | `ruff format src/ --check` + `ruff check src/` + `mypy src/`       | PR gate, fast |
| `ai_proof_e2e.yml` | dispatch                | ubuntu&nbsp;×&nbsp;**firefox+chrome matrix** | Heroku warm-up + run + sed filter ChromeDriver C++ stacks + upload | Manual only   |

## Differences vs `ocarina-example`

| Aspect             | `ocarina-example`        | `ocarina-with-ai-example`                 |
| ------------------ | ------------------------ | ----------------------------------------- |
| **Browser matrix** | Firefox only (e2e.yml)   | Firefox **+** Chrome (parallelized)       |
| **SUT**            | Igoristan (GitHub Pages) | CURA (Heroku eco-dyno)                    |
| **Pre-run**        | warm-up Redis client     | warm-up Heroku dyno                       |
| **Output filter**  | _none_                   | sed filters ChromeDriver C++ stack frames |
| **`WAIT_TIMEOUT`** | default 10               | 15 (compensates for Heroku latency)       |

## Heroku warm-up

```bash
curl -sf --retry 6 --retry-delay 5 --retry-all-errors \
  --max-time 30 https://katalon-demo-cura.herokuapp.com/ > /dev/null
echo "Dyno is warm"
```

> CURA runs on a Heroku dyno that sleeps after inactivity.
> Tests hitting a cold dyno produce timeouts (false fails) and slow
> confirmations (false passes on gap tests). Wake it explicitly
> before any browser opens.

## The `sed` filter for ChromeDriver C++ stacktraces

```bash
.venv/bin/python -u src/main.py ... 2>&1 | sed -u \
  -e '/Stacktrace:/{N;/\n#[0-9][0-9]* 0x[0-9a-f][0-9a-f]* <unknown>/{s/Stacktrace:\n[^\n]*/HIDDEN/;b};P;D}' \
  -e '/^#[0-9][0-9]* 0x[0-9a-f][0-9a-f]* <unknown>/d'
```

> ChromeDriver release builds ship without debug symbols. On errors it
> dumps raw C++ stack frames ("#N 0x<addr> <unknown>") into the WebDriver
> response, which Selenium surfaces as the exception message&nbsp;—&nbsp;polluting
> both the live log and the pretty-print summary with unreadable hex noise.
> No Python-side fix exists. Strip the frames with sed before they land.
> pipefail preserves Python's exit code through the pipe.

- ChromeDriver, on error, dumps unreadable C++ stack frames (`#0 0x7f3b... <unknown>`).
- Selenium surfaces them _in the exception message_.
- Pollutes logs and the `pretty_print_results` output.
- No relevant fix directly in Python code.
- `sed` strips them _before_ they reach the user, straight from the shell.

`set -o pipefail` preserves Python's exit code.

## `fail-fast: false`

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - browser: firefox
        driver: geckodriver
      - browser: chrome
        driver: chromedriver
```

If Firefox fails, Chrome continues. The value is in comparing both runs.

## `WAIT_TIMEOUT: 15`

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
  WAIT_TIMEOUT: 15
```

15 seconds instead of default 10. Compensates for Heroku dyno latency that can exceed the average even after _cold-start_ (even with curl warm-up, subsequent requests may be slow).

Reminder: `_NOT_CONFIRMED_TIMEOUT = 10` (in `confirmation.py`) **is not affected** (see [`../08-ai-example/06-data-gaps.md`](../08-ai-example/06-data-gaps.md)).

## Browsers in CI

### Firefox

```yaml
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
```

### Chrome

```yaml
- name: Install chromedriver
  if: matrix.browser == 'chrome'
  run: |
    CHROME_VER=$(google-chrome-stable --version | grep -oP '\d+\.\d+\.\d+\.\d+')
    wget -q -O chromedriver.zip \
      "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VER}/linux64/chromedriver-linux64.zip"
    unzip -q chromedriver.zip
    mv chromedriver-linux64/chromedriver ./chromedriver
    chmod +x ./chromedriver
```

`ubuntu-latest` ships `google-chrome-stable`. We extract its exact version, download the matching chromedriver from Google's official `chrome-for-testing-public` CDN.

This guarantees Chrome ↔ ChromeDriver version compatibility.

## `Enumerate traces`

```yaml
- name: Enumerate traces
  if: always()
  run: |
    sync
    find $GITHUB_WORKSPACE/.screenshots -type f 2>/dev/null || true
    find $GITHUB_WORKSPACE/.ocarina_logs -type f 2>/dev/null || true
    find $GITHUB_WORKSPACE/.reports -type f 2>/dev/null || true
```

Step that _forces a filesystem sync_ and _lists_ produced traces before upload. Lets you see directly in GitHub logs which files were generated.

## Per-browser artifact upload

```yaml
- name: Upload screenshots
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: screenshots-${{ matrix.browser }}
    path: .screenshots/
    retention-days: 7
```

Names **including the browser** (`screenshots-firefox`, `screenshots-chrome`). No collision between the two parallel runs.

Retained 7 days.
