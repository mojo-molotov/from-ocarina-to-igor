---
title: "02.05.02 — TestExecutor[Driver]"
description: "Fichier source : src/ocarina/dsl/testing/internals/test_executor.py"
weight: 2
date: 2026-05-20
series: ["orchestration"]
series_order: 2
tags: ["ocarina", "watcher"]
---

# 02.05.02&nbsp;—&nbsp;`TestExecutor[Driver]`

> Fichier source&nbsp;: [`src/ocarina/dsl/testing/internals/test_executor.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing/internals/test_executor.py)

> **Responsabilité unique**&nbsp;: exécuter **une seule tentative** d'un test, avec **un seul driver**. Ne connaît ni le rejeu, ni la pool de drivers, ni l'agrégation au niveau suite.

## `ExecutionOutcome`

```python
@final
@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    result: TestResult
    skipped: bool
    setup_failed: bool
    should_retry: bool
    steps_count: int
```

| Champ          | Type                                 | Sens                                                                        |
| -------------- | ------------------------------------ | --------------------------------------------------------------------------- |
| `result`       | `TestResult` = `Result[Any] \| None` | Le résultat de la chaîne (Ok, Fail), ou `None` si skip /&nbsp;setup_failed. |
| `skipped`      | `bool`                               | True si `test_runner.skipped` (i.e. `Test(skipped=True)`).                  |
| `setup_failed` | `bool`                               | True si la fonction `setup()` du scénario a levé.                           |
| `should_retry` | `bool`                               | True si la _règle de rejeu_ s'applique (transient_error détecté).           |
| `steps_count`  | `int`                                | Nombre d'`act` appelés&nbsp;; `-1` si skip ou setup_failed.                 |

- **`slots=True`**&nbsp;: empêche l'ajout dynamique d'attributs et économise mémoire. C'est un objet qui circule en hot-path, le `slots` est justifié.
- **`frozen=True`**&nbsp;: immutable, sûr à partager entre threads.
- **`@final`**&nbsp;: pas d'héritage.

## Ordre d'exécution d'une tentative

```
┌──────────────────────────────────────────────────────────────────────┐
│  test_runner = test.spawn(driver, logger_with_taxonomy)              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  test_runner.skipped ?          │── True ─► return Outcome(skipped=True, ...)
              └────────────────┬────────────────┘
                               │ False
                               ▼
              ┌─────────────────────────────────┐
              │  logger.test_name(test.name)    │   (annotation)
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  setup() (si non-None)          │── leve ─► teardown() (si non-None)
              └────────────────┬────────────────┘            ↓
                               │                  return Outcome(setup_failed=True, should_retry=True, ...)
                               ▼
              ┌─────────────────────────────────┐
              │  watchers.start(driver, logger, │
              │                 take_screenshot)│   (1 daemon thread par watcher)
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  _run_chain(chain_runners, ...) │── retourne (result, should_retry)
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  watchers.stop()                │   (toujours)
              └────────────────┬────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  teardown() (si non-None)       │   (TOUJOURS, même si chain a fail)
              └────────────────┬────────────────┘     (les exceptions sont logguées & avalées)
                               │
                               ▼
              ┌─────────────────────────────────┐
              │  steps_count = act_counter.get()│
              │  return Outcome(...)            │
              └─────────────────────────────────┘
```

## `execute`

```python
def execute(
    self, test: Test[Driver], *,
    driver: Driver,
    taxonomy: tuple[str, ...],
    logger_with_taxonomy: ILogger,
    logger_without_taxonomy: ILogger,
    attempt: int, max_attempts: int,
) -> ExecutionOutcome:
    test_runner = test.spawn(driver, logger_with_taxonomy)

    if test_runner.skipped:
        return ExecutionOutcome(result=None, skipped=True, setup_failed=False,
                                should_retry=False, steps_count=-1)

    logger_without_taxonomy.test_name(test.name)

    if test_runner.setup is not None:
        try:
            test_runner.setup()
        except Exception as exc:
            msg = f"{test.name} -- Setup failed (attempt {attempt}/{max_attempts}): {exc}"
            logger_with_taxonomy.warning(msg)
            if test_runner.teardown is not None:
                self._run_teardown(test_runner.teardown, test_name=test.name, logger=logger_with_taxonomy)
            return ExecutionOutcome(result=None, skipped=False, setup_failed=True,
                                    should_retry=True, steps_count=-1)

    watchers: Sequence[Watcher[Driver]] = test_runner.watchers or []
    self._start_watchers(watchers, driver=driver, test_name=test.name, taxonomy=taxonomy)

    result, should_retry = self._run_chain(
        test_runner.chain_runners, test_name=test.name, attempt=attempt,
        driver=driver, logger=logger_without_taxonomy,
        logger_with_taxonomy=logger_with_taxonomy, max_attempts=max_attempts,
    )

    self._stop_watchers(watchers)

    if test_runner.teardown is not None:
        self._run_teardown(test_runner.teardown, test_name=test.name, logger=logger_with_taxonomy)

    steps_count = self._act_counter.get()
    return ExecutionOutcome(result=result, skipped=False, setup_failed=False,
                            should_retry=should_retry, steps_count=steps_count)
```

## Deux loggers&nbsp;: pourquoi

`logger_with_taxonomy` vs `logger_without_taxonomy`&nbsp;:

| Logger                    | Domain taxonomy                       | Cas d'usage                                                                                                 |
| ------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `logger_with_taxonomy`    | `(cycle, campaign, suite, test_name)` | Logs de la chaîne&nbsp;—&nbsp;écrits dans `<base>/cycle/campaign/suite/test_name.log`                       |
| `logger_without_taxonomy` | _(vide)_                              | Annonces administratives (`test_name(...)`, message de retry)&nbsp;—&nbsp;vont en console /&nbsp;par défaut |

Sans cette distinction, l'annonce de retry «&nbsp;_`Test died! Life: 3/9`_&nbsp;» serait écrite dans le fichier de log du test, qui est précisément le fichier qu'on va recycler à la prochaine tentative. Décorrélation propre.

## `_run_chain`

```python
def _run_chain(
    self, chain_runners: TestChain, *,
    test_name: str, attempt: int, driver: Driver,
    logger: ILogger, logger_with_taxonomy: ILogger, max_attempts: int,
) -> tuple[TestResult, bool]:
    result: TestResult = None

    for chain_runner in chain_runners:
        try:
            chain = chain_runner.run()
        except Exception as exc:
            chain = ActionChain(has_failed=True, result=Fail(error=exc))
        result = chain.result()

        if chain.has_failed():
            if (attempt < max_attempts
                and self._transient_errors
                and is_test_result_fail(result)
                and isinstance(result.error, self._transient_errors)):
                msg = f"{test_name} -- Test died! Life: {attempt}/{max_attempts}"
                logger.warning(msg)
                return result, True              # ◄── should_retry=True

            if self._autoscreen_on_fail and is_test_result_fail(result):
                with suppress(Exception):
                    self._take_screenshot(driver, logger_with_taxonomy, "FAIL")

            return result, False                 # ◄── should_retry=False

    return result, False                         # ◄── tous les chain_runners sont passés
```

| Cas                                                                         | Comportement                                                                                                                      |
| --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Chain `Ok`                                                                  | Continue. À la fin, retourne `(last_result, False)`.                                                                              |
| Chain `Fail` + transient + reste des tentatives                             | Log warning «&nbsp;_Test died! Life: X/Y_&nbsp;», retourne `(result, True)`. **Pas de screenshots automatiques** (on va rejouer). |
| Chain `Fail` + non-transient (ou plus de tentatives) + `autoscreen_on_fail` | Screenshots automatiques, retourne `(result, False)`.                                                                             |
| Chain `Fail` + non-transient (ou plus de tentatives) + pas d'autoscreen     | Retourne `(result, False)`.                                                                                                       |

Subtilité&nbsp;: le `try/except` autour de `chain_runner.run()` attrape les exceptions qui auraient échappé _au-delà_ du DSL ROP (un bug dans un thunk, etc.) et les ré-emballe en `Fail`.

## `_run_teardown`

```python
def _run_teardown(self, teardown: Effect, *, test_name: str, logger: ILogger) -> None:
    try:
        teardown()
    except Exception as exc:
        msg = f"{test_name} -- Teardown failed (ignored): {exc}"
        logger.warning(msg)
```

Le teardown ne **fait jamais échouer** un test. Même s'il lève, on log un warning et on continue. C'est cohérent avec l'isolation&nbsp;: le test a déjà donné son verdict (Pass /&nbsp;Fail)&nbsp;; un teardown défaillant est un problème d'infrastructure à signaler, pas un résultat de test.

## `_start_watchers`

```python
def _start_watchers(self, watchers, *, driver, test_name, taxonomy):
    for index, watcher in enumerate(watchers):
        with suppress(Exception):
            watcher_name = (
                f"[{index + 1}] {test_name} - {watcher.name}"
                if len(watchers) > 1
                else f"{test_name} - {watcher.name}"
            )
            watcher_taxonomy = (*taxonomy[:-1], watcher_name)
            scoped_logger = self._create_logger().set_domain_taxonomy(watcher_taxonomy)
            watcher.start(driver, scoped_logger, self._take_screenshot)
```

1. **Indexation `[1]`, `[2]`** seulement si **plusieurs** watchers. Lisibilité, _et_ pour éviter les collisions de noms de fichiers de logs générés par les watchers.
2. **Taxonomy = `(*taxonomy[:-1], watcher_name)`**&nbsp;: on _remplace_ le dernier élément (le `test_name`) par `<test_name> - <watcher_name>`. Conséquence côté `FileLogger`&nbsp;: un fichier `.log` par watcher, au même niveau que le fichier `.log` du test. Le plugin de génération de rapports DOCX les génère côte-à-côte dans le même dossier.
3. **`with suppress(Exception)`**&nbsp;: un watcher qui rate son `start` ne bloque pas le test. Les watchers sont des _bonus_, pas du critique.

## `_stop_watchers`

```python
def _stop_watchers(self, watchers: Sequence[Watcher[Driver]]) -> None:
    for watcher in watchers:
        with suppress(Exception):
            watcher.stop()
```

Idem&nbsp;: on suppress les erreurs. Un watcher mal écrit ne doit pas faire planter l'orchestration.

## Lien avec le retry et la pool

`TestExecutor` est strictement **stateless** par rapport au rejeu et à la pool. C'est&nbsp;:

- `TestFlow` qui acquiert un driver et qui décide de re-jouer (cf. [`03-test-flow-retries.md`](03-test-flow-retries.md)).
- `TestSuite` qui dispatch avec parallélisation (cf. [`04-test-suite.md`](04-test-suite.md)).

`TestExecutor` est appelé **par tentative**. À chaque tentative, on lui passe `(driver, attempt, max_attempts, ...)`.
