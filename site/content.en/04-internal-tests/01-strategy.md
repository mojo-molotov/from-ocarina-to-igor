---
title: "04.01 — From the outside like a user strategy"
description: "The posture documented in the scenario tests' conftest.py. No test cheats by peeking at internals."
weight: 1
date: 2026-05-20
series: ["internal-tests"]
series_order: 1
tags: ["scenarios", "selenium"]
---

# 04.01&nbsp;—&nbsp;"_From the outside like a user_" strategy

> The posture lives in the scenario tests' `conftest.py`. No test cheats by peeking at internals.

## `tests/scenarios/conftest.py`

| Component                                                                           | Role                                                                          |
| ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `FakeDriver` (dataclass)                                                            | Minimal driver: `title`, `disposed`. No Selenium method.                      |
| `make_built_driver()`                                                               | Factory `(FakeDriver, dispose)`, i.e. the signature `WebDriversPool` expects. |
| `make_pool(max_size=2)`                                                             | `WebDriversPool[FakeDriver]` ready to go.                                     |
| `RecordingPOM(POMBase)`                                                             | POM that records its calls and can be configured to raise.                    |
| `acting(pom, step)`                                                                 | Full `ActionSuccess[RecordingPOM]` (failure+success as no-ops).               |
| `scenario_of("ok", "ok2")`                                                          | `TestScenario[FakeDriver]` with N steps.                                      |
| `failing_scenario(step="boom", exc=...)`                                            | 1-step scenario that raises.                                                  |
| `make_test(name, scenario=..., test_id=..., skipped=False)`                         | `Test[FakeDriver]`                                                            |
| `make_suite(name, tests, pool=..., transient_errors=..., max_retries_per_test=...)` | `TestSuite[FakeDriver]`                                                       |
| `make_campaign(name, suites, max_workers=1)`                                        | `TestCampaign[FakeDriver]`                                                    |
| `make_cycle(name="cycle", campaigns=..., smoke=..., mode=...)`                      | `TestCycle[FakeDriver]`                                                       |
| `run_chain(runner)`                                                                 | Helper that executes a `ChainRunner` and returns the `ActionChain`.           |

## `FakeDriver`

```python
@dataclass
class FakeDriver:
    title: str = "fake"
    disposed: bool = False
```

That's **all**.
**Ocarina's core calls no Selenium API.**

Everything that gets called on the driver is called by the **POM** (user code).

The framework itself only:

- Acquires it via `WebDriversPool.acquire()`.
- Hands it to the scenario / to the watchers.
- Disposes of it at the end.

So a `FakeDriver` _with nothing_ is enough to test orchestration.  
That's the **proof by tests** that the framework is agnostic.

## `RecordingPOM`

```python
@dataclass
class RecordingPOM(POMBase):
    calls: list[str] = field(default_factory=list)
    raise_on: set[str] = field(default_factory=set)
    raises_with: dict[str, Exception] = field(default_factory=dict)
    _title: str = "Recording page"

    def verify(self, *, timeout=None) -> "RecordingPOM":
        return self._do("verify")

    def get_current_title(self) -> str:
        return self._title

    def step(self, name: str) -> "RecordingPOM":
        return self._do(name)

    def _do(self, name: str) -> "RecordingPOM":
        self.calls.append(name)
        if name in self.raise_on:
            raise self.raises_with.get(name, RuntimeError(f"{name} failed"))
        return self
```

A _spy_.

- **Records** each call in `self.calls`. Lets you assert _what was called_, in what order.
- **Can raise** on demand: `RecordingPOM(raise_on={"boom"}, raises_with={"boom": ValueError("nope")})`.
- **Returns `self`** on each call (fluent chaining).

```python
def test_short_circuit_after_failure() -> None:
    pom = RecordingPOM(raise_on={"second"})
    runner = drive_page(
        acting(pom, "first"),
        acting(pom, "second"),
        acting(pom, "third"),
    )
    chain = runner.run()
    assert chain.has_failed()
    assert pom.calls == ["first", "second"]    # ✅ "third" never called
```

## `acting(pom, step)`

```python
def acting(pom: RecordingPOM, step: str) -> Any:
    return (
        create_act(pom, lambda p: p.step(step))
        .failure(lambda exc: None)
        .success(lambda: None)
    )
```

→ Complete `ActionSuccess[RecordingPOM]`, no-op handlers. Drop straight into `drive_page(...)`.

## `make_*`

`make_test`, `make_suite`, `make_campaign`, `make_cycle` instantiate the framework _like a user_. All take _sensible defaults_ (`MutedLogger`, `make_pool()`, `max_workers=1`, etc.) so tests don't drown in boilerplate.

We test the API, not the internals.

## No framework mocking

No test uses `unittest.mock`. A handful of `unittest.mock` uses pop up _occasionally_ to _mock time_ or _mock an external call_, but **never to mock a framework class**.

That's the **guarantee** that the tests validate the framework's _real behavior_, not an assumption about it.

## `@allure.*`

```python
@allure.epic("Railway / action chain")
@allure.feature("Action chain")
@allure.tag("act", "error-handling")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("layer", "unit")
@allure.title("A raising action is caught into Fail; the failure handler fires with the exception")
def test_raising_act_is_captured_as_fail() -> None: ...
```

| Decorator                        | Meaning                                                               |
| -------------------------------- | --------------------------------------------------------------------- |
| `@allure.epic`                   | Top-level grouping (Allure)                                           |
| `@allure.feature`                | Sub-level (feature)                                                   |
| `@allure.tag`                    | Free-form tags (act, error-handling, retry, etc.)                     |
| `@allure.severity`               | TRIVIAL, MINOR, NORMAL, CRITICAL, BLOCKER                             |
| `@allure.label("layer", "unit")` | Custom label&nbsp;—&nbsp;distinguishes `unit` / `integration` / `e2e` |
| `@allure.title`                  | Human-readable title, shown in the report                             |

→ [Allure report](https://mojo-molotov.github.io/ocarina/allure-report/) (framework tests)

## `# ruff: noqa: S101`

```python
# ruff: noqa: S101
"""Railway and action-chain behavior."""
```

`S101` forbids `assert` (default, in production code). Unavoidable in tests.  
`# ruff: noqa: S101` disables this rule **for the whole file**.
