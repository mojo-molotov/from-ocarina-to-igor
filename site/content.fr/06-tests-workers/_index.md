---
title: "Chapitre 06 — tests-workers, backend Vercel Edge"
description: "Trois endpoints HTTP, deux libs (@upstash/redis, otplib), zéro Next.js applicatif. Le strict minimum pour coordonner des tests parallèles sur l'Igoristan."
weight: 7
date: 2026-05-20
tags: ["tests-workers", "otp"]
sidebar:
  open: true
---

# Chapitre 06&nbsp;—&nbsp;`tests-workers`, backend Vercel Edge

> Trois endpoints HTTP, deux libs (`@upstash/redis`, `otplib`), zéro Next.js applicatif. Le strict minimum pour _coordonner_ des tests parallèles sur l'Igoristan.

## Plan

|  #  | Fichier                                                      | Sujet                                                                      |
| :-: | ------------------------------------------------------------ | -------------------------------------------------------------------------- |
| 01  | [`01-stack-edge.md`](01-stack-edge.md)                       | Stack Vercel Edge Functions, `runtime: "edge"`, Upstash Redis, `otplib`.   |
| 02  | [`02-otp-endpoint.md`](02-otp-endpoint.md)                   | `GET /api/otp`&nbsp;—&nbsp;génération + Redis SET + free payload.          |
| 03  | [`03-otp-history.md`](03-otp-history.md)                     | `GET /api/otp-history`&nbsp;—&nbsp;SCAN Redis + retour de tous les events. |
| 04  | [`04-corsicadex.md`](04-corsicadex.md)                       | `GET /api/corsicadex?id=N`&nbsp;—&nbsp;lookup statique.                    |
| 05  | [`05-is-authorized.md`](05-is-authorized.md)                 | `isAuthorized.ts`&nbsp;—&nbsp;`x-api-key` vs `apiKey` query param.         |
| 06  | [`06-redis-upstash.md`](06-redis-upstash.md)                 | `lib/redis.ts`&nbsp;—&nbsp;config Upstash.                                 |
| 07  | [`07-otp-coordination-flow.md`](07-otp-coordination-flow.md) | Le flux complet OTP&nbsp;: Igoristan ↔ workers ↔ Ocarina ↔ Redis.          |

## Objectifs

- 3 endpoints `.ts`.
- 2 fichiers `lib/`.
- 1 fichier `consts/`.
- Total&nbsp;: ~7 fichiers TypeScript de code, plus `package.json` et `vercel.json`.

L'objectif&nbsp;: être _déployable en 30 secondes_ par un humain.

```
→ pnpm install
→ vercel env add API_SECRET
→ vercel env add UPSTASH_REDIS_REST_URL
→ vercel env add UPSTASH_REDIS_REST_TOKEN
→ vercel deploy
```

Note&nbsp;: c'est le seul dépôt de l'écosystème en **ISC** (et pas MIT).  
Choix par défaut du scaffold Vercel, conservé.

## Lectures connexes

- Comment l'Igoristan appelle ces endpoints&nbsp;: [`../05-igoristan/03-use-auth.md`](../05-igoristan/03-use-auth.md), [`../05-igoristan/02-routes.md`](../05-igoristan/02-routes.md) (Corsicamon).
- Comment Ocarina récupère l'OTP&nbsp;: [`../07-ocarina-example/`](../07-ocarina-example/README.md)
