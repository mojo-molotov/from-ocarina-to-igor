---
title: "02.03.06 — drive_page"
description: "Source file: src/ocarina/opinionated/dsl/drive_page.py"
weight: 6
date: 2026-05-20
series: ["railway"]
series_order: 6
tags: ["ocarina", "rop", "scenarios"]
---

# 02.03.06&nbsp;—&nbsp;`drive_page`

> Source file: [`src/ocarina/opinionated/dsl/drive_page.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/dsl/drive_page.py)

## Code

```python
def drive_page(
    first: ActionSuccess[TPOM], *rest: ActionSuccess[TPOM]
) -> ChainRunner[TPOM]:
    return chain_actions(first, *rest)
```

**Literally** `chain_actions`.

## Why this alias?

### 1. Semantics: "I'm taking control of a page"

Holy Book quote ("First scenarios"):

> `drive_page` expresses the fact that you are taking control of _one_ page.
> Any _transition_ becomes explicit through the opening of a new `drive_page`.

```python
return [
    drive_page(
        act(on_homepage, open_homepage)...,
        act(on_homepage, verify_homepage)...,
        act(on_homepage, click_cta)...,
    ),                                          # ⬅ closing control of the homepage
    drive_page(                                 # ⬅ opening control of the next page
        act(on_target_page, verify_target_page)...,
    ),
]
```

### 2. Discipline

Mixing acts from two different POMs inside one `drive_page` is a _mypy_ error (see [`02-action-chain-states.md`](02-action-chain-states.md), "narrowing via `act()`" section). The semantics get enforced concretely.

### 3. Report readability

`ocarina-with-ai-example`'s `CLAUDE.md` documents the rule that depends on this semantic:

> **Every `drive_page` produces at least one `log_and_screenshot`.** A `drive_page` models one page's worth of work and almost always ends by submitting / navigating / verifying&nbsp;—&nbsp;it _is_ a page transition. The report's screenshot sequence must let a reader replay the journey `drive_page` by `drive_page`; "one screenshot per scenario" collapses a multi-page journey into a single still.

Net effect: **one `drive_page` = one ending screenshot** (minimum). The DOCX report (see [`../11-opinionated/05-plugins-reports.md`](../11-opinionated/05-plugins-reports.md)) turns into a comic strip of the journey.

## Architectural consequences

| Consequence                                                    | Detail                                                                                                                                                                                                   |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A `drive_page` is typed on _one_ POM** (`ChainRunner[TPOM]`) | The checker refuses test steps from heterogeneous pages                                                                                                                                                  |
| **Multi-page = list of `drive_page`**                          | The scenario returns `list[drive_page(...), drive_page(...), drive_page(...)]`                                                                                                                           |
| **Composability**                                              | `drive_page(...)` is a `ChainRunner`; you can store it in a variable, pass it as an argument, place it in a `match_page` branch                                                                          |
| **No custom logic**                                            | `drive_page` is a **monomorphism** of `chain_actions` (same function, narrower type). You can write your own `drive_component` or `drive_modal` that also returns a `ChainRunner` and composes alongside |

## The alias is in `opinionated/`, not in `dsl/`

`drive_page` lives in `src/ocarina/opinionated/dsl/`, not `src/ocarina/dsl/`.

- The "pure" DSL holds only `chain_actions` (plus `create_act`, `match_page`).
- `drive_page` is an opt-in _semantic alias_, a **monomorphism** of `chain_actions`&nbsp;—&nbsp;no extra logic, just intent.
- A project could pull **only** `chain_actions` and roll its own alias (`drive_workflow`, `drive_section`, `drive_component`, etc.) without touching the framework.

That fits the Holy Book's "sovereign grammar" philosophy. See [`../../11-independence/01-sovereign-grammar.md`](../../11-independence/01-sovereign-grammar.md)

## Dedicated tests

Several tests in [`tests/scenarios/`](https://github.com/mojo-molotov/ocarina/tree/main/tests/scenarios) exercise `drive_page` (via the conftest's `acting(pom, step)` and `scenario_of("ok")`). They cover:

- sequential execution of the acts,
- short-circuit after failure,
- thread-local `act` counting.
