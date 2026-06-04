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
      run: bun add -g allure@3.9.0

    - name: Restore Allure history
      shell: bash
      run: |
        echo "📥 Restoring history..."
        rm -rf .allure-history-tmp
        git clone --depth=1 \
          --branch "${{ inputs.branch-name }}" \
          "https://x-access-token:${{ github.token }}@github.com/${{ github.repository }}.git" \
          .allure-history-tmp 2>/dev/null || echo "⚠️ First run (no history yet)"

        # Allure 3 keeps history in a single JSONL file (see allurerc.mjs
        # historyPath) instead of Allure 2's history/ folder. Restore it to the
        # repo root so `allure generate` reads and appends to it.
        if [ -f ".allure-history-tmp/history.jsonl" ]; then
          cp .allure-history-tmp/history.jsonl ./history.jsonl
        fi

    - name: Generate Allure report
      shell: bash
      run: |
        echo "📊 Generating report..."
        # Output dir, historyPath and categories come from allurerc.mjs.
        allure generate "${{ inputs.results-dir }}" \
          --output "${{ inputs.report-dir }}"

    - name: Save history
      shell: bash
      # … pousse le nouveau history.jsonl sur la branche allure-history …
```

1. **Setup Bun** (Bun installe `allure` plus vite que npm).
2. **Install Allure CLI** (`bun add -g allure@3.9.0`&nbsp;—&nbsp;le rapport «&nbsp;Awesome&nbsp;» d'Allure 3).
3. **Restore history**&nbsp;: clone la branche `allure-history` et recopie son `history.jsonl` à la racine du repo. Si la branche n'existe pas (premier run), `|| echo "⚠️ First run"` reste silencieux.
4. **Generate report**&nbsp;: `allure generate` (le dossier de sortie, le `historyPath` et les catégories proviennent tous d'`allurerc.mjs`&nbsp;—&nbsp;plus d'options `-o`/`--clean`&nbsp;; `--clean` a disparu avec Allure 3).
5. **Save history**&nbsp;: pousse le nouveau `history.jsonl` sur la branche `allure-history`.

> **Allure 2 → 3.** Jusqu'ici la pipeline épinglait `allure-commandline@2.41.0` et le rapport GitHub Pages restait figé sur l'ancienne interface d'Allure 2. Le mécanisme d'historisation a profondément changé d'une version majeure à l'autre&nbsp;: Allure 3 lit et complète un unique fichier `history.jsonl` (défini par `historyPath` dans `allurerc.mjs`) au lieu du dossier `history/` recopié à la main par Allure 2. La trend d'Allure 2 est incompatible avec le format JSONL&nbsp;: les tendances repartent de zéro au premier build Allure 3, puis se reconstituent au fil des runs suivants.

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

## `allurerc.mjs`

Avec Allure 3, le fichier `categories.json` dédié disparaît. La configuration&nbsp;—&nbsp;dossier de sortie, chemin de l'historique et catégories de failures&nbsp;—&nbsp;tient désormais dans un seul fichier `allurerc.mjs` que la CLI Allure charge. Les catégories sont reprises telles quelles de l'ancien `categories.json`&nbsp;: les `matchedStatuses` / `messageRegex` d'Allure 2 deviennent `matchers.statuses` / `matchers.message` (qui accepte une `RegExp`).

```javascript
// allurerc.mjs — configuration d'Allure 3.
export default {
  name: "Ocarina",
  output: "allure-report",
  historyPath: "./history.jsonl",
  plugins: {
    awesome: {
      options: { reportName: "Ocarina" },
    },
  },
  categories: {
    rules: [
      { name: "Test defects", matchers: { statuses: ["broken"] } },
      {
        name: "Invariant violations",
        matchers: { statuses: ["failed"], message: /.*InvariantViolationError.*/ },
      },
      {
        name: "Assertion errors",
        matchers: { statuses: ["failed"], message: /.*AssertionError.*/ },
      },
      { name: "Skipped", matchers: { statuses: ["skipped"] } },
    ],
  },
};
```

Le choix d'exporter un objet brut plutôt que `defineConfig` du paquet `allure` est délibéré&nbsp;: avec une installation globale (`bun add -g allure`), rien ne garantit que cet import se résolve depuis le fichier de config&nbsp;; s'en passer permet à la config de fonctionner aussi bien en CI qu'en local.

```makefile
.PHONY: test
test: cram-test
	-pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
```

La cible `make test` ne copie plus `categories.json` dans les résultats&nbsp;: les catégories sont embarquées dans `allurerc.mjs`. Allure s'en sert pour ranger les failures dans la catégorie correspondante du rapport HTML.

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
