# Ch 04 — Internal tests

Chapter brief for LLM navigation. Source articles: `site/content.en/04-internal-tests/`.

## Articles

| File | Description |
| --- | --- |
| `01-strategy.md` | "From the outside like a user" strategy. `conftest.py`: `FakeDriver`, `RecordingPOM`, fixture builders. |
| `02-cram-prysk.md` | Cram tests via `prysk`: `.t` files that test the CLI by running it and diffing stdout. |
| `03-pytest-scenarios.md` | Pytest scenarios applied to the framework itself (pytest + allure + hypothesis). |
| `04-mypy-plugins-types.md` | Static typing tests via `pytest-mypy-plugins` (`.yml` files): assert that specific type expressions pass or fail mypy. |
| `05-syrupy-snapshots.md` | Snapshot tests (`syrupy`) for `pretty_print_results` and `results_to_json` output stability. |
| `06-hypothesis-properties.md` | Property-based testing for invariants: `hypothesis` strategies generating arbitrary inputs to `validate`. |
| `07-coverage-policy.md` | Coverage policy: what is tested, what is deliberately NOT tested, and why. |
| `08-allure-history.md` | Allure report generation + composite action `allure-history` + GitHub Pages deployment. |

## Key concepts

- **Five test families**: cram (CLI), pytest scenarios (integration), mypy-plugins (static types), syrupy snapshots (serialization), hypothesis (property-based).
- **`FakeDriver`**: a `WebDriver` test double that records calls without opening a browser. Core fixture for all framework tests.
- **`RecordingPOM`**: a `POMBase` subclass that captures which methods were called, in what order.
- **`pytest-mypy-plugins`**: tests that assert a type annotation is or isn't accepted by mypy — the only way to test generic bounds and discriminated union exhaustiveness statically.
- **Hypothesis** is used to generate arbitrary combinations of actions and invariant inputs, proving the railway's error-handling is sound under any sequence.
- **Coverage policy**: Ocarina does not chase 100% line coverage. The policy documents which paths are intentionally untested (e.g., driver lifecycle under real network conditions).
- **Allure history**: each CI run uploads a new Allure report to GitHub Pages, maintaining a browsable test history at `https://mojo-molotov.github.io/ocarina/allure-report/`.

## Connections

- The framework being tested → Ch 02
- FP concepts that hypothesis exercises → Ch 03
- CI workflow that runs all test families → Ch 10 (ocarina workflows)

## Not covered here

Step-by-step Selenium debugging, geckodriver troubleshooting. Test results for specific historical runs are in the Allure report, not here.
