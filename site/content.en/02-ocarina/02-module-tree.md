---
title: "02.02 — The ocarina module tree"
weight: 2
date: 2026-05-20
series: ["ocarina"]
series_order: 2
---

# 02.02&nbsp;—&nbsp;The `ocarina` module tree

The Python source module ships **114 `.py` files** across four conceptual layers.

```
src/ocarina/
├── __init__.py                              # empty — no global "facade", everything is imported precisely
├── py.typed                                 # PEP 561: declares the package as "typed"
│
├── railway/                                 # Layer 1 — FP primitives
│   ├── __init__.py
│   └── result.py                            # Ok[T] / Fail / Result[T] / is_ok / is_fail
│
├── custom_types/                            # Layer 2 — types and aliases
│   ├── __init__.py
│   ├── effect.py                            # type Effect = Callable[[], None]
│   ├── thunk.py                             # type Thunk[T] = Callable[[], T]
│   ├── tpom.py                              # TypeVar TPOM bound POMBase
│   ├── supports_write.py                    # Protocol SupportsWrite[T], mirrors a type not exposed by Python stdlib
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
├── custom_errors/                           # Layer 2: errors
│   ├── __init__.py
│   └── test_framework/
│       ├── __init__.py
│       ├── no_matching_branch.py            # NoMatchingBranchError
│       ├── pages.py                         # PageVerificationError
│       ├── driver_died.py                   # DriverDiedError
│       └── campaigns.py
│
├── custom_invariants/                       # Layer 2: ready-to-use invariants
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
├── ports/                                   # Layer 3: ports (interfaces)
│   ├── __init__.py
│   ├── ilogger.py                           # ILogger (ABC)
│   └── itake_screenshot.py                  # ITakeScreenshot[Driver] (Protocol)
│
├── pom/                                     # Layer 3: Page Object Model
│   ├── __init__.py
│   ├── base.py                              # POMBase (ABC: verify + get_current_title)
│   └── selenium/
│       ├── __init__.py
│       └── muted.py                         # MutedPOM utility
│
├── aggregates/                              # Layer 3: result aggregates
│   ├── __init__.py
│   └── tests_layers.py                      # is_test_result_ok / _fail / _skipped (TypeGuard)
│
├── dsl/                                     # Layer 4: Ocarina DSL
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
│       │   └── create_act.py                # low-level primitive (to be wrapped on the project side)
│       └── internals/
│           ├── __init__.py
│           └── action_chain.py              # ActionStart → ActionFailure → ActionSuccess → ActionChain
│                                            # + Neutral{Start,Failure,Success}  (failure rail)
│
├── infra/                                   # Layer 5: infrastructure
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
│       ├── driver_healthcheck.py            # driver_healthcheck (pings driver.title)
│       └── mixins.py                        # SeleniumTitleMixin (typing keyway)
│
└── opinionated/                             # Layer 6: opt-in, everything that is "nice but replaceable"
    ├── __init__.py
    ├── consts/loggers_choices.py            # LOGGERS_CHOICES = ("terminal", "file", "terminal+file", "muted")
    ├── infra/
    │   ├── __init__.py
    │   └── act_counter.py                   # ThreadsBasedActCounter (thread-local counter)
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
    │   └── drive_page.py                    # drive_page = chain_actions, a semantic alias
    ├── launcher/
    │   ├── __init__.py
    │   └── bootstrap.py                     # bootstrap(...) + run_plugins(*plugins, exceptions_logger)
    ├── loggers/
    │   ├── __init__.py
    │   ├── create_matching_logger.py        # create_matching_logger("terminal"|"file"|...) + get_default_log_dir
    │   ├── print_logger.py                  # PrintLogger (ANSI)
    │   ├── file_logger.py                   # FileLogger (taxonomy -> file tree)
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
            ├── pretty_print_results.py      # hierarchical ANSI report
            ├── results_to_json.py           # JSON generator
            ├── docx_tests_proofs.py         # DOCX generator (consumes the log tree)
            └── timing.py                    # context manager `with timing(prefix="Duration:")`
```

## Layered diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│ USER PROJECT (e.g. ocarina-example, ocarina-with-ai-example)             │
│  ┌────────────────────┐  ┌────────────────────┐  ┌─────────────────────┐ │
│  │ pages/ (POMBase)   │  │ scenarios/ (Test)  │  │ adapters/ (act, ...)│ │
│  └────────────────────┘  └────────────────────┘  └─────────────────────┘ │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │ imports
┌─────────────────────────────────▼────────────────────────────────────────┐
│ LAYER 6 — opinionated/  (CLI, loggers, plugins, bootstrap)               │
│   Opt-in. Can be replaced wholesale.                                     │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ LAYER 5 — infra/  (pool, builder, screenshotter, Selenium adapters)      │
│   I/O. No DSL logic.                                                     │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ LAYER 4 — dsl/  (testing, invariants, testing_with_railway)              │
│   Pure DSL, no I/O. All the grammar.                                     │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ LAYER 3 — ports/  +  pom/  +  aggregates/                                │
│   Interfaces and abstractions.                                           │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ LAYER 2 — custom_types/  +  custom_errors/  +  custom_invariants/        │
│   Shapes, aliases, types, exceptions, ready-to-use invariants.           │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼────────────────────────────────────────┐
│ LAYER 1 — railway/  (Result, Ok, Fail, is_ok, is_fail)                   │
│   The functional primitive. No dependencies.                             │
└──────────────────────────────────────────────────────────────────────────┘
```

This **strict stratification** rules out _import cycles_ and lets you swap any upper layer without touching the ones below:

| Replace               | Consequence                                                                                                                      |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **`opinionated/`**    | You keep the DSL and the orchestration. No loss. See [`11-opinionated/`](11-opinionated/README.md).                              |
| **`infra/selenium/`** | You can use Playwright, Puppeteer, or a fake driver. The signature to honor is `BuiltWebDriver[Driver] = tuple[Driver, Effect]`. |
| **`pom/selenium/`**   | Same: `POMBase` is agnostic.                                                                                                     |

## Import relationships

| Isolation-breaking import                          | Verdict                                                                                                                                                                                                                    |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `railway/result.py` imports something from Ocarina | **No**. No internal dependency.                                                                                                                                                                                            |
| `custom_types/` imports `dsl/`                     | **No**. All arrows point the other way.                                                                                                                                                                                    |
| `dsl/` imports `infra/`                            | **Almost not**: only the orchestration calls the `ActCounter` (default instance) from `opinionated/infra/`, and `WebDriversPool` from `infra/`. The pure DSL (`testing_with_railway/`, `invariants/`) never touches infra. |
| `ports/` imports `infra/`                          | **No**. Ports sit above infra.                                                                                                                                                                                             |
