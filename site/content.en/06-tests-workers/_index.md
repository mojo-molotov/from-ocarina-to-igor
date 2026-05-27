---
title: "Chapter 06 — tests-workers, Vercel Edge backend"
description: "Three HTTP endpoints, two libs (@upstash/redis, otplib), zero Next.js app code. The bare minimum to coordinate parallel tests against Igoristan."
weight: 7
date: 2026-05-20
tags: ["tests-workers", "otp"]
sidebar:
  open: true
---

# Chapter 06&nbsp;—&nbsp;`tests-workers`, Vercel Edge backend

> Three HTTP endpoints, two libs (`@upstash/redis`, `otplib`), zero Next.js app code. The bare minimum to _coordinate_ parallel tests against Igoristan.

## Outline

|  #  | File                                                         | Topic                                                                    |
| :-: | ------------------------------------------------------------ | ------------------------------------------------------------------------ |
| 01  | [`01-stack-edge.md`](01-stack-edge.md)                       | Stack Vercel Edge Functions, `runtime: "edge"`, Upstash Redis, `otplib`. |
| 02  | [`02-otp-endpoint.md`](02-otp-endpoint.md)                   | `GET /api/otp`&nbsp;—&nbsp;generation + Redis SET + free payload.        |
| 03  | [`03-otp-history.md`](03-otp-history.md)                     | `GET /api/otp-history`&nbsp;—&nbsp;Redis SCAN + return of every event.   |
| 04  | [`04-corsicadex.md`](04-corsicadex.md)                       | `GET /api/corsicadex?id=N`&nbsp;—&nbsp;static lookup.                    |
| 05  | [`05-is-authorized.md`](05-is-authorized.md)                 | `isAuthorized.ts`&nbsp;—&nbsp;`x-api-key` vs `apiKey` query param.       |
| 06  | [`06-redis-upstash.md`](06-redis-upstash.md)                 | `lib/redis.ts`&nbsp;—&nbsp;Upstash config.                               |
| 07  | [`07-otp-coordination-flow.md`](07-otp-coordination-flow.md) | Full OTP flow: Igoristan ↔ workers ↔ Ocarina ↔ Redis.                    |

## Goals

- 3 `.ts` endpoints.
- 2 `lib/` files.
- 1 `consts/` file.
- Total: ~7 TypeScript code files, plus `package.json` and `vercel.json`.

Goal: _deployable in 30 seconds_ by a human.

```
→ pnpm install
→ vercel env add API_SECRET
→ vercel env add UPSTASH_REDIS_REST_URL
→ vercel env add UPSTASH_REDIS_REST_TOKEN
→ vercel deploy
```

Note: the only repo in the ecosystem under **ISC** (not MIT).  
Vercel scaffold default, kept as-is.

## Related reading

- How Igoristan calls these endpoints: [`../05-igoristan/03-use-auth.md`](../05-igoristan/03-use-auth.md), [`../05-igoristan/02-routes.md`](../05-igoristan/02-routes.md) (Corsicamon).
- How Ocarina retrieves the OTP: [`../07-ocarina-example/`](../07-ocarina-example/)
