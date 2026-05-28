---
title: "04.03 — Tests scénarios (pytest + allure)"
description: "Les treize fichiers de tests scénarios d'Ocarina sous pytest et allure, qui couvrent dynamiquement le DSL et l'orchestration."
weight: 3
date: 2026-05-20
series: ["tests-internes"]
series_order: 3
---

# 04.03&nbsp;—&nbsp;Tests scénarios (pytest + allure)

> 13 fichiers `test_*.py` du dossier `tests/scenarios/` couvrent le DSL et l'orchestration. Tests dynamiques.

## Listing

```
tests/scenarios/
├── conftest.py                              # FakeDriver, RecordingPOM, make_*
├── test_railway_and_action_chain.py         # create_act, drive_page, Result, ChainRunner
├── test_match_page.py                       # match_page / when (premières / dernières branches, exceptions)
├── test_validate.py                         # validate, assert_that, otherwise, then, chain_validations
├── test_invariants_properties.py            # hypothesis (cf. 06-hypothesis-properties)
├── test_drivers_pool.py                     # WebDriversPool (acquire, warmup, shutdown, semaphore leaks)
├── test_screenshotter.py                    # Screenshotter (single shot, burst, healthcheck, threadsafety)
├── test_driver_builder.py                   # DriverBuilder (profile tmp dir, dispose)
├── test_watcher.py                          # Watcher (start, stop, callback errors swallowed, dedup cache)
├── test_test_suite.py                       # TestSuite (parallel, saturation, only/exclude, transient_errors)
├── test_test_cycle_and_bootstrap.py         # TestCycle, mode fail-fast vs wait-for-all, bootstrap
├── test_loggers_and_reports.py              # PrintLogger, FileLogger, pretty_print, JSON
├── test_docx_tests_proofs.py                # generate_docx_proof (parse logs, insert images)
└── test_env.py                              # smoke test : versions, Python 3.14+
```

## Exemple de test interne

```python
@allure.epic("Railway / action chain")
@allure.feature("Action chain")
@allure.tag("act", "handlers", "happy-path")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("layer", "unit")
@allure.title("A successful act reports success; the success handler fires once")
def test_success_act_fires_success_handler() -> None:
    pom = RecordingPOM()
    calls = {"success": 0, "failure": 0}

    chain = (
        create_act(pom, lambda p: p.step("click"))
        .failure(lambda _: calls.__setitem__("failure", calls["failure"] + 1))
        .success(lambda: calls.__setitem__("success", calls["success"] + 1))
        .execute()
    )

    assert chain.is_ok()
    assert pom.calls == ["click"]
    assert calls == {"success": 1, "failure": 0}
```

| Assertion                               | Cible                                      |
| --------------------------------------- | ------------------------------------------ |
| `chain.is_ok()`                         | API publique                               |
| `pom.calls == ["click"]`                | comportement observable du POM (recording) |
| `calls == {"success": 1, "failure": 0}` | bon handler appelé                         |

## Annotations Allure

| Catégorie             | Valeurs typiques                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `epic`                | "Railway /&nbsp;action chain", "Invariants", "Orchestration", "Watcher", "Drivers pool", "Reports", "Match page"   |
| `feature`             | "Action chain", "Validate", "TestSuite", "TestCycle", "Bootstrap", "Pretty print", "JSON", "DOCX proofs"           |
| `tag`                 | "act", "handlers", "happy-path", "error-handling", "retry", "transient", "smoke", "skip", "saturation", "parallel" |
| `severity`            | CRITICAL > NORMAL > MINOR > TRIVIAL                                                                                |
| `label("layer", ...)` | "unit", "integration"                                                                                              |

## `test_test_suite.py`

- Tests passent en mode séquentiel (`max_workers=1`).
- Tests passent en mode parallèle (`max_workers=N`).
- Filtrage `--only` /&nbsp;`--exclude`.
- Mutex `--only` + `--exclude`.
- Saturation&nbsp;: tests clonés avec `[COPY N]`.
- Retries sur transient errors.
- Setup failure&nbsp;→&nbsp;SKIPPED si tous les attempts ratent dès le setup.
- Test `skipped=True` s'arrête directement.
- Garde-fous (noms uniques, IDs uniques).
- `take_screenshot` appelé sur fail si `autoscreen_on_fail`.
- Comptage exact des tentatives sur `max_retries` (un test couvre le bord de la boucle).

## `test_match_page.py`

| Cas                                                         | Assertion                                         |
| ----------------------------------------------------------- | ------------------------------------------------- |
| Première branche matche&nbsp;→&nbsp;exécutée                | `chain.is_ok()`, branches suivantes non évaluées  |
| Deuxième branche matche&nbsp;→&nbsp;exécutée                | id.                                               |
| Aucune branche ne matche                                    | `NoMatchingBranchError` dans le `Fail`            |
| Branche matche, mais son `then` fail                        | `Fail` propagé                                    |
| `condition` lève une `Exception` ordinaire                  | Traité comme `False`, branches suivantes essayées |
| `condition` lève une exception du tuple `raised_exceptions` | Re-raise                                          |
| Branche `then=[]` matche                                    | `Ok(None)`                                        |
| `match_page` au milieu d'un `test_chain`                    | Court-circuite si fail                            |

## `test_drivers_pool.py`

Note&nbsp;: utilisation d'un `FakeDriverFactory` qui peut être configuré pour lever /&nbsp;bloquer /&nbsp;dormir, et qui compte ses appels.

- `acquire` avant `warmup`&nbsp;: crée à la demande.
- `acquire` après `warmup`&nbsp;: récupère depuis la queue.
- `warmup` créé exactement `max_size` drivers.
- `acquire` au-delà de `max_size`&nbsp;: bloque jusqu'à release.
- `create_driver` qui lève&nbsp;: release le sémaphore (pas de leak).
- `dispose` qui lève&nbsp;: release quand même (pas de leak).
- `WarmupTimeoutError` quand la progression stagne.
- `shutdown` dispose les drivers en queue, pas les acquis.

## `test_docx_tests_proofs.py`

- Parse un arbre `logs/{campaign}/{suite}/{test}.log` minimal.
- Génère 1 `.docx` par `.log`.
- Insère une image quand le `.log` contient `"Screenshot: <path>"`.
- Convertit `[UTC_DATE::...]` en heure locale.
- Tronque les filenames trop longs.
- Crée un sous-dossier unique sous `output_root`.

Note&nbsp;: ce test produit de vrais `.docx` que `python-docx` valide.

## Conventions

Tous les tests&nbsp;:

- Sont en `snake_case`.
- Commencent par `test_`.
- Ont un nom **descriptif** (`test_success_act_fires_success_handler` plutôt que `test_act_1`).
- Sont annotés Allure (titre lisible, severité, tag).

Cela rend le rapport Allure **navigable comme un livre**&nbsp;: chaque test est un chapitre auto-documenté.

## `pytest --hypothesis-show-statistics`

```
pytest --alluredir=$(ALLURE_RESULTS) -vv --hypothesis-show-statistics
```

`--hypothesis-show-statistics` écrit à la fin du run&nbsp;:

```
=== Hypothesis Statistics ===
- 12 passing examples
- 0 failing examples
- 0 invalid examples
```

Permet de voir combien d'exemples ont été générés par `hypothesis` (cf. [`06-hypothesis-properties.md`](06-hypothesis-properties.md)).
