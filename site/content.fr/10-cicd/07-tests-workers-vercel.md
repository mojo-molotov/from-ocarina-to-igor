---
title: "10.07 — tests-workers : pas de CI GitHub, déploiement Vercel auto"
description: "tests-workers, le seul dépôt de l'écosystème sans workflow GitHub Actions : tout le déploiement passe automatiquement par Vercel."
weight: 7
date: 2026-05-20
series: ["ci-cd"]
series_order: 7
---

# 10.07&nbsp;—&nbsp;`tests-workers`&nbsp;: pas de CI GitHub, déploiement Vercel auto

> Le seul dépôt de l'écosystème **sans workflow GitHub Actions**. Tout passe par Vercel.

## Le contenu du `.github/`

```
tests-workers/
└── (aucun .github/ — pas de workflows)
```

Pas de `ci.yml`. Pas de `deploy.yml`. Pas d'action GitHub.

## `vercel.json`

```json
{
  "version": 2,
  "buildCommand": "echo 'No build required'",
  "outputDirectory": ".",
  "framework": null
}
```

Vercel _détecte_ le projet comme _TypeScript Edge Functions_, build à la volée (transpile TS au runtime).

## `package.json#scripts`

```json
{
  "scripts": {
    "vercel-build": "echo 'Build skipped'"
  }
}
```

`vercel-build` hook&nbsp;:&nbsp;`echo` no-op.  
Vercel ne tente pas de build.

## Le déploiement (manuel)

Documenté dans le README&nbsp;:

```bash
→ pnpm install
→ vercel env add API_SECRET
→ vercel env add UPSTASH_REDIS_REST_URL
→ vercel env add UPSTASH_REDIS_REST_TOKEN
→ vercel deploy
```

C'est tout. Quatre commandes, exécutées par l'auteur depuis sa machine.

## Pourquoi pas de CI GitHub

| Raison                                | Détail                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Vercel auto-deploy depuis le repo** | Vercel peut être configuré pour deploy automatiquement à chaque push GitHub.                                                                                                                                                                                                                                                                     |
| **Pas de tests dynamiques**           | Le code n'est pas à risque, a été testé manuellement, et ne sera plus mis à jour. C'est un projet terminé.                                                                                                                                                                                                                                       |
| **Pas de checks statiques**           | Aucun test statique automatisé non plus. Tout a été testé manuellement. Des anomalies sur ce composant seraient rapidement détectées via les tests e2e et sont facilement isolables et reproductibles. La plupart du temps, par expérience, les problèmes viennent plutôt d'Upstash qui décide de kill l'instance Redis sans raison par exemple. |

## Auto-deploy Vercel

Vercel offre une intégration GitHub native&nbsp;:

- Connecter le repo GitHub à un projet Vercel.
- Vercel deploy chaque push main&nbsp;→&nbsp;production.
- Vercel deploy chaque PR&nbsp;→&nbsp;preview URL.

Le `vercel.json` et les env vars sont configurés une fois côté dashboard Vercel. Plus rien à faire ensuite.

## URL de production

```
https://tests-workers.vercel.app
```

Avec les endpoints&nbsp;:

```
https://tests-workers.vercel.app/api/otp?_user=<u>
https://tests-workers.vercel.app/api/otp-history
https://tests-workers.vercel.app/api/corsicadex?id=<n>
```

Cf. [`../06-tests-workers/`](../06-tests-workers/README.md)

## Contraste avec les autres déploiements

| Dépôt                       | Hébergement  | Trigger deploy                    | YAML CI                               |
| --------------------------- | ------------ | --------------------------------- | ------------------------------------- |
| `igoristan`                 | GitHub Pages | push main                         | `deploy.yml`                          |
| `ocarina-holy-book`         | GitHub Pages | push main                         | `deploy.yml`                          |
| `tests-workers`             | Vercel       | push main (auto Vercel)           | _aucun_                               |
| `ocarina` (artefact Allure) | GitHub Pages | push main +&nbsp;action composite | `main_ci.yml` +&nbsp;action composite |

Trois patterns différents. `tests-workers` est le seul à _déléguer entièrement_ le deploy à un service tiers.

## Avantage /&nbsp;inconvénient

Le projet **accepte** le vendor lock-in pour la simplicité. C'est cohérent avec un projet qui doit être _déployable en 30 secondes_ et qui de toute manière est tout petit et pourrait rapidement être migré en cas de problème.

## La licence ISC

`tests-workers` est en **ISC** (et pas MIT comme les autres). Provient du scaffold Vercel CLI qui génère ISC par défaut. L'auteur n'a même pas regardé.

Note&nbsp;: ISC ≈ MIT (les deux sont des licences permissives à 1 paragraphe). Aucune différence pratique pour les contributeurs.

## Sécurité

`API_SECRET` est&nbsp;:

1. Stocké dans les variables d'environnement côté Vercel (dashboard).
2. Jamais commit dans le repo.
3. Lu au _cold-start_ du Worker via `process.env.API_SECRET`.
