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
| `understand-sut-constraints` | Comprend les "bornes" du SUT pour ne pas les dépasser     |
| `understand-ocarina`         | Parcourt le Holy Book + le code source d'Ocarina          |

## `understand-ocarina`

```
input  : question de l'utilisateur ("comment fait-on un match_page ?")
output : Claude charge :
            - les pages Holy Book pertinentes (depuis https://mojo-molotov.github.io/ocarina-holy-book)
            - le code source d'Ocarina si nécessaire (gh api repos/mojo-molotov/ocarina/...)
            - les exemples des deux projets ocarina-example / ocarina-with-ai-example
         puis répond avec citations
```

`SKILL.md`&nbsp;:

> **Tier 1&nbsp;—&nbsp;Ocarina Holy Book (LLM-oriented, public).** The canonical LLM-facing documentation. Reach via `WebFetch` for specific pages once the page-list is known.
>
> **Tier 2&nbsp;—&nbsp;Holy Book repo (cloned + built locally, when Tier 1 unreachable).** If the website is down (DNS /&nbsp;not-yet-published /&nbsp;offline /&nbsp;404), fallback on the repository source. Clone + build locally.
>
> **Tier 3+&nbsp;—&nbsp;Ocarina source code, ocarina-example, ocarina-with-ai-example.** For code-level questions.

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
