---
title: "02.05.02 — TestExecutor[Driver]"
description: "Source file: src/ocarina/dsl/testing/internals/test_executor.py"
weight: 2
date: 2026-05-20
series: ["orchestration"]
series_order: 2
tags: ["ocarina", "watcher"]
---

# 02.05.02&nbsp;—&nbsp;`TestExecutor[Driver]`

> Source file: [`src/ocarina/dsl/testing/internals/test_executor.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/internals/test_executor.py)

> **One job**: run **one attempt** of a test with **one driver**. Knows nothing about retries, the driver pool, or suite-level aggregation.

## `ExecutionOutcome`

```python
@final
@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    result: TestResult
    skipped: bool
    setup_failed: bool
    should_retry: bool
    steps_count: int
```

| Field          | Type                                 | Meaning                                                          |
| -------------- | ------------------------------------ | ---------------------------------------------------------------- |
| `result`       | `TestResult` = `Result[Any] \| None` | The chain's result (Ok, Fail), or `None` if skip / setup_failed. |
| `skipped`      | `bool`                               | True if `test_runner.skipped` (i.e. `Test(skipped=True)`).       |
| `setup_failed` | `bool`                               | True if the scenario's `setup()` raised.                         |
| `should_retry` | `bool`                               | True if the _retry rule_ applies (transient_error detected).     |
| `steps_count`  | `int`                                | Number of `act` calls; `-1` if skip or setup_failed.             |

- **`slots=True`**: blocks dynamic attribute addition, saves memory. This object rides the hot path&nbsp;—&nbsp;`slots` earns its keep.
- **`frozen=True`**: immutable, safe to share across threads.
- **`@final`**: no inheritance.

## Execution order for one attempt

```
┌──────────────────────────────────────────────────────────────────────┐
│  test_runner = test.spawn(driver, logger_with_taxonomy)              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  test_runner.skipped ?          │── True ─► return Outcome(skipped=True, ...)
              └────────────────┬────────────────┘
                               │ False
                               ▼
              ┌─────────────────────────────────┐
              │  logger.test_name(test.name)    │   (annotation)
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  setup() (if not None)          │── raises ─► teardown() (if not None)
              └────────────────┬────────────────┘            ↓
                               │                  return Outcome(setup_failed=True, should_retry=True, ...)
                               ▼
              ┌─────────────────────────────────┐
              │  watchers.start(driver, logger, │
              │                 take_screenshot)│   (1 daemon thread per watcher)
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  _run_chain(chain_runners, ...) │── returns (result, should_retry)
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  watchers.stop()                │   (always)
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  teardown() (if not None)       │   (ALWAYS, even if chain failed)
              └────────────────┬────────────────┘     (exceptions are logged & swallowed)
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  steps_count = act_counter.get()│
              │  return Outcome(...)            │
              └─────────────────────────────────┘
```

## `execute`

```python
def execute(
    self, test: Test[Driver], *,
    driver: Driver,
    taxonomy: tuple[str, ...],
    logger_with_taxonomy: ILogger,
    logger_without_taxonomy: ILogger,
    attempt: int, max_attempts: int,
) -> ExecutionOutcome:
    test_runner = test.spawn(driver, logger_with_taxonomy)

    if test_runner.skipped:
        return ExecutionOutcome(result=None, skipped=True, setup_failed=False,
                                should_retry=False, steps_count=-1)

    logger_without_taxonomy.test_name(test.name)

    if test_runner.setup is not None:
        try:
            test_runner.setup()
        except Exception as exc:
            msg = f"{test.name} -- Setup failed (attempt {attempt}/{max_attempts}): {exc}"
            logger_with_taxonomy.warning(msg)
            if test_runner.teardown is not None:
                self._run_teardown(test_runner.teardown, test_name=test.name, logger=logger_with_taxonomy)
            return ExecutionOutcome(result=None, skipped=False, setup_failed=True,
                                    should_retry=True, steps_count=-1)

    watchers: Sequence[Watcher[Driver]] = test_runner.watchers or []
    self._start_watchers(watchers, driver=driver, test_name=test.name, taxonomy=taxonomy)

    result, should_retry = self._run_chain(
        test_runner.chain_runners, test_name=test.name, attempt=attempt,
        driver=driver, logger=logger_without_taxonomy,
        logger_with_taxonomy=logger_with_taxonomy, max_attempts=max_attempts,
    )

    self._stop_watchers(watchers)

    if test_runner.teardown is not None:
        self._run_teardown(test_runner.teardown, test_name=test.name, logger=logger_with_taxonomy)

    steps_count = self._act_counter.get()
    return ExecutionOutcome(result=result, skipped=False, setup_failed=False,
                            should_retry=should_retry, steps_count=steps_count)
```

## Two loggers: why

`logger_with_taxonomy` vs `logger_without_taxonomy`:

| Logger                    | Domain taxonomy                       | Use case                                                                                              |
| ------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `logger_with_taxonomy`    | `(cycle, campaign, suite, test_name)` | Chain logs&nbsp;—&nbsp;written to `<base>/cycle/campaign/suite/test_name.log`                         |
| `logger_without_taxonomy` | _(empty)_                             | Administrative announcements (`test_name(...)`, retry message)&nbsp;—&nbsp;go to console / by default |

Without the split, the retry announcement "_Test died! Life: 3/9_" would land inside the test's own log file&nbsp;—&nbsp;the exact file you're about to recycle for the next attempt. Clean decoupling.

## `_run_chain`

```python
def _run_chain(
    self, chain_runners: TestChain, *,
    test_name: str, attempt: int, driver: Driver,
    logger: ILogger, logger_with_taxonomy: ILogger, max_attempts: int,
) -> tuple[TestResult, bool]:
    result: TestResult = None

    for chain_runner in chain_runners:
        try:
            chain = chain_runner.run()
        except Exception as exc:
            chain = ActionChain(has_failed=True, result=Fail(error=exc))
        result = chain.result()

        if chain.has_failed():
            if (attempt < max_attempts
                and self._transient_errors
                and is_test_result_fail(result)
                and isinstance(result.error, self._transient_errors)):
                msg = f"{test_name} -- Test died! Life: {attempt}/{max_attempts}"
                logger.warning(msg)
                return result, True              # ◄── should_retry=True

            if self._autoscreen_on_fail and is_test_result_fail(result):
                with suppress(Exception):
                    self._take_screenshot(driver, logger_with_taxonomy, "FAIL")

            return result, False                 # ◄── should_retry=False

    return result, False                         # ◄── all chain_runners passed
```

| Case                                                                     | Behavior                                                                                                                  |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Chain `Ok`                                                               | Continue. At the end, returns `(last_result, False)`.                                                                     |
| Chain `Fail` + transient + attempts left                                 | Log warning "_Test died! Life: X/Y_", returns `(result, True)`. **No auto-screenshots**&nbsp;—&nbsp;we're about to retry. |
| Chain `Fail` + non-transient (or out of attempts) + `autoscreen_on_fail` | Auto-screenshots, returns `(result, False)`.                                                                              |
| Chain `Fail` + non-transient (or out of attempts) + no autoscreen        | Returns `(result, False)`.                                                                                                |

Subtle point: the `try/except` around `chain_runner.run()` catches anything that would've escaped the ROP DSL (thunk bug, etc.) and re-wraps it as a `Fail`.

## `_run_teardown`

```python
def _run_teardown(self, teardown: Effect, *, test_name: str, logger: ILogger) -> None:
    try:
        teardown()
    except Exception as exc:
        msg = f"{test_name} -- Teardown failed (ignored): {exc}"
        logger.warning(msg)
```

Teardown **never fails** a test. If it raises, a warning gets logged and execution moves on. Lines up with isolation: the test has already given its verdict (Pass / Fail). A failing teardown is infrastructure noise to flag, not a test result.

## `_start_watchers`

```python
def _start_watchers(self, watchers, *, driver, test_name, taxonomy):
    for index, watcher in enumerate(watchers):
        with suppress(Exception):
            watcher_name = (
                f"[{index + 1}] {test_name} - {watcher.name}"
                if len(watchers) > 1
                else f"{test_name} - {watcher.name}"
            )
            watcher_taxonomy = (*taxonomy[:-1], watcher_name)
            scoped_logger = self._create_logger().set_domain_taxonomy(watcher_taxonomy)
            watcher.start(driver, scoped_logger, self._take_screenshot)
```

1. **`[1]`, `[2]` indexing** only kicks in with **multiple** watchers. Readability, _plus_ no log-filename collisions across watchers.
2. **Taxonomy = `(*taxonomy[:-1], watcher_name)`**: we _swap_ the last element (`test_name`) for `<test_name> - <watcher_name>`. Net effect on the `FileLogger`: one `.log` per watcher, sibling to the test's `.log`. The DOCX report plugin emits them side-by-side in the same folder.
3. **`with suppress(Exception)`**: a watcher whose `start` blows up doesn't block the test. Watchers are _bonuses_, not critical.

## `_stop_watchers`

```python
def _stop_watchers(self, watchers: Sequence[Watcher[Driver]]) -> None:
    for watcher in watchers:
        with suppress(Exception):
            watcher.stop()
```

Same idea, errors suppressed. A sloppy watcher shouldn't crash the orchestration.

## Link to retry and pool

`TestExecutor` is strictly **stateless** about retries and the pool. Those live elsewhere:

- `TestFlow` acquires a driver and decides whether to replay (see [`03-test-flow-retries.md`](03-test-flow-retries.md)).
- `TestSuite` dispatches with parallelization (see [`04-test-suite.md`](04-test-suite.md)).

`TestExecutor` is called **per attempt**, each call handed `(driver, attempt, max_attempts, ...)`.
