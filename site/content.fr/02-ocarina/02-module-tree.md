---
title: "02.02 — Arborescence du module ocarina"
description: "L'arborescence du module Python ocarina : 114 fichiers répartis en quatre couches conceptuelles, du railway aux composants opinionated."
weight: 2
date: 2026-05-20
series: ["ocarina"]
series_order: 2
---

# 02.02&nbsp;—&nbsp;Arborescence du module `ocarina`

Le module Python source contient **114 fichiers `.py`** répartis en quatre couches conceptuelles.

```
src/ocarina/
├── __init__.py                              # vide — pas de "facade" globale, on importe précisément
├── py.typed                                 # PEP 561 : déclare le package comme "typed"
│
├── railway/                                 # Couche 1 — primitives FP
│   ├── __init__.py
│   └── result.py                            # Ok[T] / Fail / Result[T] / is_ok / is_fail
│
├── custom_types/                            # Couche 2 — types et alias
│   ├── __init__.py
│   ├── effect.py                            # type Effect = Callable[[], None]
│   ├── thunk.py                             # type Thunk[T] = Callable[[], T]
│   ├── tpom.py                              # TypeVar TPOM bound POMBase
│   ├── supports_write.py                    # Protocol SupportsWrite[T], reflète type non exposé par lib standard Python
│   ├── built_web_driver.py                  # type BuiltWebDriver[Driver] = tuple[Driver, Effect]
│   ├── scenario.py                          # Scenario[Driver] (frozen dataclass)
│   ├── test_components.py                   # TestChain / TestSetup / TestTeardown / TestWatchers
│   ├── test_runner.py                       # TestRunner[Driver]
│   ├── oc_test.py                           # TestName / TestScenario / TestScenarioFragment
│   ├── oc_test_layers.py                    # TestResult / TestSuiteResult / TestCampaignResults / TestCycleResults
│   └── selenium/
│       ├── built_web_driver.py              # BuiltSeleniumWebDriver
│       ├── oc_test_scenario.py
│       ├── supported_browsers.py            # type SupportedSeleniumBrowser = Literal["chrome", "firefox", "edge", "safari"]
│       └── web_drivers_pool.py              # type SeleniumWebDriversPool = WebDriversPool[WebDriver]
│
├── custom_errors/                           # Couche 2 : erreurs
│   ├── __init__.py
│   └── test_framework/
│       ├── __init__.py
│       ├── no_matching_branch.py            # NoMatchingBranchError
│       ├── pages.py                         # PageVerificationError
│       ├── driver_died.py                   # DriverDiedError
│       └── campaigns.py
│
├── custom_invariants/                       # Couche 2 : invariants prêts-à-l'emploi
│   ├── __init__.py
│   └── testing/
│       ├── __init__.py
│       ├── workers.py                       # validate_workers_amount
│       ├── oc_test_runners_ids.py           # validate_test_runners_ids
│       ├── oc_test_runners_names.py         # validate_test_runners_names (unique + valid filename)
│       ├── oc_test_suites_names.py
│       ├── oc_test_campaigns_names.py
│       └── oc_test_cycles_names.py
│
├── ports/                                   # Couche 3 : ports (interfaces)
│   ├── __init__.py
│   ├── ilogger.py                           # ILogger (ABC)
│   └── itake_screenshot.py                  # ITakeScreenshot[Driver] (Protocol)
│
├── pom/                                     # Couche 3 : Page Object Model
│   ├── __init__.py
│   ├── base.py                              # POMBase (ABC : verify + get_current_title)
│   └── selenium/
│       ├── __init__.py
│       └── muted.py                         # MutedPOM utilitaire
│
├── aggregates/                              # Couche 3 : agrégats de résultats
│   ├── __init__.py
│   └── tests_layers.py                      # is_test_result_ok / _fail / _skipped (TypeGuard)
│
├── dsl/                                     # Couche 4 : DSL Ocarina
│   ├── __init__.py
│   ├── invariants/
│   │   ├── __init__.py
│   │   ├── validate.py                      # entry-point validate(), BusinessInvariantValidator, FrameworkInvariantValidator
│   │   ├── assertions.py                    # is_str / is_email / is_positive / is_in / has_unique_elements / each / ...
│   │   ├── errors.py                        # InvariantViolationError / DuplicatesError / AggregateInvariantViolationError
│   │   └── internals/
│   │       ├── __init__.py
│   │       └── validation_chain.py          # ValidationStartBlock / ValidationAssertBlock / _ValidationChain / _any_of / chain_validations
│   ├── testing/
│   │   ├── __init__.py
│   │   ├── oc_test.py                       # class Test[Driver]
│   │   ├── oc_test_suite.py                 # class TestSuite[Driver]
│   │   ├── oc_test_campaign.py              # class TestCampaign[Driver] + campaign_has_failed
│   │   ├── oc_test_cycle.py                 # class TestCycle[Driver] + type Mode + has_test_cycle_failed
│   │   ├── filter_tests_by_ids.py
│   │   ├── watcher.py                       # class Watcher[Driver]
│   │   ├── internals/
│   │   │   ├── __init__.py
│   │   │   ├── test_executor.py             # class TestExecutor[Driver] + ExecutionOutcome (frozen, slots)
│   │   │   └── test_flow.py                 # class TestFlow[Driver]
│   │   └── selenium/
│   │       ├── __init__.py
│   │       ├── create_test.py               # create_selenium_test(...)
│   │       └── create_watcher.py            # create_selenium_watcher(...) + type SeleniumWatcher
│   └── testing_with_railway/
│       ├── __init__.py
│       ├── chain_actions.py                 # class ChainRunner[T] + chain_actions
│       ├── match_page.py                    # When + _match_page_builder + create_match_page
│       ├── constructors/
│       │   ├── __init__.py
│       │   └── create_act.py                # primitive de bas niveau (à wrapper côté projet)
│       └── internals/
│           ├── __init__.py
│           └── action_chain.py              # ActionStart → ActionFailure → ActionSuccess → ActionChain
│                                            # + Neutral{Start,Failure,Success}  (rail d'échec)
│
├── infra/                                   # Couche 5 : infrastructure
│   ├── __init__.py
│   ├── drivers_pool.py                      # class WebDriversPool[Driver] + WarmupTimeoutError
│   ├── driver_builder.py                    # class DriverBuilder[Driver]
│   ├── screenshotter.py                     # class Screenshotter[TDriver] + ScreenshotterConfig
│   ├── act_counter.py                       # class ActCounter (interface)
│   └── selenium/
│       ├── __init__.py
│       ├── create_driver.py                 # _build_firefox / _build_chrome / _build_edge / _build_safari
│       ├── create_drivers_pool.py           # create_selenium_drivers_pool
│       ├── create_screenshotter.py          # create_selenium_screenshotter
│       ├── driver_healthcheck.py            # driver_healthcheck (ping driver.title)
│       └── mixins.py                        # SeleniumTitleMixin (détrompeur de typage)
│
└── opinionated/                             # Couche 6 : opt-in, tout ce qui est "joli mais remplaçable"
    ├── __init__.py
    ├── consts/loggers_choices.py            # LOGGERS_CHOICES = ("terminal", "file", "terminal+file", "muted")
    ├── infra/
    │   ├── __init__.py
    │   └── act_counter.py                   # ThreadsBasedActCounter (compteur thread-local)
    ├── cli/
    │   ├── __init__.py
    │   ├── builder.py                       # CliBuilder + CliArg + _SilentArgumentParser
    │   ├── store.py                         # CliStore[TKeys] + _CliField[T] + field(...)
    │   ├── phantoms.py                      # phantom_validate (no-op predicate)
    │   └── selenium/
    │       ├── __init__.py
    │       ├── cli_store_singleton.py       # SeleniumCliStoreSingleton (push / get)
    │       └── create_cli_store.py          # create_selenium_{auto,win,macos,linux}_cli_store
    ├── dsl/
    │   ├── __init__.py
    │   └── drive_page.py                    # drive_page = chain_actions, alias sémantique
    ├── launcher/
    │   ├── __init__.py
    │   └── bootstrap.py                     # bootstrap(...) + run_plugins(*plugins, exceptions_logger)
    ├── loggers/
    │   ├── __init__.py
    │   ├── create_matching_logger.py        # create_matching_logger("terminal"|"file"|...) + get_default_log_dir
    │   ├── print_logger.py                  # PrintLogger (ANSI)
    │   ├── file_logger.py                   # FileLogger (taxonomie -> arbre de fichiers)
    │   ├── print_and_file_logger.py
    │   ├── muted_logger.py
    │   ├── custom_types/supported_loggers.py
    │   └── utils/
    │       ├── __init__.py
    │       └── format_metadata_str.py       # format_utc_date_metadata_str / format_current_thread_metadata_str / concat_metadata
    └── plugins/
        ├── __init__.py
        └── reports/
            ├── __init__.py
            ├── pretty_print_results.py      # rapport ANSI hiérarchique
            ├── results_to_json.py           # générateur JSON
            ├── docx_tests_proofs.py         # générateur DOCX (consomme l'arbre de logs)
            └── timing.py                    # context manager `with timing(prefix="Duration:")`
```

## Schéma en couches

```
┌──────────────────────────────────────────────────────────────────────────┐
│ USER PROJECT (e.g. ocarina-example, ocarina-with-ai-example)             │
│  ┌────────────────────┐  ┌────────────────────┐  ┌─────────────────────┐ │
│  │ pages/ (POMBase)   │  │ scenarios/ (Test)  │  │ adapters/ (act, ...)│ │
│  └────────────────────┘  └────────────────────┘  └─────────────────────┘ │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │ imports
┌─────────────────────────────────▼────────────────────────────────────────┐
│ COUCHE 6 — opinionated/  (CLI, loggers, plugins, bootstrap)              │
│   opt-in. Peut être remplacée intégralement.                             │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ COUCHE 5 — infra/  (pool, builder, screenshotter, adapters Selenium)     │
│   I/O. Pas de logique DSL.                                               │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ COUCHE 4 — dsl/  (testing, invariants, testing_with_railway)             │
│   DSL pur, sans I/O. Toute la grammaire.                                 │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ COUCHE 3 — ports/  +  pom/  +  aggregates/                               │
│   Interfaces et abstractions.                                            │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ COUCHE 2 — custom_types/  +  custom_errors/  +  custom_invariants/       │
│   _Shapes_, alias, types, exceptions, invariants prêts-à-l'emploi.       │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ COUCHE 1 — railway/  (Result, Ok, Fail, is_ok, is_fail)                  │
│   La primitive fonctionnelle. Aucune dépendance.                         │
└──────────────────────────────────────────────────────────────────────────┘
```

Cette **stratification stricte** garantit l'absence de _cycles d'import_ et permet de remplacer chaque couche supérieure sans toucher aux couches inférieures&nbsp;:

| Substituer            | Conséquence                                                                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **`opinionated/`**    | On garde le DSL et l'orchestration. Aucune perte. Voir [`11-opinionated/`](11-opinionated/README.md).                                     |
| **`infra/selenium/`** | On peut utiliser Playwright, Puppeteer, ou un fake driver. La signature à respecter est `BuiltWebDriver[Driver] = tuple[Driver, Effect]`. |
| **`pom/selenium/`**   | Idem&nbsp;: `POMBase` est agnostique.                                                                                                     |

## Relation d'imports

| import brisant isolation                            | Constat                                                                                                                                                                                                                                 |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `railway/result.py` importe quelque chose d'Ocarina | **Non**. Aucune dépendance interne.                                                                                                                                                                                                     |
| `custom_types/` importe `dsl/`                      | **Non**. Toutes les flèches vont dans l'autre sens.                                                                                                                                                                                     |
| `dsl/` importe `infra/`                             | **Quasi non**&nbsp;: seule l'orchestration appelle l'`ActCounter` (instance par défaut) issue de `opinionated/infra/`, et `WebDriversPool` du `infra/`. Mais le DSL pur (`testing_with_railway/`, `invariants/`) ne touche pas l'infra. |
| `ports/` importe `infra/`                           | **Non**. Les ports sont au-dessus de l'infra.                                                                                                                                                                                           |
