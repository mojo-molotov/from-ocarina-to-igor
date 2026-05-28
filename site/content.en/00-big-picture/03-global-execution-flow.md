---
title: "00.03 — End-to-end execution flow of an e2e campaign"
description: "The full execution flow of an Ocarina e2e campaign, from CLI parsing to the SUT, through the drivers pool, the cycle and the plugins."
weight: 3
date: 2026-05-20
series: ["big-picture"]
series_order: 3
tags: ["selenium"]
---

# 00.03&nbsp;—&nbsp;End-to-end execution flow of an e2e campaign

Run `python -u src/main.py …` on either suite (`ocarina-example` or `ocarina-with-ai-example`) and this chain kicks off:

```
USER  ────────────────────────────────────────────────────────────────────
       python -u src/main.py --browser firefox --workers 3 [...]
              │
              ▼
       (1) parse CLI
           CliStoreSingleton.push(create_selenium_auto_cli_store())
              │
              ▼
       (2) build pool
           create_selenium_drivers_pool(max_size=N)
              │
              ▼
       (3) warm up external dependencies
           - Redis (ocarina-example)
           - Heroku dyno (ai-example, via curl --retry 6)
              │
              ▼
       (4) bootstrap(
              test_cycle  = create_e2e_test_cycle(drivers_pool),
              run_plugins = lambda results: run_plugins(
                                generate_docx_proof, generate_json_results,
                                exceptions_logger=...),
              post_exec   = pretty_print_results + sys.exit(1) on fail
           )
              │
OCARINA  ─────┼──────────────────────────────────────────────────────────
              │
              ▼
       (5) TestCycle.run_all (saturate_workers=True)
              ├─ smoke_tests_campaigns      [mode: fail-fast | wait-for-all]
              │     └─ TestCampaign.run_all
              │           └─ TestSuite.run (max_workers, saturate_workers)
              │                 └─ ThreadPoolExecutor → TestFlow.run
              │                       └─ pool.acquire() → TestExecutor.execute
              │                             ├─ setup()                  (optional)
              │                             ├─ watchers.start()         (daemon threads)
              │                             ├─ chain_runners            (Railway DSL)
              │                             ├─ watchers.stop()
              │                             └─ teardown()               (always)
              ├─ campaigns (main)
              │  (skipped if a smoke failed)
              │
SUT   ────────┼────────────────────────────────────────────────────────────
              │
              ▼
       Selenium WebDriver ⇄ real browser
       sometimes: OTP HTTP GET + Redis (on the ocarina-example side)
              │
              ▼
       (6) run_plugins(results)
              ├─ generate_docx_proof  (reads the log tree, builds .docx files)
              ├─ generate_json_results (serializes results to .json)
              ├─ others if declared (parallelized via ThreadPoolExecutor)
              │
              ▼
       (6') post_exec(results)
              ├─ pretty_print_results (ANSI, hierarchical)
              └─ has_test_cycle_failed → sys.exit(1) if applicable
```

## Step-by-step

### (1) Parse CLI

`create_selenium_auto_cli_store()` detects the OS via `platform.system()`:

| OS             | Browsers offered              |
| -------------- | ----------------------------- |
| Windows        | `chrome`, `firefox`, `edge`   |
| macOS (Darwin) | `chrome`, `firefox`, `safari` |
| Linux          | `chrome`, `firefox`           |

Every validation (`--driver-path` must point at a file, `--workers ≥ 1`, `--only` / `--exclude` mutex, etc.) goes through `validate(...)`. Ocarina's invariant chain validates Ocarina itself. Detail: [`../02-ocarina/11-opinionated/03-selenium-cli.md`](../02-ocarina/11-opinionated/03-selenium-cli.md)

### (2) Build pool

`create_selenium_drivers_pool(max_size=N)` builds a `WebDriversPool` backed by a `Semaphore(N)` and a `Queue(N)`. See [`../02-ocarina/10-infra/01-drivers-pool.md`](../02-ocarina/10-infra/01-drivers-pool.md)

> Detail: the **`ai-example`** version _overrides_ this construction to build Chrome differently (password manager disabled, leak detection disabled). See [`../08-ai-example/06-data-gaps.md`](../08-ai-example/06-data-gaps.md)

### (3) Warm-up

| Dependency  | Command                                                      | Why                                                                                      |
| ----------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Redis       | `warmup_redis_client()` (`StrictRedis.from_url(...).ping()`) | Cut the cold-start latency, verify that Redis responds                                   |
| Heroku dyno | `curl -sf --retry 6 --retry-delay 5 …`                       | CURA runs on a Heroku eco-dyno that sleeps; Napoleon disapproves of tests on a cold dyno |

### (4) Bootstrap

`bootstrap(test_cycle, run_plugins, post_exec, saturate_workers=True)`:

1. `results = test_cycle.run_all(saturate_workers=saturate_workers)`
2. `run_plugins(results)`
3. `if post_exec: post_exec(results)`

Order is strict: **cycle → plugins → post_exec**. `post_exec` is where you wire `pretty_print_results` + `sys.exit(1)`.

### (5) TestCycle

See [`../02-ocarina/05-orchestration/`](../02-ocarina/05-orchestration/README.md): every level (`Test`, `TestExecutor`, `TestFlow`, `TestSuite`, `TestCampaign`, `TestCycle`) gets its own file.

| Level          | Role                                                                                | Concurrency    |
| -------------- | ----------------------------------------------------------------------------------- | -------------- |
| `Test`         | Test case (`spawn` injects driver + logger)                                         | &nbsp;—&nbsp;  |
| `TestExecutor` | One **attempt** (setup → watchers.start → chain → watchers.stop → teardown)         | &nbsp;—&nbsp;  |
| `TestFlow`     | **Retry** loop (1+max_retries, linear backoff)                                      | &nbsp;—&nbsp;  |
| `TestSuite`    | Parallel suite (ThreadPoolExecutor) + saturation + ID filtering                     | **N threads**  |
| `TestCampaign` | Sequence of suites (sequential between suites, parallel inside)                     | suite-level    |
| `TestCycle`    | Smoke + main; the `mode` (fail-fast \| wait-for-all) applies **only to the smokes** | campaign-level |

### (6) Post-execution plugins

`run_plugins(*plugins, exceptions_logger)`:

- **1 plugin** → run sequentially.
- **N plugins** → run **in parallel** via `ThreadPoolExecutor(max_workers=len(plugins))`.
- If a plugin raises, the exception gets **logged** and the others keep going.
- **Plugins are independent by construction**: no inter-plugin hooks, no coordination.

The two plugins wired up in the demos:

- `generate_docx_proof(logs_root, output_root, logger)`: one `.docx` per test case, screenshots included, UTC dates converted to local time.
- `generate_json_results(results, output_dir, logger)`: a `.json` file containing a minimalistic test report.

**Auto-derived taxonomy**: Ocarina pulls the folder tree straight from what the code declares (Campaign / Suite / Test). Logs and DOCX reports land in folders mirroring that tree automatically. No config to maintain.

See [`../02-ocarina/11-opinionated/05-plugins-reports.md`](../02-ocarina/11-opinionated/05-plugins-reports.md)

## Sequence diagram (OTP authentication)

Textbook case: the "Login with OTP" test in `ocarina-example`. Three actors: the Ocarina suite, the Igoristan SUT, and `tests-workers`.

```
Ocarina suite                      Igoristan (UI)              tests-workers / Upstash Redis
─────────────                      ──────────────              ──────────────────────────────
TestCycle.run_all
    │
    ├─ TestSuite.run (max_workers=N)
    │      │
    │      ├─ ThreadPoolExecutor ⇒ N TestFlow.run parallelized
    │      │       │
    │      │       └─ TestFlow.run(test)
    │      │             │
    │      │             ├─ pool.acquire() → fresh driver
    │      │             │
    │      │             ├─ TestExecutor.execute(driver)
    │      │             │     │
    │      │             │     ├─ setup()  (none here)
    │      │             │     ├─ watchers.start() (none here)
    │      │             │     ├─ chain_runners[0..n].run() :
    │      │             │     │     drive_page : OPEN login page
    │      │             │     │     drive_page : type creds, tick OTP, click "Send"
    │      │             │     │                       │
    │      │             │     │                       └──► fetch /api/otp?_user=u
    │      │             │     │                              │             │
    │      │             │     │                              │             ├─► GET /api/otp?_user=u
    │      │             │     │                              │             │     redis.set otp:<ts>:<uuid> = {event}
    │      │             │     │                              │ ◄─── 200 {otpCode}
    │      │             │     │                       UI displays OTP screen
    │      │             │     │
    │      │             │     │     drive_page : retrieve_dashboard_otp_code()
    │      │             │     │                       │
    │      │             │     │                       └──── HTTP GET /api/otp-history ───┐
    │      │             │     │                                                          │
    │      │             │     │                                                          ▼
    │      │             │     │                                                  SCAN otp:* (batch 100)
    │      │             │     │                      ┌─────────── 200 [events] ──────────┘
    │      │             │     │                      │
    │      │             │     │                      ▼
    │      │             │     │     filter by _user, sort ASC, pick the first match
    │      │             │     │
    │      │             │     │     drive_page : type OTP, confirm
    │      │             │     │                  → AUTHENTICATED_WITH_MFA
    │      │             │     ├─ watchers.stop() (none)
    │      │             │     └─ teardown() (none)
    │      │             │
    │      │             ├─ pool.release() → driver disposed
    │      │             │
    │      │             └─ return (TestResult, steps_count, test_id)
    │      │
    │      └─ wait(futures, FIRST_COMPLETED) — aggregates
    │
    └─ ... next campaigns
```

## `TestFlow.run`&nbsp;—&nbsp;Anatomy of a transient failure

```
attempt = 1
                    ┌─ pool.acquire ─ fresh driver ──┐
attempt 1  ────────►│ TestExecutor.execute(...)      │  → outcome
                    └────────────────────────────────┘
   │
   ├─ outcome.skipped         → return (None, -1, id)
   ├─ outcome.setup_failed    → setup_failures += 1
   ├─ outcome.should_retry &&
   │  attempt < max_attempts  → logger.cleanup(); time.sleep(attempt); continue
   └─ break

   …

attempt N ────────► (same)

   …

if setup_failures >= max_attempts:
    return (None, -1, id)        # ⚠️  test SKIPPED, not FAILED
return (last_result, last_steps_count, id)
```

| Parameter              | Default                                                                                                                                      | Source               |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `max_retries_per_test` | **8** (i.e. 9 attempts total&nbsp;—&nbsp;“_9 lives like a cat_” 🐱)                                                                          | `TestSuite.__init__` |
| `transient_errors`     | `()` at framework level; defined by the user for their project (`WebDriverException`, `ReadTimeoutError`, `HttpErrorPageReachedError`, etc.) | project adapter      |
| Backoff                | `time.sleep(attempt)`&nbsp;—&nbsp;linear 1s, 2s, 3s, …                                                                                       | `TestFlow.run`       |

See [`../02-ocarina/05-orchestration/03-test-flow-retries.md`](../02-ocarina/05-orchestration/03-test-flow-retries.md) for the full detail.
