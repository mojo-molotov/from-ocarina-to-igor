---
title: "11.02 — Auditability in an afternoon"
description: "Operational commitment: a human must be able to read the whole framework and understand it in a few hours. No hidden magic."
weight: 2
date: 2026-05-20
series: ["independence"]
series_order: 2
---

# 11.02&nbsp;—&nbsp;Auditability "_in an afternoon_"

> Operational commitment: a human must be able to _read_ the whole framework and understand it in a few hours. No hidden magic.

## Commitment

Holy Book quote (chapter "_What is Ocarina?_"):

> For teams constrained by _security policies_: the code is small, auditable in an afternoon. Nothing hidden. The only external dependencies live in the post-execution plugins and if one of them doesn't fit, it can be removed without breaking anything else.

## As few dependencies as possible

```toml
dependencies = ["python-docx>=1.2.0"]
```

`python-docx` is used _exclusively_ by `generate_docx_proof` (post-execution plugin).  
The rest of the framework imports it nowhere.

| Audit                                            | Verdict                                                                                    |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| Which libs are vendor-shipped with Ocarina?      | `python-docx` (+ Python stdlib)                                                            |
| If the auditor doesn't trust `python-docx`?      | Disable the DOCX plugin → everything else runs                                             |
| Are there hidden deps in `requirements-dev.txt`? | Yes (Selenium, allure, mypy, ruff, …) **but they're not embedded in the release binaries** |
| How many SBOM entries for `pip install ocarina`? | ~2 (`ocarina` + `python-docx`)                                                             |

## Nothing hidden

The auditor can **verify everything**:

1. **The source**: public on GitHub MIT.
2. **The build**: standard `hatchling` build, reproducible.
3. **The tests**: cram + pytest + mypy plugins + syrupy + hypothesis.
4. **The Allure report**: published on GitHub Pages, viewable by anyone.
5. **The CIs**: `main_ci.yml`.

No:

- Proprietary build step.
- Third-party artifact download on install.
- Obfuscated code.
- Hidden telemetry.
- External API call to authorize use.

## Code is Law

See [`../01-philosophy/04-citations-and-influences.md`](../01-philosophy/04-citations-and-influences.md)

> Code _substitutes for_ the Law. Lessig, 1999, a wake-up cry. Then picked up by Ethereum, 2015, conversely as political ideal.

For "_code to be the law_", it must be readable. Otherwise it's just "_the law is what we don't understand, but which executes_".

Ocarina is explicitly _auditable_, hence _legislative_ in the noble sense.

## Portability

Holy Book quote:

> In the most extreme cases: Ocarina doesn't need to be installed.  
> Copy it, adapt it, run it.  
> No dependency to audit.

You can literally **copy** the `src/ocarina/` folder into your project and use it as a sub-package. No install.

Use case: an _ultra-paranoid_ client refusing any pip install. Copy. Adapt. It runs.

## `dsl/` / `infra/` / `opinionated/` separation

See [`../02-ocarina/02-module-tree.md`](../02-ocarina/02-module-tree.md)

| Layer                       | Audit first                                         |
| --------------------------- | --------------------------------------------------- |
| `railway/`                  | 30 minutes: understand ROP                          |
| `custom_types/`             | 30 minutes: types and aliases                       |
| `dsl/testing_with_railway/` | 1h: the DSL state machine                           |
| `dsl/invariants/`           | 1h: invariants chain                                |
| `dsl/testing/`              | 1h: orchestration (Test → Suite → Campaign → Cycle) |
| `infra/`                    | 30 minutes: pool, builder, screenshotter            |
| `opinionated/`              | 30 minutes: CLI, loggers, plugins, bootstrap        |

Total: **~5 hours** for a full audit. A quiet afternoon.

## Post-execution plugins only

> The only external dependencies live in the post-execution plugins and if one of them doesn't fit, it can be removed without breaking anything else.

See [`../02-ocarina/11-opinionated/05-plugins-reports.md`](../02-ocarina/11-opinionated/05-plugins-reports.md) and [`../02-ocarina/11-opinionated/06-bootstrap-launcher.md`](../02-ocarina/11-opinionated/06-bootstrap-launcher.md)

`run_plugins(*plugins, exceptions_logger)`:

```python
def _run_plugin(plugin: Effect, exceptions_logger: ILogger) -> None:
    try:
        plugin()
    except Exception as exc:
        exceptions_logger.exception("The plugin failed.", exc=exc)
```

If `python-docx` is broken / un-installable: the DOCX plugin raises, we log, **the rest continues**.

The run still produces:

1. The `pretty_print_results` report.
2. The JSON report (`results_to_json`).
3. The `sys.exit(1)` on fail.

Only the DOCX will be missing. You can remove the DOCX plugin call from your `main.py` entirely if you prefer.

## Anti No-Code

See the Holy Book (chapter "_First feedbacks_", "_Anti No-Code_" section):

> Code is raw data. Auditable. Inspectable. **A white box.**  
> Exactly what AI has known how to work with since its very beginnings.

"_White box_": we see everything. No proprietary black box.

The opposition to No-Code isn't ideological posturing&nbsp;—&nbsp;it's a demand for **auditability**. A No-Code workflow is, by definition, non-auditable.

## Anti dev-bros

Holy Book:

> Unlike _researchers_, engineers and their business-school friends rely on _mental models_. The most "prestigious" schools have taught them one thing: passing big-talk off as "engineering", whereas those who know call this work _programming astrology_.

Ocarina rejects the big-talk. The code is what it is, verifiable. No esoteric "_patterns_" justifying pointless complexity.

## Consequence for teams _stuck behind security policies_

The auditability pitch is explicitly aimed at them:

> For teams constrained by _security policies_: the code is small, auditable in an afternoon.

A team that can't `pip install <random>` can:

1. Audit Ocarina (one afternoon).
2. Audit project adapters (a few more hours).
3. Ask the security team to whitelist it.
4. Run without fear.

No Ocarina consultant, no SaaS, no enterprise license. **Free.**
