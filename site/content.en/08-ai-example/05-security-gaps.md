---
title: "08.05 — Security gaps (G-SEC-1 to G-SEC-3)"
description: 'Three documented security gaps. Not actively exploited (cf. the rule "security testing is functional and static, never active"), but observed via functional tests.'
weight: 5
date: 2026-05-20
series: ["ai-example"]
series_order: 5
---

# 08.05&nbsp;—&nbsp;Security gaps (G-SEC-1 to G-SEC-3)

> Three documented security gaps. Not actively exploited (cf. the rule "_security testing is functional and static, never active_"), but observed via functional tests.

## G-SEC-1&nbsp;—&nbsp;No CSRF token on the front-end forms

### Symptom

The `<form>` rendered on Heroku **does not contain** a CSRF token.

### Source

`views/page_appointment.php` in the GitHub repo _calls_ `$antiCSRF->insertHiddenToken()` before the submit button. But on the **deployed** version, this token does **not** appear in the HTML.

Divergence between source-code intent and the actual deployed deliverable.

### Authentication

`authenticate.php` doesn't validate the CSRF either:

```php
_f::login(_f::post("username"), _f::post("password"));
```

No `$antiCSRF->isValidRequest()` check.

### Bonus bug

Even if the form _did_ have the token: `$antiCSRF` is **never defined** in the code.  
It's an expression evaluated against an undefined variable.

### Impact

Cross-origin POSTs to `appointment.php` or `authenticate.php` (with the right field names) succeed unconditionally. It's possible to impersonate a CURA user by exploiting this vulnerability.

### Test approach

**No automated test** for this gap. The finding is documented in `IDENTIFIED_GAPS.md` (G-SEC-1) with proof via static PHP reading and manual DOM inspection on the Heroku deployment.

The gap could be materialized as a functional test, but isn't yet.

## G-SEC-2&nbsp;—&nbsp;`_f::logout()` doesn't destroy the cookie

### Symptom

After `GET authenticate.php?logout`, the browser keeps the `PHPSESSID` cookie with the same value. The session is erased server-side, but the cookie remains.

### Source

```php
public function logout() {
    session_unset();
    $this->antiCSRF->unsetToken();
    return session_destroy();
}
```

`session_destroy()` destroys server data. **But** doesn't call `setcookie(session_name(), '', time() - 42000, '/')`, which would force the browser to delete the cookie.

### Why it matters

Risk of a combined attack with G-SEC-1.

### Recommendation

Call `setcookie(session_name(), '', time() - 42000, '/')` _before_ `session_destroy()`.

### Test approach

| Test                              | Verifies                                                                                      |
| --------------------------------- | --------------------------------------------------------------------------------------------- |
| `post_logout_access`              | After logout, navigation to `/history.php` redirects (URL change → server-side session check) |
| `post_logout_server_invalidation` | A forced reload after logout (bypassing the BFCache) also redirects                           |
| `post_logout_bfcache_exposure`    | The "back" button after logout doesn't restore the authenticated view from the BFCache        |
| `post_logout_frenetic_navigation` | Back/forward stress after logout, the protected page stays locked for N cycles                |
| `rapid_logout_relogin`            | Rapid logout/login cycles, session integrity (probe)                                          |

All five tests **PASS when CURA behaves correctly**&nbsp;—&nbsp;the session is invalidated server-side. G-SEC-2 (cookie persisting in the browser) stays in `IDENTIFIED_GAPS.md` without a dedicated functional test, because the lingering cookie alone doesn't grant access: `session_destroy()` on the server does the job, and these 5 tests prove it.

## G-SEC-3&nbsp;—&nbsp;No rate-limit, no lockout, no CAPTCHA

### Source

```php
if ($user === USERNAME && $password === PASSWORD) {
    ...
}
```

`_f::login()` does a `===` comparison (case-sensitive, no _type juggling_). **But no throttle, no lockout, no CAPTCHA**.

### Risk

Bruteforce risk.

### Out of scope

> Out of scope to exploit on a demo app; documented because the implementation has no defensive depth.

Passive documentation only. No brute-force test&nbsp;—&nbsp;that's active, and forbidden.

`IDENTIFIED_GAPS.md` documents the finding without a corresponding automated test. The "gap test required if user-facing" rule doesn't apply: brute-forcing an auth form isn't normal user behavior.

## _Static-only_ discipline, to keep within the functional perimeter

`CLAUDE.md`:

> This is a **functional** test suite. Its scope ends at _what a real user can do through the browser_, plus _reading source for gap analysis_. Inside that scope:
>
> - Static analysis is welcome and encouraged.
> - Functional tests that exercise security-relevant behaviour through the **normal UI/HTTP path**&nbsp;—&nbsp;submitting an empty visit date through the real form, attempting a duplicate booking through the real form, asserting no CSRF input by reading the rendered HTML, checking that the back-button doesn't expose a logged-out view by pressing back&nbsp;—&nbsp;are fine.
>
> **Forbidden, no exceptions:**
>
> - Crafted attack payloads (SQL injection, XSS, command injection, header pollution, path traversal, deserialisation, …).
> - Token tampering, signature stripping, cookie forgery, session-fixation attempts, forced-browsing fuzzers.
> - Cross-origin POSTs constructed outside the suite, scripted directory enumeration, DOS, rate-floods.

| Action                                    | Category             | Status       |
| ----------------------------------------- | -------------------- | ------------ |
| Submit a dateless form via the real UI    | Functional           | ✅ OK        |
| Verify no CSRF token by reading the DOM   | Functional           | ✅ OK        |
| Try multiple bookings via the real UI     | Functional           | ✅ OK        |
| Press the "back" button after logging out | Functional           | ✅ OK        |
| Send `'  OR 1=1 --` in the username field | **Crafted payload**  | ❌ FORBIDDEN |
| Tampering of the `PHPSESSID` cookie       | **Tampering**        | ❌ FORBIDDEN |
| Forged cross-origin POST                  | **Out of normal UI** | ❌ FORBIDDEN |
| Brute-forcing login                       | **Rate flood**       | ❌ FORBIDDEN |

Active testing belongs in a different project (Burp / ZAP / sqlmap / dedicated engagement).

## Diagram (security breaches)

```
                          ┌───────────────────────────────────────────┐
                          │           CURA / PHP                      │
                          ├───────────────────────────────────────────┤
                          │                                           │
        G-SEC-1:          │  page_login.php / page_appointment.php    │
        forms without CSRF│  → no <input name="csrf_token">           │
        ↑                 │                                           │
        │                 │  authenticate.php:                        │
        │                 │   _f::login(...)  with no isValidRequest  │
        │                 │                                           │
        │                 │  appointment.php:                         │
        │                 │   $antiCSRF->isValidRequest()             │
        │                 │   ← $antiCSRF is not defined here         │
        │                 │                                           │
        └─────────────────┤                                           │
        G-SEC-2:          │  functions.php / _f::logout():            │
        cookie stays      │   session_destroy()                       │
        ↑                 │   ← no setcookie(... time()-42000)        │
        │                 │                                           │
        └─────────────────┤                                           │
        G-SEC-3:          │  _f::login():                             │
        no rate-limit     │   if ($user === USERNAME && ...)          │
        ↑                 │   ← no throttle, lockout, captcha         │
        │                 │                                           │
        └─────────────────┤                                           │
                          └───────────────────────────────────────────┘
```
