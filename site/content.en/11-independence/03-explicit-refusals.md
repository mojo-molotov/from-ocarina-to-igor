---
title: "11.03 — Explicit refusals"
description: "A synthesis of Ocarina's explicit refusals: async, a pytest plugin, a textual DSL and reactive programming, each with its rationale."
weight: 3
date: 2026-05-20
series: ["independence"]
series_order: 3
---

# 11.03&nbsp;—&nbsp;Explicit refusals

> Synthesis of refusals scattered across the Holy Book.

## Summary table

| Refusal                   | Reason                                                                                        | Reference              |
| ------------------------- | --------------------------------------------------------------------------------------------- | ---------------------- |
| `async`/`await`           | Selenium synchronous, Requests synchronous; readability; no point introducing an _event-loop_ | Holy Book              |
| pytest plugin             | Independence, ISTQB fidelity                                                                  | Ocarina `README`       |
| Text DSL (Robot, Gherkin) | No translation layer                                                                          | Holy Book              |
| Reactive programming      | Static scenarios, in-memory cache suffices                                                    | Holy Book              |
| Tricks and hacks          | "_Teach the pattern, not the symptom_"                                                        | `CLAUDE.md` ai-example |
| "_Stylish_" contributions | "_It's my car_"                                                                               | Holy Book              |
| Active security tests     | Functional and static only, never attacks                                                     | `CLAUDE.md` ai-example |

## 1. Refusal of `async`/`await`

Central quote:

> Ocarina doesn't support `async`/`await` and never will.

| Argument                | Response                                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| "_It's faster_"         | Not for Selenium (synchronous by nature)                                                                                        |
| "_Everyone does it_"    | Everyone often does it _badly_                                                                                                  |
| "_For HTTP APIs_"       | `requests` (synchronous) works just fine                                                                                        |
| "_For locks_"           | `threading.Lock` + `redis.lock` are enough                                                                                      |
| "_For parallelization_" | `ThreadPoolExecutor` (see [`../02-ocarina/05-orchestration/04-test-suite.md`](../02-ocarina/05-orchestration/04-test-suite.md)) |

## 2. Refusal to be a pytest plugin

Ocarina's `README`:

> Ships its own test runner: Ocarina is NOT a pytest plugin.

| With pytest plugin                                 | Standalone runner                               |
| -------------------------------------------------- | ----------------------------------------------- |
| pytest vocabulary (function, fixture, parametrize) | ISTQB vocabulary (test, suite, campaign, cycle) |
| Lifecycle depends on pytest                        | Own controllable lifecycle                      |
| Compatibility with other pytest plugins            | No API surface to maintain                      |
| Discoverable via `pytest --collect`                | Direct `python -u src/main.py`                  |

See [`../01-philosophy/02-istqb-vs-pytest.md`](../01-philosophy/02-istqb-vs-pytest.md)

## 3. Refusal of text DSLs

No `.robot`, `.feature`, `.spec.yml` files. Everything is Python.

Quote (Holy Book `what-is-it`):

> _Robot Framework_ tried to dodge that with a _DSL_ (...) **their own format** and **their own plugin ecosystem**. So RF de-facto imposes its own standards: that's the immediate cost of its promise.

| Text DSL                                            | Embedded Python DSL                |
| --------------------------------------------------- | ---------------------------------- |
| Translation layer (parser, alternative runtime)     | None: it's just Python             |
| Hard refactoring (search in `.robot`)               | Trivial refactoring (Python IDE)   |
| Impossible / partial type checking                  | Full type checking (`mypy strict`) |
| Proprietary tooling (PyCharm RF plugin, RIDE, etc.) | Any Python editor                  |

See [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md)

## 4. Refusal of reactive programming

Holy Book (chapter "_First jutsus_", "_Reactive programming: NO_" section):

> Ocarina test scenarios are intentionally static. Yet a web application is dynamic, and sometimes capturing a value on the fly to pass it to a later step is perfectly legitimate.
>
> Ocarina doesn't answer that. It doesn't need to.

Answer: in-memory cache + reserved keys (see [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md))

| With reactivity                                 | Without (cache)                      |
| ----------------------------------------------- | ------------------------------------ |
| Scenarios full of _streams_ and _subscriptions_ | Readable declarative scenarios       |
| Hard debugging (event flow)                     | Trivial debugging (sequential calls) |
| Subtle concurrency hazards                      | Simple `threading.Lock`              |
| Dependencies on RxPY or similar                 | No reactive dep                      |

## 5. Refusal of "_geek tricks_"

`CLAUDE.md` `ocarina-with-ai-example`:

> **No tricks or hacks.** JS-clicks to skip hit-testing, `# noqa` to silence a rule, `time.sleep` to mask a race, `driver.implicitly_wait` to patch a timing bug. If a hack is genuinely the only option, document why no clean fix exists and mark it so a reader doesn't copy the pattern. The JS-click-for-logout incident is the canonical anti-example: `ElementClickInterceptedException` had a clean polling fix; the JS click hid the problem.

| Hack                                                        | Why it's NO                                                |
| ----------------------------------------------------------- | ---------------------------------------------------------- |
| `driver.execute_script("...click()")` to bypass hit-testing | Hides a real UI defect; a human user couldn't have clicked |
| `# noqa` without justification                              | Hides a real style/security violation                      |
| `time.sleep(N)` to mask a race condition                    | "_Mysterious timing_" nonsense                             |
| `driver.implicitly_wait(N)` patched outside the framework   | Decouples from the CLI `--wait-timeout` config             |
| `delete_all_cookies()` to "_reset state_"                   | A user doesn't do this; hides a real session bug           |
| `driver.refresh()` to bypass cache                          | A user doesn't do this; hides a real bug                   |
| Query-string cache busters (`?_=<ts>`)                      | Same                                                       |

If a hack is **really** necessary: document why.

## 6. Refusal of "_stylish_" contributions

Holy Book (chapter "_First feedbacks_", "_Incorruptibles_" section):

> "_Handing over Ocarina means handing over a car I've maintained entirely myself, for myself, hence very carefully. That said, it is and will remain handed over as-is. It's my car._"

And:

> "_Contributing to an open-source project because it's "stylish" is a totally immature view, and tolerance for this phenomenon causes havoc._"

Contribution acceptance criterion: **alignment** with the direction. Not "_does it work_" but "_does it respect the project's philosophy?_".

The author quotes DHH:

> [My response will be supplemented with a David Heinemeier Hansson (DHH) quote: "Fuck You".](https://world.hey.com/dhh/i-won-t-let-you-pay-me-for-my-open-source-d7cf4568)

[![Fuck you](/assets/img/dhh-fuck-you-vendoritis-2006.jpg)](https://world.hey.com/dhh/i-won-t-let-you-pay-me-for-my-open-source-d7cf4568)

## 7. Refusal of active/offensive security tests

`CLAUDE.md` `ocarina-with-ai-example`:

> This is a **functional** test suite. (...) Inside that scope:
>
> - Static analysis is welcome and encouraged.
> - Functional tests that exercise security-relevant behaviour through the **normal UI/HTTP path** (...) are fine.
>
> **Forbidden, no exceptions:**
>
> - Crafted attack payloads of any kind: SQL injection strings, XSS / HTML / JS payloads, command injection, header/parameter pollution, path traversal, deserialisation payloads.
> - Token tampering, signature stripping, cookie forgery, session-fixation attempts, forced-browsing fuzzers.
> - Cross-origin POSTs constructed outside the suite, scripted directory enumeration, DOS, rate-floods&nbsp;—&nbsp;anything that escalates from "use the app like a user" to "attack the app like an adversary".

**Strict** limit: use the app like a user, don't attack it like an adversary.

Active testing is a different project (Burp, ZAP, sqlmap, a separate contract and dedicated scope).

## Why

Every refusal **recenters** the project:

| Refusal                      | Simplification                          |
| ---------------------------- | --------------------------------------- |
| No `async`                   | Readable synchronous code               |
| No pytest plugin             | No incomprehensible pytest API to learn |
| No text DSL                  | No parser to maintain                   |
| No reactivity                | Simple cache suffices                   |
| No hacks                     | Expressive code                         |
| No "_stylish_" contributions | Coherent direction                      |
| No active security tests     | Respect for the functional perimeter    |

Saying `no` is also design. Cf. Steve Jobs: "_Innovation is saying no to 1,000 things._"

## Refusal of growth without benefit

None of these refusals is dogmatic. Each is **justified** by an explicit trade-off:

```
Hypothetical benefit: X
Operational cost: Y
Verdict: not worth it
```

If a new use case justifies reconsidering a refusal, the author will. But the burden of proof is on the proposer.

That's the practical embodiment of sovereignty.
