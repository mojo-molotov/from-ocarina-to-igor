---
title: "Chapter 07 — ocarina-example, the canonical suite"
description: "ocarina-example, the reference e2e suite against the Igoristan: the repository every Ocarina project reads and copies adapters from."
weight: 8
date: 2026-05-20
tags: ["ocarina-example", "scenarios"]
sidebar:
  open: true
---

# Chapter 07&nbsp;—&nbsp;`ocarina-example`

> E2E suite designed to test Igoristan. The **reference example**: every Ocarina project starts by reading this repo and copying its adapters.

## Outline

|  #  | File                                                             | Topic                                                                                                    |
| :-: | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 01  | [`01-tree.md`](01-tree.md)                                       | The full `src/` tree: pages/, lib/, api/, caches/, constants/, tests/.                                   |
| 02  | [`02-adapters.md`](02-adapters.md)                               | The 5 adapters (`act`, `match_page`, `TestSuite`, `TestCampaign`, `EnvGetters`).                         |
| 03  | [`03-scenarios-login.md`](03-scenarios-login.md)                 | Dashboard login scenarios: happy / unhappy / data-driven.                                                |
| 04  | [`04-scenarios-corsicamon.md`](04-scenarios-corsicamon.md)       | Corsicamon scenarios: api_key, draw, add, back.                                                          |
| 05  | [`05-scenarios-randomness.md`](05-scenarios-randomness.md)       | Randomness scenarios (4 levels): random_error, random_loaders, dsed, madness, chaotic_form, walkthrough. |
| 06  | [`06-scenarios-sacred-upload.md`](06-scenarios-sacred-upload.md) | Sacred upload scenarios: upload_files, back_to_igoristan.                                                |
| 07  | [`07-humanized-driver.md`](07-humanized-driver.md)               | `HumanizedDriver`: Selenium proxy to simulate human typing.                                              |
| 08  | [`08-caches-locks.md`](08-caches-locks.md)                       | L1 cache (`dogpile.cache.memory`) + reserved keys + distributed Redis locks.                             |
| 09  | [`09-watcher-catch-me.md`](09-watcher-catch-me.md)               | The `catch_me_if_you_can` watcher for the chaotic form.                                                  |
| 10  | [`10-env-getters.md`](10-env-getters.md)                         | `EnvGetters[_CredsKeys, _ValuesKeys]` strictly typed via `Literal`.                                      |
| 11  | [`11-ci.md`](11-ci.md)                                           | CI: `main_ci.yml` + `dev_ci.yml` (lint+typecheck) + `e2e.yml` (Redis + manual Firefox).                  |

## Goal

Holy Book quote (chapter "First steps"):

> **Note:** This manual is intended to help you get familiar with the provided `ocarina-example` project, which remains **the source of truth** to refer to in all circumstances.

The project is documented as **the** canonical reference. Any question about how to do X starts with: "look at how it's done in `ocarina-example`".

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

## E2E cycle

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

- **Mode**: `wait-for-all-smoke-tests` (both smokes run even if one fails).
- **2 smoke campaigns** (global + corsicamon).
- **4 main campaigns** (login, randomness, sacred upload, corsicamon).
