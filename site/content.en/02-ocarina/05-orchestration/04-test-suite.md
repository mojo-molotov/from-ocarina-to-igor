---
title: "02.05.04 — TestSuite[Driver] — parallelized engine"
description: "TestSuite[Driver]: Ocarina's parallelized engine, concurrent test execution, worker saturation, ID filtering and pre-execution invariants."
weight: 4
date: 2026-05-20
series: ["orchestration"]
series_order: 4
tags: ["ocarina", "parallelization"]
---

# 02.05.04&nbsp;—&nbsp;`TestSuite[Driver]`&nbsp;—&nbsp;parallelized engine

> Source file: [`src/ocarina/dsl/testing/oc_test_suite.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_suite.py)
>
> **One job**: run a sequence of `Test`s in parallel, handle _saturation_, ID filtering, and pre-execution invariant validation.

## Constructor

```python
def __init__(
    self,
    *,
    name: str,
    tests: Sequence[Test[Driver]],
    create_logger: Thunk[ILogger],
    drivers_pool: WebDriversPool[Driver],
    take_screenshot: ITakeScreenshot[Driver],
    act_counter: ActCounter | None = None,
    transient_errors: tuple[type[Exception], ...] = (),
    copy_indicator: str = "COPY",
    put_space_after_copy_indicator: bool = True,
    max_retries_per_test: int | None = None,
    autoscreen_on_fail: bool = False,
    saturate_workers: bool | None = None,
    only_ids: Iterable[str] = (),
    exclude_ids: Iterable[str] = (),
) -> None:
    self._guards_on_invoke(tests)
    # ... assignments ...
    self._tests = filter_tests_by_ids(
        tests,
        only=only_ids,
        exclude=exclude_ids,
        logger=create_logger().set_prefix(lambda: f"{self.name}: filtering tests..."),
    )
```

| Parameter                        | Type                          | Role                                                                | Default                                        |
| -------------------------------- | ----------------------------- | ------------------------------------------------------------------- | ---------------------------------------------- |
| `name`                           | `str`                         | Suite name (appears in logs & reports)                              | &nbsp;—&nbsp;                                  |
| `tests`                          | `Sequence[Test[Driver]]`      | List of tests to run                                                | &nbsp;—&nbsp;                                  |
| `create_logger`                  | `Thunk[ILogger]`              | Logger factory                                                      | &nbsp;—&nbsp;                                  |
| `drivers_pool`                   | `WebDriversPool[Driver]`      | Shared pool                                                         | &nbsp;—&nbsp;                                  |
| `take_screenshot`                | `ITakeScreenshot[Driver]`     | Callable `(driver, logger, category) -> None`                       | &nbsp;—&nbsp;                                  |
| `act_counter`                    | `ActCounter \| None`          | If `None` → `ThreadsBasedActCounter()`                              | `None`                                         |
| `transient_errors`               | `tuple[type[Exception], ...]` | Exceptions that trigger a retry                                     | `()`                                           |
| `copy_indicator`                 | `str`                         | Prefix for saturation-cloned tests                                  | `"COPY"`                                       |
| `put_space_after_copy_indicator` | `bool`                        | `[COPY 1]` (`True`) vs `[COPY1]` (`False`)                          | `True`                                         |
| `max_retries_per_test`           | `int \| None`                 | Max retries for a potentially flaky test                            | `None` → `_DEFAULT_MAX_RETRIES_PER_TEST` (8)   |
| `autoscreen_on_fail`             | `bool`                        | Automatically capture one or several screenshots (burst) on failure | `False`                                        |
| `saturate_workers`               | `bool \| None`                | Clone tests to saturate every worker if the pool is large enough    | `None` → cascade: suite > campaign > bootstrap |
| `only_ids`                       | `Iterable[str]`               | `--only` filter                                                     | `()`                                           |
| `exclude_ids`                    | `Iterable[str]`               | `--exclude` filter                                                  | `()`                                           |

## Guardrails

### At `__init__` time

```python
def _guards_on_invoke(self, tests: Sequence[Test[Driver]]) -> None:
    validate_test_runners_ids(tests=tests, name="tests").execute().raise_if_invalid()
```

→ Every `test_id` must be unique. Otherwise: `AggregateInvariantViolationError`. _Raised at construction_, before any execution attempt. Duplicate a `test_id` by accident and you find out instantly.

### Before execution

```python
def _guards_with_mounted_tests(self, tests: Sequence[Test[Driver]]) -> None:
    validate_test_runners_names(tests=tests, name="tests").execute().raise_if_invalid()
```

→ Every `name` must be unique + valid as a filename (see `is_valid_filename`). Since `1.1.10` this uniqueness is case-insensitive (NFC + casefold). Called **after saturation** (see [`05-saturation.md`](05-saturation.md)) because that's when the `[COPY 1] foo` names land.

### `validate_workers_amount`

```python
def run(self, *, max_workers: int, saturate_workers: bool = True) -> TestSuiteResults:
    self._results.clear()
    validate_workers_amount(workers_amount=max_workers, name="max_workers").execute().raise_if_invalid()
    ...
```

→ `max_workers >= 1`. Raises otherwise.

## Sequential vs parallel mode

```python
if max_workers == 1:
    self._guards_with_mounted_tests(self._tests)
    for test in self._tests:
        self._results[test.name] = flow.run(test)
else:
    # ... saturation ...
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(flow.run, test): (test.name, test.test_id)
            for test in tests
        }
        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                name, _ = futures.pop(future)
                self._results[name] = future.result()
```

### 1. `max_workers == 1` mode (sequential)

- No `ThreadPoolExecutor`.
- No saturation (pointless with one worker).
- Name guard fires immediately.
- Tests run one by one, in declared order.

### 2. `max_workers >= 2` mode (parallel)

- **Pool warm-up** if `saturate_workers=True`:
  ```python
  try:
      self._drivers_pool.warmup()
  except WarmupTimeoutError:
      # … help message + shutdown … re-raise
  ```
- **Saturation** of tests up to `max_workers` (see [`05-saturation.md`](05-saturation.md)).
- **`ThreadPoolExecutor(max_workers=N)`**: N worker threads.
- **`wait(futures, FIRST_COMPLETED)` pattern**: free memory as early as possible.

## `while futures`

```python
while futures:
    done, _ = wait(futures, return_when=FIRST_COMPLETED)
    for future in done:
        name, _ = futures.pop(future)
        self._results[name] = future.result()
```

1. **`wait(futures, return_when=FIRST_COMPLETED)`**: blocks until **at least one** future finishes. More efficient than `as_completed` (which iterates).
2. **`futures.pop(future)`**: drops it from the dict so the next `wait` doesn't see it again.
3. **`future.result()`**: grabs the return value (or re-raises the exception thrown in the thread).
4. **`self._results[name] = ...`**: _aggregate into a dict_, keyed by test name.

## warm-up

`WebDriversPool.warmup()` pre-instantiates all drivers _before_ submitting the futures.

| Without warm-up                                                     | With warm-up                                     |
| ------------------------------------------------------------------- | ------------------------------------------------ |
| 1st thread acquires a driver → cold-start latency (sometimes 5-10s) | All drivers ready                                |
| Risk of cascading cold-starts                                       | Drivers acquired instantly                       |
| No early detection of a driver that fails to start                  | `WarmupTimeoutError` raised early, with help msg |

Warm-up also has a **watchdog**: stall for `warmup_timeout` (5 min by default) and it raises. See [`../10-infra/01-drivers-pool.md`](../10-infra/01-drivers-pool.md)

## `try / except WarmupTimeoutError`

```python
try:
    self._drivers_pool.warmup()
except WarmupTimeoutError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(
        "Warmup stalled: killing the program. Expect it to raise soon."
        " Cleanup will be attempted but some browser processes may survive."
        " Check Activity Monitor / Dock for remaining instances."
    )
    time.sleep(30)
    self._drivers_pool.shutdown()
    time.sleep(5)
    raise
```

- **Explicit message** about Activity Monitor / Dock: the user knows what to do.
- **`time.sleep(30)`**: gives in-flight drivers time to die cleanly.
- **`shutdown()`** explicit.
- **`time.sleep(5)`**: lets shutdown finish.
- **`raise`**: propagate, the run fails cleanly.

## `test_names_and_ids`

```python
@property
def test_names_and_ids(self) -> Sequence[tuple[str, TestId]]:
    return [(test.name, test.test_id) for test in self._tests]
```

Used by `TestCampaign.run_all(skip_all=True)`: producing an _empty_ results dict (global skip) needs names and IDs without touching the tests.

## `_campaign_name` and `_cycle_name` fields injected post-construction

```python
self._campaign_name: str = ""
self._cycle_name: str = ""
```

These fields are **injected after the fact** by `TestCampaign.__init__` and `TestCycle.__init__`:

```python
# TestCampaign.__init__
for suite in self._suites:
    suite._campaign_name = self.name  # noqa: SLF001

# TestCycle.__init__
for campaign in self._campaigns:
    for suite in campaign._suites:
        suite._cycle_name = name
```

This enables **dynamic taxonomy construction**, wired just in time before the run. The merge is **bidirectional** and **strictly internal** to the framework&nbsp;—&nbsp;hence the access to "private" values via `# noqa: SLF001` (Self001). Deliberate: we **really don't want** to expose a setter or allow this publicly. It's a _hack_, but a justified one that leans on _laziness_&nbsp;—&nbsp;since execution is deferred, you can wire things ad hoc before the program even starts.
