---
title: "02.05.03 — TestFlow[Driver] — politique de rejeu"
description: "TestFlow[Driver] : la politique de rejeu d'Ocarina, boucle de retries avec driver propre à chaque tentative et backoff linéaire."
weight: 3
date: 2026-05-20
series: ["orchestration"]
series_order: 3
tags: ["ocarina"]
---

# 02.05.03&nbsp;—&nbsp;`TestFlow[Driver]`&nbsp;—&nbsp;politique de rejeu

> Fichier source&nbsp;: [`src/ocarina/dsl/testing/internals/test_flow.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/internals/test_flow.py)
>
> **Responsabilité unique**&nbsp;: pour un seul `Test`, exécuter la boucle de rejeu, acquérir un driver propre à chaque tentative, et appliquer la politique de backoff.

## Pourquoi un niveau intermédiaire entre `TestSuite` et `TestExecutor`

| Niveau         | Ne sait pas                                          |
| -------------- | ---------------------------------------------------- |
| `TestExecutor` | Le rejeu, la pool de drivers                         |
| **`TestFlow`** | La concurrence inter-tests, l'agrégation suite-level |
| `TestSuite`    | L'exécution d'une tentative, le rejeu                |

C'est une séparation _vraiment stricte_. `TestFlow` est le seul à connaître à la fois la pool et la politique de rejeu&nbsp;: son job est de _combiner_ les deux.

## Code

```python
def run(self, test: Test[Driver]) -> TestSuiteResult:
    max_attempts = 1 + self._max_retries
    setup_failures = 0
    last_steps_count = -1
    last_result = None

    taxonomy = (self._cycle_name, self._campaign_name, self._suite_name, test.name)
    logger_with_taxonomy = self._create_logger().set_domain_taxonomy(taxonomy)
    logger_without_taxonomy = self._create_logger()

    for attempt in range(1, max_attempts + 1):
        self._act_counter.reset()

        with self._drivers_pool.acquire() as driver:
            outcome = self._executor.execute(
                test,
                driver=driver,
                taxonomy=taxonomy,
                logger_with_taxonomy=logger_with_taxonomy,
                logger_without_taxonomy=logger_without_taxonomy,
                attempt=attempt,
                max_attempts=max_attempts,
            )

        if outcome.skipped:
            return None, -1, test.test_id

        if outcome.setup_failed:
            setup_failures += 1

        last_result = outcome.result
        last_steps_count = outcome.steps_count

        if outcome.should_retry and attempt <= max_attempts:
            logger_with_taxonomy.cleanup()
            time.sleep(attempt)
            continue

        break

    if setup_failures >= max_attempts:
        msg = (
            f"{test.name} — Skipped: setup failed on all"
            f" {max_attempts} attempts. Fix the setup before retrying."
        )
        logger_with_taxonomy.warning(msg)
        return None, -1, test.test_id

    self._act_counter.reset()
    return last_result, last_steps_count, test.test_id
```

## Anatomie ligne par ligne

### Calcul du nombre total de tentatives

```python
max_attempts = 1 + self._max_retries
```

`_max_retries` est passé au constructeur (default 8). Donc `max_attempts = 9` par défaut. Le Holy Book y fait référence&nbsp;: «&nbsp;_9 vies comme un chat_ 🐱&nbsp;» dans le chapitre «&nbsp;_Premiers obstacles du monde réel_&nbsp;».

### Construction des deux loggers _une seule fois_

```python
taxonomy = (cycle, campaign, suite, test_name)
logger_with_taxonomy = self._create_logger().set_domain_taxonomy(taxonomy)
logger_without_taxonomy = self._create_logger()
```

Deux loggers, **construits une seule fois** pour toutes les tentatives. C'est le `FileLogger` qui se charge de _réinitialiser_ son fichier à la prochaine tentative (`logger.cleanup()`, voir plus bas).

### Boucle principale

```python
for attempt in range(1, max_attempts + 1):
    self._act_counter.reset()
    with self._drivers_pool.acquire() as driver:
        outcome = self._executor.execute(...)
```

- **`act_counter.reset()`** avant chaque tentative pour ne pas compter les pas de test de l'exécution précédente du test.
- **`with pool.acquire() as driver`**&nbsp;: un driver _frais_ par tentative. Le `with` garantit le dispose à la sortie, même en cas d'exception.
- **`executor.execute(...)`** délègue tout le reste.

### Trois branchements après chaque tentative

```python
if outcome.skipped:
    return None, -1, test.test_id

if outcome.setup_failed:
    setup_failures += 1

last_result = outcome.result
last_steps_count = outcome.steps_count

if outcome.should_retry and attempt < max_attempts:
    logger_with_taxonomy.cleanup()
    time.sleep(attempt)
    continue

break
```

| Cas                                                  | Comportement                                                                                                                  |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `outcome.skipped` (par exemple `Test(skipped=True)`) | Retourne immédiatement `(None, -1, test_id)`. Pas de retry, pas de comptage.                                                  |
| `outcome.setup_failed`                               | Incrémente `setup_failures`&nbsp;; le reste de la logique s'applique (peut quand même retry si `should_retry=True`).          |
| `outcome.should_retry and attempt < max_attempts`    | `logger.cleanup()` (recycle le fichier de log), `time.sleep(attempt)` (backoff linéaire 1s, 2s, 3s, …), `continue` la boucle. |
| sinon                                                | `break`&nbsp;—&nbsp;on a un verdict définitif (Pass ou Fail).                                                                 |

### Backoff linéaire `time.sleep(attempt)`

| Attempt | Sleep avant retry |
| ------- | ----------------- |
| 1       | 1s                |
| 2       | 2s                |
| 3       | 3s                |
| 4       | 4s                |
| 5       | 5s                |
| 6       | 6s                |
| 7       | 7s                |
| 8       | 8s                |
| 9       | 9s                |

Total dans le pire des cas&nbsp;: `1+2+3+4+5+6+7+8+9 = 45s` de sleep cumulé, hors temps réel d'exécution.

Pourquoi **linéaire** plutôt qu'**exponentiel** (`2^attempt`)&nbsp;? Parce que le pire des cas exponentiel ferait `2+4+8+16+32+64+128+256+512 = 1022s` ≈ 17 min de sleep cumulé.

### Cas «&nbsp;_toutes les tentatives de setup ont échoué_&nbsp;»

```python
if setup_failures >= max_attempts:
    msg = (
        f"{test.name} — Skipped: setup failed on all"
        f" {max_attempts} attempts. Fix the setup before retrying."
    )
    logger_with_taxonomy.warning(msg)
    return None, -1, test.test_id
```

Si `setup()` a échoué à **chaque** tentative, le test est **SKIPPED**, pas FAILED. Si le setup ne marche jamais, on ne peut pas conclure que la chaîne est cassée, on conclut juste que **le test n'a pas pu être exécuté**. Un message explicite invite à _corriger le setup_ (action concrète).

C'est un détail qui sépare une _défaillance d'infrastructure_ d'une _défaillance fonctionnelle_.

## `TestSuiteResult`

```python
type TestSuiteResult = tuple[TestResult, _TestStepsCount, TestId]
```

- `TestResult`&nbsp;: `Ok`, `Fail`, ou `None` (skip).
- `_TestStepsCount`&nbsp;: `int`, `-1` si skip /&nbsp;setup_failed-all.
- `TestId`&nbsp;: `str`.

C'est le tuple qui remonte à `TestSuite`, qui l'agrège dans son `dict[str, TestSuiteResult]`.

## Pourquoi `logger.cleanup()` avant le retry

On s'en fout d'avoir des artefacts (fichier de log dédié, ou bruit dans le DOCX) pour de la flakiness&nbsp;: inspecter le terminal pour constater la flakiness suffit. `cleanup` recycle donc le fichier de log courant à chaque retry, plutôt que d'en empiler un de plus pour chaque tentative.

Pour le `PrintLogger`&nbsp;: `cleanup` est un no-op.

## Tableau récapitulatif des paramètres `__init__`

```python
def __init__(
    self,
    *,
    executor: TestExecutor[Driver],
    drivers_pool: WebDriversPool[Driver],
    create_logger: Thunk[ILogger],
    act_counter: ActCounter,
    cycle_name: str,
    campaign_name: str,
    suite_name: str,
    max_retries: int = _DEFAULT_MAX_RETRIES,   # 8
) -> None: ...
```

| Paramètre                                   | Source                                                                                                                                                 | Pourquoi                                     |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------- |
| `executor`                                  | `TestSuite._build_flow()` instancie&nbsp;; lui-même reçoit `create_logger`, `take_screenshot`, `act_counter`, `transient_errors`, `autoscreen_on_fail` | Délégation de l'exécution d'une tentative.   |
| `drivers_pool`                              | Construit côté projet (`create_selenium_drivers_pool`)                                                                                                 | Acquisition de drivers frais.                |
| `create_logger`                             | _Thunk_ qui retourne un nouveau logger                                                                                                                 | Construire deux loggers _une seule fois_.    |
| `act_counter`                               | `ThreadsBasedActCounter()` thread-local                                                                                                                | Compter les `act` exécutés.                  |
| `cycle_name`, `campaign_name`, `suite_name` | Injectés en cascade depuis `TestSuite`                                                                                                                 | Construire la taxonomy pour le `FileLogger`. |
| `max_retries`                               | Défini par projet via `TestSuite(max_retries_per_test=...)`                                                                                            | 8 par défaut&nbsp;; 9 vies.                  |
