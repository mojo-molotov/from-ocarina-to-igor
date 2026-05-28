---
title: "08.07 — Spec gaps (G-SPEC-1 to G-SPEC-3)"
description: "The three CURA spec gaps, divergences between observed behavior and what a healthcare system should do, by ocarina-with-ai-example."
weight: 7
date: 2026-05-20
series: ["ai-example"]
series_order: 7
---

# 08.07&nbsp;—&nbsp;Spec gaps (G-SPEC-1 to G-SPEC-3)

> Three gaps on business behavior vs the _expected_ spec of a healthcare system.

## G-SPEC-1&nbsp;—&nbsp;History sorted by submission order, not by date

### Source

```php
// views/page_history.php
foreach ($_SESSION['history'] as $appointment) {
    // ... render ...
}
```

No `usort`. No sort. No sort step exists anywhere.

`appointment.php` pushes with `array_push($_SESSION['history'], $_POST)`&nbsp;—&nbsp;append to the end (it's a _pushback_).

### Unmet spec

`REQ-HIST-3` from the FRD:

> Most recent calendar date first

(_Reconstructed_ spec by AI&nbsp;—&nbsp;typical of a history system.)

### Symptom

Appointments appear in the order they were confirmed by the system, regardless of `visit_date`. A booking for 2026-12-31, submitted today (2026-05-22), and a booking for next week, submitted three days later (2026-05-25), end up displayed with the December booking _above_ the next-week one.

### Test

```python
# src/tests/scenarios/journey/history_ordering.py
"""History ordered most-recent calendar date first (REQ-HIST-3 / §9.8 gap).

Flow:
  login → book #1 (visit_date = in 30 days) → book #2 (visit_date = tomorrow)
  → open history → verify card order: #2 above #1 (most recent first)
  (intentional FAIL — CURA renders in submission order, §9.8 gap)

Pre-fragments: login_as_demo_user
Post-fragments: (none)
"""
```

**Intentionally failing** test. Booking#1 (far date) then booking#2 (near date) should show #2 first. CURA shows them in insertion order&nbsp;—&nbsp;#1 on top. Documented failure.

## G-SPEC-2&nbsp;—&nbsp;Profile page = placeholder

### Source

```php
// views/page_profile.php
// renders the #profile section but contains no editable fields,
// no form, no API endpoint.
```

### Symptom

Logged-in users see "_Profile_" in the menu, navigate to it, and find **an empty page**. No form, no button, just text (_placeholder_).

### Test

```python
# src/tests/scenarios/profile/view_profile.py
def scenario_view_profile(driver, logger):
    on_profile = ProfilePage(driver=driver)
    return [
        drive_page(
            act(on_profile, open_profile_page)...,
            act(on_profile, verify_profile_is_placeholder)...,    # PASS = documents the placeholder
        ),
    ]
```

This test **PASSES**&nbsp;—&nbsp;it documents current behavior. Not a gap test; an exploratory trace.

If CURA ever adds a real profile page, `verify_profile_is_placeholder` breaks → revise the test.

## G-SPEC-3&nbsp;—&nbsp;Unauthorized access redirects to `/`, not to login

### Source

```php
// appointment.php
if (!$session_check) {
    header("Location: " . SITE_URL);                  // ← redirects to /
    exit;
}
```

`history.php` does the same.

### Expected spec

Should redirect to `/profile.php#login`, not `/`. The user loses context ("I wanted my history"). Ergonomic flaw.

### Symptom

Unauthenticated user clicks a _deep-link_ pointing at `/appointment.php` or `/history.php` → lands on the homepage → has to click "_Make Appointment_" again to reach the login page.

### Test

```python
# src/tests/scenarios/login/unauthenticated_appointment_access.py
def scenario_unauthenticated_appointment_access(driver, logger):
    on_appointment = AppointmentPage(driver=driver)
    on_home = HomePage(driver=driver)
    return [
        drive_page(
            act(on_appointment, open_appointment_page)...,
            act(on_appointment, verify_redirected_to_home)...,    # PASS = documents the behavior
        ),
        drive_page(
            act(on_home, verify_home_page)...,
        ),
    ]
```

`unauthenticated_appointment_access.py`, `unauthenticated_history_access.py`, `unauthenticated_profile_access.py`.

All three tests PASS&nbsp;—&nbsp;they document exploration. With the FRD reconstructed and non-authoritative, we can't call this a clear anomaly. We recommend and document.

## Pattern: gap test vs exploratory pass

Spec gaps are mostly exploratory-pass (documents current behavior) rather than intentional-fail (asserts a block that should exist but doesn't).

| G-DATA-\*                                    | G-SPEC-\*                                       |
| -------------------------------------------- | ----------------------------------------------- |
| "CURA accepts X, which it should reject"     | "CURA does X instead of Y"                      |
| Gap test: assert rejection, intentional fail | Documentary test: assert current behavior, pass |

Assertive gap tests are reserved for journeys where **a healthcare system should clearly reject the user**. For minor spec divergences (history order, empty profile page, suboptimal redirect), document rather than assert.

## The art of choosing

`CURA_TEST_STRATEGY.md`:

> When to add one [exploratory test]:
>
> - A business-logic constraint is plausible but absent from the SFD ("can I book the same date twice in different slots?").
> - **Decide before writing**: is the current behaviour reasonable (→ exploratory / pass) or a gap (→ assertive / intentional fail)?
> - Always pair with an SFD update.

Human decision before writing. No automatic toggle. That's what keeps the strategy **readable** for a newcomer: every test sits in the category matching its intent.

## `IDENTIFIED_GAPS.md`

Every gap (DATA, SPEC, SEC) has an entry in `IDENTIFIED_GAPS.md`. Test name, docstring, and gap entry must be **synchronized**.

`CLAUDE.md`:

> **No SFD references outside `#` comments.** Test names, log messages, exception messages, docstrings&nbsp;—&nbsp;none contain `SFD §x.x`. Those references belong in `CURA_FRD.md` and in inline comments. The SFD number means nothing to someone reading a test report.

Test names are **human-readable** (`Past date booking accepted`, not `Test_FRD_9_7`). The `§9.7` reference lives in code as a comment and in `IDENTIFIED_GAPS.md`.
