---
title: "02.05.08 — filter_tests_by_ids"
weight: 8
date: 2026-05-20
series: ["orchestration"]
series_order: 8
tags: ["ocarina"]
---

# 02.05.08&nbsp;—&nbsp;`filter_tests_by_ids`

> Source file: [`src/ocarina/dsl/testing/filter_tests_by_ids.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/filter_tests_by_ids.py)
>
> Called by `TestSuite.__init__` to apply the CLI flags `--only <ids>` and `--exclude <ids>`. Mutually exclusive&nbsp;—&nbsp;can't pass both.

## Code

```python
def filter_tests_by_ids[Driver](
    tests: Sequence[Test[Driver]],
    *,
    only: Iterable[str] = (),
    exclude: Iterable[str] = (),
    logger: ILogger,
) -> Sequence[Test[Driver]]:
    only_set = set(only)
    exclude_set = set(exclude)

    if only_set and exclude_set:
        raise ValueError("--only and --exclude cannot be used together")

    known_ids = {test.test_id for test in tests}

    if only_set:
        matched = only_set & known_ids
        if matched:
            joined = ", ".join(sorted(matched))
            logger.info(f"--only: matched test IDs: {joined}")
        return [test for test in tests if test.test_id in only_set]

    if exclude_set:
        matched = exclude_set & known_ids
        if matched:
            joined = ", ".join(sorted(matched))
            logger.info(f"--exclude: matched test IDs: {joined}")
        return [test for test in tests if test.test_id not in exclude_set]

    return tests
```

## Four guarantees

### 1. Mutex `--only` / `--exclude`

```python
if only_set and exclude_set:
    raise ValueError("--only and --exclude cannot be used together")
```

Passing both is a _runtime_ error (not a _mypy_ one). Semantically nonsense: "keep only A, B" AND "exclude C, D"? At the CLI level, doesn't make sense. The mutex kills ambiguity.

This constraint is also formalized CLI-side in `_create_validate_only_exclude_mutex_effect` (see [`../11-opinionated/03-selenium-cli.md`](../11-opinionated/03-selenium-cli.md)). The user sees the error _before_ the suite is even constructed.

### 2. _Silent ignore_ of unknown IDs

If the user passes `--only test_login,test_typo` and `test_typo` doesn't exist (typo), Ocarina **silently ignores** `test_typo`:

```python
return [test for test in tests if test.test_id in only_set]
```

No match for `test_typo` → it just doesn't appear. No error, no warning.

The reasoning, spelled out in the docstring:

> Unknown IDs (not matching any test.test_id) are silently ignored, so a typo in a CI script does not break the run.

→ Pragmatic call: a CI that "doesn't break on a typo" is more _robust_ than one that demands perfect IDs.

### 3. Log of matched IDs

```python
matched = only_set & known_ids
if matched:
    joined = ", ".join(sorted(matched))
    logger.info(f"--only: matched test IDs: {joined}")
```

```
Login happy paths: filtering tests... --only: matched test IDs: login_no_otp, login_otp
```

Sorted, comma-separated. 20 IDs still reads cleanly.

### 4. If neither `only` nor `exclude` → return `tests` as-is

```python
return tests
```

`TestSuite(... only_ids=(), exclude_ids=())` adds **no copy**, **no overhead**. Default case.

## Prefixed logger

```python
logger=create_logger().set_prefix(lambda: f"{self.name}: filtering tests...")
```

→ Log line becomes `Login happy paths: filtering tests... --only: ...`. The prefix is **lazy** (`Thunk[str]`), recomputed on every log. See [`../09-ports.md`](../09-ports.md), `ILogger.set_prefix` section.

## Integration in `TestSuite.__init__`

```python
# in TestSuite.__init__
self._tests = filter_tests_by_ids(
    tests,
    only=only_ids,
    exclude=exclude_ids,
    logger=create_logger().set_prefix(
        lambda: f"{self.name}: filtering tests..."
    ),
)
```

Filtering happens at **suite construction**, not at execution.

- The `validate_test_runners_ids` / `validate_test_runners_names` invariants run on `self._tests` (post-filter).
- If saturation is on and only one test survives, _that test_ gets cloned up to `max_workers`.

## Smoke edge case

You can _filter_ with `--only`, which applies **to every suite**.

- No smoke test matches `--only` → empty smoke suite → `campaign_has_failed` returns `False` → main runs, smoke bypassed.
- No main test matches either → empty `_results`.

`--only` is a filter, not a hierarchy selector. You can filter cross-cuttingly by ID.

## Diagram

```
                ┌────────────────────────────────┐
                │ filter_tests_by_ids(tests,     │
                │   only=..., exclude=...)       │
                └──────────────┬─────────────────┘
                               ▼
                ┌────────────────────────────────┐
                │ only_set && exclude_set ?      │── True ─► raise ValueError
                └──────────────┬─────────────────┘
                               ▼
                ┌────────────────────────────────┐
                │ only_set non-empty ?           │── True ─► log matched IDs
                └──────────────┬─────────────────┘            return [test for test in tests if test.test_id in only_set]
                               ▼
                ┌────────────────────────────────┐
                │ exclude_set non-empty ?        │── True ─► log matched IDs
                └──────────────┬─────────────────┘            return [test for test in tests if test.test_id not in exclude_set]
                               ▼
                          return tests
```
