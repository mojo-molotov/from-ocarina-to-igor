---
title: "02.03.03 — Le rail d'échec : NeutralAction*"
description: "Cas particulier du builder : que se passe-t-il quand on enchaîne une action sur un ActionChain qui a déjà échoué ?"
weight: 3
date: 2026-05-20
series: ["railway"]
series_order: 3
tags: ["ocarina"]
---

# 02.03.03&nbsp;—&nbsp;Le rail d'échec&nbsp;:&nbsp;`NeutralAction*`

> Cas particulier du builder&nbsp;:&nbsp;que se passe-t-il quand on _enchaîne_ une action sur un `ActionChain` qui a déjà échoué&nbsp;?

## Pourquoi des classes _Neutral_ plutôt qu'un `if` côté utilisateur

Lorsqu'on enchaîne une action sur un `ActionChain` qui a déjà échoué, on bascule dans trois classes _Neutral_ qui acceptent la même API, mais ne font rien.

Imaginons que le DSL n'ait pas cette mécanique.  
Le code utilisateur ressemblerait à&nbsp;:

```python
chain = act1.failure(h).success(h).execute()

if chain.is_ok():
    chain = chain.then(act2).failure(h).success(h).execute()

if chain.is_ok():
    chain = chain.then(act3).failure(h).success(h).execute()
```

Ce serait _imperatif_, illisible, et briserait le but du DSL. Le rail neutre rend possible l'écriture flat&nbsp;:

```python
chain = (
    act1.failure(h).success(h).execute()
    .then(act2).failure(h).success(h).execute()
    .then(act3).failure(h).success(h).execute()
)
```

Toutes les actions sont **toujours** appelées dans le code (au sens syntaxique). Mais dès que `chain.then(act2)` est appelé sur un `ActionChain` qui a échoué, il retourne un `NeutralActionStart`. Le reste de la chaîne (`.failure → .success → .execute`) **passe à travers** les neutres sans rien faire.

## Code des trois classes

```python
@final
class NeutralActionStart[T]:
    def __init__(self, *, result: Result[T] | None) -> None:
        self._result = result

    def failure(self, *args, **kwargs) -> NeutralActionFailure[T]:
        return NeutralActionFailure(result=self._result)


@final
class NeutralActionFailure[T]:
    def __init__(self, *, result: Result[T] | None) -> None:
        self._result = result

    def success(self, *args, **kwargs) -> NeutralActionSuccess[T]:
        return NeutralActionSuccess(result=self._result)


@final
class NeutralActionSuccess[T]:
    def __init__(self, *, result: Result[T] | None) -> None:
        self._result = result

    def execute(self) -> ActionChain[T]:
        return ActionChain(has_failed=True, result=self._result)
```

### 1. `*args, **kwargs` ignorés

```python
def failure(self, *args, **kwargs) -> NeutralActionFailure[T]:
```

Les neutres acceptent _n'importe quel argument_&nbsp;—&nbsp;handler, kwargs&nbsp;—&nbsp;et les jettent. Le `# noqa: ARG002` dans le code source pour `*args` est explicite&nbsp;:&nbsp;on ne lit pas, c'est volontaire.

### 2. Même retour de type que les classes actives

`NeutralActionStart.failure` retourne `NeutralActionFailure`, comme `ActionStart.failure` retourne `ActionFailure`. C'est l'isomorphisme qui permet la composition fluide.

### 3. `result: Result[T] | None`

Le `None` est là pour le cas où la chaîne a été **interrompue avant** d'avoir produit un résultat. C'est explicité dans le docstring&nbsp;:

> ActionChain&nbsp;: `result` may be Ok, Fail, or None if skipped.

### 4. Propagation du `result` initial

Le `Fail` accumulé au premier échec est **propagé tel quel** jusqu'au bout. C'est le `result` du `Fail` initial qui sera consulté à la fin via `chain.result()`. Pas de _wrapping_, pas de réincarnation.

### 5. `has_failed=True` figé

Une fois sur le rail d'échec, on ne peut **pas en sortir**.

### 6. `@final` ici aussi

Aucune extension possible.

## Le point d'aiguillage&nbsp;: `ActionChain.then(...)`

```python
def then(
    self, action_or_start: Action[T] | ActionStart[T]
) -> ActionStart[T] | NeutralActionStart[T]:
    if self._has_failed:
        return NeutralActionStart(result=self._result)

    if isinstance(action_or_start, ActionStart):
        action = action_or_start.__action__
    else:
        action = action_or_start

    return ActionStart(action)
```

1. **Accepte `Action[T] | ActionStart[T]`**&nbsp;: on peut passer une `Action` directement ou un `ActionStart` (auquel cas on extrait son `__action__`). C'est utile pour `chain_actions` qui itère sur des `ActionSuccess` (et utilise leur `__action__`).
2. **Le typage du retour est une union**&nbsp;: `ActionStart[T] | NeutralActionStart[T]`. Le checker traite les deux uniformément parce que les deux exposent `.failure(...)`.
3. **Décision en O(1)**&nbsp;: un `bool`, pas un `isinstance`.

## Schéma temporel

Cas&nbsp;: trois acts dans un `drive_page`, le second échoue.

```
t0 : start
t1 : act1.execute()             → Ok                → ActionChain(has_failed=False, result=Ok)
t2 : chain.then(act2)           → ActionStart       (rail de succès)
t3 : .failure(h)                → ActionFailure
t4 : .success(h)                → ActionSuccess
t5 : .execute()                 → action() lève → Fail
                                → failure_handler(exc)        ❌ FIRE
                                → ActionChain(has_failed=True, result=Fail)
t6 : chain.then(act3)           → NeutralActionStart          ⚠️  passage rail d'échec
t7 : .failure(h)                → NeutralActionFailure        (h IGNORÉ)
t8 : .success(h)                → NeutralActionSuccess        (h IGNORÉ)
t9 : .execute()                 → ActionChain(has_failed=True, result=<le Fail de t5>)
```

Note de subtilité&nbsp;: les handlers du _troisième_ act ne sont **jamais appelés**. Ni le failure ni le success. C'est le sens propre du _short-circuit_.

## Pourquoi pas d'`Optional` partout

On pourrait imaginer une variante où `NeutralAction*` n'existerait pas, et où chaque méthode du builder vérifierait `if self._already_failed: ...`. Le coût serait&nbsp;:

- Un `bool` supplémentaire par classe.
- Une vérification _runtime_ à chaque méthode.
- Une API plus difficile à raisonner (chaque méthode a deux comportements).

La solution _trois classes neutres_ est plus simple à lire (chaque classe a **un seul** comportement) et plus rapide à exécuter (pas de check). C'est un cas-école d'application de KISS&nbsp;—&nbsp;voir [`../../01-philosophy/03-kiss-and-complexity.md`](../../01-philosophy/03-kiss-and-complexity.md)

## Tests dédiés au rail neutre

[`tests/scenarios/test_railway_and_action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_railway_and_action_chain.py) contient des tests précisément sur ce point, par exemple&nbsp;:

```python
@allure.title("A drive_page with a mid-failure short-circuits subsequent acts")
def test_drive_page_short_circuits_after_failure() -> None:
    pom = RecordingPOM(raise_on={"second"})
    runner = drive_page(
        create_act(pom, lambda p: p.step("first")).failure(lambda _: None).success(lambda: None),
        create_act(pom, lambda p: p.step("second")).failure(lambda _: None).success(lambda: None),
        create_act(pom, lambda p: p.step("third")).failure(lambda _: None).success(lambda: None),
    )
    chain = runner.run()
    assert chain.has_failed()
    assert pom.calls == ["first", "second"]   # ✅ "third" jamais appelé
```
