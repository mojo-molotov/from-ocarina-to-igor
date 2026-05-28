---
title: "07.01 — Tree"
description: "The full tree of ocarina-example: pages, lib, api, caches, constants and tests of the reference e2e suite against the Igoristan."
weight: 1
date: 2026-05-20
series: ["ocarina-example"]
series_order: 1
tags: ["scenarios"]
---

# 07.01&nbsp;—&nbsp;Tree

```
src/
├── main.py                                                     # entry point (see README)
│
├── api/                                                        # external HTTP clients
│   ├── retrieve_dashboard_otp_code.py                          # filter + sort + pick OTP
│   ├── get_otp_history.py                                      # HTTP GET /api/otp-history
│   └── constants/endpoints.py                                  # URLs of tests-workers endpoints
│
├── caches/                                                     # in-memory L1 cache
│   ├── l1.py                                                   # dogpile.cache.memory TTL 30m
│   └── reserve_free_cache_key.py                               # UUID + threading.Lock
│
├── constants/                                                  # constants
│   ├── pages/
│   │   ├── homepage.py                                         # HOMEPAGE_URL
│   │   ├── dashboard.py                                        # DASHBOARD_URL + input ids
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
│   ├── connectors/test_steps/actions/                          # functions (TPOM) -> TPOM
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
│       │   │   │   ├── act.py                                  # ⭐ act adapter (on_failure hook)
│       │   │   │   ├── env_getters.py                          # ⭐ typed EnvGetters adapter
│       │   │   │   └── match_page.py                           # ⭐ match_page adapter
│       │   │   └── selenium/
│       │   │       ├── test_suite.py                           # ⭐ TestSuite adapter
│       │   │       ├── test_campaign.py                        # ⭐ TestCampaign adapter
│       │   │       ├── cli_getters.py                          # typed getters from CliStore
│       │   │       ├── logs.py                                 # create_just_log_error, etc.
│       │   │       └── screenshotter.py                        # take_screenshot helper
│       │   └── regex/error_page.py                             # ERROR_PAGE_REGEX
│       ├── redis/
│       │   └── client.py                                       # Redis Singleton client
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
│   │   └── fixtures/                                           # files to upload
│   ├── dashboard/
│   │   ├── login.py                                            # ⭐ with OTP, retries, redis locks
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

## Folder semantics

| Folder                               | Role                                         | Convention                                 |
| ------------------------------------ | -------------------------------------------- | ------------------------------------------ |
| `pages/`                             | POMs (inherit `SeleniumTitleMixin, POMBase`) | One class per page, fluent (`return self`) |
| `lib/connectors/test_steps/actions/` | Connectors `(TPOM) -> TPOM`                  | Pure functions; if parameters, closures    |
| `lib/custom_errors/`                 | Project exceptions                           | Exception subclasses                       |
| `lib/ext/ocarina/adapters/`          | Adapters above Ocarina                       | See [`02-adapters.md`](02-adapters.md)     |
| `lib/ext/redis/`                     | Redis Singleton wrapper                      | For distributed locks                      |
| `lib/ext/selenium/`                  | Selenium extensions specific to the project  | `HumanizedDriver`, `Watcher` callback      |
| `caches/`                            | In-memory L1 cache                           | `dogpile.cache.memory` + UUID reservation  |
| `constants/`                         | Constants                                    | URLs, redis keys, transient errors         |
| `api/`                               | External HTTP clients                        | OTP retrieval, OTP history                 |
| `tests/`                             | ISTQB hierarchy                              | cycles / campaigns / suites / scenarios    |

## `lib/` vs `pages/`

1. **`pages/`**: POMs&nbsp;—&nbsp;encapsulate a page's state (locators, action methods).
2. **`lib/connectors/test_steps/actions/`**: connectors&nbsp;—&nbsp;functions that call into POMs.

```python
act(on_homepage, open_homepage)
#                ^^^^^^^^^^^^^
#                connector defined in lib/connectors/test_steps/actions/homepage.py
```

```python
def open_homepage(p: Homepage) -> Homepage:
    return p.open()
```

The AI project's `CLAUDE.md` enforces this as a discipline:

> **Log factories, never inline lambdas.** `.failure(log_error("msg"))` / `.success(log_success("msg"))`.

And for connectors:

> A connector function must be used in at least one scenario; speculative ones are caught in review.

## `tests/scenarios/` vs `tests/suites/` vs `tests/campaigns/` vs `tests/cycles/`

| Folder       | Files                               | Type               |
| ------------ | ----------------------------------- | ------------------ |
| `scenarios/` | `(driver, logger) -> Scenario`      | scenario factories |
| `suites/`    | `(*, drivers_pool) -> TestSuite`    | suite factories    |
| `campaigns/` | `(*, drivers_pool) -> TestCampaign` | campaign factories |
| `cycles/`    | `(drivers_pool) -> TestCycle`       | cycle factories    |

Each level **only depends on the one below**.

## _Levels_ in `randomness/`

```
randomness/
├── level_1/{random_error_page,random_loaders_page}.py     # simple errors
├── level_2/{dsed,madness}.py                              # errors with branches
├── level_3/chaotic_form.py                                # UI chaos (HumanizedDriver + Watcher)
└── level_4/walkthrough.py                                 # journey accumulating several very random pages
```
