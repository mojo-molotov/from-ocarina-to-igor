---
title: "09.03.05 — Pick skills"
description: "The Pick family of AI-facing skills: artifact selection, screenshots, logs and reports, always by mtime and never by filename."
weight: 5
date: 2026-05-20
series: ["skills"]
series_order: 5
tags: ["holy-book"]
---

# 09.03.05&nbsp;—&nbsp;Pick skills

> Picking artifacts (screenshots, logs, reports). **Always by mtime, never by filename.**

## Listing (potentially non-exhaustive)

| Skill              | Target                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------- |
| `pick-screenshots` | Picks the most recent screenshots (by mtime), contextualizing them with logs where possible |
| `pick-logs`        | Picks the most recent logs (by mtime)                                                       |
| `pick-reports`     | Picks the most recent DOCX/JSON reports (by mtime)                                          |

## "_mtime_"

Holy Book quote:

> **Mtime, not filename.** UUID suffixes are random; `pick-*` sorts by mtime.

All Ocarina artifacts are named with a UUID:

- Screenshots: `SUCCESS_a3f2b1c4.png`, `FAIL_b9e8d2a3.png`
- Logs: `<test name>.log` but in a `<cycle>/<campaign>/<suite>/<test>.log` tree, often duplicated between runs with a root folder suffixed by a UUID for multiple runs on the same machine
- Reports: `<uuid hex 8>.json`, `<uuid hex 4>/<...>.docx`

## Schema

```
input  : "run review-report on the last run"
        → pick-reports (mtime DESC, limit 1)
        → review-report on the picked report
```

```
input  : "find screenshots of test X from the last run"
        → pick-reports → last run
        → pick-screenshots scoped
```

## Why dedicated skills rather than `ls -t`

| Without a skill                                                                     | With a skill                     |
| ----------------------------------------------------------------------------------- | -------------------------------- |
| Claude has to guess the directory convention (`.reports/docx/` vs `.reports/json/`) | The skill knows the convention   |
| Risk of picking an unrelated screenshot                                             | The skill scopes to the last run |
| No filtering by browser / by test / by category                                     | The skill exposes typed filters  |

## "_pick then act_"

```
Failing cycle  →  pick-reports  →  review-report(<picked report>)
                                            ↓
                                    classification → IDENTIFIED_GAPS.md
```

`pick-*` is rarely called alone. It's always a **prelude** to a skill that consumes the picked artifact.

## Random-naming illustration

When an Ocarina-driven test cycle finishes, artifacts are built like:

```
.reports/
├── docx/
│   └── <uuid 4 chars>/                                           # per run
│       └── <campaign>/
│           └── <suite>/
│               └── <test>.docx
└── json/
    └── <uuid 8 chars>.json                                       # per run
```
