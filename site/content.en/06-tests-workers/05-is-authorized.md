---
title: "06.05 — isAuthorized.ts"
weight: 5
date: 2026-05-20
series: ["tests-workers"]
series_order: 5
---

# 06.05&nbsp;—&nbsp;`isAuthorized.ts`

> Source file: [`lib/isAuthorized.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/lib/isAuthorized.ts)
>
> Verifies that a request contains the right `x-api-key`.

## Code

```typescript
import type { NextRequest } from "next/server";

const API_SECRET = process.env.API_SECRET;

function isAuthorized(request: NextRequest): boolean {
  if (typeof API_SECRET !== "string") {
    console.error("[CONFIG ERROR] API_SECRET is not defined");
    return false;
  }

  const { searchParams } = new URL(request.url);
  const apiKey = searchParams.get("apiKey") ?? request.headers.get("x-api-key");
  return apiKey === API_SECRET;
}

export default isAuthorized;
```

## Approach

### 1. `API_SECRET`

```typescript
const API_SECRET = process.env.API_SECRET;
```

Read once at Edge worker startup (cold start), stored as a module variable. Faster than hitting `process.env` on every call.

### 2. `typeof !== "string"` guard

```typescript
if (typeof API_SECRET !== "string") {
  console.error("[CONFIG ERROR] API_SECRET is not defined");
  return false;
}
```

Undefined env var → log + refuse. No startup panic. Fail-safe: auth is refused, so a missing env var can't be exploited.

### 3. Key passing

```typescript
const apiKey = searchParams.get("apiKey") ?? request.headers.get("x-api-key");
```

1. **Query string** `?apiKey=<X>`.
2. **Header** `x-api-key: <X>` (fallback).

| Case                       | Where                                                 |
| -------------------------- | ----------------------------------------------------- |
| cURL                       | Query string (simpler, no need for `-H`)              |
| Production / browser fetch | Header (_best practice_, doesn't show in server logs) |

The README documents both:

```bash
curl -H "x-api-key: SECRET" "https://.../api/otp"
curl "https://.../api/otp?apiKey=SECRET"           # same thing
```

## Export/import

```typescript
export default isAuthorized;
```

```typescript
import isAuthorized from "../lib/isAuthorized";
```

## No _rate-limit_

No rate-limiting. An attacker with the right `API_SECRET` could spam&nbsp;—&nbsp;but they'd need the secret first, and the Vercel Free Tier caps requests at ~100 req/s anyway. Application-level rate-limiting isn't needed here.

## `console.error`

```typescript
console.error("[CONFIG ERROR] API_SECRET is not defined");
```

`console.*` in an Edge Function shows up in the Vercel dashboard logs. If `API_SECRET` is undefined, the maintainer sees it immediately.
