---
title: "Chapitre 04 — Tests internes du framework"
description: "Comment Ocarina se teste lui-même : cinq familles de tests, une politique de couverture assumée et un rapport Allure historisé sur GitHub Pages."
weight: 5
date: 2026-05-20
tags: ["tests-internes", "typage", "scenarios"]
sidebar:
  open: true
---

# Chapitre 04&nbsp;—&nbsp;Tests internes du framework

> Comment Ocarina se teste lui-même. Cinq familles de tests, une politique de couverture lucide, un rapport Allure historisé sur GitHub Pages.

## Plan

|  #  | Fichier                                                      | Sujet                                                                                                          |
| :-: | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-strategy.md`](01-strategy.md)                           | Stratégie «&nbsp;_dehors comme un utilisateur_&nbsp;» + le `conftest.py` (FakeDriver, RecordingPOM, builders). |
| 02  | [`02-cram-prysk.md`](02-cram-prysk.md)                       | Cram tests (`prysk`)&nbsp;: fichiers `.t`                                                                      |
| 03  | [`03-pytest-scenarios.md`](03-pytest-scenarios.md)           | Scénarios de test appliqués au framework (pytest + allure + hypothesis).                                       |
| 04  | [`04-mypy-plugins-types.md`](04-mypy-plugins-types.md)       | Tests sur le **typage statiques** via `pytest-mypy-plugins` (`*.yml`).                                         |
| 05  | [`05-syrupy-snapshots.md`](05-syrupy-snapshots.md)           | Snapshot tests (`syrupy`) pour `pretty_print_results` et `results_to_json`.                                    |
| 06  | [`06-hypothesis-properties.md`](06-hypothesis-properties.md) | Property-based testing pour les invariants.                                                                    |
| 07  | [`07-coverage-policy.md`](07-coverage-policy.md)             | Politique de couverture&nbsp;: ce qui est testé, ce qui ne l'est PAS, pourquoi.                                |
| 08  | [`08-allure-history.md`](08-allure-history.md)               | Allure + action composite `allure-history` + déploiement GH Pages.                                             |

## Tableau récapitulatif

| Famille         | Outil                      | Quantité                                    | Sujet                                               | Cible                               |
| --------------- | -------------------------- | ------------------------------------------- | --------------------------------------------------- | ----------------------------------- |
| Scénarios       | `pytest` + `allure-pytest` | ~13 fichiers `test_*.py`                    | DSL et orchestration                                | Couvre le _comportement_            |
| Cram            | `prysk`                    | 10 fichiers `.t`                            | CLI&nbsp;: parsing, validations, defaults           | Couvre la _surface utilisateur CLI_ |
| Types statiques | `pytest-mypy-plugins`      | ~5 fichiers `*test_types.yml`               | Inférences de type, narrowing, erreurs attendues    | Couvre le _typage_                  |
| Snapshots       | `syrupy`                   | 2 fichiers `.ambr`                          | Sortie de `pretty_print_results`, `results_to_json` | Couvre le _format de sortie_        |
| Property-based  | `hypothesis`               | 1 fichier (`test_invariants_properties.py`) | Comportement sur valeurs aléatoires                 | Couvre la _robustesse aux inputs_   |

## Approche

Dans le fichier `conftest.py`&nbsp;:

> Philosophy&nbsp;: exercise the framework from the outside the way a real user does. No asserts on private attributes, no mocks of framework internals&nbsp;—&nbsp;just a minimal fake driver + driver pool, and small constructors for Scenario /&nbsp;Test /&nbsp;TestSuite /&nbsp;TestCampaign /&nbsp;TestCycle.

Les tests **n'inspectent pas** les mécanismes internes (phénomène de la _sonde anale_\*). Ils _exercent_ le framework comme un projet utilisateur le ferait. C'est la garantie que les tests valident le _contrat public_, pas l'implémentation.

\* _Attribuer ce phénomène sous forme de citation à un confrère de la littérature pour les plus facétieux._
