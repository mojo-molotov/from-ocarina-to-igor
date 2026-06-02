# Skill: locate

**Goal**: given a symbol (class name, method, type, CLI flag, endpoint, config key, error type), return the primer article that documents it — without navigating by topic.

**Scope**: primer only. Index maps symbols to article paths under `site/content.en/`.

**Primer base URL**: `https://mojo-molotov.github.io/from-ocarina-to-igor/`  
**Related skills**: `{base}/skills/fetch/SKILL.md` · `{base}/skills/answer/SKILL.md` · `{base}/skills/navigate/SKILL.md` · `{base}/skills/synthesize/SKILL.md`

**Prerequisite**: none. This skill is standalone. Use it when you know the name of what you're looking for (not its topic). If you only know the topic, use `navigate/SKILL.md` instead.

---

## Quick jump by chapter

If you already know which repo or layer the symbol belongs to, jump directly to that section of the index below:

| Domain | Jump to |
| --- | --- |
| Railway (`Result`, `ActionChain`, `chain_actions`, `drive_page`, `match_page`) | [Railway](#framework-core--railway-02-ocarina03-railway) |
| Invariants (`validate`, `assert_that`, `InvariantViolationError`) | [Invariants](#framework-core--invariants-02-ocarina04-invariants) |
| Orchestration (`Test`, `TestFlow`, `TestSuite`, `TestCampaign`, `TestCycle`, `filter_tests_by_ids`) | [Orchestration](#framework-core--orchestration-02-ocarina05-orchestration) |
| Framework other (`Scenario`, `Watcher`, `POMBase`, `ILogger`, `DriversPool`, `PlaywrightDriver`, `bootstrap`) | [Framework other](#framework-core--other-02-ocarina) |
| Functional patterns (`Thunk`, `Effect`, `TypeGuard`, `fold`) | [Functional](#functional-patterns-03-functional) |
| Internal tests (`FakeDriver`, `syrupy`, `hypothesis`, `prysk`) | [Internal tests](#internal-tests-04-internal-tests) |
| Igoristan (`useAuth`, `wireit`, `LoginForm`, routes) | [Igoristan](#igoristan-05-igoristan) |
| tests-workers (`/api/otp`, `isAuthorized`, Upstash) | [tests-workers](#tests-workers-06-tests-workers) |
| ocarina-example (`HumanizedDriver`, `EnvGetters`, `catch_me_if_you_can`, adapters) | [ocarina-example](#ocarina-example-07-ocarina-example) |
| AI example (CURA, gap codes, `ai_proof_e2e.yml`) | [AI example](#ocarina-with-ai-example-08-ai-example) |
| Holy Book (`llms.txt`, `CLAUDE.md`, PDF, VitePress) | [Holy Book](#holy-book-09-holy-book) |
| CI/CD (workflow files, geckodriver, Allure history) | [CI/CD](#cicd-10-cicd) |
| Glossary / references | [References](#glossary-and-references-99-references) |

---

## Step 1 — look up the symbol

Find the symbol in the index below. Match is exact first, then prefix, then substring.

If no match: go to **Step 3 — not found**.

---

## Index

### Framework core — Railway (`02-ocarina/03-railway/`)

| Symbol | Article |
| --- | --- |
| `Result[T]`, `Ok[T]`, `Err`, `Fail` | `02-ocarina/03-railway/01-result.md` |
| `ActionChain`, EMPTY, LOADED, COMMITTED | `02-ocarina/03-railway/02-action-chain-states.md` |
| neutral rail, `has_failed` | `02-ocarina/03-railway/03-neutral-rail.md` |
| `chain_actions`, `ChainRunner` | `02-ocarina/03-railway/04-chain-actions-fold.md` |
| `create`, `act` (lifecycle hooks) | `02-ocarina/03-railway/05-create-act-hooks.md` |
| `drive_page` | `02-ocarina/03-railway/06-drive-page.md` |
| `match_page`, `when` | `02-ocarina/03-railway/07-match-page-when.md` |

### Framework core — Invariants (`02-ocarina/04-invariants/`)

| Symbol | Article |
| --- | --- |
| `validate`, `assert_that`, `execute` | `02-ocarina/04-invariants/01-validate-flow.md` |
| `assert_url`, `assert_text`, `assert_element` | `02-ocarina/04-invariants/02-assertions.md` |
| `otherwise`, `any_of` | `02-ocarina/04-invariants/03-otherwise-any-of.md` |
| `then`, `chain_of_validations`, `chain_validations` | `02-ocarina/04-invariants/04-then-chain-of-validations.md` |
| business validator, framework validator | `02-ocarina/04-invariants/05-business-vs-framework-validator.md` |
| `InvariantViolationError`, `AggregateInvariantViolationError` | `02-ocarina/04-invariants/06-invariant-errors.md` |

### Framework core — Orchestration (`02-ocarina/05-orchestration/`)

| Symbol | Article |
| --- | --- |
| `Test[Driver]`, `TestRunner`, `TestScenario`, `TestScenarioFragment`, `spawn`, `skipped`, `pre_test_scenarios_fragments`, `post_test_scenarios_fragments`, `create_selenium_test` | `02-ocarina/05-orchestration/01-test.md` |
| `TestExecutor`, `ExecutionOutcome`, `_run_chain`, `_run_teardown`, `_start_watchers`, `autoscreen_on_fail` | `02-ocarina/05-orchestration/02-test-executor.md` |
| `TestFlow`, retry, backoff, `max_retries`, `logger.cleanup`, 9 lives | `02-ocarina/05-orchestration/03-test-flow-retries.md` |
| `TestSuite`, `max_workers`, `ThreadPoolExecutor`, warmup, `WarmupTimeoutError`, `_campaign_name`, `_cycle_name` | `02-ocarina/05-orchestration/04-test-suite.md` |
| `saturate_workers`, saturation, `[COPY N]`, `copy_indicator`, `_prepare_tests_for_saturated_threading` | `02-ocarina/05-orchestration/05-saturation.md` |
| `TestCampaign`, `campaign_has_failed`, `skip_all`, `run_all` | `02-ocarina/05-orchestration/06-test-campaign.md` |
| `TestCycle`, `has_test_cycle_failed`, `fail-fast-on-first-smoke-campaigns-sequence-fail`, `wait-for-all-smoke-tests`, smoke campaigns, main campaigns | `02-ocarina/05-orchestration/07-test-cycle-modes.md` |
| `filter_tests_by_ids`, `--only`, `--exclude`, `only_ids`, `exclude_ids` | `02-ocarina/05-orchestration/08-filter-tests-by-ids.md` |

### Framework core — Other (`02-ocarina/`)

| Symbol | Article |
| --- | --- |
| `Scenario`, `test_chain`, `setup`, `teardown`, `watchers` | `02-ocarina/06-scenario.md` |
| `Watcher[Driver]`, `watcher.start`, `watcher.stop` | `02-ocarina/07-watcher.md` |
| `POMBase` | `02-ocarina/08-pom-base.md` |
| `ILogger`, `ITakeScreenshot`, `set_domain_taxonomy`, `set_prefix` | `02-ocarina/09-ports.md` |
| `DriversPool`, `WebDriversPool`, `pool.acquire`, `pool.warmup`, `pool.shutdown` | `02-ocarina/10-infra/01-drivers-pool.md` |
| `DriverBuilder` | `02-ocarina/10-infra/02-driver-builder.md` |
| `Screenshotter` | `02-ocarina/10-infra/03-screenshotter.md` |
| `ActCounter`, `ThreadsBasedActCounter` | `02-ocarina/10-infra/04-act-counter.md` |
| Selenium adapters, typed wrappers | `02-ocarina/10-infra/05-selenium-adapters.md` |
| `PlaywrightDriver`, `create_playwright_driver`, `create_playwright_drivers_pool`, `create_playwright_screenshotter`, `submit` (owner thread), `_OwnerThread`, `call_timeout`, `is_dead`/`is_closed`, `DriverDiedError`, `PlaywrightTitleMixin`, `playwright_driver_healthcheck` | `02-ocarina/10-infra/06-playwright-actor.md` |
| `CLIBuilder` | `02-ocarina/11-opinionated/01-cli-builder.md` |
| phantom parameters, store parameters | `02-ocarina/11-opinionated/02-cli-store-phantoms.md` |
| `SeleniumCLI`, `--only`, `--exclude` (CLI side), `_create_validate_only_exclude_mutex_effect` | `02-ocarina/11-opinionated/03-selenium-cli.md` |
| `FileLogger`, `PrintLogger`, `ConsoleLogger` | `02-ocarina/11-opinionated/04-loggers.md` |
| Allure reporter, JSON reporter, plugin | `02-ocarina/11-opinionated/05-plugins-reports.md` |
| `bootstrap` | `02-ocarina/11-opinionated/06-bootstrap-launcher.md` |
| `TestName`, `TestId`, `PageUrl`, `TestResult`, `TestSuiteResult`, `TestCampaignResults`, `TestCycleResults` | `02-ocarina/12-custom-types-errors.md` |
| module tree | `02-ocarina/02-module-tree.md` |
| identity, version, dependencies, `mypy --strict` | `02-ocarina/01-identity.md` |

### Functional patterns (`03-functional/`)

| Symbol | Article |
| --- | --- |
| `Effect`, `Thunk[T]` | `03-functional/01-effect-thunk-result.md` |
| closures, inversion of control, IoC | `03-functional/02-closures-ioc.md` |
| lazy evaluation, `ChainRunner.run`, lazy prefix | `03-functional/03-lazy-evaluation.md` |
| fold, `functools.reduce` | `03-functional/04-fold-reduce.md` |
| declarative style | `03-functional/05-declarative.md` |
| PEP 695, `type X[T]`, `TypeVar bound` | `03-functional/06-pep-695-generics.md` |
| `TypeGuard`, `@final`, discriminated union, sealed | `03-functional/07-discriminated-unions-typeguards.md` |

### Internal tests (`04-internal-tests/`)

| Symbol | Article |
| --- | --- |
| `FakeDriver`, `RecordingPOM`, `conftest.py` | `04-internal-tests/01-strategy.md` |
| cram, prysk, `.t` files | `04-internal-tests/02-cram-prysk.md` |
| `pytest-mypy-plugins`, `.yml` type tests | `04-internal-tests/04-mypy-plugins-types.md` |
| syrupy, `pretty_print_results`, `results_to_json` | `04-internal-tests/05-syrupy-snapshots.md` |
| hypothesis, property-based | `04-internal-tests/06-hypothesis-properties.md` |
| coverage policy | `04-internal-tests/07-coverage-policy.md` |
| Allure, `allure-history`, GitHub Pages report | `04-internal-tests/08-allure-history.md` |

### Igoristan (`05-igoristan/`)

| Symbol | Article |
| --- | --- |
| `useAuth`, OTP, `Math.random() < 0.9`, MFA | `05-igoristan/03-use-auth.md` |
| `LoginForm`, `ChaoticForm`, `Dropzone`, `RandomLoader` | `05-igoristan/04-key-components.md` |
| wireit, `prebuild`, `build`, `dev`, `lint`, `typecheck` | `05-igoristan/05-wireit.md` |
| Husky, lint-staged, commitlint, commitizen | `05-igoristan/06-husky-commitlint.md` |
| `ci-pr.yml`, `deploy.yml` (Igoristan) | `05-igoristan/07-ci-deploy.md` |
| routes (Igoristan), 10 routes | `05-igoristan/02-routes.md` |
| stack (React, Vike, Vite, Tailwind, Valibot, pnpm) | `05-igoristan/01-stack.md` |

### tests-workers (`06-tests-workers/`)

| Symbol | Article |
| --- | --- |
| `/api/otp`, OTP generation | `06-tests-workers/02-otp-endpoint.md` |
| `/api/otp-history`, Redis SCAN | `06-tests-workers/03-otp-history.md` |
| `/api/corsicadex`, Corsicadex | `06-tests-workers/04-corsicadex.md` |
| `isAuthorized`, `x-api-key`, `apiKey` | `06-tests-workers/05-is-authorized.md` |
| `lib/redis.ts`, Upstash, `@upstash/redis` | `06-tests-workers/06-redis-upstash.md` |
| OTP coordination flow (full diagram) | `06-tests-workers/07-otp-coordination-flow.md` |
| Vercel Edge, `runtime: "edge"`, `otplib` | `06-tests-workers/01-stack-edge.md` |

### ocarina-example (`07-ocarina-example/`)

| Symbol | Article |
| --- | --- |
| adapters, `act` (adapter), `match_page` (adapter), `TestSuite` (adapter), `TestCampaign` (adapter), `EnvGetters` (adapter) | `07-ocarina-example/02-adapters.md` |
| login scenarios, happy path, unhappy path, data-driven | `07-ocarina-example/03-scenarios-login.md` |
| Corsicamon scenarios, `api_key`, `draw`, `add`, `back` | `07-ocarina-example/04-scenarios-corsicamon.md` |
| randomness scenarios, `chaotic_form`, `madness`, `dsed` | `07-ocarina-example/05-scenarios-randomness.md` |
| sacred upload, `upload_files` | `07-ocarina-example/06-scenarios-sacred-upload.md` |
| `HumanizedDriver` | `07-ocarina-example/07-humanized-driver.md` |
| `dogpile.cache.memory`, L1 cache, Redis locks, reserved keys | `07-ocarina-example/08-caches-locks.md` |
| `catch_me_if_you_can`, watcher (example) | `07-ocarina-example/09-watcher-catch-me.md` |
| `EnvGetters[_CredsKeys, _ValuesKeys]`, `Literal` env keys | `07-ocarina-example/10-env-getters.md` |
| `main_ci.yml`, `e2e.yml`, `dev_ci.yml` (example) | `07-ocarina-example/11-ci.md` |
| source tree (ocarina-example) | `07-ocarina-example/01-tree.md` |

### ocarina-with-ai-example (`08-ai-example/`)

| Symbol | Article |
| --- | --- |
| AI manifesto, "Code: 99% Claude" | `08-ai-example/01-ai-manifesto.md` |
| CURA Healthcare, Heroku eco-dyno | `08-ai-example/02-sut-cura.md` |
| `CLAUDE.md` (AI example), `CURA_FRD.md`, `CURA_TEST_STRATEGY.md`, `IDENTIFIED_GAPS.md` | `08-ai-example/03-canonical-documents.md` |
| test strategy (AI), happy/unhappy/edge/business logic vulnerability/exploratory | `08-ai-example/04-test-strategy.md` |
| G-SEC-1, G-SEC-2, G-SEC-3, CSRF, session, rate-limit | `08-ai-example/05-security-gaps.md` |
| G-DATA-1, G-DATA-2, visit_date, duplicates | `08-ai-example/06-data-gaps.md` |
| G-SPEC-1, G-SPEC-2, G-SPEC-3, history order, profile placeholder | `08-ai-example/07-spec-gaps.md` |
| BFCache, B-BROWSER-1, A-ENV-1, A-ENV-2 | `08-ai-example/08-bfcache.md` |
| `ai_proof_ci.yml`, `ai_proof_e2e.yml`, Heroku warm-up, ChromeDriver filter | `08-ai-example/09-ci-matrix.md` |

### Holy Book (`09-holy-book/`)

| Symbol | Article |
| --- | --- |
| VitePress, `@sugarat`, Pagefind | `09-holy-book/01-stack-vitepress.md` |
| i18n, FR/EN/RU, fallback | `09-holy-book/02-i18n.md` |
| skills taxonomy, 40+ skills | `09-holy-book/03-skills/_index.md` |
| `CLAUDE.md` (Holy Book), `CLAUDE.slim.md` | `09-holy-book/04-claude-md.md` |
| PDF generation, Reportlab, `prompts/generate-books/` | `09-holy-book/05-pdf-generation.md` |
| `llms.txt`, `llms-full.txt`, public URLs | `09-holy-book/06-public-resources.md` |

### CI/CD (`10-cicd/`)

| Symbol | Article |
| --- | --- |
| CI matrix (all repos) | `10-cicd/01-matrix.md` |
| `main_ci.yml`, `dev_ci.yml`, `unstable_python_full_build.yml` (ocarina) | `10-cicd/02-ocarina-workflows.md` |
| `main_ci.yml`, `e2e.yml` (ocarina-example) | `10-cicd/03-example-workflows.md` |
| `ai_proof_ci.yml`, `ai_proof_e2e.yml` | `10-cicd/04-ai-workflows.md` |
| `ci-pr.yml`, `deploy.yml` (igoristan) | `10-cicd/05-igoristan-workflows.md` |
| `deploy.yml` (holy-book) | `10-cicd/06-holy-book-workflow.md` |
| Vercel auto-deploy, tests-workers deploy | `10-cicd/07-tests-workers-vercel.md` |

### Glossary and references (`99-references/`)

| Symbol | Article |
| --- | --- |
| Any term definition (ROP, ISTQB, SUT, …) | `99-references/01-glossary.md` |
| Any source file cited in the primer | `99-references/02-file-index.md` |

---

## Step 2 — fetch the article

Use `fetch/SKILL.md` to read the located article. The path is relative to `site/content.en/` in the cloned repo, or fetchable via GitHub raw:

```
https://raw.githubusercontent.com/mojo-molotov/from-ocarina-to-igor/main/site/content.en/{path}
```

Read only the sections that answer the question. The articles are dense.

---

## Step 3 — not found

If the symbol is not in the index:

1. Try `navigate/SKILL.md` with the symbol as the question — it may match a topic keyword.
2. Try `99-references/02-file-index.md` — it indexes source files cited across the primer.
3. Try `99-references/01-glossary.md` — it may define the term.
4. If still not found: the symbol is either not documented in the primer, or it's a post-v1.1.9 addition. Say so explicitly.

Never invent a location. "Not in the index" is a valid answer.
