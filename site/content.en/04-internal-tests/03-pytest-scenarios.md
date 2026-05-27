---
title: "04.03 — Scenario tests (pytest + allure)"
description: "13 test_*.py files in tests/scenarios/ cover the DSL and orchestration. Dynamic tests."
weight: 3
date: 2026-05-20
series: ["internal-tests"]
series_order: 3
---

# 04.03&nbsp;—&nbsp;Scenario tests (pytest + allure)

> 13 `test_*.py` files in `tests/scenarios/` cover the DSL and orchestration. Dynamic tests.

## Listing

```
tests/scenarios/
├── conftest.py                              # FakeDriver, RecordingPOM, make_*
├── test_railway_and_action_chain.py         # create_act, drive_page, Result, ChainRunner
├── test_match_page.py                       # match_page / when (first/last branches, exceptions)
├── test_validate.py                         # validate, assert_that, otherwise, then, chain_validations
├── test_invariants_properties.py            # hypothesis (see 06-hypothesis-properties)
├── test_drivers_pool.py                     # WebDriversPool (acquire, warmup, shutdown, semaphore leaks)
├── test_screenshotter.py                    # Screenshotter (single shot, burst, healthcheck, threadsafety)
├── test_driver_builder.py                   # DriverBuilder (profile tmp dir, dispose)
├── test_watcher.py                          # Watcher (start, stop, callback errors swallowed, dedup cache)
├── test_test_suite.py                       # TestSuite (parallel, saturation, only/exclude, transient_errors)
├── test_test_cycle_and_bootstrap.py         # TestCycle, mode fail-fast vs wait-for-all, bootstrap
├── test_loggers_and_reports.py              # PrintLogger, FileLogger, pretty_print, JSON
├── test_docx_tests_proofs.py                # generate_docx_proof (parse logs, insert images)
└── test_env.py                              # smoke test: versions, Python 3.14+
```

## Example internal test

```python
@allure.epic("Railway / action chain")
@allure.feature("Action chain")
@allure.tag("act", "handlers", "happy-path")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("layer", "unit")
@allure.title("A successful act reports success; the success handler fires once")
def test_success_act_fires_success_handler() -> None:
    pom = RecordingPOM()
    calls = {"success": 0, "failure": 0}

    chain = (
        create_act(pom, lambda p: p.step("click"))
        .failure(lambda _: calls.__setitem__("failure", calls["failure"] + 1))
        .success(lambda: calls.__setitem__("success", calls["success"] + 1))
        .execute()
    )

    assert chain.is_ok()
    assert pom.calls == ["click"]
    assert calls == {"success": 1, "failure": 0}
```

| Assertion                               | Target                              |
| --------------------------------------- | ----------------------------------- |
| `chain.is_ok()`                         | Public API                          |
| `pom.calls == ["click"]`                | Observable POM behavior (recording) |
| `calls == {"success": 1, "failure": 0}` | Right handler called                |

## Allure annotations

| Category              | Typical values                                                                                                     |
| --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `epic`                | "Railway / action chain", "Invariants", "Orchestration", "Watcher", "Drivers pool", "Reports", "Match page"        |
| `feature`             | "Action chain", "Validate", "TestSuite", "TestCycle", "Bootstrap", "Pretty print", "JSON", "DOCX proofs"           |
| `tag`                 | "act", "handlers", "happy-path", "error-handling", "retry", "transient", "smoke", "skip", "saturation", "parallel" |
| `severity`            | CRITICAL > NORMAL > MINOR > TRIVIAL                                                                                |
| `label("layer", ...)` | "unit", "integration"                                                                                              |

## `test_test_suite.py`

- Tests pass in sequential mode (`max_workers=1`).
- Tests pass in parallel mode (`max_workers=N`).
- `--only` / `--exclude` filtering.
- `--only` + `--exclude` mutex.
- Saturation: tests cloned with `[COPY N]`.
- Retries on transient errors.
- Setup failure → SKIPPED when every attempt fails at setup.
- A `skipped=True` test stops immediately.
- Guardrails (unique names, unique IDs).
- `take_screenshot` called on fail if `autoscreen_on_fail`.
- Exact attempt counting on `max_retries` (one test covers the loop edge).

## `test_match_page.py`

| Case                                                               | Assertion                                     |
| ------------------------------------------------------------------ | --------------------------------------------- |
| First branch matches → executed                                    | `chain.is_ok()`, later branches not evaluated |
| Second branch matches → executed                                   | id.                                           |
| No branch matches                                                  | `NoMatchingBranchError` in the `Fail`         |
| Branch matches, but its `then` fails                               | `Fail` propagated                             |
| `condition` raises an ordinary `Exception`                         | Treated as `False`, later branches tried      |
| `condition` raises an exception from the `raised_exceptions` tuple | Re-raise                                      |
| Branch `then=[]` matches                                           | `Ok(None)`                                    |
| `match_page` in the middle of a `test_chain`                       | Short-circuits if failed                      |

## `test_drivers_pool.py`

Uses a `FakeDriverFactory` that can be configured to raise / block / sleep, and counts its calls.

- `acquire` before `warmup`: creates on demand.
- `acquire` after `warmup`: pulls from the queue.
- `warmup` creates exactly `max_size` drivers.
- `acquire` beyond `max_size`: blocks until release.
- `create_driver` raising: releases the semaphore (no leak).
- `dispose` raising: releases anyway (no leak).
- `WarmupTimeoutError` when progress stalls.
- `shutdown` disposes drivers in the queue, not the acquired ones.

## `test_docx_tests_proofs.py`

- Parses a minimal `logs/{campaign}/{suite}/{test}.log` tree.
- Generates 1 `.docx` per `.log`.
- Inserts an image when the `.log` contains `"Screenshot: <path>"`.
- Converts `[UTC_DATE::...]` to local time.
- Truncates over-long filenames.
- Creates a unique subfolder under `output_root`.

Note: this test produces real `.docx` files validated by `python-docx`.

## Conventions

All tests:

- Are in `snake_case`.
- Begin with `test_`.
- Have a **descriptive** name (`test_success_act_fires_success_handler` rather than `test_act_1`).
- Are annotated with Allure (readable title, severity, tag).

The Allure report ends up **navigable like a book**&nbsp;—&nbsp;every test reads as a self-documenting chapter.

## `pytest --hypothesis-show-statistics`

```
pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
```

`--hypothesis-show-statistics` prints at the end of the run:

```
=== Hypothesis Statistics ===
- 12 passing examples
- 0 failing examples
- 0 invalid examples
```

Shows how many examples `hypothesis` generated (see [`06-hypothesis-properties.md`](06-hypothesis-properties.md)).
