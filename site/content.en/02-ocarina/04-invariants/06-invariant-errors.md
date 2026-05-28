---
title: "02.04.06 — Invariant error hierarchy"
description: "Ocarina's invariant error hierarchy: InvariantViolationError, DuplicatesError and AggregateInvariantViolationError."
weight: 6
date: 2026-05-20
series: ["invariants"]
series_order: 6
tags: ["ocarina"]
---

# 02.04.06&nbsp;—&nbsp;Invariant error hierarchy

> Source file: [`src/ocarina/dsl/invariants/errors.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/errors.py)

```
InvariantViolationError (base — subclass of Exception)
├── DuplicatesError                  (raised by `has_unique_elements`)
└── AggregateInvariantViolationError (raised by `_ValidationResult.raise_if_invalid`)
```

## `InvariantViolationError`

```python
class InvariantViolationError(Exception):
    """Base exception raised when an invariant is violated."""
```

Bare `Exception` subclass, no extra logic. Every predicate raises this (or a subclass).

```python
try:
    validate(value).assert_that(predicate).execute().raise_if_invalid()
except InvariantViolationError as e:
    logger.error(f"Validation failed: {e}")
```

… catches **every** violation with a single clause.

## `DuplicatesError`

```python
class DuplicatesError(InvariantViolationError):
    def __init__(self, duplicates: Sequence[Any], message: str | None = None) -> None:
        self.duplicates = duplicates
        msg = message or "Duplicate elements detected:\n" + "\n".join(
            f" - {d}" for d in duplicates
        )
        super().__init__(msg)
```

- Stashes the duplicate list in `.duplicates`.
- Default message: "_Duplicate elements detected:`\n` - apple`\n` - banana_".
- Accepts a custom `message=`.

Raised by [`has_unique_elements`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/assertions.py).

## `AggregateInvariantViolationError`

```python
class AggregateInvariantViolationError(InvariantViolationError):
    def __init__(self, errors: Sequence[InvariantViolationError]) -> None:
        self.errors = errors
        count = len(errors)
        is_plural = count > 1
        if is_plural:
            message = f"{count} invariant violations occurred:\n" + "\n".join(
                f"› {e}" for e in errors
            )
        else:
            message = "Invariant violation occurred:\n" + "\n".join(
                f"› {e}" for e in errors
            )
        super().__init__(message)
```

1. **Auto singular/plural**: "_1 invariant violation occurred_" vs "_3 invariant violations occurred_."
2. **`›` (U+203A) prefix**. The `# noqa: RUF001 -> This is intentional.` in the source spells it out&nbsp;—&nbsp;ruff flags this unicode char because it can be confused with `>`. Author kept it on purpose: `›` is visually quieter.
3. **Original errors** stay accessible via `.errors`.

## Full invariant-failure cycles

### Case 1&nbsp;—&nbsp;Single-predicate failure

```
validate(workers_amount, name="max_workers")
    .assert_that(is_positive, msg="Number of workers must be at least 1.")
    .assert_that(is_not_zero, msg="Number of workers must be at least 1.")
    .execute()
    .raise_if_invalid()

  ┌─ workers_amount = 0
  │     │
  │     ▼ .assert_that(is_positive, msg=...)
  │  _ValidationChain.add_assertion(0, _PredicateWithMsg(is_positive, "..."), "max_workers")
  │     │
  │     ▼ .assert_that(is_not_zero, msg=...)
  │  _ValidationChain.add_assertion(0, _PredicateWithMsg(is_not_zero, "..."), "max_workers")
  │     │
  │     ▼ .execute()
  │  _ValidationChain.execute() :
  │     - step 1 : is_positive(0)        → OK (0 >= 0)
  │     - step 2 : is_not_zero(0)        → RAISES → InvariantViolationError("max_workers: ...")
  │     - errors = [exc1] ; is_valid = False
  │     │
  │     ▼ .raise_if_invalid()
  │  raise AggregateInvariantViolationError([exc1])
  └─► "Invariant violation occurred:\n› max_workers: Number of workers must be at least 1."
```

### Case 2&nbsp;—&nbsp;`otherwise` failure (all `_any_of` branches fail)

```
validate(age, name="age")
    .assert_that(is_equal_to(18), msg="Must be exactly 18")
    .otherwise(is_less_than_or_equal_to(65), msg="Or must be 65 or younger")
    .execute()
    .raise_if_invalid()

  ┌─ age = 70
  │     │
  │     ▼ .otherwise(...) → combined = _any_of(is_equal_to(18), is_less_than_or_equal_to(65))
  │     ▼ .execute()
  │     - combined(70) step :
  │           is_equal_to(18)(70)              → RAISES
  │           is_less_than_or_equal_to(65)(70) → RAISES
  │           all fail → InvariantViolationError("All predicates failed for value 70...")
  │     - errors = [exc_combined] ; is_valid = False
  │     │
  │     ▼ .raise_if_invalid()
  └─► "Invariant violation occurred:\n› age: All predicates failed for value 70.
       » At least one of the following conditions must be satisfied:
         | age: Must be exactly 18
         | age: Or must be 65 or younger"
```

### Case 3&nbsp;—&nbsp;Aggregated failure across multiple values via `.then(...)`

```
validate(user, name="user")
    .assert_that(is_not_none)
    .then(user.email, name="user.email")
    .assert_that(is_email)
    .then(user.age, name="user.age")
    .assert_that(is_positive)
    .execute()
    .raise_if_invalid()

  ┌─ user = User(email="not-an-email", age=-3)
  │     │
  │     ▼ .execute() (chain shared across all blocks)
  │     - step 1 : is_not_none(user)               → OK
  │     - step 2 : is_email("not-an-email")        → RAISES (exc_email)
  │     - step 3 : is_positive(-3)                 → RAISES (exc_age)
  │     - errors = [exc_email, exc_age] ; is_valid = False
  │     │
  │     ▼ .raise_if_invalid()
  └─► "2 invariant violations occurred:
       › user.email: 'not-an-email' must contain exactly one '@' character.
       › user.age: -3 is not positive."
```

## Link to the Allure taxonomy

> Note: the Allure taxonomy below applies to **Ocarina's internal unit tests** (covering the framework itself). It's not aimed at framework users, but they can **optionally crib it** for their own reports.

`categories.json` (see [`../01-identity.md`](../01-identity.md)):

```json
{
  "name": "Invariant violations",
  "matchedStatuses": ["failed"],
  "messageRegex": ".*InvariantViolationError.*"
}
```

Any internal test that raises an `InvariantViolationError`&nbsp;—&nbsp;directly or via aggregation&nbsp;—&nbsp;lands in the Allure category **Invariant violations**. You spot them at a glance in the HTML report.

## Why not an `assert` or a `ValueError`?

1. **`assert`** disappears under `python -O`. Unacceptable for runtime validation.
2. **`ValueError`** is too broad: you'd catch unrelated errors (e.g., `Path(...)` raising `ValueError` on an invalid path).
3. A dedicated class lets you **catch** precisely and **route** to the dedicated Allure category.

## _Explicitly_ raising an `InvariantViolationError`

```python
def is_my_business_rule(value: str) -> None:
    if not _my_check(value):
        raise InvariantViolationError(f"'{value}' violates rule X.")
```

That's the only exception you should raise. Anything else _escaping_ a predicate gets _propagated, not aggregated_&nbsp;—&nbsp;which breaks the aggregation invariant. So inside a predicate, **catch** whatever you need to catch and **re-raise** as `InvariantViolationError`.
