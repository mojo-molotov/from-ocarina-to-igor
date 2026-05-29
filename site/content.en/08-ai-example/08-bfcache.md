---
title: "08.08 — Chrome BFCache (B-BROWSER-1) + environment artifacts"
description: "The Chrome BFCache gap in CURA: a protected page restored from cache after logout, plus the related environment artifacts."
weight: 8
date: 2026-05-20
series: ["ai-example"]
series_order: 8
---

# 08.08&nbsp;—&nbsp;Chrome BFCache (B-BROWSER-1) + environment artifacts

> Chrome restores a `no-store` page after logout, from the BFCache, even though it's a page protected by authentication.

## B-BROWSER-1&nbsp;—&nbsp;Chrome's BFCache is a pain

### Symptom

After logout, clicking the back button to be redirected to a page that was protected by authentication (e.g. `history.php`):

- **Chrome**: the page _stays displayed_ with its contents as shown to a still-authenticated user. The URL remains `history.php`, and the server isn't re-contacted to validate or invalidate access.
- **Firefox**: a new request goes to the server, which sees the session is dead and redirects.

### Very annoying gap

`history.php` correctly sends:

- `Cache-Control: no-store, no-cache, must-revalidate`
- `Pragma: no-cache`
- `Expires`

And server-side session invalidation works correctly.

**But Chrome's BFCache restores the page anyway** from a local _snapshot_.

### Confirmation recipe: back-then-reload

```
back() → we're on history.php, authenticated page restored
   ↓ (nothing touched the server)
refresh() → reload forces a server round-trip
   ↓
server: session dead → 302 to homepage
   ↓
we are redirected
```

- `back()` shows us the page again we shouldn't see anymore **AND** `refresh()` causes a redirect → confirmed BFCache _hit_.
- `back()` redirects immediately → server-side invalidation working as expected.
- `back()` shows us the page again we shouldn't see anymore **AND** `refresh()` doesn't redirect → server-side invalidation is broken (**anomaly**).

`CLAUDE.md`:

> **A confirmed BFCache exposure raises a dedicated, non-transient exception**&nbsp;—&nbsp;`BackForwardCacheExposureError` (`src/lib/errors.py`). Never a bare `AssertionError`; never a Selenium `WebDriverException`. The finding is deterministic and must never land in `transient_errors`.

### Dedicated exception

```python
# src/lib/errors.py
class BackForwardCacheExposureError(Exception):
    """The browser's back-forward cache exposed a logged-out authenticated view."""
```

Not in `transient_errors`. This finding is deterministic&nbsp;—&nbsp;we observe it immediately and it's never a flake.

### Related tests

| Test                                 | Recipe                                                                                                         |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| `post_logout_bfcache_exposure.py`    | back-then-reload: if back lingers on a page that shouldn't be shown + refresh redirects → BFCacheExposureError |
| `post_logout_server_invalidation.py` | direct refresh: confirms the server does invalidate (PASS)                                                     |
| `post_logout_frenetic_navigation.py` | back/forward stress (3 cycles): tries to provoke a mysterious BFCache timing                                   |

- **`post_logout_bfcache_exposure`**: FAIL on Chrome, PASS on Firefox.
- **`post_logout_server_invalidation`**: PASS on both (the server does its part).

### Code

```python
class HistoryPage(SeleniumBackAndForwardNavigationMixin, SeleniumTitleMixin, POMBase):
    def verify_back_button_did_not_restore_view(self) -> Self:
        # We're on history.php after back()
        pre_url = self._driver.current_url
        self._driver.refresh()
        try:
            WebDriverWait(self._driver, get_timeout()).until(
                ec.url_changes(pre_url)
            )
            # ✅ refresh redirected → server-side invalidation works
            # → back() stayed put = BFCache hit
            raise BackForwardCacheExposureError(
                f"Browser BFCache restored authenticated view of {pre_url} after logout."
            )
        except TimeoutException:
            # refresh didn't redirect → BFCache OR server-side fail
            # ... distinguish ...
            raise
```

The back→refresh distinction is encapsulated in the POM. The scenario just calls `verify_back_button_did_not_restore_view`.

### "_Cross-browser difference is a finding_"

`CLAUDE.md`:

> **Never skip a test on the browser where it fails.**

This test stays active on both browsers.

1. On Chrome, it deterministically documents the fragility.
2. On Firefox, it documents that Firefox honors `no-store`.

### Recommendation to CURA

`IDENTIFIED_GAPS.md`:

> **Recommendation for CURA:** send `Clear-Site-Data: "cache", "cookies"` on the logout response so the snapshot is evicted regardless of the browser's back-forward-cache policy.

This header forces the browser to destroy the cached snapshot regardless of BFCache policy.

## A-ENV-1&nbsp;—&nbsp;Rapid POST drop under `--workers 3`

### Symptom

Under `--workers 3`, a _rapid consecutive_ POST from one of the three parallel workers fails intermittently.  
Observed on:

- `Appointments - Saturation` (5 successive bookings).
- `Journey - History ordered ...` (2 successive bookings).

### Cause

Heroku eco-dyno concurrency limit hit by near-simultaneous POSTs. Infra issue, not a SUT bug. In single-worker mode, 2 consecutive bookings go through in 200–600ms.

### Flakiness handling

`TimeoutException ⊆ WebDriverException`&nbsp;→&nbsp;in `transient_errors` →&nbsp;auto-retry. A failure surviving all retries means contention was too high&nbsp;—&nbsp;not a regression, but worth a DevOps follow-up.

## A-ENV-2&nbsp;—&nbsp;Weak-password detection modal (Chrome)

### Symptom

On Chrome only, after a successful login, every subsequent action (click, keystroke, enter) did **nothing**. Root cause: a native Chrome modal&nbsp;—&nbsp;"your password has leaked"&nbsp;—&nbsp;appeared and swallowed all input.

### Cause

`ThisIsNotAPassword` is in Google's publicly-leaked credentials database. Chrome's password manager fires right after any successful login with this credential&nbsp;—&nbsp;a test-environment issue that hits the tester directly.

### Resolution

`src/lib/ext/ocarina/adapters/selenium/create_drivers_pool.py`:

```python
options.add_experimental_option("prefs", {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False,
})
options.add_argument("--disable-features=PasswordLeakDetection")
```

Disables Chrome's password manager and leak detection. The modal disappears.

### `IDENTIFIED_GAPS.md`

> **Why it stays documented:** the entry preserves _why_ the chrome driver adapter exists&nbsp;—&nbsp;delete the adapter and this artifact returns.

Institutional memory. If a future refactor removes the adapter, we'll know why it existed.

## Semantic conventions

| Prefix | Category                   | Example                                               |
| ------ | -------------------------- | ----------------------------------------------------- |
| `G-`   | Gap (CURA is broken)       | `G-SEC-1`, `G-DATA-1`, `G-SPEC-1`                     |
| `B-`   | Browser (browser behavior) | `B-BROWSER-1`                                         |
| `A-`   | Environment artifact       | `A-ENV-1` (dyno contention), `A-ENV-2` (Chrome modal) |
