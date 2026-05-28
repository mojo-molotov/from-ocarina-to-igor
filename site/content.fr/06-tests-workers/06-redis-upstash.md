---
title: "06.06 — lib/redis.ts + Upstash"
description: "lib/redis.ts : le client Upstash Redis de tests-workers, configuré par variables d'environnement pour le runtime Edge."
weight: 6
date: 2026-05-20
series: ["tests-workers"]
series_order: 6
---

# 06.06&nbsp;—&nbsp;`lib/redis.ts` + Upstash

> Fichier source&nbsp;: [`lib/redis.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/lib/redis.ts)

## Code

```typescript
import { Redis } from "@upstash/redis";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

export default redis;
```

## Pourquoi `@upstash/redis` plutôt que `ioredis`

| Critère          | `ioredis`         | `@upstash/redis`            |
| ---------------- | ----------------- | --------------------------- |
| Protocole        | TCP /&nbsp;RESP   | HTTP /&nbsp;REST            |
| Edge runtime     | ❌ Non            | ✅ Oui                      |
| Connexion        | Persistante       | Per-request                 |
| Latence (_warm_) | < 1ms             | 50-100ms                    |
| Latence (_cold_) | 200ms+            | 50-100ms                    |
| Coût             | Variable          | Pay-per-request             |
| Setup            | Self-hosted Redis | Upstash dashboard (managed) |

L'_Edge runtime_ n'accepte **pas** de connexions TCP persistantes (chaque _worker_ est éphémère).  
Donc&nbsp;: Upstash REST.

## Singleton

```typescript
const redis = new Redis({...});
export default redis;
```

L'instance est créée _une seule fois_ à l'import du module (_cold start_).  
Elle est réutilisée pour toutes les requêtes du _worker_.

Avec un trafic raisonnable, le _worker_ reste _warm_.

## Consommation des variables d'environnement

```typescript
url: process.env.UPSTASH_REDIS_REST_URL,
token: process.env.UPSTASH_REDIS_REST_TOKEN,
```

```
UPSTASH_REDIS_REST_URL    = "https://us1-something-12345.upstash.io"
UPSTASH_REDIS_REST_TOKEN  = "AcdefGHi..."
```

Le token est un _JWT-like_ généré par Upstash, scopé à une base Redis spécifique.

## `vercel env add`

Le README détaille&nbsp;:

```bash
vercel env add API_SECRET
vercel env add UPSTASH_REDIS_REST_URL
vercel env add UPSTASH_REDIS_REST_TOKEN
vercel deploy
```

→ Trois `vercel env add`, puis `vercel deploy`.  
Pas de config locale nécessaire.

## API

| Méthode Redis                          | Endpoint           | Usage               |
| -------------------------------------- | ------------------ | ------------------- |
| `redis.set(key, value, { ex: ttl })`   | `/api/otp`         | `SET` avec TTL      |
| `redis.scan(cursor, { match, count })` | `/api/otp-history` | `SCAN` cursor-based |
| `redis.mget(...keys)`                  | `/api/otp-history` | `MGET` (Multi-get)  |

## Gestion des erreurs

`@upstash/redis` lève en cas d'erreur réseau ou serveur.  
Le code _ne catch pas_&nbsp;: les erreurs remontent au _handler_ de Vercel, qui répond `500 Internal Server Error`.

1. Du côté de l'Igoristan&nbsp;: l'utilisateur voit une erreur OTP, peut retry.
2. Côté Ocarina&nbsp;: `transient_errors` catch et retry.

## Absence de timeout explicite

```typescript
const redis = new Redis({
  url: ...,
  token: ...,
});
```

Pas de `timeout` configuré. `@upstash/redis` a un default (typiquement 5s).

L'_Edge runtime_ a son propre timeout (10s par défaut côté Vercel).  
Donc même si `@upstash/redis` ne timeout pas, Vercel coupe la _Edge Function_.
