---
title: "02.03.05 — create_act et ses hooks"
description: "create_act : la primitive bas niveau qui crée le verbe act d'un projet, avec ses hooks on_failure et la convention d'un act unique."
weight: 5
date: 2026-05-20
series: ["railway"]
series_order: 5
tags: ["ocarina"]
---

# 02.03.05&nbsp;—&nbsp;`create_act` et ses hooks

> Fichier source&nbsp;: [`src/ocarina/dsl/testing_with_railway/constructors/create_act.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/constructors/create_act.py)
>
> Cette fonction est la **primitive de bas niveau** qui crée un constructeur de _pas de test_. Elle est appelée par l'utilisateur **une fois**, pour créer un verbe `act` propre au projet. Selon la complexité du projet, on peut envisager plusieurs `act` distincts avec des hooks différents, mais aucun cas d'usage encore observé pour ça, donc on préconise de n'en créer **qu'un seul**. Ce n'est pas un singleton pour autant&nbsp;:&nbsp;c'est _juste_ une convention.

## Signature

```python
def create_act(
    pom: TPOM,
    action: Callable[[TPOM], TPOM],
    *,
    on_failure: Callable[[TPOM, Exception], Fail] | None = None,
    on_run_effect: Effect | None = None,
    act_counter_effect: Effect | None = None,
) -> ActionStart[TPOM]:
```

| Paramètre            | Position     | Type                                        | Rôle                                                                                                                                                                                |
| -------------------- | ------------ | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pom`                | positionnel  | `TPOM` (bound `POMBase`)                    | La page (ou n'importe quelle subclass POMBase) sur laquelle on agit.                                                                                                                |
| `action`             | positionnel  | `Callable[[TPOM], TPOM]`                    | La fonction qui agit sur la page et retourne la page (fluent). Idempotente pour le typage.                                                                                          |
| `on_failure`         | keyword-only | `Callable[[TPOM, Exception], Fail] \| None` | Hook d'**affinage** du `Fail`&nbsp;: si on tombe dedans, on a déjà failed&nbsp;; le hook permet juste de typer plus précisément l'erreur (par exemple `HttpErrorPageReachedError`). |
| `on_run_effect`      | keyword-only | `Effect \| None`                            | Effet de bord appelé **avant** l'action (par exemple&nbsp;: logger un step number).                                                                                                 |
| `act_counter_effect` | keyword-only | `Effect \| None`                            | Effet de bord _supplémentaire_ appelé avant l'action. Par défaut&nbsp;: incrémente le compteur d'`act`.                                                                             |

## Code

```python
def run_action() -> Result[TPOM]:
    try:
        if act_counter_effect:
            act_counter_effect()
        else:
            ThreadsBasedActCounter().incr_act_call_count()

        if on_run_effect:
            on_run_effect()

        result_pom = action(pom)
        return Ok(result_pom)
    except Exception as exc:  # noqa: BLE001
        if on_failure:
            return on_failure(pom, exc)
        return Fail(error=exc)

return ActionStart(run_action)
```

1. **Le `try` enveloppe TOUT**&nbsp;: `act_counter_effect`, `on_run_effect`, _et_ l'action. Si l'un de ces effets de bord lève (par exemple, si `on_run_effect` accède à une ressource morte), c'est traité comme un échec de pas de test. Tout ce qu'il se passe «&nbsp;_pendant le pas de test_&nbsp;» EST le pas de test.
2. **L'ordre est déterministe**&nbsp;: compteur&nbsp;→&nbsp;run effect →&nbsp;action. Le compteur s'incrémente _même si_ l'action va échouer (c'est intentionnel&nbsp;: on veut savoir combien de pas de test ont été _tentés_, pas réussis).
3. **`on_failure` peut renvoyer un `Fail` enrichi**&nbsp;: c'est ici qu'on transforme une `WebDriverException` en `HttpErrorPageReachedError`, par exemple.

## `ActCounter` par défaut&nbsp;: `ThreadsBasedActCounter`

```python
from ocarina.opinionated.infra.act_counter import ActCounter as ThreadsBasedActCounter
# ...
if act_counter_effect:
    act_counter_effect()
else:
    ThreadsBasedActCounter().incr_act_call_count()
```

Source&nbsp;: [`src/ocarina/opinionated/infra/act_counter.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/opinionated/infra/act_counter.py)

```python
from threading import local
from ocarina.infra.act_counter import ActCounter as _ActCounter

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

C'est un compteur **thread-local**. C'est un choix **architectural**&nbsp;: un worker de test = un thread, d'où cette implémentation naïve et efficace. Chaque worker du `TestSuite` a son propre compteur, ce qui évite la contention sans avoir besoin de `threading.Lock`. C'est `TestExecutor` qui le _lit_ à la fin (`steps_count = self._act_counter.get()`).

## Pattern recommandé (extrait du docstring)

```python
# In your project, create a wrapper with custom logic
def act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]:
    def failure_hook(pom: TPOM, exc: Exception) -> Fail:
        # Detect HTTP error pages
        title = pom.get_current_title()
        if ERROR_PAGE_REGEX.match(title):
            return Fail(error=HttpErrorPageReachedError(title))
        return Fail(error=exc)

    return create_act(
        pom, action,
        on_failure=failure_hook,
        on_run_effect=increment_step_counter
    )

# Then use your wrapper
act(page, lambda p: p.click_button())
    .failure(log_error)
    .success(log_success)
    .execute()
```

Ce pattern est exactement celui appliqué dans `ocarina-example/lib/ext/ocarina/adapters/agnostic/act.py` (cf. [`../../07-ocarina-example/02-adapters.md`](../../07-ocarina-example/02-adapters.md)).

## Pourquoi ne pas juste utiliser `create_act` directement partout

1. **`on_failure` _devrait_ être spécifique au projet.** Sans `on_failure`, toute exception devient un `Fail(exc)` brut. Avec ce hook, on peut identifier des _classes_ d'erreurs (page d'erreur HTTP, page de maintenance, etc.), ce qui rend les `transient_errors` plus précises.
2. **`on_run_effect`** est l'endroit où l'on peut ajouter du logging step-by-step ou des metrics.
3. **Le compteur d'`act`** est presque toujours celui par défaut, mais peut être surchargé pour des cas particuliers.

## `__action__` est récupérée par `chain_actions`

`ActionStart(run_action)` stocke `run_action` dans `self.__action__`. Quand `chain_actions` réutilise cet `ActionStart` (via `step.__action__`), il récupère exactement ce thunk capturant `pom`, `action`, `on_failure`, `on_run_effect`, `act_counter_effect` en _closure_. Tout est paresseux jusqu'au `.execute()`.

## Tableau récapitulatif des hooks

| Hook                 | Quand est-il appelé&nbsp;?                | Quel effet&nbsp;?                                                                                                         |
| -------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `act_counter_effect` | Avant l'action, avant `on_run_effect`     | Si fourni&nbsp;: remplace l'incrémentation par défaut. Si absent&nbsp;: `ThreadsBasedActCounter().incr_act_call_count()`. |
| `on_run_effect`      | Avant l'action, après le compteur         | Effet de bord libre                                                                                                       |
| `on_failure`         | Après le `except`, avant le retour `Fail` | Reçoit `(pom, exc)`, retourne un `Fail` _affiné_                                                                          |
