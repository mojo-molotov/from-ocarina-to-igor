---
title: "04.08 — Allure + composite action allure-history + GH Pages deploy"
description: "Ocarina's Allure report, generated on every CI run, versioned on a dedicated Git branch and published to GitHub Pages."
weight: 8
date: 2026-05-20
series: ["internal-tests"]
series_order: 8
---

# 04.08&nbsp;—&nbsp;Allure + composite action `allure-history` + GH Pages deploy

> The Allure report gets generated on every CI, _archived_ on a dedicated Git branch, then _published_ on GitHub Pages. Live URL: <https://mojo-molotov.github.io/ocarina/allure-report/>.

## Pipeline

```
┌────────────────────────────────────────────────────────┐
│ main_ci.yml (push/PR main, or dispatch)                │
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
   │  - local composite action:        │
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

`.github/actions/allure-history/action.yml`: composite action **local** to the repo (`uses: ./.github/actions/allure-history`).

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
      # … pushes the new history.jsonl to the allure-history branch …
```

1. **Setup Bun** (Bun installs `allure` faster than npm).
2. **Install Allure CLI** (`bun add -g allure@3.9.0` — the Allure 3 "Awesome" report).
3. **Restore history**: clones the `allure-history` branch and copies its `history.jsonl` back to the repo root. If the branch doesn't exist (first run), `|| echo "⚠️ First run"` stays silent.
4. **Generate report**: `allure generate` (output dir, `historyPath` and categories all come from `allurerc.mjs` — no more `-o`/`--clean` flags; `--clean` was removed in Allure 3).
5. **Save history**: pushes the new `history.jsonl` onto the `allure-history` branch.

> **Allure 2 → 3.** Before this, the pipeline pinned `allure-commandline@2.41.0` and the GitHub Pages report was stuck on the legacy Allure 2 UI. The history mechanism changed substantially across the major version: Allure 3 reads and appends to a single `history.jsonl` file (configured by `historyPath` in `allurerc.mjs`) instead of Allure 2's manually-copied `history/` folder. Allure 2 trend history is incompatible with the JSONL format, so trends restart on the first Allure 3 build and rebuild over subsequent runs.

## `allure-history-push`

```yaml
allure-history:
  ...
  concurrency:
    group: allure-history-push
    cancel-in-progress: false
```

Prevents **two concurrent runs** from pushing to `allure-history` simultaneously.  
The second waits. `cancel-in-progress: false` → we _don't_ cancel a running job, we wait.

## GH Pages deploy

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

- `always()`: even if `test` failed, deploy the report (which will show the failure).
- `github.repository_visibility != 'private'`: public repo only.
- `github.event_name != 'pull_request'`: not for PRs (PRs don't deploy).

## `allurerc.mjs`

With Allure 3, the standalone `categories.json` is gone. Configuration — output dir, history path and the failure categories — lives in a single `allurerc.mjs` config file the Allure CLI loads. The categories were ported straight from the former `categories.json`: Allure 2's `matchedStatuses` / `messageRegex` map to `matchers.statuses` / `matchers.message` (which accepts a `RegExp`).

```javascript
// allurerc.mjs — Allure 3 configuration.
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

A plain object is exported on purpose, rather than `defineConfig` from the `allure` package: with a global install (`bun add -g allure`) that import isn't guaranteed to resolve from the config file, so avoiding it keeps the config working in CI and locally alike.

```makefile
.PHONY: test
test: cram-test
	-pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
```

The `make test` target no longer copies `categories.json` into the results — the categories ship in `allurerc.mjs`. Allure uses them to bucket failures into matching categories in the HTML report.

## Statuses

| Status    | Meaning                                                                                          |
| --------- | ------------------------------------------------------------------------------------------------ |
| `passed`  | The test passed.                                                                                 |
| `failed`  | The test failed (assertion / invariant). Category: "Invariant violations" or "Assertion errors". |
| `broken`  | The test failed. Category: "Test defects".                                                       |
| `skipped` | The test didn't run. Category: "Skipped".                                                        |

## Navigation

```
https://mojo-molotov.github.io/ocarina/allure-report/

  ├─ Overview          (global graphs, trends history)
  ├─ Categories        (Test defects, Invariant violations, Assertion errors, Skipped)
  ├─ Suites            (by epic → feature → test)
  ├─ Behaviors         (by tag)
  ├─ Packages          (by Python module — useful for the maintainer)
  └─ Timeline          (by worker thread, in temporal order)
```

The **trend** on the timeline is what the archiving makes possible.  
You can see passing/failing/skipped evolve across the last N runs.
