---
title: "03.04 — reduce / fold dans Ocarina"
description: "Un seul reduce dans toute la base de code. Mais c'est le réducteur central : il fait fonctionner chain_actions."
weight: 4
date: 2026-05-20
series: ["fonctionnel"]
series_order: 4
---

# 03.04&nbsp;—&nbsp;`reduce` /&nbsp;fold dans Ocarina

> Un seul `reduce` dans toute la base de code. Mais c'est **le** réducteur central&nbsp;: il fait fonctionner `chain_actions`.

## Code

```python
# src/ocarina/dsl/testing_with_railway/chain_actions.py
from functools import reduce

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

## Anatomie

| Concept FP       | Réalisation Python                       |
| ---------------- | ---------------------------------------- |
| Type accumulator | `ActionChain[T]`                         |
| Type element     | `ActionSuccess[T]`                       |
| Reducer          | `reducer(chain, step) -> ActionChain[T]` |
| Initial value    | `first.execute()`                        |
| Iterable         | `rest` (le tuple de `*rest`)             |
| Short-circuit    | `if chain.has_failed(): return chain`    |
| Result           | `ActionChain[T]` (le dernier)            |

## Flot d'exécution

```
initial = first.execute()                                          # → ActionChain(ok=True, result=Ok(...))

step 1 : reducer(<initial>, act2) :
  chain.has_failed() = False
  chain.then(act2.__action__).failure(...).success(...).execute()
  → action lève → Fail
  → failure_handler(exc)  ❌ FIRE
  → ActionChain(ok=False, result=Fail(exc))

step 2 : reducer(<failed>, act3) :
  chain.has_failed() = True
  return chain                                                     ⚠️  short-circuit

result du reduce = <failed ActionChain>
```

## Pourquoi `reduce`

```python
# Approche impérative (équivalente)
def thunk() -> ActionChain[T]:
    chain = first.execute()
    for step in rest:
        if chain.has_failed():
            break
        chain = (
            chain.then(step.__action__)
            .failure(step.__failure_handler__)
            .success(step.__success_handler__)
            .execute()
        )
    return chain
```

| Reduce                                            | Boucle impérative      |
| ------------------------------------------------- | ---------------------- |
| Une seule **valeur** circule (le `chain`)         | Un état + une mutation |
| Reducer = fonction pure (testable en isolation)   | Logique inline         |
| Sémantique «&nbsp;_accumulateur_&nbsp;» explicite | Logique implicite      |
| Standard fonctionnel                              | Standard impératif     |

C'est une **expression d'intention**&nbsp;: on _replie_ une liste sur un accumulator. La sémantique est claire dès la première lecture. C'est ce qu'on appelle un **catamorphisme**.

## `break` vs `return chain` dans le reducer

Le reducer ne peut pas `break`&nbsp;: il _doit_ retourner une valeur. Donc il retourne `chain` _inchangé_ à chaque step après l'échec.

C'est exactement ce qu'on veut&nbsp;: le fold continue sur les éléments restants, mais chaque appel du reducer renvoie le _même_ `chain failed`&nbsp;: c'est un court-circuit.

## `any` /&nbsp;`all` = folds Pythoniques

```python
def has_test_cycle_failed(results: TestCycleResults) -> bool:
    return any(
        is_test_result_fail(outcome)
        for campaigns in results.values()
        for tests in campaigns.values()
        for outcome, _, _ in tests.values()
    )
```

`any(...)` est un fold OR avec court-circuit. C'est trois `for` imbriqués qu'on _plie_ en un seul bool.

C'est la même mécanique conceptuelle que `chain_actions.reducer`, juste sans avoir besoin de `reduce` explicite.

## Pourquoi pas `toolz`, `funcy`, ou un wrapper maison

Le projet n'importe **aucune** lib FP tierce. `functools.reduce` est dans la stdlib depuis 30 ans. Pas de magie, pas de risque de breaking change, pas de dette d'audit.
