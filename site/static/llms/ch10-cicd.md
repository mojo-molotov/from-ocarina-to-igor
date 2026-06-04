# Ch 10 — CI/CD

Chapter brief for LLM navigation. Source articles: `site/content.en/10-cicd/`.

## Articles

| File | Description |
| --- | --- |
| `_index.md` | Chapter landing page. Overview count table (workflows per repo). "Cross-cutting discipline": the conventions shared across every workflow (`workflow_dispatch` always present, venv/node_modules cache, matrix strategy, `fail-fast: false`, artifact upload, `if: always()`, `environment:` for secrets, `concurrency: pages`, `defaults.run.shell: bash`). "Light on PR, heavy on manual". |
| `01-matrix.md` | Summary matrix of every CI workflow across all six repos: repo, workflow file, trigger, OS/runtime, what it does. |
| `02-ocarina-workflows.md` | `ocarina` repo: `main_ci.yml` (full build + tests ubuntu × windows × py 3.14), `dev_ci.yml` (check-coding-style + tests + a non-gating coverage summary in the GitHub step summary via `irongut/CodeCoverageSummary`), `unstable_python_full_build.yml` (monthly cron on Python pre-release, 1st of month). |
| `03-example-workflows.md` | `ocarina-example` repo: `main_ci.yml` (lint + typecheck), `dev_ci.yml`, `e2e.yml` (ubuntu + Redis service + Firefox + geckodriver 0.35.0). |
| `04-ai-workflows.md` | `ocarina-with-ai-example` repo: `ai_proof_ci.yml` (lint + typecheck), `ai_proof_e2e.yml` (ubuntu × Firefox/Chrome matrix, geckodriver 0.36.0 + auto-matched chromedriver). |
| `05-igoristan-workflows.md` | `igoristan` repo: `ci-pr.yml` (ubuntu × node 24 + pnpm 11, 3 parallel jobs), `deploy.yml` (push main → GitHub Pages). |
| `06-holy-book-workflow.md` | `ocarina-holy-book` repo: `deploy.yml` (VitePress build + Pagefind index + GitHub Pages deploy). |
| `07-tests-workers-vercel.md` | `tests-workers` repo: no GitHub Actions. Vercel auto-deploys on push to main. **Contains ASCII diagram.** |

## Key concepts

- **No workflow in tests-workers**: deployment is Vercel-managed, not GitHub Actions. Article 07 documents the Vercel auto-deploy flow with a diagram.
- **Cross-platform matrix**: `ocarina`'s `main_ci.yml` and `unstable_python_full_build.yml` both run ubuntu + windows × Python 3.14. `ocarina-example`'s `main_ci.yml` also runs a windows runner; the other repos are ubuntu-only.
- **`unstable_python_full_build.yml`**: monthly canary run (cron `0 3 1 * *`, 1st of month at 03:00 UTC) on Python 3.15-dev to catch breakage before a new Python version ships.
- **geckodriver version pinning**: `ocarina-example`'s `e2e.yml` manually downloads geckodriver 0.35.0. `ocarina-with-ai-example`'s `ai_proof_e2e.yml` pins geckodriver 0.36.0 and uses an auto-matched chromedriver for its Firefox/Chrome matrix. `ocarina`'s own framework CI runs no browser (cram + pytest; the Playwright smoke auto-skips without Chromium).
- **Redis service container**: `e2e.yml` in `ocarina-example` spins up a Redis service container for the distributed lock tests. The container is available at `redis://localhost:6379` during the run.
- **Heroku warm-up**: `ai_proof_e2e.yml` pings CURA Healthcare before running tests (Heroku eco-dyno cold starts).
- **Allure history**: after each `ocarina` CI run, a composite action (`allure-history`) appends the new report to GitHub Pages, maintaining a browsable history. Report generation uses Allure 3 (the "Awesome" report, `allure@3.9.0`), configured by `allurerc.mjs` (output dir, `historyPath`, categories); history lives in a single `history.jsonl` file on the `allure-history` branch rather than Allure 2's `history/` folder.
- **Cross-cutting discipline** (conventions shared by every workflow): `workflow_dispatch` always present (manual launch), venv/`node_modules` caching, matrix strategy with `fail-fast: false`, artifact upload of everything generated with `if: always()`, `environment:` for secrets (`OC`, `github-pages`), `concurrency: pages` against deploy races, `defaults.run.shell: bash` for cross-OS parity.
- **Light on PR, heavy on manual**: push/PR runs fast lint + typecheck + unit tests; full (heavy) e2e runs on manual `workflow_dispatch`; a monthly cron runs `unstable_python_full_build.yml` on Python 3.15-dev.

## Diagrams

- `07-tests-workers-vercel.md` — Vercel auto-deploy flow.

## Connections

- Framework CI → `02-ocarina-workflows.md` (links to Ch 02, Ch 04)
- Example suite CI → `03-example-workflows.md` (links to Ch 07)
- AI example CI → `04-ai-workflows.md` (links to Ch 08)
- Igoristan CI → `05-igoristan-workflows.md` (links to Ch 05)
- Holy Book CI → `06-holy-book-workflow.md` (links to Ch 09)
- Vercel deploy → `07-tests-workers-vercel.md` (links to Ch 06)

## Not covered here

Secrets layout and values for each repo. Current CI green/red state. GitHub Actions runner pricing or quota details.

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
