---
title: "Chapitre 05 — L'Igoristan, le SUT public"
description: "Application web volontairement chaotique, hébergée sur GitHub Pages, empire personnel d'Igor. Sert de SUT à ocarina-example et de terrain de jeu pour démontrer le rejeu, les watchers, les match_page."
weight: 6
date: 2026-05-20
tags: ["igoristan"]
sidebar:
  open: true
---

# Chapitre 05&nbsp;—&nbsp;L'Igoristan, le SUT public

> Application web volontairement chaotique, hébergée sur GitHub Pages, _empire personnel_ d'Igor. Sert de SUT à `ocarina-example` et de terrain de jeu pour démontrer le rejeu, les watchers, les `match_page`.

## Plan

|  #  | Fichier                                            | Sujet                                                                                                    |
| :-: | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 01  | [`01-stack.md`](01-stack.md)                       | Stack React 19 /&nbsp;Vike SSG /&nbsp;Vite 7 /&nbsp;Tailwind 4 /&nbsp;Valibot /&nbsp;wireit /&nbsp;pnpm. |
| 02  | [`02-routes.md`](02-routes.md)                     | Les 10 routes, leur rôle, leur dose de chaos.                                                            |
| 03  | [`03-use-auth.md`](03-use-auth.md)                 | Le faux `useAuth`, MFA OTP, `Math.random() < 0.9`.                                                       |
| 04  | [`04-key-components.md`](04-key-components.md)     | `LoginForm`, `ChaoticForm`, `Dropzone`, `RandomLoader`, etc.                                             |
| 05  | [`05-wireit.md`](05-wireit.md)                     | Pipelines `wireit` (`prebuild`, `build`, `dev`, `lint`, `typecheck`, `ci:format-check`).                 |
| 06  | [`06-husky-commitlint.md`](06-husky-commitlint.md) | Husky + lint-staged + commitlint + commitizen.                                                           |
| 07  | [`07-ci-deploy.md`](07-ci-deploy.md)               | CI/CD&nbsp;: `ci-pr.yml` (3 jobs parallèles) + `deploy.yml` (push main&nbsp;→&nbsp;Pages).               |

## Pourquoi un SUT volontairement chaotique

Le Holy Book mentionne principalement l'Igoristan via le pointeur vers `ocarina-example`. Mais l'intention est claire&nbsp;:&nbsp;un site qui marche tout le temps ne sert à rien pour démontrer un framework de test résilient.

L'Igoristan a été conçu _comme_ un terrain de jeu pour exercer chaque mécanique d'Ocarina&nbsp;:

| Mécanique d'Ocarina        | Page de l'Igoristan correspondante                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `transient_errors` + rejeu | `useAuth` (10% d'échec aléatoire), `corsicamon` (1/5 lève `Error('lol')`), `donkey-sausage-eater-detector` (30% d'erreur) |
| `match_page` /&nbsp;`when` | `donkey-sausage-eater-detector` (Approved vs Disapproved), `madness` (Cors vs ThisIsBastia)                               |
| `Watcher`                  | `chaotic-form` (éléments `.catch-me-if-you-can`)                                                                          |
| Cache + verrous Redis      | `useAuth` OTP (coordination entre workers)                                                                                |
| Upload de fichiers         | `sacred-upload` (Dropzone)                                                                                                |
| API key UI-side            | `corsicamon`                                                                                                              |

## Lectures connexes

- Les scénarios qui exercent ces pages&nbsp;: [`../07-ocarina-example/`](../07-ocarina-example/README.md)
- Le backend qui coordonne OTP et Corsicadex&nbsp;: [`../06-tests-workers/`](../06-tests-workers/README.md)
