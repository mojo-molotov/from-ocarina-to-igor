---
title: "Chapitre 02.11 — Couche opinionated/"
description: "La couche opinionated d'Ocarina, entièrement opt-in : CLI, loggers, plugins de rapport et bootstrap, la version clé en main remplaçable du framework."
weight: 11
date: 2026-05-20
tags: ["ocarina"]
sidebar:
  open: true
---

# Chapitre 02.11&nbsp;—&nbsp;Couche `opinionated/`

> Tout ce qui est **opt-in**&nbsp;: un utilisateur sourcilleux peut tout remplacer. CLI, loggers, plugins de rapport, bootstrap, alias `drive_page`. Cette couche est ce qu'on voit en surface&nbsp;; elle n'est pas le cœur, c'est la version «&nbsp;_clé en main_&nbsp;» qu'Ocarina fournit pour qu'un projet typique n'ait pas à réinventer.

## Plan

|  #  | Fichier                                                | Sujet                                                                                                             |
| :-: | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-cli-builder.md`](01-cli-builder.md)               | `CliBuilder`, `CliArg`, `_SilentArgumentParser`.                                                                  |
| 02  | [`02-cli-store-phantoms.md`](02-cli-store-phantoms.md) | `CliStore[TKeys]`, `_CliField[T]`, `phantom_validate`.                                                            |
| 03  | [`03-selenium-cli.md`](03-selenium-cli.md)             | `create_selenium_auto_cli_store` + flags + validation.                                                            |
| 04  | [`04-loggers.md`](04-loggers.md)                       | `ILogger` impl&nbsp;: `PrintLogger`, `FileLogger`, `PrintAndFileLogger`, `MutedLogger`, `create_matching_logger`. |
| 05  | [`05-plugins-reports.md`](05-plugins-reports.md)       | `pretty_print_results`, `results_to_json`, `generate_docx_proof`, `timing`.                                       |
| 06  | [`06-bootstrap-launcher.md`](06-bootstrap-launcher.md) | `bootstrap` + `run_plugins` (parallèle).                                                                          |

## Opt-out/opt-in

| Sans `opinionated/`                            | Avec `opinionated/`                                                    |
| ---------------------------------------------- | ---------------------------------------------------------------------- |
| L'utilisateur doit écrire son CLI from scratch | `create_selenium_auto_cli_store()` lui donne tout                      |
| L'utilisateur doit écrire son logger           | `create_matching_logger("terminal+file")` lui donne tout               |
| L'utilisateur doit écrire ses rapports         | `pretty_print_results`, `generate_json_results`, `generate_docx_proof` |
| L'utilisateur doit écrire son main()           | `bootstrap(test_cycle, run_plugins, post_exec)`                        |

## Alternatives

| Composant                         | Remplaçable par…                                                             |
| --------------------------------- | ---------------------------------------------------------------------------- |
| `CliBuilder` /&nbsp;`CliStore`    | Toute lib argparse-like (click, typer, fire)                                 |
| `PrintLogger` /&nbsp;`FileLogger` | Toute impl d'`ILogger`                                                       |
| `pretty_print_results`            | Toute fonction `(TestCycleResults) -> None`                                  |
| `generate_docx_proof`             | Idem                                                                         |
| `bootstrap`                       | Toute fonction `() -> None` qui appelle `TestCycle.run_all` + post-traite    |
| `drive_page`                      | `chain_actions` direct, ou un alias projet (`drive_section`, `drive_widget`) |
