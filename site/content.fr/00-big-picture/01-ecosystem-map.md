---
title: "00.01 — Cartographie de l'écosystème"
description: "Les six dépôts publics de l'écosystème Ocarina, leurs cinq rôles et les contrats qui les relient, présentés en une seule cartographie."
weight: 1
date: 2026-05-20
series: ["big-picture"]
series_order: 1
tags: ["otp"]
---

# 00.01&nbsp;—&nbsp;Cartographie de l'écosystème

L'écosystème Ocarina est constitué de **six dépôts publics** sur le compte
GitHub [`mojo-molotov`](https://github.com/mojo-molotov). Ils s'organisent en
**cinq rôles distincts** qui se composent&nbsp;:

| Rôle                                     | Dépôt                                                             | Forme                                                   |
| ---------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------- |
| **Framework**                            | `ocarina`                                                         | Bibliothèque Python publiée sur PyPI                    |
| **Application sous test (SUT) publique** | `igoristan`                                                       | SPA React + Vike déployée sur GitHub Pages              |
| **Backend de coordination**              | `tests-workers`                                                   | API Vercel Edge + Upstash Redis                         |
| **Suite d'exemples**                     | `ocarina-example` _(canonique)_, `ocarina-with-ai-example` _(IA)_ | Projets Python e2e tournés vers l'Igoristan /&nbsp;CURA |
| **Documentation publique**               | `ocarina-holy-book`                                               | Site VitePress FR + EN, PDF, skills IA                  |

## Schéma d'ensemble (big picture)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              OCARINA (BIG PICTURE)                              │
└─────────────────────────────────────────────────────────────────────────────────┘

   ┌──────────────────────────────┐         ┌──────────────────────────────────┐
   │  [PACKAGE]  ocarina          │ ──────► │  [PACKAGE]  ocarina-example      │
   │  Framework Python 3.14+      │   pip   │  Suite e2e contre l'Igoristan    │
   │  ROP / DSL / orchestration   │ install │  (Selenium + Firefox + Redis)    │
   └──────────────────────────────┘         └──────────────────────────────────┘
            │  │                                       │  ▲   │
            │  │                                       │  │  utilise
            │  │ pip install ocarina                   │  │  IGOR_API_KEY
            │  ▼                                       ▼  │   │
            │  ┌────────────────────────────────────┐  pilote │
            │  │ [PACKAGE]  ocarina-with-ai-example │  ┌──────┴──────────────────┐
            │  │ Suite e2e CURA Healthcare          │  │ [WEBSITE]  igoristan    │
            │  │ Claude Code, 99% machine           │  │ React 19 + Vike         │
            │  └────────────────────────────────────┘  │ GitHub Pages            │
            │              │                           └──────┬──────────────────┘
            │              │ pilote                           │ fetch OTP
            │              ▼                                  ▼
            │   ┌──────────────────────────────┐    ┌──────────────────────────────┐
            │   │ [WEBSITE]  CURA Healthcare   │    │ [BACKEND]  tests-workers     │
            │   │ Heroku, PHP open source      │    │ Vercel Edge Functions        │
            │   └──────────────────────────────┘    │ + Upstash Redis              │
            │                                       │ /api/otp, /otp-history,      │
            │                                       │ /api/corsicadex              │
            │                                       └──────────────────────────────┘
            │                                                 ▲
            │                                                 │ x-api-key
            │                                                 │ (IGOR_API_KEY ≡ API_SECRET)
            │                                                 │
            ▼
   ┌──────────────────────────────┐
   │  [DOCS]  ocarina-holy-book   │
   │  VitePress FR + EN + RU      │
   │  Skills IA, PDF, llms.txt    │
   │  GitHub Pages                │
   └──────────────────────────────┘
```

1. **`ocarina`&nbsp;→&nbsp;suites d'exemples**&nbsp;: dépendance Python classique (`pip install ocarina`).
2. **Suites d'exemples&nbsp;→&nbsp;SUT (Igoristan /&nbsp;CURA)**&nbsp;: pilotage navigateur via Selenium.
3. **Suite Igoristan ↔ `tests-workers`**&nbsp;: appels HTTP (OTP, Corsicadex)&nbsp;; le secret partagé `IGOR_API_KEY` (côté client) ≡ `API_SECRET` (côté serveur).

## Responsabilités

| Rôle                    | Contrat                                                                                            | Besoin                                                                                                                        |
| ----------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Framework               | _Donner_ le DSL, l'orchestration, la pool de drivers, les reporters                                | Doit être petit, auditable, sans dépendances cachées                                                                          |
| SUT public              | _Offrir_ un terrain de jeu volontairement chaotique (random errors, OTP, formulaires capricieux)   | Hébergé en permanence sur GitHub Pages, sans backend lourd                                                                    |
| Backend de coordination | _Coordonner_ les workers sur l'OTP, fournir des données pour les tests parallèles                  | Stateless côté code, l'état vit dans Redis (Upstash)                                                                          |
| Exemples                | _Démontrer_ comment on utilise réellement Ocarina, à la fois sans IA (canonique) et avec IA (CURA) | Doivent être publics, exécutables, complets, suivis en CI                                                                     |
| Documentation           | _Transmettre_ le pourquoi, le comment, et l'usage IA                                               | Doit exister en EN + FR + RU (tradition corso-russe), exposer des fichiers adaptés aux LLMs comme `llms.txt`, générer des PDF |

## Trois licences

| Licence            | Dépôts concernés                                                             | Pourquoi                                                                                                                                                      |
| ------------------ | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MIT**            | `ocarina`, `ocarina-example`, `ocarina-with-ai-example`, `ocarina-holy-book` | Tout ce qui est code Python ou doc, transmissible «&nbsp;_tel quel_&nbsp;», souverain&nbsp;—&nbsp;voir [`../11-independence/`](../11-independence/README.md). |
| **ISC**            | `tests-workers`                                                              | Choix par défaut du _scaffold_ Vercel Edge, conservé.                                                                                                         |
| _(aucune licence)_ | `igoristan`                                                                  | Application démo publique, hébergée par l'auteur (à considérer comme WTFPL).                                                                                  |

## Points de friction volontaires entre dépôts

Le design est **volontairement asymétrique** sur certains axes&nbsp;; ces frictions sont des outils de test&nbsp;:

- L'Igoristan a un `useAuth` _**faux**_&nbsp;: `Math.random() < 0.9` peut faire échouer le login _même avec le bon mot de passe_, ce qui force la stratégie de rejeu côté Ocarina. Voir [`../05-igoristan/03-use-auth.md`](../05-igoristan/03-use-auth.md)
- `tests-workers` **ampute volontairement les millisecondes** du timestamp OTP (`.000Z`) pour forcer la coordination avec du _delta timing_. Voir [`../06-tests-workers/07-otp-coordination-flow.md`](../06-tests-workers/07-otp-coordination-flow.md)
- CURA Healthcare contient des **gaps connus** documentés dans `IDENTIFIED_GAPS.md`&nbsp;: les tests qui leur sont associés sont _intentionnellement en échec_ dans cette version de la suite IA. Voir [`../08-ai-example/05-security-gaps.md`](../08-ai-example/05-security-gaps.md)
- Le compteur `Math.random() < 0.3` côté `donkey-sausage-eater-detector` exerce `match_page` (branchement sur états aléatoires). Voir [`../05-igoristan/02-routes.md`](../05-igoristan/02-routes.md)
- La page _random-error_ de l'Igoristan exerce les `transient_errors` (retry d'Ocarina) en levant des erreurs aléatoires. La _chaotic form_ balance des erreurs au hasard sans impacter directement les tests, pour exercer les **watchers**. Des **temps de chargement aléatoires** permettent enfin de vérifier les flots de test face aux _race conditions_.

Ces frictions volontaires sont la **raison d'être** du SUT&nbsp;: un site qui marche tout le temps ne sert à rien pour démontrer un framework de test résilient.
