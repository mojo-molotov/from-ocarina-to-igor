---
title: "06.04 — GET /api/corsicadex?id=N"
description: "L'endpoint GET /api/corsicadex de tests-workers : un lookup statique par id, exercé par les scénarios Corsicamon de l'Igoristan."
weight: 4
date: 2026-05-20
series: ["tests-workers"]
series_order: 4
---

# 06.04&nbsp;—&nbsp;`GET /api/corsicadex?id=N`

> Fichier source&nbsp;: [`api/corsicadex.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/corsicadex.ts)

## Code

```typescript
import type { NextRequest } from "next/server";
import isAuthorized from "../lib/isAuthorized";
import { corsicaDexData } from "../consts/corsicadexData";

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

  const url = new URL(request.url);
  const id = url.searchParams.get("id");

  if (!id) {
    return new Response(JSON.stringify({ error: "Missing id parameter" }), {
      status: 400,
      headers: { "Content-Type": "application/json", ...corsHeaders },
    });
  }

  const corsicamonId = parseInt(id, 10);

  if (isNaN(corsicamonId)) {
    return new Response(JSON.stringify({ error: "Invalid ID" }), {
      status: 400,
      headers: { "Content-Type": "application/json", ...corsHeaders },
    });
  }

  const corsicamon = corsicaDexData.find((p) => p.id === corsicamonId);

  if (!corsicamon) {
    return new Response(JSON.stringify({ error: "Corsicamon not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json", ...corsHeaders },
    });
  }

  return new Response(JSON.stringify(corsicamon), {
    headers: { "Content-Type": "application/json", ...corsHeaders },
  });
}
```

## Mécanique

_Lookup_ statique dans un _array_ TypeScript.

| Cas                       | Status | Body                                  |
| ------------------------- | ------ | ------------------------------------- |
| Pas d'`x-api-key`         | 401    | `{ "error": "Unauthorized" }`         |
| Pas de query `?id=`       | 400    | `{ "error": "Missing id parameter" }` |
| `?id=foo` (pas un nombre) | 400    | `{ "error": "Invalid ID" }`           |
| `?id=999` (n'existe pas)  | 404    | `{ "error": "Corsicamon not found" }` |
| OK                        | 200    | `{ "id": ..., "name": ..., ... }`     |

## `consts/corsicadexData.ts`

Le fichier contient un array statique `corsicaDexData` avec 8 _Corsicamons_ (l'équivalent local des Pokémons).

```typescript
export const corsicaDexData = [
  {
    id: 4,
    name: "donkey-sausage",
    type: "siciliacchia di merda",
    sprite: "...",
    description: "...",
  },
  ...
];
```

Du côté de l'Igoristan (`/igoristan/corsicamon`),  
`Math.floor(Math.random() * 8) + 1` choisit un ID entre 1 et 8.

## Pourquoi pas Redis

Le dataset de _Corsicamon_ est&nbsp;:

- Petit (8 entrées).
- Statique (jamais modifié au runtime).
- Compilé dans le bundle (zéro _round-trip_ Redis).

Pas besoin de DB.

## Validation de schéma côté Igoristan

```typescript
// igoristan/src/schemas/Pokemon.ts
import { object, number, string, ... } from 'valibot';

export const PokemonSchema = object({
  id: number(),
  name: string(),
  type: string(),
  sprite: string(),
  description: string(),
});

export type Pokemon = InferOutput<typeof PokemonSchema>;
```

`/corsicamon/+Page.tsx`&nbsp;:

```tsx
const res = await fetch(`${CORSICADEX_API}?id=${id}`, {
  headers: { "x-api-key": apiKey },
});
const data = await res.json();
const parseResult = safeParse(PokemonSchema, data);
if (!parseResult.success) {
  setErrorMessage("Invalid Pokemon data");
  return null;
}
return parseResult.output;
```

→ L'Igoristan **valide au runtime** la réponse via une **validation de schéma**&nbsp;: la réponse doit correspondre à `PokemonSchema`. Si l'API renvoie une forme inattendue, l'UI le signale.

## Coût

- 0 _round-trip_ réseau (pas de Redis).
- 1 `.find` sur un array de 8 entrées (O(n) trivial).
- Total&nbsp;: quelques µs sur l'_Edge_.

## Pourquoi `parseInt(id, 10)` avec radix explicite

```typescript
const corsicamonId = parseInt(id, 10);
```

Le radix `10` est explicite. Sans, `parseInt("010")` retourne `10` (depuis 2015), mais l'ancien comportement (`8`, base octale) reste possible dans certains runtimes, la "bonne pratique" est de toujours l'expliciter.

ESLint a la règle `radix` activée par défaut côté Igoristan, qui interdit `parseInt(x)` sans radix.
