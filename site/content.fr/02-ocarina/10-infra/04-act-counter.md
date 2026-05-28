---
title: "02.10.04 — ActCounter + ThreadsBasedActCounter"
description: "ActCounter et ThreadsBasedActCounter : le compteur thread-local des act exécutés par tentative, pour situer l'étape exacte d'un échec dans le rapport."
weight: 4
date: 2026-05-20
series: ["infra"]
series_order: 4
tags: ["ocarina"]
---

# 02.10.04&nbsp;—&nbsp;`ActCounter` + `ThreadsBasedActCounter`

> Compteur thread-local du nombre d'`act` exécutés par tentative. Permet de reporter au rapport «&nbsp;_ce test a fait 17 steps avant d'échouer au step 18_&nbsp;».

## Interface

```python
# src/ocarina/infra/act_counter.py
class ActCounter:
    def get(self) -> int: ...
    def reset(self) -> None: ...
    def incr_act_call_count(self) -> None: ...
```

## Implémentation par défaut

```python
# src/ocarina/opinionated/infra/act_counter.py
from threading import local

_thread_local = local()
_COUNTER_KEY: Final[str] = "ocarina_counter"


class ActCounter(_ActCounter):
    def get(self) -> int:
        return getattr(_thread_local, _COUNTER_KEY, 0)

    def reset(self) -> None:
        setattr(_thread_local, _COUNTER_KEY, 0)

    def incr_act_call_count(self) -> None:
        if not hasattr(_thread_local, _COUNTER_KEY):
            self.reset()
        setattr(_thread_local, _COUNTER_KEY, getattr(_thread_local, _COUNTER_KEY) + 1)
```

- **`threading.local()`**&nbsp;: un namespace dont les attributs sont _par thread_. Chaque thread a sa propre valeur.
- **`_COUNTER_KEY = "ocarina_counter"`**&nbsp;: la clé d'attribut.
- **Pas de lock**&nbsp;: chaque thread n'écrit que sa propre valeur, donc pas de race condition.

## Pourquoi thread-local plutôt qu'un compteur partagé + lock&nbsp;?

Ocarina est architecturé de sorte qu'**un thread = un test**. Et aucune envie d'introduire toute une _state monad_ ou quoi, autant placer cette «&nbsp;_impureté_&nbsp;» (qui reste un "état") ici. C'est tout.

## Usage dans `create_act`

```python
def run_action() -> Result[TPOM]:
    try:
        if act_counter_effect:
            act_counter_effect()
        else:
            ThreadsBasedActCounter().incr_act_call_count()
        ...
```

À chaque `act(pom, action)` exécuté, le compteur du thread courant est incrémenté.

## Usage dans `TestFlow.run`

```python
for attempt in range(1, max_attempts + 1):
    self._act_counter.reset()                           # ◄── reset AVANT chaque tentative
    with self._drivers_pool.acquire() as driver:
        outcome = self._executor.execute(...)
    ...
```

Et à la fin&nbsp;:

```python
self._act_counter.reset()                               # ◄── reset après la dernière tentative
return last_result, last_steps_count, test.test_id
```

## Usage dans `TestExecutor.execute`

```python
steps_count = self._act_counter.get()
return ExecutionOutcome(
    result=result, skipped=False, setup_failed=False,
    should_retry=should_retry, steps_count=steps_count,
)
```

Le `steps_count` est lu **à la fin** d'une tentative. C'est ce qui apparaît dans le `TestSuiteResult = (TestResult, steps_count, test_id)`, et dans le `pretty_print_results` («&nbsp;_⫸ At step 3_&nbsp;» quand un test fail).

## `act_counter_effect`&nbsp;—&nbsp;pourquoi un hook customisable

Parce que c'est une **impureté** et qu'on veut garder un œil dessus en termes de testabilité. L'exposer ne coûte rien. C'est tout.

Le default reste «&nbsp;_incrémente le compteur thread-local d'Ocarina_&nbsp;», ce qui couvre 99% des cas.

## Pourquoi deux fichiers (`infra/` + `opinionated/infra/`)

| Fichier                                        | Rôle                                                                                         |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `src/ocarina/infra/act_counter.py`             | **Interface** `ActCounter`. Décrit le contrat. Utilisable par n'importe qui.                 |
| `src/ocarina/opinionated/infra/act_counter.py` | **Implémentation** `ThreadsBasedActCounter`. Choix opinionated d'utiliser `threading.local`. |
