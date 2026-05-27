---
title: "01.02 — ISTQB vs pytest / Jest / Mocha"
weight: 2
date: 2026-05-20
series: ["philosophy"]
series_order: 2
tags: ["istqb"]
---

# 01.02&nbsp;—&nbsp;ISTQB vs pytest / Jest / Mocha

## The methodological observation

Past the technical bet on the technical / non-technical barrier (see [`01-flip-the-problem.md`](01-flip-the-problem.md)), there's a **second bet**: the one on trade vocabulary.

> The ISTQB and professional testers have spent decades building a precise, battle-tested vocabulary: _test cycles_, _campaigns_, _test suites_, _test cases_, _test steps_. A clear hierarchy, built to **organize, trace and drive** software quality.
>
> Automation tools have **largely ignored that legacy**.
>
> _pytest_, _Jest_, _Mocha_… they're all **hybrid mixes** where testers have to learn to think like developers, and nobody really speaks the same language.

## The architectural consequence

Ocarina takes that vocabulary **seriously** and ports it straight into the class hierarchy.

| ISTQB vocabulary | Ocarina class                                    | Source file                                                       |
| ---------------- | ------------------------------------------------ | ----------------------------------------------------------------- |
| Test step        | `act()` (user verb, returns `ActionStart[TPOM]`) | `src/ocarina/dsl/testing_with_railway/constructors/create_act.py` |
| Test case        | `Test[Driver]`                                   | `src/ocarina/dsl/testing/oc_test.py`                              |
| Test suite       | `TestSuite[Driver]`                              | `src/ocarina/dsl/testing/oc_test_suite.py`                        |
| Campaign         | `TestCampaign[Driver]`                           | `src/ocarina/dsl/testing/oc_test_campaign.py`                     |
| Cycle            | `TestCycle[Driver]`                              | `src/ocarina/dsl/testing/oc_test_cycle.py`                        |

Not "decorative namespaces". Every level has a **distinct job** (see [`../02-ocarina/05-orchestration/`](../02-ocarina/05-orchestration/README.md)):

| Level          | Job                                                                                 |
| -------------- | ----------------------------------------------------------------------------------- |
| `act`          | One atomic action on a page.                                                        |
| `Test`         | Metadata (`name`, `test_id`, `skipped`) + scenario + pre/post fragments + watchers. |
| `TestSuite`    | Driver pool, parallelization, _saturation_, ID filtering, retry policy.             |
| `TestCampaign` | Sequence of suites with shared workers config.                                      |
| `TestCycle`    | Smoke + main, _mode_ applies to the smoke tests (fail-fast \| wait-for-all).        |

## The break with pytest

Ocarina is **not** a pytest plugin. The README says so flat out:

> Ships its own test runner: Ocarina is NOT a pytest plugin.

Why?

1. **pytest vocabulary isn't ISTQB.** pytest has `test_function`, `parametrize`, `fixture`, `conftest`. Internally coherent, but a different universe. Wrapping Ocarina as a pytest plugin would have forced _translation_&nbsp;—&nbsp;exactly what the philosophy refuses (see [`01-flip-the-problem.md`](01-flip-the-problem.md)).
2. **Independence.** A plugin depends on its host's API. Ocarina wants to be auditable in an afternoon, no pytest knowledge required.
3. **Stance on fixtures.** Ocarina swaps fixtures for _closures_ + _scenario fragments_ + `Effect` for `setup`/`teardown`. Stance: "poor man's rich"&nbsp;—&nbsp;one mechanism, the **closure**, for _every_ injection. One closure does what classical OO would pull off with fixtures + scopes + inheritance.

## The break with Cucumber / Gherkin

No `.feature` file, no step definition, no glue layer. The scenario is **Python**, directly executable, directly typed, directly refactorable. No permanent translation to maintain.

The "language" Ocarina exposes to scenarios isn't a text DSL. It's an **embedded Python DSL**:

```python
return [
    drive_page(
        act(on_homepage, open_then_verify_homepage)
            .failure(just_log_error("Failed to reach the homepage..."))
            .success(log_success_with_current_url_and_take_screenshot("On the homepage!")),
        act(on_homepage, click_book_call_page_cta)
            .failure(just_log_error("Failed to click on the 'Book a call' CTA..."))
            .success(just_log_success("Clicked on the 'Book a call' CTA!")),
    ),
    drive_page(
        act(on_book_a_call_page, verify_book_call_page)
            .failure(just_log_error("Failed to verify the 'Book a call' page..."))
            .success(log_success_with_current_url_and_take_screenshot("On the 'Book a call' page!")),
    ),
]
```

Pure Python. No lexer, no third-party runtime, no translation. Typed too&nbsp;—&nbsp;the slightest mismatch is a _mypy_ error (see [`../02-ocarina/03-railway/02-action-chain-states.md`](../02-ocarina/03-railway/02-action-chain-states.md)).

## Consequence on reporting

The _reporting_ sticks to ISTQB vocabulary too. `pretty_print_results` spits out:

```
Campaign
• Suite
  > Test case 1
    » PASSED
  > Test case 2
    » FAILED
      → Error message
        ⫸ At step 3
```

Three indents, three levels: campaign, suite, case. The _step_ only shows up as failure context ("At step 3"). No Python class name surfaces in the output&nbsp;—&nbsp;the end user sees trade vocabulary, not code.

## ISTQB ↔ Ocarina glossary

| ISTQB term      | Ocarina term                                                           | Note                                                         |
| --------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------ |
| _Test step_     | `act()`                                                                | Atomic action.                                               |
| _Test case_     | `Test[Driver]`                                                         | Wraps a scenario.                                            |
| _Test scenario_ | `Scenario[Driver]`                                                     | Made of a `test_chain`, a `setup`, a `teardown`, `watchers`. |
| _Test suite_    | `TestSuite[Driver]`                                                    | Parallelized.                                                |
| _Test campaign_ | `TestCampaign[Driver]`                                                 | Sequential (between suites).                                 |
| _Test cycle_    | `TestCycle[Driver]`                                                    | Smoke + main, fail-fast or wait-for-all.                     |
| _Smoke test_    | `smoke_tests_campaigns=`                                               | Gate.                                                        |
| _Setup_         | `Scenario.setup: Effect`                                               | `Effect`.                                                    |
| _Teardown_      | `Scenario.teardown: Effect`                                            | `Effect` too. Always runs, errors swallowed.                 |
| _Test report_   | `pretty_print_results`, `generate_docx_proof`, `generate_json_results` | Post-execution plugins.                                      |

## Link to Python's evolving type system

The Holy Book draws a sharp dependency: this vocabulary couldn't have been embodied this rigorously before PEP 695 _generics_, because you need to parameterize `TestSuite[Driver]` with a precise driver type. From the Holy Book (chapter "First feedbacks"):

> The recent evolution of Python's _type system_ is central to what makes Ocarina possible. Without being "the future" either: **this is established science, but one that arrived cruelly late in our ecosystem.**

That's why the framework requires `requires-python = ">=3.14"` (see [`../00-big-picture/02-stack-matrix.md`](../00-big-picture/02-stack-matrix.md)).
