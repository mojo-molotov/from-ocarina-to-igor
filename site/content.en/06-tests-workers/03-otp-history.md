---
title: "06.03 — GET /api/otp-history"
description: "Source file: api/otp-history.ts"
weight: 3
date: 2026-05-20
series: ["tests-workers"]
series_order: 3
tags: ["otp"]
---

# 06.03&nbsp;—&nbsp;`GET /api/otp-history`

> Source file: [`api/otp-history.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/otp-history.ts)

## Code

```typescript
import type { NextRequest } from "next/server";
import redis from "../lib/redis";
import isAuthorized from "../lib/isAuthorized";

export const config = { runtime: "edge" };

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "x-api-key, Content-Type",
} as const;

export default async function handler(request: NextRequest) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  if (!isAuthorized(request)) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json", ...corsHeaders },
    });
  }

  let cursor = "0";
  const allEvents = [];
  const BATCH_SIZE = 100;

  do {
    const [newCursor, keys] = await redis.scan(cursor, {
      match: "otp:*",
      count: BATCH_SIZE,
    });
    cursor = newCursor;

    if (keys.length > 0) {
      const values = await redis.mget(...keys);
      allEvents.push(...values.filter(Boolean));
    }
  } while (cursor !== "0");

  return new Response(JSON.stringify(allEvents), {
    headers: { "Content-Type": "application/json", ...corsHeaders },
  });
}
```

## Redis `SCAN` mechanics

```typescript
let cursor = "0";
const allEvents = [];
const BATCH_SIZE = 100;

do {
  const [newCursor, keys] = await redis.scan(cursor, {
    match: "otp:*",
    count: BATCH_SIZE,
  });
  cursor = newCursor;

  if (keys.length > 0) {
    const values = await redis.mget(...keys);
    allEvents.push(...values.filter(Boolean));
  }
} while (cursor !== "0");
```

1. `cursor = "0"` (initialization).
2. Loop:
   - `SCAN <cursor> MATCH otp:* COUNT 100` returns `[newCursor, keys]`.
   - If `keys` non-empty: `MGET k1 k2 ...` fetches the values.
   - `cursor = newCursor`.
3. We stop when `cursor === "0"` (cycle complete).

Why `SCAN` rather than `KEYS`?

| `KEYS otp:*`               | `SCAN 0 MATCH otp:*`    |
| -------------------------- | ----------------------- |
| Blocks the Redis server    | Iterative, non-blocking |
| Returns everything at once | Pages of N              |
| **Discouraged in prod**    | **Recommended**         |

For 1000 `otp:*` keys, that's ~10 round-trips.

## Why `MGET` rather than individual `GET`s?

`MGET k1 k2 ... kN` is **one** round-trip for N values. Individual `GET` calls would be N round-trips.

On Upstash REST, each round-trip costs ~50ms. 100 individual GETs = 5 seconds.

## `.filter(Boolean)`

```typescript
allEvents.push(...values.filter(Boolean));
```

`MGET` returns `null` for keys that expired between the `SCAN` and the `MGET`. `.filter(Boolean)` drops those nulls.

## Result

```typescript
return new Response(JSON.stringify(allEvents), {
  headers: { "Content-Type": "application/json", ...corsHeaders },
});
```

```json
[
  {
    "_user": "SacredFigatellu",
    "otpCode": "123456",
    "secret": "...",
    "createdAtTimestampLackingMsPrecision": "2024-05-17T13:27:53.000Z",
    "expiresAt": "2024-05-17T13:32:53.123Z"
  },
  {
    "_user": "Napoleon",
    "otpCode": "789012",
    ...
  },
  ...
]
```

## Security

```typescript
if (!isAuthorized(request)) {
  return new Response(JSON.stringify({ error: "Unauthorized" }),
    { status: 401, ... });
}
```

Wrong or missing `x-api-key` → 401. History is only readable by someone who knows `API_SECRET`.

## Contract with Ocarina

`ocarina-example/api/get_otp_history.py`:

```python
def get_otp_history(*, igor_api_key: str, timeout: int) -> list[dict[str, Any]]:
    response = requests.get(
        "https://tests-workers.vercel.app/api/otp-history",
        headers={"x-api-key": igor_api_key},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
```

Plain GET, `x-api-key` header, parse JSON. No pagination needed&nbsp;—&nbsp;the endpoint aggregates everything server-side.

## Cost

For 100 _events_ in Redis:

- 1 `SCAN` → 100 keys returned (1 _round-trip_).
- 1 `MGET` of 100 keys → 100 values (1 _round-trip_).
- Total: 2 _round-trips_.

For 1000 _events_:

- 10 `SCAN`s.
- 10 `MGET`s.
- Total: 20 _round-trips_.

At ~50ms per round-trip, 1000 events takes ~1s total.

## "_Shared history_" semantics

Every OTP from any worker (human or Selenium, any user) lands in Redis. Filtering by `_user` is client-side.

1. **Server simplicity**: no filter logic, just dump everything.
2. **Flexibility**: clients can filter by `_env`, `_userId`, or any free-payload field the server doesn't know about.
3. **Manageable volume**: 6 min TTL × N OTP/sec = a few hundred entries at most.

Smart Client / Dumb Server: logic lives in the tests, the server just dumps.
