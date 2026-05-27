---
title: "Chapitre 07 — ocarina-example, la suite canonique"
description: "Suite e2e conçue pour tester l'Igoristan. C'est l'exemple de référence : tout projet Ocarina commence par lire ce dépôt et copier ses adapters."
weight: 8
date: 2026-05-20
tags: ["ocarina-example", "scenarios"]
sidebar:
  open: true
---

# Chapitre 07&nbsp;—&nbsp;`ocarina-example`

> Suite e2e conçue pour tester l'Igoristan. C'est l'**exemple de référence**&nbsp;: tout projet Ocarina commence par lire ce dépôt et copier ses adapters.

## Plan

|  #  | Fichier                                                          | Sujet                                                                                                          |
| :-: | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-tree.md`](01-tree.md)                                       | L'arborescence `src/` complète&nbsp;: pages/, lib/, api/, caches/, constants/, tests/.                         |
| 02  | [`02-adapters.md`](02-adapters.md)                               | Les 5 adapters (`act`, `match_page`, `TestSuite`, `TestCampaign`, `EnvGetters`).                               |
| 03  | [`03-scenarios-login.md`](03-scenarios-login.md)                 | Scénarios Dashboard login&nbsp;: happy /&nbsp;unhappy /&nbsp;data-driven.                                      |
| 04  | [`04-scenarios-corsicamon.md`](04-scenarios-corsicamon.md)       | Scénarios Corsicamon&nbsp;: api_key, draw, add, back.                                                          |
| 05  | [`05-scenarios-randomness.md`](05-scenarios-randomness.md)       | Scénarios randomness (4 levels)&nbsp;: random_error, random_loaders, dsed, madness, chaotic_form, walkthrough. |
| 06  | [`06-scenarios-sacred-upload.md`](06-scenarios-sacred-upload.md) | Scénarios sacred upload&nbsp;: upload_files, back_to_igoristan.                                                |
| 07  | [`07-humanized-driver.md`](07-humanized-driver.md)               | `HumanizedDriver`&nbsp;: proxy Selenium pour simuler la saisie humaine.                                        |
| 08  | [`08-caches-locks.md`](08-caches-locks.md)                       | Cache L1 (`dogpile.cache.memory`) + clés réservées + locks Redis distribués.                                   |
| 09  | [`09-watcher-catch-me.md`](09-watcher-catch-me.md)               | Le watcher `catch_me_if_you_can` pour le chaotic form.                                                         |
| 10  | [`10-env-getters.md`](10-env-getters.md)                         | `EnvGetters[_CredsKeys, _ValuesKeys]` typé strictement via `Literal`.                                          |
| 11  | [`11-ci.md`](11-ci.md)                                           | CI&nbsp;: `main_ci.yml` + `dev_ci.yml` (lint+typecheck) + `e2e.yml` (Redis&nbsp;+&nbsp;Firefox manuel).        |

## Objectif

Citation du Holy Book (chapitre «&nbsp;_Premiers pas_&nbsp;»)&nbsp;:

> **Note&nbsp;:** Ce livre a pour but de faciliter la prise en main du projet `ocarina-example` fourni, qui reste **la source de vérité** à consulter en toutes circonstances.

→ Le projet est documenté comme **la** référence canonique. Toute question sur _comment faire X_ commence par&nbsp;:&nbsp;«&nbsp;_regarde comment c'est fait dans `ocarina-example`_&nbsp;».

## `main.py`

```python
if __name__ == "__main__":
    CliStoreSingleton().push(create_selenium_auto_cli_store())

    drivers_pool = create_selenium_drivers_pool(...)
    logger = create_matching_logger(CliStoreSingleton().get("logger"))
    logger.info("Warming up the Redis client...")
    warmup_redis_client()
    logger.success("Redis client initialized!")

    def _post_exec(results: TestCycleResults) -> None:
        print()
        pretty_print_results(results, with_colors=True)
        if has_test_cycle_failed(results):
            sys.exit(1)

    with timing(prefix="Tests duration:"):
        bootstrap(
            post_exec=_post_exec,
            test_cycle=create_e2e_test_cycle(drivers_pool),
            run_plugins=lambda results: run_plugins(
                lambda: generate_docx_proof(...),
                lambda: generate_json_results(results=results, ...),
                exceptions_logger=...,
            ),
        )
```

## Cycle e2e

```python
# src/tests/cycles/e2e.py
E2E_CYCLE_NAME = "e2e"

def create_e2e_test_cycle(drivers_pool: SeleniumWebDriversPool):
    return TestCycle(
        name=E2E_CYCLE_NAME,
        campaigns=[
            create_igoristan_login_campaign(drivers_pool=drivers_pool),
            create_igoristan_randomness_campaign(drivers_pool=drivers_pool),
            create_igoristan_sacred_upload_campaign(drivers_pool=drivers_pool),
            create_igoristan_corsicamon_campaign(drivers_pool=drivers_pool),
        ],
        smoke_tests_campaigns=[
            create_igoristan_global_smoke_campaign(drivers_pool=drivers_pool),
            create_igoristan_corsicamon_smoke_campaign(drivers_pool=drivers_pool),
        ],
        mode="wait-for-all-smoke-tests",
    )
```

- **Mode**&nbsp;: `wait-for-all-smoke-tests` (les deux smoke tournent même si l'un fail).
- **2 smoke campaigns** (global + corsicamon).
- **4 main campaigns** (login, randomness, sacred upload, corsicamon).
