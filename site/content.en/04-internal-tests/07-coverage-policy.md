---
title: "04.07 — Coverage policy: what's tested, what isn't, why"
description: "Ocarina's coverage policy: line coverage scoped to the pure DSL and agnostic infra, the rest tested otherwise or out of scope."
weight: 7
date: 2026-05-20
series: ["internal-tests"]
series_order: 7
---

# 04.07&nbsp;—&nbsp;Coverage policy: what's tested, what isn't, why

> Line coverage is **explicitly scoped** to the pure DSL and agnostic infra. The rest gets tested by other means (cram, types, snapshots, e2e) or stays out of scope (inert shapes).

## `pyproject.toml#tool.coverage.run`

```toml
[tool.coverage.run]
omit = [
    "*/__init__.py",
    "*/tests/*",
    "*/test_*.py",
    "src/ocarina/custom_errors/*",
    "src/ocarina/custom_types/*",
    "src/ocarina/ports/*",
    "src/ocarina/opinionated/loggers/custom_types/*",
    "src/**/*singleton.py",
    "src/**/consts/**",
    # Selenium adapter layer — exercised only against a real browser.
    "src/ocarina/infra/selenium/*",
    "src/ocarina/dsl/testing/selenium/*",
    "src/ocarina/opinionated/cli/selenium/*",
    "src/ocarina/pom/selenium/muted.py",
    "src/ocarina/opinionated/cli/phantoms.py",
    # Opinionated loggers — only file_logger.py stays in scope.
    "src/ocarina/opinionated/loggers/create_matching_logger.py",
    "src/ocarina/opinionated/loggers/muted_logger.py",
    "src/ocarina/opinionated/loggers/print_logger.py",
    "src/ocarina/opinionated/loggers/print_and_file_logger.py",
    "src/ocarina/opinionated/loggers/utils/*",
    # Traversed by cram tests
    "src/ocarina/opinionated/cli/store.py",
    "src/ocarina/opinionated/cli/builder.py",
]
```

## Categories

### 1. Obvious exclusions

| Pattern                    | Justification                                    |
| -------------------------- | ------------------------------------------------ |
| `*/__init__.py`            | Empty modules (Python 3 often doesn't need them) |
| `*/tests/*`, `*/test_*.py` | Tests don't test themselves                      |

### 2. Types / errors / ports / shapes

| Path                                             | Justification                                                 |
| ------------------------------------------------ | ------------------------------------------------------------- |
| `src/ocarina/custom_types/*`                     | Just `type X = ...` and frozen dataclasses. No runtime logic. |
| `src/ocarina/custom_errors/*`                    | Just Exception subclasses. No logic.                          |
| `src/ocarina/ports/*`                            | ABCs and Protocols. No behavior.                              |
| `src/ocarina/opinionated/loggers/custom_types/*` | id.                                                           |
| `src/**/consts/**`                               | Constants (`LOGGERS_CHOICES = (...)`).                        |
| `src/**/*singleton.py`                           | Trivial Singleton wrappers.                                   |

### 3. Selenium layer (e2e only)

| Path                                     | Justification                                                                                |
| ---------------------------------------- | -------------------------------------------------------------------------------------------- |
| `src/ocarina/infra/selenium/*`           | Real Selenium code (`Chrome()`, `Firefox()`). Only runs with a real browser.                 |
| `src/ocarina/dsl/testing/selenium/*`     | `create_selenium_test`, `create_selenium_watcher` (trivial factories on `Test` / `Watcher`). |
| `src/ocarina/opinionated/cli/selenium/*` | `create_selenium_*_cli_store` (reads `platform.system`, instantiates).                       |
| `src/ocarina/pom/selenium/muted.py`      | Utility `MutedPOM` (nearly empty).                                                           |

These files are **covered** by:

- **`ocarina-example/e2e.yml`** (manual CI, Firefox + Redis).
- **`ocarina-with-ai-example/ai_proof_e2e.yml`** (manual CI, Chrome + Firefox).

**External e2e suites** prove the adapters work&nbsp;—&nbsp;not the framework's pytest coverage.

### 4. Opinionated loggers (except FileLogger)

| Path                                                                                                     | Justification                                                                                              |
| -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `print_logger.py`, `muted_logger.py`, `print_and_file_logger.py`, `create_matching_logger.py`, `utils/*` | Trivial variants (terminal only, muted, factory dispatch).                                                 |
| `file_logger.py`                                                                                         | **Stays in scope**&nbsp;—&nbsp;it's the only one with real logic (taxonomy → file tree, cleanup, recycle). |

`FileLogger` is tested by `test_loggers_and_reports.py`. The others are trivial variations on `PrintLogger` that snapshots cover.

### 5. CLI traversed by cram

| Path                                      | Justification                                                    |
| ----------------------------------------- | ---------------------------------------------------------------- |
| `src/ocarina/opinionated/cli/store.py`    | Tested by cram (the `.t`s exercise `set` / `get` / `_Unset`)     |
| `src/ocarina/opinionated/cli/builder.py`  | Tested by cram (the `.t`s exercise parse + validation + effects) |
| `src/ocarina/opinionated/cli/phantoms.py` | Indirectly tested (the fields using it go through cram)          |

## Retained perimeter

| Module                                                                                         | Why                                                                                                 |
| ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `src/ocarina/railway/*`                                                                        | ROP core                                                                                            |
| `src/ocarina/dsl/invariants/*`                                                                 | Invariants DSL&nbsp;—&nbsp;tested by pytest + mypy plugins + hypothesis                             |
| `src/ocarina/dsl/testing/*` (except `selenium/`)                                               | Orchestration&nbsp;—&nbsp;tested in the "scenarios" folder of unit tests                            |
| `src/ocarina/dsl/testing_with_railway/*`                                                       | ROP DSL&nbsp;—&nbsp;tested by scenarios + mypy plugins                                              |
| `src/ocarina/infra/drivers_pool.py`, `driver_builder.py`, `screenshotter.py`, `act_counter.py` | Agnostic infra&nbsp;—&nbsp;tested with `FakeDriver`                                                 |
| `src/ocarina/aggregates/*`                                                                     | TypeGuard helpers                                                                                   |
| `src/ocarina/custom_invariants/*`                                                              | Pre-built invariants&nbsp;—&nbsp;tested by "scenarios" and traversed by the classes that use them   |
| `src/ocarina/opinionated/dsl/drive_page.py`                                                    | Trivial alias                                                                                       |
| `src/ocarina/opinionated/infra/act_counter.py`                                                 | Thread-local counter                                                                                |
| `src/ocarina/opinionated/launcher/bootstrap.py`                                                | Bootstrap&nbsp;—&nbsp;tested by `test_test_cycle_and_bootstrap.py`                                  |
| `src/ocarina/opinionated/plugins/reports/*`                                                    | Plugins&nbsp;—&nbsp;tested by `test_loggers_and_reports.py`, `test_docx_tests_proofs.py`, snapshots |

## Metrics

`--cov-report=html` (HTML) + `--cov-report=xml:coverage.xml` (XML) show:

| Coverage type   | Metric                                      |
| --------------- | ------------------------------------------- |
| Line coverage   | % of lines executed at least once           |
| Branch coverage | % of branches (if/else) covered _both ways_ |

The `--cov-branch` flag is on&nbsp;—&nbsp;Ocarina measures branch coverage, not just line (instruction) coverage.

## HTML

`make serve-htmlcov` opens `htmlcov/index.html` in the browser.

- Green: covered.
- Red: not covered.
- Yellow: partially covered (missing branch).

## Why not test "everything"

| Naïve approach                                                | Ocarina policy                                                     |
| ------------------------------------------------------------- | ------------------------------------------------------------------ |
| Test everything, aim for 100% everywhere                      | Test _what matters_, aim for a healthy score on what matters       |
| Cover inert shapes (`type Result = ...`) → trivial 100%       | Exclude → 100% truly reflects covered _behavior_                   |
| Test Selenium adapters in unit CI → browser setup on every PR | Test the adapters in _manual_ e2e CI → fast CI, heavy CI on demand |
| Test trivial loggers → boilerplate                            | Test only loggers with real logic                                  |

On top of what pytest gives us, we account for the other _mechanisms_ verifying Ocarina's quality (cram, e2e, snapshots, types, manual tests).
