---
title: "00.04 — Relations between the six repositories"
weight: 4
date: 2026-05-20
series: ["big-picture"]
series_order: 4
tags: ["otp"]
---

# 00.04&nbsp;—&nbsp;Relations between the six repositories

Every edge of the graph is a _contract_&nbsp;—&nbsp;a secret, a URL, a payload type, or a version. One pair per section below.

## `ocarina` ↔ `ocarina-example`

| Direction                     | Mechanism                         |
| ----------------------------- | --------------------------------- |
| `ocarina` → `ocarina-example` | `pip install ocarina` from PyPI   |
| `ocarina-example` → `ocarina` | None (the example pushes nothing) |

The example **writes its own adapters** on top of the framework:

- `lib/ext/ocarina/adapters/agnostic/act.py` → adds an `on_failure` hook that turns an HTTP error page (title matched by `ERROR_PAGE_REGEX`) into `HttpErrorPageReachedError`.
- `lib/ext/ocarina/adapters/agnostic/match_page.py` → `create_match_page(raised_exceptions=transient_errors)`.
- `lib/ext/ocarina/adapters/agnostic/env_getters.py` → typed `EnvGetters[_CredsKeys, _ValuesKeys]`.
- `lib/ext/ocarina/adapters/selenium/test_suite.py` → pins `max_retries_per_test=8`, `transient_errors=...`, `autoscreen_on_fail=True`, propagates `--only`/`--exclude`.
- `lib/ext/ocarina/adapters/selenium/test_campaign.py` → pins `max_workers=get_max_workers()`.

## `ocarina` ↔ `ocarina-with-ai-example`

- `pip install . ruff mypy mypy-extensions typing-extensions pre-commit`&nbsp;—&nbsp;the AI example pins its dep in `pyproject.toml`: `ocarina>=1.0.3`.
- `act` adapter is **minimal** here. No `on_failure` (CURA doesn't throw deliberately random HTTP error pages). See [`../08-ai-example/`](../08-ai-example/README.md)
- `create_drivers_pool` adapter is **overridden** to build a _clean_ Chrome (password manager off, leak detection off). See [`../08-ai-example/06-data-gaps.md`](../08-ai-example/06-data-gaps.md)

## `ocarina-example` ↔ `igoristan`

| Direction                       | Contract                                      | Detail                                                                     |
| ------------------------------- | --------------------------------------------- | -------------------------------------------------------------------------- |
| `ocarina-example` → `igoristan` | Public URLs                                   | Everything goes through `https://mojo-molotov.github.io/igoristan/<route>` |
| `igoristan` → `ocarina-example` | none (the SUT doesn't know it's being tested) | &nbsp;—&nbsp;                                                              |

`src/constants/pages/`:

```
homepage.py                       → /igoristan/
dashboard.py                      → /igoristan/dashboard
random_loaders.py                 → /igoristan/random-loaders
sacred_upload.py                  → /igoristan/sacred-upload
corsicamon.py                     → /igoristan/corsicamon
chaotic_form.py                   → /igoristan/chaotic-form
madness.py                        → /igoristan/madness
random_error_page.py              → /igoristan/random-error
donkey_sausage_eater_detector.py  → /igoristan/donkey-sausage-eater-detector
```

## `igoristan` ↔ `tests-workers`

| Direction                     | Endpoint                                                                          | Auth                                                                          |
| ----------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `igoristan` → `tests-workers` | `GET https://tests-workers.vercel.app/api/otp?_user=<u>` (header `x-api-key`)     | OTP API key supplied by the user in the UI                                    |
| `igoristan` → `tests-workers` | `GET https://tests-workers.vercel.app/api/corsicadex?id=<n>` (header `x-api-key`) | Corsicadex API key supplied by the user in the UI                             |
| `igoristan` → `tests-workers` | `GET https://tests-workers.vercel.app/api/corsicamon?<...>` (header `x-api-key`)  | Corsicamon API key (read-only, strict third-party service) supplied in the UI |
| `tests-workers` → `igoristan` | None (`tests-workers` doesn't know it's serving the Igoristan)                    | &nbsp;—&nbsp;                                                                 |

- **SUT ↔ tests-workers**: Igoristan _consumes_ the **OTP** (push), **Corsicadex**, and **Corsicamon** (read) endpoints.
- **e2e tests ↔ tests-workers**: `ocarina-example` _only consumes_ **`/api/otp-history`** (read). It **doesn't** use Corsicadex directly, and **doesn't push** OTPs&nbsp;—&nbsp;it just reads the history to fetch the code the SUT generated.

## `ocarina-example` ↔ `tests-workers`

| Direction                           | Endpoint                                                                                   | Auth                                    | Why                                                                              |
| ----------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------- | -------------------------------------------------------------------------------- |
| `ocarina-example` → `tests-workers` | `GET https://tests-workers.vercel.app/api/otp-history` (header `x-api-key: $IGOR_API_KEY`) | `IGOR_API_KEY` ≡ `API_SECRET` on Vercel | Retrieve the OTP history to pick the right one (filter by `_user`, sort by date) |

On the server side (`tests-workers`), a single `API_SECRET` is expected on the `x-api-key` header OR the `?apiKey=` query param. See [`../06-tests-workers/05-is-authorized.md`](../06-tests-workers/05-is-authorized.md)

## `ocarina-with-ai-example` ↔ CURA Healthcare

| Direction           | URL                                        | Detail                                                               |
| ------------------- | ------------------------------------------ | -------------------------------------------------------------------- |
| `ai-example` → CURA | `https://katalon-demo-cura.herokuapp.com/` | Heroku eco-dyno, _falls asleep_; a `warm-up` `curl` precedes the run |
| CURA → `ai-example` | none                                       | &nbsp;—&nbsp;                                                        |

CURA is **not part of the ecosystem repos**. It's an external SUT&nbsp;—&nbsp;an open-source PHP app hosted by Katalon (`katalon-studio/katalon-demo-cura`). A real-world case used as the AI _proof_. The gaps observed (CSRF, etc.) weren't documented up front. They got uncovered **empirically** through the work with Claude. The PHP source can be read after the fact to _explain_ the gaps.

## `ocarina-holy-book` ↔ everything else

| Direction              | Mechanism                                                                            | Detail                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| Holy Book → everything | Internal Markdown links to the other repos (`mojo-molotov/ocarina`, etc.)            | The chapters “First steps”, “First real-world hurdles”, etc. cite them through GitHub links. |
| Everything → Holy Book | Ocarina's `pyproject.toml#Documentation` URL points to the Holy Book                 | `Documentation = "https://mojo-molotov.github.io/ocarina-holy-book"`                         |
| LLMs → Holy Book       | `llms.txt`, `llms-full.txt`, `CLAUDE.md`, `CLAUDE.slim.md` exposed at canonical URLs | See [`../09-holy-book/06-public-resources.md`](../09-holy-book/06-public-resources.md)       |

## Secrets / environment variables

| Variable                             | Producer                                                    | Consumer(s)                                                          | Role                                                                   |
| ------------------------------------ | ----------------------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `IGOR_API_KEY`                       | user (`.env` locally, or the GitHub `OC` environment in CI) | `ocarina-example` (`get_otp_history`, `retrieve_dashboard_otp_code`) | `x-api-key` header sent to `tests-workers`                             |
| `API_SECRET`                         | user (`vercel env add API_SECRET`)                          | `tests-workers` (`isAuthorized.ts`)                                  | Expected key (must be ≡ `IGOR_API_KEY`)                                |
| `UPSTASH_REDIS_REST_URL`             | user (`vercel env add`)                                     | `tests-workers` (`lib/redis.ts`)                                     | Upstash Redis URL                                                      |
| `UPSTASH_REDIS_REST_TOKEN`           | user (`vercel env add`)                                     | `tests-workers` (`lib/redis.ts`)                                     | Upstash Redis token                                                    |
| `DASH_USERNAME` / `DASH_PASSWORD`    | user (`.env`)                                               | `ocarina-example` (`EnvGetters`)                                     | Fake dashboard credentials (default `SacredFigatellu` / `figatellu`)   |
| `REDIS_URL`                          | user (`.env`)                                               | `ocarina-example` (`lib/ext/redis/client.py`)                        | Local Redis URL used for **distributed locks** (distinct from Upstash) |
| `WAIT_TIMEOUT`                       | CI                                                          | `ocarina-with-ai-example` (`ai_proof_e2e.yml`)                       | `--wait-timeout 15`                                                    |
| `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` | CI                                                          | `actions/*`                                                          | Forces Node 24 on JS-based actions                                     |
| `TZ`                                 | CI                                                          | `ocarina-holy-book/deploy.yml` (`Europe/Paris`)                      | Date rendering in the docs / PDFs                                      |

## Secrets diagram

```
   ┌────────────────────────────────────────────────────────────────┐
   │                User (human or CI env)                          │
   └────────┬──────────────────────────────┬────────────────────────┘
            │ IGOR_API_KEY                 │ UPSTASH_REDIS_REST_*
            │                              │ API_SECRET (= IGOR_API_KEY)
            ▼                              ▼
   ┌──────────────────────────┐   ┌──────────────────────────────────┐
   │ ocarina-example/.env     │   │ Vercel project envs              │
   │ (or the "OC" env in CI)  │   │ (tests-workers)                  │
   └────────────┬─────────────┘   └────────────────────┬─────────────┘
                │ x-api-key                            │
                ▼                                      │
   ┌──────────────────────────┐                        │
   │ GET /api/otp-history     │                        │
   └────────────┬─────────────┘                        │
                │                                      │
                │   (from the Igoristan UI)            │
                │   GET /api/otp?_user=u               │
                ▼                                      ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │  tests-workers — isAuthorized.ts                                 │
   │  Compares the x-api-key header (or ?apiKey=) against API_SECRET  │
   └────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │  Upstash Redis (UPSTASH_REDIS_REST_URL + TOKEN)                  │
   └──────────────────────────────────────────────────────────────────┘
```
