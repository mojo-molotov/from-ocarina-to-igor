---
title: "02.04.06 — Hiérarchie d'erreurs des invariants"
description: "La hiérarchie d'erreurs des invariants d'Ocarina : InvariantViolationError, DuplicatesError et AggregateInvariantViolationError."
weight: 6
date: 2026-05-20
series: ["invariants"]
series_order: 6
tags: ["ocarina"]
---

# 02.04.06&nbsp;—&nbsp;Hiérarchie d'erreurs des invariants

> Fichier source&nbsp;: [`src/ocarina/dsl/invariants/errors.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/errors.py)

```
InvariantViolationError (base — sous-classe d'Exception)
├── DuplicatesError                  (levée par `has_unique_elements`)
└── AggregateInvariantViolationError (levée par `_ValidationResult.raise_if_invalid`)
```

## `InvariantViolationError`

```python
class InvariantViolationError(Exception):
    """Base exception raised when an invariant is violated."""
```

Une simple sous-classe d'`Exception` sans logique propre. Tous les prédicats lèvent cette classe (ou une sous-classe).

```python
try:
    validate(value).assert_that(predicate).execute().raise_if_invalid()
except InvariantViolationError as e:
    logger.error(f"Validation failed: {e}")
```

… attrape **toutes** les violations en une seule clause.

## `DuplicatesError`

```python
class DuplicatesError(InvariantViolationError):
    def __init__(self, duplicates: Sequence[Any], message: str | None = None) -> None:
        self.duplicates = duplicates
        msg = message or "Duplicate elements detected:\n" + "\n".join(
            f" - {d}" for d in duplicates
        )
        super().__init__(msg)
```

- Stocke la liste des doublons dans `.duplicates`.
- Génère un message «&nbsp;_Duplicate elements detected:`\n` - apple`\n` - banana_&nbsp;» par défaut.
- Accepte un `message=` custom.

Levée par [`has_unique_elements`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/invariants/assertions.py)

## `AggregateInvariantViolationError`

```python
class AggregateInvariantViolationError(InvariantViolationError):
    def __init__(self, errors: Sequence[InvariantViolationError]) -> None:
        self.errors = errors
        count = len(errors)
        is_plural = count > 1
        if is_plural:
            message = f"{count} invariant violations occurred:\n" + "\n".join(
                f"› {e}" for e in errors
            )
        else:
            message = "Invariant violation occurred:\n" + "\n".join(
                f"› {e}" for e in errors
            )
        super().__init__(message)
```

1. **Singulier/pluriel automatique**. «&nbsp;_1 invariant violation occurred_&nbsp;» vs «&nbsp;_3 invariant violations occurred_&nbsp;».
2. **Préfixe `›`** (U+203A). Le `# noqa: RUF001 -> This is intentional.` dans le code le signale&nbsp;: ruff alerte sur ce caractère unicode qui pourrait être confondu avec `>`, l'auteur dit que c'est volontaire (le `›` est plus discret visuellement).
3. **Accès aux erreurs originales** via `.errors`.

## Cycles complets d'échecs d'invariants

### Cas 1&nbsp;—&nbsp;Échec d'un prédicat

```
validate(workers_amount, name="max_workers")
    .assert_that(is_positive, msg="Number of workers must be at least 1.")
    .assert_that(is_not_zero, msg="Number of workers must be at least 1.")
    .execute()
    .raise_if_invalid()

  ┌─ workers_amount = 0
  │     │
  │     ▼ .assert_that(is_positive, msg=...)
  │  _ValidationChain.add_assertion(0, _PredicateWithMsg(is_positive, "..."), "max_workers")
  │     │
  │     ▼ .assert_that(is_not_zero, msg=...)
  │  _ValidationChain.add_assertion(0, _PredicateWithMsg(is_not_zero, "..."), "max_workers")
  │     │
  │     ▼ .execute()
  │  _ValidationChain.execute() :
  │     - step 1 : is_positive(0)        → OK (0 >= 0)
  │     - step 2 : is_not_zero(0)        → LÈVE → InvariantViolationError("max_workers: ...")
  │     - errors = [exc1] ; is_valid = False
  │     │
  │     ▼ .raise_if_invalid()
  │  raise AggregateInvariantViolationError([exc1])
  └─► "Invariant violation occurred:\n› max_workers: Number of workers must be at least 1."
```

### Cas 2&nbsp;—&nbsp;Échec d'`otherwise` (toutes les branches `_any_of` échouent)

```
validate(age, name="age")
    .assert_that(is_equal_to(18), msg="Must be exactly 18")
    .otherwise(is_less_than_or_equal_to(65), msg="Or must be 65 or younger")
    .execute()
    .raise_if_invalid()

  ┌─ age = 70
  │     │
  │     ▼ .otherwise(...) → combined = _any_of(is_equal_to(18), is_less_than_or_equal_to(65))
  │     ▼ .execute()
  │     - step combiné(70) :
  │           is_equal_to(18)(70)              → LÈVE
  │           is_less_than_or_equal_to(65)(70) → LÈVE
  │           toutes échouent → InvariantViolationError("All predicates failed for value 70...")
  │     - errors = [exc_combined] ; is_valid = False
  │     │
  │     ▼ .raise_if_invalid()
  └─► "Invariant violation occurred:\n› age: All predicates failed for value 70.
       » At least one of the following conditions must be satisfied:
         | age: Must be exactly 18
         | age: Or must be 65 or younger"
```

### Cas 3&nbsp;—&nbsp;Échec agrégé sur plusieurs valeurs via `.then(...)`

```
validate(user, name="user")
    .assert_that(is_not_none)
    .then(user.email, name="user.email")
    .assert_that(is_email)
    .then(user.age, name="user.age")
    .assert_that(is_positive)
    .execute()
    .raise_if_invalid()

  ┌─ user = User(email="not-an-email", age=-3)
  │     │
  │     ▼ .execute() (chain partagée entre tous les blocks)
  │     - step 1 : is_not_none(user)               → OK
  │     - step 2 : is_email("not-an-email")        → LÈVE  (exc_email)
  │     - step 3 : is_positive(-3)                 → LÈVE  (exc_age)
  │     - errors = [exc_email, exc_age] ; is_valid = False
  │     │
  │     ▼ .raise_if_invalid()
  └─► "2 invariant violations occurred:
       › user.email: 'not-an-email' must contain exactly one '@' character.
       › user.age: -3 is not positive."
```

## Lien avec la taxonomie Allure

> Note&nbsp;: la taxonomie Allure ci-dessous concerne **les tests unitaires internes d'Ocarina** (couvrant le framework lui-même). Elle n'est pas destinée aux utilisateurs du framework, mais ces derniers peuvent **éventuellement s'en inspirer** pour leurs propres rapports.

`categories.json` (cf. [`../01-identity.md`](../01-identity.md))&nbsp;:

```json
{
  "name": "Invariant violations",
  "matchedStatuses": ["failed"],
  "messageRegex": ".*InvariantViolationError.*"
}
```

Tout test interne qui lève (directement ou via agrégation) un `InvariantViolationError` est rangé dans la catégorie Allure **Invariant violations**. On les retrouve d'un coup d'œil dans le rapport HTML.

## Pourquoi pas un `assert` ou un `ValueError`&nbsp;?

1. **`assert`** peut être désactivé par `python -O`. Inacceptable pour de la validation runtime.
2. **`ValueError`** est trop large&nbsp;: on attraperait par accident des erreurs venues d'ailleurs (par exemple de `Path(...)` qui lève `ValueError` pour un chemin invalide).
3. Une classe dédiée permet de **catcher** spécifiquement et de la **router** vers la catégorie Allure dédiée.

## Levée _explicite_ d'un `InvariantViolationError`

```python
def is_my_business_rule(value: str) -> None:
    if not _my_check(value):
        raise InvariantViolationError(f"'{value}' violates rule X.")
```

C'est la seule exception qu'on est censé lever. Toute autre exception _sortant_ d'un prédicat sera _propagée et non agrégée_, ce qui casse l'invariant d'agrégation. Donc&nbsp;: si on écrit un prédicat, on **catch** ce qui doit l'être et on **repropage** en `InvariantViolationError`.
