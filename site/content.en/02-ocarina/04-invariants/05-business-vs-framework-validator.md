---
title: "02.04.05 — BusinessInvariantValidator vs FrameworkInvariantValidator"
description: "BusinessInvariantValidator and FrameworkInvariantValidator: two code-identical factories that exist purely to signal intent."
weight: 5
date: 2026-05-20
series: ["invariants"]
series_order: 5
tags: ["ocarina"]
---

# 02.04.05&nbsp;—&nbsp;`BusinessInvariantValidator` vs `FrameworkInvariantValidator`

> Two factories, identical code, exist purely **to signal intent**.

## Code

```python
class _BaseCustomInvariantValidator:
    @staticmethod
    def create[T](
        value: T,
        name: str,
        build_chain: Callable[[ValidationStartBlock[T], T], ValidationAssertBlock[T]],
    ) -> ValidationAssertBlock[T]:
        return _create_business_invariant_validator(
            value, name, lambda chain: build_chain(chain, value)
        )


@final
class BusinessInvariantValidator(_BaseCustomInvariantValidator):
    """Factory for creating business domain invariant validators.

    Use this for domain-specific validation logic (e.g., "user must be adult",
    "order total must match items").
    """


@final
class FrameworkInvariantValidator(_BaseCustomInvariantValidator):
    """Factory for creating framework-level invariant validators.

    Use this for technical/framework validation logic (e.g., "config must be valid",
    "test structure must be correct").
    """
```

```python
def _create_business_invariant_validator[T](
    value: T,
    name: str,
    build_chain: ValidationChainBuilder[T],
) -> ValidationAssertBlock[T]:
    start_block = validate(value, name=name)
    return build_chain(start_block)
```

## Why two classes?

1. `BusinessInvariantValidator` flags a business rule; `FrameworkInvariantValidator`, a technical framework rule. Intent jumps off the page.
2. **Grep**. `FrameworkInvariantValidator.create` finds _every framework invariant_ in one search. Same for business rules on the project side.
3. **Maintainability**. Want to add behavior (different log, different stack trace) to one or the other? Do it without touching every call-site.

## Usage

| Invariant                                                          | Category  | Where it lives                                                     |
| ------------------------------------------------------------------ | --------- | ------------------------------------------------------------------ |
| `validate_workers_amount`                                          | Framework | `src/ocarina/custom_invariants/testing/workers.py`                 |
| `validate_test_runners_ids`                                        | Framework | `src/ocarina/custom_invariants/testing/oc_test_runners_ids.py`     |
| `validate_test_runners_names`                                      | Framework | `src/ocarina/custom_invariants/testing/oc_test_runners_names.py`   |
| `validate_test_suites_names`                                       | Framework | `src/ocarina/custom_invariants/testing/oc_test_suites_names.py`    |
| `validate_test_campaigns_names`                                    | Framework | `src/ocarina/custom_invariants/testing/oc_test_campaigns_names.py` |
| `validate_test_cycle_name`                                         | Framework | `src/ocarina/custom_invariants/testing/oc_test_cycles_names.py`    |
| _Business example_: “the username must be on the whitelist”        | Business  | To be written on the user project side                             |
| _Business example_: “the booking date must be future and < 1 year” | Business  | To be written on the user project side                             |

## Full pattern

```python
# src/ocarina/custom_invariants/testing/workers.py
from ocarina.dsl.invariants.assertions import is_not_zero, is_positive
from ocarina.dsl.invariants.validate import FrameworkInvariantValidator


def _workers_amount_chain(
    chain: ValidationStartBlock[int],
    value: int,
) -> ValidationAssertBlock[int]:
    msg = f"Value Error: Number of workers must be at least 1 (got: {value})."
    return chain.assert_that(is_positive, msg=msg).assert_that(is_not_zero, msg=msg)


def validate_workers_amount(
    *, workers_amount: int, name: str
) -> ValidationAssertBlock[int]:
    """Validate that workers amount is at least 1."""
    return FrameworkInvariantValidator.create(
        workers_amount, name, _workers_amount_chain
    )
```

1. Private `_workers_amount_chain(chain, value) -> ValidationAssertBlock` defines the _what_.
2. Public `validate_workers_amount(*, workers_amount, name)` is the API and delegates to `FrameworkInvariantValidator.create`.
3. Caller in `TestSuite.run`: `validate_workers_amount(...).execute().raise_if_invalid()`.

## Which factory for which case

Holy Book (excerpt from the "Extensibility" chapter):

> Convention: `FrameworkInvariantValidator.create` for technical invariants, `BusinessInvariantValidator.create` for business rules.

| Rule                                                | Category              |
| --------------------------------------------------- | --------------------- |
| “`max_workers >= 1`”                                | Framework (technical) |
| “every test name is unique”                         | Framework             |
| “`DASH_PASSWORD` must not be empty”                 | Business              |
| “the booking date must be in the future”            | Business              |
| “`user.email` matches the internal company pattern” | Business              |

## Tacit rule: don't mix

The checker won't stop you from mixing; the convention will. If an invariant validates both a business rule and a technical one, **split it**. Sharper, more actionable error messages on aggregated failures.
