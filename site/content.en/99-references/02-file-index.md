---
title: "99.02 — Index of cited files"
description: "The index of source files cited throughout the compendium, organized by repository, with direct GitHub URLs."
weight: 2
date: 2026-05-20
series: ["references"]
tags: ["references"]
series_order: 2
---

# 99.02&nbsp;—&nbsp;Index of cited files

> Per repo, the source files explicitly cited in the primer. Direct GitHub URLs.

## `mojo-molotov/ocarina`&nbsp;—&nbsp;Framework

### Root

- [`pyproject.toml`](https://github.com/mojo-molotov/ocarina/blob/main/pyproject.toml)
- [`Makefile`](https://github.com/mojo-molotov/ocarina/blob/main/Makefile)
- [`mypy.ini`](https://github.com/mojo-molotov/ocarina/blob/main/mypy.ini)
- [`.pre-commit-config.yaml`](https://github.com/mojo-molotov/ocarina/blob/main/.pre-commit-config.yaml)
- [`categories.json`](https://github.com/mojo-molotov/ocarina/blob/main/categories.json)
- [`README.md`](https://github.com/mojo-molotov/ocarina/blob/main/README.md)

### `src/ocarina/railway/`

- [`result.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/railway/result.py)

### `src/ocarina/custom_types/`

- [`effect.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/effect.py)
- [`thunk.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/thunk.py)
- [`tpom.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/tpom.py)
- [`scenario.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/scenario.py)
- [`test_components.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/test_components.py)
- [`test_runner.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/test_runner.py)
- [`oc_test_layers.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/oc_test_layers.py)

### `src/ocarina/custom_errors/test_framework/`

- [`no_matching_branch.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_errors/test_framework/no_matching_branch.py)
- [`driver_died.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_errors/test_framework/driver_died.py)
- [`pages.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_errors/test_framework/pages.py)

### `src/ocarina/custom_invariants/testing/`

- [`workers.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_invariants/testing/workers.py)
- [`oc_test_runners_ids.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_invariants/testing/oc_test_runners_ids.py)
- [`oc_test_runners_names.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_invariants/testing/oc_test_runners_names.py)
- [`oc_test_suites_names.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_invariants/testing/oc_test_suites_names.py)
- [`oc_test_campaigns_names.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_invariants/testing/oc_test_campaigns_names.py)
- [`oc_test_cycles_names.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_invariants/testing/oc_test_cycles_names.py)

### `src/ocarina/dsl/invariants/`

- [`validate.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/validate.py)
- [`assertions.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/assertions.py)
- [`errors.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/errors.py)
- [`internals/validation_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/internals/validation_chain.py)

### `src/ocarina/dsl/testing/`

- [`oc_test.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test.py)
- [`oc_test_suite.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_suite.py)
- [`oc_test_campaign.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_campaign.py)
- [`oc_test_cycle.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_cycle.py)
- [`watcher.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/watcher.py)
- [`filter_tests_by_ids.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/filter_tests_by_ids.py)
- [`internals/test_executor.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/internals/test_executor.py)
- [`internals/test_flow.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/internals/test_flow.py)
- [`selenium/create_test.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/selenium/create_test.py)
- [`selenium/create_watcher.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/selenium/create_watcher.py)

### `src/ocarina/dsl/testing_with_railway/`

- [`chain_actions.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/chain_actions.py)
- [`match_page.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/match_page.py)
- [`internals/action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/internals/action_chain.py)
- [`constructors/create_act.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/constructors/create_act.py)

### `src/ocarina/aggregates/`

- [`tests_layers.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/aggregates/tests_layers.py)

### `src/ocarina/infra/`

- [`drivers_pool.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/drivers_pool.py)
- [`driver_builder.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/driver_builder.py)
- [`screenshotter.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/screenshotter.py)
- [`act_counter.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/act_counter.py)
- [`selenium/create_driver.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/selenium/create_driver.py)
- [`selenium/create_drivers_pool.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/selenium/create_drivers_pool.py)
- [`selenium/create_screenshotter.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/selenium/create_screenshotter.py)
- [`selenium/driver_healthcheck.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/selenium/driver_healthcheck.py)
- [`selenium/mixins.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/infra/selenium/mixins.py)

### `src/ocarina/ports/`

- [`ilogger.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/ports/ilogger.py)
- [`itake_screenshot.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/ports/itake_screenshot.py)

### `src/ocarina/pom/`

- [`base.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/pom/base.py)

### `src/ocarina/opinionated/`

- [`infra/act_counter.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/infra/act_counter.py)
- [`cli/builder.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/builder.py)
- [`cli/store.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/store.py)
- [`cli/phantoms.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/phantoms.py)
- [`cli/selenium/create_cli_store.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/cli/selenium/create_cli_store.py)
- [`dsl/drive_page.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/dsl/drive_page.py)
- [`launcher/bootstrap.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/launcher/bootstrap.py)
- [`loggers/print_logger.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/loggers/print_logger.py)
- [`loggers/file_logger.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/loggers/file_logger.py)
- [`loggers/utils/format_metadata_str.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/loggers/utils/format_metadata_str.py)
- [`plugins/reports/pretty_print_results.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/plugins/reports/pretty_print_results.py)
- [`plugins/reports/results_to_json.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/plugins/reports/results_to_json.py)
- [`plugins/reports/docx_tests_proofs.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/plugins/reports/docx_tests_proofs.py)
- [`plugins/reports/timing.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/plugins/reports/timing.py)

### Tests

- [`tests/cram/cli_help.t`](https://github.com/mojo-molotov/ocarina/blob/main/tests/cram/cli_help.t)
- [`tests/cram/cli_happy_path.t`](https://github.com/mojo-molotov/ocarina/blob/main/tests/cram/cli_happy_path.t)
- (other `.t`s)
- [`tests/scenarios/conftest.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/conftest.py)
- [`tests/scenarios/test_railway_and_action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_railway_and_action_chain.py)
- (other `test_*.py`)
- [`tests/dsl/invariants/test_types.yml`](https://github.com/mojo-molotov/ocarina/blob/main/tests/dsl/invariants/test_types.yml)
- [`tests/dsl/testing_with_railway/test_types.yml`](https://github.com/mojo-molotov/ocarina/blob/main/tests/dsl/testing_with_railway/test_types.yml)

### Workflows

- [`.github/workflows/main_ci.yml`](https://github.com/mojo-molotov/ocarina/blob/main/.github/workflows/main_ci.yml)
- [`.github/workflows/dev_ci.yml`](https://github.com/mojo-molotov/ocarina/blob/main/.github/workflows/dev_ci.yml)
- [`.github/workflows/unstable_python_full_build.yml`](https://github.com/mojo-molotov/ocarina/blob/main/.github/workflows/unstable_python_full_build.yml)
- [`.github/actions/allure-history/action.yml`](https://github.com/mojo-molotov/ocarina/blob/main/.github/actions/allure-history/action.yml)

## `mojo-molotov/ocarina-example`

### Code

- [`src/main.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/main.py)
- [`src/tests/cycles/e2e.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/tests/cycles/e2e.py)
- [`src/tests/scenarios/dashboard/access/happy_paths.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/tests/scenarios/dashboard/access/happy_paths.py)
- [`src/lib/ext/ocarina/adapters/agnostic/act.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/lib/ext/ocarina/adapters/agnostic/act.py)
- [`src/lib/ext/ocarina/adapters/agnostic/env_getters.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/lib/ext/ocarina/adapters/agnostic/env_getters.py)
- [`src/lib/ext/selenium/humanize/proxy.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/lib/ext/selenium/humanize/proxy.py)
- [`src/lib/ext/selenium/watchers/catch_me_if_you_can_watcher.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/lib/ext/selenium/watchers/catch_me_if_you_can_watcher.py)
- [`src/lib/ext/redis/client.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/lib/ext/redis/client.py)
- [`src/caches/l1.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/caches/l1.py)
- [`src/caches/reserve_free_cache_key.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/caches/reserve_free_cache_key.py)
- [`src/api/retrieve_dashboard_otp_code.py`](https://github.com/mojo-molotov/ocarina-example/blob/main/src/api/retrieve_dashboard_otp_code.py)

### Workflows

- [`.github/workflows/main_ci.yml`](https://github.com/mojo-molotov/ocarina-example/blob/main/.github/workflows/main_ci.yml)
- [`.github/workflows/dev_ci.yml`](https://github.com/mojo-molotov/ocarina-example/blob/main/.github/workflows/dev_ci.yml)
- [`.github/workflows/e2e.yml`](https://github.com/mojo-molotov/ocarina-example/blob/main/.github/workflows/e2e.yml)

## `mojo-molotov/ocarina-with-ai-example`

### Docs

- [`README.md`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/README.md)
- [`CLAUDE.md`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/CLAUDE.md)
- [`CURA_FRD.md`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/CURA_FRD.md)
- [`CURA_TEST_STRATEGY.md`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/CURA_TEST_STRATEGY.md)
- [`IDENTIFIED_GAPS.md`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/IDENTIFIED_GAPS.md)

### Code

- [`src/main.py`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/main.py)
- [`src/tests/cycles/e2e.py`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/tests/cycles/e2e.py)
- [`src/tests/scenarios/_fragments/auth.py`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/tests/scenarios/_fragments/auth.py)
- [`src/tests/scenarios/appointment/past_date_booking.py`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/tests/scenarios/appointment/past_date_booking.py)
- [`src/lib/ext/ocarina/adapters/selenium/test_suite.py`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/lib/ext/ocarina/adapters/selenium/test_suite.py)
- [`src/lib/ext/ocarina/adapters/selenium/create_drivers_pool.py`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/lib/ext/ocarina/adapters/selenium/create_drivers_pool.py)
- [`src/lib/ext/ocarina/adapters/selenium/browser_navigation.py`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/src/lib/ext/ocarina/adapters/selenium/browser_navigation.py)

### Workflows

- [`.github/workflows/ai_proof_ci.yml`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/.github/workflows/ai_proof_ci.yml)
- [`.github/workflows/ai_proof_e2e.yml`](https://github.com/mojo-molotov/ocarina-with-ai-example/blob/main/.github/workflows/ai_proof_e2e.yml)

## `mojo-molotov/igoristan`

### Code

- [`src/config/routes.ts`](https://github.com/mojo-molotov/igoristan/blob/main/src/config/routes.ts)
- [`src/config/brand.ts`](https://github.com/mojo-molotov/igoristan/blob/main/src/config/brand.ts)
- [`src/hooks/useAuth.ts`](https://github.com/mojo-molotov/igoristan/blob/main/src/hooks/useAuth.ts)
- [`src/components/LoginForm.tsx`](https://github.com/mojo-molotov/igoristan/blob/main/src/components/LoginForm.tsx)
- [`src/pages/index/+Page.tsx`](https://github.com/mojo-molotov/igoristan/blob/main/src/pages/index/+Page.tsx)
- [`src/pages/corsicamon/+Page.tsx`](https://github.com/mojo-molotov/igoristan/blob/main/src/pages/corsicamon/+Page.tsx)
- [`src/pages/donkey-sausage-eater-detector/+Page.tsx`](https://github.com/mojo-molotov/igoristan/blob/main/src/pages/donkey-sausage-eater-detector/+Page.tsx)
- [`src/pages/dashboard/+Page.tsx`](https://github.com/mojo-molotov/igoristan/blob/main/src/pages/dashboard/+Page.tsx)
- [`vite.config.ts`](https://github.com/mojo-molotov/igoristan/blob/main/vite.config.ts)
- [`package.json`](https://github.com/mojo-molotov/igoristan/blob/main/package.json)
- [`eslint.config.ts`](https://github.com/mojo-molotov/igoristan/blob/main/eslint.config.ts)

### Workflows

- [`.github/workflows/ci-pr.yml`](https://github.com/mojo-molotov/igoristan/blob/main/.github/workflows/ci-pr.yml)
- [`.github/workflows/deploy.yml`](https://github.com/mojo-molotov/igoristan/blob/main/.github/workflows/deploy.yml)

## `mojo-molotov/tests-workers`

### Code

- [`api/otp.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/otp.ts)
- [`api/otp-history.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/otp-history.ts)
- [`api/corsicadex.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/api/corsicadex.ts)
- [`lib/redis.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/lib/redis.ts)
- [`lib/isAuthorized.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/lib/isAuthorized.ts)
- [`consts/corsicadexData.ts`](https://github.com/mojo-molotov/tests-workers/blob/main/consts/corsicadexData.ts)
- [`package.json`](https://github.com/mojo-molotov/tests-workers/blob/main/package.json)
- [`vercel.json`](https://github.com/mojo-molotov/tests-workers/blob/main/vercel.json)
- [`README.md`](https://github.com/mojo-molotov/tests-workers/blob/main/README.md)

(No GitHub Actions workflow.)

## `mojo-molotov/ocarina-holy-book`

### Docs (EN)

- [`docs/index.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/index.md)
- [`docs/what-is-it.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/what-is-it.md)
- [`docs/first-feedbacks.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/first-feedbacks.md)
- [`docs/setup.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/setup.md)
- [`docs/scenarios-composability.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/scenarios-composability.md)
- [`docs/datasets-smoke-tests-setup-teardown-proxy-api-and-caching.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/datasets-smoke-tests-setup-teardown-proxy-api-and-caching.md)
- [`docs/handling-flakiness.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/handling-flakiness.md)
- [`docs/extensibility.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/extensibility.md)
- [`docs/using-ocarina-with-ai.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/using-ocarina-with-ai.md)

### Configs

- [`docs/.vitepress/config.mts`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/.vitepress/config.mts)
- [`docs/.vitepress/plugins/llm.ts`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/.vitepress/plugins/llm.ts)
- [`docs/.vitepress/plugins/pub.ts`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/.vitepress/plugins/pub.ts)
- [`docs/.vitepress/plugins/skills.ts`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/docs/.vitepress/plugins/skills.ts)
- [`package.json`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/package.json)

### AI

- [`ai/CLAUDE.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/ai/CLAUDE.md)
- [`ai/CLAUDE.slim.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/ai/CLAUDE.slim.md)
- [`ai/skills/README.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/ai/skills/README.md)
- `ai/skills/<name>/SKILL.md` × 40+

### Prompts

- [`prompts/generate-books/prompt.md`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/prompts/generate-books/prompt.md)
- [`prompts/generate-books/script.py`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/prompts/generate-books/script.py)

### Workflows

- [`.github/workflows/deploy.yml`](https://github.com/mojo-molotov/ocarina-holy-book/blob/main/.github/workflows/deploy.yml)
