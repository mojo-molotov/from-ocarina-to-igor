---
title: "06.02 — GET /api/otp"
description: "L'endpoint GET /api/otp de tests-workers : génération d'un OTP avec otplib, stockage Redis et payload de coordination des workers."
weight: 2
date: 2026-05-20
series: ["tests-workers"]
series_order: 2
tags: ["otp"]
---

# 06.02&nbsp;—&nbsp;`GET /api/otp`

> Fichier source&nbsp;: [`api/otp.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/otp.ts)

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

## Flot

```
1. Request arrive
   ↓
2. Si OPTIONS → 200 + CORS headers (preflight)
   ↓
3. isAuthorized(request) ? Non → 401
   ↓
4. Parse searchParams ; tout sauf "secret" est mis dans freePayload
   ↓
5. payloadSize > 4 KB ? → 400
   ↓
6. secret = ?secret=<X> (si fourni) sinon random Base32 32-chars
   ↓
7. ensureSecretLength : assure 32..64 chars, multiple de 8
   ↓
8. otpCode = generate({ secret })   ← otplib TOTP RFC 6238
   ↓
9. createdAt = floor(now / 1000) * 1000  ← amputation des ms
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

- `*` origin&nbsp;: permet à l'Igoristan (depuis `https://mojo-molotov.github.io`) d'appeler le service.
- `GET, OPTIONS`&nbsp;: seuls verbes supportés.
- Custom header `x-api-key` autorisé (sinon le _browser_ bloquerait).

`as const` rend l'objet `readonly` côté TypeScript.

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

1. Tout query param **sauf** `secret` est inclus dans la _free payload_.
2. Si l'ajout d'une entrée dépasse 4 KB, on _arrête_ d'ajouter (mais on continue à compter pour le check final).
3. Si on dépasse globalement&nbsp;: 400 Bad Request.

Pourquoi une _free payload_&nbsp;?  
Pour que **n'importe quel champ libre** (typiquement `_user`) puisse être stocké avec l'événement.

L'Igoristan envoie `?_user=<username>`, qui se retrouve dans `event._user`, et Ocarina retrouve l'OTP par filtre sur `_user` en plus de filtrer sur le _timestamp_.

## Génération du secret (Base32)

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

1. **`crypto.getRandomValues`**&nbsp;: CSPRNG natif du Web (et de _l'Edge runtime_).
2. **Base32 alphabet**&nbsp;: `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567` (32 caractères, RFC 4648).
3. **`% 32`**&nbsp;: mappe un octet aléatoire 0-255 sur un index 0-31 (`256 / 32 = 8`).

## `ensureSecretLength`

Si un `secret` custom est passé en query, il faut s'assurer du respect des contraintes&nbsp;:

1. Longueur ≥ 32.
2. Longueur ≤ 64.
3. Longueur multiple de 8 (requis par TOTP RFC).

Si < 32&nbsp;: on répète. Si > 64&nbsp;: on tronque.  
Sinon&nbsp;: on tronque au multiple de 8 inférieur.

Cette robustesse permet à un utilisateur de passer `?secret=foo` sans planter&nbsp;:&nbsp;`foo` est trop court, alors on le répète&nbsp;→&nbsp;`foofoofoofoo...` jusqu'à 32 chars, on tronque au multiple de 8.

## `key` Redis

```typescript
const key = `otp:${now}:${crypto.randomUUID()}`;
```

`otp:<timestamp_ms>:<uuid>`.

1. Préfixe `otp:` permet le `SCAN MATCH otp:*` côté _OTP history_.
2. `<timestamp_ms>` permet un tri _lexico-sémantique_ approximatif (Redis ne trie pas, mais `SCAN` retourne les keys avec un ordre arbitraire).
3. `<uuid>` garantit l'unicité même si deux workers _Edge_ créent à la même milliseconde (race condition).

## TTL

```typescript
const OTP_TTL = 60 * 5; // 5 min — durée de validité OTP
const OTP_HISTORY_TTL = OTP_TTL + 60; // 6 min — durée de vie en Redis
```

Stratégie&nbsp;: l'OTP est _valide_ 5 min, mais on conserve en Redis 1 min de plus.  
Marge pour que `/api/otp-history` puisse encore permettre de le voir si la requête arrive _juste après_ l'expiration.

## Imprécision du _timestamp_

```typescript
const createdAtTimestampLackingMsPrecision = new Date(
  now - (now % 1000),
).toISOString();
```

On _enlève_ volontairement les millisecondes&nbsp;:

1. `now = 1715952473123`&nbsp;→&nbsp;`now - 1715952473123 % 1000 = 1715952473123 - 123 = 1715952473000`
   2.&nbsp;→&nbsp;`new Date(1715952473000).toISOString() = "2024-05-17T13:27:53.000Z"`

Le nom de la variable est explicite&nbsp;: `createdAtTimestampLackingMsPrecision`

Voir [`07-otp-coordination-flow.md`](07-otp-coordination-flow.md)

## Format de l'_event_

```typescript
const event = {
  ...freePayload, // ex. _user, env, userId
  otpCode, // ex. "123456"
  secret, // ex. "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"
  createdAtTimestampLackingMsPrecision, // "2024-05-17T13:27:53.000Z"
  expiresAt: new Date(expiresAtMs).toISOString(), // "2024-05-17T13:32:53.123Z"
};
```

`expiresAt` _conserve_ les millisecondes.  
Seul `createdAt` est amputé.

`expiresAt` n'est pas utilisé pour _filtrer_, juste pour _informer_.  
Le filtre côté Ocarina utilise `createdAt`, dont l'imprécision force la coordination par `_user` et par _delta timing_.

## Réponse HTTP

```typescript
return new Response(JSON.stringify(event), {
  headers: { "Content-Type": "application/json", ...corsHeaders },
});
```

Default status&nbsp;: 200.  
Body = _event_ JSON.

Headers CORS pour que l'Igoristan puisse interagir.
