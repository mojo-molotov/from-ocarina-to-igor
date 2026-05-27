---
title: "04.04 — Static typing tests (pytest-mypy-plugins)"
description: "Five *test_types.yml files that test the checker's behavior. A testing dimension unique to Ocarina in its way: we make sure that what should be a mypy error actually is one."
weight: 4
date: 2026-05-20
series: ["internal-tests"]
series_order: 4
tags: ["typing"]
---

# 04.04&nbsp;—&nbsp;_Static typing_ tests (`pytest-mypy-plugins`)

> Five `*test_types.yml` files that test _the checker's behavior_. A testing dimension **unique** to Ocarina in its way: we make sure that what _should_ be a _mypy_ error actually is one.

## Listing

```
tests/
├── dsl/
│   ├── invariants/test_types.yml
│   └── testing_with_railway/test_types.yml
└── opinionated/
    ├── cli/test_types.yml
    ├── infra/test_types.yml
    └── plugins/reports/...   (snapshots — not YAML)
```

## YAML

```yaml
- case: compatible_predicate_types
  description: Predicates should accept values of compatible types
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_email, is_positive

    validate(1234).assert_that(is_positive)
    validate("a@a.com").assert_that(is_email)
```

Without `out:` → we expect `mypy` to pass **without error** on the given code.

```yaml
- case: incompatible_predicate_types
  description: Predicates should reject values of incompatible types
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_positive

    validate("lol").assert_that(is_positive)
  out: |
    main:4: error: Argument 1 to "assert_that" of "ValidationStartBlock" has incompatible type "Callable[[float], None]"; expected "Callable[[str], None]"  [arg-type]
```

With `out:` → we expect this _exact_ error message from _mypy_.

## Sample tested cases (invariants)

```yaml
- case: generics_preserved_through_chain
  description: Generic type parameter T should be preserved across validation chain
  regex: true
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_positive

    result = validate(42).assert_that(is_positive)
    reveal_type(result)
  out: |
    main:5: note: Revealed type is .*ValidationAssertBlock\[.*int.*\]

- case: then_allows_type_change
  description: .then() should allow switching to a different type in the validation chain
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_positive, is_email

    validate(42).assert_that(is_positive).then("email@test.com").assert_that(is_email)

- case: otherwise_with_same_type
  description: .otherwise() should accept predicates of the same type
  main: |
    from ocarina.dsl.invariants.validate import validate
    from ocarina.dsl.invariants.assertions import is_positive, is_not_zero

    validate(5).assert_that(is_positive).otherwise(is_not_zero)

- case: multiple_otherwise_preserves_type
  description: Multiple .otherwise() calls should preserve the same type throughout
  main: |
    validate(5) \
        .assert_that(is_equal_to(10)) \
        .otherwise(is_equal_to(20)) \
        .otherwise(is_positive) \
        .otherwise(is_not_zero)

- case: execute_returns_result_type
  description: .execute() should return ValidationResult regardless of validated type
  ...
```

## Sample tested cases (testing_with_railway)

```yaml
- case: act_preserves_TPOM
  description: act(pom: TPOM, action) preserves TPOM through the chain
  regex: true
  main: |
    from selenium.webdriver.remote.webdriver import WebDriver
    from ocarina.dsl.testing_with_railway.constructors.create_act import create_act

    class HomePage:
        def click(self) -> "HomePage": return self
        def get_current_title(self) -> str: return ""
        def verify(self): return self

    pom = HomePage()
    result = create_act(pom, lambda p: p.click())
    reveal_type(result)
  out: |
    main: note: Revealed type is .*ActionStart\[HomePage\]

- case: drive_page_refuses_heterogenous_TPOMs
  description: drive_page enforces TPOM uniformity at the type level
  main: |
    ...  # mixing HomePage + DashboardPage in the same drive_page
  out: |
    main: error: Expected type 'ActionSuccess\[HomePage\]'; got 'ActionSuccess\[DashboardPage\]'
```

## Why test typing

### 1. The DSL's safety **depends on** typing

The `ActionStart → ActionFailure → ActionSuccess → ActionChain` state machine is secured _by typing_. A regression in the DSL code that breaks this property has to surface. A runtime test isn't enough&nbsp;—&nbsp;we need a test on the checker.

### 2. `reveal_type`s document the inferences

A `reveal_type(result)` in a YAML test tells you exactly what _mypy_ infers. These tests **document** the expected inferences.

### 3. Refactor safety

A contributor refactors `validate` and breaks `T` preservation → the YAML type test catches it. No need to re-read every user scenario to notice the checker is letting through things it should reject.

## Invocation by pytest

```
pytest tests/dsl/invariants/test_types.yml
```

The `pytest-mypy-plugins` plugin loads the YAML, runs each `case`:

1. Creates a Python file with the contents of `main`.
2. Runs _mypy_ on it.
3. Compares the output to the `out` field (or expects nothing if `out` is absent).
4. PASS/FAIL accordingly.

## `regex: true`

With `regex: true` in the `case`, `out:` is interpreted as a regex (not a literal string). Catches messages like:

```yaml
out: |
  main: note: Revealed type is .*ValidationAssertBlock\[.*int.*\]
```

The `.*int.*` absorbs variations in _mypy_'s formatting (which shows `int`, `Literal[42]`, `builtins.int*`, etc. depending on version).

## DSL tested dynamically and statically

Any change to `validate.py`, `assertions.py`, `validation_chain.py`, `action_chain.py`, `chain_actions.py`, `match_page.py`, `create_act.py` must pass:

- The pytest scenario tests (~behavior).
- The cram tests (CLI).
- **The YAML mypy tests** (~typing).

That's what makes the DSL **stable**: you can't break it at _any_ level without a red test flagging it.

## The omission on the `pyproject.toml` side

```toml
[tool.coverage.run]
omit = [
    ...
    "src/ocarina/custom_types/*",
    "src/ocarina/ports/*",
    "src/ocarina/opinionated/cli/phantoms.py",
    ...
]
```

These _shape_ files aren't in pytest's coverage (detection runs on dynamically executed code; coverage doesn't account for static tests).

Coverage here is brought **by the `pytest-mypy-plugins` (YAML) tests.**
