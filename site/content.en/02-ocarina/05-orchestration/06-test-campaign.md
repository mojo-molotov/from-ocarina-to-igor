---
title: "02.05.06 — TestCampaign[Driver]"
description: "TestCampaign[Driver]: ordered execution of a sequence of suites sharing a worker config, with the campaign_has_failed flag."
weight: 6
date: 2026-05-20
series: ["orchestration"]
series_order: 6
tags: ["ocarina", "parallelization"]
---

# 02.05.06&nbsp;—&nbsp;`TestCampaign[Driver]`

> Source file: [`src/ocarina/dsl/testing/oc_test_campaign.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_campaign.py)
>
> **One job**: run a **sequence of suites** in order, share a workers config, and declare `campaign_has_failed`.

## Code

```python
class TestCampaign[Driver]:
    def __init__(
        self,
        *,
        name: str,
        suites: Sequence[TestSuite[Driver]],
        max_workers: int,
        saturate_workers: bool | None = None,
    ) -> None:
        validate_test_suites_names(suites=suites, name="suites").execute().raise_if_invalid()

        self.name = name
        self._suites = suites
        self._results: TestCampaignResults = {}
        self._max_workers = max_workers
        self._saturate_workers = saturate_workers

        for suite in self._suites:
            suite._campaign_name = self.name

    def run_all(
        self, *, skip_all: bool = False, saturate_workers: bool = True
    ) -> TestCampaignResults:
        self._results.clear()

        resolved_saturate_workers = (
            self._saturate_workers
            if self._saturate_workers is not None
            else saturate_workers
        )

        if skip_all:
            for suite in self._suites:
                self._results[suite.name] = {
                    name: (None, -1, test_id)
                    for name, test_id in suite.test_names_and_ids
                }
            return self._results

        for suite in self._suites:
            self._results[suite.name] = suite.run(
                max_workers=self._max_workers,
                saturate_workers=resolved_saturate_workers,
            )

        return self._results


def campaign_has_failed(results: TestCampaignResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaign_results in results.values()
        for outcome, _, _ in campaign_results.values()
    )
```

## Anatomy

### Constructor guard

```python
validate_test_suites_names(suites=suites, name="suites").execute().raise_if_invalid()
```

→ Suite names inside a campaign must be unique — case-insensitively since `1.1.10` (NFC + casefold). Raised _at construction_.

### Inject the campaign name into the suites

```python
for suite in self._suites:
    suite._campaign_name = self.name
```

We poke `suite._campaign_name` directly. Deliberate: _attach_ the campaign name to each suite so `TestFlow` can build the `(cycle, campaign, suite, test_name)` taxonomy later.

### Sequentiality

```python
for suite in self._suites:
    self._results[suite.name] = suite.run(
        max_workers=self._max_workers,
        saturate_workers=resolved_saturate_workers,
    )
```

One suite after the other. Parallelization lives _inside_ a suite, not between suites.  
→ Inter-suite sequentiality is a design invariant, not a limitation.

### `max_workers` is _campaign-level_

`max_workers` is set once for the whole campaign, shared across all its suites. We don't want a "rich" suite hogging more workers than a "poor" one. Projects can still _split_ workloads across multiple campaigns (e.g. a "smoke" campaign with 2 workers, a "load" one with 8).

### `skip_all=True`

```python
self._results[suite.name] = {
    name: (None, -1, test_id)
    for name, test_id in suite.test_names_and_ids
}
```

Every skipped test gets `(None, -1, test_id)`.

1. **`None`** because we **can't say** Ok or Fail. Logical third value for a skip.
2. **`-1`** as step count&nbsp;—&nbsp;clear **sentinel** (standard programming idiom).
3. **`test_id`** preserved for the report.

Invoked by `TestCycle` after a smoke failure: "_skip every main campaign with a SKIPPED status_."

## `campaign_has_failed`

```python
def campaign_has_failed(results: TestCampaignResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaign_results in results.values()
        for outcome, _, _ in campaign_results.values()
    )
```

1. `results.values()` iterates over `TestSuiteResults` (one per suite).
2. `campaign_results.values()` iterates over `TestSuiteResult` (one per test inside the suite).
3. `outcome, _, _` unpacks `(TestResult, steps_count, test_id)`.

`any` short-circuits as soon as a `Fail` is found.

## When does `TestCycle` call `campaign_has_failed`?

```python
def _run_smoke(*, fail_fast: bool) -> bool:
    failed = False
    for campaign in self._smoke_campaigns:
        results = campaign.run_all(skip_all=failed if fail_fast else False, ...)
        self._results[campaign.name] = results
        if campaign_has_failed(results):
            failed = True
    return failed
```

`campaign_has_failed` is used **only** by `TestCycle` to decide what's next (skip the main campaigns).

## Recap

| Aspect                  | `TestCampaign`                                            |
| ----------------------- | --------------------------------------------------------- |
| Inter-suite concurrency | **Sequential**, never parallel                            |
| Intra-suite concurrency | Delegated to `TestSuite` (parallelizes with a ThreadPool) |
| `max_workers`           | A single shared value                                     |
| `saturate_workers`      | Cascade `bootstrap > campaign > suite` (deepest wins)     |
