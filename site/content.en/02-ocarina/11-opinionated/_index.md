---
title: "Chapter 02.11 — opinionated/ layer"
description: "Ocarina's fully opt-in opinionated layer: CLI, loggers, report plugins and bootstrap, the framework's replaceable turnkey version."
weight: 11
date: 2026-05-20
tags: ["ocarina"]
sidebar:
  open: true
---

# Chapter 02.11&nbsp;—&nbsp;`opinionated/` layer

> Everything that's **opt-in**: a picky user can swap any of it. CLI, loggers, report plugins, bootstrap, `drive_page` alias. This layer is what you see on the surface, not the core&nbsp;—&nbsp;the turnkey version Ocarina ships so a typical project doesn't have to reinvent it.

## Plan

|  #  | File                                                   | Subject                                                                                                                |
| :-: | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-cli-builder.md`](01-cli-builder.md)               | `CliBuilder`, `CliArg`, `_SilentArgumentParser`.                                                                       |
| 02  | [`02-cli-store-phantoms.md`](02-cli-store-phantoms.md) | `CliStore[TKeys]`, `_CliField[T]`, `phantom_validate`.                                                                 |
| 03  | [`03-selenium-cli.md`](03-selenium-cli.md)             | `create_selenium_auto_cli_store` + flags + validation.                                                                 |
| 04  | [`04-loggers.md`](04-loggers.md)                       | `ILogger` implementations: `PrintLogger`, `FileLogger`, `PrintAndFileLogger`, `MutedLogger`, `create_matching_logger`. |
| 05  | [`05-plugins-reports.md`](05-plugins-reports.md)       | `pretty_print_results`, `results_to_json`, `generate_docx_proof`, `timing`.                                            |
| 06  | [`06-bootstrap-launcher.md`](06-bootstrap-launcher.md) | `bootstrap` + `run_plugins` (parallel).                                                                                |

## Opt-out / opt-in

| Without `opinionated/`      | With `opinionated/`                                                    |
| --------------------------- | ---------------------------------------------------------------------- |
| Write your CLI from scratch | `create_selenium_auto_cli_store()` hands it to you                     |
| Write your logger           | `create_matching_logger("terminal+file")` hands it to you              |
| Write your reports          | `pretty_print_results`, `generate_json_results`, `generate_docx_proof` |
| Write your `main()`         | `bootstrap(test_cycle, run_plugins, post_exec)`                        |

## Alternatives

| Component                    | Replaceable by…                                                                |
| ---------------------------- | ------------------------------------------------------------------------------ |
| `CliBuilder` / `CliStore`    | Any argparse-like lib (click, typer, fire)                                     |
| `PrintLogger` / `FileLogger` | Any `ILogger` implementation                                                   |
| `pretty_print_results`       | Any `(TestCycleResults) -> None` function                                      |
| `generate_docx_proof`        | Same                                                                           |
| `bootstrap`                  | Any `() -> None` function that calls `TestCycle.run_all` + post-processes      |
| `drive_page`                 | `chain_actions` directly, or a project alias (`drive_section`, `drive_widget`) |
