---
title: "10.04 — Workflows ocarina-with-ai-example"
description: "Les workflows de ocarina-with-ai-example : ai_proof_ci pour la PR rapide et ai_proof_e2e manuel avec matrice Firefox et Chrome."
weight: 4
date: 2026-05-20
series: ["ci-cd"]
series_order: 4
tags: ["selenium"]
---

# 10.04&nbsp;—&nbsp;Workflows `ocarina-with-ai-example`

> Voir aussi [`../08-ai-example/09-ci-matrix.md`](../08-ai-example/09-ci-matrix.md)

## Vue d'ensemble

| Workflow           | Trigger                 | OS                                            | Effet                                                                             | Note              |
| ------------------ | ----------------------- | --------------------------------------------- | --------------------------------------------------------------------------------- | ----------------- |
| `ai_proof_ci.yml`  | push main, PR, dispatch | ubuntu&nbsp;×&nbsp;py&nbsp;3.14               | `ruff format src/ --check` +&nbsp;`ruff check src/` +&nbsp;`mypy src/`            | Gate PR, rapide   |
| `ai_proof_e2e.yml` | dispatch                | ubuntu&nbsp;×&nbsp;**matrice firefox+chrome** | warm-up Heroku +&nbsp;run +&nbsp;sed filter ChromeDriver C++ stacks +&nbsp;upload | Manuel uniquement |

## Différences avec `ocarina-example`

| Aspect              | `ocarina-example`        | `ocarina-with-ai-example`                    |
| ------------------- | ------------------------ | -------------------------------------------- |
| **Matrice browser** | Firefox seul (e2e.yml)   | Firefox **+** Chrome (parallélisés)          |
| **SUT**             | Igoristan (GitHub Pages) | CURA (Heroku eco-dyno)                       |
| **Pre-run**         | warm-up Redis client     | warm-up Heroku dyno                          |
| **Filtre output**   | _aucun_                  | sed filtre les stack frames C++ ChromeDriver |
| **`WAIT_TIMEOUT`**  | default 10               | 15 (compense les latences Heroku)            |

## warm-up Heroku

```bash
curl -sf --retry 6 --retry-delay 5 --retry-all-errors \
  --max-time 30 https://katalon-demo-cura.herokuapp.com/ > /dev/null
echo "Dyno is warm"
```

> CURA runs on a Heroku dyno that sleeps after inactivity.
> Tests hitting a cold dyno produce timeouts (false fails) and slow
> confirmations (false passes on gap tests). Wake it explicitly
> before any browser opens.

## Le filtre `sed` des stacktraces C++ ChromeDriver

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

- ChromeDriver, en cas d'erreur, dump des stack frames C++ illisibles (`#0 0x7f3b... <unknown>`).
- Selenium les remonte _dans le message d'exception_.
- Pollue les logs et la sortie `pretty_print_results`
- Pas de correctif pertinent à faire directement dans le code Python.
- `sed` les vire _avant_ que ça n'atteigne l'utilisateur, directement depuis le shell.

`set -o pipefail` préserve l'exit code de Python.

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

Si Firefox fail, Chrome continue.  
La valeur est dans la **comparaison** des deux runs.

## `WAIT_TIMEOUT: 15`

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
  WAIT_TIMEOUT: 15
```

15 secondes au lieu du default 10. Compense les latences Heroku dyno qui peuvent être supérieures à la moyenne même après _cold-start_ (même avec warm-up curl, les requêtes suivantes peuvent être lentes).

Rappel&nbsp;: `_NOT_CONFIRMED_TIMEOUT = 10` (dans `confirmation.py`) **n'est pas affecté** (cf. [`../08-ai-example/06-data-gaps.md`](../08-ai-example/06-data-gaps.md)).

## Navigateurs web en CI

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

`ubuntu-latest` ships `google-chrome-stable`. On extrait sa version exacte, on télécharge le chromedriver matché depuis le CDN officiel Google `chrome-for-testing-public`.

→ Garantit la compatibilité Chrome&nbsp;↔&nbsp;ChromeDriver.

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

Step qui _force une synchronisation du système de fichiers_ et _liste_ les traces produites avant l'upload. Permet de voir directement dans les logs GitHub quels fichiers ont été générés.

## Upload artifacts par navigateur

```yaml
- name: Upload screenshots
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: screenshots-${{ matrix.browser }}
    path: .screenshots/
    retention-days: 7
```

Noms **incluant le navigateur** (`screenshots-firefox`, `screenshots-chrome`). Pas de collision entre les deux runs parallèles.

Conservé 7 jours.
