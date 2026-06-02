---
title: "09.03 — Skills exposés aux IA"
description: "Les plus de 40 skills exposés aux IA par le Holy Book : des procédures destinées aux LLMs, versionnées sur GitHub et classées par familles."
weight: 3
date: 2026-05-20
tags: ["holy-book"]
sidebar:
  open: true
---

# 09.03&nbsp;—&nbsp;Skills exposées aux IA

> Plus de 40 _skills_ (procédures destinées aux LLMs) versionnés sur GitHub. Classés **par familles**. Documentés dans le Holy Book (chapitre «&nbsp;_Utiliser Ocarina avec l'IA_&nbsp;»).

## Arborescence de fichiers

```
ai/skills/
├── README.md
└── <skill-name>/
    └── SKILL.md
```

Chaque skill = un dossier + un `SKILL.md`

`SKILL.md`&nbsp;:

- Frontmatter YAML avec `name` et `description` (utilisée par Claude pour décider de _trigger_ ce skill).
- Corps Markdown&nbsp;: la procédure détaillée, sections, étapes, exemples.

`README.md`&nbsp;:

- Index des skills&nbsp;: regroupe par familles, rappelle des interconnexions possibles.

Le plugin `docs/.vitepress/plugins/skills.ts` traverse ce dossier et les copie pour en faire des pages publiques `/skills/<name>`.

## Familles (liste non exhaustive)

|  #  | Famille                        | Sujet                                                                                |
| :-: | ------------------------------ | ------------------------------------------------------------------------------------ |
| 01  | [Review](01-review.md)         | Lectures statiques, remontent des constats                                           |
| 02  | [Analyse](02-analyse.md)       | Dynamique&nbsp;: flakiness, fixture, watcher, screenshot                             |
| 03  | [Black-hat](03-black-hat.md)   | Idéations de vulnérabilités de logique métier                                                          |
| 04  | [Comprehend](04-comprehend.md) | Catalogue, écosystème, contraintes SUT, indexation d'Ocarina dans le contexte du LLM |
| 05  | [Pick](05-pick.md)             | Utilisation des artefacts (screenshots, logs, reports)                               |
| 06  | [Author](06-author.md)         | Délègue la production de livrables au LLM                                            |
| 07  | [Refactor](07-refactor.md)     | Refactor, DRY, introduction de retries dans les POM                                  |
| 08  | [State](08-state.md)           | Questionne les états dans le SUT (bouchons, persistance des données...)              |
| 09  | [Setup](09-setup.md)           | Préparer l'environnement (`setup-environment`) + cadrer la latitude laissée à l'IA pour une mission (`profile-environment`) |
| ... | ...                            | ...                                                                                  |

## «&nbsp;_Remonter, ne pas appliquer_&nbsp;»

> **Remonter, ne pas appliquer.** Les skills produisent&nbsp;; l'utilisateur décide.

Chaque skill _produit_ un rapport /&nbsp;une suggestion /&nbsp;un diff.  
L'humain _décide_ d'appliquer ou non.

## Chaînes récurrentes

### 1. Cycle en échec

```
review-report          →  analyse-*         →  write-a-probe
        ↓                       ↓                      ↓
   classification         instrumentation         script jetable
                                                       ↓
trouvailles propagées dans IDENTIFIED_GAPS.md / SFD / commentaires de scénario
                                                       ↓
                                                sonde supprimée
```

### 2. Scénario black-hat prometteur

```
empiricism             →  extend-coverage
    ↓                          ↓
vérifier le SUT          souvent en échec intentionnel
```

### 3. Changement de spec

```
update-frd-and-tests    (SFD d'abord, tests ensuite)
        ↓
les tests gap sont reformulés, pas basculés bêtement du rouge au vert
```

### 4. Nouvelle primitive Ocarina

```
understand-ocarina      →  mise à jour → reprise
        ↓
parcourt la doc
```

## Discipline transversale

1. **Remonter, ne pas appliquer.** L'utilisateur décide.
2. **Empirique plutôt qu'assertif.** Phrase rituelle&nbsp;: «&nbsp;_Juste remarque, je suppose. Je vérifie empiriquement._&nbsp;»
3. **Les tests gap sont reformulés, pas basculés au vert.**
4. **Les signaux des watchers sont négatifs uniquement.** Un watcher qui émet «&nbsp;_login réussi_&nbsp;» casse le contrat.
5. **Utilisation de systèmes distribués quand une ressource est partagée.**
6. **Repérage des artefacts avec mtime, pas juste par nom de fichier.** Les suffixes UUID sont aléatoires.
7. **La latitude ne fait que se resserrer.** Par défaut, tout est autorisé&nbsp;: démo publique ouverte (lire la source du SUT, sonder l'application réelle, identifiants publics). `profile-environment` resserre selon la mission&nbsp;; rien ne desserre jamais la ligne de sécurité.

## Hors périmètre

> - Ne génère pas de tests de façon autonome.
> - Ne patche pas les hallucinations en CI&nbsp;; un échec déclenche `review-report` + `analyse-*`.
> - Ne réécrit pas la spec&nbsp;; seul `update-frd-and-tests` le fait, avec une ligne de révision.
> - Ne fait pas de tests de sécurité actifs. Jamais.

Le périmètre est strict.  
L'IA est **un outil**, pas un substitut au jugement humain.
