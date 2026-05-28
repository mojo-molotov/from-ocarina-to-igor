---
title: "10.02 — ocarina workflows (framework)"
description: "The ocarina framework's three workflows: main_ci for production, dev_ci for working branches and a monthly build on Python 3.15-dev."
weight: 2
date: 2026-05-20
series: ["ci-cd"]
series_order: 2
---

# 10.02&nbsp;—&nbsp;`ocarina` workflows (framework)

> Three workflows: `main_ci.yml` (production), `dev_ci.yml` (dev/feature/fix branches), `unstable_python_full_build.yml` (monthly cron on Python 3.15-dev).

## `main_ci.yml`

### Trigger

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      python_versions:
        description: "Python versions to test"
        type: choice
        required: false
        default: "Stable only"
        options:
          - "Stable only"
          - "Stable + unstable (uses pre-built wheels)"
```

`workflow_dispatch` with a Python-version choice. Lets the user _trigger_ a build with 3.15-dev (_pre-built wheels only_) without waiting for the monthly cron.

### Setup job

```yaml
setup:
  runs-on: ubuntu-latest
  outputs:
    python_stable: ${{ steps.versions.outputs.python_stable }}
    python_unstable: ${{ steps.versions.outputs.python_unstable }}
  steps:
    - id: versions
      run: |
        echo "python_stable=3.14" >> $GITHUB_OUTPUT
        echo "python_unstable=3.15-dev" >> $GITHUB_OUTPUT
```

A setup job produces outputs that later jobs consume. Centralizes the version config.

### Test job (matrix)

```yaml
test:
  needs: setup
  strategy:
    fail-fast: false
    matrix:
      os: [ubuntu-latest, windows-latest]
      python-version: ${{
        contains(github.event.inputs.python_versions, 'unstable')
          && fromJSON(format('["{0}", "{1}"]', needs.setup.outputs.python_stable, needs.setup.outputs.python_unstable))
          || fromJSON(format('["{0}"]', needs.setup.outputs.python_stable))
      }}
```

- If the `python_versions` input contains "_unstable_": matrix = `[3.14, 3.15-dev]`.
- Otherwise: matrix = `[3.14]`.
- Cross-OS: ubuntu + windows.

2 or 4 jobs depending on input.

### venv cache

```yaml
- name: Cache virtual environment
  if: matrix.python-version == needs.setup.outputs.python_stable
  id: cache-venv
  uses: actions/cache@v5
  with:
    path: .venv
    key: venv-${{ runner.os }}-py${{ steps.setup-python.outputs.python-version }}-${{ hashFiles('pyproject.toml', 'requirements.txt', 'requirements-dev.txt', 'requirements-dev.in') }}
    restore-keys: |
      venv-${{ runner.os }}-py${{ steps.setup-python.outputs.python-version }}-
```

Aggressively caches the venv directly for the _stable_ version. 3.15-dev moves fast; caching the venv would often be _stale_.

### Install with wheels-only on unstable

```yaml
- name: Install dependencies
  if: matrix.python-version == needs.setup.outputs.python_unstable || steps.cache-venv.outputs.cache-hit != 'true'
  run: |
    if [ "${{ matrix.python-version }}" = "${{ needs.setup.outputs.python_unstable }}" ]; then
      PIP_ONLY_BINARY=":all:" make install-on-ci
    else
      make install-on-ci
    fi
```

On 3.15-dev: `PIP_ONLY_BINARY=":all:"` forces pip to use **only pre-built wheels**&nbsp;—&nbsp;no Rust compilations in CI.

### Test

```yaml
- name: Check coding style
  run: |
    . $VENV_ACTIVATE
    make check-coding-style

- name: Run tests
  shell: bash
  env:
    PYTHONUTF8: "1"
  run: |
    . $VENV_ACTIVATE
    make test
```

`PYTHONUTF8=1` forces UTF-8 encoding (useful on Windows). `make test` = cram + pytest with Allure output.

### Upload Allure artifacts

```yaml
- name: Upload Allure results
  if: always()
  uses: actions/upload-artifact@v7
  with:
    name: allure-results-${{ matrix.os }}-${{ matrix.python-version }}
    path: allure-results/
    retention-days: 1
```

Name per OS × Python. `retention-days: 1` (short).

### Allure history job

```yaml
allure-history:
  needs: test
  if: always() && github.event_name != 'pull_request'
  runs-on: ubuntu-latest
  permissions:
    contents: write
  concurrency:
    group: allure-history-push
    cancel-in-progress: false
  steps:
    - uses: actions/checkout@v6
    - uses: actions/download-artifact@v8
      with:
        pattern: allure-results-*
        path: allure-results
        merge-multiple: true
    - uses: ./.github/actions/allure-history
      with:
        branch-name: allure-history
```

1. **`if: always() && github.event_name != 'pull_request'`**: runs even if tests fail, but _not_ on PRs (to avoid polluting history with unmerged PRs and out of vigilance against the Supply Chain Attack trend).
2. **`merge-multiple: true`**: merges all `allure-results-*` artifacts into a single `allure-results/`.
3. **Local composite action** `./.github/actions/allure-history` (see [`../04-internal-tests/08-allure-history.md`](../04-internal-tests/08-allure-history.md)).

### Deploy job

```yaml
deploy:
  needs: allure-history
  if: always() && github.repository_visibility != 'private' && github.event_name != 'pull_request'
  runs-on: ubuntu-latest
  permissions:
    pages: write
    id-token: write
  environment:
    name: github-pages
    url: ${{ steps.deployment.outputs.page_url }}
  steps:
    - uses: actions/download-artifact@v8
      with: { name: allure-report, path: allure-report/ }
    - name: Prepare Pages structure
      run: |
        mkdir -p pages-root
        mv allure-report pages-root/allure-report
    - uses: actions/upload-pages-artifact@v4
      with: { path: pages-root/ }
    - id: deployment
      uses: actions/deploy-pages@v5
```

The Allure report is served at https://mojo-molotov.github.io/ocarina/allure-report/

## `dev_ci.yml`

```yaml
on:
  push:
    branches: [dev, "feature/**", "fix/**"]
  pull_request:
    branches: [dev]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # ... setup ...
      - name: Check coding style
        run: make check-coding-style
      - name: Run tests
        run: make test
```

No OS matrix. No Allure history. No deploy. Just check-style + fast tests.

Triggers: `dev`, `feature/**`, `fix/**` branches. Lets contributors check their branches without touching main.

## `unstable_python_full_build.yml`

```yaml
name: Unstable Python Full Build

on:
  schedule:
    - cron: "0 3 1 * *"
  workflow_dispatch:

jobs:
  full-unstable-build:
    if: github.ref == 'refs/heads/main'
    name: Python 3.15-dev on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: 3.15-dev
          allow-prereleases: true
          cache: pip
      # ... install + check-coding-style + run tests ...
```

| Mechanic                              | Detail                                                    |
| ------------------------------------- | --------------------------------------------------------- |
| `cron: "0 3 1 * *"`                   | 03:00 UTC, 1st of each month                              |
| `if: github.ref == 'refs/heads/main'` | Runs _only_ on main, not on a fork or other branch        |
| `python-version: 3.15-dev`            | Force 3.15 pre-release                                    |
| `allow-prereleases: true`             | setup-python accepts pre-releases                         |
| `cache: pip`                          | Cache pip only (not .venv, too aggressive on pre-release) |

| Weekly                      | Monthly                        |
| --------------------------- | ------------------------------ |
| Faster regression detection | Enough (3.15-dev moves slowly) |
| More CI quota used          | Economical                     |

The author chose a monthly cadence.

## stable + unstable

`unstable_python_full_build.yml` _is not_ part of `main_ci`.

3.15-dev moves fast and may break for reasons unrelated to Ocarina. The monthly cron gives notification without blocking.
