---
title: "08.02 — CURA Healthcare (SUT)"
description: "CURA Healthcare, the external SUT of ocarina-with-ai-example: an open-source PHP app hosted on a Heroku dyno, with public credentials."
weight: 2
date: 2026-05-20
series: ["ai-example"]
series_order: 2
---

# 08.02&nbsp;—&nbsp;CURA Healthcare (SUT)

## Ocarina's first victim

- **Hosting**: https://katalon-demo-cura.herokuapp.com/
- **Source**: https://github.com/katalon-studio/katalon-demo-cura (PHP, open source, MIT)
- **Host**: Heroku eco-dyno (sleeps after inactivity)
- **Credentials**: `John Doe` / `ThisIsNotAPassword` (public, hardcoded on the login page)

## Perimeter

| Page                   | Function                                                                     |
| ---------------------- | ---------------------------------------------------------------------------- |
| `/`                    | Marketing homepage                                                           |
| `/profile.php#login`   | Login                                                                        |
| `/appointment.php`     | Booking form (facility, programs, hospital_readmission, visit_date, comment) |
| `/confirmation.php`    | Booking confirmation                                                         |
| `/history.php`         | The user's booking history                                                   |
| `/profile.php#profile` | Profile page (empty placeholder&nbsp;—&nbsp;gap §G-SPEC-2)                   |

## Why target CURA

1. **Open source**&nbsp;—&nbsp;we can read the PHP to understand why a given behavior exists.
2. **Plenty of gaps**&nbsp;—&nbsp;rich territory for findings.
3. **Public demo**&nbsp;—&nbsp;no authorization needed. Stable (maintained by Katalon).

There's also a tacit reason: Katalon is a competing test-framework vendor (Katalon Studio). It's poetic to test their demo app with Ocarina.

## `CURA_FRD.md`

> **About `CURA_FRD.md`.** CURA is a public demo app&nbsp;—&nbsp;**no functional documentation exists anywhere.** `CURA_FRD.md` was written from scratch, entirely by AI, by exploring the live app and reading its open-source PHP. It's a _reconstructed_ spec&nbsp;—&nbsp;AI _reverse engineering_ of what CURA does and of what a healthcare system like it _should_ do&nbsp;—&nbsp;this document, however, is not a source of authority.

1. Manual exploration sessions of the live app.
2. PHP reading via `gh api repos/katalon-studio/katalon-demo-cura/contents/...`.
3. Hypotheses about _what a healthcare system should do_ (§9).

The FRD is the semantic tree the tests are grounded in. Each test cites a `REQ-X-N` or a `§9.x` (gap).

## FRD scope

| Section | Content                                                          |
| ------- | ---------------------------------------------------------------- |
| 1-3     | Executive summary, system overview, roles                        |
| 4       | Functional requirements (Auth, Appointment, History, Profile)    |
| 5       | Element IDs (one per form field)                                 |
| 6       | URL map (`/profile.php#login`, etc.)                             |
| 7       | Business rules                                                   |
| 8       | Error handling                                                   |
| **9**   | **Known bugs / gaps** (CSRF, validation, session, BFCache, etc.) |

**Each gap has a stable ID (`§9.1`, `§9.2`, ...) referenced by the tests.**

## `IDENTIFIED_GAPS.md`

| Document             | Content                                                                  | Audience     |
| -------------------- | ------------------------------------------------------------------------ | ------------ |
| `CURA_FRD.md` §9     | Gap description (impact, recommendation, test ref)                       | Stakeholders |
| `IDENTIFIED_GAPS.md` | **Technical** inventory: PHP citations _file:line_, reproduction recipes | Maintainers  |

```markdown
### G-SEC-1 — No CSRF token on deployed forms

- **Where:** `views/page_login.php` (login form), `views/page_appointment.php` (appointment form) on https://katalon-demo-cura.herokuapp.com/.
- **Github source vs deployment:** `page_appointment.php` in the github repo calls `$antiCSRF->insertHiddenToken()` before the submit button. The
  **deployed** Heroku app does not render a hidden token input — verified by reading the live `<form>` HTML; the only fields are
  `facility / hospital_readmission / programs / visit_date / comment`. Reproduce by driving a Selenium browser through login → appointment and reading
  `document.querySelector('form').outerHTML`.
- **Authentication side:** `authenticate.php` performs no CSRF validation on login either — it directly calls
  `_f::login(_f::post("username"), _f::post("password"))` without consulting `$antiCSRF`.
- **Bonus bug:** Even if the form _did_ include a token, `appointment.php` checks `$antiCSRF->isValidRequest()` where `$antiCSRF` is never defined in
  that file (`security.php`'s class isn't instantiated there). The expression evaluates against an undefined variable; the check is no-op.
- **Impact:** Cross-origin POSTs to `appointment.php` and `authenticate.php` with the right field names succeed unconditionally for the demo account.
- **SFD ref:** §9.9.
```

Precise `file:line` references, reproduction recipe, FRD cross-ref. Forensic documentation.

## Heroku dyno

CURA runs on a Heroku **eco-dyno**: sleeps after ~30 min of inactivity, cold-starts on the next request.

Hence the Heroku warm-up step in `ai_proof_e2e.yml`:

```bash
curl -sf --retry 6 --retry-delay 5 --retry-all-errors \
  --max-time 30 https://katalon-demo-cura.herokuapp.com/ > /dev/null
echo "Dyno is warm"
```

```
# CURA runs on a Heroku dyno that sleeps after inactivity.
# Tests hitting a cold dyno produce timeouts (false fails) and slow
# confirmations (false passes on gap tests). Wake it explicitly
# before any browser opens.
```

## `A-ENV-1`: dyno contention under `--workers 3`

> ### A-ENV-1&nbsp;—&nbsp;Rapid-POST drop under `--workers 3` against the shared dyno
>
> - **Symptom:** Under `--workers 3`, a **rapid second-in-a-row POST** from one of the three parallel workers intermittently fails to redirect within 10 s.
> - **Matrix-wide, not browser-specific:** the trigger is three browser instances hammering one Heroku eco dyno, not any one browser.
> - **Not a CSRF issue:** per G-SEC-1, the deployed forms have no token.
> - **Not a SUT bug at single-worker:** solo (one worker) books two consecutive appointments cleanly in ~200–600 ms each.
> - **Cause:** Heroku eco-dyno concurrency limit hit by near-simultaneous POSTs from parallel workers.
> - **Handling:** `TimeoutException ⊆ WebDriverException` is in `transient_errors`, so a single occurrence auto-retries. A failure that survives all
>   retries is this artifact at full contention, not a regression.

## `A-ENV-2`: Chrome password breach detection

> ### A-ENV-2&nbsp;—&nbsp;Chrome password-breach modal swallows all input after login (resolved)
>
> - **Symptom (historical):** On chrome only, a test that logged in and then did _anything_&nbsp;—&nbsp;click, `send_keys`, even `Keys.ENTER` on a focused submit
>   button&nbsp;—&nbsp;saw the input silently do nothing.
> - **Cause:** the demo password `ThisIsNotAPassword` is a publicly-leaked credential, so Chrome's password manager raised a native breach-detection
>   modal on every successful login. The modal is browser chrome&nbsp;—&nbsp;invisible to `elementFromPoint`, doesn't block JS&nbsp;—&nbsp;but it captures every real input
>   event.
> - **Resolution:** `src/lib/ext/ocarina/adapters/selenium/create_drivers_pool.py` builds chrome with the consumer password manager off.
> - **Why it stays documented:** the entry preserves _why_ the chrome driver adapter exists&nbsp;—&nbsp;delete the adapter and this artifact returns.

## Related reading

- The detailed gaps: [`05-security-gaps.md`](05-security-gaps.md), [`06-data-gaps.md`](06-data-gaps.md), [`07-spec-gaps.md`](07-spec-gaps.md), [`08-bfcache.md`](08-bfcache.md)
- The custom `create_drivers_pool` (Chrome clean): [`09-ci-matrix.md`](09-ci-matrix.md)
