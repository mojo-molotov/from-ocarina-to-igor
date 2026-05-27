---
title: "03.03 — Évaluation paresseuse"
description: "Dans Ocarina, rien n'est exécuté tant qu'on ne l'a pas explicitement déclenché. C'est ce qui rend les scénarios composables comme des valeurs."
weight: 3
date: 2026-05-20
series: ["fonctionnel"]
series_order: 3
tags: ["watcher", "scenarios"]
---

# 03.03&nbsp;—&nbsp;Évaluation paresseuse

> Dans Ocarina, **rien n'est exécuté tant qu'on ne l'a pas explicitement déclenché**. C'est ce qui rend les scénarios composables comme des valeurs.

## Zzz

| Endroit                                        | Forme                                                 | Déclencheur                         |
| ---------------------------------------------- | ----------------------------------------------------- | ----------------------------------- |
| `ChainRunner[T]`                               | `Thunk[ActionChain[T]]`                               | `runner.run()`                      |
| `validate(...)`                                | `ValidationStartBlock` /&nbsp;`ValidationAssertBlock` | `.execute()`                        |
| `match_page(...)`                              | retourne un `ChainRunner[Any]`                        | `.run()` (via la chaîne englobante) |
| `Watcher.callback`                             | `Callable[[Watcher], None]`                           | `_loop` quand `start()` est appelé  |
| `logger.set_prefix(thunk)`                     | `Thunk[str]`                                          | recalculé à chaque appel de log     |
| `Scenario.setup` /&nbsp;`teardown`             | `Effect`                                              | appelé par `TestExecutor`           |
| `bootstrap(post_exec=...)`                     | `Callable[[TestCycleResults], None]`                  | appelé après `run_plugins`          |
| `CliBuilder(effects_factory=lambda ns: (...))` | `Effects`                                             | appelés après le parse argparse     |
| `test_scenario: TestScenario[Driver]`          | `Callable[[Driver, ILogger], Scenario[Driver]]`       | appelé par `Test.spawn`             |
| `dispatch[mode]()` dans `TestCycle.run_all`    | dict de `Thunk[bool]`                                 | appelé en lookup                    |

## `ChainRunner`

```python
runner = drive_page(act1, act2, act3)        # ⚠️  rien exécuté
# … plus tard …
chain = runner.run()                         # ▶︎  exécution
```

| Capacité                                             | Sans paresse                                  | Avec paresse   |
| ---------------------------------------------------- | --------------------------------------------- | -------------- |
| Stocker un scénario dans une variable                | impossible (déjà exécuté)                     | trivial        |
| Multiplier `[runner] * 5`                            | exécute 1 fois, on a 5 références au résultat | exécute 5 fois |
| Passer un `runner` à un autre `runner` (composition) | impossible                                    | trivial        |
| Réordonner les `act` dans un test refactor           | difficile                                     | trivial        |

## `validate(...).execute()`

```python
v = validate(value, name="x").assert_that(is_positive).assert_that(is_not_zero)
# … on peut composer …
combined = chain_validations(v, other_validation)
# … rien d'exécuté jusqu'ici …
combined.execute().raise_if_invalid()        # ▶︎  exécution + agrégation
```

C'est ce qui permet à `_ValidationChain` de **collecter** toutes les erreurs avant d'en lever une seule (`AggregateInvariantViolationError`).

## `Watcher.callback`

```python
watcher = Watcher(callback=my_callback, name="x", poll_interval=0.5)
# rien d'exécuté

watcher.start(driver, logger, take_screenshot)
# ▶︎  spawn d'un daemon thread qui appelle my_callback(self) toutes les 0.5 s
```

Conséquence&nbsp;: la _création_ d'un watcher est gratuite. On peut en mettre 10 dans `scenario.watchers` sans coût&nbsp;; ils ne tournent que pendant `test_chain`.

## `set_prefix(thunk)`

```python
logger.set_prefix(lambda: f"[{datetime.now().isoformat()}]")
```

Pourquoi un `Thunk`&nbsp;? Parce qu'on veut **un préfixe différent à chaque log** (timestamps changent). Si on passait une `str`, ce serait figé.

## `effects_factory(ns) -> Effects`

```python
return CliBuilder(
    args=[...],
    effects_factory=lambda ns: (
        lambda: store.set("workers", ns.workers),
        lambda: store.set("browser", ns.browser),
        ...
        _create_validate_only_exclude_mutex_effect(ns),
        ...
    ),
)
```

- `effects_factory` est appelé _après_ le parse argparse, avec `ns` complet.
- Il retourne un tuple d'`Effect`.
- Le `CliBuilder` les exécute un par un.

On peut **séparer** la déclaration des effets (`(lambda: ..., lambda: ...)`) de leur exécution.

## `TestScenario[Driver]`

```python
type TestScenario[Driver] = Callable[[Driver, ILogger], Scenario[Driver]]
```

Pas un `Scenario` directement&nbsp;:

- `driver` n'existe pas au moment de la déclaration du test (il est acquis par `TestFlow.run`).
- `logger` n'existe pas non plus (il est créé par `TestSuite._create_logger`).

→ On déclare le scénario _en différé_&nbsp;: «&nbsp;_voici comment construire le Scenario quand tu auras un driver et un logger_&nbsp;». Le framework appelle cette factory au runtime.

## `dispatch[mode]()`

```python
dispatch: dict[Mode, Thunk[bool]] = {
    "fail-fast-on-first-smoke-campaigns-sequence-fail":
        lambda: _run_smoke(fail_fast=True),
    "wait-for-all-smoke-tests":
        lambda: _run_smoke(fail_fast=False),
}

skip_all = dispatch[self._mode]()
```

| `if/elif`                                               | dispatch table                                      |
| ------------------------------------------------------- | --------------------------------------------------- |
| Code impératif                                          | Code déclaratif                                     |
| Une seule branche évaluée&nbsp;—&nbsp;c'est OK          | Aucune branche évaluée tant qu'on ne fait pas `()`  |
| Difficile à étendre                                     | Ajouter un mode = ajouter une clé                   |
| Vérification d'exhaustivité du `Literal` plus difficile | Le checker peut vérifier que la table couvre `Mode` |

## Paresse et composition

La paresse n'est pas une optimisation, c'est ce qui rend la composition **propre**.

Si `validate(...).assert_that(...)` s'exécutait tout de suite, on ne pourrait pas combiner avec une autre chaîne via `chain_validations`.

Si un `ChainRunner` s'exécutait à sa création, on ne pourrait pas le mettre dans une branche `match_page`.
