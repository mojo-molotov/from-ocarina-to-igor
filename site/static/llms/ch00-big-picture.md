# Ch 00 — Big picture

Chapter brief for LLM navigation. Source articles: `site/content.en/00-big-picture/`.

## Articles

| File | Description |
| --- | --- |
| `_index.md` | Chapter landing page. Framing: cartography of the ecosystem — who talks to whom, who depends on what, which way the data flows. Cross-links to philosophy (Ch 01), the framework (Ch 02), both example suites (Ch 07/08), the SUT (Ch 05) and the OTP/Corsicadex backend (Ch 06). |
| `01-ecosystem-map.md` | ASCII diagram: the six repos on one map, their role, license, and the contract binding them. **Contains ASCII diagram.** |
| `02-stack-matrix.md` | Tech stack per repo: language, runtime deps, build tool, deployment target, current version. |
| `03-global-execution-flow.md` | End-to-end execution flow: USER → CLI → DriversPool → TestCycle → SUT → Plugins. **Contains ASCII diagram.** |
| `04-repo-relations.md` | Bilateral dependency map: who imports what, who consumes which artifact, which secrets are shared. |

## Key concepts

- **Six repositories**: `ocarina` (framework, Python, MIT), `ocarina-example` (canonical e2e suite), `ocarina-with-ai-example` (AI co-written suite), `igoristan` (public SUT, React/Vike/Tailwind, GitHub Pages), `tests-workers` (Vercel Edge OTP backend), `ocarina-holy-book` (VitePress public docs).
- `ocarina` is the only shared runtime dependency — all test suites import it, nothing else does.
- `igoristan` is intentionally chaotic; it is the SUT for `ocarina-example`.
- `tests-workers` exposes OTP and Corsicadex endpoints (primitives). It does not coordinate anything — coordinating across distributed parallel runs is left to the tests, which must make do with what the endpoints expose (e.g. the deliberately ms-stripped OTP timestamp).
- The global execution flow: a CLI call triggers a `TestCampaign`, which fans out into `TestCycle`s, each managing a `DriversPool`, running `Test` objects against the SUT, and funneling results through reporter plugins (Allure, JSON).

## Diagrams

- `01-ecosystem-map.md` — full ecosystem ASCII map (6 repos, data flows, dependency arrows).
- `03-global-execution-flow.md` — end-to-end campaign execution flow diagram.

## Connections

- Framework internals → Ch 02
- Philosophy behind the design → Ch 01
- Canonical test suite → Ch 07
- AI test suite → Ch 08
- Public SUT detail → Ch 05
- OTP backend detail → Ch 06
- All CI workflows → Ch 10

## Not covered here

Stack versions beyond v1.1.9, runtime environment state, secrets layout, live deployment status.

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
