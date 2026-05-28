---
title: "07.01 — Arborescence"
description: "L'arborescence complète de ocarina-example : pages, lib, api, caches, constants et tests de la suite e2e de référence contre l'Igoristan."
weight: 1
date: 2026-05-20
series: ["ocarina-example"]
series_order: 1
tags: ["scenarios"]
---

# 07.01&nbsp;—&nbsp;Arborescence

```
src/
├── main.py                                                     # entry point (cf. README)
│
├── api/                                                        # clients HTTP externes
│   ├── retrieve_dashboard_otp_code.py                          # filter + sort + pick OTP
│   ├── get_otp_history.py                                      # HTTP GET /api/otp-history
│   └── constants/endpoints.py                                  # URLs des endpoints tests-workers
│
├── caches/                                                     # cache L1 in-memory
│   ├── l1.py                                                   # dogpile.cache.memory TTL 30m
│   └── reserve_free_cache_key.py                               # UUID + threading.Lock
│
├── constants/                                                  # constantes
│   ├── pages/
│   │   ├── homepage.py                                         # HOMEPAGE_URL
│   │   ├── dashboard.py                                        # DASHBOARD_URL + ids des inputs
│   │   ├── random_loaders.py
│   │   ├── sacred_upload.py
│   │   ├── corsicamon.py
│   │   ├── chaotic_form.py
│   │   ├── madness.py
│   │   ├── random_error_page.py
│   │   └── donkey_sausage_eater_detector.py
│   └── sys/
│       ├── redis_keys.py                                       # OTP_SEND_LOCK_KEY, ...
│       └── transient_errors.py                                 # (WebDriverException, HttpError...)
│
├── lib/
│   ├── connectors/test_steps/actions/                          # fonctions (TPOM) -> TPOM
│   │   ├── homepage.py
│   │   ├── dashboard_login.py                                  # ~10 connectors (with/without retries)
│   │   ├── dashboard_welcome.py
│   │   ├── dashboard_protected_page.py
│   │   ├── sacred_upload.py
│   │   ├── corsicamon_enter_api_key.py
│   │   ├── corsicamon_main.py
│   │   ├── chaotic_form.py
│   │   ├── random_error.py
│   │   ├── random_loaders.py
│   │   ├── madness.py
│   │   ├── this_is_bastia.py
│   │   ├── cors_errors.py
│   │   ├── bsod.py
│   │   ├── dsed.py
│   │   └── ids_bypassed.py
│   ├── custom_errors/
│   │   ├── http.py                                             # HttpErrorPageReachedError
│   │   └── transient_error.py                                  # TransientError
│   └── ext/                                                    # extensions / adapters
│       ├── ocarina/
│       │   ├── adapters/
│       │   │   ├── agnostic/
│       │   │   │   ├── act.py                                  # ⭐ adapter act (hook on_failure)
│       │   │   │   ├── env_getters.py                          # ⭐ adapter EnvGetters typé
│       │   │   │   └── match_page.py                           # ⭐ adapter match_page
│       │   │   └── selenium/
│       │   │       ├── test_suite.py                           # ⭐ adapter TestSuite
│       │   │       ├── test_campaign.py                        # ⭐ adapter TestCampaign
│       │   │       ├── cli_getters.py                          # getters typés depuis le CliStore
│       │   │       ├── logs.py                                 # create_just_log_error, etc.
│       │   │       └── screenshotter.py                        # take_screenshot helper
│       │   └── regex/error_page.py                             # ERROR_PAGE_REGEX
│       ├── redis/
│       │   └── client.py                                       # Singleton client Redis
│       └── selenium/
│           ├── humanize/                                       # ⭐ HumanizedDriver + keyboard
│           │   ├── proxy.py
│           │   └── keyboard.py
│           ├── pages/verify_elements_presence.py
│           └── watchers/catch_me_if_you_can_watcher.py         # ⭐ Watcher callback
│
├── pages/                                                      # POMs (Selenium + SeleniumTitleMixin)
│   ├── homepage.py
│   ├── random_loaders.py
│   ├── chaotic_form.py
│   ├── random_error.py
│   ├── sacred_upload/
│   │   ├── sacred_upload.py
│   │   └── fixtures/                                           # fichiers à uploader
│   ├── dashboard/
│   │   ├── login.py                                            # ⭐ avec OTP, retries, redis locks
│   │   ├── welcome_page.py
│   │   └── protected_page.py
│   ├── corsicamon/
│   │   ├── enter_api_key.py
│   │   └── main.py
│   ├── madness/
│   │   ├── base.py
│   │   ├── matchers.py                                         # has_cors, has_this_is_bastia
│   │   ├── cors.py
│   │   └── this_is_bastia.py
│   └── donkey_sausage_detector/
│       └── ids_bypassed.py
│
└── tests/
    ├── cycles/e2e.py                                           # ⭐ TestCycle (smoke + main)
    ├── campaigns/
    │   ├── global_smoke_tests.py                               # smoke
    │   ├── corsicamon.py                                       # main (+ smoke variant)
    │   ├── dashboard_login.py                                  # main
    │   ├── randomness.py                                       # main
    │   └── sacred_upload.py                                    # main
    ├── suites/
    │   ├── global_smoke_tests.py
    │   ├── randomness.py
    │   ├── dashboard/
    │   │   ├── access/
    │   │   │   ├── happy_paths.py
    │   │   │   └── unhappy_paths.py
    │   │   └── data_driven/multi_login.py
    │   ├── sacred_upload/{happy_paths,unhappy_paths}.py
    │   └── corsicamon/{smoke_tests,happy_paths,unhappy_paths}.py
    └── scenarios/
        ├── homepage/verify_homepage.py
        ├── dashboard/
        │   ├── access/{happy_paths,unhappy_paths}.py
        │   ├── back_to_igoristan.py
        │   └── data_driven/{multi_login,datasets/multi_login}.py
        ├── sacred_upload/{upload_files,just_go_back_to_igoristan}.py
        ├── corsicamon/{enter_api_key,new_draw,add_corsicamon,back_to_igoristan}.py
        └── randomness/
            ├── level_1/{random_error_page,random_loaders_page}.py
            ├── level_2/{dsed,madness}.py
            ├── level_3/chaotic_form.py
            └── level_4/walkthrough.py
```

## Sémantique des dossiers

| Dossier                              | Rôle                                          | Convention                                             |
| ------------------------------------ | --------------------------------------------- | ------------------------------------------------------ |
| `pages/`                             | POMs (héritent `SeleniumTitleMixin, POMBase`) | Une classe par page, fluent (`return self`)            |
| `lib/connectors/test_steps/actions/` | Connectors `(TPOM) -> TPOM`                   | Fonctions pures&nbsp;; si paramètres, closures         |
| `lib/custom_errors/`                 | Exceptions projet                             | Sous-classes d'Exception                               |
| `lib/ext/ocarina/adapters/`          | Adapters au-dessus d'Ocarina                  | Cf. [`02-adapters.md`](02-adapters.md)                 |
| `lib/ext/redis/`                     | Wrapper Singleton Redis                       | Pour les locks distribués                              |
| `lib/ext/selenium/`                  | Extensions Selenium spécifiques au projet     | `HumanizedDriver`, `Watcher` callback                  |
| `caches/`                            | Cache L1 in-memory                            | `dogpile.cache.memory` + UUID reservation              |
| `constants/`                         | Constantes                                    | URLs, redis keys, transient errors                     |
| `api/`                               | Clients HTTP externes                         | OTP retrieval, OTP history                             |
| `tests/`                             | Hiérarchie ISTQB                              | cycles /&nbsp;campaigns /&nbsp;suites /&nbsp;scenarios |

## `lib/` vs `pages/`

1. **`pages/`**&nbsp;: _POMs_, encapsulent l'état d'une page (locators, méthodes d'action).
2. **`lib/connectors/test_steps/actions/`**&nbsp;: _connectors_, fonctions qui _réfèrent_ aux POMs.

```python
act(on_homepage, open_homepage)
#                ^^^^^^^^^^^^^
#                connector défini dans lib/connectors/test_steps/actions/homepage.py
```

```python
def open_homepage(p: Homepage) -> Homepage:
    return p.open()
```

Le `CLAUDE.md` du projet IA en fait une discipline&nbsp;:

> **Log factories, never inline lambdas.** `.failure(log_error("msg"))` /&nbsp;`.success(log_success("msg"))`.

Et pour les connectors&nbsp;:

> A connector function must be used in at least one scenario; speculative ones are caught in review.

## `tests/scenarios/` vs `tests/suites/` vs `tests/campaigns/` vs `tests/cycles/`

| Dossier      | Fichiers                            | Type                  |
| ------------ | ----------------------------------- | --------------------- |
| `scenarios/` | `(driver, logger) -> Scenario`      | factories de scénario |
| `suites/`    | `(*, drivers_pool) -> TestSuite`    | factories de suite    |
| `campaigns/` | `(*, drivers_pool) -> TestCampaign` | factories de campagne |
| `cycles/`    | `(drivers_pool) -> TestCycle`       | factories de cycle    |

Chaque niveau **ne dépend que de celui en dessous**.

## _Levels_ dans `randomness/`

```
randomness/
├── level_1/{random_error_page,random_loaders_page}.py     # erreurs simples
├── level_2/{dsed,madness}.py                              # erreurs avec branches
├── level_3/chaotic_form.py                                # chaos UI (HumanizedDriver + Watcher)
└── level_4/walkthrough.py                                 # parcours accumulant plusieurs pages très aléatoires
```
