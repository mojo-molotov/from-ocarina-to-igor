---
title: "06.05 — isAuthorized.ts"
weight: 5
date: 2026-05-20
series: ["tests-workers"]
series_order: 5
---

# 06.05&nbsp;—&nbsp;`isAuthorized.ts`

> Fichier source&nbsp;: [`lib/isAuthorized.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/lib/isAuthorized.ts)
>
> Vérifie qu'une requête contient le bon `x-api-key`.

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

## Approche

### 1. `API_SECRET`

```typescript
const API_SECRET = process.env.API_SECRET;
```

Lu une seule fois, au démarrage du worker _Edge_ (_cold start_).  
Stocké en tant que variable de module.

Plus rapide que `process.env.API_SECRET` à chaque appel.

### 2. Guard `typeof !== "string"`

```typescript
if (typeof API_SECRET !== "string") {
  console.error("[CONFIG ERROR] API_SECRET is not defined");
  return false;
}
```

Si la variable d'environnement n'est pas définie&nbsp;: log + refuse.  
Pas de _panic_ au démarrage.

Comportement «&nbsp;_fail-safe_&nbsp;»&nbsp;: on refuse l'auth, un attaquant ne peut pas exploiter l'absence de variable d'environnement.

### 3. Passage de la clé

```typescript
const apiKey = searchParams.get("apiKey") ?? request.headers.get("x-api-key");
```

1. **Query string** `?apiKey=<X>`.
2. **Header** `x-api-key: <X>` (fallback).

| Cas                             | Endroit                                                        |
| ------------------------------- | -------------------------------------------------------------- |
| cURL                            | Query string (plus simple, pas besoin de `-H`)                 |
| Production /&nbsp;browser fetch | Header (_best practice_, n'apparaît pas dans les logs serveur) |

Le README documente les deux&nbsp;:

```bash
curl -H "x-api-key: SECRET" "https://.../api/otp"
curl "https://.../api/otp?apiKey=SECRET"           # même chose
```

## Export/import

```typescript
export default isAuthorized;
```

```typescript
import isAuthorized from "../lib/isAuthorized";
```

## Absence de _rate-limit_

Aucun _rate-limit_ n'est appliqué.  
Un attaquant avec _le bon `API_SECRET`_ pourrait spammer.

Mais&nbsp;: il _faut_ déjà connaître `API_SECRET`.  
Et le déploiement _Vercel Free Tier_ a des limites _built-in_ (100 requêtes/seconde par défaut).

Donc le _rate-limit_ applicatif n'est pas indispensable.

## `console.error`

```typescript
console.error("[CONFIG ERROR] API_SECRET is not defined");
```

Tout `console.*` dans une _Edge Function_ apparaît dans le _dashboard_ de Vercel (logs).  
Si `API_SECRET` n'est pas défini, le _maintainer_ le voit dans les logs.
