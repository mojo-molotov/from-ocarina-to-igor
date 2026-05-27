---
title: "06.01 — Stack Vercel Edge"
weight: 1
date: 2026-05-20
series: ["tests-workers"]
series_order: 1
tags: ["otp"]
---

# 06.01&nbsp;—&nbsp;Stack Vercel Edge

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

| Lib                                | Rôle                                                   |
| ---------------------------------- | ------------------------------------------------------ |
| **`@upstash/redis`** (runtime)     | Client Redis _REST_ (pas TCP). Compatible Edge.        |
| **`otplib`** (runtime)             | Génération TOTP RFC 6238.                              |
| **`next`** (dev seulement)         | _Types_ uniquement (`NextRequest`). Pas d'app Next.js. |
| **`@vercel/node`** (dev seulement) | Types Vercel.                                          |
| **`@types/node`** (dev seulement)  | Types Node 22+.                                        |

Note&nbsp;: **aucune** dépendance runtime au-delà de `@upstash/redis` + `otplib`.  
Le bundle est microscopique&nbsp;→&nbsp;cold start&nbsp;<&nbsp;100ms.

## `vercel.json`

```json
{
  "version": 2,
  "buildCommand": "echo 'No build required'",
  "outputDirectory": ".",
  "framework": null
}
```

| Champ                                      | Valeur                   | Effet                                                       |
| ------------------------------------------ | ------------------------ | ----------------------------------------------------------- |
| `version: 2`                               | Vercel v2                | &nbsp;—&nbsp;                                               |
| `buildCommand: "echo 'No build required'"` | Pas de build             | TypeScript est transpilé _à la volée_ par le runtime Vercel |
| `outputDirectory: "."`                     | Racine du repo           | Pas de `dist/` à produire                                   |
| `framework: null`                          | Pas de framework détecté | Vercel ne fait pas d'auto-config                            |

## Le runtime Edge

Chaque endpoint déclare&nbsp;:

```typescript
export const config = { runtime: "edge" };
```

| Aspect                                   | Edge Functions                        | Node Serverless |
| ---------------------------------------- | ------------------------------------- | --------------- |
| Cold start                               | < 50ms                                | 200-500ms       |
| Mémoire                                  | ~128 MB                               | jusqu'à 3 GB    |
| API Node                                 | Limité (pas de `fs`, `child_process`) | Full Node       |
| Geo                                      | Co-localisée à l'utilisateur          | Région unique   |
| `fetch`, `crypto.getRandomValues`, `URL` | Native                                | Native          |
| Tarification                             | Moins cher                            | Plus cher       |

Pour 3 endpoints qui ne font qu'**HTTP + Redis**, _Edge_ est le bon choix.

## Pourquoi `next` est en `devDependencies`

```typescript
import type { NextRequest } from "next/server";
```

`tests-workers` n'utilise Next.js que pour _le type_ `NextRequest`. Pas d'app Next.js. C'est de l'_emprunt de typage_&nbsp;:&nbsp;Vercel publie les types `NextRequest` parce qu'ils sont compatibles avec les _Edge Functions_.

Au runtime, l'objet est juste une `Request` (Standard Web), mais typé `NextRequest` pour avoir l'autocomplétion des helpers `searchParams`, etc.

## Pourquoi Upstash plutôt qu'un Redis classique

| Redis classique (TCP)    | Upstash (REST)             |
| ------------------------ | -------------------------- |
| Connexion persistante    | HTTP par requête           |
| Pas compatible Edge      | Compatible Edge            |
| Plus rapide en multi-ops | Plus simple en single-op   |
| Self-hosted ou managed   | Managed (Cloudflare-style) |

L'_Edge runtime_ n'a pas de socket TCP. Upstash expose Redis via HTTP+REST.

## `API_SECRET`

```typescript
const API_SECRET = process.env.API_SECRET;
```

Lu au démarrage du Worker (_cold start_).  
Stocké en mémoire pour la durée de vie d'un _worker_ (qui peut servir N requêtes).

## `UPSTASH_REDIS_REST_*`

```typescript
// lib/redis.ts
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});
```

1. `UPSTASH_REDIS_REST_URL`&nbsp;: l'URL HTTPS du Redis Upstash.
2. `UPSTASH_REDIS_REST_TOKEN`&nbsp;: le token Bearer pour s'authentifier.

`vercel env add ...` (cf. README).

## Pourquoi seulement 3 endpoints

| Endpoint               | Pourquoi                                                          |
| ---------------------- | ----------------------------------------------------------------- |
| `/api/otp?_user=<u>`   | Génère un OTP pour le test login MFA                              |
| `/api/otp-history`     | Permet à Ocarina de retrouver l'OTP qu'Igoristan vient de générer |
| `/api/corsicadex?id=N` | Fournit des données pour la page «&nbsp;_Pokédex corse_&nbsp;»    |

Pas de _webhook_, pas de _polling_, pas de DB autre que Redis. Le **strict minimum.**
