---
title: "10.02 — Workflows ocarina (framework)"
description: "Les trois workflows du framework ocarina : main_ci pour la production, dev_ci pour les branches de travail et un build mensuel sur Python 3.15-dev."
weight: 2
date: 2026-05-20
series: ["ci-cd"]
series_order: 2
---

# 10.02&nbsp;—&nbsp;Workflows `ocarina` (framework)

> Trois workflows&nbsp;: `main_ci.yml` (production), `dev_ci.yml` (branches dev/feature/fix), `unstable_python_full_build.yml` (cron mensuel sur Python 3.15-dev).

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

`workflow_dispatch` avec un choix de version Python. Permet à l'utilisateur de _déclencher_ un build avec 3.15-dev (_pre-built wheels only_) sans attendre le cron mensuel.

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

→ Définit les versions Python dans un job _setup_ qui produit des _outputs_ consommés par les jobs suivants. Centralise la config.

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

- Si l'input `python_versions` contient «&nbsp;_unstable_&nbsp;»&nbsp;: matrice = `[3.14, 3.15-dev]`.
- Sinon&nbsp;: matrice = `[3.14]`.
- Cross OS&nbsp;: ubuntu + windows.

→ 2 ou 4 jobs selon l'input.

### Cache venv

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

Cache aggressivement directement le venv pour la version _stable_. La 3.15-dev change vite, le cache en prenant directement le venv serait souvent _stale_.

### Install avec wheels-only sur unstable

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

Sur 3.15-dev&nbsp;: `PIP_ONLY_BINARY=":all:"` force pip à n'utiliser **que les wheels pré-compilés**. Pas là pour faire tourner des compilations Rust en CI.

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

`PYTHONUTF8=1` force l'encodage UTF-8 (utile sur Windows). `make test` = cram + pytest avec Allure output.

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

Name par OS × Python. `retention-days: 1` (court).

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

1. **`if: always() && github.event_name != 'pull_request'`**&nbsp;: tourne même si tests fail, mais _pas_ sur les PR (pour ne pas polluer l'historique avec des PRs non mergées et par vigilance face à la grande mode des _Supply Chain Attacks_).
2. **`merge-multiple: true`**&nbsp;: fusionne tous les `allure-results-*` artifacts en un seul `allure-results/`.
3. **Action composite locale** `./.github/actions/allure-history` (cf. [`../04-internal-tests/08-allure-history.md`](../04-internal-tests/08-allure-history.md)).

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

Le rapport Allure est servi sur https://mojo-molotov.github.io/ocarina/allure-report/

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

      - name: Coverage summary
        if: always()
        uses: irongut/CodeCoverageSummary@51cc3a756ddcd398d447c044c02cb6aa83fdae95
        with:
          filename: coverage.xml
          format: markdown
          output: both
          hide_complexity: true

      - name: Add coverage to job summary
        if: always()
        run: cat code-coverage-results.md >> $GITHUB_STEP_SUMMARY
```

Pas de matrice OS. Pas d'Allure history. Pas de deploy. Juste check-style + test rapide&nbsp;—&nbsp;plus un récapitulatif de couverture.

Triggers&nbsp;: `dev`, branches `feature/**`, `fix/**`. Permet aux contributeurs de checker leurs branches sans toucher à main.

**Récapitulatif de couverture.** Une dernière étape lit le `coverage.xml` déjà produit par pytest-cov et l'affiche dans le récapitulatif du run sur GitHub (via `irongut/CodeCoverageSummary`, épinglée sur un SHA de commit). Les deux étapes sont en `if: always()`, si bien que le récapitulatif apparaît même quand les tests échouent. Aucun seuil n'est configuré&nbsp;: c'est purement informatif et ne conditionne jamais le build. La colonne de complexité est masquée (`hide_complexity: true`), car coverage.py / pytest-cov ne calculent pas la complexité cyclomatique&nbsp;: la valeur Cobertura vaut toujours 0 et la colonne ne ferait qu'induire en erreur.

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

| Mécanique                             | Détail                                                         |
| ------------------------------------- | -------------------------------------------------------------- |
| `cron: "0 3 1 * *"`                   | 03:00 UTC, le 1er de chaque mois                               |
| `if: github.ref == 'refs/heads/main'` | Tourne _seulement_ sur main, pas sur fork ou autre branche     |
| `python-version: 3.15-dev`            | Forcer 3.15 pré-release                                        |
| `allow-prereleases: true`             | setup-python accepte les pré-releases                          |
| `cache: pip`                          | Cache pip seulement (pas .venv, trop agressif sur pré-release) |

| Weekly                                 | Monthly                            |
| -------------------------------------- | ---------------------------------- |
| Plus rapide à détecter des régressions | Suffit (3.15-dev avance lentement) |
| Plus de quota CI utilisé               | Économe                            |

L'auteur a choisi une fréquence mensuelle.

## stable + unstable

`unstable_python_full_build.yml` _ne fait pas_ parti de `main_ci`.

3.15-dev change vite, peut casser pour des raisons hors-Ocarina.  
On veut être averti (cron mensuel) mais pas bloqué.
