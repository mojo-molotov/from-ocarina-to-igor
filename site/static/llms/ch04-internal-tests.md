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
- **Playwright actor, two test levels**: `test_playwright_driver_actor.py` mocks `sync_playwright` to exercise the owner-thread marshalling logic in CI with no browser (re-entrancy, `call_timeout`/dead-driver, no thread leak); `test_playwright_adapter.py` is a real-browser smoke (warmup cross-thread, mixin, screenshotter, watcher, trace/video) that auto-skips without Chromium. The Playwright CLI also has its own cram `.t` files (`pw_cli_*.t`, no `--driver-path`, plus `--video-dir`/`--trace-dir`). `infra/playwright/*` is omitted from the coverage metric (like Selenium) but the actor logic is still tested via the mock.
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

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
