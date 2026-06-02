# Ch 07 — ocarina-example

Chapter brief for LLM navigation. Source articles: `site/content.en/07-ocarina-example/`.

## Articles

| File | Description |
| --- | --- |
| `_index.md` | Chapter landing page. Holy Book "First steps" quote naming `ocarina-example` the source of truth. Carries the `main.py` bootstrap snippet and the e2e `TestCycle` composition: mode `wait-for-all-smoke-tests`, 2 smoke campaigns (global + corsicamon) + 4 main campaigns (login, randomness, sacred upload, corsicamon). |
| `01-tree.md` | Full `src/` tree: `pages/`, `lib/`, `api/`, `caches/`, `constants/`, `tests/`. **Contains ASCII diagram.** |
| `02-adapters.md` | The 5 adapters: `act`, `match_page`, `TestSuite`, `TestCampaign`, `EnvGetters` — how to specialize Ocarina for a project. |
| `03-scenarios-login.md` | Dashboard login scenarios: happy path, unhappy path, data-driven (multiple credentials). |
| `04-scenarios-corsicamon.md` | Corsicamon scenarios: `api_key`, `draw`, `add`, `back` — full Corsicamon workflow. |
| `05-scenarios-randomness.md` | Randomness scenarios (4 difficulty levels): `random_error`, `random_loaders`, `dsed`, `madness`, `chaotic_form`, `walkthrough`. |
| `06-scenarios-sacred-upload.md` | Sacred upload scenarios: `upload_files`, `back_to_igoristan` — file upload flow. |
| `07-humanized-driver.md` | `HumanizedDriver`: Selenium proxy simulating human typing speed and interaction patterns. |
| `08-caches-locks.md` | L1 cache (`dogpile.cache.memory`) + reserved cache keys + distributed Redis locks (coordination across parallel test runners). |
| `09-watcher-catch-me.md` | The `catch_me_if_you_can` watcher: monitors the chaotic form for state changes, retries on random failures. |
| `10-env-getters.md` | `EnvGetters[_CredsKeys, _ValuesKeys]`: strictly typed env var access using `Literal` type parameters. |
| `11-ci.md` | CI: `main_ci.yml` + `dev_ci.yml` (lint + typecheck) + `e2e.yml` (Redis service + manual Firefox + geckodriver). |

## Key concepts

- **Adapters pattern**: Ocarina's core types are abstract. `ocarina-example` wraps them with project-specific defaults (browser options, env getters, reporter config). Every new project copies this adapter layer.
- **Scenario families**: login (auth flow), Corsicamon (API-backed game), randomness (4 levels of chaos), sacred upload (file handling). Each family covers happy, unhappy, and edge cases.
- **`HumanizedDriver`**: a `WebDriver` proxy that adds randomized typing delays and mouse movement simulation. Required because Igoristan's `Math.random()` gates can distinguish programmatic from human-like input.
- **Caches and locks**: `dogpile.cache.memory` for L1 caching (session tokens, OTP codes) + distributed Redis locks to prevent concurrent tests from generating multiple OTP codes simultaneously.
- **`EnvGetters`**: typed access to environment variables. Two `Literal` type parameters enumerate the allowed credential keys and value keys — accessing an undefined key is a type error.
- **`catch_me_if_you_can`**: the canonical `Watcher` example. Registers a lazy callback that fires when the chaotic form reaches an observable state. Documents the Watcher pattern in real use.
- **CI**: `e2e.yml` spins up a Redis service container, downloads geckodriver manually, and runs the full e2e campaign against the live Igoristan site.
- **Source of truth** (framing): the Holy Book names `ocarina-example` *the* canonical reference — any "how do I do X" starts with "look at how it's done here". The chapter landing page shows the `main.py` bootstrap and the e2e `TestCycle` composition: mode `wait-for-all-smoke-tests`, 2 smoke campaigns (global + corsicamon) + 4 main campaigns (login, randomness, sacred upload, corsicamon).

## Diagrams

- `01-tree.md` — `ocarina-example` source tree.

## Connections

- Framework being used → Ch 02
- SUT being tested → Ch 05 (Igoristan)
- OTP backend called → Ch 06 (tests-workers)
- CI workflow detail → Ch 10
- AI-written equivalent → Ch 08

## Not covered here

Igoristan's actual route implementation (read Ch 05 or the source). Specific Selenium debugging procedures.

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
