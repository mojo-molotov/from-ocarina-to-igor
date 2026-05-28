---
title: "02.04.01 — Le flot validate → assert_that → execute → raise_if_invalid"
description: "Le flot validate, assert_that, execute, raise_if_invalid : la machine à états du sous-DSL d'invariants typés d'Ocarina."
weight: 1
date: 2026-05-20
series: ["invariants"]
series_order: 1
tags: ["ocarina"]
---

# 02.04.01&nbsp;—&nbsp;Le flot `validate → assert_that → execute → raise_if_invalid`

> Fichier source&nbsp;: [`src/ocarina/dsl/invariants/validate.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/validate.py) (entry-point) + [`src/ocarina/dsl/invariants/internals/validation_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/internals/validation_chain.py)

## La machine à états

### Diagramme

```
validate(value: T)
       │
       ▼
ValidationStartBlock[T]
       │
       └─ assert_that(predicate, *, msg=None)
              │
              ▼
       ValidationAssertBlock[T]   ← état qui accepte plusieurs continuations
              │
              ├─► assert_that(P)     [boucle, AND chaînable, voir le diagramme dédié]
              ├─► otherwise(P)       [OR, voir 03-otherwise-any-of.md]
              ├─► then(U, name=...)  [change de valeur, voir 04-then-chain-of-validations.md]
              └─► execute()          → _ValidationResult
                                          │
                                          ├─ is_valid: bool
                                          ├─ errors: Sequence[InvariantViolationError]
                                          ├─ validated_values: Sequence[Any]
                                          └─ raise_if_invalid() : None | raise AggregateInvariantViolationError
```

### Boucle `assert_that`

`assert_that` formule **une** assertion sur la valeur courante. Plusieurs `assert_that` peuvent se suivre, chacun ajoutant une condition supplémentaire à la chaîne (AND logique, ordre préservé).

```
ValidationAssertBlock[T] ──assert_that(P)──► ValidationAssertBlock[T]
                ▲                                       │
                └───────────────────────────────────────┘
                  (chaîne autant de fois qu'on veut)
```

### Bifurcation `otherwise`

`otherwise` remplace le _dernier_ prédicat échoué par une alternative. Voir [`03-otherwise-any-of.md`](03-otherwise-any-of.md) pour le détail (et `any_of`, qui en généralise la sémantique).

```
ValidationAssertBlock[T] ──assert_that(P_last)──► ...
        │
        └── otherwise(P_alt)
             └─► ValidationAssertBlock[T]   (P_alt remplace P_last)
```

### Bascule de valeur avec `then`

`then(new_value)` revient sur le rail `ValidationStartBlock` avec une **nouvelle** valeur à valider, dans la même chaîne. Voir [`04-then-chain-of-validations.md`](04-then-chain-of-validations.md)

```
ValidationAssertBlock[T] ──then(U, name=...)──► ValidationStartBlock[U]
```

## Code

### `validate` (entry-point)

```python
def validate[T](value: T, *, name: str | None = None) -> ValidationStartBlock[T]:
    return ValidationStartBlock(value, name=name)
```

Une simple factory. Le `name=` est utilisé pour préfixer les messages d'erreur («&nbsp;_`email: …`_&nbsp;»).

### `ValidationStartBlock.assert_that`

```python
def assert_that(self, predicate: Predicate[T], *, msg: str | None = None) -> ValidationAssertBlock[T]:
    predicate = _with_msg(predicate, msg, self._name)
    self._chain.add_assertion(self._value, predicate, self._name)
    return ValidationAssertBlock(self._value, self._chain, self._name, last_predicate=predicate)
```

1. **Wrap du prédicat**&nbsp;: `_with_msg` enrobe le prédicat avec un message custom (optionnel) et un nom (optionnel). Si le prédicat échoue, le message custom remplace le message par défaut.
2. **Ajout au `_ValidationChain`**&nbsp;: la chaîne accumule les tuples `(value, name, predicate)`.
3. **Transition d'état**&nbsp;: on retourne un `ValidationAssertBlock` qui mémorise `last_predicate` (pour `.otherwise(...)`).

### `_PredicateWithMsg`

```python
@final
class _PredicateWithMsg[T]:
    def __init__(self, predicate: Predicate[T], msg: str | None = None) -> None:
        self.predicate = predicate
        self.msg = msg

    def __call__(self, value: T) -> None:
        try:
            self.predicate(value)
        except InvariantViolationError as exc:
            if self.msg:
                raise InvariantViolationError(self.msg) from exc
            raise
```

Le _wrapper_ qui **affine** le `InvariantViolationError` avec le message custom si fourni. L'erreur est de toute façon levée&nbsp;; on l'affine simplement avant de la propager.

### `_ValidationChain.execute`

```python
def execute(self) -> _ValidationResult:
    def run_step(value, predicate_with_msg):
        try:
            predicate_with_msg(value)
        except InvariantViolationError as exc:
            return False, exc
        else:
            return True, value

    errors = []
    validated = []
    for value, _, predicate_with_msg in self._steps:
        success, outcome = run_step(value, predicate_with_msg)
        if success:
            validated.append(outcome)
        else:
            errors.append(outcome)
    return _ValidationResult(
        is_valid=(len(errors) == 0),
        errors=errors,
        validated_values=validated,
    )
```

Mécanique&nbsp;: **tous les steps sont exécutés**, pas de _fail-fast_. Les erreurs sont **agrégées** dans une liste, les valeurs validées dans une autre. Ce qui rend ce DSL utile pour les CLI&nbsp;: un utilisateur voit toutes ses erreurs en un coup, pas une à la fois.

### `_ValidationResult.raise_if_invalid`

```python
def raise_if_invalid(self) -> None:
    if not self.is_valid:
        raise AggregateInvariantViolationError(self.errors)
```

Le seul moyen de _lever_ les erreurs collectées. Si l'on ne l'appelle pas, le résultat est silencieux (utile pour les cas où on veut accéder à `.errors` manuellement).

## `AggregateInvariantViolationError`

```python
def __init__(self, errors: Sequence[InvariantViolationError]) -> None:
    self.errors = errors
    count = len(errors)
    is_plural = count > 1
    if is_plural:
        message = f"{count} invariant violations occurred:\n" + "\n".join(f"› {e}" for e in errors)
    else:
        message = "Invariant violation occurred:\n" + "\n".join(f"› {e}" for e in errors)
    super().__init__(message)
```

Mise en forme&nbsp;: singulier _ou_ pluriel automatique («&nbsp;_1 invariant violation occurred_&nbsp;» vs «&nbsp;_3 invariant violations occurred_&nbsp;»).

## Exemple

```python
from ocarina.dsl.invariants.validate import validate
from ocarina.dsl.invariants.assertions import is_str, is_email

validate(email, name="email")
    .assert_that(is_str)
    .assert_that(is_email)
    .execute()
    .raise_if_invalid()
```

- `email` est validé _deux_ fois (les deux assertions sont jouées).
- Si _les deux_ échouent&nbsp;: un `AggregateInvariantViolationError` est levé avec **les deux messages**.
- Si _aucune_ n'échoue&nbsp;: `.raise_if_invalid()` est un no-op.

## CLI

Le validateur de la CLI utilise ce DSL&nbsp;:

```python
# create_cli_store.py
"workers": field(
    validate=lambda chain: chain.assert_that(is_positive, msg="--workers should be a positive value")
                                .assert_that(is_not_zero, msg="--workers should not be zero")
),
```

Et dans `CliStore.set` (`store.py`)&nbsp;:

```python
def set(self, value: T) -> None:
    if not isinstance(self._value, _Unset):
        raise RuntimeError("Value already set.")
    self._validate(_validate(value)).execute().raise_if_invalid()
    self._value = value
```

C'est **le même** DSL. Pas de validation _ad hoc_, pas de système parallèle. La composition d'invariants est l'unique langage d'expression de la validation dans tout le framework.

## Utilisation par les `custom_invariants/testing/`

```python
# custom_invariants/testing/workers.py
def _workers_amount_chain(chain: ValidationStartBlock[int], value: int) -> ValidationAssertBlock[int]:
    msg = f"Value Error: Number of workers must be at least 1 (got: {value})."
    return chain.assert_that(is_positive, msg=msg).assert_that(is_not_zero, msg=msg)

def validate_workers_amount(*, workers_amount: int, name: str) -> ValidationAssertBlock[int]:
    return FrameworkInvariantValidator.create(workers_amount, name, _workers_amount_chain)
```

Et dans `TestSuite.run`&nbsp;:

```python
validate_workers_amount(workers_amount=max_workers, name="max_workers").execute().raise_if_invalid()
```

Avant que la pool ne soit warmed-up, avant qu'aucun thread ne démarre, on _refuse_ proprement un `max_workers <= 0`.
