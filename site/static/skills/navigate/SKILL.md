# Skill: navigate-primer

**Goal**: given a question about Ocarina, return the right chapter brief to fetch — and the specific articles to read if the brief is not enough.

**Primer base URL**: `https://mojo-molotov.github.io/from-ocarina-to-igor/`  
**Briefs**: `{base}/llms/ch{NN}-{slug}.md`  
**Related skills**: `{base}/skills/fetch/SKILL.md` · `{base}/skills/answer/SKILL.md` · `{base}/skills/locate/SKILL.md` · `{base}/skills/synthesize/SKILL.md`

---

## Step 1 — classify the question

Match the question against the topic table below. Pick the **first** matching row.

| Topic keywords | Chapter brief | Typical articles to go deeper |
| --- | --- | --- |
| ecosystem, repos, overview, "what is", stack matrix, execution flow, repo relations | `ch00-big-picture` | `00-big-picture/01-ecosystem-map.md`, `03-global-execution-flow.md` |
| philosophy, KISS, ISTQB, "why", citations, influences, political, anti-hype, anti-SaaS | `ch01-philosophy` | `01-philosophy/02-istqb-vs-pytest.md`, `05-political-stance.md` |
| framework, Result, Ok, Err, ROP, railway, ActionChain, validate, invariant, orchestration, TestSuite, TestCampaign, TestCycle, Scenario, Watcher, POMBase, ports, DriversPool, bootstrap, CLI, Playwright, actor, owner thread, marshalling, call_timeout, DriverDiedError | `ch02-ocarina` | `02-ocarina/03-railway/`, `04-invariants/`, `05-orchestration/`, `10-infra/06-playwright-actor.md` |
| functional, FP, thunk, closure, fold, reduce, lazy, generics, PEP 695, discriminated union, TypeGuard | `ch03-functional` | `03-functional/01-effect-thunk-result.md`, `07-discriminated-unions-typeguards.md` |
| internal tests, cram, prysk, pytest-mypy-plugins, syrupy, hypothesis, coverage, Allure | `ch04-internal-tests` | `04-internal-tests/` — article matching keyword |
| igoristan, SUT, React, Vike, wireit, useAuth, OTP, commitlint, Husky, chaotic | `ch05-igoristan` | `05-igoristan/` — article matching keyword |
| tests-workers, Vercel Edge, OTP, Corsicadex, Redis, Upstash, authorization, coordination | `ch06-tests-workers` | `06-tests-workers/07-otp-coordination-flow.md` for the big picture |
| ocarina-example, canonical, adapters, login, Corsicamon, randomness, sacred upload, HumanizedDriver, caches, locks, EnvGetters, watcher catch | `ch07-ocarina-example` | `07-ocarina-example/` — article matching keyword |
| AI example, Claude, CURA, co-written, gaps, security, data, spec, bfcache, ai manifesto | `ch08-ai-example` | `08-ai-example/` — article matching keyword |
| Holy Book, VitePress, i18n, skills, CLAUDE.md, PDF, public resources | `ch09-holy-book` | `09-holy-book/` — article matching keyword |
| CI, CD, workflow, GitHub Actions, matrix, geckodriver, Allure history, Vercel deploy | `ch10-cicd` | `10-cicd/01-matrix.md` first, then per-repo article |
| independence, sovereign, auditability, refusal, async, DSL, No-Code | `ch11-independence` | `11-independence/` — all three articles are short |
| manifesto, hacker, LulzSec, YTCracker, Zone-H, DEF CON, villain, λ-calculus, DHH, Paul Graham, infopreneur, SaaS fraud, survivor, underground, typing, RL | `ch12-manifesto` | `12-manifesto-deciphered/` — article matching keyword |
| glossary, term, definition, cited files, cited people, references | `ch99-references` | `99-references/01-glossary.md` |

If no row matches → say so clearly. Do not guess a chapter. Offer to synthesize from the Holy Book or source code instead (see `gap-aware` section in `answer/SKILL.md`).

---

## Step 2 — fetch and decide depth

Fetch the identified brief using `fetch/SKILL.md` (`{base}/skills/fetch/SKILL.md`). Read it.

**Stop at the brief if**: the question is about what exists, the general flow, or which file to look at.

**Go to article depth if**: the question asks for a specific signature, a precise behavior, a code snippet, or an error type. In that case, use the brief's Articles table to pick the one or two articles that match.

**If the question spans multiple chapters** (e.g. "how does the AI example use the framework" → ch08 + ch02): list both briefs and fetch both. Hard limit: 3 chapters per question.

**Never open more than 3 articles without a clear reason.** The brief table is the filter.

To answer from what you've fetched: use `answer/SKILL.md` (`{base}/skills/answer/SKILL.md`).  
For cross-chapter relationships specifically: use `synthesize/SKILL.md` (`{base}/skills/synthesize/SKILL.md`).
