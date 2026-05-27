---
title: "02.03.02 — La machine à états du builder"
weight: 2
date: 2026-05-20
series: ["railway"]
series_order: 2
tags: ["ocarina", "rop"]
---

# 02.03.02&nbsp;—&nbsp;La machine à états du builder

> Fichier source&nbsp;: [`src/ocarina/dsl/testing_with_railway/internals/action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/internals/action_chain.py)
>
> C'est ici qu'est implémentée _toute_ la mécanique ROP&nbsp;: le passage par quatre états successifs typés, qui interdit littéralement (au sens du _type-checker_) toute fantaisie syntaxique. Le DSL est aussi son propre système immunitaire.

## Vue d'ensemble

```
                      ┌─────────────────┐
   start(action)  →   │  ActionStart[T] │     un Action[T] = Thunk[Result[T]]
                      └────────┬────────┘
                               │ .failure(failure_handler)
                               ▼
                      ┌─────────────────┐
                      │ ActionFailure[T]│
                      └────────┬────────┘
                               │ .success(success_handler)
                               ▼
                      ┌─────────────────┐
                      │ ActionSuccess[T]│
                      └────────┬────────┘
                               │ .execute()   ── exécute action(), fire le handler
                               ▼
                      ┌─────────────────┐
                      │ ActionChain[T]  │     contient (has_failed, result)
                      └──────┬──────────┘
                             │ .then(next_action_or_start)
              ┌──────────────┴──────────────┐
              │                             │
   has_failed=True                   has_failed=False
              │                             │
              ▼                             ▼
   ┌──────────────────┐         ┌──────────────────┐
   │ NeutralAction-   │         │ ActionStart[T]   │  → cycle recommence
   │ Start[T]         │         │  (l'action suiv. │
   │ (rail d'échec :  │         │   sera exécutée) │
   │  toute la chaîne │         └──────────────────┘
   │  devient no-op,  │
   │ tout en gardant  │
   │ l'API fluide)    │
   └──────────────────┘
              │
              ▼ (.failure → .success → .execute, tout en no-op)
   ┌──────────────────┐
   │  ActionChain[T]  │   has_failed=True, result=<le Fail accumulé>
   └──────────────────┘
```

## Les types `Action`, `FailureHandler`, `SuccHandler`

```python
type Action[T]        = Thunk[Result[T]]      # () -> Result[T]
type FailureHandler   = Callable[[Exception], None]
type SuccHandler      = Effect                # () -> None
```

- **`Action[T]` est un `Thunk`**. Cela veut dire qu'au moment où `ActionStart(action)` est appelé, **rien n'est exécuté**. L'action est juste capturée.
- **`FailureHandler` reçoit l'exception**, mais ne reçoit **pas** le `Fail` ni le `Result`. C'est volontaire&nbsp;:&nbsp;99% des handlers veulent tracer l'exception, prendre un screenshot, et c'est tout.
- **`SuccHandler` est un `Effect`** (sans argument). Idem&nbsp;: un handler de succès log un message statique, fait un screenshot, pas besoin du résultat.

## Typestate Pattern&nbsp;: pourquoi on ne peut pas se tromper

L'enchaînement est **strictement linéaire**. Chaque méthode renvoie un type différent, qui n'expose que la _suite logique_ de l'enchaînement&nbsp;:

| Type               | Méthodes exposées                                      | Pas de                                         |
| ------------------ | ------------------------------------------------------ | ---------------------------------------------- |
| `ActionStart[T]`   | `.failure(h)`                                          | `.success`, `.execute` (n'existent pas&nbsp;!) |
| `ActionFailure[T]` | `.success(h')`                                         | `.failure` (a déjà été appelé), `.execute`     |
| `ActionSuccess[T]` | `.execute()`                                           | `.failure`, `.success`                         |
| `ActionChain[T]`   | `.then(...)`, `.has_failed()`, `.is_ok()`, `.result()` | `.failure`, `.success`, `.execute`             |

Extraits du Holy Book (chapitre sur la composabilité des scénarios)&nbsp;:

### Tentative 1&nbsp;: Oublier `.success`

```python
drive_page(
    act(on_book_a_call_page, verify_book_call_page)
    .failure(just_log_error("..."))
)

# error: Expected type 'ActionSuccess[TPOM ≤: POMBase]', got 'ActionFailure[BookCallPage]' instead
```

### Tentative 2&nbsp;: Mettre `.success` avant `.failure`

```python
drive_page(
    act(on_book_a_call_page, verify_book_call_page)
    .success(log_success_with_url_and_screenshot("..."))   # ← erreur ici
)

# error:
# "ActionStart[BookCallPage]" has no attribute "success"
# Unresolved attribute reference 'success' for class 'ActionStart'
```

### Tentative 3&nbsp;: Inverser `.failure` et `.success`

```python
drive_page(
    act(on_book_a_call_page, verify_book_call_page)
    .success(...)
    .failure(...)
)

# error:
# "ActionStart[BookCallPage]" has no attribute "success"
```

Le checker refuse littéralement le code. La grammaire est **type-level**, pas seulement conventionnelle.

## Le narrowing par `act()`&nbsp;: conservation du `TPOM`

Le projet utilisateur définit `act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]`. Le `TPOM` est conservé _tout au long_ de la chaîne&nbsp;:

```python
on_homepage = Homepage(driver=driver)
act(on_homepage, verify_book_call_page)
#                ^^^^^^^^^^^^^^^^^^^^^
# error: Argument 2 to "act" has incompatible type
#   "Callable[[BookCallPage], BookCallPage]";
#   expected "Callable[[Homepage], Homepage]"
```

Mélanger des `act` hétérogènes dans un même `drive_page` est aussi refusé&nbsp;:

```python
drive_page(
    act(on_homepage, ...).failure(...).success(...),
    act(on_book_a_call_page, verify_book_call_page).failure(...).success(...),
    #   ^^^^^^^^^^^^^^^^^^^
    # error: Expected type 'ActionSuccess[Homepage]',
    #        got 'ActionSuccess[BookCallPage]' instead
)
```

Cette contrainte est ce qui force **transition de page = nouveau `drive_page`**. C'est une question de **sémantique**&nbsp;: ça aide à la revue (voir les transitions de page, identifier rapidement une capture d'écran manquante). Cf. [`05-create-act-hooks.md`](05-create-act-hooks.md)

## `ActionSuccess.execute()`

```python
def execute(self) -> ActionChain[T]:
    result = self.__action__()                              # 1. exécute l'action

    if is_fail(result):
        self.__failure_handler__(result.error)              # 2a. fire failure
        return ActionChain(has_failed=True, result=result)  #     rail d'échec

    self.__success_handler__()                              # 2b. fire success
    return ActionChain(has_failed=False, result=result)     #     rail de succès
```

1. **L'action est appelée sans argument** (c'est un `Thunk[Result[T]]`). Tout son contexte a été capturé en _closure_ par `create_act`.
2. Le handler de _failure_ reçoit `result.error`.
3. Le handler de _success_ ne reçoit **rien**.
4. `ActionChain` capture deux choses&nbsp;: un drapeau (`has_failed: bool`) **et** le `Result` lui-même. Le drapeau permet à `.then()` de prendre une décision _sans_ refaire un `isinstance` (_hot-path_).

## `__action__`, `__failure_handler__`, `__success_handler__`

Triple naming en _dunder_ (double underscores).

Ce sont des attributs **internes** au framework. La double underscore notation est utilisée pour signaler «&nbsp;_ne touche pas, c'est de la plomberie_&nbsp;». `chain_actions` les lit pour reconstruire la chaîne&nbsp;:

```python
def reducer(chain: ActionChain[T], step: ActionSuccess[T]) -> ActionChain[T]:
    if chain.has_failed():
        return chain
    return (
        chain.then(step.__action__)
        .failure(step.__failure_handler__)
        .success(step.__success_handler__)
        .execute()
    )
```

L'inspiration directe vient de [`xhtmlboi.github.io/articles/yocaml.html`](https://xhtmlboi.github.io/articles/yocaml.html). Le principe&nbsp;: partir d'une composition fonctionnelle «&nbsp;_plate_&nbsp;», explicite, avec potentiellement beaucoup de parenthèses imbriquées&nbsp;; puis introduire un opérateur (ici la chaîne `.failure().success().execute()` + `.then()`) qui _aplatit_ la lecture tout en conservant le typage. Ocarina applique exactement ce pattern, sur des _actions_ Selenium plutôt que des _rules_ OCaml.

## Récapitulatif

| Principe                                                 | Conséquence                                                                           |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Linéarité du builder                                     | Erreur _mypy_ si on saute une étape ou si on change l'ordre                           |
| `@final` sur chaque classe                               | Pas d'héritage utilisateur des classes ROP                                            |
| `Action[T]` est un `Thunk`                               | Évaluation paresseuse&nbsp;; tout est composable comme valeur                         |
| Une seule conversion `except → Fail` (dans `create_act`) | Aucune exception en aval&nbsp;; tout est valeur typée                                 |
| `ActionChain` porte `(has_failed, result)`               | `.then(...)` décide entre `ActionStart` et `NeutralActionStart` via un simple booléen |
| `__action__` etc. en dunder                              | Plomberie, relations bidirectionnelles dans l'implémentation du framework             |
