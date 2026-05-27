---
title: "02.06 — Scenario[Driver]"
description: "Fichier source : src/ocarina/custom_types/scenario.py"
weight: 6
date: 2026-05-20
series: ["ocarina"]
series_order: 6
tags: ["watcher", "scenarios"]
---

# 02.06&nbsp;—&nbsp;`Scenario[Driver]`

> Fichier source&nbsp;: [`src/ocarina/custom_types/scenario.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/custom_types/scenario.py)

## Dataclass

```python
@final
@dataclass(frozen=True)
class Scenario[Driver]:
    test_chain: TestChain
    setup: TestSetup = field(default=None)
    teardown: TestTeardown = field(default=None)
    watchers: TestWatchers[Driver] | None = field(default=None)
```

```python
# src/ocarina/custom_types/test_components.py
type TestChain = Sequence[ChainRunner[Any]]
type TestSetup = Effect | None
type TestTeardown = Effect | None
type TestWatchers[Driver] = Sequence[Watcher[Driver]] | None
```

## Cycle de vie (per attempt)

```
1. setup()           — optionnel, Effect libre (DB, API, …)
       → lève     :  skip de test_chain, jump à teardown,
                     return Outcome(setup_failed=True, should_retry=True)
       → ok       :  continue à test_chain

2. test_chain        — la chaîne réelle (Sequence[ChainRunner])
       (les watchers tournent pendant ce temps)

3. teardown()        — optionnel, toujours exécuté
       → lève     :  log warning + ignore (n'affecte pas le verdict)

Si TOUTES les tentatives lèvent au setup :
    → test marqué SKIPPED (pas FAILED)
    → log warning « setup keeps failing »
```

## `setup` et `teardown`

`setup` et `teardown` sont **driver-free et injectionless by design.**

C'est documenté dans le docstring du module&nbsp;:

> They are plain `Effect`s&nbsp;—&nbsp;`() -> None`.
> They are meant for infrastructure concerns: seeding a database, calling an API, cleaning up state. Selenium belongs in `test_chain`.
> Whatever context they need (logger, driver, config) must be **captured in the closure** at scenario construction time.

```python
def my_scenario(driver: WebDriver, logger: ILogger) -> Scenario[WebDriver]:
    return Scenario(
        setup=lambda: seed_test_user(logger=logger),                # logger capturé
        teardown=lambda: delete_test_user(logger=logger),           # logger capturé
        test_chain=[...],
    )
```

1. **Pas de couplage** entre infrastructure et POMs. Le setup d'une DB n'a pas à connaître Selenium.
2. **Symétrie avec les `Watcher.callback`**&nbsp;: eux aussi reçoivent leur contexte via closure (le `Watcher` injecte `driver`, `logger`, `take_screenshot` _au moment de `start()`_).
3. **Testabilité**&nbsp;: on peut tester un setup en isolation, sans le wrapper Selenium.

## `test_chain`

```python
type TestChain = Sequence[ChainRunner[Any]]
```

C'est exactement ce qu'on construit en retournant `[drive_page(...), drive_page(...), match_page(...), drive_page(...)]`. Chaque élément est exécuté séquentiellement par `_run_chain` (cf. [`05-orchestration/02-test-executor.md`](05-orchestration/02-test-executor.md)).

Nuance&nbsp;: `ChainRunner[Any]` (pas `ChainRunner[TPOM]`). C'est parce qu'une `test_chain` peut **mélanger** des `drive_page` sur différentes pages (HomePage, LoginPage, DashboardPage…) et des `match_page` (qui retournent `ChainRunner[Any]`). L'`Any` est le _ramasse-tout_ qui rend la séquence hétérogène typable.

## `watchers`

```python
type TestWatchers[Driver] = Sequence[Watcher[Driver]] | None
```

Les watchers sont des _daemon threads_ qui observent le navigateur en parallèle de la chaîne, et qui reportent les frictions détectées via `watcher.report(...)`. Voir [`07-watcher.md`](07-watcher.md)

- **Démarrés _juste avant_ la chaîne**, **arrêtés _juste après_**. Strictement scopés à `test_chain`. Ils ne voient pas le `setup` ni le `teardown`.
- **Un thread par watcher**.
- **Un logger scopé par watcher**&nbsp;: `(*taxonomy[:-1], "<test_name> - <watcher_name>")`. Donne un fichier `.log` au même niveau que celui du test.

## Exemple

```python
from ocarina.custom_types.scenario import Scenario

def my_scenario(driver: WebDriver, logger: ILogger) -> Scenario[WebDriver]:
    page = MyPage(driver=driver)

    return Scenario(
        setup=lambda: seed_test_user(logger=logger),
        test_chain=[
            drive_page(
                act(page, open_page)
                    .failure(log_error("Failed to open..."))
                    .success(log_success("Opened!")),
            ),
            drive_page(
                act(page, verify_page)
                    .failure(log_error("Failed to verify..."))
                    .success(log_success("Verified!")),
            ),
        ],
        teardown=lambda: delete_test_user(logger=logger),
        watchers=[
            MyWatcher(...),
        ],
    )
```

## Pourquoi `frozen=True` et `@final`

`@final` + `@dataclass(frozen=True)`&nbsp;:

| Propriété                                     | Conséquence                                                      |
| --------------------------------------------- | ---------------------------------------------------------------- |
| `frozen=True`                                 | Impossible de muter `scenario.test_chain = [...]` après création |
| `@final`                                      | Impossible d'hériter (`class MyScenario(Scenario[WebDriver])`)   |
| Construction par kwargs implicite (dataclass) | API stable                                                       |

Un `Scenario` est une **valeur**.

## `TestRunner`

`Test.spawn(driver, logger)` retourne un `TestRunner` qui **agrège**&nbsp;:

- `chain_runners` (concaténation `pre + scenario.test_chain + post`),
- `setup` (vient de `scenario.setup`),
- `teardown` (vient de `scenario.teardown`),
- `watchers` (vient de `scenario.watchers`),
- `skipped` (vient de `Test._skipped`).

Donc&nbsp;: ce qui est dans le `Scenario` est **strictement le scénario**. Les fragments pre/post sont _ajoutés autour_ par `spawn`.

## Test associé

[`tests/scenarios/test_test_suite.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_test_suite.py) contient un test qui passe par un scenario avec setup+teardown&nbsp;:

```python
@allure.title("setup that fails on first attempt, succeeds on retry, then test passes")
def test_setup_retries_then_test_passes() -> None:
    ...
```

Cf. [`../04-internal-tests/03-pytest-scenarios.md`](../04-internal-tests/03-pytest-scenarios.md)
