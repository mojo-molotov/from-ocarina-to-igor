---
title: "02.04.03 — .otherwise(...) and _any_of"
description: "How Ocarina expresses a logical OR between two predicates without breaking error aggregation."
weight: 3
date: 2026-05-20
series: ["invariants"]
series_order: 3
tags: ["ocarina"]
---

# 02.04.03&nbsp;—&nbsp;`.otherwise(...)` and `_any_of`

> How Ocarina expresses a **logical OR** between two predicates without breaking error aggregation.

## The problem

Concrete case: you want "`age == 18` OR `age <= 65`." The ROP/invariants syntax is a strict chain of assertions, and every `.assert_that()` is an AND. How do you express an OR?

## Code

```python
def otherwise(self, fallback: Predicate[T], *, msg: str | None = None) -> ValidationAssertBlock[T]:
    if self._last_predicate is None:
        raise RuntimeError("otherwise() must follow assert_that().")

    fallback_with_msg = _with_msg(fallback, msg, self._name)
    combined = _any_of(
        self._last_predicate, *([*self._otherwise_predicates, fallback_with_msg])
    )
    self._chain._steps.pop()                    # replace the last step
    self._chain.add_assertion(self._value, combined, self._name)
    self._last_predicate = combined
    self._otherwise_predicates.append(fallback_with_msg)
    return self
```

1. **Guard**: `otherwise()` has to follow an `assert_that()`. With no prior predicate it raises. (In practice the type-checker already rules it out&nbsp;—&nbsp;`ValidationStartBlock.otherwise` doesn't exist.)
2. **Combination**: combine previous predicate + all accumulated `otherwise` predicates + the new one, via `_any_of`. Result: a composite predicate.
3. **Step replacement**: _pop_ the last step from `_ValidationChain` and _push_ the combined one. Otherwise the original predicate AND the combined one would both be present, and the original error would resurface.

## `_any_of`

```python
def _any_of[T](*predicates: _PredicateWithMsg[T]) -> _PredicateWithMsg[T]:
    def _try_predicate(p: _PredicateWithMsg[T], value: T) -> InvariantViolationError | None:
        try:
            p(value)
        except InvariantViolationError as exc:
            return exc
        else:
            return None

    def combined(value: T) -> None:
        errors = []
        for p in predicates:
            error = _try_predicate(p, value)
            if error is None:
                return                              # ✅ one predicate passes → all pass
            errors.append(error)

        formatted_error_messages = "  | " + "\n  | ".join(str(e) for e in errors)
        msg = (
            f"All predicates failed for value {value!r}.\n"
            "» At least one of the following conditions must be satisfied:\n"
            f"{formatted_error_messages}"
        )
        raise InvariantViolationError(msg)

    return _PredicateWithMsg(combined)
```

1. **First success wins**: the moment one predicate passes, `combined` returns `None`.
2. **All fail**: build an _aggregated_ message listing **every** failure, separated by `|`.
3. **Result is a `_PredicateWithMsg`**: plug it back into the chain like any other predicate.
4. **Aggregation is recursive**: 3 successive `otherwise()` calls fold `(P_orig OR P_otherwise1 OR P_otherwise2 OR P_otherwise3)` into one predicate.

## Example

```python
validate(age, name="age")
    .assert_that(is_equal_to(18), msg="Must be 18 or at most 65")
    .otherwise(is_less_than_or_equal_to(65), msg="Must be 18 or at most 65")
    .execute()
    .raise_if_invalid()
```

1. If `age == 18`: `is_equal_to(18)` passes → OK.
2. If `age == 30`: `is_equal_to(18)` raises, `is_less_than_or_equal_to(65)` passes → OK.
3. If `age == 70`: both raise → `InvariantViolationError` with:

```
age: All predicates failed for value 70.
» At least one of the following conditions must be satisfied:
  | age: Must be 18 or at most 65
  | age: Must be 18 or at most 65
```

(The duplicated message comes from passing the same `msg=` twice. Intentional here&nbsp;—&nbsp;we _want_ a single statement of intent.)

For a cleaner error (one statement of the contract that actually _diagnoses_ what broke), split the `msg=`:

```python
validate(age, name="age")
    .assert_that(is_equal_to(18), msg="Must be exactly 18")
    .otherwise(is_less_than_or_equal_to(65), msg="Can be 65 or younger")
    .execute()
    .raise_if_invalid()
```

`age == 70`:

```
age: All predicates failed for value 70.
» At least one of the following conditions must be satisfied:
  | age: Must be exactly 18
  | age: Can be 65 or younger
```

## Multi-otherwise example

```python
validate(age, name="age")
    .assert_that(is_equal_to(18), msg="Must be 18")
    .otherwise(is_equal_to(21), msg="Or must be 21")
    .otherwise(is_equal_to(65), msg="Or must be 65")
    .execute()
```

`age == 30`:

```
age: All predicates failed for value 30.
» At least one of the following conditions must be satisfied:
  | age: Must be 18
  | age: Or must be 21
  | age: Or must be 65
```

## On the CLI side

```python
"profile_path": field(
    validate=lambda chain: chain.assert_that(is_none, msg="Maybe you could omit --profile-path")
                                .otherwise(is_dir,    msg="--profile-path should be a path to a directory")
),
```

Reads as: `profile_path` is valid if it's `None`, or if it points to a directory.

## Related type tests

[`tests/dsl/invariants/test_types.yml`](https://github.com/mojo-molotov/ocarina/blob/main/tests/dsl/invariants/test_types.yml):

```yaml
- case: otherwise_with_same_type
  description: .otherwise() should accept predicates of the same type
  main: |
    validate(5).assert_that(is_positive).otherwise(is_not_zero)

- case: multiple_otherwise_preserves_type
  description: Multiple .otherwise() calls should preserve the same type throughout
  main: |
    validate(5) \
        .assert_that(is_equal_to(10)) \
        .otherwise(is_equal_to(20)) \
        .otherwise(is_positive) \
        .otherwise(is_not_zero)
```

The type holds throughout. Mixing a `Predicate[int]` with a `Predicate[str]` in the same chain won't compile.
