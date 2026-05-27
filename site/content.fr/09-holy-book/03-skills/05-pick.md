---
title: "09.03.05 — Skills Pick"
description: "Sélection d'artefacts (screenshots, logs, reports). Toujours par mtime, jamais par nom de fichier."
weight: 5
date: 2026-05-20
series: ["skills"]
series_order: 5
tags: ["holy-book"]
---

# 09.03.05&nbsp;—&nbsp;Skills Pick

> Sélection d'artefacts (screenshots, logs, reports). **Toujours par mtime, jamais par nom de fichier.**

## Listing (potentiellement non exhaustif)

| Skill              | Cible                                                                                                    |
| ------------------ | -------------------------------------------------------------------------------------------------------- |
| `pick-screenshots` | Pioche les screenshots les plus récents (par mtime), en les contextualisant à l'aide de logs si possible |
| `pick-logs`        | Pioche les logs les plus récents (par mtime)                                                             |
| `pick-reports`     | Pioche les reports DOCX/JSON les plus récents (par mtime)                                                |

## «&nbsp;_mtime_&nbsp;»

Citation du Holy Book&nbsp;:

> **Mtime, pas nom de fichier.** Les suffixes UUID sont aléatoires&nbsp;; `pick-*` trie par mtime.

Tous les artefacts d'Ocarina sont nommés avec un UUID&nbsp;:

- Screenshots&nbsp;: `SUCCESS_a3f2b1c4.png`, `FAIL_b9e8d2a3.png`
- Logs&nbsp;: `<test name>.log` mais dans un arbre `<cycle>/<campaign>/<suite>/<test>.log` souvent dupliqué entre runs avec un dossier racine suffixé d'un UUID en cas d'exécutions multiples sur la même machine
- Rapports&nbsp;: `<uuid hex 8>.json`, `<uuid hex 4>/<...>.docx`

## Schéma

```
input  : "lance review-report sur le dernier run"
        → pick-reports (mtime DESC, limit 1)
        → review-report sur le rapport sélectionné
```

```
input  : "trouve les screenshots du test X dans le dernier run"
        → pick-reports → dernier run
        → pick-screenshots scopé
```

## Pourquoi des skills dédiées plutôt que `ls -t`

| Sans skill                                                                             | Avec skill                        |
| -------------------------------------------------------------------------------------- | --------------------------------- |
| Claude doit deviner la convention de répertoire (`.reports/docx/` vs `.reports/json/`) | Le skill connaît la convention    |
| Risque de pick un screenshot hors sujet                                                | Le skill scope au dernier run     |
| Pas de filtrage par browser /&nbsp;par test /&nbsp;par catégorie                       | Le skill expose des filtres typés |

## «&nbsp;_pick then act_&nbsp;»

```
Cycle en échec  →  pick-reports  →  review-report(<picked report>)
                                            ↓
                                    classification → IDENTIFIED_GAPS.md
```

`pick-*` est rarement appelée seule. C'est toujours un **prélude** à un skill qui consomme l'artefact pické.

## Illustration des nommages aléatoires

Quand un cycle de test propulsé par Ocarina se termine, les artefacts sont construits tel que&nbsp;:

```
.reports/
├── docx/
│   └── <uuid 4 chars>/                                           # par run
│       └── <campaign>/
│           └── <suite>/
│               └── <test>.docx
└── json/
    └── <uuid 8 chars>.json                                       # par run
```
