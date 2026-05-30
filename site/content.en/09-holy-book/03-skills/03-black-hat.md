---
title: "09.03.03 — Black-hat skills"
description: "The Black-hat family of AI-facing skills: business-logic-vulnerability ideation with no execution, where security testing stays functional and static."
weight: 3
date: 2026-05-20
series: ["skills"]
series_order: 3
tags: ["holy-book"]
---

# 09.03.03&nbsp;—&nbsp;Black-hat skills (6)

> **Ideations** of business logic vulnerabilities&nbsp;—&nbsp;no execution: "_security testing is functional and static, never active_".

## Listing (potentially non-exhaustive)

| Skill                              | Target                                                                                                         |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `business-logic-vulnerability-ideation`         | Break the product through legitimate-looking but malicious usage paths                                         |
| `incoherence-attack-ideation`      | Each step taken alone looks innocent; but combinations of these steps can cause an inconsistency in the system |
| `persistence-attack-ideation`      | Repeated attempts at a blocked action                                                                          |
| `permission-appropriateness-audit` | Is the access model itself appropriate?                                                                        |
| `bfcache-exposure-ideation`        | BFCache attacks                                                                                                |
| `lateral-resource-ideation`        | IDOR via the address bar only                                                                                  |

## Perimeter

All these skills _imagine_ attacks **the AI** could phrase.

The human:

- Evaluates relevance ("_is this gap plausible?_").
- Decides whether to turn it into a test (functional, via the UI).
- Writes the test (with help from other skills, e.g. `extend-coverage`).

The AI **never launches** an active attack. Forbidden.

## `business-logic-vulnerability-ideation`

```
input  : the FRDs + the SUT source code (if open source)
output : list of legitimate-looking but malicious usages
         examples (CURA and similar apps):
            - past-date booking (G-DATA-1)
            - duplicate booking (G-DATA-2)
            - overlapping appointments (G-DATA-2)
            - book at non-business hours
            - book a date "100 years in the future"
            - book with empty visit_date if HTML5 required is bypassed
```

The AI brainstorms. The human sorts. For each retained idea, write a gap test (assertive fail if the system should reject the behavior).

## `incoherence-attack-ideation`

```
example: geographically impossible same-day booking
         - book Hongkong CURA @ 10:00 (allowed on its own)
         - book Tokyo CURA @ 12:00 (allowed on its own)
         - combination: impossible (the patient can't teleport)
```

## `persistence-attack-ideation`

```
example: a user blocked by rate-limit / missing permission
         → tries 100 times in a row
         → checks whether the system releases after N attempts or whether the block holds
```

On CURA: no rate-limit (G-SEC-3), so nothing to test. On other SUTs, this can reveal blocking-logic bugs.

## `permission-appropriateness-audit`

```
input  : the FRDs + observation of the access model
output : audit the model:
            - does role X have access to resource Y without reason?
            - does endpoint Z require auth but shouldn't?
            - does endpoint W not require auth but should?
```

Often reveals gaps in the FRDs ("_we hadn't thought of that case_").

## `bfcache-exposure-ideation`

```
input  : auth-protected pages of the SUT
output : for each page, a back-then-reload recipe:
            - login → navigate to the page → logout → back() → expect redirect
            - if no redirect: refresh() → expect redirect (= BFCache hit)
            - otherwise: real server-side gap
```

## `lateral-resource-ideation`

```
input  : resource URLs with an ID (`/order/123`, `/user/456`, …)
output : for each resource, propose:
            - login as user A
            - try to access `/order/<user_B_id>`
            - verify the system refuses
```

This is **IDOR** (_Insecure Direct Object Reference_), but via the **address bar only**&nbsp;—&nbsp;no payload, no MITM proxy. Just a human typing a URL.

## Cross-cutting discipline

Every black-hat skill **imagines**, never **executes**.

If an idea deserves testing:

1. The human validates the idea.
2. Translates it into a functional gap test (via `extend-coverage`).
3. The test goes through the UI / normal behaviors covered by the functional test.
4. The test PASSES or FAILS (intentional).
5. Everything is documented in `IDENTIFIED_GAPS.md`.

No payload, no cross-origin POST, no scripted fuzzing. See [`../../08-ai-example/05-security-gaps.md`](../../08-ai-example/05-security-gaps.md) section "_Security testing is functional and static&nbsp;—&nbsp;never active_".
