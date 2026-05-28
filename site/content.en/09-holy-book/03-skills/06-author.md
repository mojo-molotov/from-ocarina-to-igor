---
title: "09.03.06 — Author skills"
description: "The Author family of AI-facing skills: skills that produce a deliverable, tests, probes, test strategy or coverage extension."
weight: 6
date: 2026-05-20
series: ["skills"]
series_order: 6
tags: ["holy-book"]
---

# 09.03.06&nbsp;—&nbsp;Author skills

> Skills that **produce a deliverable**. Tests, probes, docs, reports.

## Listing (potentially non-exhaustive)

| Skill                       | Target                                                                |
| --------------------------- | --------------------------------------------------------------------- |
| `empiricism`                | Verify before encoding; don't crush an intentionally failing gap test |
| `write-a-probe`             | Throwaway "probe" script, gitignored                                  |
| `write-test-strategy`       | Generates the test strategy document from the suite                   |
| `extend-coverage`           | Extends coverage from existing heritage                               |
| `update-frd-and-tests`      | Propagates a spec update                                              |
| `manual-reproduction-guide` | Writes a step-by-step reproduction scenario executable by a human     |
| `manage-backlog`            | `BACKLOG.md`                                                          |
| `pr-report`                 | PR report adapted to context                                          |

## `empiricism`

```
input  : user intent ("write a test that asserts X")
output : before encoding X:
            1. empirically verify that X is true
                - probe
                - gh api on the source code
                - curl -v to inspect HTTP responses
                - ...
            2. if X confirmed → encode
            3. if X false → correct intent
            4. if X ambiguous → ask the human
```

> "_Fair point, I'm assuming. Let me verify empirically._"

## `write-a-probe`

```
input  : question to investigate ("does the confirmation arrive in < 5s?")
output : throwaway Python script that:
            - lives in a gitignored directory (typically: `probes/`)
            - bypasses the Ocarina workflow (no Test, no Suite)
            - drives the browser or makes HTTP calls directly
            - prints state (URL, DOM, cookies, timings) to stdout
            - is never committed
         after use: finding goes to IDENTIFIED_GAPS.md / FRD / comment
         then the probe is deleted
```

`CLAUDE.md`:

> A **probe** is a one-off script that drives the browser (or raw HTTP) through a suspect flow and prints concrete runtime state. It **bypasses the Ocarina workflow entirely**&nbsp;—&nbsp;no `create_selenium_test`, no suites, no campaigns, no assertions. Probes live in a gitignored directory, are **never committed or pushed**, and are deleted once the answer lands in a durable artifact.

And:

> Reach for one when the framework's error surface doesn't show enough&nbsp;—&nbsp;a bare `TimeoutException` or `AssertionError` you can't act on. The trigger is the visibility gap, not where you are in the test lifecycle.

## `write-test-strategy`

```
input  : test heritage, test base
output : a test-strategy .md containing:
            - scope
            - test types
            - coverage tables (REQ-X-N × test_X)
            - suite/campaign tree
            - expected pass/fail breakdown
            - gaps
            - CI matrix
```

Output: `CURA_TEST_STRATEGY.md`

## `extend-coverage`

```
input  : a gap / an attack idea found by a black-hat skill
output : a new test that exercises this gap:
            - via the normal UI (no payload)
            - asserts rejection if expected (gap test)
            - asserts current behavior if exploratory
            - hooks into an FRD update
```

## `update-frd-and-tests`

```
input  : spec change ("CURA fixed G-DATA-1")
output : atomic diff:
            - FRD §9.7: adds revision ("2026-XX-XX: fixed")
            - IDENTIFIED_GAPS.md: adds revision
            - test: invert assertion (FAIL → PASS), rename, move if needed
            - analyze every inline comment referencing the old gap
```

The _only_ skill that modifies the spec it's given as reference.

> **Don't rewrite the spec; only `update-frd-and-tests` does, with a revision line.**

## `manual-reproduction-guide`

```
input  : a failing test
output : a step-by-step guide for a human to reproduce the failure manually
```

```
1. Open https://katalon-demo-cura.herokuapp.com/profile.php#login
2. Type "John Doe" in username field
3. Type "ThisIsNotAPassword" in password field
4. Click Login
5. Navigate to /appointment.php
6. ...
7. Observe: confirmation page rendered with past date (expected: rejection)
```

## `manage-backlog`

```
input  : work sessions / discussions
output : maintains BACKLOG.md:
            - findings to investigate later
            - suggested improvements
            - tests to write
            - open questions on the SUT
         prioritization
```

## `pr-report`

```
input  : an update to push as a PR
output : a PR report adapted to the change type:
            - feature PR: tests added, coverage diff
            - bugfix PR: regression test, link to the gap
            - refactor PR: checks behavior hasn't changed
            - doc PR: no tests
            - mixed PR: multiple sections
```

Produces a coherent report in `gh pr create --body ...` format.

## Cross-cutting discipline

All Author skills **produce** something _persistent_, _deliverables_: test, doc, file.
