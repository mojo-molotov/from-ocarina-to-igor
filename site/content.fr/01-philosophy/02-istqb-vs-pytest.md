---
title: "01.02 — ISTQB vs pytest / Jest / Mocha"
description: "Pourquoi Ocarina adopte le vocabulaire ISTQB là où pytest, Jest et Mocha restent hybrides, et la hiérarchie Test, Suite, Campaign, Cycle qui en découle."
weight: 2
date: 2026-05-20
series: ["philosophie"]
series_order: 2
tags: ["istqb"]
---

# 01.02&nbsp;—&nbsp;ISTQB vs pytest /&nbsp;Jest /&nbsp;Mocha

## Le constat méthodologique

Au-delà du pari technique sur la barrière techniques /&nbsp;non-techniques (voir [`01-flip-the-problem.md`](01-flip-the-problem.md)), il y a un **second pari**&nbsp;: celui du vocabulaire métier.

> L'ISTQB et les testeurs professionnels ont construit, depuis des décennies, un vocabulaire précis et éprouvé&nbsp;: _cycles de test_, _campagnes_, _suites de test_, _cas de test_, _pas de test_. Une hiérarchie claire, pensée pour **organiser, tracer et piloter** la qualité logicielle.
>
> Les outils automatisés, eux, ont **largement ignoré cet héritage**.
>
> _pytest_, _Jest_, _Mocha_… tous sont **un mix hybride** où les testeurs doivent apprendre à penser comme des développeurs, et où personne ne parle vraiment la même langue.

## La conséquence architecturale

Ocarina prend ce vocabulaire **au sérieux** et le transpose littéralement dans la hiérarchie de classes.

| Vocabulaire ISTQB | Classe Ocarina                                            | Fichier source                                                    |
| ----------------- | --------------------------------------------------------- | ----------------------------------------------------------------- |
| Pas de test       | `act()` (verbe utilisateur, retourne `ActionStart[TPOM]`) | `src/ocarina/dsl/testing_with_railway/constructors/create_act.py` |
| Cas de test       | `Test[Driver]`                                            | `src/ocarina/dsl/testing/oc_test.py`                              |
| Suite de test     | `TestSuite[Driver]`                                       | `src/ocarina/dsl/testing/oc_test_suite.py`                        |
| Campagne          | `TestCampaign[Driver]`                                    | `src/ocarina/dsl/testing/oc_test_campaign.py`                     |
| Cycle             | `TestCycle[Driver]`                                       | `src/ocarina/dsl/testing/oc_test_cycle.py`                        |

Ce ne sont pas des «&nbsp;_namespaces décoratifs_&nbsp;»&nbsp;: chaque niveau a une **responsabilité distincte** (cf. [`../02-ocarina/05-orchestration/`](../02-ocarina/05-orchestration/README.md))&nbsp;:

| Niveau         | Responsabilité                                                                         |
| -------------- | -------------------------------------------------------------------------------------- |
| `act`          | Une action atomique sur une page.                                                      |
| `Test`         | Métadonnées (`name`, `test_id`, `skipped`) + scénario + fragments pre/post + watchers. |
| `TestSuite`    | Pool de drivers, parallélisation, _saturation_, filtrage IDs, retries policy.          |
| `TestCampaign` | Séquence de suites avec config workers partagée.                                       |
| `TestCycle`    | Smoke + main, _mode_ appliqué aux smokes tests (fail-fast \| wait-for-all).            |

## La rupture avec pytest

Ocarina n'est **pas** un plugin pytest. Le README l'affirme explicitement&nbsp;:

> Ships its own test runner: Ocarina is NOT a pytest plugin.

Pourquoi&nbsp;?

1. **Le vocabulaire pytest n'est pas l'ISTQB.** pytest a `test_function`, `parametrize`, `fixture`, `conftest`. C'est cohérent _en interne_ mais c'est un autre univers. Faire d'Ocarina un plugin pytest aurait obligé à _traduire_, exactement ce que la philosophie refuse (cf. [`01-flip-the-problem.md`](01-flip-the-problem.md)).
2. **Indépendance.** Un plugin dépend de l'API de son hôte. Ocarina veut être auditable en une après-midi, sans connaître pytest.
3. **Posture envers les fixtures.** Ocarina remplace les fixtures par des _closures_ + _scenario fragments_ + _Effect_ pour `setup`/`teardown`. La posture est celle du «&nbsp;_poor man's rich_&nbsp;»&nbsp;: un seul mécanisme, la **closure**, pour _toutes_ les injections. Une closure suffit là où la POO classique invoquerait fixtures + scopes + héritage.

## La rupture avec Cucumber /&nbsp;Gherkin

Aucun fichier `.feature`, aucune step definition, aucun glue layer. Le scénario est **du Python**, exécutable directement, typé directement, refactorisable directement. Aucune traduction permanente à maintenir.

Le «&nbsp;_langage_&nbsp;» qu'expose Ocarina aux scénarios n'est pas un DSL textuel&nbsp;; c'est un **DSL Python embedded**&nbsp;:

```python
return [
    drive_page(
        act(on_homepage, open_then_verify_homepage)
            .failure(just_log_error("Failed to reach the homepage..."))
            .success(log_success_with_current_url_and_take_screenshot("On the homepage!")),
        act(on_homepage, click_book_call_page_cta)
            .failure(just_log_error("Failed to click on the 'Book a call' CTA..."))
            .success(just_log_success("Clicked on the 'Book a call' CTA!")),
    ),
    drive_page(
        act(on_book_a_call_page, verify_book_call_page)
            .failure(just_log_error("Failed to verify the 'Book a call' page..."))
            .success(log_success_with_current_url_and_take_screenshot("On the 'Book a call' page!")),
    ),
]
```

C'est du Python pur. Aucun lexer, aucun runtime tiers, aucune traduction. Et c'est typé&nbsp;: la moindre incompatibilité est une erreur _mypy_ (cf. [`../02-ocarina/03-railway/02-action-chain-states.md`](../02-ocarina/03-railway/02-action-chain-states.md)).

## Conséquence sur le reporting

Le _reporting_ aussi colle au vocabulaire ISTQB. `pretty_print_results` produit&nbsp;:

```
Campaign
• Suite
  > Test case 1
    » PASSED
  > Test case 2
    » FAILED
      → Error message
        ⫸ At step 3
```

Trois indentations, trois niveaux&nbsp;: campagne, suite, cas. Le _step_ est mentionné comme contexte d'échec («&nbsp;_At step 3_&nbsp;»). Aucun nom de classe Python n'apparaît dans la sortie&nbsp;: l'utilisateur final voit du vocabulaire métier, pas du code.

## Glossaire ISTQB ↔ Ocarina

| Terme ISTQB     | Terme Ocarina                                                          | Note                                                                      |
| --------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| _Test step_     | `act()`                                                                | Action atomique.                                                          |
| _Test case_     | `Test[Driver]`                                                         | Encapsule un scénario.                                                    |
| _Test scenario_ | `Scenario[Driver]`                                                     | Composé d'une `test_chain`, d'un `setup`, d'un `teardown`, de `watchers`. |
| _Test suite_    | `TestSuite[Driver]`                                                    | Parallélisé.                                                              |
| _Test campaign_ | `TestCampaign[Driver]`                                                 | Séquentiel (entre suites).                                                |
| _Test cycle_    | `TestCycle[Driver]`                                                    | Smoke + main, fail-fast ou wait-for-all.                                  |
| _Smoke test_    | `smoke_tests_campaigns=`                                               | Gate.                                                                     |
| _Setup_         | `Scenario.setup: Effect`                                               | `Effect`.                                                                 |
| _Teardown_      | `Scenario.teardown: Effect`                                            | `Effect` également&nbsp;; toujours exécuté, erreurs ignorées.             |
| _Test report_   | `pretty_print_results`, `generate_docx_proof`, `generate_json_results` | Plugins post-exec.                                                        |

## Lien avec l'évolution du système de types Python

Le Holy Book trace une dépendance fine&nbsp;: ce vocabulaire ne pouvait pas être incarné aussi rigoureusement avant les _generics_ PEP 695, parce qu'il faut pouvoir paramétrer `TestSuite[Driver]` avec un type de driver précis&nbsp;:

> Les récentes évolutions du _système de types_ de Python, sur lequel Ocarina s'appuie profondément, font partie de la raison-même de sa faisabilité.

C'est aussi pour cette raison que le framework est en `requires-python = ">=3.14"` (cf. [`../00-big-picture/02-stack-matrix.md`](../00-big-picture/02-stack-matrix.md)).
