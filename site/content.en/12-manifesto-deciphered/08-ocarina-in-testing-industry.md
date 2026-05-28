---
title: "12.08 — Ocarina in the testing industry"
description: "Why Ocarina is not a better pytest or Cypress but structurally elsewhere: the shift it represents in the testing industry."
weight: 8
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 8
tags: ["istqb", "typing"]
---

# 12.08&nbsp;—&nbsp;Ocarina in the testing industry

> Ocarina isn't a _better_ pytest, isn't a _better_ Robot Framework, isn't a _better_ Cypress. It's **structurally elsewhere**. This chapter tries to explain the _shift_ it represents and the head start it takes.

## 1. The current industry map

### Three big e2e tool families

| Family             | Examples                                                | Model                                                 |
| ------------------ | ------------------------------------------------------- | ----------------------------------------------------- |
| **Text DSLs**      | Robot Framework, Cucumber + Gherkin                     | Permanent translation layer between _text_ and _code_ |
| **Runner plugins** | pytest-selenium, pytest-playwright, pytest-bdd          | Grafted onto pytest, inherit its lifecycle            |
| **Vendor SaaS**    | BrowserStack, Sauce Labs, LambdaTest, Cypress Dashboard | Local runner + paid execution cloud                   |

### Three shared _friction surfaces_

| Friction                       | Manifestation                                                                            |
| ------------------------------ | ---------------------------------------------------------------------------------------- |
| **Marketing > Technical**      | Tools sold on demos, conferences, and _oriented_ certifications. _Hype_ drives adoption. |
| **Vendor lock-in**             | Once adopted, refactor is costly, _hostage taking_.                                      |
| **Misplaced cognitive effort** | Understanding the tool takes longer than doing the work.                                 |

## 2. Ocarina's technical bet

1. **No text DSL** → pure Python, _embedded DSL_.
2. **No pytest plugin** → integrated runner, absolute ISTQB fidelity.
3. **No `async`/`await`** → simplicity, Selenium-synchronous compatibility, no "_geek tricks_".
4. **No SaaS** → all local, very dense core, _white box_.

See also: [`../11-independence/03-explicit-refusals.md`](../11-independence/03-explicit-refusals.md)

None of these refusals is without reason. Each is **justified** by an explicit trade-off, and their **combination** produces a solution with no direct equivalent on the market.

## 3. The _shift_ Ocarina represents

### First axis: return to the _vocabulary_ of testing (ISTQB)

The modern e2e industry has a _mixed_ vocabulary: "_pytest fixture_", "_Gherkin step def_", etc. No business actor (ISTQB-certified functional tester) has this vocabulary in mind.

| ISTQB      | Ocarina        |
| ---------- | -------------- |
| Test step  | `act`          |
| Test case  | `Test`         |
| Test suite | `TestSuite`    |
| Campaign   | `TestCampaign` |
| Cycle      | `TestCycle`    |

It's a _shift_: the code _becomes readable_ by a functional tester.  
Not just by a Python developer.

### Second axis: make _strict typing_ a business discipline

No popular e2e framework has `mypy strict = true` as a prerequisite.  
Ocarina does.

- Errors are caught **before execution**.
- The DSL is **enforced by the compiler** (mixing heterogeneous POMs in a `drive_page` is a _mypy_ error, not a runtime error).
- Maintenance is extremely guided (the _type checker_ rechecks consistency after every change).

It's a _shift_: we _move the effort_ from _when it breaks_ to _when it's written_.

### Third axis: make AI a first-class client

Ocarina _actively_ exposes to LLMs:

- `llms.txt`, `llms-full.txt`.
- `CLAUDE.md`, `CLAUDE.slim.md`.
- 40+ versioned skills (`SKILL.md`).
- An entire e2e suite co-written by Claude (`ocarina-with-ai-example`).

No competing test framework has this _AI surface_.  
It's a _shift_: we _design the DSL to be consumable by AI and human_, not just human.

### Fourth axis: make _grammatical sovereignty_ a promise

Ocarina doesn't ship a fixed DSL. It ships:

- `ChainRunner[T]` as the extension point.
- "_Project adapter_" pattern as convention.
- Closure-based composition rather than inheritance.

Each project writes **its own framework on top of the framework** (`act`, `match_page`, `TestSuite` adapter, `TestCampaign` adapter, `EnvGetters`).

It's a _shift_: we _give the grammar back_ to the project, rather than fully entrusting it to the tool.

## 4. Head start

### Where Ocarina is ahead

| Axis                             | Estimated lead vs the industry                                                      |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| **Strict typing in e2e**         | 5-10 years (most frameworks stay `Any`-everywhere)                                  |
| **AI-first**                     | 2-5 years (others start exposing MCP/AI hooks, though with a questionable approach) |
| **Embedded vs text DSL**         | Permanent (philosophical difference, no catch-up planned)                           |
| **ISTQB vocabulary**             | Permanent (philosophical difference)                                                |
| **Auditability (1 runtime dep)** | Permanent (philosophical difference)                                                |
| **ROP as core**                  | 5-10 years (most use classic exceptions)                                            |

### Where Ocarina isn't ahead

| Axis                   | Reality                                                                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Notoriety**          | None in the mainstream. Target audience: advanced testers.                                                                                       |
| **Plugin ecosystem**   | Deliberately minimal. The Python ecosystem is one of the industry's largest and can be directly embedded in an Ocarina project without friction. |
| **Cloud-as-a-service** | None (deliberate). On the other hand, Ocarina is natively built for _horizontal scaling_.                                                        |
| **Multi-language**     | Python only (deliberate).                                                                                                                        |

### Vision

Ocarina **starts from the following hypotheses**:

1. **The market will shift** toward _fewer platforms_, _more clean code_, _more internal development_. The Sanity → Markdown evolution (Lee Robinson, Cursor, December 2025, confirmed by Sanity themselves in their public response) is a signal.
2. **AI will replace frameworks with long learning curves**. Why learn _Robot Framework_ if Claude can write a Python test in 5 seconds? That's what the author calls a [_Juicero press_](https://www.ouest-france.fr/leditiondusoir/2017-09-06/juicero-la-machine-a-jus-de-fruits-qui-ne-sert-a-rien-f38d8076-6c38-4d7b-a57a-947e5e247dda).
3. **Functional testers will be _revalued_** because they'll carry the _business vision_, while AI carries the _technique_.

If these three hypotheses hold (and there are signals they will), Ocarina is exactly in the right place.

If they don't, Ocarina will remain a niche project, but the author accepts that explicitly ("_It's my car_").

## 5. The market&nbsp;—&nbsp;honest analysis

### Short term (2026-2028)

- Ocarina will remain **niche**. No enterprise tooling, no SLAs, no paid support.
- Adoption by **consultants** who want a _portable_ tool ("_Ocarina in your pocket_").
- Adoption by **functional testers** who want to deliver rather than waste time on endless "_geek tricks_".
- Adoption by **solo devs / boutique agencies** who write their own tests.
- Adoption by **security-paranoid teams** that can't use SaaS.

### Medium term (2028-2032)

Three scenarios:

#### Scenario A&nbsp;—&nbsp;Ocarina stays niche

- 500-2000 users.
- Small but tight-knit community.
- No market influence.
- The author doesn't give a damn. The adventure continues. The code stays auditable.

#### Scenario B&nbsp;—&nbsp;Ocarina influences without being adopted

- More likely. Ocarina's **ideas** (strict typing in e2e, ISTQB vocabulary, AI-first) diffuse and are picked up by more popular frameworks.
- Ocarina isn't massively adopted, but becomes the _intellectual reference_ that gets cited.
- Like Hindley-Milner for programming languages: few people write it in practice, but all modern languages are heirs.

#### Scenario C&nbsp;—&nbsp;Ocarina is widely adopted

- Less likely. Requires a triggering event.
- If it happens: Ocarina will have waited for its moment.

### Long term (2032+)

Ocarina is built to _outlive its author_. The code is small, audited, MIT. Fork it, pick it up, maintain it.

## 6. Qualitative comparison with some alternatives

| Aspect                           | Ocarina                                                                                         | Robot Framework               | Playwright                               | Cypress                   | Selenium IDE        |
| -------------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------- | ---------------------------------------- | ------------------------- | ------------------- |
| Text DSL                         | ❌ Pure Python                                                                                  | ✅ .robot files               | ❌ Pure TS                               | ❌ Pure JS                | ✅ Steps file       |
| Runner plugin                    | ❌ Internal runner                                                                              | ❌ Internal runner            | ✅ Jest/Mocha                            | ❌ Internal runner        | (UI)                |
| Strict typing (mypy/strict)      | ✅ ALL                                                                                          | ❌ (Python typing still rare) | ⚠️ TS support but POMs often `any`-typed | ⚠️ JSDoc rare             | ❌                  |
| ROP                              | ✅ Central                                                                                      | ❌ Exceptions                 | ❌ Exceptions                            | ❌ Exceptions             | ❌                  |
| AI-first                         | ✅ documented, technology designed for it from the start                                        | ❌                            | ⚠️ Playwright CodeGen                    | ⚠️ Third-party AI tooling | ❌                  |
| ISTQB vocabulary                 | ✅ strict                                                                                       | ⚠️ partial                    | ❌ Jest-like                             | ❌ describe/it            | ❌                  |
| Vendor lock-in                   | ❌ None                                                                                         | ❌ None                       | ⚠️ Microsoft                             | ⚠️ Cypress.io             | ⚠️ Selenium project |
| Auditability                     | ✅ 1 runtime dep                                                                                | ❌ Internal ecosystem         | ❌ Massive Node deps                     | ❌ Cypress runtime        | ⚠️                  |
| Async/await                      | ❌ Refused                                                                                      | ❌                            | ✅ Mandatory                             | ✅ Mandatory              | ❌                  |
| Parallelization                  | ✅ ThreadPool + Semaphore + simple parallelization strategy, customizable by the user, no magic | ⚠️ pabot                      | ✅ JS Workers                            | ✅ Parallel CI            | ❌                  |
| Native _anti-flakiness_ approach | ✅ Parallelization + Test cloning + Fine AI analysis                                            | ❌                            | ❌                                       | ❌                        | ❌                  |

## 7. Values Ocarina carries

Test code:

- **must be readable by functional testers** (ISTQB vocabulary)
- **must first and foremost be a cross-team communication tool** (same)
- **must be readable by AI** (strict typing + strict linter + well-defined grammar)
- **must remain maintainable** (very strong content/form separation)
- **must be driven by the test strategy without compromise** (huge _skill_ battery)
- **must be auditable and portable** (a single dep, MIT, copyable)
- **doesn't need a platform** to work
- **doesn't have to reinvent the wheel** (back to fundamentals)
