---
title: "04.08 — Allure + action composite allure-history + déploiement GH Pages"
description: "Le rapport Allure d'Ocarina, généré à chaque CI, historisé sur une branche Git dédiée puis publié sur GitHub Pages."
weight: 8
date: 2026-05-20
series: ["tests-internes"]
series_order: 8
---

# 04.08&nbsp;—&nbsp;Allure + action composite `allure-history` + déploiement GH Pages

> Le rapport Allure est généré à chaque CI, _historisé_ sur une branche Git dédiée, puis _publié_ sur GitHub Pages. Live URL&nbsp;: <https://mojo-molotov.github.io/ocarina/allure-report/>.

## Pipeline

```
┌────────────────────────────────────────────────────────┐
│ main_ci.yml (push/PR main, ou dispatch)                │
└──────────────────┬─────────────────────────────────────┘
                   ▼
   ┌───────────────────────────────────┐
   │ job : test                        │
   │  - matrix (ubuntu / windows × py) │
   │  - make test (cram + pytest)      │
   │  - upload-artifact allure-results │
   └───────────────┬───────────────────┘
                   ▼
   ┌───────────────────────────────────┐
   │ job : allure-history              │
   │  - download all allure-results    │
   │  - action composite locale :      │
   │       allure-history/action.yml   │
   │  - upload-artifact allure-report  │
   └───────────────┬───────────────────┘
                   ▼
   ┌───────────────────────────────────┐
   │ job : deploy                      │
   │  - download allure-report         │
   │  - prepare pages-root/            │
   │  - actions/upload-pages-artifact  │
   │  - actions/deploy-pages           │
   └───────────────────────────────────┘
```

## `allure-history`

`.github/actions/allure-history/action.yml`&nbsp;: action composite **locale** au repo (`uses: ./.github/actions/allure-history`).

```yaml
name: "Allure History Manager"
description: "Generate and save Allure reports with history"

inputs:
  branch-name:
    description: "Branch name to store history"
    required: true
  results-dir:
    description: "Directory containing allure results"
    default: "allure-results"
  report-dir:
    description: "Directory to generate allure report"
    default: "allure-report"

runs:
  using: "composite"
  steps:
    - name: Setup Bun
      uses: oven-sh/setup-bun@0c5077e51419868618aeaa5fe8019c62421857d6

    - name: Install Allure
      shell: bash
      run: bun add -g allure-commandline@2.41.0

    - name: Restore Allure history
      shell: bash
      run: |
        echo "📥 Restoring history..."
        mkdir -p .allure-history-tmp
        git clone --depth=1 \
          --branch "${{ inputs.branch-name }}" \
          "https://x-access-token:${{ github.token }}@github.com/${{ github.repository }}.git" \
          .allure-history-tmp 2>/dev/null || echo "⚠️ First run (no history yet)"

        if [ -d ".allure-history-tmp/history" ]; then
          mkdir -p "${{ inputs.results-dir }}/history"
          cp -r .allure-history-tmp/history/* "${{ inputs.results-dir }}/history/" || true
        fi

    - name: Generate Allure report
      shell: bash
      run: |
        echo "📊 Generating report..."
        allure generate "${{ inputs.results-dir }}" \
          -o "${{ inputs.report-dir }}" \
          --clean

    - name: Save history
      shell: bash
      # … pousse la nouvelle history sur la branche allure-history …
```

1. **Setup Bun** (Bun installe `allure-commandline` plus vite que npm).
2. **Install Allure CLI** (`bun add -g allure-commandline@2.41.0`).
3. **Restore history**&nbsp;: clone la branche `allure-history`, copie l'arbre `history/` dans `allure-results/history/`. Si la branche n'existe pas (premier run), `|| echo "⚠️ First run"` reste silencieux.
4. **Generate report**&nbsp;: `allure generate --clean`.
5. **Save history**&nbsp;: push la nouvelle `history/` sur la branche `allure-history`.

## `allure-history-push`

```yaml
allure-history:
  ...
  concurrency:
    group: allure-history-push
    cancel-in-progress: false
```

Empêche **deux runs concurrents** de pousser sur `allure-history` en même temps.  
Le second attend. `cancel-in-progress: false`&nbsp;→&nbsp;on _ne_ cancel _pas_ un run en cours&nbsp;;&nbsp;on attend.

## Déploiement GH Pages

```yaml
deploy:
  name: Deploy Allure report to GitHub Pages
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
    - name: Download report
      uses: actions/download-artifact@v8
      with:
        name: allure-report
        path: allure-report/

    - name: Prepare Pages structure
      run: |
        mkdir -p pages-root
        mv allure-report pages-root/allure-report

    - name: Upload Pages artifact
      uses: actions/upload-pages-artifact@v4
      with:
        path: pages-root/

    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v5
```

- `always()`&nbsp;: même si `test` a fail, on déploie le rapport (qui montrera l'échec).
- `github.repository_visibility != 'private'`&nbsp;: seulement pour un repo public.
- `github.event_name != 'pull_request'`&nbsp;: pas pour les PR (les PR ne déploient pas).

## `categories.json`

```json
[
  {
    "name": "Test defects",
    "matchedStatuses": ["broken"],
    "messageRegex": ".*"
  },
  {
    "name": "Invariant violations",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*InvariantViolationError.*"
  },
  {
    "name": "Assertion errors",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*AssertionError.*"
  },
  { "name": "Skipped", "matchedStatuses": ["skipped"], "messageRegex": ".*" }
]
```

```makefile
.PHONY: test
test: cram-test
	-pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
	$(PY_CMD) -c "import shutil; shutil.copy('categories.json', '$(ALLURE_RESULTS)/categories.json')"
```

Allure utilise `categories.json` pour ranger les failures dans une catégorie correspondante du rapport HTML.

## Statuts

| Statut    | Sens                                                                                                        |
| --------- | ----------------------------------------------------------------------------------------------------------- |
| `passed`  | Le test est passé.                                                                                          |
| `failed`  | Le test a fail (assertion /&nbsp;invariant). Catégorie&nbsp;: "Invariant violations" ou "Assertion errors". |
| `broken`  | Le test a fail. Catégorie&nbsp;: "Test defects".                                                            |
| `skipped` | Le test n'a pas tourné. Catégorie&nbsp;: "Skipped".                                                         |

## Navigation

```
https://mojo-molotov.github.io/ocarina/allure-report/

  ├─ Overview          (graphes globaux, trends history)
  ├─ Categories        (Test defects, Invariant violations, Assertion errors, Skipped)
  ├─ Suites            (par epic → feature → test)
  ├─ Behaviors         (par tag)
  ├─ Packages          (par module Python — utile pour le mainteneur)
  └─ Timeline          (par worker thread, dans l'ordre temporel)
```

La **trend** sur la timeline est rendue possible par l'historisation.  
On voit l'évolution des passing/failing/skipped sur les N derniers runs.
