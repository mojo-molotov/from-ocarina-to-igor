---
title: "05.03 — The fake useAuth + MFA OTP"
description: "The Igoristan's fake useAuth hook: a 10% random failure and an optional OTP MFA, to exercise retries and worker coordination."
weight: 3
date: 2026-05-20
series: ["igoristan"]
series_order: 3
tags: ["otp"]
---

# 05.03&nbsp;—&nbsp;The fake `useAuth` + MFA OTP

> Igoristan's `useAuth` hook is deliberately fake. Two mechanics to exercise Ocarina's replay and worker coordination: a 10% random failure and an optional MFA OTP.

## Code

```ts
// src/hooks/useAuth.ts
const VALID_PASSWORD = "figatellu";
const NOT_AUTHENTICATED = -1;
const AUTHENTICATED_WITHOUT_MFA = 1;
const AUTHENTICATED_WITH_MFA = 2;

// * ... This is FAKED
export const useAuth = () => {
  const [_isAuthenticated, setIsAuthenticated] = useLocalStorage(
    "isAuthenticated",
    NOT_AUTHENTICATED,
  );
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = useCallback(
    () => _isAuthenticated !== NOT_AUTHENTICATED,
    [_isAuthenticated],
  );
  const isAuthenticatedWithMFA = useCallback(
    () => _isAuthenticated === AUTHENTICATED_WITH_MFA,
    [_isAuthenticated],
  );
  const logout = useCallback(
    () => setIsAuthenticated(NOT_AUTHENTICATED),
    [setIsAuthenticated],
  );

  useEffect(() => {
    const delay = 500 * randint(1, 5); // ◄── random delay 0.5–2.5s
    const timer = setTimeout(() => setIsLoading(false), delay);
    return () => clearTimeout(timer);
  }, []);

  const login: LoginFn = ({ pre = false, password, withMFA }) => {
    if (password === VALID_PASSWORD && Math.random() < 0.9) {
      // ◄── 10% fail despite correct password
      if (!pre) {
        setIsAuthenticated(
          withMFA ? AUTHENTICATED_WITH_MFA : AUTHENTICATED_WITHOUT_MFA,
        );
      }
      return true;
    }
    return false;
  };

  return { isAuthenticatedWithMFA, isAuthenticated, isLoading, logout, login };
};
```

## Mechanics

### 1. `LocalStorage`

```ts
const [_isAuthenticated, setIsAuthenticated] = useLocalStorage(
  "isAuthenticated",
  NOT_AUTHENTICATED,
);
```

Three values: `-1` (not authenticated), `1` (no MFA), `2` (with MFA).  
Persisted in `localStorage`, easy to inspect for testing / manual debugging.

### 2. The password is plaintext

```ts
const VALID_PASSWORD = "figatellu";
```

Public, hardcoded: it's a demo.

### 3. **Random failure**

```ts
if (password === VALID_PASSWORD && Math.random() < 0.9) {
```

Login only succeeds if the password is correct **AND** a random draw < 0.9. So 10% chance of **failure despite a correct password**.

The **key** SUT point for exercising replay with Ocarina:

| Project side                     | Behavior                                                         |
| -------------------------------- | ---------------------------------------------------------------- |
| Test passes successfully         | OK (90% of the time)                                             |
| Test fails with "_Login failed_" | Retry handled _directly in the POM_ (not via `transient_errors`) |
| Test fails 9 times in a row      | Probability = `0.1^9 ≈ 10⁻⁹` → infeasible                        |

→ With `max_retries_per_test=8` (default), a login test has a failure probability below `10⁻⁹`.  
Without retry, it would be 10%.

The **empirical demonstration** of why retries earn their keep.

### 4. Random initialization delay

```ts
const delay = 500 * randint(1, 5); // 500, 1000, 1500, 2000, 2500
const timer = setTimeout(() => setIsLoading(false), delay);
```

→ `isLoading = true` for 0.5 to 2.5 seconds at startup. On the test side, you have to wait until `isLoading` flips to `false` before interacting&nbsp;—&nbsp;confirms the value of `WebDriverWait` and catches race conditions from overly aggressive `.find_element` use with Selenium.

### 5. The `pre` mode in `login`

```ts
const login: LoginFn = ({ pre = false, password, withMFA }) => {
    if (password === VALID_PASSWORD && Math.random() < 0.9) {
      if (!pre) {
        setIsAuthenticated(...);
      }
      return true;
    }
    return false;
};
```

`pre = true` lets you **validate the password without authenticating**&nbsp;—&nbsp;useful for the MFA UI flow: validate the password, _move on_ to the OTP screen, only authenticate once the OTP is also validated.

## Flow (MFA)

```
1. USER / SELENIUM types username + password + checks "Use OTP"
   ↓
2. login({ pre: true, password, withMFA: true })
   ↓
3. If OK → fetch /api/otp?_user=<username> (to tests-workers)
   ↓
4. tests-workers: redis.set otp:<ts>:<uuid> = { otpCode, ... }
   ↓
5. UI shows OTP screen
   ↓
6. USER / SELENIUM types the OTP code
   ↓
7. login({ pre: false, password, withMFA: true }) → setIsAuthenticated(2)
```

## OTP retrieval on the Ocarina side

```python
# ocarina-example/src/api/retrieve_dashboard_otp_code.py
def retrieve_dashboard_otp_code(*, min_utc_date, timeout, expected_login=None):
    env = create_env_getters()
    igor_api_key = env.get_value("igor_api_key")
    entries = get_otp_history(igor_api_key=igor_api_key, timeout=timeout)

    def _entry_matches(entry):
        expected_user = expected_login or env.get_credentials("dashboard")["login"]
        is_testing_entry = entry["_user"] == expected_user
        if not is_testing_entry:
            return False
        created_at = datetime.fromisoformat(entry["createdAtTimestampLackingMsPrecision"])
        return created_at >= min_utc_date - timedelta(seconds=1)

    matching = list(filter(_entry_matches, entries))
    if not matching:
        return None
    matching.sort(key=lambda e: e["createdAtTimestampLackingMsPrecision"])
    return matching[0]["otpCode"]
```

1. Fetches the **full** OTP history.
2. Filters by `_user`.
3. Filters by `createdAt >= min_utc_date - 1s` (margin for _clock skew_).
4. Sorts ascending by date.
5. Returns the **first match** (the oldest).

The _first_ is the one most likely still in the validity window (an OTP's TTL is 5 min on the `tests-workers` side).

## Coordination via Redis (`OTP_SEND_LOCK_KEY`)

To stop two workers from clicking "_Send OTP_" _at the same time_ (same second) for the same user, `ocarina-example` uses a **distributed Redis lock**:

```python
# pages/dashboard/login.py
def _get_lock() -> RedisLock:
    client = get_redis_client()
    redis_lock: RedisLock = client.lock(OTP_SEND_LOCK_KEY, timeout=60)
    return redis_lock
```

See [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md)

## OTP screen, UI side

```tsx
// src/components/LoginForm.tsx (extract)
if (useOTP && !otpResponse) {
  const success = onLogin({ withMFA: true, pre: true, password });
  if (!success) {
    setError('Invalid credentials. Try any:figatellu');
    return;
  }
  ...
  const response = await fetch(`https://tests-workers.vercel.app/api/otp?_user=${encodeURIComponent(username)}`, {
    headers: { 'x-api-key': otpApiKey },
    signal: abortControllerRef.current.signal
  });
  ...
}
```

1. `login({ pre: true })`&nbsp;—&nbsp;not authenticated yet, just password validation.
2. `fetch('/api/otp?_user=<u>', { headers: { 'x-api-key': <user-typed-key> } })`&nbsp;—&nbsp;fetches an OTP.
3. OTP screen shows, waits for the code.
