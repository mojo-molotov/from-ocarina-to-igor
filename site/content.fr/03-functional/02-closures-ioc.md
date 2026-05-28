---
title: "03.02 — Closures comme primitive d'inversion de contrôle"
description: "Les closures comme primitive d'inversion de contrôle dans Ocarina : pas de conteneur DI, l'injection passe par la capture de scope."
weight: 2
date: 2026-05-20
series: ["fonctionnel"]
series_order: 2
---

# 03.02&nbsp;—&nbsp;Closures comme primitive d'inversion de contrôle

> Pas de DI container. Pas de framework d'injection. **Une closure est la primitive d'injection** d'Ocarina.

## L'idée

Une closure capture des valeurs dans son scope englobant. Quand on retourne une fonction depuis une autre fonction, les paramètres de l'extérieur sont **disponibles à l'intérieur**, même après que la fonction extérieure ait rendu la main.

```python
def make_handler(logger: ILogger) -> Callable[[str], FailureHandler]:
    def make_failure_handler(msg: str) -> FailureHandler:
        def actual_handler(exc: Exception) -> None:
            logger.error(msg, exc=exc)
        return actual_handler
    return make_failure_handler
```

C'est aussi du _currying_&nbsp;: `make_handler(logger)(msg)(exc)`. Chaque appel capture une nouvelle couche d'environnement.

## Rappel du Holy Book

```python
# ocarina-example/lib/ext/ocarina/adapters/selenium/logs.py
def create_just_log_error(*, logger: ILogger) -> Callable[[str], FailureHandler]:
    return lambda msg: lambda exc: logger.error(msg, exc=exc)
```

| Niveau | Capture  | Appel typique                          |
| ------ | -------- | -------------------------------------- |
| 1      | `logger` | `create_just_log_error(logger=logger)` |
| 2      | `msg`    | `just_log_error("Failed to do X")`     |
| 3      | `exc`    | passé en arg par le framework          |

```python
just_log_error = create_just_log_error(logger=logger)

return [
    drive_page(
        act(on_homepage, open_homepage)
            .failure(just_log_error("Failed to open the homepage..."))    # ← niveau 2
            ...
    )
]
```

Le `just_log_error("Failed to open...")` retourne un `FailureHandler` qui, quand appelé par le framework avec l'exception, écrit le message.

## Pourquoi pas un objet avec méthodes&nbsp;?

Et bien PARCE QUE.

## L'IoC concrète d'Ocarina

L'inversion de contrôle dans Ocarina est essentiellement «&nbsp;_le framework appelle ton code_&nbsp;» plutôt que «&nbsp;_ton code appelle le framework_&nbsp;».

### 1. `create_act(on_failure=...)`

```python
def act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]:
    def failure_hook(pom: TPOM, exc: Exception) -> Fail:
        if is_http_error_page(pom):
            return Fail(error=HttpErrorPageReachedError(...))
        return Fail(error=exc)
    return create_act(pom, action, on_failure=failure_hook)
```

→ Le framework appelle _ton_ `failure_hook` quand l'action lève. Ton hook a accès à `pom` (capturé en argument) et à `exc`. Tu décides du `Fail` retourné.

### 2. `Scenario.setup` /&nbsp;`Scenario.teardown`

```python
return Scenario(
    setup=lambda: seed_test_user(logger=logger),         # closure logger
    teardown=lambda: delete_test_user(logger=logger),    # closure logger
    test_chain=[...],
)
```

→ Le framework appelle _ton_ `setup` au bon moment. Tu lui donnes accès à `logger` via une closure si tu veux.

### 3. `Watcher.callback`

```python
def my_callback(watcher: Watcher) -> None:
    elements = watcher.driver.execute_script("...")
    for el in elements:
        watcher.report(f"detected: {el}")

scenario = Scenario(
    test_chain=[...],
    watchers=[Watcher(callback=my_callback, name="cookies", poll_interval=0.8)],
)
```

→ Le framework appelle _ton_ `my_callback` toutes les "`poll_interval`" secondes. Tu lui passes le `Watcher` (qui te donne `driver`, `cache`, `report`).

### 4. `match_page(when(condition=...))`

```python
match_page(branches=[
    when(check.has_cookies_banner, name="A", then=[...]),
    when(check.has_not_cookies_banner, name="B", then=[...]),
])
```

→ Le framework appelle _ta_ `condition` au runtime pour décider de la branche.

### 5. `bootstrap(post_exec=...)`

```python
def _post_exec(results: TestCycleResults) -> None:
    pretty_print_results(results, with_colors=True)
    if has_test_cycle_failed(results):
        sys.exit(1)

bootstrap(test_cycle=..., run_plugins=..., post_exec=_post_exec)
```

→ Le framework appelle _ta_ `_post_exec` à la fin du cycle.

## Connecteurs paramétrés

Pattern du Holy Book (chapitre «&nbsp;_Premiers obstacles du monde réel_&nbsp;»)&nbsp;:

```python
def enter_xxx_key(p: CorsicamonEnterXXXKeyPage) -> CorsicamonEnterXXXKeyPage:
    return p.enter_xxx_key()

def enter_xxx_key_with_retries(
    *, retries: int, logger: ILogger,
) -> Callable[[CorsicamonEnterXXXKeyPage], CorsicamonEnterXXXKeyPage]:

    def unwrapped(p: CorsicamonEnterXXXKeyPage) -> CorsicamonEnterXXXKeyPage:
        return p.enter_xxx_key_with_retries(retries=retries, logger=logger)

    return unwrapped
```

> Il suffit de retourner le `def` avec la signature attendue, à l'intérieur d'une fonction qui capture les paramètres. C'est une _closure_.

- `enter_xxx_key` est un _connector_ direct.
- `enter_xxx_key_with_retries(retries=3, logger=logger)` retourne **un connector** qui sait combien de retries et quel logger utiliser. Le framework reçoit ce connector et l'appelle avec un `(p: CorsicamonEnterXXXKeyPage)`.

## Pourquoi

Le Holy Book (chapitre 1.3)&nbsp;:

> _M'imposer leur incompréhension de l'évaluation paresseuse et de l'IoC comme des vérités absolues_.

L'IoC d'Ocarina est **explicite, locale, typée**. Pas de magie.

| Bénéfice               | Comparaison                                                                                          |
| ---------------------- | ---------------------------------------------------------------------------------------------------- |
| **Aucun setup global** | Pas de `inject()`, pas de `bind(...)` à écrire avant de tester.                                      |
| **Tests triviaux**     | Pour tester `create_just_log_error(logger=mock_logger)(msg)(exc)`, on fait juste ça. Aucune fixture. |
| **Type-safe**          | Le checker vérifie la signature à chaque niveau de currying.                                         |
| **Refactor friendly**  | Renommer un paramètre traverse tout le call graph proprement.                                        |

## Données&nbsp;→&nbsp;fonctions

Le Holy Book le formule autrement dans le chapitre «&nbsp;_Premiers retours_&nbsp;»&nbsp;:

> La donnée brute.

Dans Ocarina, «&nbsp;_la donnée brute_&nbsp;» inclut **les fonctions** comme valeurs de première classe. Un `Effect` est une donnée. Un `Thunk[T]` est une donnée. Une closure est une donnée enrichie. On les passe, on les compose, on les stocke. C'est algébrique.
