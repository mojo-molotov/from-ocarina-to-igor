---
title: "06.07 — OTP coordination flow + deliberate imprecision"
description: "The tests-workers OTP coordination flow: how N parallel Ocarina workers retrieve the right OTP despite deliberate imprecision."
weight: 7
date: 2026-05-20
series: ["tests-workers"]
series_order: 7
tags: ["otp", "parallelisation"]
---

# 06.07&nbsp;—&nbsp;OTP coordination flow + deliberate imprecision

> The backend's reason to exist: let N parallel Ocarina workers **retrieve the right OTP** for their _user_, even when several OTPs are generated.

## Flow

```
   ┌───────────────────────────────────────────────────────────────────┐
   │               Worker (among --workers 3 of Ocarina)               │
   └───────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Selenium opens the Dashboard login page                           │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Acquire the distributed Redis lock (OTP_SEND_LOCK_KEY)            │
   │   → only this worker can click "Send OTP" during ACQ              │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ min_utc_date = datetime.now(UTC)                                  │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ L1 cache: record min_utc_date + username in the cache             │
   │   (keys reserved by reserve_free_cache_key)                       │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Selenium types username + password + ticks OTP + click "REQ OTP"  │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ IGORISTAN UI: fetch /api/otp?_user=<username>                     │
   │   (x-api-key typed by Selenium into the UI)                       │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ TESTS-WORKERS /api/otp:                                           │
   │   generate(secret) → otpCode                                      │
   │   createdAt = floor(now/1000)*1000  ← ms stripped                 │
   │   event = { _user, otpCode, createdAt, expiresAt, ... }           │
   │   redis.set("otp:<now>:<uuid>", JSON, EX 360)                     │
   │   return event                                                    │
   └──────────────────────────────────┬────────────────────────────────┘
                                      ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ IGORISTAN UI: displays OTP screen                                 │
   └──────────────────────────────────┬────────────────────────────────┘
                                      ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Release the OTP_SEND_LOCK_KEY Redis lock                          │
   └──────────────────────────────────┬────────────────────────────────┘
                                      ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Selenium: retrieve_dashboard_otp_code(min_utc_date, _user)        │
   │   ↓                                                               │
   │   GET /api/otp-history  (x-api-key = IGOR_API_KEY)                │
   │   ↓                                                               │
   │   TESTS-WORKERS: SCAN otp:* + MGET → all events                   │
   │   ↓                                                               │
   │   client-side filter by _user                                     │
   │   filter createdAt >= min_utc_date - 1s                           │
   │   sort ASC by createdAt                                           │
   │   return first.otpCode                                            │
   └──────────────────────────────────┬────────────────────────────────┘
                                      ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │ Selenium types the OTP into the Igoristan UI                      │
   │   → AUTHENTICATED_WITH_MFA                                        │
   └───────────────────────────────────────────────────────────────────┘
```

## Race conditions

1. Worker A: `min_utc_date_A = 13:27:53.123`, generates OTP_A at 13:27:53.250.
2. Worker B: `min_utc_date_B = 13:27:53.130`, generates OTP_B at 13:27:53.470.

Without coordination, A could pick up OTP_B instead of OTP_A&nbsp;—&nbsp;the timestamps are close and truncated to the second.

## Distributed lock

The `OTP_SEND_LOCK_KEY` lock serializes `REQ OTP` calls&nbsp;—&nbsp;A finishes before B starts.

Two different users requesting simultaneously don't block each other (per-user lock). Both OTPs can land in the same second. That's what the `_user` filter is for.

## `_user` filter

```python
def _entry_matches(entry):
    expected_user = expected_login or env.get_credentials("dashboard")["login"]
    is_testing_entry = entry["_user"] == expected_user
    if not is_testing_entry:
        return False
    created_at = datetime.fromisoformat(entry["createdAtTimestampLackingMsPrecision"])
    return created_at >= min_utc_date - timedelta(seconds=1)
```

## Stripped ms

```typescript
const createdAtTimestampLackingMsPrecision = new Date(
  now - (now % 1000),
).toISOString();
```

`createdAt` is rounded to the second. All OTPs generated in the same second have identical `createdAt` values. Sorting by timestamp alone is useless.

## Cycle and coordination

```
Worker A: min_utc_date_A = 13:27:53.500
          OTP issued: createdAt = 13:27:53.000 (stripped)

Filter: 13:27:53.000 >= 13:27:53.500 - 1s = 13:27:52.500   ✅ passes
```

Without the `-1s` margin, we'd miss the OTP we just requested.

To create a stable time window, the test forces a 2.5s sleep inside the lock in `start_to_login_with_otp`:

```python
if workers > 1:
    with _get_lock():
        time.sleep(2.5)
        _send(username)
    else:
        _send(username)
```

The system combines `_user` filtering, delta timing, and sequential locks to reliably identify its own OTP.

An implementation that relied on timestamp alone would break the moment you parallelize.

## Excerpt from `tests-workers`'s README

```
### Quirks

Returns ISO timestamps precise to seconds only (`.000Z`) to force proper concurrency handling in test frameworks.
```

Deliberate, documented, and a lovely gift from the backend: a subtle quirk the test suite must handle correctly.

## Why Redis and not just a local lock

Three Ocarina workers = three threads, one WebDriver process per thread. One main process, N threads, each driving a Selenium session.

`threading.Lock` would work in that scenario. But scale horizontally&nbsp;—&nbsp;two machines running `ocarina-example` simultaneously, or two terminals on the same machine&nbsp;—&nbsp;and `threading.Lock` is no longer enough. You need a distributed lock. Redis provides one via `setnx`-based `redis.lock()`.

## Conclusion

`tests-workers` is intentionally designed to make test coordination **hard but possible**. It's a training ground. Real SUTs have this kind of imprecision all the time&nbsp;—&nbsp;rate limits, timestamps precise only to the second, race-prone APIs.
