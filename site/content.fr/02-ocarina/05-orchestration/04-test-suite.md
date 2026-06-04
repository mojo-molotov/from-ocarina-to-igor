---
title: "02.05.04 — TestSuite[Driver] — moteur parallélisé"
description: "TestSuite[Driver] : le moteur parallélisé d'Ocarina, exécution concurrente des tests, saturation des workers, filtrage par IDs et invariants pré-exécution."
weight: 4
date: 2026-05-20
series: ["orchestration"]
series_order: 4
tags: ["ocarina", "parallelisation"]
---

# 02.05.04&nbsp;—&nbsp;`TestSuite[Driver]`&nbsp;—&nbsp;moteur parallélisé

> Fichier source&nbsp;: [`src/ocarina/dsl/testing/oc_test_suite.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/oc_test_suite.py)
>
> **Responsabilité unique**&nbsp;: exécuter une séquence de `Test` en parallèle, gérer la _saturation_, le filtrage par IDs, et la validation des invariants pré-exécution.

## Constructeur

```python
def __init__(
    self,
    *,
    name: str,
    tests: Sequence[Test[Driver]],
    create_logger: Thunk[ILogger],
    drivers_pool: WebDriversPool[Driver],
    take_screenshot: ITakeScreenshot[Driver],
    act_counter: ActCounter | None = None,
    transient_errors: tuple[type[Exception], ...] = (),
    copy_indicator: str = "COPY",
    put_space_after_copy_indicator: bool = True,
    max_retries_per_test: int | None = None,
    autoscreen_on_fail: bool = False,
    saturate_workers: bool | None = None,
    only_ids: Iterable[str] = (),
    exclude_ids: Iterable[str] = (),
) -> None:
    self._guards_on_invoke(tests)
    # ... assignations ...
    self._tests = filter_tests_by_ids(
        tests,
        only=only_ids,
        exclude=exclude_ids,
        logger=create_logger().set_prefix(lambda: f"{self.name}: filtering tests..."),
    )
```

| Paramètre                        | Type                          | Rôle                                                                               | Défaut                                                         |
| -------------------------------- | ----------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `name`                           | `str`                         | Nom de la suite (apparaît dans logs & rapports)                                    | &nbsp;—&nbsp;                                                  |
| `tests`                          | `Sequence[Test[Driver]]`      | Liste des tests à exécuter                                                         | &nbsp;—&nbsp;                                                  |
| `create_logger`                  | `Thunk[ILogger]`              | Factory de logger                                                                  | &nbsp;—&nbsp;                                                  |
| `drivers_pool`                   | `WebDriversPool[Driver]`      | Pool partagée                                                                      | &nbsp;—&nbsp;                                                  |
| `take_screenshot`                | `ITakeScreenshot[Driver]`     | Callable `(driver, logger, category) -> None`                                      | &nbsp;—&nbsp;                                                  |
| `act_counter`                    | `ActCounter \| None`          | Si `None`&nbsp;→&nbsp;`ThreadsBasedActCounter()`                                   | `None`                                                         |
| `transient_errors`               | `tuple[type[Exception], ...]` | Exceptions qui déclenchent un retry                                                | `()`                                                           |
| `copy_indicator`                 | `str`                         | Préfixe pour les tests clonés en saturation                                        | `"COPY"`                                                       |
| `put_space_after_copy_indicator` | `bool`                        | `[COPY 1]` (`True`) vs `[COPY1]` (`False`)                                         | `True`                                                         |
| `max_retries_per_test`           | `int \| None`                 | Nombre maximum de retentatives d'un test potentiellement flaky                     | `None`&nbsp;→&nbsp;`_DEFAULT_MAX_RETRIES_PER_TEST` (8)         |
| `autoscreen_on_fail`             | `bool`                        | Capture automatiquement un ou des screenshots (rafale) en cas d'échec              | `False`                                                        |
| `saturate_workers`               | `bool \| None`                | Clonage des tests pour saturer tous les workers si la pool est suffisamment grosse | `None`&nbsp;→&nbsp;cascade&nbsp;: suite > campaign > bootstrap |
| `only_ids`                       | `Iterable[str]`               | Filtre `--only`                                                                    | `()`                                                           |
| `exclude_ids`                    | `Iterable[str]`               | Filtre `--exclude`                                                                 | `()`                                                           |

## Garde-fous

### Au moment du `__init__`

```python
def _guards_on_invoke(self, tests: Sequence[Test[Driver]]) -> None:
    validate_test_runners_ids(tests=tests, name="tests").execute().raise_if_invalid()
```

→ Tous les `test_id` doivent être uniques. Sinon&nbsp;: `AggregateInvariantViolationError`. _Levé dès la construction_, avant la moindre tentative d'exécution. Si l'utilisateur a dupliqué un `test_id` par erreur, il l'apprend immédiatement.

### Avant l'exécution

```python
def _guards_with_mounted_tests(self, tests: Sequence[Test[Driver]]) -> None:
    validate_test_runners_names(tests=tests, name="tests").execute().raise_if_invalid()
```

→ Tous les `name` doivent être uniques + valides comme noms de fichiers (cf. `is_valid_filename`). Depuis `1.1.10`, cette unicité est insensible à la casse (NFC + casefold). Appelé **après saturation** (cf. [`05-saturation.md`](05-saturation.md)), parce que les noms `[COPY 1] foo` viennent d'être introduits.

### `validate_workers_amount`

```python
def run(self, *, max_workers: int, saturate_workers: bool = True) -> TestSuiteResults:
    self._results.clear()
    validate_workers_amount(workers_amount=max_workers, name="max_workers").execute().raise_if_invalid()
    ...
```

→ `max_workers >= 1`. Lève sinon.

## Mode séquentiel vs parallèle

```python
if max_workers == 1:
    self._guards_with_mounted_tests(self._tests)
    for test in self._tests:
        self._results[test.name] = flow.run(test)
else:
    # ... saturation ...
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(flow.run, test): (test.name, test.test_id)
            for test in tests
        }
        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                name, _ = futures.pop(future)
                self._results[name] = future.result()
```

### 1. Mode `max_workers == 1` (séquentiel)

- Pas de `ThreadPoolExecutor`.
- Pas de saturation (inutile&nbsp;: un seul worker).
- Garde-fou de noms tout de suite.
- Tests exécutés un par un, dans l'ordre déclaré.

### 2. Mode `max_workers >= 2` (parallèle)

- **Warm-up du pool** si `saturate_workers=True`&nbsp;:
  ```python
  try:
      self._drivers_pool.warmup()
  except WarmupTimeoutError:
      # … message d'aide + shutdown … re-raise
  ```
- **Saturation** des tests jusqu'à `max_workers` (cf. [`05-saturation.md`](05-saturation.md)).
- **`ThreadPoolExecutor(max_workers=N)`**&nbsp;: N threads de worker.
- **Pattern `wait(futures, FIRST_COMPLETED)`**&nbsp;: libérer la mémoire au plus tôt.

## `while futures`

```python
while futures:
    done, _ = wait(futures, return_when=FIRST_COMPLETED)
    for future in done:
        name, _ = futures.pop(future)
        self._results[name] = future.result()
```

1. **`wait(futures, return_when=FIRST_COMPLETED)`**&nbsp;: bloque jusqu'à ce qu'**au moins un** future se termine. Plus efficient que `as_completed` (qui itère).
2. **`futures.pop(future)`**&nbsp;: on retire de la liste pour que le prochain `wait` ne revoit pas le même future.
3. **`future.result()`**&nbsp;: récupère la valeur de retour (ou lève de nouveau l'exception si elle a été levée dans le thread).
4. **`self._results[name] = ...`**&nbsp;: on _agrège dans un dict_, indexé par nom de test.

## warm-up

`WebDriversPool.warmup()` pré-instancie tous les drivers _avant_ de soumettre les futures.

| Sans warm-up                                                                     | Avec warm-up                                  |
| -------------------------------------------------------------------------------- | --------------------------------------------- |
| Le 1er thread acquiert un driver&nbsp;→&nbsp;délai de cold-start (parfois 5-10s) | Tous les drivers prêts                        |
| Risque de cascade de cold-starts                                                 | Drivers acquis instantanément                 |
| Aucune détection précoce d'un driver qui ne se lance pas                         | `WarmupTimeoutError` levé tôt, message d'aide |

Le warm-up a aussi un **watchdog**&nbsp;: si la progression stagne pendant `warmup_timeout` (5 min par défaut), il lève. Voir [`../10-infra/01-drivers-pool.md`](../10-infra/01-drivers-pool.md)

## `try / except WarmupTimeoutError`

```python
try:
    self._drivers_pool.warmup()
except WarmupTimeoutError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(
        "Warmup stalled: killing the program. Expect it to raise soon."
        " Cleanup will be attempted but some browser processes may survive."
        " Check Activity Monitor / Dock for remaining instances."
    )
    time.sleep(30)
    self._drivers_pool.shutdown()
    time.sleep(5)
    raise
```

- **Message explicite** vers Activity Monitor /&nbsp;Dock&nbsp;: l'utilisateur sait quoi faire.
- **`time.sleep(30)`**&nbsp;: laisse le temps aux drivers en cours d'instanciation de mourir proprement.
- **`shutdown()`** explicite.
- **`time.sleep(5)`**&nbsp;: laisse un délai au shutdown.
- **`raise`**&nbsp;: on propage l'exception, le run échoue proprement.

## `test_names_and_ids`

```python
@property
def test_names_and_ids(self) -> Sequence[tuple[str, TestId]]:
    return [(test.name, test.test_id) for test in self._tests]
```

Utilisé par `TestCampaign.run_all(skip_all=True)`&nbsp;: quand on doit produire un dict de résultats _vides_ (skip global), il faut connaître les noms et IDs sans toucher aux tests.

## Champs `_campaign_name` et `_cycle_name` injectés post-création

```python
self._campaign_name: str = ""
self._cycle_name: str = ""
```

Ces champs sont **injectés après-coup** par `TestCampaign.__init__` et `TestCycle.__init__`&nbsp;:

```python
# TestCampaign.__init__
for suite in self._suites:
    suite._campaign_name = self.name  # noqa: SLF001

# TestCycle.__init__
for campaign in self._campaigns:
    for suite in campaign._suites:
        suite._cycle_name = name
```

C'est ce qui permet la **construction dynamique de la taxonomie**, faite à temps avant le run. Le merge est **bidirectionnel** et **strictement interne** au framework, d'où le fait qu'on accède à des valeurs «&nbsp;_privées_&nbsp;» via `# noqa: SLF001` (Self001). Justement&nbsp;: on **ne veut surtout pas** exposer un setter ou autoriser ça publiquement. C'est un _hack_, mais un hack pertinent qui s'appuie sur la _paresse_ (l'exécution étant retardée, il est possible de faire des branchements "ad hoc" avant de lancer le programme).
