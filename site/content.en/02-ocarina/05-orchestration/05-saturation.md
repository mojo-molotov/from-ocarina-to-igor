---
title: "02.05.05 — Worker saturation"
description: "Ocarina-specific trick: if a suite has fewer tests than workers, tests get randomly cloned until the worker count is filled. Copies are renamed [COPY 1] <name>, [COPY 2] <name>, etc."
weight: 5
date: 2026-05-20
series: ["orchestration"]
series_order: 5
tags: ["ocarina", "parallelization"]
---

# 02.05.05&nbsp;—&nbsp;Worker saturation

> Ocarina-specific trick: if a suite has fewer tests than workers, **tests get randomly cloned** until the worker count is filled. Copies are renamed `[COPY 1] <name>`, `[COPY 2] <name>`, etc.

## Why

The Holy Book formalizes the rationale in the "First real-world hurdles" chapter:

> Its `saturate_workers` option lets you force random cloning of tests inside a suite.
>
> As soon as there are more available _workers_ in the _DriversPool_ than there are tests to run in a suite, Ocarina will randomly clone tests, start every driver, and assign each one a test to perform.

And the finality:

> Beyond concurrency concerns, this cloning mechanic also makes sure that passing tests owe nothing to chance. The effect grows with the degree of horizontal scaling and the number of workers involved.

Two distinct wins:

1. **Surfacing concurrency _heisenbugs_**. A race condition is more likely to show its face when the test runs N times in parallel.
2. **Anti-luck**. A test that passes N times in parallel isn't passing _by luck_.

## Code

```python
def _prepare_tests_for_saturated_threading(
    self, max_workers: int
) -> Sequence[Test[Driver]]:
    base_tests = list(self._tests)

    if len(base_tests) == 0:
        return base_tests

    extra_tests: list[Test[Driver]] = []
    copy_counters: dict[str, int] = {}

    for _ in range(max_workers - len(base_tests)):
        original = random.choice(base_tests)  # noqa: S311
        copy_counters.setdefault(original.name, 0)
        copy_counters[original.name] += 1

        cloned = copy.copy(original)
        space = " " if self._put_space_after_copy_indicator else ""
        cloned.name = (
            f"[{self._copy_indicator}{space}{copy_counters[original.name]}]"
            f" {original.name}"
        )
        extra_tests.append(cloned)

    return base_tests + extra_tests
```

1. **Base list**: convert to `list` (mutation).
2. **Short-circuit on empty**: `--only` or `--exclude` could have emptied the suite, hence the check.
3. **Loop** `max_workers - len(base_tests)`:
   - **`random.choice(base_tests)`**: random pick (the same test can land twice).
   - **`copy.copy(original)`**: shallow copy. Scenario factory shared by reference, `name` mutable. Safe thanks to IoC + scenarios being **idempotent by design**.
   - **Rename**: `[COPY 1] <name>`, `[COPY 2] <name>`. Counter is per-test.
4. **Return**: `base + extras`.

Notes:

- **`# noqa: S311`**: ruff warns on `random.choice` (non-cryptographic). Deliberate: crypto-grade randomness is overkill, we just need variation.
- **`copy.copy(original)`** is enough. `copy.deepcopy` would be overkill&nbsp;—&nbsp;we just want a new wrapper with another `name`, not a duplicated scenario factory. Lean enough to stay lightweight.

## `saturate_workers`

The `saturate_workers` parameter can be set at **three** different places:

| Level          | Source                               | Effect                 |
| -------------- | ------------------------------------ | ---------------------- |
| `bootstrap`    | `bootstrap(saturate_workers=...)`    | Global default         |
| `TestCampaign` | `TestCampaign(saturate_workers=...)` | Overrides `bootstrap`  |
| `TestSuite`    | `TestSuite(saturate_workers=...)`    | Overrides the campaign |

Rule: **deepest wins**. From the Holy Book:

> It can also be enabled or disabled individually, either at suite level or at campaign level. In case of contradiction, the deepest element of the tree has the final word. For instance, if a campaign says to disable the option but a suite says to enable it, the suite takes precedence.

Mechanically, in `TestSuite.run`:

```python
resolved_saturate_workers = (
    self._saturate_workers
    if self._saturate_workers is not None
    else saturate_workers
)
```

If the suite has a non-None `_saturate_workers` (explicitly `True` or `False`), that wins. Otherwise the value the campaign passed down is used (and the campaign follows the same rule against bootstrap).

## Use case: surfacing concurrency issues

A suite with **a single test** + `--workers 3` + `saturate_workers=True`:

```
base_tests = [test_login]                 # 1 test
max_workers = 3
extras = [
    [COPY 1] test_login,                  # same factory, other wrapper
    [COPY 2] test_login,                  # same
]
tests = [test_login, [COPY 1] test_login, [COPY 2] test_login]
```

All 3 land on 3 _parallelized_ drivers. If `test_login` has a race condition (e.g. a local cache that isn't thread-safe), it shows up fast.

## Use case: maximize targeting

The Holy Book mentions:

> It's possible to temporarily create a suite with only one test to maximize targeting.

Pattern: **isolate** a problematic test in its own suite, set `--workers N`, leave `saturate_workers=True`. Clone N copies, hammer it, see what falls out.

## Use case: already-large data-driven tests

A suite with 12 data-driven tests and `--workers 3`: **no saturation**. `12 > 3` already, more tests than workers, the loop runs zero times.

```python
for _ in range(max_workers - len(base_tests)):   # range(3 - 12) = range(-9) = empty
    ...
```

## `[COPY 1]`, `[COPY 2]`, … vs `[+1]`, `[+2]`, …

`copy_indicator` is configurable:

```python
TestSuite(
    copy_indicator="+",
    put_space_after_copy_indicator=False,
    ...
)
```

→ Copies become `[+1] <name>`, `[+2] <name>`. That's what `ocarina-example`'s adapter does to keep logs tighter (see [`../../07-ocarina-example/02-adapters.md`](../../07-ocarina-example/02-adapters.md)).

## CI calls it out explicitly

`ocarina-with-ai-example`'s `CLAUDE.md`:

> With `--workers N`, Ocarina duplicates single-test suites up to N times to flush concurrency hazards (race conditions, session cleanup, driver reuse). The `[COPY N]` annotations are not noise&nbsp;—&nbsp;they confirm the saturation framework is active. Expect them on small smoke suites; this is a feature.
