---
title: "01.01 — Prendre le problème à l'envers"
description: "Le pari fondateur d'Ocarina face à Robot Framework et Cucumber : supprimer la barrière entre ceux qui codent et ceux qui définissent les tests."
weight: 1
date: 2026-05-20
series: ["philosophie"]
series_order: 1
---

# 01.01&nbsp;—&nbsp;Prendre le problème à l'envers

## Le constat

Tous les frameworks de test e2e contemporains ont été construits sur un postulat implicite&nbsp;: il existe une **barrière** entre _ceux qui codent_ et _ceux qui définissent les tests_. Cette barrière est tenue pour acquise&nbsp;: méthodologiquement, organisationnellement, parfois contractuellement.

> La plupart des frameworks de test ont été conçus dans un monde où la barrière entre «&nbsp;_ceux qui codent_&nbsp;» et «&nbsp;_ceux qui définissent les tests_&nbsp;» était réelle et structurelle.

Les deux réponses _historiques_ à ce postulat sont citées nommément dans le Holy Book&nbsp;:

### Robot Framework

> _Robot Framework_ a essayé de la contourner avec un _DSL_ (_Domain Specific Language_), incluant **leur propre format** et **leur propre écosystème de plugins**. Ainsi, RF impose de-facto ses propres standards&nbsp;: c'est le coût immédiat de sa promesse.

Mécanique&nbsp;: on remplace la complexité du code par la complexité **d'un autre code**. Le ticket d'entrée n'est pas annulé, il est _déplacé_. Désormais on doit apprendre la syntaxe RF, son écosystème de _librairies_ et de _ressources_, sa façon d'orchestrer.

### Cucumber

> _Cucumber_ a essayé avec le _Gherkin_&nbsp;: un langage «&nbsp;_naturel_&nbsp;» qui, en pratique, **contraint tout le monde sans vraiment libérer personne**. Coût&nbsp;: couche de traduction permanente, désynchronisation Gherkin/code.

Mécanique&nbsp;: on construit une _illusion_ de langage naturel, qui a en réalité une grammaire stricte et une sémantique limitée. Le coût n'est pas le langage en lui-même mais la **couche de traduction permanente** entre le Gherkin et le code Step Definitions, qui dérive dans le temps si elle n'est pas surveillée.

## Le pari opposé

Plutôt que de _déguiser_ la barrière, Ocarina parie qu'**elle va disparaître**&nbsp;:

> **Ocarina parie sur le contraire&nbsp;:** cette barrière va disparaître. Il s'agit d'un non-débat sur lequel tout le monde s'est construit un nœud autour du cou. Outils honteusement compliqués, vendus comme «&nbsp;_solutions_&nbsp;». Impact&nbsp;: **désastre opérationnel** dès lors que l'on a un besoin qui ne peut pas s'exprimer dans un «&nbsp;_cadre_&nbsp;» qui n'est PAS réellement générique.

Et&nbsp;:

> Et le pire&nbsp;: **toutes ces technologies continueront d'évoluer dans ce sens**. AUCUNE d'entre elle ne prendra ce _shift_, puisqu'il s'agit d'un changement de paradigme et d'**un retour aux fondamentaux qui contredit totalement leur proposition de valeur**.

## L'IA est le pont, pas le DSL

Le verrou rhétorique du Holy Book sur ce point&nbsp;:

> Avec l'IA, et des outils comme _Claude Code_, ce pari devient chaque jour plus solide. Le pont entre techniques et non-techniques n'est plus une couche d'abstraction.
>
> **C'est l'IA elle-même. IA qui travaille sur de la donnée brute.**

Conséquences observables dans le code&nbsp;:

| Choix de design                                                  | Justification ramenée à ce pari                                                        |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Pas de DSL textuel (pas de fichiers `.robot`, pas de `.feature`) | L'IA travaille mieux sur du Python typé que sur un méta-langage à grammaire propre.    |
| `ruff` ALL + `mypy` strict                                       | Plus la donnée brute est typée et lintée, plus l'IA peut la consommer de façon fiable. |
| `CLAUDE.md`, `CLAUDE.slim.md` exposés                            | L'IA est un client de première classe de la documentation.                             |
| 40+ `skills/` versionnés sur GitHub                              | Les procédures _LLM-friendly_ sont des artefacts comme les autres.                     |
| `llms.txt` /&nbsp;`llms-full.txt` générés au build VitePress     | Le site _publie_ activement vers les LLMs.                                             |

L'incarnation pratique est le dépôt [`ocarina-with-ai-example`](../08-ai-example/README.md)&nbsp;: une suite e2e _réelle_, écrite **à 99% par Claude Code**, mais dont l'intelligence est partagée à hauteur de 50-50 entre l'auteur et l'IA.

## Le coût de la «&nbsp;_créativité_&nbsp;» des autres

Le Holy Book formalise pourquoi le nivellement par DSL n'est pas neutre&nbsp;:

> Le coût le plus important est un **nivellement par le bas, la réduction des options et une «&nbsp;_flexibilité_&nbsp;» qui s'obtient en se _battant_ contre des _outils_ plutôt que d'utiliser des _solutions_**.

> Pourtant, ce qu'il nous reste à présent, c'est le besoin d'un code de test **lisible, traçable et flexible**, sous sa forme la plus **brute**.

Le mot _brute_ est important&nbsp;: il revient ailleurs («&nbsp;_données brutes_&nbsp;», «&nbsp;_la donnée brute_&nbsp;»), et c'est l'axe sur lequel le projet se prolonge vers l'IA. Voir [`05-political-stance.md`](05-political-stance.md), section «&nbsp;_Anti No-Code_&nbsp;».

## Conséquences sur l'architecture d'Ocarina

| Position philosophique      | Conséquence architecturale                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pas de DSL textuel          | Pas de parser, pas de _runtime_ alternatif. Python pur.                                                                                           |
| Pas de couche de traduction | Pas de Gherkin /&nbsp;pas de Step Definitions. Le _connector_ `(TPOM) -> TPOM` est la plus petite unité, écrite en Python.                        |
| IA = pont privilégié        | Une partie significative de la doc est _formellement_ destinée aux LLMs (`llms.txt`, `skills/`, `CLAUDE.md`).                                     |
| Pas d'écosystème de plugins | Pas de plugin pytest. Ocarina embarque son propre runner. Tout l'écosystème Python peut être utilisé sans friction à la liberté de l'utilisateur. |
| Strictness maximale         | `ruff ALL`, `mypy strict`, `@final` partout, `noqa` toujours explicites et locaux.                                                                |
