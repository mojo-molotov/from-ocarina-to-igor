# Ch 11 — Independence

Chapter brief for LLM navigation. Source articles: `site/content.en/11-independence/`.

## Articles

| File | Description |
| --- | --- |
| `01-sovereign-grammar.md` | No imposed DSL, no ecosystem lock-in, extension by composition. Why Ocarina's vocabulary is sovereign. |
| `02-auditability.md` | "Auditable in an afternoon": 1 runtime dependency (`python-docx`), 3,610 SLOC, MIT. Anti-No-Code. |
| `03-explicit-refusals.md` | Documented explicit refusals: `async`/`await`, pytest plugin, "stylish" contributions, "geek stuff". |

## Key concepts

- **"Sovereign grammar"**: Ocarina uses its own vocabulary (`Test`, `TestSuite`, `TestCampaign`, `TestCycle`, `Scenario`, `act`, `validate`) rather than pytest fixtures, unittest assertions, or any third-party DSL. Changing the test runner doesn't break your tests.
- **"Auditable in an afternoon"**: the entire framework is 3,610 SLOC (AST count, excluding blank lines, comments and docstrings; ~8,000 raw lines in `src/`) with one runtime dependency (`python-docx`). Any competent developer can read and understand the full source in a working day. This is a design constraint, not an accident.
- **Anti-No-Code**: No-Code tools abstract away the code in a way that makes auditing impossible and puts the user at the mercy of the tool vendor. Ocarina explicitly refuses this direction.
- **`async`/`await` refusal**: explicitly documented. Selenium is synchronous; adding `async` complexity to tests adds cognitive overhead with no benefit for the use case. The refusal is final, not provisional.
- **Pytest plugin refusal**: Ocarina does not integrate as a pytest plugin. It is a standalone orchestrator. Using pytest as a runner would mean living under pytest's conventions and lifecycle, which contradicts sovereign grammar.
- **"Stylish" contributions refusal**: contributions that add complexity for aesthetic reasons (clever abstractions, metaprogramming, etc.) are refused. KISS is enforced at the contribution level.

## Connections

- Philosophy that motivates independence → Ch 01
- The explicit refusals in practice → Ch 02 (no async, no pytest integration)
- Political stance → Ch 01 (`05-political-stance.md`)
- Manifesto context → Ch 12 (`11-saas-arr-fraud.md`, `08-ocarina-in-testing-industry.md`)

## Not covered here

Alternative frameworks' approaches to independence. Migration guides from Playwright/Cypress to Ocarina (not documented anywhere in the primer).

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
