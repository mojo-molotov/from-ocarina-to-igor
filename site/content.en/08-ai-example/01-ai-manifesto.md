---
title: "08.01 — Code: 99% Claude, 1% Igor, intelligence: 50-50"
description: "The README of ocarina-with-ai-example and its candid statement: 99% of the code written by Claude Code, intelligence shared fifty-fifty."
weight: 1
date: 2026-05-20
series: ["ai-example"]
series_order: 1
tags: ["watcher"]
---

# 08.01&nbsp;—&nbsp;Code: 99% Claude, 1% Igor, intelligence: 50-50

## README

> ## A note to the reader
>
> This project is an experiment in AI-driven test engineering. In the interest of honesty about how it was built:
>
> |                  | Claude Code | Human |
> | ---------------- | ----------- | ----- |
> | **Code written** | 99%         | 1%    |
> | **Intelligence** | 50%         | 50%   |
>
> Almost every line was machine-written. The judgement behind it&nbsp;—&nbsp;what to test, what to distrust, when to dig and when to stop&nbsp;—&nbsp;was shared.

## `CLAUDE.md`

`CLAUDE.md` is a working contract with Claude. It defines:

1. Where files live (`src/` layout).
2. Code conventions (`TYPE_CHECKING` guard, log factories, etc.).
3. Hard-won rules ("_No tricks or hacks_", "_Teach the pattern, not the symptom_", etc.).
4. Approved patterns (data-driven, scenario fragments, dispatch tables).
5. Forbidden patterns (JS-click to bypass, `time.sleep` to mask a race condition, etc.).

Claude reads this at the start of each session to frame the work.

## `CLAUDE.slim.md`

Same rules as `CLAUDE.md`, stripped of examples and justifications.

Holy Book (chapter "Using Ocarina with AI"):

> Slim when context is heavy; full for onboarding and reviews. Full wins on disagreement.

Context-window management: when Claude is already loaded with code and FRDs, use `slim.md` to save tokens.

## Holy Book reminder

### The three ancestral stones

```
1. CLAUDE.md at the project root.
2. skills/ with one <name>/SKILL.md per procedure.
3. Verification rule: every SUT claim comes from observation
   (probe, gh api, curl -v), never inference.
```

The three pillars of Ocarina's human ↔ AI collaboration.

## `CLAUDE.local.md`

```markdown
# Local machine config

## chromedriver

Path: `/path/to/chromedriver`

## Ocarina source repos (git clones)

- **ocarina**: `/path/to/ocarina`
- **ocarina-example**: `/path/to/ocarina-example`
```

gitignored.

Claude reads paths from `CLAUDE.local.md` rather than hardcoding or searching. If the file is missing, Claude creates it by asking the user for the relevant paths.

## Empiricism

_Ritual_ phrase quoted in the Holy Book:

> "_Fair point, I'm assuming. Let me verify empirically._"

Before writing a test based on _what we think_ the SUT does, we **verify** via:

1. A probe (`write-a-probe` skill).
2. `gh api` to read the source.
3. `curl -v` to observe the HTTP response.

That's what sets this project apart from classic e2e suites: **we don't assume.** We verify, then encode.

## Surface, don't apply

Holy Book:

> **Surface, don't apply.** Skills produce; the user decides.

Claude **can**:

1. Analyze the last run's report (skill `review-report`).
2. Suggest a categorization of failures (intentional gap / cross-browser / real regression).
3. Propose an update to `IDENTIFIED_GAPS.md`.

But Claude **doesn't decide**:

1. Which category is correct → the human validates.
2. Whether a gap should be added → the human confirms.
3. Whether the spec should be modified → the human approves (the `update-frd-and-tests` skill produces a diff, the human merges).

## "_Gap tests are reframed, not flipped_"

Quote:

> **Gap tests are reframed, not turned green.** Invert the assertion, rename, move the strategy-doc row, log the resolution in `IDENTIFIED_GAPS.md`. One motion via `update-frd-and-tests`.

If a gap test was red (CURA doesn't validate the date) and CURA later gets patched:

- ❌ Don't: delete the test, flip it green, remove the assertion.
- ✅ Do: **keep the test**, **invert the assertion** ("we expect validation to work"), rename it ("Date validation works" instead of "Date validation gap"), update `IDENTIFIED_GAPS.md` with the fix date.

The history of gaps is **preserved**. No amnesia.

## "_Watcher emissions are negative signals only_"

Quote:

> **Watcher emissions are negative signals only.** A watcher emitting "_login succeeded_" breaks the contract.

Explained here: [`../02-ocarina/07-watcher.md`](../02-ocarina/07-watcher.md)  
Exists explicitly as a discipline rule for Claude.

## "_Distributed when scarcity is shared_"

> **Distributed when scarcity is shared.** If workers contend on a SUT-capped resource (sessions, slots, quotas), coordinate through distributed primitives. Otherwise a worker-local in-memory cache is fine&nbsp;—&nbsp;provided keys can't collide and generation is thread-safe.

That's what `ocarina-example` embodies (see [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md)): `dogpile.cache.memory` _or_ Redis depending on scope.

## "_Mtime, not filename_"

> **Mtime, not filename.** UUID suffixes are random; `pick-*` sorts by mtime.

To pick the latest report/log/screenshot, don't sort by name (UUIDs are random). Sort by mtime.

All `pick-screenshots`, `pick-logs`, `pick-reports` skills follow this convention.

## Discipline

The goal: prevent Claude from hallucinating. The rules above are **cognitive counterweights** for the machine.

Without them, the AI would be tempted to:

1. Invent a test instead of verifying the SUT.
2. Mask a regression by flipping a test green.
3. Emit a positive watcher signal ("login succeeded") to seem helpful.
4. Use a local cache for a distributed quota.
5. Burn enormous numbers of tokens slogging through screenshots, logs, and reports.

`CLAUDE.md` is an immune system.
