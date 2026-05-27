---
title: "09.04 — CLAUDE.md et CLAUDE.slim.md"
description: "Le Holy Book publie activement les fichiers CLAUDE.md. Cela permet à un LLM de récupérer la doc projet sans passer par le repo."
weight: 4
date: 2026-05-20
series: ["holy-book"]
series_order: 4
---

# 09.04&nbsp;—&nbsp;`CLAUDE.md` et `CLAUDE.slim.md`

> Le Holy Book **publie activement** les fichiers `CLAUDE.md`. Cela permet à un LLM de récupérer la doc projet sans passer par le repo.

## Les deux fichiers

```
ai/
├── CLAUDE.md       # version complète (règles + organisation projet)
└── CLAUDE.slim.md  # version courte (règles uniquement)
```

## URLs publiques

```
https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md
https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md
```

Citation du Holy Book (chapitre «&nbsp;_Utiliser Ocarina avec l'IA_&nbsp;»)&nbsp;:

> Slim quand le contexte est chargé&nbsp;; complet pour l'onboarding et les revues. En cas de divergence, le complet l'emporte.

## Différences Slim/Full

| Aspect                        | `CLAUDE.md`  | `CLAUDE.slim.md` |
| ----------------------------- | ------------ | ---------------- |
| Volume                        | ~600+ lignes | ~150-200 lignes  |
| Règles                        | ✅ toutes    | ✅ toutes        |
| Justifications détaillées     | ✅           | ❌               |
| Exemples du passé (expertise) | ✅           | ❌               |
| Organisation du projet        | ✅           | ❌               |
| Hiérarchie technique          | ✅           | ❌               |
| Conventions de PR             | ✅           | ❌               |
| Forme attendue de la CI       | ✅           | ❌               |

## Le bon fichier au bon moment

```
Onboarding (premier contact avec le projet)  →  CLAUDE.md  (lit tout)
Run normal (juste appliquer les règles)       →  CLAUDE.slim.md (économise tokens)
Revue de PR                                   →  CLAUDE.md (justifications)
Audit profond                                 →  CLAUDE.md (tout)
```

## `CLAUDE.md`

Sections type (basées sur `ocarina-with-ai-example`)&nbsp;:

1. **Project context**&nbsp;: repo, framework, SUT.
2. **Project philosophy**&nbsp;: «&nbsp;_No tricks or hacks_&nbsp;», «&nbsp;_Teach the pattern, not the symptom_&nbsp;».
3. **Layout**&nbsp;: arbre complet du repo.
4. **Conventions**&nbsp;: 12+ règles concrètes.
5. **Hard-won rules**&nbsp;: leçons tirées d'échecs passés.
6. **Test strategy**&nbsp;: structure du cycle.
7. **Running tests**&nbsp;: commandes CLI.
8. **Reports and screenshots**&nbsp;: règles d'usage.
9. **Scenario fragments**&nbsp;: critères d'extraction.
10. **Data-driven tests**&nbsp;: conventions.
11. **Conventions complémentaires**.

## `CLAUDE.slim.md`

Juste les **règles** (sans justifications détaillées, sans exemples)&nbsp;:

```markdown
# Slim rules — Ocarina with AI example

- No tricks or hacks. Polling fix > JS click bypass.
- Teach the pattern, not the symptom.
- Tests sécurité : fonctionnels et statiques, jamais actifs.
- Utiliser des constantes : pas de magic numbers.
- Datasets : décision humaine ; propose, pas exécute.
- Vérifier empiriquement le SUT avant d'encoder.
- Re-dériver à chaque exécution : pas d'héritage de diagnostic.
- One scenario per file (data-driven exception).
- Top docstring as arrows flow.
- All create_selenium_test() at bottom of file.
- POM selectors at top of class.
- Always WebDriverWait, never raw find_element.
- Implicit wait set by CLI, never patched in POM/test code.
- Tests gap : reformulés, pas basculés au vert.
- Watcher signals : negatifs uniquement.
- Distribué quand ressource partagée.
- Mtime pas nom de fichier.
- ...
```

→ Chaque ligne = une règle.

## Pourquoi exposer aux LLMs

| Sans exposition publique                                                                                         | Avec exposition                              |
| ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| Un LLM doit cloner le repo pour lire le CLAUDE.md                                                                | URL canonique&nbsp;→&nbsp;un seul `WebFetch` |
| Pas de découverte «&nbsp;_hors session_&nbsp;» (un utilisateur qui pose une question Ocarina sans avoir le repo) | Le LLM peut lire la doc directement          |
| Indexation difficile par les moteurs de recherche LLM                                                            | Indexé naturellement                         |

## La distinction _doc utilisateur_ vs _doc LLM_

| Doc                                                 | Audience       | Format                                   |
| --------------------------------------------------- | -------------- | ---------------------------------------- |
| Holy Book (`/setup`, `/scenarios-composability`, …) | Humain         | Prose, exemples, illustrations           |
| `CLAUDE.md`                                         | LLM (+ humain) | Règles sèches, justifications condensées |
| `skills/*/SKILL.md`                                 | LLM            | Recettes opérationnelles                 |

→ Trois audiences, trois formats. Le Holy Book sert les trois. C'est l'**incarnation pratique** de «&nbsp;_l'IA est le pont_&nbsp;».

## Pattern «&nbsp;_ressources canoniques_&nbsp;»

Les URLs sont stables&nbsp;:

```
https://mojo-molotov.github.io/ocarina-holy-book/llms.txt
https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt
https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md
https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md
https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf
https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf
```

Documentées dans le Holy Book (chapitre «&nbsp;_Utiliser Ocarina avec l'IA_&nbsp;»), à la fin&nbsp;:

> ## Ressources exposées
>
> - https://mojo-molotov.github.io/ocarina-holy-book/llms.txt
> - https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt
> - https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md
> - https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-ru.pdf
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf
