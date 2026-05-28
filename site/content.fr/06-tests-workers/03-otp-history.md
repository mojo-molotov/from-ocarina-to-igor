---
title: "06.03 — GET /api/otp-history"
description: "L'endpoint GET /api/otp-history de tests-workers : un SCAN Redis qui retourne tous les événements OTP pour départager les workers."
weight: 3
date: 2026-05-20
series: ["tests-workers"]
series_order: 3
tags: ["otp"]
---

# 06.03&nbsp;—&nbsp;`GET /api/otp-history`

> Fichier source&nbsp;: [`api/otp-history.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/otp-history.ts)

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

## Mécanique de `SCAN` Redis

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

1. `cursor = "0"` (initialisation).
2. Boucle&nbsp;:
   - `SCAN <cursor> MATCH otp:* COUNT 100` retourne `[newCursor, keys]`.
   - Si `keys` non vide&nbsp;: `MGET k1 k2 ...` récupère les valeurs.
   - `cursor = newCursor`.
3. On s'arrête quand `cursor === "0"` (cycle terminé).

Pourquoi `SCAN` plutôt que `KEYS`&nbsp;?

| `KEYS otp:*`            | `SCAN 0 MATCH otp:*`    |
| ----------------------- | ----------------------- |
| Bloque le serveur Redis | Itératif, ne bloque pas |
| Renvoie tout d'un coup  | Pages de N              |
| **Déconseillé en prod** | **Recommandé**          |

Pour 1000 clés `otp:*`, on fait ~10 round-trips.

## Pourquoi `MGET` plutôt que `GET` individuel&nbsp;?

`MGET k1 k2 k3 ... kN` est **un** _round-trip_ qui ramène N valeurs.  
`GET k1; GET k2; ...; GET kN` serait N _round-trips_.

Sur un Upstash REST (HTTP), chaque _round-trip_ coûte ~50ms.  
Pour 100 clés&nbsp;: `100*50 = 5000ms`.

## `.filter(Boolean)`

```typescript
allEvents.push(...values.filter(Boolean));
```

`MGET` peut retourner `null` pour les clés qui ont expiré _entre_ le `SCAN` et le `MGET` (race condition).  
`.filter(Boolean)` élimine les `null` /&nbsp;`undefined` qui sont _falsy_ en Javascript.

## Résultat

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

## Sécurité

```typescript
if (!isAuthorized(request)) {
  return new Response(JSON.stringify({ error: "Unauthorized" }),
    { status: 401, ... });
}
```

Sans `x-api-key` correct, 401.  
Donc l'historique n'est lisible que par quelqu'un qui connaît `API_SECRET`.

## Contrat avec Ocarina

`ocarina-example/api/get_otp_history.py`&nbsp;:

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

→ Un simple GET, header `x-api-key`, parse JSON.  
Pas de pagination côté client (l'endpoint a déjà tout agrégé).

## Coût

Pour 100 _events_ dans Redis&nbsp;:

- 1 `SCAN`&nbsp;→&nbsp;100 keys retournées (1 _round-trip_).
- 1 `MGET` de 100 keys&nbsp;→&nbsp;100 values (1 _round-trip_).
- Total&nbsp;: 2 _round-trips_.

Pour 1000 _events_&nbsp;:

- 10 `SCAN`.
- 10 `MGET`.
- Total&nbsp;: 20 _round-trips_.

À ~50ms par _round-trip_, c'est 1s pour 1000 _events_.

## Sémantique «&nbsp;_historique partagé_&nbsp;»

Tous les OTP émis par n'importe quel _worker_ (invoqué par un humain ou par Selenium, pour n'importe quel _user_) finissent dans Redis.  
Le filtre par `_user` se fait **côté client**, pas côté serveur.

1. **Simplicité côté serveur**&nbsp;: pas de logique de filtre, juste un dump.
2. **Flexibilité**&nbsp;: un client pourrait filtrer par `_env`, par `_userId`, par `_anything`. Le serveur ne sait pas ce qu'il y a dans le _free payload_.
3. **Volume gérable**&nbsp;: 6 min × N OTP/sec = quelques centaines, pas des millions.

C'est une **approche «&nbsp;_Smart Client /&nbsp;Dumb Server_&nbsp;»**&nbsp;: la logique applicative est côté tests, le serveur se contente de _dump_.
