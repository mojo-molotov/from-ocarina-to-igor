# Ch 08 — ocarina-with-ai-example

Chapter brief for LLM navigation. Source articles: `site/content.en/08-ai-example/`.

## Articles

| File | Description |
| --- | --- |
| `01-ai-manifesto.md` | The repo README: "Code: 99% Claude / Intelligence: 50-50" headline, the AI co-authorship manifesto. |
| `02-sut-cura.md` | CURA Healthcare: external open-source PHP SUT hosted on Heroku eco-dyno (cold starts). |
| `03-canonical-documents.md` | The 4 canonical documents: `CLAUDE.md` (AI instructions), `CURA_FRD.md` (functional requirements), `CURA_TEST_STRATEGY.md`, `IDENTIFIED_GAPS.md`. |
| `04-test-strategy.md` | Test types: happy path, unhappy path, edge cases, business attack, exploratory, regression. |
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

## Connections

- Framework used → Ch 02
- Philosophy of "AI as bridge" → Ch 01 (`01-flip-the-problem.md`)
- Canonical suite for comparison → Ch 07
- AI use in Ocarina deciphered → Ch 12 (`14-real-ai-in-ocarina.md`, `15-typing-ai-rl-probes.md`)
- CI workflows → Ch 10

## Not covered here

The CURA Healthcare application's source code or business logic. Current state of identified gaps (whether they've been fixed upstream). Exact Claude prompts used during authorship (only `CLAUDE.md` is documented, not session transcripts).
