# Skill: answer-from-primer

**Goal**: answer a question about the Ocarina ecosystem from the primer — correctly, at the right depth, with explicit gap awareness.

This skill is self-contained. Load it alone and follow it start to finish.

**Primer base URL**: `https://mojo-molotov.github.io/from-ocarina-to-igor/`  
**Related skills** (standalone, load separately if the question explicitly calls for it):
- Cross-chapter synthesis: `{base}/skills/synthesize/SKILL.md`
- Symbol lookup (when you know the class/method name): `{base}/skills/locate/SKILL.md`
- Navigate / fetch only (rare): `{base}/skills/navigate/SKILL.md` · `{base}/skills/fetch/SKILL.md`

---

## Principles — read once, apply throughout

1. **Never invent.** API signatures, class names, config keys, error types — if you haven't read them in a source, don't write them. "I don't know" is correct; making something plausible up is not.
2. **Minimize fetches.** Every fetch costs context. Stop at the brief if it answers the question. Skip the brief entirely if a sub-router (see Step 1) points straight at the article.
3. **Don't re-fetch.** If you already read a brief or article earlier in this conversation, reuse it. Only re-fetch if you specifically need a section you skipped.
4. **Lead with the answer, not the navigation path.** The user doesn't want "I fetched ch02 then read article 05-orchestration/02..." — they want the answer. Show your work only if asked.
5. **Be explicit about what's missing.** If the primer doesn't cover something, name the gap clearly. Vague hedging ("might be in there somewhere") is worse than a direct "not documented here, try X".

---

## Step 1 — route the question

**Before the table, check these short-circuits:**

- **Symbol lookup** (you know a class, method, type, CLI flag, endpoint, or error code by name): load `locate/SKILL.md` instead — it routes by symbol directly to the article, faster than this table.
- **Multi-chapter question** (the answer clearly requires tracing a relationship between two or more chapters — e.g. "compare X in ocarina-example vs ocarina-with-ai-example", "how does the philosophy show up in the framework"): load `synthesize/SKILL.md` — it has the inter-chapter map and procedure.
- **Out of scope** (the question is clearly not about Ocarina at all): say so, don't pretend to route it.

Otherwise, match the question against the table below. Pick the **first** matching row.

| Topic keywords | Brief | Typical articles to go deeper |
| --- | --- | --- |
| ecosystem, repos, overview, stack matrix, execution flow, repo relations | `ch00-big-picture` | `00-big-picture/01-ecosystem-map.md`, `03-global-execution-flow.md` |
| philosophy, KISS, ISTQB, "why does Ocarina", citations, influences, political, anti-hype, anti-SaaS | `ch01-philosophy` | `01-philosophy/02-istqb-vs-pytest.md`, `05-political-stance.md` |
| framework, Result, Ok, Err, ROP, railway, ActionChain, validate, invariant, orchestration, TestSuite, TestCampaign, TestCycle, Scenario, Watcher, POMBase, ports, DriversPool, bootstrap, CLI, retry, saturation | `ch02-ocarina` | `02-ocarina/03-railway/`, `04-invariants/`, `05-orchestration/` |
| functional, FP, thunk, closure, fold, reduce, lazy, generics, PEP 695, discriminated union, TypeGuard | `ch03-functional` | `03-functional/01-effect-thunk-result.md`, `07-discriminated-unions-typeguards.md` |
| internal tests, cram, prysk, pytest-mypy-plugins, syrupy, hypothesis, coverage, Allure | `ch04-internal-tests` | `04-internal-tests/` — article matching keyword |
| igoristan, SUT, React, Vike, wireit, useAuth, OTP, commitlint, Husky, chaotic | `ch05-igoristan` | `05-igoristan/` — article matching keyword |
| tests-workers, Vercel Edge, OTP endpoint, Corsicadex, Redis, Upstash, authorization, coordination | `ch06-tests-workers` | `06-tests-workers/07-otp-coordination-flow.md` for the big picture |
| ocarina-example, canonical, adapters, login, Corsicamon, randomness, sacred upload, HumanizedDriver, caches, locks, EnvGetters, watcher catch | `ch07-ocarina-example` | `07-ocarina-example/` — article matching keyword |
| AI example, Claude, CURA, co-written, gaps, security, data, spec, bfcache | `ch08-ai-example` | `08-ai-example/` — article matching keyword |
| Holy Book, VitePress, i18n, skills, CLAUDE.md, PDF, public resources | `ch09-holy-book` | `09-holy-book/` — article matching keyword |
| CI, CD, workflow, GitHub Actions, matrix, geckodriver, Allure history, Vercel deploy | `ch10-cicd` | `10-cicd/01-matrix.md` first, then per-repo article |
| independence, sovereign, auditability, refusal, async, DSL, No-Code | `ch11-independence` | `11-independence/` — all three articles are short |
| manifesto, hacker, LulzSec, YTCracker, Zone-H, DEF CON, villain, λ-calculus, DHH, Paul Graham, infopreneur, SaaS fraud, survivor, underground | `ch12-manifesto` | `12-manifesto-deciphered/` — article matching keyword |
| glossary, term, definition, cited files, cited people | `ch99-references` | `99-references/01-glossary.md` |

**If no row matches**: skip to **Step 4 — Handling gaps**. Do not guess a chapter.

**Escalation rule**: if while answering you find yourself heavily leaning on concepts that live in another chapter (not just citing them — really borrowing from them), stop and load `synthesize/SKILL.md`. The table optimizes for the primary chapter; cross-chapter answers need explicit tracing.

### Disambiguation — when keywords overlap

Several keywords appear in multiple rows. Use intent to pick:

| Ambiguous keyword | Use this chapter when… |
| --- | --- |
| **OTP** | UI/auth side of Igoristan → ch05 · Edge endpoint generating it → ch06 · how a test consumes it → ch07 |
| **matrix** | Stack matrix per repo → ch00 · CI workflow matrix → ch10 |
| **CLI** | Framework's CLI machinery (`SeleniumCLI`, `CLIBuilder`, `--only`, `--exclude`) → ch02 · CI workflow CLI invocation → ch10 |
| **skills** | The 40+ skills inside the Holy Book → ch09 · the four primer skills (this file, locate, navigate, etc.) → no chapter, they're meta |
| **Watcher** | Framework primitive → ch02 · Concrete `catch_me_if_you_can` usage → ch07 |
| **adapter** | Framework's port/adapter pattern (`ILogger`, `ITakeScreenshot`) → ch02 · `ocarina-example`'s 5 adapters (`act`, `match_page`, etc.) → ch07 |
| **CI / workflow** | Per-repo CI structure overview → ch10 · CI for a specific repo's tests (e.g. e2e logic) → that repo's chapter |
| **scenarios** | The `Scenario` primitive → ch02 · Concrete scenario families → ch07 (canonical) or ch08 (AI-written) |

### Ch02 is large — route by sub-area first

Ch02 has 40+ articles across 5 sub-folders. Before fetching the brief, pick the sub-area:

| Question is about… | Sub-folder |
| --- | --- |
| `Result[T]`, error propagation, chain composition, action lifecycle (`create`/`act`), page navigation | `02-ocarina/03-railway/` |
| `validate`, `assert_that`, invariant errors, business vs framework validators | `02-ocarina/04-invariants/` |
| `Test`, `TestSuite`, `TestCampaign`, `TestCycle`, retry, saturation, filtering by ID, smoke modes | `02-ocarina/05-orchestration/` |
| `DriversPool`, `DriverBuilder`, `Screenshotter`, `ActCounter`, Selenium adapters | `02-ocarina/10-infra/` |
| `bootstrap`, `CLIBuilder`, `SeleniumCLI`, loggers, reporter plugins | `02-ocarina/11-opinionated/` |
| `Scenario`, `Watcher`, `POMBase`, `ILogger`/`ITakeScreenshot` ports, custom types/errors | `02-ocarina/06-*` to `09-*`, `12-*` |

Read the ch02 brief only if you need the overall map. For a precise question, jump straight to the sub-folder article.

---

## Step 2 — fetch at the right depth

**Determine your access mode first:**

| Tools available | Mode |
| --- | --- |
| Bash/shell (Read, grep, git) | **Local** — read files directly from the cloned repo |
| Bash, but repo not cloned | **Clone** — run `git clone https://github.com/mojo-molotov/from-ocarina-to-igor.git /tmp/from-ocarina-to-igor`, then use Local mode |
| WebFetch only, no shell | **Remote** — fetch by URL |

**Fetch the brief first:**
- Local/Clone: `site/static/llms/{brief-slug}.md`
- Remote: `https://mojo-molotov.github.io/from-ocarina-to-igor/llms/{brief-slug}.md`

**Read the brief. Stop here if it answers the question.**

Brief is enough when: the question is about what exists, the general flow, or which file to look at.

**If article depth is needed**, fetch the specific article:
- Local/Clone: `site/content.en/{article-path}`
- Remote (GitHub raw): `https://raw.githubusercontent.com/mojo-molotov/from-ocarina-to-igor/main/site/content.en/{article-path}`

**Volume guideline**: ~8 articles is roughly the dense content of one full chapter. Beyond that, you're consuming more context than you're producing answer value — ask the user to narrow the scope. Treat it as a soft ceiling, not a hard cliff.

---

## Step 3 — answer

Rules:

- Lead with the answer, not the navigation path taken.
- **Quote** when precision matters (signatures, exact parameter names, error types) — label the source file.
- **Paraphrase** for flows and concepts — shorter and cleaner.
- **Diagrams**: reproduce ASCII verbatim, never reformat. Put in a plain fenced code block.
- **Cross-chapter**: make the connection explicit, not two separate summaries.
- Code blocks for signatures and exact values. Tables for option comparisons.

---

## Step 4 — handling gaps

This step has two modes:

**A. The question itself is out of scope** (you arrived here from Step 1 because no row matched).  
Don't answer from a chapter. Open with a clean "not documented in the primer" — then offer the next-best source (see below).

**B. You answered, but partially** (post-Step-3 check).  
Re-read your answer. If you implied the primer covers more than it does, correct yourself. Name what's missing.

In both modes, use the boundaries below to be specific about why.

### The primer's known boundaries

- **Versioned to v1.1.10.** Post-1.1.10 API changes aren't here.
- **No runtime state.** Secrets, live Redis keys, current OTP values, current deployments — never documented.
- **Igoristan routes are structural, not behavioral.** The primer describes what each route is for, not the JS/TS implementation detail.
- **No step-by-step debugging procedures.** Selenium/geckodriver troubleshooting isn't covered.
- **Internal helpers and deprecated APIs** are deliberately excluded.

Write the gap declaration in your own words. Be specific about what's missing and why. Don't recite — explain.

### When you need to point outside the primer

In decreasing authority:

1. **Holy Book** `https://mojo-molotov.github.io/ocarina-holy-book/` — user-facing setup, onboarding, 40+ skills. Fetch `llms-full.txt` for full content.
2. **Source code** — six public repos at `https://github.com/mojo-molotov/`. `ocarina` is ~3 000 lines with dense docstrings.
3. **Holy Book skills** — `https://github.com/mojo-molotov/ocarina-holy-book/tree/main/docs/.vitepress/public/skills`

When you synthesize from these rather than quote the primer, label it: _"This is synthesis from [source], not official primer documentation."_

---

## Worked example

**Question**: "What's the retry policy in Ocarina? Does it back off exponentially?"

**Step 1 — route**: keywords "retry" → ch02 row. Sub-area router → `02-ocarina/05-orchestration/`. Question names a precise behavior → article depth needed.

**Step 2 — fetch**: skip the ch02 brief (too broad). Fetch the orchestration sub-folder. Article `03-test-flow-retries.md` matches by filename.

**Step 3 — answer**:

> Retry is in `TestFlow` (`src/ocarina/dsl/testing/internals/test_flow.py`), not in `TestExecutor`. Defaults to **9 attempts** (`max_retries=8`, `max_attempts=1 + max_retries`).
>
> Backoff is **linear**, not exponential: `time.sleep(attempt)` before each retry. Worst-case cumulative sleep over 9 attempts: 45s. Exponential (`2^attempt`) was rejected explicitly — it would have produced ~17 minutes.
>
> A fresh `WebDriver` is acquired from the pool for every attempt (`with self._drivers_pool.acquire() as driver`).
>
> Only failures matching `transient_errors` (passed at suite construction) trigger a retry; non-transient failures terminate immediately. If `setup()` fails on **all** attempts, the test is marked SKIPPED rather than FAILED — distinguishes infrastructure failure from functional failure.

**Step 4 — gap check**: nothing missing. The article covers the policy completely. No gap declaration needed.

**Key things this example demonstrates**:
- Skipped the brief because the question was precise — went straight to the article.
- Quoted the source file path when naming the file.
- Used a code-style block for `time.sleep(attempt)` because it's exact.
- Made the design decision visible (why linear, not exponential) — that's in the article and matters.
- Didn't pad the answer with the navigation path taken.
