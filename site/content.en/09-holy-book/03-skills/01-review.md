---
title: "09.03.01 — Review skills"
description: "The Review family of AI-facing skills: static reads that surface systematic review findings on an Ocarina project."
weight: 1
date: 2026-05-20
series: ["skills"]
series_order: 1
tags: ["holy-book", "watcher"]
---

# 09.03.01&nbsp;—&nbsp;Review skills

> **Static** reads, surface findings. A large family. Lets the AI _review_ its project systematically.

## Listing (potentially non-exhaustive)

| Skill                               | Target                                                                                                                 |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `review-spec-gaps`                  | Clarification questions on the FRDs                                                                                    |
| `review-watcher-misuse`             | Verifies the "_negative-only_" principle of `watcher.report(...)`                                                      |
| `review-compartmentalisation-leaks` | Detects URLs, selectors, magic numbers in wrong places                                                                 |
| `review-dead-code`                  | Detects unused connectors / POMs / scenarios / suites / fragments / constants                                          |
| `review-report`                     | Classifies each FAIL / SKIP of an execution                                                                            |
| `review-type-ignore`                | Audits `# type: ignore`s (are they justified?)                                                                         |
| `review-match-candidates`           | Spots places where a `match` (Python, _pattern matching_) could be used instead of `if` `elif` `elif` `if` `if` `elif` |
| `review-unverified-transitions`     | Verifies that every _page transition_ has a `verify`                                                                   |
| `review-submit-dispatchers`         | Audits input-confirmation methods (click vs enter key...)                                                              |
| `review-comment-drift`              | Detects comments that have drifted from the code                                                                       |
| `review-suite-stability`            | Evaluates a suite's stability (proportion of retries, transient_errors hits)                                           |
| `review-intent-collisions`          | Detects tests that overwrite each other (conflicting intents) and asks/proposes clarifications                         |
| `review-watcher-emissions`          | Audits watcher emissions (volume, dedup, relevance)                                                                    |
| `review-hierarchy-naming`           | Audits the test-hierarchy naming (`TestCycle` / `TestCampaign` / `TestSuite` / `Test`) for the lazy-naming antipattern where a child carries the parent's name |

## `review-dead-code`

```
input  : test base
output : list of unused elements (connectors / POMs / scenarios / fragments / constants)
         + per-element recommendation:
            - delete
            - move to incubator (<root-source>/incubator/, dependency tree preserved)
            - keep (justify)
```

## `review-report`

```
input  : a recent execution (logs + reports)
output : per-test classification:
            - PASS                  (nothing to do)
            - SKIP                  (why?)
            - intentional gap FAIL  (G-DATA-*, G-SEC-*, ...)
            - cross-browser FAIL    (B-BROWSER-*)
            - transient FAIL        (A-ENV-*)
            - regression            ⚠️ ALERT
```

## `review-watcher-misuse`

```
input  : all watcher.report(...) calls
output : list of reports that look positive ("success", "completed", "ok", ...)
         → recommendation: remove or rephrase as negative
```

## `review-comment-drift`

```
input  : every code comment
output : list of comments that no longer match the adjacent code
         (typical: comment mentions foo, code mentions bar)
```

Helps remove stale comments.  
"_Teach the pattern, not the symptom_."

## `review-compartmentalisation-leaks`

```
input  : all source code
output : detected leaks:
            - inline URLs in scenarios/connectors → suggests moving to constants/
            - selectors inside methods → suggests moving to top of POM
            - magic numbers in methods → suggests moving to constants
```

`CLAUDE.md` rules:

- URLs in `src/constants/urls.py`, never inline.
- Selectors at the top of POM code.
- Etc.

## Role

1. **Read** the code (and sometimes the last execution).
2. **Categorize** findings.
3. **Suggest** actions.
4. **Don't modify** the code directly.
5. **The human decides.**
