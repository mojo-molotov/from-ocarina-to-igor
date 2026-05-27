---
title: "09.03.07 — Refactor skills"
description: "Skills that refactor the existing automated-test base."
weight: 7
date: 2026-05-20
series: ["skills"]
series_order: 7
tags: ["holy-book", "scenarios"]
---

# 09.03.07&nbsp;—&nbsp;Refactor skills

> Skills that **refactor** the existing automated-test base.

## Listing (potentially non-exhaustive)

| Skill                    | Target                                                      |
| ------------------------ | ----------------------------------------------------------- |
| `refactor-fragmentation` | DRY based on user preference                                |
| `introduce-pom-retries`  | POM-internal retries, with split (first-try + with-retries) |

## `refactor-fragmentation`

```
input  : the test base
output : DRY refactor suggestions:
            - blocks repeated in 3+ scenarios → extract into a fragment
            - near-identical connectors → extract a parameterized connector
            - repeated log+screenshot sequences → extract a helper
         + per-case recommendation
```

`CLAUDE.md`:

> **When to extract a fragment**
>
> - **Don't extract preemptively.** Two scenarios sharing 3 acts is a coincidence. Wait for **3+ scenarios** with the same block.
> - **The block must be a precondition/postcondition, not the focus of any test.** `valid_login.py` does not use the login fragment&nbsp;—&nbsp;login _is_ the test there, and uses `log_and_screenshot` for the meaningful page transition.
> - **Unhappy-path login tests stay self-contained.** `failed_logins` and `unauthenticated_history_access` don't use the fragment&nbsp;—&nbsp;they must stay independent of demo-user state.

1. **Quantity**: 3+ scenarios with the same block.
2. **Role**: pre/postcondition, not the test's focus.
3. **Independence**: unhappy-path tests must stay self-contained.

`refactor-fragmentation` applies these criteria and **suggests** (without applying).

## `introduce-pom-retries`

```
input  : a connector that exercises a flaky action (e.g. clicking a button that may fail intermittently)
output : refactor into:
            1. POM method `<action>` without retry (single try)
            2. POM method `<action>_with_retries(retries: int, logger: ILogger)` that retries internally
            3. dual connectors:
                - `<action>`: calls POM `<action>`
                - `<action>_with_retries(retries, logger)`: calls POM `<action>_with_retries`
            4. scenarios updated to use the appropriate variant
```

That's the pattern seen in `ocarina-example/lib/connectors/test_steps/actions/dashboard_login.py`:

```python
def login_without_otp(creds: ImmutableCredentials):
    def unwrapped(p: DashboardLoginPage) -> DashboardLoginPage:
        return p.login_without_otp(creds)
    return unwrapped


def login_without_otp_and_with_retries(
    creds: ImmutableCredentials, retries: int, *, logger: ILogger
):
    def unwrapped(p: DashboardLoginPage) -> DashboardLoginPage:
        return p.login_without_otp_and_with_retries(creds, retries, logger=logger)
    return unwrapped
```

Two connectors. The scenario picks based on need:

- Happy-path case: `login_without_otp_and_with_retries` (the 10%-fail `useAuth` forces the retry).
- Unhappy-path case ("_login with wrong password_"): `login_without_otp` (we _want_ the failure to surface, no retry).

## Why split

| Without splitting                          | With splitting                                                                                              |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| One `login(...)` method, always with retry | Tests that want to see an immediate failure are clouded by retries                                          |
| No happy / unhappy differentiation         | Clear differentiation                                                                                       |
| Brittle tests if you remove the retry      | Robust tests: test coverage preserved; a complementary test refusing flakiness keeps tracing it on the side |

## "_Retries at the POM, not in the scenario_"

Holy Book (chapter "_First real-world hurdles_"):

> ## Test step hazards
>
> Thinking I had left that kind of nonsense behind me, I moved on, only to find unstable forms and authentication systems that worked half the time.
>
> Here, Ocarina's answer is different: we delegate the responsibility to the POM.

| Variant                                    | Pro                                                                       | Con                                                 |
| ------------------------------------------ | ------------------------------------------------------------------------- | --------------------------------------------------- |
| Framework-level retry (`transient_errors`) | Transparent, appropriate for flakiness that's truly impossible to isolate | Replays _the whole_ test, not just the flaky action |
| POM-level retry                            | Granular + placed in a well-named method                                  | &nbsp;—&nbsp;                                       |

## Cross-cutting discipline

- **Analyze** patterns in the base.
- **Suggest** refactors.
- **Don't immediately apply** unless explicitly instructed.
- **Respect** extraction rules.
