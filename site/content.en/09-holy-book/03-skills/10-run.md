---
title: "09.03.10 — Run skills"
description: "The Run family of AI-facing skills: surface the pre-run choices before a local dispatch, then hand the composed command back."
weight: 10
date: 2026-05-20
series: ["skills"]
series_order: 10
tags: ["holy-book"]
---

# 09.03.10&nbsp;—&nbsp;Run skills

> Surface the choices to make _before_ a local dispatch, compose the command, and hand it back. The skill never launches the run itself.

## Listing (potentially non-exhaustive)

| Skill                   | Target                                                                          |
| ----------------------- | ------------------------------------------------------------------------------- |
| `propose-visual-review` | Offer headed (`--not-headless`) vs headless (CI-shaped) before a run, then compose the command |

## `propose-visual-review`

```
input  : an upcoming local run
output : the headed vs headless choice:
            - --not-headless: watch the browser, useful when debugging a flaky flow
            - headless (CI-shaped): faster, matches what CI does
         + the trade-off and what to watch for during a headed run
         + the composed command, handed back for the user to launch
```

## Role

- **Surface** the pre-run choice; explain the trade-off.
- **Compose** the command.
- **Don't launch** it — the user runs it.
