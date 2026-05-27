# Ch 02 — Ocarina framework

Chapter brief for LLM navigation. Source articles: `site/content.en/02-ocarina/`.

## Articles

| File | Description |
| --- | --- |
| `01-identity.md` | Technical identity: Python 3.14+, v1.1.0, single runtime dependency (`selenium`), `mypy --strict`, MIT. |
| `02-module-tree.md` | Full Python module tree with layered ASCII diagram. **Contains ASCII diagram.** |
| `03-railway/01-result.md` | `Result[T]` discriminated union: `Ok[T]` / `Err`. The base type of the entire railway. |
| `03-railway/02-action-chain-states.md` | `ActionChain` builder state machine: EMPTY → LOADED → COMMITTED. **Contains ASCII diagram.** |
| `03-railway/03-neutral-rail.md` | The neutral rail: how a chain absorbs errors without stopping. |
| `03-railway/04-chain-actions-fold.md` | `chain_actions`: fold-left over a list of thunks, threading `Result[T]`. |
| `03-railway/05-create-act-hooks.md` | `create` / `act` hooks: lifecycle entry points for scenarios. |
| `03-railway/06-drive-page.md` | `drive_page`: typed page navigation returning `Result[PageObject]`. |
| `03-railway/07-match-page-when.md` | `match_page` / `when`: pattern-matching on the current page. |
| `04-invariants/01-validate-flow.md` | Full validate → `assert_that` → `execute` flow. **Contains ASCII diagram.** |
| `04-invariants/02-assertions.md` | The assertion library: `assert_that`, `assert_url`, `assert_text`, etc. |
| `04-invariants/03-otherwise-any-of.md` | `otherwise` / `any_of`: logical combinators for invariants. |
| `04-invariants/04-then-chain-of-validations.md` | `then` / `chain_of_validations`: sequential invariant chains. |
| `04-invariants/05-business-vs-framework-validator.md` | Distinction between business validators and framework validators. |
| `04-invariants/06-invariant-errors.md` | Invariant error class hierarchy. **Contains ASCII diagram.** |
| `05-orchestration/01-test.md` | `Test` dataclass: the atomic unit. |
| `05-orchestration/02-test-executor.md` | `TestExecutor` internal flow: setup, run, teardown, result collection. **Contains ASCII diagram.** |
| `05-orchestration/03-test-flow-retries.md` | Retry logic and test flow states. |
| `05-orchestration/04-test-suite.md` | `TestSuite`: grouping `Test` objects, smoke vs regression. |
| `05-orchestration/05-saturation.md` | Saturation mode: running every test until the pool is exhausted. |
| `05-orchestration/06-test-campaign.md` | `TestCampaign`: the top-level orchestrator, fan-out to cycles. |
| `05-orchestration/07-test-cycle-modes.md` | `TestCycle` modes: standard, saturation, filter. |
| `05-orchestration/08-filter-tests-by-ids.md` | Filtering tests by ID for targeted reruns. |
| `06-scenario.md` | `Scenario` lifecycle: `create` → `act` → invariants → result. |
| `07-watcher.md` | `Watcher`: lazy callback registered on a chain, fires on state change. |
| `08-pom-base.md` | `POMBase`: the base class all Page Object Models inherit from. |
| `09-ports.md` | Ports and adapters: `ILogger`, `ITakeScreenshot` — the two interfaces Ocarina depends on. |
| `10-infra/01-drivers-pool.md` | `DriversPool`: concurrent Selenium driver lifecycle management. |
| `10-infra/02-driver-builder.md` | `DriverBuilder`: constructs Firefox/Chrome WebDrivers with options. |
| `10-infra/03-screenshotter.md` | `Screenshotter`: `ITakeScreenshot` implementation. |
| `10-infra/04-act-counter.md` | `ActCounter`: counts actions for saturation and metrics. |
| `10-infra/05-selenium-adapters.md` | Selenium adapters: typed wrappers around raw WebDriver calls. |
| `11-opinionated/01-cli-builder.md` | `CLIBuilder`: Click-based CLI construction for test suites. |
| `11-opinionated/02-cli-store-phantoms.md` | Store and phantom CLI parameters. |
| `11-opinionated/03-selenium-cli.md` | `SeleniumCLI`: opinionated CLI entry point for Selenium campaigns. |
| `11-opinionated/04-loggers.md` | Built-in loggers: console, file, structured. |
| `11-opinionated/05-plugins-reports.md` | Reporter plugins: Allure, JSON, composite. |
| `11-opinionated/06-bootstrap-launcher.md` | `bootstrap`: the one function that wires everything and starts the campaign. |
| `12-custom-types-errors.md` | Custom types (`PageUrl`, `TestId`, …) and custom error hierarchy. |

## Key concepts

- **Railway Oriented Programming (ROP)**: every operation returns `Result[T]`. Errors are values, never exceptions (in normal flow). The chain short-circuits on `Err` without raising.
- **`ActionChain`**: builder pattern over a list of thunks. State machine prevents misuse at static analysis time.
- **Invariants**: `validate(driver).assert_that(condition).execute()` — observe first, assert second. Never execute without having observed.
- **ISTQB hierarchy**: `Test` < `TestSuite` < `TestCampaign` < `TestCycle`. Each level has a defined contract.
- **Ports**: Ocarina core depends on two interfaces (`ILogger`, `ITakeScreenshot`). Everything else is a detail.
- **Single runtime dep**: only `selenium`. No test runner, no assertion lib, no fixture framework.
- **`mypy --strict`**: the entire framework is fully typed. Type errors are caught statically.

## Diagrams

- `02-module-tree.md` — full Python module tree.
- `03-railway/02-action-chain-states.md` — `ActionChain` state machine.
- `04-invariants/01-validate-flow.md` — validate → assert_that → execute flow.
- `04-invariants/06-invariant-errors.md` — invariant error class hierarchy.
- `05-orchestration/02-test-executor.md` — `TestExecutor` internal flow.

## Connections

- FP patterns underlying the design → Ch 03
- Framework testing itself → Ch 04
- Canonical usage in a real suite → Ch 07
- AI-authored suite → Ch 08
- Philosophy motivating the design → Ch 01

## Not covered here

Private helpers, internal test utilities beyond the documented families, deprecated APIs, API changes after v1.1.0. Runtime debugging (geckodriver troubleshooting, Selenium session errors) is not documented.
