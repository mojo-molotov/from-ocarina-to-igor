---
title: "09.03.01 — Skills Review"
description: "La famille de skills Review exposés aux IA : des lectures statiques qui remontent des constats de revue systématique sur un projet Ocarina."
weight: 1
date: 2026-05-20
series: ["skills"]
series_order: 1
tags: ["holy-book", "watcher"]
---

# 09.03.01&nbsp;—&nbsp;Skills Review

> Lectures **statiques**, remontent des constats. Une grande famille. Permet à l'IA d'effectuer de la _revue_ sur son projet de manière systématique.

## Listing (potentiellement non exhaustif)

| Skill                               | Cible                                                                                                                                      |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `review-spec-gaps`                  | Questions de clarification sur les SFD                                                                                                     |
| `review-watcher-misuse`             | Vérifie le principe «&nbsp;_négatif uniquement_&nbsp;» de `watcher.report(...)`                                                            |
| `review-compartmentalisation-leaks` | Détecte URLs, sélecteurs, nombres magiques aux mauvais endroits                                                                            |
| `review-dead-code`                  | Détecte connecteurs /&nbsp;POMs /&nbsp;scénarios /&nbsp;suites /&nbsp;fragments /&nbsp;constantes non utilisés                             |
| `review-report`                     | Classifie chaque FAIL /&nbsp;SKIP d'une exécution                                                                                          |
| `review-type-ignore`                | Audite les `# type: ignore` (sont-ils justifiés&nbsp;?)                                                                                    |
| `review-match-candidates`           | Identifie les endroits où un `match` (Python, _pattern matching_) pourrait être utilisé plutôt que des `if` `elif` `elif` `if` `if` `elif` |
| `review-unverified-transitions`     | Vérifie qu'à chaque _transition de page_, il y a un `verify`                                                                               |
| `review-submit-dispatchers`         | Audite les méthodes de confirmation de saisie (clic vs touche entrée...)                                                                   |
| `review-comment-drift`              | Détecte les commentaires qui sont désynchronisés avec le code                                                                              |
| `review-suite-stability`            | Évalue la stabilité d'une suite (proportion de retries, transient_errors hits)                                                             |
| `review-intent-collisions`          | Détecte les tests qui s'écrasent mutuellement (intentions contradictoires) et demande/propose des clarifications                           |
| `review-watcher-emissions`          | Audite les émissions de watchers (volume, déduplication, pertinence)                                                                       |
| `review-hierarchy-naming`           | Audite le nommage de la hiérarchie (`TestCycle` / `TestCampaign` / `TestSuite` / `Test`) pour repérer l'antipattern où un enfant reprend le nom du parent |

## `review-dead-code`

```
input  : base de tests
output : liste des éléments non utilisés (connectors / POMs / scénarios / fragments / constantes)
         + recommandation par élément :
            - supprimer
            - mettre en incubateur (<racine-source>/incubator/, arbre de dépendances préservé)
            - conserver (justifier)
```

## `review-report`

```
input  : une exécution récente (logs + reports)
output : classification de chaque test :
            - PASS                  (rien à faire)
            - SKIP                  (pourquoi ?)
            - intentional gap FAIL  (G-DATA-*, G-SEC-*, ...)
            - cross-browser FAIL    (B-BROWSER-*)
            - transient FAIL        (A-ENV-*)
            - régression            ⚠️ ALERTE
```

## `review-watcher-misuse`

```
input  : tous les watcher.report(...)
output : liste des reports qui semblent positifs (« success », « completed », « ok », ...)
         → recommandation : supprimer ou reformuler en négatif
```

## `review-comment-drift`

```
input  : tous les commentaires du code
output : liste des commentaires qui semblent ne plus correspondre au code adjacent
         (typique : commentaire mentionne foo, code mentionne bar)
```

Aide à éliminer les commentaires obsolètes.  
«&nbsp;_Teach the pattern, not the symptom_&nbsp;».

## `review-compartmentalisation-leaks`

```
input  : tout le code source
output : leaks détectés :
            - URLs inline dans scenarios/connectors → propose déplacement vers constants/
            - selectors dans methods → propose déplacement vers top of POM
            - magic numbers dans methods → propose déplacement vers constants
```

Règles du `CLAUDE.md`&nbsp;:

- URLs dans `src/constants/urls.py`, jamais inline.
- Sélecteurs en haut du code des POM.
- Etc.

## Rôle

1. **Lire** le code (et parfois la dernière exécution).
2. **Catégoriser** les trouvailles.
3. **Suggérer** des actions.
4. **Ne pas modifier directement** le code.
5. **L'humain décide.**
