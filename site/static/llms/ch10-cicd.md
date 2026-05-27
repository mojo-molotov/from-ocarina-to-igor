# Ch 10 — CI/CD

Chapter brief for LLM navigation. Source articles: `site/content.en/10-cicd/`.

## Articles

| File | Description |
| --- | --- |
| `01-matrix.md` | Summary matrix of every CI workflow across all six repos: repo, workflow file, trigger, OS/runtime, what it does. |
| `02-ocarina-workflows.md` | `ocarina` repo: `main_ci.yml` (full build + tests ubuntu × windows × py 3.14), `dev_ci.yml` (lint + typecheck), `unstable_python_full_build.yml` (nightly on Python pre-release). |
| `03-example-workflows.md` | `ocarina-example` repo: `main_ci.yml` (lint + typecheck), `dev_ci.yml`, `e2e.yml` (ubuntu + Redis service + Firefox + geckodriver 0.35.0). |
| `04-ai-workflows.md` | `ocarina-with-ai-example` repo: `ai_proof_ci.yml` (lint + typecheck), `ai_proof_e2e.yml` (ubuntu × Firefox/Chrome matrix). |
| `05-igoristan-workflows.md` | `igoristan` repo: `ci-pr.yml` (ubuntu × node 24 + pnpm 10, 3 parallel jobs), `deploy.yml` (push main → GitHub Pages). |
| `06-holy-book-workflow.md` | `ocarina-holy-book` repo: `deploy.yml` (VitePress build + Pagefind index + GitHub Pages deploy). |
| `07-tests-workers-vercel.md` | `tests-workers` repo: no GitHub Actions. Vercel auto-deploys on push to main. **Contains ASCII diagram.** |

## Key concepts

- **No workflow in tests-workers**: deployment is Vercel-managed, not GitHub Actions. Article 07 documents the Vercel auto-deploy flow with a diagram.
- **`ocarina` cross-platform matrix**: `main_ci.yml` runs on ubuntu + windows × Python 3.14. This is the only repo with a Windows runner.
- **`unstable_python_full_build.yml`**: nightly canary run on Python pre-release to catch breakage before a new Python version ships.
- **geckodriver version pinning**: `ocarina-example`'s `e2e.yml` manually downloads geckodriver 0.35.0 (not auto-matched). `ocarina`'s own CI uses auto-matched chromedriver.
- **Redis service container**: `e2e.yml` in `ocarina-example` spins up a Redis service container for the distributed lock tests. The container is available at `redis://localhost:6379` during the run.
- **Heroku warm-up**: `ai_proof_e2e.yml` pings CURA Healthcare before running tests (Heroku eco-dyno cold starts).
- **Allure history**: after each `ocarina` CI run, a composite action (`allure-history`) appends the new report to GitHub Pages, maintaining a browsable history.

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
