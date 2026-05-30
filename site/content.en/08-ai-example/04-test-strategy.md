---
title: "08.04 — Test strategy"
description: "The test strategy of ocarina-with-ai-example: six test types with distinct expected statuses, from happy path to intentionally failing business logic vulnerabilities."
weight: 4
date: 2026-05-20
series: ["ai-example"]
series_order: 4
tags: ["parallelisation"]
---

# 08.04&nbsp;—&nbsp;Test strategy

> Six **test types**, six distinct roles. Documented in `CURA_TEST_STRATEGY.md` §3.

## Test types

| Type                                                                                              | Expected status                                       | Authoritative source                                                             |
| ------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Happy path**                                                                                    | PASS                                                  | Nominal flows described from the FRDs                                            |
| **Unhappy path**                                                                                  | PASS (the test passes when the app correctly refuses) | Existing validations work                                                        |
| **Edge case / boundary**                                                                          | PASS or FAIL                                          | Depending on the test, often accompanied by a note added to the FRDs             |
| **Business logic vulnerability / gap test** (functional tests trying to "break" the product and identify gaps) | **Intentional FAIL**                                  | Behaviors a system should prevent but CURA doesn't                               |
| **Exploratory / observed-behaviour**                                                              | PASS                                                  | Documents current behavior when the spec doesn't cover it                        |
| **Permanent security regression fixture**                                                         | PASS (= security holds)                               | Verifies a security fix holds (fixes that stay permanently in the test heritage) |

## Happy path

> Exercises the nominal flow with valid inputs and an authenticated user. Verifies that the system produces the correct output (confirmation, history entry, etc.).

`valid_login.py`&nbsp;—&nbsp;login with valid credentials → we _expect_ a successful login.

## Unhappy path

> Exercises flows where the user provides invalid input or acts outside their authorisation. The test **passes** when the application responds with the correct rejection.

- Login with wrong credentials → we _expect_ an error message.
- Empty creds → we _expect_ an error message.
- Unauthorized access to the history page → we _expect_ a redirect.
- Submitting an appointment form without a date → we _expect_ the submission to be refused.

## Edge case / boundary

> Exercises the limits of what the application is supposed to accept or reject, where the specification is unclear or the behaviour is surprising.

Synced with `CURA_FRD.md`: a note is added when a gap is found.

## Business logic vulnerability / gap test

Intentionally failing tests until a fix lands:

| Test                                                                 | Gap      | FRD  |
| -------------------------------------------------------------------- | -------- | ---- |
| `Appointment - Server accepts empty date when client bypass applied` | G-DATA-1 | §9.1 |
| `Appointment - Past date booking accepted`                           | G-DATA-1 | §9.7 |
| `Appointments - Duplicate booking`                                   | G-DATA-2 | §9.6 |
| `Appointments - Overlapping appointments`                            | G-DATA-2 | §9.6 |
| `Journey - History ordered most-recent date first`                   | G-SPEC-1 | §9.8 |

> Implementation rule: gap tests must fail with a clear, specific message&nbsp;—&nbsp;not a generic `TimeoutException`. They use `ConfirmationPage.verify_not_confirmed()`, which checks `url_contains("appointment.php")` (fast, not DOM-dependent, not blocked by HTML5 validation popups). The assertion window is fixed at `_NOT_CONFIRMED_TIMEOUT` (10 s, defined in `confirmation.py`) and is intentionally **independent of `--wait-timeout`**.

Gap tests must fail **clearly**&nbsp;—&nbsp;no generic `TimeoutException`.

`_NOT_CONFIRMED_TIMEOUT` is fixed at 10s and deliberately decoupled from `--wait-timeout`. Bumping `--wait-timeout` to stabilize another test shouldn't accidentally make a gap test pass.

## Telling a gap test apart from a validation test

> Distinguishing a gap test from a validation pass:
>
> - **Gap test (intentionally FAILS):** CURA _should_ reject X but doesn't. The test asserts rejection; the failure documents the gap.
> - **Validation test (PASSES):** CURA _does_ correctly reject X. The test asserts rejection; the pass confirms the validation still works.

Two tests can have opposite intentions. The **name**, the docstring, and the entry in `IDENTIFIED_GAPS.md` disambiguate.

## Exploratory / observed-behaviour

> Documents what CURA actually does when no requirement is specified. These tests **pass** and record the observed behaviour both in the per-test log and in the SFD.

`saturation_booking.py`&nbsp;—&nbsp;5 consecutive bookings on different dates in one session, all accepted. Documents the absence of a rate limit.

> When to add one:
>
> - A business-logic constraint is plausible but absent from the SFD ("can I book the same date twice in different slots?").
> - Decide before writing: is the current behaviour reasonable (→ exploratory / pass) or a gap (→ assertive / intentional fail)?
> - Always pair with an SFD update.

Human decision before writing: is the current behavior OK or a gap?

1. OK → exploratory test, expected to pass.
2. Gap → assertive test, intentionally failing.

## Permanent regression tests

Verifies a critical security fix still holds. If the fix regresses, the test turns red. Documents fix maintenance over time.

## `cycles/e2e.py`

```python
E2E_CYCLE_NAME = "CURA E2E"

def create_e2e_test_cycle(drivers_pool) -> TestCycle[WebDriver]:
    return TestCycle(
        name=E2E_CYCLE_NAME,
        smoke_tests_campaigns=[create_prerequisites_campaign(drivers_pool=drivers_pool)],
        campaigns=[
            create_authentication_campaign(drivers_pool=drivers_pool),
            create_appointments_campaign(drivers_pool=drivers_pool),
            create_profile_campaign(drivers_pool=drivers_pool),
            create_user_journeys_campaign(drivers_pool=drivers_pool),
        ],
    )
```

## Hierarchy

```
Cycle "CURA E2E"
├── Smoke (gate, fail-fast)
│   └── Campaign "Prerequisites"
│       └── Suite "Authentication baseline"
│           └── Test "valid_login"                     # gate
│
└── Main
    ├── Campaign "Authentication"
    │   ├── Suite "Session management"
    │   └── Suite "Failure modes"
    │       ├── failed_logins.py                       # data-driven: invalid / empty / wrong-case
    │       ├── unauthenticated_appointment_access.py
    │       ├── unauthenticated_history_access.py
    │       ├── unauthenticated_profile_access.py
    │       ├── logout.py
    │       ├── post_logout_access.py
    │       ├── post_logout_bfcache_exposure.py        # B-BROWSER-1
    │       ├── post_logout_frenetic_navigation.py
    │       ├── post_logout_server_invalidation.py
    │       └── rapid_logout_relogin.py
    ├── Campaign "Appointments"
    │   ├── Suite "Booking"
    │   │   ├── book_appointments.py                   # data-driven: Hongkong / Tokyo+readmission / Seoul
    │   │   ├── missing_visit_date_validation.py
    │   │   ├── server_side_date_bypass.py             # G-DATA-1
    │   │   ├── past_date_booking.py                   # G-DATA-1
    │   │   ├── enter_on_visit_date_no_submit.py
    │   │   ├── duplicate_booking.py                   # G-DATA-2
    │   │   ├── overlapping_appointments.py            # G-DATA-2
    │   │   └── saturation_booking.py                  # exploratory
    │   └── Suite "History"
    │       ├── view_history.py
    │       └── empty_history.py
    ├── Campaign "Profile"
    │   └── Suite "Profile access"
    │       └── view_profile.py                        # G-SPEC-2 documents the placeholder
    └── Campaign "User journeys"
        └── Suite "Cross-feature flows"
            ├── book_and_verify_history.py
            ├── history_ordering.py                    # G-SPEC-1
            ├── sidebar_navigation.py
            └── sidebar_login_navigation.py
```

## `CLAUDE.md`

### "_Smoke is structural, not lexical_"

> Express the gate via `TestCycle.smoke_tests_campaigns=`; never put "smoke" in a name string.

"smoke" must not appear in test or suite names. The gate semantics live in Ocarina's **structure** (`smoke_tests_campaigns=`), not in a string.

### "_Smoke is the minimum that proves the system is alive_"

> A test belongs in smoke iff its failure makes the rest of the cycle uninformative.

Strict criterion: smoke only if failure invalidates everything else. `valid_login` qualifies&nbsp;—&nbsp;no auth, no CURA testing.

### "_Each main campaign is feature-shaped, not method-shaped_"

Campaigns named by feature (`Authentication`, `Appointments`, `Profile`, `User journeys`), not by HTTP method.

### "_Default mode is fail-fast_"

The default smoke-tests mode is sufficient here. `wait-for-all-smoke-tests` is reserved for cycles with multiple independent smoke campaigns (cf. `ocarina-example`, which has 2).

## `--workers 3`

> **Never `--workers 1`.** Single-worker runs mask concurrency failures and diverge from CI. Always `--workers 3` (matches `ai_proof_e2e.yml`); CI is the canonical reference.

Never test with a single worker:

1. One worker masks race conditions.
2. CI runs with 3; match it locally.
3. `saturate_workers=True` clones tests to hit N=3 → exposes heisenbugs.
