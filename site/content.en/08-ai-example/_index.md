---
title: "Chapter 08 — ocarina-with-ai-example"
description: "ocarina-with-ai-example, the CURA Healthcare e2e suite co-written by Claude Code: living proof of the AI is the bridge philosophy."
weight: 9
date: 2026-05-20
tags: ["ai-example"]
sidebar:
  open: true
---

# Chapter 08&nbsp;—&nbsp;`ocarina-with-ai-example`

> CURA Healthcare e2e suite **co-written by Claude Code**. The living _proof of concept_ of the "_AI is the bridge_" philosophy.

## Outline

|  #  | File                                                     | Topic                                                                                                                  |
| :-: | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-ai-manifesto.md`](01-ai-manifesto.md)               | The README and its "_Code: 99% Claude / Intelligence: 50-50_" headline.                                                |
| 02  | [`02-sut-cura.md`](02-sut-cura.md)                       | CURA Healthcare: external SUT, open-source PHP, Heroku eco-dyno.                                                       |
| 03  | [`03-canonical-documents.md`](03-canonical-documents.md) | The 4 documents: `CLAUDE.md`, `CURA_FRD.md`, `CURA_TEST_STRATEGY.md`, `IDENTIFIED_GAPS.md`.                            |
| 04  | [`04-test-strategy.md`](04-test-strategy.md)             | Test types (happy / unhappy / edge / business logic vulnerability / exploratory / regression).                                      |
| 05  | [`05-security-gaps.md`](05-security-gaps.md)             | Security gaps: CSRF, session, rate-limit (G-SEC-1 to G-SEC-3).                                                         |
| 06  | [`06-data-gaps.md`](06-data-gaps.md)                     | Data gaps: visit_date with no validation, duplicates (G-DATA-1 to G-DATA-2).                                           |
| 07  | [`07-spec-gaps.md`](07-spec-gaps.md)                     | Spec gaps: history order, profile placeholder, redirects (G-SPEC-1 to G-SPEC-3).                                       |
| 08  | [`08-bfcache.md`](08-bfcache.md)                         | Chrome BFCache: B-BROWSER-1 (and A-ENV-1, A-ENV-2).                                                                    |
| 09  | [`09-ci-matrix.md`](09-ci-matrix.md)                     | CI: `ai_proof_ci.yml` + `ai_proof_e2e.yml` Firefox/Chrome matrix + Heroku warm-up + ChromeDriver stacktrace filtering. |

## Success story

|              | Claude Code | Human |
| ------------ | ----------- | ----- |
| Code written | 99%         | 1%    |
| Intelligence | 50%         | 50%   |

> Almost every line was machine-written. The judgement behind it&nbsp;—&nbsp;what to test, what to distrust, when to dig and when to stop&nbsp;—&nbsp;was shared.

It's the embodiment of [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md):

> With AI, and tools like _Claude Code_, this bet gets sturdier by the day. The bridge between technical and non-technical is no longer a layer of abstraction.
>
> It's AI itself. AI working on raw data.

## Holy Book reminder

Four things _this project is not_, per the Holy Book (chapter "Using Ocarina with AI"):

> - Doesn't generate tests autonomously.
> - Doesn't patch hallucinations in CI; a failure triggers `review-report` + `analyse-*`.
> - Doesn't rewrite the spec; only `update-frd-and-tests` does, with a revision line.
> - Doesn't run active security tests. Ever.

The human keeps control. The AI produces the machinery.

## Singularity

1. **Reading the PHP source to find real defects**: missing CSRF, client-only validation, history ordered by submission, etc.
2. **Business logic vulnerability tests**: past-date booking, duplicate appointments, geographically impossible slots.
3. **Cross-browser divergence as a finding**: Chrome BFCache restoring a `no-store` page after logout.

Each gap is documented with `file:line` and PHP evidence, and materialized as an intentionally red test that stays red until CURA is fixed.

## Related reading

- The philosophical bet → [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md)
- The role of AI _skills_ documented on the Holy Book → [`../09-holy-book/`](../09-holy-book/)
- The framework it uses → [`../02-ocarina/`](../02-ocarina/)
