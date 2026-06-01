---
title: "Chapter 04 — Framework internal tests"
description: "How Ocarina tests itself: five families of tests, a deliberate coverage policy and an Allure report versioned on GitHub Pages."
weight: 5
date: 2026-05-20
tags: ["internal-tests", "typing", "scenarios"]
sidebar:
  open: true
---

# Chapter 04&nbsp;—&nbsp;Framework internal tests

> How Ocarina tests itself. Five test families, a clear-eyed coverage policy, an Allure report archived on GitHub Pages.

## Outline

|  #  | File                                                         | Topic                                                                                               |
| :-: | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| 01  | [`01-strategy.md`](01-strategy.md)                           | "_From the outside like a user_" strategy + the `conftest.py` (FakeDriver, RecordingPOM, builders). |
| 02  | [`02-cram-prysk.md`](02-cram-prysk.md)                       | Cram tests (`prysk`): `.t` files                                                                    |
| 03  | [`03-pytest-scenarios.md`](03-pytest-scenarios.md)           | Test scenarios applied to the framework (pytest + allure + hypothesis).                             |
| 04  | [`04-mypy-plugins-types.md`](04-mypy-plugins-types.md)       | Tests on **static typing** via `pytest-mypy-plugins` (`*.yml`).                                     |
| 05  | [`05-syrupy-snapshots.md`](05-syrupy-snapshots.md)           | Snapshot tests (`syrupy`) for `pretty_print_results` and `results_to_json`.                         |
| 06  | [`06-hypothesis-properties.md`](06-hypothesis-properties.md) | Property-based testing for invariants.                                                              |
| 07  | [`07-coverage-policy.md`](07-coverage-policy.md)             | Coverage policy: what's tested, what is NOT, why.                                                   |
| 08  | [`08-allure-history.md`](08-allure-history.md)               | Allure + composite action `allure-history` + GH Pages deploy.                                       |

## Summary table

| Family         | Tool                       | Quantity                                 | Topic                                               | Target                        |
| -------------- | -------------------------- | ---------------------------------------- | --------------------------------------------------- | ----------------------------- |
| Scenarios      | `pytest` + `allure-pytest` | ~15 `test_*.py` files                    | DSL, orchestration, Playwright actor                | Covers _behavior_             |
| Cram           | `prysk`                    | 15 `.t` files                            | Selenium + Playwright CLI: parsing, validations, defaults | Covers _CLI user surface_     |
| Static types   | `pytest-mypy-plugins`      | ~5 `*test_types.yml` files               | Type inferences, narrowing, expected errors         | Covers _typing_               |
| Snapshots      | `syrupy`                   | 2 `.ambr` files                          | Output of `pretty_print_results`, `results_to_json` | Covers _output format_        |
| Property-based | `hypothesis`               | 1 file (`test_invariants_properties.py`) | Behavior on random values                           | Covers _robustness to inputs_ |

## Approach

In `conftest.py`:

> Philosophy: exercise the framework from the outside the way a real user does. No asserts on private attributes, no mocks of framework internals&nbsp;—&nbsp;just a minimal fake driver + driver pool, and small constructors for Scenario / Test / TestSuite / TestCampaign / TestCycle.

The tests **don't inspect** the internal machinery (the _anal probe_\* phenomenon). They _exercise_ the framework the way a user project would. That's the guarantee the tests validate the _public contract_, not the implementation.

\* _For the more mischievous: attribute this phenomenon as a quotation to some literary peer._
