---
title: "Chapitre 02.10 — Infrastructure"
description: "La couche infrastructure d'Ocarina : pool de drivers, builders, screenshotter, compteur d'acts et les adapters Selenium et Playwright qui les implémentent."
weight: 10
date: 2026-05-20
tags: ["ocarina", "selenium"]
sidebar:
  open: true
---

# Chapitre 02.10&nbsp;—&nbsp;Infrastructure

> Tout ce qui touche aux _ressources externes_&nbsp;: pool de drivers, builders, screenshotters, compteur d'acts, et les adapters Selenium qui implémentent ces abstractions. Depuis la `1.1.3`, un `infra/playwright/` parallèle livre les mêmes contrats en saveur Playwright&nbsp;—&nbsp;même pool, même builder, mêmes ports.

## Plan

|  #  | Fichier                                              | Sujet                                                                                                                                    |
| :-: | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-drivers-pool.md`](01-drivers-pool.md)           | `WebDriversPool[Driver]`&nbsp;: `Semaphore`, `Queue`, `warmup` avec watchdog, `shutdown`.                                                |
| 02  | [`02-driver-builder.md`](02-driver-builder.md)       | `DriverBuilder[Driver]`&nbsp;: gestion du profile et tmp dirs.                                                                           |
| 03  | [`03-screenshotter.md`](03-screenshotter.md)         | `Screenshotter[TDriver]` + `ScreenshotterConfig`&nbsp;: burst, healthcheck, threadsafe.                                                  |
| 04  | [`04-act-counter.md`](04-act-counter.md)             | `ActCounter` + `ThreadsBasedActCounter` (thread-local).                                                                                  |
| 05  | [`05-selenium-adapters.md`](05-selenium-adapters.md) | `create_driver` (Firefox/Chrome/Edge/Safari), `create_drivers_pool`, `create_screenshotter`, `driver_healthcheck`, `SeleniumTitleMixin`. |

## `BuiltWebDriver[Driver]`

```python
type BuiltWebDriver[Driver] = tuple[Driver, Effect]
```

C'est l'unité d'échange entre le builder et la pool&nbsp;: un tuple `(driver, dispose)`. Le `dispose` est un `Effect` (sans argument, sans retour) qui sait nettoyer ce driver précisément (`driver.quit()` + suppression du profile tmp si nécessaire).

Cette signature **simple** est la garantie de portabilité&nbsp;: n'importe quelle techno peut produire un `BuiltWebDriver[Driver]` du moment qu'elle expose un `dispose: Effect`. Ocarina le prouve en livrant **deux** backends&nbsp;—&nbsp;Selenium et, depuis la `1.1.3`, Playwright&nbsp;—&nbsp;et rien n'empêche d'ajouter Puppeteer ou un fake driver.

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

Côté adapter (`infra/selenium/create_drivers_pool.py`)&nbsp;:

```python
drivers_pool = WebDriversPool(create_driver=..., max_size=max_size, warmup_timeout=warmup_timeout)
atexit.register(drivers_pool.shutdown)
return drivers_pool
```

L'enregistrement `atexit` garantit qu'il n'y ait pas de zombie quelle que soit la façon dont le programme s'arrête.
