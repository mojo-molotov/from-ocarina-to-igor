---
title: "04.06 — Property-based testing (hypothesis)"
description: "A single file (test_invariants_properties.py), but the pattern is interesting: we generate inputs and verify universal properties of the invariant predicates."
weight: 6
date: 2026-05-20
series: ["internal-tests"]
series_order: 6
tags: ["invariants"]
---

# 04.06&nbsp;—&nbsp;Property-based testing (`hypothesis`)

> A single file (`test_invariants_properties.py`), but the pattern is interesting: we **generate** inputs and verify **universal properties** of the invariant predicates.

## The concept

`hypothesis` auto-generates _test cases_ that satisfy given constraints, then checks a property holds for every generated case. On failure, _hypothesis_ does **shrinking** to find the **smallest counter-example**.

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_is_positive_passes_on_positive(value):
    if value >= 0:
        is_positive(value)             # must not raise
    else:
        with pytest.raises(InvariantViolationError):
            is_positive(value)         # must raise
```

→ `hypothesis` generates integers (typically 100 by default), checks the property on each. _Unexpected_ exception → fail. The shrinker finds the smallest failing case (`0`? `-1`? `MIN_INT`?).

## Properties tested in Ocarina

The file `test_invariants_properties.py` covers several predicates:

| Predicate                    | Tested property                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| `is_positive(v)`             | passes iff `v >= 0`                                                                        |
| `is_not_zero(v)`             | passes iff `v != 0`                                                                        |
| `is_in(elements)(v)`         | passes iff `v in elements`                                                                 |
| `has_unique_elements()(seq)` | passes iff `len(seq) == len(set(seq))`                                                     |
| `is_iso_date_string(s)`      | passes iff `datetime.fromisoformat(s)` doesn't raise                                       |
| `is_email(s)`                | passes iff `s` matches the defined constraints (1 `@`, non-empty parts, `.` in the domain) |

## Why `hypothesis` rather than explicit tests

| Explicit tests                             | Hypothesis                                            |
| ------------------------------------------ | ----------------------------------------------------- |
| Covers the cases you thought of            | Covers the cases you _didn't_ think of                |
| If you miss an edge case, the test passes  | If an edge case exists, _hypothesis_ tends to find it |
| Maintenance: add an edge case = add a test | Maintenance: the property is stable                   |
| Documents _what works_                     | Documents _the mathematical property_                 |

## Hypothesis Statistics

```
=== Hypothesis Statistics ===

test_is_positive_passes_on_positive:
    - 100 passing examples, 0 failing examples, 0 invalid examples
    - Typical runtimes: 0-1 ms, ~ 50% in 0.0 ms
    - Shrinking events: 0
```

Shows how many examples were generated, the average time, and whether the shrinker fired.

## Failure

Say `is_positive` has a bug&nbsp;—&nbsp;accepts `-1` by mistake.

```
Falsifying example: test_is_positive_rejects_negative(value=-1)
```

`hypothesis` reports the exact failing input. No hunting needed.

## Limits

`hypothesis` does **not** replace functional tests; it complements them.

Very useful for:

- "_Pure_" functions (one input, one deterministic output).
- Invariants ("_this property holds for all `x`_").

Hence concentrated in `test_invariants_properties.py`.

## `--hypothesis-show-statistics`

```makefile
-pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
```

→ At the end of the run, you see the stats of every `@given(...)` invocation.

Lets you spot:

- Too many _invalid examples_ (poorly written strategy).
- Abnormal mean times (slow test).
- Too-frequent shrinking (flaky test, badly stated property).

## Fuzzing

`hypothesis` can also do _stateful testing_ (`RuleBasedStateMachine`)&nbsp;—&nbsp;generates sequences of actions on a mutable state. **Not used** in Ocarina.

- Main classes (`Test`, `TestSuite`) are _immutable_ or stateful in a strictly controlled way.
- The DSL is declarative.
