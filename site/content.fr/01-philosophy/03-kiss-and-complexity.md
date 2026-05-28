---
title: "01.03 — KISS et complexité ostentatoire"
description: "La réponse d'Ocarina à la critique de simplicité : KISS bien compris, la distinction entre simple et peu élaboré, et le refus de la complexité ostentatoire."
weight: 3
date: 2026-05-20
series: ["philosophie"]
series_order: 3
tags: ["rop", "typage"]
---

# 01.03&nbsp;—&nbsp;KISS et complexité ostentatoire

## La critique reçue

Le premier retour public reçu par Ocarina, _systématique_ d'après l'auteur&nbsp;:

> La première «&nbsp;_critique_&nbsp;» a souvent été la même&nbsp;: «&nbsp;_Tu te vantes de quelque chose qui est très simple._&nbsp;»

Le Holy Book y répond longuement. Trois piliers&nbsp;: le **caractère opérant** de la simplicité, la **distinction simple ≠ peu élaboré**, et le **refus de toutes les contre-propositions «&nbsp;_créatives_&nbsp;»** reçues.

## Simple ≠ peu élaboré

> C'est aussi pour cette raison que **KISS** (_Keep it simple, stupid_) est si mal compris dans l'industrie&nbsp;: **beaucoup imaginent que «&nbsp;_simple_&nbsp;» signifie «&nbsp;_peu élaboré_&nbsp;»**.
> Difficile de moins bien comprendre une théorie.

Ce qui est «&nbsp;_simple_&nbsp;» est le **résultat** d'un travail d'élaboration. C'est un état terminal, pas un état initial.

## Les contre-propositions refusées

L'article _Premiers retours_ énumère, **point par point**, les contributions que d'autres «&nbsp;_confrères_&nbsp;» ont essayé d'imposer. Chacune est citée _pour être refusée_&nbsp;:

> - Tordre l'implémentation de ROP (_Railway Oriented Programming_) d'Ocarina jusqu'à lui en faire perdre tout son sens, puisqu'ils ne savaient même pas ce que signifie ROP,
> - Inclure des «&nbsp;_hooks_&nbsp;» et autres «&nbsp;_techniques de ninja_&nbsp;» en plein milieu des pas de test,
> - Abandonner le typage,
> - Tout réécrire en Rust pour la «&nbsp;_performance_&nbsp;»,
> - M'imposer leur incompréhension de l'évaluation paresseuse et de l'_IoC_ comme des vérités absolues,
> - «&nbsp;_M'expliquer_&nbsp;» ce que sont la programmation impérative et déclarative en racontant n'importe quoi,
> - Me «&nbsp;_parler_&nbsp;» d'_event-driven programming_, toujours en racontant n'importe quoi,
> - Et pire que tout, me parler d'une horrifiante théorie d'«&nbsp;_orienté objet déclaratif_&nbsp;»,
> - Etc.

Chacun de ces refus est documenté par un _choix de design_ d'Ocarina&nbsp;:

| Refus                                           | Choix Ocarina                                                                                                                                                                                                                                                                                |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| «&nbsp;_Tordre ROP_&nbsp;»                      | `Result[T]`, machine à états `ActionStart → ActionFailure → ActionSuccess → ActionChain`, `Neutral*` pour le rail d'échec. Strictement linéaire, ne peut pas être détourné. Voir [`../02-ocarina/03-railway/02-action-chain-states.md`](../02-ocarina/03-railway/02-action-chain-states.md). |
| «&nbsp;_Hooks au milieu des pas de test_&nbsp;» | Hooks confinés à `create_act(on_failure=…, on_run_effect=…, act_counter_effect=…)`. Pas de hook _global_ injectable. Voir [`../02-ocarina/03-railway/05-create-act-hooks.md`](../02-ocarina/03-railway/05-create-act-hooks.md).                                                              |
| «&nbsp;_Abandonner le typage_&nbsp;»            | `mypy strict = true`, `ruff select = ALL`, generics PEP 695 partout, `pytest-mypy-plugins` pour _tester les types_. Voir [`../04-internal-tests/04-mypy-plugins-types.md`](../04-internal-tests/04-mypy-plugins-types.md).                                                                   |
| «&nbsp;_Réécrire en Rust_&nbsp;»                | Python pur. Le sujet du framework est la _lisibilité_ et le _vocabulaire métier_, pas la performance brute qui ne dépend pas ici du langage utilisé pour l'orchestration.                                                                                                                    |
| «&nbsp;_Incompréhension IoC /&nbsp;lazy_&nbsp;» | `Effect`, `Thunk`, `ChainRunner`, `validate(...).execute()`, `Watcher.callback`&nbsp;: tout est paresseux, et l'IoC est documentée dans le code. Voir [`../03-functional/`](../03-functional/README.md).                                                                                     |
| «&nbsp;_Orienté objet déclaratif_&nbsp;»        | `@final` partout&nbsp;; pas d'héritage non contrôlé&nbsp;; extension par **composition** (closures, adapters projet).                                                                                                                                                                        |

## Le compliment recherché

> Et si, en lisant un premier scénario de test, la réaction est «&nbsp;_c'est super simple_&nbsp;», il est dommage de penser le faire sur le ton de la critique&nbsp;: **c'est exactement le compliment recherché**.
> Merci.

Cette phrase est centrale&nbsp;: la simplicité du résultat _est_ la métrique de qualité. Une métrique inverse «&nbsp;_regarde comme c'est élaboré_&nbsp;» est explicitement qualifiée de _narcissisme_ dans le Holy Book&nbsp;:

> Le **narcissisme** s'exprime à travers le fait de tout rendre honteusement compliqué dans l'unique but de _dominer_. Pas à travers l'acquisition de compétences et la simplification des process, puisque la finalité est le dysfonctionnement total&nbsp;: le chaos.

## L'intolérance à l'échec, signal narcissique

Le Holy Book introduit une catégorie clinique&nbsp;: l'intolérance à l'échec comme signature du narcissique en environnement de test.

> On les reconnaît aussi face à leur _intolérance à l'échec_. Ils veulent systématiquement montrer à quel point, EUX, ont «&nbsp;_pensé à tout_&nbsp;».
> Jamais de rouge avec un narcissique, que du vert, que du «&nbsp;_prêt à partir en production_&nbsp;».

Ocarina prend le parti opposé&nbsp;: **un échec documenté vaut mieux**. C'est exactement la posture d'`ocarina-with-ai-example` qui _conserve_ ses tests en échec sur les gaps de CURA (cf. [`../08-ai-example/05-security-gaps.md`](../08-ai-example/05-security-gaps.md))&nbsp;:

> Anything red _outside_ those categories is a real regression or a transient network error.

Et la règle est gravée dans le `CLAUDE.md` du projet IA&nbsp;:

> **Les tests gap sont reformulés, pas basculés au vert.** Inverser l'assertion, renommer, déplacer la ligne dans le doc de stratégie, consigner la date dans `IDENTIFIED_GAPS.md`.

## La praticité comme objectif

La conclusion de l'article&nbsp;:

> Plutôt que de vouloir «&nbsp;_faire des trucs de geeks_&nbsp;», Ocarina propose de résoudre de _petits problèmes_ sans en créer de plus importants.
> La conclusion qui en a été tirée est&nbsp;:&nbsp;«&nbsp;_Ocarina est pratique_&nbsp;».
> C'est le but d'Ocarina&nbsp;:&nbsp;sa praticité.
