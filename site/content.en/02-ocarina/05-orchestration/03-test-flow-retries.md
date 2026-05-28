---
title: "02.05.03 — TestFlow[Driver] — retry policy"
description: "TestFlow[Driver]: Ocarina's retry policy, a retry loop with a fresh driver per attempt and linear backoff."
weight: 3
date: 2026-05-20
series: ["orchestration"]
series_order: 3
tags: ["ocarina"]
---

# 02.05.03&nbsp;—&nbsp;`TestFlow[Driver]`&nbsp;—&nbsp;retry policy

> Source file: [`src/ocarina/dsl/testing/internals/test_flow.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/internals/test_flow.py)
>
> **One job**: for a single `Test`, run the retry loop, acquire a fresh driver per attempt, apply the backoff policy.

## Why an intermediate level between `TestSuite` and `TestExecutor`

| Level          | Doesn't know about                              |
| -------------- | ----------------------------------------------- |
| `TestExecutor` | Retries, the driver pool                        |
| **`TestFlow`** | Inter-test concurrency, suite-level aggregation |
| `TestSuite`    | One attempt's execution, retries                |

A _genuinely strict_ separation. `TestFlow` is the only level that knows both the pool and the retry policy&nbsp;—&nbsp;combining them is its whole job.

## Code

```python
def run(self, test: Test[Driver]) -> TestSuiteResult:
    max_attempts = 1 + self._max_retries
    setup_failures = 0
    last_steps_count = -1
    last_result = None

    taxonomy = (self._cycle_name, self._campaign_name, self._suite_name, test.name)
    logger_with_taxonomy = self._create_logger().set_domain_taxonomy(taxonomy)
    logger_without_taxonomy = self._create_logger()

    for attempt in range(1, max_attempts + 1):
        self._act_counter.reset()

        with self._drivers_pool.acquire() as driver:
            outcome = self._executor.execute(
                test,
                driver=driver,
                taxonomy=taxonomy,
                logger_with_taxonomy=logger_with_taxonomy,
                logger_without_taxonomy=logger_without_taxonomy,
                attempt=attempt,
                max_attempts=max_attempts,
            )

        if outcome.skipped:
            return None, -1, test.test_id

        if outcome.setup_failed:
            setup_failures += 1

        last_result = outcome.result
        last_steps_count = outcome.steps_count

        if outcome.should_retry and attempt <= max_attempts:
            logger_with_taxonomy.cleanup()
            time.sleep(attempt)
            continue

        break

    if setup_failures >= max_attempts:
        msg = (
            f"{test.name} — Skipped: setup failed on all"
            f" {max_attempts} attempts. Fix the setup before retrying."
        )
        logger_with_taxonomy.warning(msg)
        return None, -1, test.test_id

    self._act_counter.reset()
    return last_result, last_steps_count, test.test_id
```

## Line-by-line anatomy

### Total number of attempts

```python
max_attempts = 1 + self._max_retries
```

`_max_retries` lands in the constructor (default 8). So `max_attempts = 9` by default. The Holy Book has a name for it: "_9 lives like a cat_ 🐱" in the "First real-world hurdles" chapter.

### Build the two loggers _once_

```python
taxonomy = (cycle, campaign, suite, test_name)
logger_with_taxonomy = self._create_logger().set_domain_taxonomy(taxonomy)
logger_without_taxonomy = self._create_logger()
```

Two loggers, **built once** for all attempts. The `FileLogger` is in charge of _resetting_ its file on the next attempt (`logger.cleanup()`, see below).

### Main loop

```python
for attempt in range(1, max_attempts + 1):
    self._act_counter.reset()
    with self._drivers_pool.acquire() as driver:
        outcome = self._executor.execute(...)
```

- **`act_counter.reset()`** before each attempt so the previous attempt's steps don't double-count.
- **`with pool.acquire() as driver`**: a _fresh_ driver per attempt. `with` guarantees disposal on exit, even on exception.
- **`executor.execute(...)`** delegates the rest.

### Three branches after each attempt

```python
if outcome.skipped:
    return None, -1, test.test_id

if outcome.setup_failed:
    setup_failures += 1

last_result = outcome.result
last_steps_count = outcome.steps_count

if outcome.should_retry and attempt < max_attempts:
    logger_with_taxonomy.cleanup()
    time.sleep(attempt)
    continue

break
```

| Case                                              | Behavior                                                                                                     |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `outcome.skipped` (e.g. `Test(skipped=True)`)     | Immediate return `(None, -1, test_id)`. No retry, no counting.                                               |
| `outcome.setup_failed`                            | Bumps `setup_failures`; the rest of the logic still applies (a retry can still fire if `should_retry=True`). |
| `outcome.should_retry and attempt < max_attempts` | `logger.cleanup()` (recycle the log file), `time.sleep(attempt)` (linear backoff 1s, 2s, 3s, …), `continue`. |
| otherwise                                         | `break`&nbsp;—&nbsp;verdict is in (Pass or Fail).                                                            |

### Linear backoff `time.sleep(attempt)`

| Attempt | Sleep before retry |
| ------- | ------------------ |
| 1       | 1s                 |
| 2       | 2s                 |
| 3       | 3s                 |
| 4       | 4s                 |
| 5       | 5s                 |
| 6       | 6s                 |
| 7       | 7s                 |
| 8       | 8s                 |
| 9       | 9s                 |

Worst case: `1+2+3+4+5+6+7+8+9 = 45s` of accumulated sleep on top of actual execution.

Why **linear** instead of **exponential** (`2^attempt`)? Exponential worst case is `2+4+8+16+32+64+128+256+512 = 1022s` ≈ 17 minutes of sleep.

### "All setup attempts failed" case

```python
if setup_failures >= max_attempts:
    msg = (
        f"{test.name} — Skipped: setup failed on all"
        f" {max_attempts} attempts. Fix the setup before retrying."
    )
    logger_with_taxonomy.warning(msg)
    return None, -1, test.test_id
```

If `setup()` failed on **every** attempt, the test is **SKIPPED**, not FAILED. When the setup never works, you can't conclude the chain is broken&nbsp;—&nbsp;only that **the test couldn't run**. An explicit message tells you to _fix the setup_ (actionable).

A detail that separates _infrastructure failure_ from _functional failure_.

## `TestSuiteResult`

```python
type TestSuiteResult = tuple[TestResult, _TestStepsCount, TestId]
```

- `TestResult`: `Ok`, `Fail`, or `None` (skip).
- `_TestStepsCount`: `int`, `-1` if skip / setup_failed-all.
- `TestId`: `str`.

The tuple that bubbles up to `TestSuite`, where it gets aggregated into `dict[str, TestSuiteResult]`.

## Why `logger.cleanup()` before the retry

We don't care about artifacts (dedicated log file or noise in the DOCX) for flakiness&nbsp;—&nbsp;checking the terminal is enough to confirm it. So `cleanup` recycles the current log file on every retry instead of stacking one per attempt.

For `PrintLogger`, `cleanup` is a no-op.

## `__init__` parameters recap

```python
def __init__(
    self,
    *,
    executor: TestExecutor[Driver],
    drivers_pool: WebDriversPool[Driver],
    create_logger: Thunk[ILogger],
    act_counter: ActCounter,
    cycle_name: str,
    campaign_name: str,
    suite_name: str,
    max_retries: int = _DEFAULT_MAX_RETRIES,   # 8
) -> None: ...
```

| Parameter                                   | Source                                                                                                                                          | Why                                  |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| `executor`                                  | Instantiated by `TestSuite._build_flow()`; receives `create_logger`, `take_screenshot`, `act_counter`, `transient_errors`, `autoscreen_on_fail` | Delegates one attempt's execution.   |
| `drivers_pool`                              | Built on the project side (`create_selenium_drivers_pool`)                                                                                      | Acquiring fresh drivers.             |
| `create_logger`                             | _Thunk_ that returns a new logger                                                                                                               | Build two loggers _only once_.       |
| `act_counter`                               | `ThreadsBasedActCounter()` thread-local                                                                                                         | Count executed `act` calls.          |
| `cycle_name`, `campaign_name`, `suite_name` | Injected in cascade from `TestSuite`                                                                                                            | Build the taxonomy for `FileLogger`. |
| `max_retries`                               | Defined per project via `TestSuite(max_retries_per_test=...)`                                                                                   | 8 by default; 9 lives.               |
