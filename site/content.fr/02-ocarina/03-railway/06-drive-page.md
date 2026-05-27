---
title: "02.03.06 — drive_page"
description: "Fichier source : src/ocarina/opinionated/dsl/drive_page.py"
weight: 6
date: 2026-05-20
series: ["railway"]
series_order: 6
tags: ["ocarina", "rop", "scenarios"]
---

# 02.03.06&nbsp;—&nbsp;`drive_page`

> Fichier source&nbsp;: [`src/ocarina/opinionated/dsl/drive_page.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/dsl/drive_page.py)

## Code

```python
def drive_page(
    first: ActionSuccess[TPOM], *rest: ActionSuccess[TPOM]
) -> ChainRunner[TPOM]:
    return chain_actions(first, *rest)
```

C'est **exactement** `chain_actions`.

## Pourquoi cet alias&nbsp;?

### 1. Sémantique&nbsp;: «&nbsp;_je prends le contrôle d'une page_&nbsp;»

Citation du Holy Book (_Premiers scénarios_)&nbsp;:

> `drive_page` exprime que l'on prend le contrôle d'_une_ page.
> Toute _transition_ devient explicite par l'ouverture d'un nouveau `drive_page`.

```python
return [
    drive_page(
        act(on_homepage, open_homepage)...,
        act(on_homepage, verify_homepage)...,
        act(on_homepage, click_cta)...,
    ),                                          # ⬅ fermeture du contrôle de la homepage
    drive_page(                                 # ⬅ ouverture du contrôle de la page suivante
        act(on_target_page, verify_target_page)...,
    ),
]
```

### 2. Discipline

Mélanger des actes sur deux POMs différents dans un même `drive_page` devient une erreur _mypy_ (cf. [`02-action-chain-states.md`](02-action-chain-states.md), section «&nbsp;_narrowing par `act()`_&nbsp;»). Cela force concrètement à respecter la sémantique.

### 3. Lecture des rapports

Le `CLAUDE.md` d'`ocarina-with-ai-example` documente la règle qui dépend de cette sémantique&nbsp;:

> **Every `drive_page` produces at least one `log_and_screenshot`.** A `drive_page` models one page's worth of work and almost always ends by submitting /&nbsp;navigating /&nbsp;verifying&nbsp;—&nbsp;it _is_ a page transition. The report's screenshot sequence must let a reader replay the journey `drive_page` by `drive_page`&nbsp;; «&nbsp;_one screenshot per scenario_&nbsp;» collapses a multi-page journey into a single still.

Donc&nbsp;: **un `drive_page` = un screenshot de fin** (au moins). Le rapport DOCX (cf. [`../11-opinionated/05-plugins-reports.md`](../11-opinionated/05-plugins-reports.md)) devient une bande dessinée du parcours.

## Conséquences architecturales

| Conséquence                                                     | Détail                                                                                                                                                                                                              |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Un `drive_page` est typé sur _un_ POM** (`ChainRunner[TPOM]`) | Le checker refuse les pas de test sur des pages hétérogènes                                                                                                                                                         |
| **Multi-pages = liste de `drive_page`**                         | Le scénario retourne `list[drive_page(...), drive_page(...), drive_page(...)]`                                                                                                                                      |
| **Composabilité**                                               | `drive_page(...)` est un `ChainRunner`&nbsp;; on peut le stocker dans une variable, le passer en argument, le mettre dans une branche `match_page`                                                                  |
| **Pas de logique custom**                                       | `drive_page` est un **monomorphisme** de `chain_actions` (même fonction, type plus étroit). On peut écrire son propre `drive_component` ou `drive_modal` qui retourne aussi un `ChainRunner` et qui se compose avec |

## L'alias est dans `opinionated/`, pas dans `dsl/`

`drive_page` vit dans `src/ocarina/opinionated/dsl/`, pas dans `src/ocarina/dsl/`.

- Le DSL «&nbsp;_pur_&nbsp;» ne contient que `chain_actions` (et `create_act`, `match_page`).
- `drive_page` est un _alias sémantique_ opt-in, un **monomorphisme** de `chain_actions` qui n'apporte aucune logique mais nomme l'intention.
- Un projet pourrait théoriquement importer **uniquement** `chain_actions` et créer son propre alias (`drive_workflow`, `drive_section`, `drive_component`, etc.) sans toucher au framework.

C'est cohérent avec la philosophie «&nbsp;_grammaire souveraine_&nbsp;» du Holy Book. Voir [`../../11-independence/01-sovereign-grammar.md`](../../11-independence/01-sovereign-grammar.md)

## Tests dédiés

Plusieurs tests dans [`tests/scenarios/`](https://github.com/mojo-molotov/ocarina/tree/main/tests/scenarios) exercent `drive_page` (via les conftest `acting(pom, step)` et `scenario_of("ok")`). Ces tests valident&nbsp;:

- l'exécution séquentielle des actes,
- le court-circuit après échec,
- le comptage d'`act` thread-local.
