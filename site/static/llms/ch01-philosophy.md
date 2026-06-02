# Ch 01 — Philosophy

Chapter brief for LLM navigation. Source articles: `site/content.en/01-philosophy/`.

## Articles

| File | Description |
| --- | --- |
| `_index.md` | Chapter landing page. Framing: Ocarina is opinionated; the philosophy is the filter that killed every feature, DSL and shortcut along the way, not a decorative preamble. |
| `01-flip-the-problem.md` | The bet opposite to Robot Framework / Cucumber: dissolve the technical/non-technical barrier with AI as the bridge, not a DSL. |
| `02-istqb-vs-pytest.md` | Why ISTQB methodology is the reading grid and pytest/Jest/Mocha are hybrids. Consequence: the four-level hierarchy `Test → TestSuite → TestCampaign → TestCycle`. |
| `03-kiss-and-complexity.md` | KISS done right: rejection of ostentatious complexity, rejection of "declarative object-oriented", rejection of rewriting in Rust. |
| `04-citations-and-influences.md` | Full reference table: Wlaschin, λ-calculus, Lessig, DHH, Paul Graham, Bugayenko, Terry Davis, Lao-Tzu, Saint-Exupéry, Proust, Watts, Rilke, YTCracker, LulzSec, Lee Robinson, Cluely. |
| `05-political-stance.md` | Incorruptibility, anti-hype, anti-armchair-experts, anti-No-Code, secession, _Code is Law_, refusal of `async`/`await`. |

## Key concepts

- **"Flip the problem"**: instead of a DSL so non-technical stakeholders can write tests, Ocarina gives structured typed code so AI can write tests that non-technical stakeholders can read.
- **ISTQB vocabulary** is a deliberate political choice — it is the shared grammar of the testing profession, not a pytest/unittest convention.
- **KISS as a filter**: every feature, shortcut, and DSL that was refused was refused by applying KISS. The result is ~4,060 SLOC (AST count, excluding blank lines, comments and docstrings; ~8,700 raw lines in `src/`) with one runtime dependency (`python-docx`).
- **Political stance**: Ocarina refuses SaaS, refuses `async`/`await` (not a testing concern), refuses No-Code (anti-intellectual), refuses careerist influencer culture.
- **Citations are sourced**: every quote in the Holy Book manifesto has an attributed source. Ch 12 documents them all.
- **Opinionated by design** (chapter framing): the philosophy isn't a decorative preamble — it's the filter that ruled out every feature, DSL and shortcut. Ocarina refuses to be all things to all people.

## Connections

- ISTQB hierarchy in code → Ch 02 (orchestration)
- ROP as implementation of "flip the problem" → Ch 02 (railway)
- Political stance applied → Ch 11 (independence, explicit refusals)
- All citations traced → Ch 12 (manifesto)
- AI-as-bridge proof of concept → Ch 08

## Not covered here

The Holy Book's onboarding chapters ("What is Ocarina?", "First feedbacks") are not reproduced here — read the Holy Book directly for user-facing setup guidance.

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
