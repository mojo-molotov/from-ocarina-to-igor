---
title: "02.05.07 — TestCycle[Driver] + modes"
description: "TestCycle[Driver]: orchestration of smoke then main campaigns, with two failure-handling modes for smoke tests."
weight: 7
date: 2026-05-20
series: ["orchestration"]
series_order: 7
tags: ["ocarina"]
---

# 02.05.07&nbsp;—&nbsp;`TestCycle[Driver]` + modes

> Source file: [`src/ocarina/dsl/testing/oc_test_cycle.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_cycle.py)
>
> **One job**: orchestrate _smoke_ then _main_ campaigns, and apply a smoke-failure-handling mode.

## Two modes

```python
type Mode = Literal[
    "fail-fast-on-first-smoke-campaigns-sequence-fail",
    "wait-for-all-smoke-tests",
]
```

| Mode                                                         | Behavior                                                                         |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `fail-fast-on-first-smoke-campaigns-sequence-fail` (default) | First smoke campaign that fails → **following** ones get _skipped_.              |
| `wait-for-all-smoke-tests`                                   | **Every** smoke campaign runs. If _any_ fails, the _main_ campaigns get skipped. |

| Case                                                              | Mode                                           |
| ----------------------------------------------------------------- | ---------------------------------------------- |
| Dependency-style smoke (e.g. "login" then "dashboard accessible") | `fail-fast` (login dies → dashboard pointless) |
| Parallel smoke (e.g. "homepage" + "API ping")                     | `wait-for-all` (we want to see both)           |

`fail-fast` is the default&nbsp;—&nbsp;it's the common case.

## Code

```python
@final
class TestCycle[Driver]:
    def __init__(
        self,
        *,
        name: str,
        campaigns: Sequence[TestCampaign[Driver]],
        smoke_tests_campaigns: Sequence[TestCampaign[Driver]] | None = None,
        mode: Mode | None = None,
    ) -> None:
        if mode is None:
            mode = "fail-fast-on-first-smoke-campaigns-sequence-fail"

        smoke_campaigns = smoke_tests_campaigns or []
        all_campaigns = [*smoke_campaigns, *campaigns]

        for campaign in all_campaigns:
            for suite in campaign._suites:
                chain_validations(
                    validate_test_cycle_name(cycle_name=name, name="test_cycle"),
                    validate_campaigns_names(campaigns=all_campaigns, name="all campaigns (smoke + deep tests)"),
                    validate_test_suites_names(suites=campaign._suites, name="suites"),
                    validate_test_runners_names(tests=suite._tests, name="tests"),
                ).execute().raise_if_invalid()

        self.name = name
        self._campaigns = campaigns
        self._smoke_campaigns = smoke_campaigns
        self._results: TestCycleResults = {}
        self._mode = mode

        # Inject the cycle name into every suite
        for campaign in self._campaigns:
            for suite in campaign._suites:
                suite._cycle_name = name
        for smoke_campaign in self._smoke_campaigns:
            for suite in smoke_campaign._suites:
                suite._cycle_name = name


    def run_all(self, *, saturate_workers: bool = True) -> TestCycleResults:
        self._results.clear()

        def _run_smoke(*, fail_fast: bool) -> bool:
            failed = False
            for campaign in self._smoke_campaigns:
                results = campaign.run_all(
                    skip_all=failed if fail_fast else False,
                    saturate_workers=saturate_workers,
                )
                self._results[campaign.name] = results
                if campaign_has_failed(results):
                    failed = True
            return failed

        dispatch: dict[Mode, Thunk[bool]] = {
            "fail-fast-on-first-smoke-campaigns-sequence-fail":
                lambda: _run_smoke(fail_fast=True),
            "wait-for-all-smoke-tests":
                lambda: _run_smoke(fail_fast=False),
        }

        skip_all = dispatch[self._mode]()

        for campaign in self._campaigns:
            self._results[campaign.name] = campaign.run_all(
                skip_all=skip_all, saturate_workers=saturate_workers
            )

        return self._results


def has_test_cycle_failed(results: TestCycleResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaigns in results.values()
        for tests in campaigns.values()
        for outcome, _, _ in tests.values()
    )
```

## Construction invariants

```python
chain_validations(
    validate_test_cycle_name(cycle_name=name, name="test_cycle"),
    validate_campaigns_names(campaigns=all_campaigns, name="..."),
    validate_test_suites_names(suites=campaign._suites, name="suites"),
    validate_test_runners_names(tests=suite._tests, name="tests"),
).execute().raise_if_invalid()
```

1. **`name`** is a valid cycle name (cross-OS filename).
2. **Unique + valid names** across all campaigns (smoke + main).
3. **Unique + valid names** across each campaign's suites.
4. **Unique + valid names** across each suite's tests.

Raised _at construction_.  
Name clash or invalid name → the user hears about it immediately.

## Mode selection via dispatch table

```python
dispatch: dict[Mode, Thunk[bool]] = {
    "fail-fast-on-first-smoke-campaigns-sequence-fail":
        lambda: _run_smoke(fail_fast=True),
    "wait-for-all-smoke-tests":
        lambda: _run_smoke(fail_fast=False),
}

skip_all = dispatch[self._mode]()
```

Functional pattern: index a _thunk_ table by the `Literal` value. In theory the checker can verify the table's exhaustiveness against the `Literal` (`Mode = Literal["a", "b"]` → both keys required).

> ⚠️ **Python limitation today**: the Python type checker **doesn't actually enforce** exhaustiveness here (TypeScript would, via `Record<Mode, ...>`). **Accepted limitation**, documented, not a feature to fix. Add a `Literal` member, forget to add it to the dispatch, mypy stays silent. Annoying. Python's `match` has the same non-exhaustive behavior.&nbsp;:'(

## _Full flow_ of a cycle

```
TestCycle.run_all(saturate_workers=True)
       │
       ▼
   dispatch[mode]()                           ▶︎  _run_smoke(fail_fast=<bool>)
       │
       │  for campaign in self._smoke_campaigns :
       │     results = campaign.run_all(skip_all=failed if fail_fast else False, ...)
       │           │
       │           ▼
       │     for each suite :
       │       suite.run(max_workers=...) → dict[test_name -> TestSuiteResult]
       │
       │     self._results[campaign.name] = results
       │     if campaign_has_failed(results) :
       │         failed = True
       │
       └─ return failed   →  skip_all
       │
       ▼
   for campaign in self._campaigns :
       results = campaign.run_all(skip_all=skip_all, ...)
       self._results[campaign.name] = results
       │
       ▼
   return self._results
```

## `has_test_cycle_failed`

```python
def has_test_cycle_failed(results: TestCycleResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaigns in results.values()
        for tests in campaigns.values()
        for outcome, _, _ in tests.values()
    )
```

1. `results.values()`: iterates over `TestCampaignResults` (one per campaign).
2. `campaigns.values()`: iterates over `TestSuiteResults` (one per suite).
3. `tests.values()`: iterates over `TestSuiteResult` (one per test).

Short-circuits on the first `Fail`.

The user's `main.py` calls it from `post_exec`:

```python
def _post_exec(results: TestCycleResults) -> None:
    print()
    pretty_print_results(results, with_colors=True)
    if has_test_cycle_failed(results):
        sys.exit(1)
```

## Why `mode` is optional

The default `"fail-fast-..."` covers 80% of cases.

`ocarina-example` flips to `wait-for-all-smoke-tests`&nbsp;—&nbsp;it has two _independent_ smoke campaigns (`global_smoke_tests` + `corsicamon_smoke`), and we want to see both fail if both fail.

`ocarina-with-ai-example` stays on the default (fail-fast)&nbsp;—&nbsp;single smoke campaign (`prerequisites`).
