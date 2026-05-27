---
title: "06.01 — Vercel Edge stack"
weight: 1
date: 2026-05-20
series: ["tests-workers"]
series_order: 1
tags: ["otp"]
---

# 06.01&nbsp;—&nbsp;Vercel Edge stack

## `package.json`

```json
{
  "name": "tests-workers",
  "version": "1.0.0",
  "scripts": {
    "vercel-build": "echo 'Build skipped'"
  },
  "packageManager": "pnpm@11.2.2",
  "dependencies": {
    "@upstash/redis": "^1.36.2",
    "otplib": "^13.2.1"
  },
  "devDependencies": {
    "@types/node": "^25.2.0",
    "next": "^16.1.6",
    "@vercel/node": "^5.5.28",
    "typescript": "^5.9.3"
  },
  "license": "ISC"
}
```

| Lib                            | Role                                           |
| ------------------------------ | ---------------------------------------------- |
| **`@upstash/redis`** (runtime) | _REST_ Redis client (no TCP). Edge-compatible. |
| **`otplib`** (runtime)         | RFC 6238 TOTP generation.                      |
| **`next`** (dev only)          | _Types_ only (`NextRequest`). No Next.js app.  |
| **`@vercel/node`** (dev only)  | Vercel types.                                  |
| **`@types/node`** (dev only)   | Node 22+ types.                                |

**No** runtime dependency beyond `@upstash/redis` + `otplib`. Bundle is microscopic → cold start < 100ms.

## `vercel.json`

```json
{
  "version": 2,
  "buildCommand": "echo 'No build required'",
  "outputDirectory": ".",
  "framework": null
}
```

| Field                                      | Value                 | Effect                                                      |
| ------------------------------------------ | --------------------- | ----------------------------------------------------------- |
| `version: 2`                               | Vercel v2             | &nbsp;—&nbsp;                                               |
| `buildCommand: "echo 'No build required'"` | No build              | TypeScript is transpiled _on the fly_ by the Vercel runtime |
| `outputDirectory: "."`                     | Repo root             | No `dist/` to produce                                       |
| `framework: null`                          | No framework detected | Vercel doesn't auto-config                                  |

## The Edge runtime

Each endpoint declares:

```typescript
export const config = { runtime: "edge" };
```

| Aspect                                   | Edge Functions                     | Node Serverless |
| ---------------------------------------- | ---------------------------------- | --------------- |
| Cold start                               | < 50ms                             | 200–500ms       |
| Memory                                   | ~128 MB                            | up to 3 GB      |
| Node API                                 | Limited (no `fs`, `child_process`) | Full Node       |
| Geo                                      | Co-located with the user           | Single region   |
| `fetch`, `crypto.getRandomValues`, `URL` | Native                             | Native          |
| Pricing                                  | Cheaper                            | More expensive  |

For 3 endpoints that do only **HTTP + Redis**, _Edge_ is the right pick.

## Why `next` is in `devDependencies`

```typescript
import type { NextRequest } from "next/server";
```

`tests-workers` uses Next.js for one thing: the `NextRequest` type. No Next.js app. Vercel publishes those types because they're compatible with Edge Functions.

At runtime the object is a standard `Request`, but typed as `NextRequest` for autocomplete on `searchParams` helpers and friends.

## Why Upstash rather than a classic Redis

| Classic Redis (TCP)    | Upstash (REST)             |
| ---------------------- | -------------------------- |
| Persistent connection  | HTTP per request           |
| Not Edge-compatible    | Edge-compatible            |
| Faster on multi-ops    | Simpler on single-op       |
| Self-hosted or managed | Managed (Cloudflare-style) |

Edge has no TCP socket. Upstash exposes Redis over HTTP+REST.

## `API_SECRET`

```typescript
const API_SECRET = process.env.API_SECRET;
```

Read at cold start. Stays in memory for the lifetime of the worker instance (which can serve N requests).

## `UPSTASH_REDIS_REST_*`

```typescript
// lib/redis.ts
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});
```

1. `UPSTASH_REDIS_REST_URL`: the HTTPS URL of the Upstash Redis.
2. `UPSTASH_REDIS_REST_TOKEN`: the Bearer token to authenticate.

`vercel env add ...` (see README).

## Why only 3 endpoints

| Endpoint               | Why                                             |
| ---------------------- | ----------------------------------------------- |
| `/api/otp?_user=<u>`   | Generates an OTP for the MFA login test         |
| `/api/otp-history`     | Gives Ocarina the OTP Igoristan just generated  |
| `/api/corsicadex?id=N` | Provides data for the "_Corsican Pokédex_" page |

No _webhook_, no _polling_, no DB other than Redis. The **bare minimum.**
