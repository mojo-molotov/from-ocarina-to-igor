---
title: "09.03.06 — Skills Author"
description: "La famille de skills Author exposés aux IA : des skills qui produisent un livrable, tests, sondes, stratégie de test ou extension de couverture."
weight: 6
date: 2026-05-20
series: ["skills"]
series_order: 6
tags: ["holy-book"]
---

# 09.03.06&nbsp;—&nbsp;Skills Author

> Skills qui **produisent un livrable**. Tests, sondes, docs, rapports.

## Listing (potentiellement non exhaustif)

| Skill                       | Cible                                                                            |
| --------------------------- | -------------------------------------------------------------------------------- |
| `empiricism`                | Vérifier avant d'encoder&nbsp;; ne pas écraser un test gap en échec intentionnel |
| `write-a-probe`             | Script de "sonde" jetable, gitignored                                            |
| `write-test-strategy`       | Génère le document de stratégie de test à partir de la suite                     |
| `extend-coverage`           | Étend la couverture à partir du patrimoine existant                              |
| `update-frd-and-tests`      | Propage une mise à jour de spec                                                  |
| `manual-reproduction-guide` | Rédige un scénario de reproduction exécutable par un humain                      |
| `manage-backlog`            | `BACKLOG.md`                                                                     |
| `pr-report`                 | Rapport de PR adapté                                                             |

## `empiricism`

```
input  : intention de l'utilisateur (« écris un test qui assert X »)
output : avant d'encoder X :
            1. vérifier empiriquement que X est vrai
                - sonde
                - gh api du code source
                - curl -v pour inspecter réponses HTTP
                - ...
            2. si X est confirmé → encoder
            3. si X est faux → corriger l'intention
            4. si X est ambigu → demander à l'humain
```

> «&nbsp;_Juste remarque, je suppose. Je vérifie empiriquement._&nbsp;»

## `write-a-probe`

```
input  : question à creuser (« est-ce que la confirmation arrive en < 5s ? »)
output : script Python jetable qui :
            - vit dans un répertoire gitignored (typique : `probes/`)
            - bypass l'Ocarina workflow (pas de Test, pas de Suite)
            - drive le navigateur ou fait des calls HTTP directement
            - print l'état (URL, DOM, cookies, timings) en stdout
            - n'est jamais commit
         après usage : la trouvaille va dans IDENTIFIED_GAPS.md / SFD / commentaire
         puis la sonde est supprimée
```

`CLAUDE.md`&nbsp;:

> A **probe** is a one-off script that drives the browser (or raw HTTP) through a suspect flow and prints concrete runtime state. It **bypasses the Ocarina workflow entirely**&nbsp;—&nbsp;no `create_selenium_test`, no suites, no campaigns, no assertions. Probes live in a gitignored directory, are **never committed or pushed**, and are deleted once the answer lands in a durable artifact.

Et&nbsp;:

> Reach for one when the framework's error surface doesn't show enough&nbsp;—&nbsp;a bare `TimeoutException` or `AssertionError` you can't act on. The trigger is the visibility gap, not where you are in the test lifecycle.

## `write-test-strategy`

```
input  : patrimoine de test, base de test
output : un .md de test strategy contenant :
            - scope
            - test types
            - coverage tables (REQ-X-N × test_X)
            - suite/campaign tree
            - expected pass/fail breakdown
            - gaps
            - CI matrix
```

→ `CURA_TEST_STRATEGY.md`

## `extend-coverage`

```
input  : un gap / une idée d'attaque trouvée par un skill black-hat
output : un nouveau test qui exerce ce gap :
            - via l'UI normale (pas de payload)
            - assert rejection si attendu (gap test)
            - assert le comportement actuel si exploratoire
            - se connecte avec SFD update
```

## `update-frd-and-tests`

```
input  : changement de spec (« CURA a corrigé G-DATA-1 »)
output : diff atomique :
            - SFD §9.7 : ajoute la révision (« 2026-XX-XX : fixed »)
            - IDENTIFIED_GAPS.md : ajoute la révision
            - test : inverse l'assertion (FAIL → PASS), renomme, déplace si nécessaire
            - analyse tous les commentaires inline qui référencent l'ancien gap
```

C'est le _seul_ skill qui modifie la spec qu'on lui fournit comme référence.

> **Ne réécris pas la spec&nbsp;; seul `update-frd-and-tests` le fait, avec une ligne de révision.**

## `manual-reproduction-guide`

```
input  : un test fail
output : un guide pour un humain, étape par étape, pour reproduire le fail manuellement
```

```
1. Open https://katalon-demo-cura.herokuapp.com/profile.php#login
2. Type "John Doe" in username field
3. Type "ThisIsNotAPassword" in password field
4. Click Login
5. Navigate to /appointment.php
6. ...
7. Observe: confirmation page rendered with past date (expected: rejection)
```

## `manage-backlog`

```
input  : sessions de travail / discussions
output : maintien de BACKLOG.md :
            - findings à investiguer plus tard
            - improvements suggérés
            - tests à écrire
            - questions ouvertes sur le SUT
         priorisation
```

## `pr-report`

```
input  : une mise à jour à pousser en tant que PR
output : rapport de PR adapté au type de changement :
            - PR de feature : tests ajoutés, coverage diff
            - PR de bugfix : test de régression, lien au gap
            - PR de refactor : checks que le comportement n'a pas changé
            - PR de doc : aucun test
            - PR mixte : sections multiples
```

Permet à l'humain de produire un rapport cohérent au format `gh pr create --body ...`

## Discipline transversale

Tous les skills Author **produisent** quelque chose de _persistant_, des _livrables_&nbsp;: test, doc, fichier.
