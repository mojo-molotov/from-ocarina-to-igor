---
title: "09.03.08 — State skill"
description: "A single skill: question-state. Interrogates the environment before believing a result."
weight: 8
date: 2026-05-20
series: ["skills"]
series_order: 8
tags: ["holy-book"]
---

# 09.03.08&nbsp;—&nbsp;State skill

> A single skill: `question-state`. Interrogates the environment before believing a result.

## The skill

```
input  : a surprising result ("the test fails")
output : a series of questions about state:
            - which browser are we running on?
            - which commit?
            - is the SUT warm or cold?
            - is Redis available?
            - what's the configured wait-timeout?
            - what's the driver version?
            - does ChromeDriver have its password-manager-off fix?
            - is this an isolated run or a parallel run?
            - are other tests touching the same SUT resources?
```

## Approach

`CLAUDE.md`:

> **Don't propagate a previous run's diagnosis without re-deriving it.**
>
> Logs, screenshots, and prior comments describe a _past_ failure. For a _current_ failure, treat them as hypotheses to test, not conclusions to inherit. Re-derive the cause from this run's evidence (current screenshot, current network response, current PHP) before reaching for the previously-tried fix. One extra check is cheap; stacking workarounds on a wrong diagnosis is what ends in a reboot.

`question-state` is the **ritual** that forces this re-derivation. It can also be supplemented by environment knowledge:

- Are there stubs?
- What isn't _ISO Prod_?
- ...

## Example

```
USER : "the login test fails, is it Chrome BFCache?"
   ↓
CLAUDE (question-state):
   - Which browser?  → Chrome
   - Which failing test? → "valid_login" (smoke gate)
   - BFCache concerns post_logout_*, not valid_login → hypothesis rejected
   - Which commit?  → main branch latest
   - Is ChromeDriver password-manager-off active? → check create_drivers_pool
   - Is the SUT (CURA) "warm"?
   - Did the test retry? → check logs
   - How many tries? → if > 5, transient; if 1, real defect
   ↓
REVISED HYPOTHESIS: maybe A-ENV-2 if the custom adapter was removed
```

## "_State, not legend_"

Don't trust a failure because "_we've seen it fail like that before_." Re-acquire the current state.

`CLAUDE.md` details why this is crucial:

- Workarounds based on _assumptions_ pile up silently.
- Each bad diagnosis adds technical debt.
- Eventually: a stack of patches that fixes _nothing_.

## Cross-cutting discipline

This skill is often invoked _at the start_ of a debug session:

```
USER : "run review-report"
   ↓
CLAUDE : (review-report identifies the failing test)
   ↓
CLAUDE : "Before proposing a fix, I'm running question-state..."
   ↓
CLAUDE : (question-state reveals an overlooked detail, e.g. the Heroku warm-up that didn't run)
   ↓
CLAUDE : "The fail is probably A-ENV-1 (cold dyno). Want to re-run with warm-up?"
```
