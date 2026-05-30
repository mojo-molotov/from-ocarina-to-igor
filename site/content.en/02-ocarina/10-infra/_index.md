---
title: "Chapter 02.10 — Infrastructure"
description: "Ocarina's infrastructure layer: drivers pool, builders, screenshotter, act counter and the Selenium and Playwright adapters that implement them."
weight: 10
date: 2026-05-20
tags: ["ocarina", "selenium"]
sidebar:
  open: true
---

# Chapter 02.10&nbsp;—&nbsp;Infrastructure

> Everything that touches _external resources_: driver pool, builders, screenshotters, act counter, and the Selenium adapters that implement them. Since `1.1.3`, a parallel `infra/playwright/` ships the same contracts in Playwright flavor&nbsp;—&nbsp;same pool, same builder, same ports.

## Plan

|  #  | File                                                 | Subject                                                                                                                                  |
| :-: | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-drivers-pool.md`](01-drivers-pool.md)           | `WebDriversPool[Driver]`: `Semaphore`, `Queue`, `warmup` with watchdog, `shutdown`.                                                      |
| 02  | [`02-driver-builder.md`](02-driver-builder.md)       | `DriverBuilder[Driver]`: profile and tmp dirs handling.                                                                                  |
| 03  | [`03-screenshotter.md`](03-screenshotter.md)         | `Screenshotter[TDriver]` + `ScreenshotterConfig`: burst, healthcheck, threadsafe.                                                        |
| 04  | [`04-act-counter.md`](04-act-counter.md)             | `ActCounter` + `ThreadsBasedActCounter` (thread-local).                                                                                  |
| 05  | [`05-selenium-adapters.md`](05-selenium-adapters.md) | `create_driver` (Firefox/Chrome/Edge/Safari), `create_drivers_pool`, `create_screenshotter`, `driver_healthcheck`, `SeleniumTitleMixin`. |

## `BuiltWebDriver[Driver]`

```python
type BuiltWebDriver[Driver] = tuple[Driver, Effect]
```

The exchange unit between the builder and the pool: a `(driver, dispose)` tuple. `dispose` is an `Effect` (no argument, no return) that knows how to clean up _that exact_ driver (`driver.quit()` + removal of the tmp profile if needed).

That **dead-simple** signature is the portability guarantee: any tech can produce a `BuiltWebDriver[Driver]` as long as it exposes a `dispose: Effect`. Ocarina proves it ships **two** such backends&nbsp;—&nbsp;Selenium and, since `1.1.3`, Playwright&nbsp;—&nbsp;and nothing stops you adding Puppeteer or a fake driver.

## `WebDriversPool[Driver]`

```
                     ┌────────────────────────┐
                     │   WebDriversPool       │
                     │   (Semaphore, Queue)   │
                     └──────────┬─────────────┘
                                │ create_driver=lambda: ...
                                ▼
                     ┌────────────────────────┐
                     │   DriverBuilder        │
                     │   (profile, tmpdir)    │
                     └──────────┬─────────────┘
                                │ build_driver=lambda profile_path: ...
                                ▼
                     ┌────────────────────────┐
                     │   create_selenium_     │
                     │   driver (per browser  │
                     │   _build_firefox/etc)  │
                     └────────────────────────┘
```

## `atexit.register(pool.shutdown)`

On the adapter side (`infra/selenium/create_drivers_pool.py`):

```python
drivers_pool = WebDriversPool(create_driver=..., max_size=max_size, warmup_timeout=warmup_timeout)
atexit.register(drivers_pool.shutdown)
return drivers_pool
```

The `atexit` registration ensures no zombies, however the program exits.
