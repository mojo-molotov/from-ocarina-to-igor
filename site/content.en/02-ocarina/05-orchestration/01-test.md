---
title: "02.05.01 — Test[Driver]"
description: "Ocarina's Test[Driver] class: the base orchestration unit, with spawn, pre and post fragments, and skip handling."
weight: 1
date: 2026-05-20
series: ["orchestration"]
series_order: 1
tags: ["ocarina", "scenarios", "selenium"]
---

# 02.05.01&nbsp;—&nbsp;`Test[Driver]`

> Source file: [`src/ocarina/dsl/testing/oc_test.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test.py)

## Signature

```python
@final
class Test[Driver]:
    def __init__(
        self,
        *,
        name: TestName,
        test_id: str | None = None,
        test_scenario: TestScenario[Driver],
        pre_test_scenarios_fragments: Sequence[TestScenarioFragment[Driver]] | None = None,
        post_test_scenarios_fragments: Sequence[TestScenarioFragment[Driver]] | None = None,
        skipped: bool = False,
    ) -> None:
        if test_id is None:
            test_id = name
        self.name = name
        self.test_id = test_id
        self._test_scenario = test_scenario
        self._pre_test_scenarios_fragments = pre_test_scenarios_fragments or []
        self._post_test_scenarios_fragments = post_test_scenarios_fragments or []
        self._skipped = skipped
```

Six parameters:

| Parameter                       | Type                                                                             | Role                                                                                                          |
| ------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `name`                          | `TestName` (`str`)                                                               | Human label; appears in the report, and **becomes the log file name** (hence subject to `is_valid_filename`). |
| `test_id`                       | `str \| None`                                                                    | Stable identifier for `--only` / `--exclude`. If absent: takes `name`.                                        |
| `test_scenario`                 | `TestScenario[Driver]` (alias = `Callable[[Driver, ILogger], Scenario[Driver]]`) | _Factory_ that builds the `Scenario` at execution time.                                                       |
| `pre_test_scenarios_fragments`  | `Sequence[TestScenarioFragment[Driver]] \| None`                                 | `(driver, logger) -> TestChain` functions executed **before** the main scenario.                              |
| `post_test_scenarios_fragments` | `Sequence[TestScenarioFragment[Driver]] \| None`                                 | `(driver, logger) -> TestChain` functions executed **after** the main scenario.                               |
| `skipped`                       | `bool`                                                                           | If `True`, the test is registered but not executed.                                                           |

### 1. `@final`

No user inheritance. Want a "special" test? _Compose_ via fragments or a scenario&nbsp;—&nbsp;don't subclass.

### 2. `*` (keyword-only)

All parameters are keyword-only.

```python
Test(
    name="Login - without OTP",
    test_id="login_no_otp",
    test_scenario=lambda driver, logger: Scenario(test_chain=...),
    pre_test_scenarios_fragments=[],
    skipped=False,
)
```

### 3. `test_id is None → test_id = name`

You always need an ID. But unless you're feeding a system that demands a separate one, the `name` does the job&nbsp;—&nbsp;uniqueness of `name` gets checked either way.

### 4. `pre_test_scenarios_fragments or []`

The `or []` lets you pass `None`. The default is `[]`, not a `tuple`, but it's typed as a `Sequence`. `Sequence` is immutable&nbsp;—&nbsp;strictly better for the type-checker.

### 5. No `_driver` or `_logger`

Runtime dependencies get injected by `spawn`, not `__init__`. That keeps a `Test` a **value**: serializable, mockable, pass it around with zero execution context.

## `spawn(driver, logger) -> TestRunner[Driver]`

```python
def spawn(self, driver: Driver, logger: ILogger) -> TestRunner[Driver]:
    chain_runners: list[ChainRunner[Any]] = []

    for pre_chain in self._pre_test_scenarios_fragments:
        chain_runners.extend(pre_chain(driver, logger))

    scenario = self._test_scenario(driver, logger)
    chain_runners.extend(scenario.test_chain)

    for post_chain in self._post_test_scenarios_fragments:
        chain_runners.extend(post_chain(driver, logger))

    return TestRunner(
        chain_runners=chain_runners,
        skipped=self._skipped,
        setup=scenario.setup,
        teardown=scenario.teardown,
        watchers=scenario.watchers,
    )
```

1. **Pre fragments**: chains get concatenated into `chain_runners`.
2. **Main scenario**: `self._test_scenario(driver, logger)` returns a `Scenario[Driver]`. Its `test_chain` lands here.
3. **Post fragments**: each fragment is called `(driver, logger) -> TestChain`; chains concatenated after.

The result: a `TestRunner` holding _everything_ needed for execution&nbsp;—&nbsp;full chain, `setup`, `teardown`, `watchers`, `skipped` flag.

## The `(driver, logger) -> TestChain` shape for fragments

Same shape as `test_scenario`, but returns a `TestChain` directly, not a `Scenario`. Why the split?

| Difference                                                            | Reason                                                                                                         |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| A fragment **doesn't have its own** `setup` / `teardown` / `watchers` | Fragments are _glue_&nbsp;—&nbsp;they're expected to use the main scenario's `setup` / `teardown` / `watchers` |
| A fragment **is concatenated** rather than **nested**                 | The final chain is `[pre.chain..., scenario.chain..., post.chain...]`, flat                                    |

The AI project's `CLAUDE.md` spells out the pattern:

> Reusable pre/post-conditions live under `src/tests/scenarios/_fragments/`. Wire them via:
>
> - `pre_test_scenarios_fragments=[fragment_fn, ...]`&nbsp;—&nbsp;before the main scenario chain.
> - `post_test_scenarios_fragments=[fragment_fn, ...]`&nbsp;—&nbsp;after.
>
> A fragment has the scenario shape `(driver: WebDriver, logger: ILogger) -> list[ChainRunner]`. The framework concatenates pre + scenario + post into one `ChainRunner` sequence.

Example: `login_as_demo_user`&nbsp;—&nbsp;see [`../../08-ai-example/`](../../08-ai-example/README.md)

## `TestRunner[Driver]`

```python
# src/ocarina/custom_types/test_runner.py
@dataclass(frozen=True)
class TestRunner[Driver]:
    chain_runners: list[ChainRunner[Any]]
    skipped: bool
    setup: Effect | None
    teardown: Effect | None
    watchers: Sequence[Watcher[Driver]] | None
```

Frozen dataclass, immutable, pure data aggregate. This is what `TestExecutor` eats.

## When to use `skipped=True`

The `skipped` flag is an escape hatch:

- For "WIP" tests that shouldn't run but should stay documented.
- For temporarily broken tests (reference the ticket, ideally in the name: `name="[WIP] Some test"`).

`Test.skipped` is read by `TestExecutor.execute`. If `True`, it returns an immediate `ExecutionOutcome(skipped=True)`.

Note: you can also _dynamically skip_ via `--exclude <test_id>` or `--only` (see [`08-filter-tests-by-ids.md`](08-filter-tests-by-ids.md)). Subtle point: untargeted tests are **destroyed**, not "skipped." They don't show up as _skipped_&nbsp;—&nbsp;the test cycle is just **narrowed**.

## The `create_selenium_test` factory

`src/ocarina/dsl/testing/selenium/create_test.py` provides a Selenium-aware factory:

```python
def create_selenium_test(
    *,
    name: TestName,
    test_id: str | None = None,
    test_scenario: TestScenario[WebDriver],
    pre_test_scenarios_fragments: Sequence[TestScenarioFragment[WebDriver]] | None = None,
    post_test_scenarios_fragments: Sequence[TestScenarioFragment[WebDriver]] | None = None,
    skipped: bool = False,
):
    return Test(
        name=name,
        test_id=test_id,
        test_scenario=test_scenario,
        pre_test_scenarios_fragments=pre_test_scenarios_fragments,
        post_test_scenarios_fragments=post_test_scenarios_fragments,
        skipped=skipped,
    )
```

Typed alias `Driver = WebDriver`. Saves call-sites from writing `Test[WebDriver](...)` on every test.
