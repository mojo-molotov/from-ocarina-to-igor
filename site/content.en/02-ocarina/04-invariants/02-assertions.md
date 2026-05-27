---
title: "02.04.02 — Catalog of builtin assertions"
description: "Source file: src/ocarina/dsl/invariants/assertions.py — ~25 predicates."
weight: 2
date: 2026-05-20
series: ["invariants"]
series_order: 2
tags: ["ocarina"]
---

# 02.04.02&nbsp;—&nbsp;Catalog of builtin assertions

> Source file: [`src/ocarina/dsl/invariants/assertions.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/assertions.py)&nbsp;—&nbsp;~25 predicates.

Every assertion follows the **same contract**:

- A direct predicate `(value: T) -> None` that raises `InvariantViolationError` on contract violation.
- Or a **closure** when you need a config argument (`is_equal_to(cmp)`, etc.).
- Or, occasionally, a **higher-order function (HOF)** like `each`. Lives here pragmatically&nbsp;—&nbsp;a dedicated file for a single case would be overkill.

## Full table

| Assertion                          | Direct / closure / HOF | Domain          | Description                                                                                             |
| ---------------------------------- | ---------------------- | --------------- | ------------------------------------------------------------------------------------------------------- |
| `is_str(value)`                    | direct                 | `Any`           | Raises if `value` is not a `str`                                                                        |
| `is_none(value)`                   | direct                 | `Any`           | Raises if `value is not None`                                                                           |
| `is_not_none(value)`               | direct                 | `Any`           | Raises if `value is None`                                                                               |
| `is_equal_to(cmp)`                 | closure                | `Any`           | Returns `(value) -> None` that raises if `value != cmp`                                                 |
| `is_not_equal_to(cmp)`             | closure                | `Any`           | Returns `(value) -> None` that raises if `value == cmp`                                                 |
| `is_less_than(cmp)`                | closure                | `float`         | `value < cmp`                                                                                           |
| `is_less_than_or_equal_to(cmp)`    | closure                | `float`         | `value <= cmp`                                                                                          |
| `is_greater_than(cmp)`             | closure                | `float`         | `value > cmp`                                                                                           |
| `is_greater_than_or_equal_to(cmp)` | closure                | `float`         | `value >= cmp`                                                                                          |
| `is_positive(value)`               | direct                 | `float`         | `value >= 0`                                                                                            |
| `is_not_zero(value)`               | direct                 | `float`         | `value != 0`                                                                                            |
| `is_in(elements)`                  | closure                | `Any`           | `value in tuple(elements)`                                                                              |
| `is_file(value)`                   | direct                 | `str \| Path`   | `Path(value).is_file()`                                                                                 |
| `is_dir(value)`                    | direct                 | `str \| Path`   | `Path(value).is_dir()`                                                                                  |
| `is_iso_date_string(value)`        | direct                 | `str`           | `datetime.fromisoformat(value)`                                                                         |
| `is_iso_utc_date_string(value)`    | direct                 | `str`           | Checks ISO + `tzinfo == UTC`                                                                            |
| `is_email(value)`                  | direct                 | `str`           | No whitespace, exactly one `@`, non-empty parts, domain contains `.`                                    |
| `has_unique_elements(*, key=None)` | closure                | `Iterable[Any]` | Detects duplicates (raises `DuplicatesError`). Type-strict (`1 ≠ True`), supports unhashables.          |
| `is_empty(value)`                  | direct                 | `Sized`         | `len(value) == 0`                                                                                       |
| `is_truthy(value)`                 | direct                 | `Any`           | `bool(value) is True`                                                                                   |
| `is_valid_filename(value)`         | direct                 | `str`           | Cross-platform: forbidden chars, Windows reserved words, no leading/trailing space or dot, length ≤ 255 |
| `each(predicate)`                  | **HOF**                | `Iterable[Any]` | Applies `predicate` to each element                                                                     |

## A few implementations in detail

### `is_email`

```python
def is_email(value: str) -> None:
    """Assert that the string is a valid email address (fast check)."""
    if " " in value:
        raise InvariantViolationError(f"'{value}' must not contain whitespace.")
    if value.count("@") != 1:
        raise InvariantViolationError(f"'{value}' must contain exactly one '@' character.")
    local_part, domain_part = value.split("@")
    if not local_part or not domain_part:
        raise InvariantViolationError(f"'{value}' must have non-empty local and domain parts.")
    if "." not in domain_part:
        raise InvariantViolationError(f"Domain part of '{value}' must contain at least one '.'.")
```

Four bare-minimum checks. No RFC 5322 regex. Deliberate: real email validation happens by _sending_ an email, not by regex.

### `has_unique_elements`

```python
def has_unique_elements(*, key: Callable[[Any], Any] | None = None):
    def unwrapped(value: Iterable[Any]) -> None:
        items = list(value)
        key_fn = key or (lambda x: x)

        seen: list[tuple[type, Any]] = []
        duplicates = []

        for item in items:
            keyed = key_fn(item)
            typed_key = (type(keyed), keyed)

            found = False
            for seen_key in seen:
                if typed_key[0] == seen_key[0] and typed_key[1] == seen_key[1]:
                    found = True
                    if keyed not in duplicates:
                        duplicates.append(keyed)
                    break

            if not found:
                seen.append(typed_key)

        if duplicates:
            raise DuplicatesError(duplicates)
    return unwrapped
```

1. **Type-strict**: `(type(keyed), keyed)` is the comparison key. So `1`, `1.0`, and `True` are _different_. Idiomatic Python says `1 == True`, but here we don't care&nbsp;—&nbsp;we want to distinguish them.
2. **Handles unhashables**: list-based comparison, O(n²) instead of using a set. Hashables still work fine (`list`, `dict`, `set` as values are OK).
3. **Raises `DuplicatesError`**: subclass of `InvariantViolationError`, formats the duplicates list cleanly.

Used to validate uniqueness of test names / IDs.

### `is_valid_filename`

```python
def is_valid_filename(value: str) -> None:
    _forbidden_chars = re.compile(r'[\x00-\x1f\\/:*?"<>|]')
    _windows_reserved = re.compile(
        r"^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$", re.IGNORECASE
    )

    if not value:
        raise InvariantViolationError("Filename must not be empty.")
    if len(value) > 255:
        raise InvariantViolationError(f"Filename '{value}' exceeds 255 characters.")
    if _forbidden_chars.search(value):
        raise InvariantViolationError(
            f"Filename '{value}' contains forbidden characters "
            '(control chars or one of: \\ / : * ? " < > |).'
        )
    if value[0] in (".", " ") or value[-1] in (".", " "):
        raise InvariantViolationError(f"Filename '{value}' must not start or end with a dot or a space.")

    stem = value.split(".", 1)[0]
    if _windows_reserved.match(stem):
        raise InvariantViolationError(f"Filename '{value}' uses a reserved Windows device name.")
```

1. Forbidden chars (control + `\ / : * ? " < > |`)
2. No leading/trailing `.` or ` `
3. No Windows-reserved name (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`)
4. Length between 1 and 255

Used to validate test names. **Every test produces a .log file** whose name comes straight from the test name. See [`validate_test_runners_names`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_invariants/testing/oc_test_runners_names.py).

### `is_iso_utc_date_string`

```python
def is_iso_utc_date_string(value: str) -> None:
    try:
        dt = datetime.fromisoformat(value)
    except Exception as exc:
        raise InvariantViolationError(f"'{value}' is not a valid ISO date string.") from exc
    if dt.tzinfo != UTC:
        raise InvariantViolationError(f"'{value}' is not in UTC (tz={dt.tzinfo}).")
```

Accepts `"2025-12-18T10:30:00+00:00"`, `"2025-12-18T10:30:00Z"`. Rejects `"2025-12-18"` (no timezone) and `"2025-12-18T10:30:00+02:00"` (not UTC).

Used on the `ocarina-example` side to validate `OTP_CACHE_DATE` pulled from the L1 cache.

### `each`

```python
def each(predicate: Predicate[Any]) -> Predicate[Iterable[Any]]:
    def unwrapped(value: Iterable[Any]) -> None:
        for item in value:
            predicate(item)
    return unwrapped
```

```python
validate(filenames).assert_that(each(is_valid_filename)).execute().raise_if_invalid()
```

## How to write your own predicate

Direct case:

```python
def is_str(value: Any) -> None:
    if not isinstance(value, str):
        raise InvariantViolationError("Expected value to be string.")
```

Parameterized case:

```python
def is_equal_to(cmp: Any) -> Predicate[Any]:
    def unwrapped(value: Any) -> None:
        if value != cmp:
            raise InvariantViolationError(f"{value} is not equal to {cmp}.")
    return unwrapped
```

1. Raise **`InvariantViolationError`**&nbsp;—&nbsp;nothing else.
2. The message has to be **diagnosable**: include `value`, `cmp`, useful context.
3. A predicate is a `Callable[[T], None]`.
