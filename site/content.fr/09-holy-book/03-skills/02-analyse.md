---
title: "09.03.02 — Skills Analyse"
description: "La famille de skills Analyse exposés aux IA : des analyses dynamiques qui exploitent logs et rapports d'exécution pour diagnostiquer la flakiness."
weight: 2
date: 2026-05-20
series: ["skills"]
series_order: 2
tags: ["holy-book"]
---

# 09.03.02&nbsp;—&nbsp;Skills Analyse

> Analyses **dynamiques**&nbsp;: utilisent les logs /&nbsp;les rapports d'une exécution récente pour diagnostiquer la flakiness.

## Listing (potentiellement non exhaustif)

| Skill                          | Cible                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------------------------- |
| `analyse-flakiness`            | Élargit le filet des `transient_errors`&nbsp;; les morts chroniques sont de vraies flakes |
| `analyse-fixture-flakiness`    | Instrumente setup/teardown&nbsp;; rend visibles les contaminations entre tests            |
| `analyse-watcher-flakiness`    | Analyse la fiabilité des watchers (volume, dedupe, faux positifs)                         |
| `analyse-screenshot-flakiness` | Regroupe les captures d'écran par `(test, étape, navigateur)`, détecte les différences    |

## `analyse-flakiness`

```
input  : logs des N dernières exécutions
output : liste de tests qui retry souvent (par % de retries)
         + recommandation :
            - ajouter une exception au tuple transient_errors
            - investiguer un test particulier (peut-être que le problème vient directement du test)
```

## `analyse-fixture-flakiness`

```
input  : tests avec setup/teardown
output : tests dont le setup fail souvent
         + recommandation :
            - vérifier l'idempotence du setup
            - voir si teardown propre (sinon contamination entre tests)
            - sortir le seed du setup vers une init manuelle si trop fragile
```

## `analyse-watcher-flakiness`

```
input  : logs des watcher.report(...) sur N runs
output : watchers à reporting anormal :
            - trop d'émissions (problème de dedupe)
            - aucune émission (le watcher est inutile)
            - faux positifs (élément attendu reporté comme intrus)
```

## `analyse-screenshot-flakiness`

```
input  : screenshots de N runs, groupés par (test, step, browser)
output : flakiness visuelle :
            - tests dont les screenshots varient anormalement entre runs
            - tests qui passent mais dont l'aspect change
            - identifier si la variation est sémantique (vraie diff) ou cosmétique
```

Utilise des heuristiques (hash, dimensions, palette dominante). Pas une vraie image diff.

## Rôle

- **Consommer** une exécution (runtime).
- **Détecter** des patterns sur la durée (N runs).
- **Proposer** des actions (élargir `transient_errors`, _refactor_ un watcher, etc.).

Rappel du Holy Book&nbsp;:

> **Cycle en échec&nbsp;:** `review-report`&nbsp;→&nbsp;`analyse-*` →&nbsp;`write-a-probe` →&nbsp;trouvailles propagées dans `IDENTIFIED_GAPS.md` /&nbsp;les SFD /&nbsp;un commentaire de scénario →&nbsp;sonde supprimée.
