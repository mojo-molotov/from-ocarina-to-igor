---
title: "06.04 — GET /api/corsicadex?id=N"
description: "The GET /api/corsicadex endpoint of tests-workers: a static lookup by id, exercised by the Igoristan's Corsicamon scenarios."
weight: 4
date: 2026-05-20
series: ["tests-workers"]
series_order: 4
---

# 06.04&nbsp;—&nbsp;`GET /api/corsicadex?id=N`

> Source file: [`api/corsicadex.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/corsicadex.ts)

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

## Mechanics

Static lookup in a TypeScript array.

| Case                      | Status | Body                                  |
| ------------------------- | ------ | ------------------------------------- |
| No `x-api-key`            | 401    | `{ "error": "Unauthorized" }`         |
| No `?id=` query           | 400    | `{ "error": "Missing id parameter" }` |
| `?id=foo` (not a number)  | 400    | `{ "error": "Invalid ID" }`           |
| `?id=999` (doesn't exist) | 404    | `{ "error": "Corsicamon not found" }` |
| OK                        | 200    | `{ "id": ..., "name": ..., ... }`     |

## `consts/corsicadexData.ts`

Static `corsicaDexData` array with 8 Corsicamons (local Pokémon equivalents).

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

On the Igoristan side (`/igoristan/corsicamon`), `Math.floor(Math.random() * 8) + 1` picks an ID between 1 and 8.

## Why not Redis

The Corsicamon dataset is small (8 entries), static, and compiled into the bundle. Zero Redis round-trips. No DB needed.

## Schema validation on the Igoristan side

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

`/corsicamon/+Page.tsx`:

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

Igoristan validates the response at runtime against `PokemonSchema`. Unexpected shape → the UI flags it.

## Cost

- 0 network round-trips (no Redis).
- 1 `.find` on an 8-entry array.
- Total: a few µs on the Edge.

## Why `parseInt(id, 10)` with explicit radix

```typescript
const corsicamonId = parseInt(id, 10);
```

Explicit radix. Without it `parseInt("010")` returns `10` today, but older runtimes return `8` (octal). Always be explicit.

ESLint's `radix` rule enforces this on the Igoristan side&nbsp;—&nbsp;`parseInt(x)` without a base is an error.
