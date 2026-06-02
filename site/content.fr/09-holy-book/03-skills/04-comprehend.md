---
title: "09.03.04 — Skills Comprehend"
description: "La famille de skills Comprehend exposés aux IA : des skills qui aident à comprendre un projet, son écosystème et les bornes du SUT avant d'agir."
weight: 4
date: 2026-05-20
series: ["skills"]
series_order: 4
tags: ["holy-book"]
---

# 09.03.04&nbsp;—&nbsp;Skills Comprehend

> Skills qui aident l'IA à **comprendre** un projet ou un écosystème avant d'agir.

## Listing (potentiellement non exhaustif)

| Skill                        | Cible                                                     |
| ---------------------------- | --------------------------------------------------------- |
| `assess-test-base`           | Catalogue la base de test existante                       |
| `assess-ecosystem`           | Recherche publique bornée, plafonnée par budget de tokens |
| `assess-impact`              | Analyse d'impact : ce qu'un changement touche en aval, à travers le graphe de dépendances |
| `understand-sut-constraints` | Comprend les "bornes" du SUT pour ne pas les dépasser     |
| `understand-ocarina`         | Aiguille selon la classe de question : le Holy Book pour la référence, le livre from-ocarina-to-igor pour l'intention ; puis la source d'Ocarina + l'exemple correspondant à l'adaptateur en place |

## `understand-ocarina`

```
input  : question de l'utilisateur — aiguillée selon sa classe :
            - "comment fait-on un match_page ?"   (référence : ce qu'est une primitive) → Holy Book
            - "pourquoi la suite est-elle bâtie sur Railway ?" (intention / cartographie / pourquoi) → le livre from-ocarina-to-igor
output : Claude charge, selon la classe de question :
            - référence    → les pages Holy Book pertinentes (https://mojo-molotov.github.io/ocarina-holy-book)
            - intention    → les chapitres pertinents du livre from-ocarina-to-igor (https://mojo-molotov.github.io/from-ocarina-to-igor/)
            - comportement → la source d'Ocarina (clone), si la doc ne le couvre pas
            - forme        → l'exemple correspondant à l'adaptateur du projet :
                              Selenium   → ocarina-example, ocarina-with-ai-example
                              Playwright → ocarina-with-playwright-example
         puis répond avec citations (tier + URL de page/chapitre ou file:line)
```

`SKILL.md`&nbsp;:

> **Tier 1&nbsp;—&nbsp;Ocarina Holy Book (reference, public).** What a primitive _is_ — signature, contract, lifecycle. Reach via `WebFetch` for specific pages once the page-list is known.
>
> **Tier 1B&nbsp;—&nbsp;the from-ocarina-to-igor book (intent / cartography / philosophy, public).** Why Ocarina is shaped this way and how the ecosystem repos relate. The two doc sites are routed by question class, not a fixed order; a question with both halves consults both.
>
> **Tier 2&nbsp;—&nbsp;doc-site repos (cloned + built locally, per-site fallback).** If a site is down (DNS /&nbsp;not-yet-published /&nbsp;offline /&nbsp;404), clone + build that site locally. The fallback is per-site: a 404 on the Holy Book doesn't mean the book is down too.
>
> **Tier 3&nbsp;—&nbsp;Ocarina source clone.** For behaviour the docs don't cover.
>
> **Tier 4&nbsp;—&nbsp;worked-example clones, matched to the driver adapter.** Selenium: ocarina-example, ocarina-with-ai-example. Playwright: ocarina-with-playwright-example.

## `assess-test-base`

```
input  : le repo de tests actuel
output : catalogue :
            - liste exhaustive des tests (cycle / campaign / suite / test)
            - couverture par feature : mapping test ↔ Exigence ("requirement") SFD
            - tests gap (intentionally failing), tests cross-browser, tests explo
            - tests data-driven
            - tests en skipped
```

## `assess-ecosystem`

Skill qui fait de la recherche web **avec limite de tokens**.

```
input  : sujet à comprendre (par exemple "comment CURA est-il déployé sur Heroku ?")
output : findings synthétisés, sources citées
contrainte : budget de tokens — pas de recherche infinie
```

## `assess-impact`

```
input  : un changement (modif du SUT / refactor prévu / une cause partagée trouvée par un diagnose-*)
output : analyse de ce que le changement touche en aval :
            - suit le changement à travers le graphe de dépendances
            - classe chaque nœud touché :
                cassé / affirmation périmée / test-gap susceptible de basculer / trou de couverture / franchissement de smoke-gate
```

L'inverse de la paire `diagnose-*`&nbsp;: les `diagnose-*` partent du symptôme et remontent jusqu'à la cause&nbsp;; `assess-impact` part du changement et trace ce qu'il touche en aval.

## `understand-sut-constraints`

```
input  : SUT (URLs, source si dispo)
output : contraintes qui cassent les tests parallèles :
            - rate-limits (`X requests / minute / IP`)
            - sessions partagées (`one session per user account`)
            - state global (`history accumulates across tests`)
            - dyno endormi (Heroku eco)
            - quota d'API tiers
```

Pour CURA&nbsp;:

- Heroku eco-dyno endormi&nbsp;→&nbsp;warm-up nécessaire.
- Sessions par user&nbsp;→&nbsp;si on lance 3 workers avec _le même_ login, c'est OK, environnement bouchonné.
- Accumulation dans l'historique&nbsp;→&nbsp;un test qui _assert_ «&nbsp;_historique vide_&nbsp;» pourrait fail si un autre test vient de réserver, mais c'est OK, environnement bouchonné.

→ L'IA flag ces contraintes pour que l'humain choisisse comment les gérer (saturate, multi-users, isolated runs, etc.).

## Discipline transversale

- **Capter** de l'information.
- **Synthétiser** en un rapport lisible.
- **Ne pas modifier directement** le code.
