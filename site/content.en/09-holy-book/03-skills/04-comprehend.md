---
title: "09.03.04 — Comprehend skills"
description: "The Comprehend family of AI-facing skills: skills that help understand a project, its ecosystem and the SUT's limits before acting."
weight: 4
date: 2026-05-20
series: ["skills"]
series_order: 4
tags: ["holy-book"]
---

# 09.03.04&nbsp;—&nbsp;Comprehend skills

> Skills that help the AI **understand** a project or ecosystem before acting.

## Listing (potentially non-exhaustive)

| Skill                        | Target                                                      |
| ---------------------------- | ----------------------------------------------------------- |
| `assess-test-base`           | Catalogs the existing test base                             |
| `assess-ecosystem`           | Bounded public research, capped by a token budget           |
| `assess-impact`              | Forward impact analysis: a change's blast radius through the dependency graph |
| `understand-sut-constraints` | Understands the SUT's "boundaries" so as not to exceed them |
| `understand-ocarina`         | Routes by question class: Holy Book for reference, the from-ocarina-to-igor book for intent; then Ocarina source + the adapter-matched worked example |

## `understand-ocarina`

```
input  : user question — routed by class:
            - "how do I do a match_page?"        (reference: what a primitive is) → Holy Book
            - "why is the suite built on Railway?" (intent / cartography / why)    → the from-ocarina-to-igor book
output : Claude loads, by question class:
            - reference  → relevant Holy Book pages (https://mojo-molotov.github.io/ocarina-holy-book)
            - intent     → relevant chapters of the from-ocarina-to-igor book (https://mojo-molotov.github.io/from-ocarina-to-igor/)
            - behaviour  → Ocarina source clone, if the docs don't cover it
            - shape      → the worked example matching the project's driver adapter:
                              Selenium   → ocarina-example, ocarina-with-ai-example
                              Playwright → ocarina-with-playwright-example
         then answers with citations (tier + page/chapter URL or file:line)
```

`SKILL.md`:

> **Tier 1&nbsp;—&nbsp;Ocarina Holy Book (reference, public).** What a primitive _is_ — signature, contract, lifecycle. Reach via `WebFetch` for specific pages once the page-list is known.
>
> **Tier 1B&nbsp;—&nbsp;the from-ocarina-to-igor book (intent / cartography / philosophy, public).** Why Ocarina is shaped this way and how the ecosystem repos relate. The two doc sites are routed by question class, not a fixed order; a question with both halves consults both.
>
> **Tier 2&nbsp;—&nbsp;doc-site repos (cloned + built locally, per-site fallback).** If a site is down (DNS /&nbsp;not-yet-published /&nbsp;offline /&nbsp;404), clone + build that site locally. The fallback is per-site: a 404 on the Holy Book doesn't mean the book is down too.
>
> **Tier 3&nbsp;—&nbsp;Ocarina source clone.** For behaviour the docs don't cover.
>
> **Tier 4&nbsp;—&nbsp;worked-example clones, matched to the driver adapter.** Selenium: ocarina-example, ocarina-with-ai-example. Playwright: ocarina-with-playwright-example.

## `assess-test-base`

```
input  : current test repo
output : catalog:
            - exhaustive list of tests (cycle / campaign / suite / test)
            - per-feature coverage: test ↔ FRD requirement mapping
            - gap tests (intentionally failing), cross-browser tests, exploratory tests
            - data-driven tests
            - skipped tests
```

## `assess-ecosystem`

Skill that does web research **with a token cap**.

```
input  : topic to understand (e.g. "how is CURA deployed on Heroku?")
output : synthesized findings, sources cited
constraint: token budget — no infinite searching
```

## `assess-impact`

```
input  : a change (SUT change / planned refactor / a diagnose-* shared-component cause)
output : forward blast-radius analysis:
            - trace the change through the dependency graph
            - classify each affected node:
                broken / stale claim / gap-test-may-flip / coverage-gap / smoke-gate crossing
```

The **forward dual** of the `diagnose-*` pair: those walk the graph backward (symptom → cause), `assess-impact` walks it forward (change → blast radius).

## `understand-sut-constraints`

```
input  : SUT (URLs, source if available)
output : constraints that break parallel tests:
            - rate-limits (`X requests / minute / IP`)
            - shared sessions (`one session per user account`)
            - global state (`history accumulates across tests`)
            - sleeping dyno (Heroku eco)
            - third-party API quota
```

For CURA:

- Sleeping Heroku eco-dyno → warm-up needed.
- Per-user sessions → if you launch 3 workers with _the same_ login, that's OK, stubbed environment.
- History accumulation → a test that _asserts_ "_empty history_" could fail if another test just booked, but that's OK, stubbed environment.

The AI flags these constraints so the human can decide how to handle them (saturate, multi-user, isolated runs, etc.).

## Cross-cutting discipline

- **Capture** information.
- **Synthesize** into a readable report.
- **Don't modify** code directly.
