---
title: "09.03.02 — Analyse skills"
description: "The Analyse family of AI-facing skills: dynamic analyses that use execution logs and reports to diagnose flakiness."
weight: 2
date: 2026-05-20
series: ["skills"]
series_order: 2
tags: ["holy-book"]
---

# 09.03.02&nbsp;—&nbsp;Analyse skills

> **Dynamic** analyses: use the logs / reports of a recent execution to diagnose a failure. Two root-cause skills sit in front of the family&nbsp;—&nbsp;`diagnose-root-cause` for a deterministic red, `diagnose-flake-root-cause` for an intermittent one&nbsp;—&nbsp;and route to the controlled `analyse-*` experiments.

## Listing (potentially non-exhaustive)

| Skill                          | Target                                                             |
| ------------------------------ | ------------------------------------------------------------------ |
| `diagnose-root-cause`          | Structured RCA for a **deterministic** red: re-derive, the synthetic-to-real ladder, root cause sorted into five buckets |
| `diagnose-flake-root-cause`    | Structured RCA for an **intermittent** failure (a flake): failure rate, signature, correlation; orchestrates the `analyse-*` experiments |
| `analyse-flakiness`            | Widens the `transient_errors` net; chronic deaths are real flakes  |
| `analyse-fixture-flakiness`    | Instruments setup/teardown; surfaces cross-test contaminations     |
| `analyse-watcher-flakiness`    | Analyzes watcher reliability (volume, dedup, false positives)      |
| `analyse-screenshot-flakiness` | Groups screenshots by `(test, step, browser)`, detects differences |

## `diagnose-root-cause`

```
input  : a deterministic red (fails every run)
output : structured root-cause analysis:
            - re-derive the failure, don't inherit prior assumptions
            - climb the synthetic-to-real ladder (fake driver → real browser)
            - read the source, confirm with a probe
            - root cause sorted into five buckets
         hands off to diagnose-flake-root-cause if the failure proves intermittent
```

## `diagnose-flake-root-cause`

```
input  : an intermittent failure (a flake)
output : distribution-based root-cause analysis:
            - establish a failure rate (the distribution is the evidence)
            - pin the signature, correlate
            - route to the right analyse-* experiment, raise the rate to confirm
            - classify into five flake buckets
         the orchestrator of the analyse-* family
```

## `analyse-flakiness`

```
input  : logs of the last N runs
output : list of tests that retry often (by % of retries)
         + recommendation:
            - add an exception to the transient_errors tuple
            - investigate a particular test (the issue might come from the test itself)
```

## `analyse-fixture-flakiness`

```
input  : tests with setup/teardown
output : tests whose setup fails often
         + recommendation:
            - verify setup idempotency
            - check teardown is clean (otherwise cross-test contamination)
            - move the seed out of setup into a manual init if too fragile
```

## `analyse-watcher-flakiness`

```
input  : watcher.report(...) logs over N runs
output : watchers with abnormal reporting:
            - too many emissions (dedup issue)
            - no emissions (the watcher is useless)
            - false positives (expected element reported as intruder)
```

## `analyse-screenshot-flakiness`

```
input  : screenshots from N runs, grouped by (test, step, browser)
output : visual flakiness:
            - tests whose screenshots vary abnormally between runs
            - tests that pass but whose look changes
            - identify whether the variation is semantic (real diff) or cosmetic
```

Uses heuristics (hash, dimensions, dominant palette). Not a real image diff.

## Role

- **Consume** an execution (runtime).
- **Detect** patterns over time (N runs).
- **Propose** actions (widen `transient_errors`, _refactor_ a watcher, etc.).

Reminder from the Holy Book:

> **Failing cycle:** `review-report` → `analyse-*` → `write-a-probe` → findings propagated to `IDENTIFIED_GAPS.md` / the FRDs / a scenario comment → probe deleted.
