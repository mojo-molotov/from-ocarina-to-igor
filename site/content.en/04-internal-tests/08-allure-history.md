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
      # … pushes the new history to the allure-history branch …
```

1. **Setup Bun** (Bun installs `allure-commandline` faster than npm).
2. **Install Allure CLI** (`bun add -g allure-commandline@2.41.0`).
3. **Restore history**: clones the `allure-history` branch, copies the `history/` tree into `allure-results/history/`. If the branch doesn't exist (first run), `|| echo "⚠️ First run"` stays silent.
4. **Generate report**: `allure generate --clean`.
5. **Save history**: pushes the new `history/` onto the `allure-history` branch.

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

Allure uses `categories.json` to bucket failures into matching categories in the HTML report.

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

See also [`02-ocarina/01-identity.md`](../02-ocarina/01-identity.md) for the rest.
