---
title: "09.03.10 — Skills Run"
description: "La famille de skills Run exposés aux IA : faire remonter les choix d'avant-exécution avant un lancement local, puis rendre la commande composée."
weight: 10
date: 2026-05-20
series: ["skills"]
series_order: 10
tags: ["holy-book"]
---

# 09.03.10&nbsp;—&nbsp;Skills Run

> Faire remonter les choix à trancher _avant_ un lancement local, composer la commande, et la rendre. Le skill ne lance jamais l'exécution lui-même.

## Listing (potentiellement non exhaustif)

| Skill                   | Cible                                                                                  |
| ----------------------- | -------------------------------------------------------------------------------------- |
| `propose-visual-review` | Propose fenêtré (`--not-headless`) vs headless (façon CI) avant une exécution, puis compose la commande |

## `propose-visual-review`

```
input  : une exécution locale à venir
output : le choix fenêtré vs headless :
            - --not-headless : on regarde le navigateur, utile pour déboguer un flux flaky
            - headless (façon CI) : plus rapide, identique à ce que fait la CI
         + le compromis et ce qu'il faut surveiller pendant une exécution fenêtrée
         + la commande composée, rendue à l'utilisateur pour qu'il la lance
```

## Rôle

- **Faire remonter** le choix d'avant-exécution&nbsp;; expliquer le compromis.
- **Composer** la commande.
- **Ne pas la lancer**&nbsp;: c'est l'utilisateur qui exécute.
