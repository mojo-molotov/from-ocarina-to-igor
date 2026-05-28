---
title: "04.07 — Politique de couverture : ce qui est testé, ce qui ne l'est pas, pourquoi"
description: "La politique de couverture d'Ocarina : la couverture par ligne scopée au DSL pur et à l'infra agnostique, le reste testé autrement ou hors scope."
weight: 7
date: 2026-05-20
series: ["tests-internes"]
series_order: 7
---

# 04.07&nbsp;—&nbsp;Politique de couverture&nbsp;: ce qui est testé, ce qui ne l'est pas, pourquoi

> La couverture par ligne est **explicitement scopée** au DSL pur et à l'infra agnostique. Le reste est testé par d'autres moyens (cram, types, snapshots, e2e) ou hors scope (shapes inertes).

## `pyproject.toml#tool.coverage.run`

```toml
[tool.coverage.run]
omit = [
    "*/__init__.py",
    "*/tests/*",
    "*/test_*.py",
    "src/ocarina/custom_errors/*",
    "src/ocarina/custom_types/*",
    "src/ocarina/ports/*",
    "src/ocarina/opinionated/loggers/custom_types/*",
    "src/**/*singleton.py",
    "src/**/consts/**",
    # Selenium adapter layer — exercised only against a real browser.
    "src/ocarina/infra/selenium/*",
    "src/ocarina/dsl/testing/selenium/*",
    "src/ocarina/opinionated/cli/selenium/*",
    "src/ocarina/pom/selenium/muted.py",
    "src/ocarina/opinionated/cli/phantoms.py",
    # Opinionated loggers — only file_logger.py stays in scope.
    "src/ocarina/opinionated/loggers/create_matching_logger.py",
    "src/ocarina/opinionated/loggers/muted_logger.py",
    "src/ocarina/opinionated/loggers/print_logger.py",
    "src/ocarina/opinionated/loggers/print_and_file_logger.py",
    "src/ocarina/opinionated/loggers/utils/*",
    # Traversed by cram tests
    "src/ocarina/opinionated/cli/store.py",
    "src/ocarina/opinionated/cli/builder.py",
]
```

## Catégories

### 1. Exclusions évidentes

| Pattern                    | Justification                                      |
| -------------------------- | -------------------------------------------------- |
| `*/__init__.py`            | Modules vides (Python 3 n'en a souvent pas besoin) |
| `*/tests/*`, `*/test_*.py` | Les tests ne se testent pas eux-mêmes              |

### 2. Types /&nbsp;errors /&nbsp;ports /&nbsp;shapes

| Chemin                                           | Justification                                                           |
| ------------------------------------------------ | ----------------------------------------------------------------------- |
| `src/ocarina/custom_types/*`                     | Juste des `type X = ...` et frozen dataclasses. Pas de logique runtime. |
| `src/ocarina/custom_errors/*`                    | Juste des sous-classes d'Exception. Pas de logique.                     |
| `src/ocarina/ports/*`                            | ABCs et Protocols. Pas de comportement.                                 |
| `src/ocarina/opinionated/loggers/custom_types/*` | id.                                                                     |
| `src/**/consts/**`                               | Constantes (`LOGGERS_CHOICES = (...)`).                                 |
| `src/**/*singleton.py`                           | Wrappers Singleton triviaux.                                            |

### 3. Couche Selenium (e2e seulement)

| Chemin                                   | Justification                                                                                      |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `src/ocarina/infra/selenium/*`           | Code Selenium réel (`Chrome()`, `Firefox()`). Ne s'exécute qu'avec un vrai navigateur.             |
| `src/ocarina/dsl/testing/selenium/*`     | `create_selenium_test`, `create_selenium_watcher` (factory triviales sur `Test` /&nbsp;`Watcher`). |
| `src/ocarina/opinionated/cli/selenium/*` | `create_selenium_*_cli_store` (lit `platform.system`, instancie).                                  |
| `src/ocarina/pom/selenium/muted.py`      | `MutedPOM` utilitaire (presque vide).                                                              |

Ces fichiers sont **couverts** par&nbsp;:

- **`ocarina-example/e2e.yml`** (CI manuelle, Firefox + Redis).
- **`ocarina-with-ai-example/ai_proof_e2e.yml`** (CI manuelle, Chrome + Firefox).

Ce sont les **suites e2e externes** qui prouvent que ces adapters marchent, pas la couverture pytest du framework.

### 4. Loggers opinionated (sauf FileLogger)

| Chemin                                                                                                   | Justification                                                                                                                           |
| -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `print_logger.py`, `muted_logger.py`, `print_and_file_logger.py`, `create_matching_logger.py`, `utils/*` | Variants triviaux (terminal seul, muted, factory dispatch).                                                                             |
| `file_logger.py`                                                                                         | **Reste en scope**&nbsp;—&nbsp;c'est le seul qui a une vraie logique (taxonomy&nbsp;→&nbsp;arborescence de fichiers, cleanup, recycle). |

Le `FileLogger` est testé par `test_loggers_and_reports.py`&nbsp;; les autres sont des variations triviales du `PrintLogger` que les snapshots couvrent.

### 5. CLI traversé par cram

| Chemin                                    | Justification                                                         |
| ----------------------------------------- | --------------------------------------------------------------------- |
| `src/ocarina/opinionated/cli/store.py`    | Testé par cram (les `.t` exercent `set` /&nbsp;`get` /&nbsp;`_Unset`) |
| `src/ocarina/opinionated/cli/builder.py`  | Testé par cram (les `.t` exercent parse + validation + effects)       |
| `src/ocarina/opinionated/cli/phantoms.py` | Testé indirectement (les fields qui l'utilisent passent par cram)     |

## Périmètre retenu

| Module                                                                                         | Pourquoi                                                                                               |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `src/ocarina/railway/*`                                                                        | Cœur ROP                                                                                               |
| `src/ocarina/dsl/invariants/*`                                                                 | DSL invariants&nbsp;—&nbsp;testé par pytest + mypy plugins + hypothesis                                |
| `src/ocarina/dsl/testing/*` (sauf `selenium/`)                                                 | Orchestration&nbsp;—&nbsp;testé dans le dossier "scenarios" des tests unitaires                        |
| `src/ocarina/dsl/testing_with_railway/*`                                                       | DSL ROP&nbsp;—&nbsp;testé par scenarios + mypy plugins                                                 |
| `src/ocarina/infra/drivers_pool.py`, `driver_builder.py`, `screenshotter.py`, `act_counter.py` | Infra agnostique&nbsp;—&nbsp;testée avec `FakeDriver`                                                  |
| `src/ocarina/aggregates/*`                                                                     | TypeGuard helpers                                                                                      |
| `src/ocarina/custom_invariants/*`                                                              | Invariants pré-faits&nbsp;—&nbsp;testés par "scenarios" et traversés par les classes qui les utilisent |
| `src/ocarina/opinionated/dsl/drive_page.py`                                                    | Alias trivial                                                                                          |
| `src/ocarina/opinionated/infra/act_counter.py`                                                 | Thread-local counter                                                                                   |
| `src/ocarina/opinionated/launcher/bootstrap.py`                                                | Bootstrap&nbsp;—&nbsp;testé par `test_test_cycle_and_bootstrap.py`                                     |
| `src/ocarina/opinionated/plugins/reports/*`                                                    | Plugins&nbsp;—&nbsp;testés par `test_loggers_and_reports.py`, `test_docx_tests_proofs.py`, snapshots   |

## Métriques

`--cov-report=html` (HTML) + `--cov-report=xml:coverage.xml` (XML) montrent&nbsp;:

| Type de couverture | Métrique                                               |
| ------------------ | ------------------------------------------------------ |
| Line coverage      | % de lignes exécutées au moins une fois                |
| Branch coverage    | % de branches (if/else) couvertes _dans les deux sens_ |

Le flag `--cov-branch` est activé&nbsp;: Ocarina mesure aussi la couverture par branches, pas juste par lignes (instructions).

## HTML

`make serve-htmlcov` ouvre `htmlcov/index.html` dans le navigateur.

- Vert&nbsp;: couvert.
- Rouge&nbsp;: non couvert.
- Jaune&nbsp;: couvert partiellement (branche manquante).

## Pourquoi ne pas "tout" tester

| Approche naïve                                                                | Politique Ocarina                                                                      |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Tout tester, viser 100% partout                                               | Tester _ce qui compte_, viser un score sain sur ce qui compte                          |
| Couvrir les shapes inertes (`type Result = ...`)&nbsp;→&nbsp;100% trivial     | Exclure →&nbsp;le 100% reflète vraiment le _comportement_ couvert                      |
| Tester les adapters Selenium en CI unit&nbsp;→&nbsp;setup browser à chaque PR | Tester les adapters en CI e2e _manuelle_&nbsp;→&nbsp;CI rapide, CI lourde à la demande |
| Tester les loggers triviaux&nbsp;→&nbsp;boilerplate                           | Tester seulement les loggers à logique réelle                                          |

En plus du coverage fourni par pytest, on prend aussi en considération le fait que l'on utilise d'autre _mécanismes_ pour vérifier la qualité d'Ocarina (cram, e2e, snapshots, types, tests manuels).
