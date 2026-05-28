---
title: "07.08 — L1 cache + reserved keys + distributed Redis locks"
description: "The in-memory L1 cache and distributed Redis locks of ocarina-example: sharing values within a test, serializing a click across workers."
weight: 8
date: 2026-05-20
series: ["ocarina-example"]
series_order: 8
---

# 07.08&nbsp;—&nbsp;L1 cache + reserved keys + distributed Redis locks

> Internal coordination mechanics: an in-memory cache to share values _within a test_, a Redis lock to serialize a click _across several workers_.

## L1 cache

```python
# src/caches/l1.py
from dogpile.cache import make_region

in_memory_cache_with_30m_ttl = make_region().configure(
    "dogpile.cache.memory", expiration_time=30 * 60
)
```

One global cache, `dogpile.cache.memory` backend, 30-minute TTL. Everything in RAM&nbsp;—&nbsp;no Redis for local-process state.

## Why an L1 cache?

Ocarina's DSL is **static**: a scenario describes a sequence of `act`s. But sometimes you need to **share a value** between two acts:

1. The first act clicks "_Send OTP_" → we note the date.
2. The second act retrieves the OTP by passing that date to `retrieve_dashboard_otp_code(min_utc_date=...)`.

## `reserve_free_cache_key`

```python
# src/caches/reserve_free_cache_key.py
import uuid
from threading import Lock
from dogpile.cache.api import NO_VALUE

_RESERVED_VALUE: Final[str] = "__RESERVED__"
_lock = Lock()


def reserve_free_cache_key(region: CacheRegion) -> str:
    while True:
        key_candidate = str(uuid.uuid4())
        with _lock:
            if region.get(key_candidate) == NO_VALUE:
                region.set(key_candidate, _RESERVED_VALUE)
                return key_candidate
```

1. Generate a UUID.
2. Acquire the local `threading.Lock`.
3. If the key is free (`NO_VALUE`): mark it `"__RESERVED__"` and return it.
4. Otherwise: loop.

The lock prevents a race between the `get` and the `set`.

## Example

```python
cache = in_memory_cache_with_30m_ttl
fresh_cache_key_for_username = reserve_free_cache_key(cache)
fresh_cache_key_for_otp_send_button_click_date = reserve_free_cache_key(cache)

return [
    drive_page(
        act(on_dashboard_login_page,
            start_to_login_with_otp_and_with_retries(
                dashboard_creds, retries_amount,
                cache=cache, logger=logger,
                username_cache_key=fresh_cache_key_for_username,
                otp_send_button_click_date_cache_key=fresh_cache_key_for_otp_send_button_click_date,
            ))...,
        act(on_dashboard_login_page,
            type_otp_with_retries(
                retries_amount,
                cache=cache, logger=logger,
                username_cache_key=fresh_cache_key_for_username,
                otp_send_button_click_date_cache_key=fresh_cache_key_for_otp_send_button_click_date,
            ))...,
    ),
]
```

Two reserved keys (`username` and `otp_send_date`), passed to both connectors.

The first connector **writes** the click date. The second **reads** it to filter the matching OTP via `retrieve_dashboard_otp_code(min_utc_date=...)`.

## Why UUIDs and not static names

```python
fresh_cache_key_for_username = reserve_free_cache_key(cache)
# = "f3a7b2c4-12d4-4abc-..."
```

Using `"username"` directly would let two parallel tests overwrite each other's entry. UUID guarantees uniqueness.

`dogpile.cache.memory` is shared across all threads in one process. Parallel tests share the same cache, so strict key uniqueness is required.

## Distributed lock (Redis)

For inter-process coordination (multiple terminals) or inter-machine (horizontal scaling):

```python
# src/lib/ext/redis/client.py
from threading import Lock
import redis as _redis

_init_lock = Lock()
_redis_client: _redis.StrictRedis | None = None


def get_redis_client() -> _redis.StrictRedis:
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    with _init_lock:
        if _redis_client is not None:
            return _redis_client
        redis_url = create_env_getters().get_value("redis_url")
        client = _redis.StrictRedis.from_url(redis_url)
        client.ping()
        _redis_client = client

    return _redis_client


def warmup_redis_client() -> None:
    get_redis_client()
```

## `DashboardLoginPage`

```python
# pages/dashboard/login.py
from constants.sys.redis_keys import OTP_SEND_LOCK_KEY

def _get_lock() -> RedisLock:
    client = get_redis_client()
    redis_lock: RedisLock = client.lock(OTP_SEND_LOCK_KEY, timeout=60)
    return redis_lock


class DashboardLoginPage(...):
    def start_to_login_with_otp(self, creds, *, cache, ...):
        lock = _get_lock()
        with lock:                                # ← serializes every "Send OTP" click
            self._click_send_otp()
            now = datetime.now(UTC)
            cache.set(otp_send_button_click_date_cache_key, now.isoformat())
            cache.set(username_cache_key, creds["login"])
        return self
```

`with lock` is a context manager:

1. On entry: Redis `SETNX` with a 60s timeout (prevents distributed deadlock on crash).
2. Already locked: wait.
3. On exit: Redis `DEL`.

Across N machines in parallel, only one worker at a time can click "Send OTP".

## `OTP_SEND_LOCK_KEY`

```python
# src/constants/sys/redis_keys.py
OTP_SEND_LOCK_KEY = "ocarina_example:otp_send_lock"
```

Naming convention: `<project>:<purpose>`.

## `warmup_redis_client`

```python
# src/main.py
logger.info("Warming up the Redis client...")
warmup_redis_client()
logger.success("Redis client initialized!")
```

Forces client creation before tests start. If Redis is down, we know immediately&nbsp;—&nbsp;not mid-test.

## Recap

| Mechanism                                    | Type                          | Scope                                                | Use                                                                                            |
| -------------------------------------------- | ----------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `in_memory_cache_with_30m_ttl`               | `dogpile.cache.memory`        | Process (impacts every worker in an Ocarina process) | Share values pulled from the test execution context across the test steps of a single scenario |
| `reserve_free_cache_key`                     | UUID + `threading.Lock`       | Thread-safe                                          | Reserve a _unique_ key in the cache                                                            |
| `get_redis_client`                           | `redis.StrictRedis` Singleton | Process                                              | Access Redis                                                                                   |
| `client.lock(OTP_SEND_LOCK_KEY, timeout=60)` | Redis `SETNX`                 | Multi-process / multi-machine                        | Force tests to wait their turn                                                                 |

## Holy Book reminder

Chapter "First jutsus", section "_Reactive programming: NO_":

> Ocarina test scenarios are intentionally static.  
> Yet a web application is dynamic, and sometimes capturing a value on the fly to pass it to a later step is perfectly legitimate.
>
> Ocarina doesn't answer that. It doesn't need to.
>
> ### Architectural answer
>
> What we're after here is an _in-memory cache_.
>
> We generate keys just before the test chain kicks off, and pass them to the POM actions. Actions write and read through a unique key. The scenario just hands them out.

And:

> **Locks**: `threading.Lock` if a single process at a time, otherwise Redis distributed locks are enough (`redis.StrictRedis` + `redis.lock`).

Clear convention: in-memory for a single Ocarina process, Redis when you need coordination across multiple processes or machines.
