---
title: "Chapter 05 — Igoristan, the public SUT"
description: "The Igoristan, Ocarina's deliberately chaotic public SUT: a playground to demonstrate retries, watchers and match_page."
weight: 6
date: 2026-05-20
tags: ["igoristan"]
sidebar:
  open: true
---

# Chapter 05&nbsp;—&nbsp;Igoristan, the public SUT

> Deliberately chaotic web app, hosted on GitHub Pages, Igor's _personal empire_. Doubles as `ocarina-example`'s SUT and a playground for replay, watchers, `match_page`.

## Outline

|  #  | File                                               | Topic                                                                                    |
| :-: | -------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 01  | [`01-stack.md`](01-stack.md)                       | Stack React 19 / Vike SSG / Vite 7 / Tailwind 4 / Valibot / wireit / pnpm.               |
| 02  | [`02-routes.md`](02-routes.md)                     | The 10 routes, their role, their dose of chaos.                                          |
| 03  | [`03-use-auth.md`](03-use-auth.md)                 | The fake `useAuth`, MFA OTP, `Math.random() < 0.9`.                                      |
| 04  | [`04-key-components.md`](04-key-components.md)     | `LoginForm`, `ChaoticForm`, `Dropzone`, `RandomLoader`, etc.                             |
| 05  | [`05-wireit.md`](05-wireit.md)                     | `wireit` pipelines (`prebuild`, `build`, `dev`, `lint`, `typecheck`, `ci:format-check`). |
| 06  | [`06-husky-commitlint.md`](06-husky-commitlint.md) | Husky + lint-staged + commitlint + commitizen.                                           |
| 07  | [`07-ci-deploy.md`](07-ci-deploy.md)               | CI/CD: `ci-pr.yml` (3 parallel jobs) + `deploy.yml` (push main → Pages).                 |

## Why a deliberately chaotic SUT

The Holy Book mostly references Igoristan via the pointer to `ocarina-example`. The intent is clear: a site that always works is useless for demoing a resilient test framework.

Igoristan was built _as_ a playground to exercise every Ocarina mechanic:

| Ocarina mechanic            | Matching Igoristan page                                                                                            |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `transient_errors` + replay | `useAuth` (10% random fail), `corsicamon` (1/5 raises `Error('lol')`), `donkey-sausage-eater-detector` (30% error) |
| `match_page` / `when`       | `donkey-sausage-eater-detector` (Approved vs Disapproved), `madness` (Cors vs ThisIsBastia)                        |
| `Watcher`                   | `chaotic-form` (`.catch-me-if-you-can` elements)                                                                   |
| Redis cache + locks         | `useAuth` OTP (worker coordination)                                                                                |
| File upload                 | `sacred-upload` (Dropzone)                                                                                         |
| UI-side API key             | `corsicamon`                                                                                                       |

## Related reading

- The scenarios that exercise these pages: [`../07-ocarina-example/`](../07-ocarina-example/)
- The backend that exposes the OTP and Corsicadex endpoints: [`../06-tests-workers/`](../06-tests-workers/)
