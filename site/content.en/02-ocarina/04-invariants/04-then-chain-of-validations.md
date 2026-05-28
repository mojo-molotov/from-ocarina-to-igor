---
title: "02.04.04 — .then(...) and chain_validations(...)"
description: "then and chain_validations: two mechanisms to compose several validations, change the validated type and keep the assertion chain."
weight: 4
date: 2026-05-20
series: ["invariants"]
series_order: 4
tags: ["ocarina"]
---

# 02.04.04&nbsp;—&nbsp;`.then(...)` and `chain_validations(...)`

> Two distinct mechanisms to compose multiple validations into one.

## `.then(new_value)`

```python
def then[U](self, new_value: U, *, name: str | None = None) -> ValidationStartBlock[U]:
    return ValidationStartBlock(new_value, self._chain, name)
```

1. **Switches the type** from `T` to `U`. The checker accepts the change.
2. **Keeps the chain** (`self._chain`). Past assertions stay in it; new ones _stack on top_.
3. **Swaps the `name`**: the `name` you pass to `.then()` is the one used for the next assertions, not the previous block's.

### Canonical use case

```python
validate(user, name="user")
    .assert_that(is_not_none)
    .then(user.email, name="user.email")
    .assert_that(is_email)
    .then(user.age, name="user.age")
    .assert_that(is_positive)
    .assert_that(is_less_than_or_equal_to(120))
    .execute()
    .raise_if_invalid()
```

Reads as: validate `user`, then `user.email`, then `user.age`. _All_ pass → OK. _One_ fails → every error rolls up into the `AggregateInvariantViolationError`.

Upside: one `.execute()`, one error message, one propagation. No need for three `validate(...).execute().raise_if_invalid()` calls.

### Subtlety

`_chain` is **shared by reference** across all blocks. Deliberate:

> The validation chain accumulator is mutable and shared across blocks in the same chain; blocks hold a reference to it, not a copy.

(Excerpt from the `validation_chain.py` intro docstring.)

That's what keeps `.then()` clean: no post-hoc recombination.

## `chain_validations(*)`

```python
def chain_validations(
    first: ValidationAssertBlock[Any],
    *rest: ValidationAssertBlock[Any],
) -> ValidationAssertBlock[Any]:
    merged_chain = _ValidationChain()
    merged_chain._merge_chain(first._chain)
    for block in rest:
        merged_chain._merge_chain(block._chain)
    return ValidationAssertBlock(first._value, merged_chain, first._name)
```

1. **Builds a new chain**. No mutation of the inputs.
2. **Merges in order**: steps from chain 1, then chain 2, then chain 3, etc.
3. **Returns a `ValidationAssertBlock`**: call `.execute()` on it.

### Use cases

```python
# Free-form example: pre-built independent validations
user_validation = validate(user, name="user").assert_that(is_not_none)
email_validation = validate(email, name="email").assert_that(is_email)
age_validation = validate(age, name="age").assert_that(is_positive)

chain_validations(user_validation, email_validation, age_validation).execute().raise_if_invalid()
```

```python
# In TestCycle.__init__
chain_validations(
    validate_test_cycle_name(cycle_name=name, name="test_cycle"),
    validate_campaigns_names(campaigns=all_campaigns, name="all campaigns (smoke + deep tests)"),
    validate_test_suites_names(suites=campaign._suites, name="suites"),
    validate_test_runners_names(tests=suite._tests, name="tests"),
).execute().raise_if_invalid()
```

## `.then()` vs `chain_validations(*)`

| Criterion      | `.then()`                                                     | `chain_validations()`                                                                                   |
| -------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| When to use it | Several **related** values (`user`, `user.email`, `user.age`) | Several **independent** validations already constructed                                                 |
| Style          | Linear in a single chain                                      | After-the-fact composition                                                                              |
| Mutation       | Mutates the underlying chain                                  | Creates a new chain (no mutation)                                                                       |
| Return type    | `ValidationStartBlock[U]`                                     | `ValidationAssertBlock[Any]`                                                                            |
| Use case       | Validating a dataclass and its fields                         | Validating the framework's invariants inside a `TestCycle` constructor, or a complex business invariant |

## Type tests

[`tests/dsl/invariants/test_types.yml`](https://github.com/mojo-molotov/ocarina/blob/main/tests/dsl/invariants/test_types.yml) contains:

```yaml
- case: then_allows_type_change
  description: .then() should allow switching to a different type in the validation chain
  main: |
    validate(42).assert_that(is_positive).then("email@test.com").assert_that(is_email)
```

The checker accepts moving from `int` to `str` via `.then()`, but rejects an assertion whose type doesn't match the current value:

```python
validate(42).assert_that(is_email)
#                        ^^^^^^^^
# error: Argument 1 to "assert_that" has incompatible type
#   "Callable[[str], None]"; expected "Callable[[int], None]"
```
