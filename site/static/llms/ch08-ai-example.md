# Ch 08 — ocarina-with-ai-example

Chapter brief for LLM navigation. Source articles: `site/content.en/08-ai-example/`.

## Articles

| File | Description |
| --- | --- |
| `_index.md` | Chapter landing page. "Success story" (Code 99% Claude / 1% human; Intelligence 50/50). "Holy Book reminder": the four things this project is NOT (no autonomous test generation, no patching hallucinations in CI, no rewriting the spec, never runs active security tests). "Singularity": reading PHP source to find real defects, business-logic vulnerability tests, cross-browser divergence as a finding. |
| `01-ai-manifesto.md` | The repo README: "Code: 99% Claude / Intelligence: 50-50" headline, the AI co-authorship manifesto. |
| `02-sut-cura.md` | CURA Healthcare: external open-source PHP SUT hosted on Heroku eco-dyno (cold starts). |
| `03-canonical-documents.md` | The 4 canonical documents: `CLAUDE.md` (AI instructions), `CURA_FRD.md` (functional requirements), `CURA_TEST_STRATEGY.md`, `IDENTIFIED_GAPS.md`. |
| `04-test-strategy.md` | Test types: happy path, unhappy path, edge cases, business logic vulnerability, exploratory, regression. |
| `05-security-gaps.md` | Security gaps identified: CSRF (G-SEC-1), session management (G-SEC-2), rate limiting (G-SEC-3). |
| `06-data-gaps.md` | Data gaps: `visit_date` with no backend validation (G-DATA-1), duplicate appointments (G-DATA-2). |
| `07-spec-gaps.md` | Spec gaps: appointment history order (G-SPEC-1), profile placeholder (G-SPEC-2), redirect flows (G-SPEC-3). |
| `08-bfcache.md` | Chrome BFCache issue B-BROWSER-1 (back-forward cache breaks auth state) + env gaps A-ENV-1, A-ENV-2. |
| `09-ci-matrix.md` | CI: `ai_proof_ci.yml` (lint + typecheck) + `ai_proof_e2e.yml` (Firefox/Chrome matrix + Heroku warm-up + ChromeDriver stacktrace filtering). |

## Key concepts

- **"AI is the bridge"** proof of concept: Claude Code wrote 99% of the code. The human author wrote `CLAUDE.md` (AI instructions), the FRD, and the test strategy. The AI produced the scenarios, POMs, and adapters.
- **CURA Healthcare**: a deliberately external, real-world SUT (not author-controlled). PHP application with Heroku hosting — introduces cold start delays the test suite must handle.
- **Canonical documents**: the structured documents that allowed Claude to write the suite without human intervention in each session. `CURA_FRD.md` describes the application. `CURA_TEST_STRATEGY.md` defines what to test. `CLAUDE.md` gives the AI its operating constraints.
- **Gap taxonomy**: gaps are categorized and coded (G-SEC-*, G-DATA-*, G-SPEC-*, B-BROWSER-*, A-ENV-*). Each gap documents a discovered defect or limitation in the SUT.
- **CI matrix**: Firefox and Chrome are tested in parallel. ChromeDriver produces verbose stacktraces on known warnings — the CI workflow filters them to keep logs readable.
- **Heroku warm-up**: CURA's Heroku eco-dyno sleeps after inactivity. The CI workflow pings the app before running tests.
- **99/1 code, 50/50 judgement** (success story): almost every line was machine-written; the judgement — what to test, what to distrust, when to dig and when to stop — was shared.
- **Four things this project is NOT** (Holy Book reminder): it doesn't generate tests autonomously; doesn't patch hallucinations in CI (a failure triggers `review-report` + `analyse-*`); doesn't rewrite the spec (only `update-frd-and-tests` does, with a revision line); and never runs active security tests. The human keeps control; the AI produces the machinery.
- **The singularity**: reading the PHP source to find real defects (missing CSRF, client-only validation, history ordered by submission), business-logic vulnerability tests (past-date booking, duplicate appointments), and cross-browser divergence as a finding (Chrome BFCache restoring a `no-store` page after logout). Each gap is documented with `file:line` + PHP evidence and materialized as an intentionally red test.

## Connections

- Framework used → Ch 02
- Philosophy of "AI as bridge" → Ch 01 (`01-flip-the-problem.md`)
- Canonical suite for comparison → Ch 07
- AI use in Ocarina deciphered → Ch 12 (`14-real-ai-in-ocarina.md`, `15-typing-ai-rl-probes.md`)
- CI workflows → Ch 10

## Not covered here

The CURA Healthcare application's source code or business logic. Current state of identified gaps (whether they've been fixed upstream). Exact Claude prompts used during authorship (only `CLAUDE.md` is documented, not session transcripts).

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
