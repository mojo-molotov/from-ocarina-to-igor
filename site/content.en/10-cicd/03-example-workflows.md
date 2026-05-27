---
title: "10.03 — ocarina-example workflows"
description: "See also ../07-ocarina-example/11-ci.md"
weight: 3
date: 2026-05-20
series: ["ci-cd"]
series_order: 3
---

# 10.03&nbsp;—&nbsp;`ocarina-example` workflows

> See also [`../07-ocarina-example/11-ci.md`](../07-ocarina-example/11-ci.md)

## Overview

| Workflow      | Trigger                        | OS                                                                                  | Effect                                                               | Note             |
| ------------- | ------------------------------ | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ---------------- |
| `main_ci.yml` | push/PR main, dispatch         | ubuntu&nbsp;+&nbsp;windows&nbsp;×&nbsp;py&nbsp;3.14                                 | `make check-coding-style` (mypy + ruff).                             | Fast PR gate     |
| `dev_ci.yml`  | push dev, dispatch             | ubuntu&nbsp;×&nbsp;py&nbsp;3.14                                                     | Same                                                                 | For dev branches |
| `e2e.yml`     | `workflow_dispatch` (env `OC`) | ubuntu&nbsp;+&nbsp;Redis service&nbsp;+&nbsp;Firefox&nbsp;+&nbsp;geckodriver 0.35.0 | Full suite run + upload `.screenshots/` `.ocarina_logs/` `.reports/` | Manual only      |

## vs `ocarina/main_ci.yml`

| Aspect                  | `ocarina/main_ci.yml`            | `ocarina-example/main_ci.yml` |
| ----------------------- | -------------------------------- | ----------------------------- |
| **Unit tests**          | Yes (pytest + cram)              | **No**                        |
| **Allure history**      | Yes                              | No                            |
| **GitHub Pages deploy** | Yes (Allure report)              | No                            |
| **OS matrix**           | Yes (ubuntu&nbsp;+&nbsp;windows) | Yes (same)                    |
| **Python matrix**       | Optional (3.14 or 3.14+3.15)     | No (3.14 only)                |

`ocarina` tests itself (unit tests) in CI. `ocarina-example` only runs static checks in CI; its e2e tests are fired on demand via `e2e.yml`.

## The Redis sidecar service

```yaml
services:
  redis:
    image: redis:8.2.5
    ports: [6379:6379]
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

GitHub Actions "spins up" a Redis container _alongside_ the job. Reachable on `localhost:6379`. Healthcheck via `redis-cli ping`.

Tests can then use Redis for distributed locks (`OTP_SEND_LOCK_KEY`) without provisioning an external Redis.

## `environment: OC`

```yaml
e2e:
  runs-on: ubuntu-latest
  environment: OC
```

- Holds the `secrets`: `IGOR_API_KEY`, `DASH_USERNAME`, `DASH_PASSWORD`.
- Can require manual approval before running (useful when consuming quota).

The user dispatching the workflow must have access to the OC environment.

## Artifacts

```yaml
- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: e2e-traces
    path: |
      .screenshots/
      .ocarina_logs/
      .reports/
```

`if: always()`: upload even if the run failed. So you can inspect _why_ it failed.

1. `.screenshots/`: all screenshots.
2. `.ocarina_logs/`: `cycle/campaign/suite/test.log` log tree.
3. `.reports/`: plugin outputs (DOCX + JSON).

## venv cache hashed on pyproject

```yaml
- uses: actions/cache@v5
  with:
    path: .venv
    key: venv-${{ runner.os }}-py-${{ hashFiles('pyproject.toml') }}
```

`hashFiles('pyproject.toml')`: if `pyproject.toml` changes (new dep, bumped version), the cache key changes → cache miss → clean reinstall.

## `Setup Firefox`

```yaml
- name: Setup Firefox
  uses: browser-actions/setup-firefox@<commit-sha>
```

Public action that installs the Firefox version matching the downloaded `geckodriver`.

_Version pinning_ by SHA is used everywhere for all non-official actions (not prefixed with `actions/`) to mitigate Supply Chain Attack risks.
