---
title: "06.02 — GET /api/otp"
description: "The GET /api/otp endpoint of tests-workers: OTP generation with otplib, Redis storage and a worker-coordination payload."
weight: 2
date: 2026-05-20
series: ["tests-workers"]
series_order: 2
tags: ["otp"]
---

# 06.02&nbsp;—&nbsp;`GET /api/otp`

> Source file: [`api/otp.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/otp.ts)

## Code

```typescript
import { generate } from "otplib";
import type { NextRequest } from "next/server";
import redis from "../lib/redis";
import isAuthorized from "../lib/isAuthorized";

export const config = { runtime: "edge" };

const SECRET_QUERY_PARAM_KEY = "secret";
const OTP_SECRET_MIN_LENGTH = 32;
const OTP_SECRET_MAX_LENGTH = 64;
const BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
const OTP_TTL = 60 * 5; // 5 minutes
const OTP_HISTORY_TTL = OTP_TTL + 60; // 6 minutes
const MAX_FREE_PAYLOAD_SIZE = 4096;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "x-api-key, Content-Type",
} as const;

function generateRandomBase32Secret(length: number = 32): string {
  let secret = "";
  const randomValues = new Uint8Array(length);
  crypto.getRandomValues(randomValues);
  for (let i = 0; i < length; i++) {
    secret += BASE32_ALPHABET[randomValues[i] % 32];
  }
  return secret;
}

function ensureSecretLength(secret: string): string {
  const cleaned = secret.toUpperCase().replace(/\s/g, "");
  if (cleaned.length > OTP_SECRET_MAX_LENGTH) {
    const validLength = Math.floor(OTP_SECRET_MAX_LENGTH / 8) * 8;
    return cleaned.substring(0, validLength);
  }
  if (cleaned.length >= OTP_SECRET_MIN_LENGTH) {
    const validLength = Math.floor(cleaned.length / 8) * 8;
    return cleaned.substring(0, validLength);
  }
  const repetitions = Math.ceil(OTP_SECRET_MIN_LENGTH / cleaned.length);
  const repeated = cleaned.repeat(repetitions);
  const validLength = Math.floor(repeated.length / 8) * 8;
  return repeated.substring(0, Math.max(validLength, OTP_SECRET_MIN_LENGTH));
}

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

  const { searchParams } = new URL(request.url);
  const freePayload: Record<string, string> = {};
  let payloadSize = 0;

  searchParams.forEach((value, key) => {
    if (key === SECRET_QUERY_PARAM_KEY) return;
    const entrySize = new TextEncoder().encode(key + value).length;
    if (payloadSize + entrySize > MAX_FREE_PAYLOAD_SIZE) {
      payloadSize += entrySize;
      return;
    }
    freePayload[key] = value;
    payloadSize += entrySize;
  });

  if (payloadSize > MAX_FREE_PAYLOAD_SIZE) {
    return new Response(
      JSON.stringify({
        error: "Bad Request",
        message: `Free payload exceeds maximum size of ${MAX_FREE_PAYLOAD_SIZE} bytes (got ${payloadSize} bytes)`,
      }),
      {
        status: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders },
      },
    );
  }

  const rawSecret =
    searchParams.get(SECRET_QUERY_PARAM_KEY) ?? generateRandomBase32Secret();
  const secret = ensureSecretLength(rawSecret);
  const otpCode = await generate({ secret });
  const now = Date.now();
  const expiresAtMs = now + OTP_TTL * 1000;
  const createdAtTimestampLackingMsPrecision = new Date(
    now - (now % 1000),
  ).toISOString();

  const event = {
    ...freePayload,
    otpCode,
    secret,
    createdAtTimestampLackingMsPrecision,
    expiresAt: new Date(expiresAtMs).toISOString(),
  };

  const key = `otp:${now}:${crypto.randomUUID()}`;
  await redis.set(key, JSON.stringify(event), { ex: OTP_HISTORY_TTL });

  return new Response(JSON.stringify(event), {
    headers: { "Content-Type": "application/json", ...corsHeaders },
  });
}
```

## Flow

```
1. Request arrives
   ↓
2. If OPTIONS → 200 + CORS headers (preflight)
   ↓
3. isAuthorized(request)? No → 401
   ↓
4. Parse searchParams; everything except "secret" goes into freePayload
   ↓
5. payloadSize > 4 KB? → 400
   ↓
6. secret = ?secret=<X> (if given) else random Base32 32-chars
   ↓
7. ensureSecretLength: enforces 32..64 chars, multiple of 8
   ↓
8. otpCode = generate({ secret })   ← otplib TOTP RFC 6238
   ↓
9. createdAt = floor(now / 1000) * 1000  ← ms stripped
   ↓
10. event = { ...freePayload, otpCode, secret, createdAt, expiresAt }
    ↓
11. key = `otp:<now>:<uuid>`
    ↓
12. redis.set(key, JSON.stringify(event), { ex: 360 })  ← TTL 6 min
    ↓
13. Response = JSON.stringify(event), 200
```

## CORS headers

```typescript
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "x-api-key, Content-Type",
} as const;
```

- `*` origin: lets Igoristan (`https://mojo-molotov.github.io`) call the service.
- `GET, OPTIONS`: the only supported verbs.
- `x-api-key` listed explicitly&nbsp;—&nbsp;otherwise the browser blocks it as a non-simple header.

`as const` makes the object readonly on the TypeScript side.

## Free payload

```typescript
searchParams.forEach((value, key) => {
  if (key === SECRET_QUERY_PARAM_KEY) return;
  const entrySize = new TextEncoder().encode(key + value).length;
  if (payloadSize + entrySize > MAX_FREE_PAYLOAD_SIZE) {
    payloadSize += entrySize;
    return;
  }
  freePayload[key] = value;
  payloadSize += entrySize;
});
```

1. Every query param **except** `secret` goes into the free payload.
2. If adding an entry would exceed 4 KB, stop adding (but keep counting for the final check).
3. Overflow globally → 400 Bad Request.

Why a free payload? So any field (typically `_user`) gets stored with the event.

Igoristan sends `?_user=<username>` → lands in `event._user` → Ocarina retrieves the OTP by filtering on `_user` and timestamp.

## Secret generation (Base32)

```typescript
function generateRandomBase32Secret(length: number = 32): string {
  let secret = "";
  const randomValues = new Uint8Array(length);
  crypto.getRandomValues(randomValues);
  for (let i = 0; i < length; i++) {
    secret += BASE32_ALPHABET[randomValues[i] % 32];
  }
  return secret;
}
```

1. **`crypto.getRandomValues`**: native Web CSPRNG, works on Edge.
2. **Base32 alphabet**: `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567`&nbsp;—&nbsp;32 chars, RFC 4648.
3. **`% 32`**: maps a random byte (0–255) to an index 0–31 (`256 / 32 = 8`, perfectly uniform).

## `ensureSecretLength`

If a custom `secret` is in the query, we enforce three constraints:

1. Length ≥ 32.
2. Length ≤ 64.
3. Length is a multiple of 8 (TOTP RFC requirement).

Too short → repeat. Too long → truncate. Otherwise → truncate to the nearest multiple of 8.

This lets a caller pass `?secret=foo` without crashing: `foo` is too short, so it gets repeated → `foofoofoofoo...` → truncated to a multiple of 8.

## Redis `key`

```typescript
const key = `otp:${now}:${crypto.randomUUID()}`;
```

`otp:<timestamp_ms>:<uuid>`.

1. The `otp:` prefix makes `SCAN MATCH otp:*` work on the history side.
2. `<timestamp_ms>` gives a rough lexico-semantic sort (Redis doesn't sort, but you can sort client-side).
3. `<uuid>` guarantees uniqueness when two Edge workers write at the same millisecond.

## TTL

```typescript
const OTP_TTL = 60 * 5; // 5 min — OTP validity duration
const OTP_HISTORY_TTL = OTP_TTL + 60; // 6 min — Redis lifetime
```

The OTP is valid for 5 min, but we keep it in Redis for 6. That extra minute is a buffer for `/api/otp-history` arriving just after the OTP technically expires.

## _Timestamp_ imprecision

```typescript
const createdAtTimestampLackingMsPrecision = new Date(
  now - (now % 1000),
).toISOString();
```

Milliseconds stripped on purpose:

`now = 1715952473123` → `now - (now % 1000) = 1715952473000` → `"2024-05-17T13:27:53.000Z"`

The variable name is the comment: `createdAtTimestampLackingMsPrecision`.

See [`07-otp-coordination-flow.md`](07-otp-coordination-flow.md) for why.

## _Event_ format

```typescript
const event = {
  ...freePayload, // e.g. _user, env, userId
  otpCode, // e.g. "123456"
  secret, // e.g. "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"
  createdAtTimestampLackingMsPrecision, // "2024-05-17T13:27:53.000Z"
  expiresAt: new Date(expiresAtMs).toISOString(), // "2024-05-17T13:32:53.123Z"
};
```

`expiresAt` keeps milliseconds. Only `createdAt` is stripped.

`expiresAt` is informational&nbsp;—&nbsp;Ocarina doesn't filter on it. The filter uses `createdAt`, and its second-level precision is what drives the `_user` + timing-delta coordination strategy.

## HTTP response

```typescript
return new Response(JSON.stringify(event), {
  headers: { "Content-Type": "application/json", ...corsHeaders },
});
```

Default status: 200. Body = event JSON. CORS headers included so Igoristan can call from the browser.
