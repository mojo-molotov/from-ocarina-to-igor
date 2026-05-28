---
title: "08.06 — Data gaps (G-DATA-1, G-DATA-2)"
description: "The two CURA data-integrity gaps, including the missing server-side validation of the visit date, documented by ocarina-with-ai-example."
weight: 6
date: 2026-05-20
series: ["ai-example"]
series_order: 6
---

# 08.06&nbsp;—&nbsp;Data gaps (G-DATA-1, G-DATA-2)

> Two major gaps on data integrity.

## G-DATA-1&nbsp;—&nbsp;No server-side validation of `visit_date`

### Source

```php
// appointment.php
array_diff_key($_POST, array(
    "facility" => "",
    "hospital_readmission" => "",
    "programs" => "",
    "visit_date" => "",
    "comment" => ""
))
```

This checks for key presence only. It **never** validates the value of `visit_date`.

### Symptom

1. **Empty visit_date**: if you strip the HTML5 `required` attribute via JS and submit with an empty date → booking accepted.
2. **Past visit_date**: if you send a backdated booking → booking accepted.
3. The booking is added to history as-is.

### Related tests

| Test                                                                 | Method                                                                                                |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `Appointment - Server accepts empty date when client bypass applied` | Strip the `required` attribute, send with empty booking date → expects rejection by the system (FAIL) |
| `Appointment - Past date booking accepted`                           | Send a booking request for yesterday → expects rejection by the system (FAIL)                         |

Both tests **fail intentionally**&nbsp;—&nbsp;they document the gap.

### "_Past date booking_"

```python
# src/tests/scenarios/appointment/past_date_booking.py
"""Past-date booking accepted — no temporal validation (§9.7 gap).

Flow:
  open appointment form → fill (facility, program, comment, date = yesterday) → submit
  → verify NOT confirmed
  (intentional FAIL — CURA accepts past dates, §9.7 gap)

A healthcare scheduling system must not accept bookings for dates that have
already passed. CURA performs no temporal validation: yesterday's date is
accepted and a confirmation is returned. The test asserts rejection and fails
when the confirmation appears.

Pre-fragments: login_as_demo_user
Post-fragments: (none)
"""

def _scenario_past_date_booking(driver, logger) -> TestChain:
    on_appointment = AppointmentPage(driver=driver)
    on_confirmation = ConfirmationPage(driver=driver)

    log_error = create_just_log_error(logger=logger)
    log_success = create_just_log_success(logger=logger)
    log_and_screenshot = create_log_success_and_take_screenshot(driver=driver, logger=logger)

    return [
        drive_page(
            act(on_appointment, open_appointment_page)
                .failure(log_error("Failed to open appointment form"))
                .success(log_success("Opened appointment form")),
            act(on_appointment, fill_appointment(
                facility="Hongkong CURA Healthcare Center",
                programs="Medicare",
                visit_date=in_days(-1),                    # ← yesterday
                comment="Past-date booking attempt",
            ))
                .failure(log_error("Failed to fill form"))
                .success(log_and_screenshot("Filled form with past date")),
            act(on_appointment, submit_appointment)
                .failure(log_error("Failed to submit"))
                .success(log_success("Submitted")),
        ),
        drive_page(
            act(on_confirmation, verify_booking_not_confirmed)
                .failure(log_error("CURA accepted past date — §9.7 gap"))
                .success(log_and_screenshot("Rejection confirmed")),
        ),
    ]
```

- `verify_booking_not_confirmed` succeeds if we stayed on `/appointment.php` (= rejection).
- If redirected to `/confirmation.php` (= acceptance), it raises → `.failure()` logs "CURA accepted past date&nbsp;—&nbsp;§9.7 gap".

### `verify_booking_not_confirmed`

```python
# pages/confirmation.py
_NOT_CONFIRMED_TIMEOUT = 10                    # ← fixed, independent of --wait-timeout

class ConfirmationPage(...):
    def verify_booking_not_confirmed(self) -> ConfirmationPage:
        try:
            WebDriverWait(self._driver, _NOT_CONFIRMED_TIMEOUT).until(
                ec.url_contains("appointment.php")
            )
            return self                          # ✅ we stayed on appointment → rejection
        except TimeoutException as exc:
            raise BookingNotRejectedError(
                f"CURA accepted the booking (url: {self._driver.current_url}); §9.7 gap"
            ) from exc
```

1. **`url_contains("appointment.php")`**: URL-based, not DOM-based&nbsp;—&nbsp;matches CURA's actual behavior.
2. **`_NOT_CONFIRMED_TIMEOUT = 10`**: fixed at 10s, independent of `--wait-timeout`.
3. **`BookingNotRejectedError`**: a specific exception&nbsp;—&nbsp;not `AssertionError`, not `TimeoutException`. This is not a flake.

## G-DATA-2&nbsp;—&nbsp;No uniqueness constraint or conflict check

### Source

```php
// appointment.php
array_push($_SESSION['history'], $_POST);
```

Unconditional `array_push`. No checks:

1. No "does this user already have an appointment on this date?" check.
2. No "are these two appointments geographically compatible?" check (Hongkong + Tokyo, same day).

### Symptoms

- **Duplicate**: two identical bookings → both are accepted and appear in history.
- **Overlap**: two bookings on the same day at very distant locations (Hongkong + Tokyo) → both are accepted.

### Related tests

| Test                                      | Method                                          | FAIL?               |
| ----------------------------------------- | ----------------------------------------------- | ------------------- |
| `Appointments - Duplicate booking`        | Book A, then book A again                       | FAIL (CURA accepts) |
| `Appointments - Overlapping appointments` | Book Hongkong/2025-05-18, book Tokyo/2025-05-18 | FAIL (CURA accepts) |

`book_then_verify_not_confirmed`

For these tests, we _reuse_ the G-DATA-1 pattern:

1. Book a first appointment (accepted).
2. Book a second nonsensical one (should be rejected).
3. `verify_booking_not_confirmed` on the second.

If the second booking is accepted too → fail (gap confirmed).

`_NOT_CONFIRMED_TIMEOUT`

All these gap tests use this constant:

```python
_NOT_CONFIRMED_TIMEOUT = 10
```

This constant deliberately bypasses CLI parameters. Bump `--wait-timeout` to 30 to stabilize another test&nbsp;—&nbsp;the gap tests stay at 10. No risk of silently inflating the gap assertion window.

`CURA_TEST_STRATEGY.md`:

> The assertion window is fixed at `_NOT_CONFIRMED_TIMEOUT` (10 s, defined in `confirmation.py`) and is intentionally **independent of `--wait-timeout`**: bumping the global wait flag for driver stability must not silently inflate every gap test's assertion budget.

## `saturation_booking`

> Example: `saturation_booking.py`&nbsp;—&nbsp;5 consecutive bookings on different dates in one session, all accepted; documents the absence of a rate limit.

Exploratory, not a gap test. It **passes**&nbsp;—&nbsp;documents that CURA accepts 5 rapid bookings. If CURA ever adds a rate-limit that rejects the 5th, this test breaks → revise it to reflect the new reality.

## Pedagogy

| Concept                                                                      | Test                                            |
| ---------------------------------------------------------------------------- | ----------------------------------------------- |
| How to express a gap test                                                    | `past_date_booking.py`                          |
| How to handle an independent timeout                                         | `_NOT_CONFIRMED_TIMEOUT`                        |
| How to distinguish a "_failing SUT_" exception from an "_expected behavior_" | `BookingNotRejectedError` vs `TimeoutException` |
| How to document observed behavior without a gap assertion                    | `saturation_booking.py`                         |
