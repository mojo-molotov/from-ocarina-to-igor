---
title: "02.04.01 — The validate → assert_that → execute → raise_if_invalid flow"
description: "The validate, assert_that, execute, raise_if_invalid flow: the state machine of Ocarina's typed invariants sub-DSL."
weight: 1
date: 2026-05-20
series: ["invariants"]
series_order: 1
tags: ["ocarina"]
---

# 02.04.01&nbsp;—&nbsp;The `validate → assert_that → execute → raise_if_invalid` flow

> Source file: [`src/ocarina/dsl/invariants/validate.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/validate.py) (entry-point) + [`src/ocarina/dsl/invariants/internals/validation_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/internals/validation_chain.py)

## The state machine

### Diagram

```
validate(value: T)
       │
       ▼
ValidationStartBlock[T]
       │
       └─ assert_that(predicate, *, msg=None)
              │
              ▼
       ValidationAssertBlock[T]   ← state accepting several continuations
              │
              ├─► assert_that(P)     [loop, AND-chainable, see dedicated diagram]
              ├─► otherwise(P)       [OR, see 03-otherwise-any-of.md]
              ├─► then(U, name=...)  [value swap, see 04-then-chain-of-validations.md]
              └─► execute()          → _ValidationResult
                                          │
                                          ├─ is_valid: bool
                                          ├─ errors: Sequence[InvariantViolationError]
                                          ├─ validated_values: Sequence[Any]
                                          └─ raise_if_invalid() : None | raise AggregateInvariantViolationError
```

### `assert_that` loop

`assert_that` declares **one** assertion on the current value. Multiple `assert_that` calls chain&nbsp;—&nbsp;each adds another condition (logical AND, order preserved).

```
ValidationAssertBlock[T] ──assert_that(P)──► ValidationAssertBlock[T]
                ▲                                       │
                └───────────────────────────────────────┘
                  (chain as many times as you want)
```

### `otherwise` branching

`otherwise` swaps the _last_ failed predicate for an alternative. Details in [`03-otherwise-any-of.md`](03-otherwise-any-of.md) (and `any_of`, the generalized form).

```
ValidationAssertBlock[T] ──assert_that(P_last)──► ...
        │
        └── otherwise(P_alt)
             └─► ValidationAssertBlock[T]   (P_alt replaces P_last)
```

### Value swap with `then`

`then(new_value)` jumps back to `ValidationStartBlock` with a **new** value, still inside the same chain. See [`04-then-chain-of-validations.md`](04-then-chain-of-validations.md).

```
ValidationAssertBlock[T] ──then(U, name=...)──► ValidationStartBlock[U]
```

## Code

### `validate` (entry-point)

```python
def validate[T](value: T, *, name: str | None = None) -> ValidationStartBlock[T]:
    return ValidationStartBlock(value, name=name)
```

Plain factory. The `name=` prefixes error messages ("`email: …`").

### `ValidationStartBlock.assert_that`

```python
def assert_that(self, predicate: Predicate[T], *, msg: str | None = None) -> ValidationAssertBlock[T]:
    predicate = _with_msg(predicate, msg, self._name)
    self._chain.add_assertion(self._value, predicate, self._name)
    return ValidationAssertBlock(self._value, self._chain, self._name, last_predicate=predicate)
```

1. **Predicate wrap**: `_with_msg` wraps it with an optional custom message and name. On failure, the custom message replaces the default one.
2. **Append to `_ValidationChain`**: the chain stacks `(value, name, predicate)` tuples.
3. **State transition**: returns a `ValidationAssertBlock` that remembers `last_predicate` (for `.otherwise(...)`).

### `_PredicateWithMsg`

```python
@final
class _PredicateWithMsg[T]:
    def __init__(self, predicate: Predicate[T], msg: str | None = None) -> None:
        self.predicate = predicate
        self.msg = msg

    def __call__(self, value: T) -> None:
        try:
            self.predicate(value)
        except InvariantViolationError as exc:
            if self.msg:
                raise InvariantViolationError(self.msg) from exc
            raise
```

A _wrapper_ that **refines** the `InvariantViolationError` with the custom message if provided. The error fires either way&nbsp;—&nbsp;we just polish it before it propagates.

### `_ValidationChain.execute`

```python
def execute(self) -> _ValidationResult:
    def run_step(value, predicate_with_msg):
        try:
            predicate_with_msg(value)
        except InvariantViolationError as exc:
            return False, exc
        else:
            return True, value

    errors = []
    validated = []
    for value, _, predicate_with_msg in self._steps:
        success, outcome = run_step(value, predicate_with_msg)
        if success:
            validated.append(outcome)
        else:
            errors.append(outcome)
    return _ValidationResult(
        is_valid=(len(errors) == 0),
        errors=errors,
        validated_values=validated,
    )
```

Mechanic: **every step runs**, no _fail-fast_. Errors stack up in one list, validated values in another. That's why this DSL fits CLIs so well: the user sees every error at once, not one drip at a time.

### `_ValidationResult.raise_if_invalid`

```python
def raise_if_invalid(self) -> None:
    if not self.is_valid:
        raise AggregateInvariantViolationError(self.errors)
```

The only way to _raise_ the collected errors. Skip the call and the result stays quiet&nbsp;—&nbsp;handy when you want to read `.errors` yourself.

## `AggregateInvariantViolationError`

```python
def __init__(self, errors: Sequence[InvariantViolationError]) -> None:
    self.errors = errors
    count = len(errors)
    is_plural = count > 1
    if is_plural:
        message = f"{count} invariant violations occurred:\n" + "\n".join(f"› {e}" for e in errors)
    else:
        message = "Invariant violation occurred:\n" + "\n".join(f"› {e}" for e in errors)
    super().__init__(message)
```

Formatting handles singular vs plural automatically ("_1 invariant violation occurred_" vs "_3 invariant violations occurred_").

## Example

```python
from ocarina.dsl.invariants.validate import validate
from ocarina.dsl.invariants.assertions import is_str, is_email

validate(email, name="email")
    .assert_that(is_str)
    .assert_that(is_email)
    .execute()
    .raise_if_invalid()
```

- `email` gets validated _twice_ (both assertions run).
- _Both_ fail → `AggregateInvariantViolationError` raised with **both messages**.
- _Neither_ fails → `.raise_if_invalid()` is a no-op.

## CLI

The CLI validator uses this DSL:

```python
# create_cli_store.py
"workers": field(
    validate=lambda chain: chain.assert_that(is_positive, msg="--workers should be a positive value")
                                .assert_that(is_not_zero, msg="--workers should not be zero")
),
```

And in `CliStore.set` (`store.py`):

```python
def set(self, value: T) -> None:
    if not isinstance(self._value, _Unset):
        raise RuntimeError("Value already set.")
    self._validate(_validate(value)).execute().raise_if_invalid()
    self._value = value
```

**Same** DSL. No _ad hoc_ validation, no parallel system. Invariant composition is the framework's only validation language.

## Use by `custom_invariants/testing/`

```python
# custom_invariants/testing/workers.py
def _workers_amount_chain(chain: ValidationStartBlock[int], value: int) -> ValidationAssertBlock[int]:
    msg = f"Value Error: Number of workers must be at least 1 (got: {value})."
    return chain.assert_that(is_positive, msg=msg).assert_that(is_not_zero, msg=msg)

def validate_workers_amount(*, workers_amount: int, name: str) -> ValidationAssertBlock[int]:
    return FrameworkInvariantValidator.create(workers_amount, name, _workers_amount_chain)
```

And in `TestSuite.run`:

```python
validate_workers_amount(workers_amount=max_workers, name="max_workers").execute().raise_if_invalid()
```

Before the pool warms up, before any thread starts, `max_workers <= 0` gets cleanly _rejected_.
