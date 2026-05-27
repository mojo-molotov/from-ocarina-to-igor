---
title: "02.03.04 — chain_actions et le ChainRunner"
weight: 4
date: 2026-05-20
series: ["railway"]
series_order: 4
tags: ["ocarina", "rop"]
---

# 02.03.04&nbsp;—&nbsp;`chain_actions` et le `ChainRunner`

> Fichier source&nbsp;: [`src/ocarina/dsl/testing_with_railway/chain_actions.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/chain_actions.py)
>
> C'est la primitive qui rend le DSL «&nbsp;_plat_&nbsp;». Sans elle, un scénario à N pas serait un escalier de `.then(...).failure(...).success(...).execute()`. Avec elle, c'est une liste.

## «&nbsp;_Parenthesis hell_&nbsp;»

> Solution&nbsp;:
>
> ```python
> # Flat, readable syntax
> runner = chain_actions(
>     action1.failure(h1).success(h2),
>     action2.failure(h3).success(h4),
>     action3.failure(h5).success(h6)
> )
> chain = runner.run()  # Execute when ready
> ```
>
> Benefits&nbsp;:
>
> - **Lazy evaluation**&nbsp;: Build chain without executing
> - **Flat syntax**&nbsp;: No deep nesting
> - **Automatic short-circuiting**&nbsp;: Stops on first failure
> - **Composability**&nbsp;: ChainRunner is a value

_(Extrait de docstring.)_

## `ChainRunner[T]`

```python
@final
class ChainRunner[T]:
    def __init__(self, *, thunk: Thunk[ActionChain[T]]) -> None:
        self._thunk = thunk

    def run(self) -> ActionChain[T]:
        return self._thunk()
```

1. **`@final`**, pas d'héritage utilisateur.
2. **Constructeur en kwargs-only** (`*, thunk: ...`) empêche l'erreur classique&nbsp;: `ChainRunner(no_idea)` qui aurait été ambigu.
3. **Le `thunk` est un `Thunk[ActionChain[T]]`**&nbsp;: c'est-à-dire `Callable[[], ActionChain[T]]`. Aucun effet de bord n'arrive avant `.run()`.
4. **`.run()` retourne l'`ActionChain[T]`**&nbsp;: on récupère donc la machine à états (cf. [`02-action-chain-states.md`](02-action-chain-states.md)) sur laquelle on peut interroger `has_failed`, `is_ok`, `result`.

## `chain_actions[T](first, *rest)`

```python
def chain_actions[T](
    first: ActionSuccess[T], *rest: ActionSuccess[T]
) -> ChainRunner[T]:

    def thunk() -> ActionChain[T]:
        def reducer(chain: ActionChain[T], step: ActionSuccess[T]) -> ActionChain[T]:
            if chain.has_failed():
                return chain
            return (
                chain.then(step.__action__)
                .failure(step.__failure_handler__)
                .success(step.__success_handler__)
                .execute()
            )
        return reduce(reducer, rest, first.execute())

    return ChainRunner(thunk=thunk)
```

C'est un _fold left_&nbsp;:

| Concept FP                   | Réalisation Python                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| Élément initial (`init`)     | `first.execute()`&nbsp;—&nbsp;exécute le premier acte, on a déjà un `ActionChain[T]` |
| Itération (`xs`)             | `rest` (le `*` des arguments)                                                        |
| Reducer (`(acc, x) -> acc'`) | `reducer(chain, step) -> ActionChain[T]`                                             |
| Court-circuit                | `if chain.has_failed(): return chain`                                                |
| Composition itérative        | `chain.then(step.__action__).failure(...).success(...).execute()`                    |

## Pourquoi `first` et `*rest` séparés&nbsp;?

1. **Typage strict**&nbsp;: on garantit au moins un `ActionSuccess[T]`. `chain_actions()` sans argument ne compile pas.
2. **Initial du fold**&nbsp;: il faut une valeur initiale (`ActionChain[T]`), donc on doit avoir _exécuté_ le premier acte avant la boucle. Si l'on faisait `*all`, on devrait construire un `ActionChain[T]` neutre initial («&nbsp;_le rail vide_&nbsp;»), ce qui forcerait à reconnaître un état «&nbsp;_nothing done_&nbsp;».
3. **Lisibilité**&nbsp;: `chain_actions(action1.failure...success(...), action2.failure...success(...), ...)` se lit naturellement.

## Pourquoi les fonctions internes

```python
def thunk() -> ActionChain[T]:
    def reducer(...): ...
    return reduce(reducer, rest, first.execute())
return ChainRunner(thunk=thunk)
```

- **`thunk` capture en closure `first` et `rest`**. `chain_actions` est donc une _closure_ sur ses arguments. Quand on appelle plus tard `runner.run()`, le `thunk()` réutilise ces captures.
- **`reducer` est défini _à l'intérieur_ de `thunk`**&nbsp;: il n'a pas besoin de capturer de variables externes, et le définir ici plutôt qu'au niveau module évite d'exposer un symbole privé au reste du package.

## Composition&nbsp;: `ChainRunner`

- On peut **stocker** un `ChainRunner` dans une variable et le réutiliser.
- On peut le **passer en argument**.
- On peut **multiplier** une liste de `ChainRunner`&nbsp;: `[runner] * 5` répète l'exécution 5 fois quand la séquence est jouée. Le Holy Book le mentionne explicitement (chapitre «&nbsp;_Scenarios composability_&nbsp;», section «&nbsp;_Répétitions_&nbsp;»).
- L'**aliasing** est trivial&nbsp;:

```python
click_confirm_cookies = drive_page(
    act(on_homepage, confirm_cookie_banner)
        .failure(log_error_with_current_url("Failed to dismiss banner..."))
        .success(log_success_with_current_url_and_take_screenshot("Banner dismissed!"))
)

# … plus tard …
return [
    match_page(branches=[
        when(check_that_page.has_cookies_banner, name="cookies", then=[click_confirm_cookies]),
        when(check_that_page.has_not_cookies_banner, name="no cookies", then=[]),
    ]),
    drive_page(...),
]
```

## `drive_page` est un monomorphisme de `chain_actions`

Le seul `drive_page` du framework est&nbsp;:

```python
def drive_page(
    first: ActionSuccess[TPOM], *rest: ActionSuccess[TPOM]
) -> ChainRunner[TPOM]:
    return chain_actions(first, *rest)
```

Voir [`06-drive-page.md`](06-drive-page.md) pour la raison d'être de cet alias.

## Trace d'exécution annotée

Cas concret&nbsp;: trois acts, le second échoue.

```
runner = drive_page(act1, act2, act3)   # ⚠️  rien exécuté

chain = runner.run()                    # ▶︎  exécution :
  ┌─ first.execute()                      = ActionChain(ok=True, result=Ok(...))   ← état initial du fold
  │
  ├─ reduce(reducer, [act2, act3], <ActionChain ci-dessus>)
  │      │
  │      ├─ reducer(<ok chain>, act2) :
  │      │     chain.then(act2.__action__)        → ActionStart        (rail succès)
  │      │     .failure(act2.__failure_handler__) → ActionFailure
  │      │     .success(act2.__success_handler__) → ActionSuccess
  │      │     .execute()                         → action lève → Fail
  │      │                                        → failure_handler(exc)  ❌
  │      │                                        → ActionChain(ok=False, result=Fail(exc))
  │      │
  │      └─ reducer(<failed chain>, act3) :
  │            chain.has_failed() → True → return chain      ⚠️  act3 jamais exécuté
  │
  └─ return ActionChain(ok=False, result=Fail(exc))
```

## `functools`

```python
from functools import reduce
```

Pas de `toolz`, pas de `funcy`, pas de wrapper maison. Juste `functools.reduce`, c'est la signature canonique d'un fold en Python.

## Tests dédiés

[`tests/scenarios/test_railway_and_action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_railway_and_action_chain.py) contient des tests sur&nbsp;:

- chaînage de 3+ actes en succession,
- court-circuit après 2e échec (le 3e n'est jamais appelé),
- comptage d'`act` via `ActCounter` (le compteur n'est pas incrémenté pour les pas de test court-circuités).
