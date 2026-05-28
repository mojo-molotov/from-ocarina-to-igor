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
| `understand-sut-constraints` | Understands the SUT's "boundaries" so as not to exceed them |
| `understand-ocarina`         | Walks the Holy Book + Ocarina's source code                 |

## `understand-ocarina`

```
input  : user question ("how do I do a match_page?")
output : Claude loads:
            - relevant Holy Book pages (from https://mojo-molotov.github.io/ocarina-holy-book)
            - Ocarina source if needed (gh api repos/mojo-molotov/ocarina/...)
            - examples from the two ocarina-example / ocarina-with-ai-example projects
         then answers with citations
```

`SKILL.md`:

> **Tier 1&nbsp;—&nbsp;Ocarina Holy Book (LLM-oriented, public).** The canonical LLM-facing documentation. Reach via `WebFetch` for specific pages once the page-list is known.
>
> **Tier 2&nbsp;—&nbsp;Holy Book repo (cloned + built locally, when Tier 1 unreachable).** If the website is down (DNS / not-yet-published / offline / 404), fallback on the repository source. Clone + build locally.
>
> **Tier 3+&nbsp;—&nbsp;Ocarina source code, ocarina-example, ocarina-with-ai-example.** For code-level questions.

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
