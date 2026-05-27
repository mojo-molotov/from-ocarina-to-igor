---
title: "02.04.03 — .otherwise(...) et _any_of"
description: "Comment Ocarina exprime un OR logique entre deux prédicats sans casser l'agrégation d'erreurs."
weight: 3
date: 2026-05-20
series: ["invariants"]
series_order: 3
tags: ["ocarina"]
---

# 02.04.03&nbsp;—&nbsp;`.otherwise(...)` et `_any_of`

> Comment Ocarina exprime un **OR logique** entre deux prédicats sans casser l'agrégation d'erreurs.

## Le problème

Cas concret&nbsp;: on veut «&nbsp;_`age == 18` OR `age <= 65`_&nbsp;». La syntaxe ROP/invariants est strictement chaîne d'assertions&nbsp;; chaque `.assert_that()` est un AND. Comment exprimer un OR&nbsp;?

## Code

```python
def otherwise(self, fallback: Predicate[T], *, msg: str | None = None) -> ValidationAssertBlock[T]:
    if self._last_predicate is None:
        raise RuntimeError("otherwise() must follow assert_that().")

    fallback_with_msg = _with_msg(fallback, msg, self._name)
    combined = _any_of(
        self._last_predicate, *([*self._otherwise_predicates, fallback_with_msg])
    )
    self._chain._steps.pop()                    # remplace le dernier step
    self._chain.add_assertion(self._value, combined, self._name)
    self._last_predicate = combined
    self._otherwise_predicates.append(fallback_with_msg)
    return self
```

1. **Guard**. `otherwise()` doit suivre un `assert_that()`. Sans prédicat précédent, on lève. (En pratique, le type-checker l'interdit déjà&nbsp;: `ValidationStartBlock.otherwise` n'existe pas.)
2. **Combinaison**. On combine le prédicat précédent + tous les `otherwise` déjà accumulés + le nouveau, via `_any_of`. Le résultat est un prédicat composite.
3. **Remplacement du step**. On _pop_ le dernier step du `_ValidationChain` et on _push_ le step combiné. Sans ça, on aurait à la fois le prédicat original ET le combiné, donc l'erreur originale resurgirait.

## `_any_of`

```python
def _any_of[T](*predicates: _PredicateWithMsg[T]) -> _PredicateWithMsg[T]:
    def _try_predicate(p: _PredicateWithMsg[T], value: T) -> InvariantViolationError | None:
        try:
            p(value)
        except InvariantViolationError as exc:
            return exc
        else:
            return None

    def combined(value: T) -> None:
        errors = []
        for p in predicates:
            error = _try_predicate(p, value)
            if error is None:
                return                              # ✅ un prédicat passe → tout passe
            errors.append(error)

        formatted_error_messages = "  | " + "\n  | ".join(str(e) for e in errors)
        msg = (
            f"All predicates failed for value {value!r}.\n"
            "» At least one of the following conditions must be satisfied:\n"
            f"{formatted_error_messages}"
        )
        raise InvariantViolationError(msg)

    return _PredicateWithMsg(combined)
```

1. **First success wins**&nbsp;: dès qu'un prédicat passe, `combined` retourne `None` (succès).
2. **Si tous échouent**&nbsp;: on construit un message _agrégé_ listant **toutes** les raisons d'échec, séparées par `|`
3. **Le résultat est un `_PredicateWithMsg`**&nbsp;: on peut le rebrancher dans la chaîne comme n'importe quel autre prédicat.
4. **L'agrégation est récursive**&nbsp;: si on a 3 `otherwise()` successifs, le 3e combine `(P_orig OR P_otherwise1 OR P_otherwise2 OR P_otherwise3)` en un seul prédicat.

## Exemple

```python
validate(age, name="age")
    .assert_that(is_equal_to(18), msg="Must be 18 or at most 65")
    .otherwise(is_less_than_or_equal_to(65), msg="Must be 18 or at most 65")
    .execute()
    .raise_if_invalid()
```

1. Si `age == 18`&nbsp;: `is_equal_to(18)` passe&nbsp;→&nbsp;OK.
2. Si `age == 30`&nbsp;: `is_equal_to(18)` lève, `is_less_than_or_equal_to(65)` passe&nbsp;→&nbsp;OK.
3. Si `age == 70`&nbsp;: les deux lèvent&nbsp;→&nbsp;`InvariantViolationError` avec&nbsp;:

```
age: All predicates failed for value 70.
» At least one of the following conditions must be satisfied:
  | age: Must be 18 or at most 65
  | age: Must be 18 or at most 65
```

(Le doublon de message vient du fait qu'on a passé le même `msg=` aux deux&nbsp;; c'est volontaire ici, on _veut_ exprimer une intention unique.)

Pour un message d'erreur plus élégant (un seul énoncé du contrat, _diagnostiquant_ ce qui s'est passé), on peut dissocier les `msg=`&nbsp;:

```python
validate(age, name="age")
    .assert_that(is_equal_to(18), msg="Must be exactly 18")
    .otherwise(is_less_than_or_equal_to(65), msg="Can be 65 or younger")
    .execute()
    .raise_if_invalid()
```

`age == 70`&nbsp;:

```
age: All predicates failed for value 70.
» At least one of the following conditions must be satisfied:
  | age: Must be exactly 18
  | age: Can be 65 or younger
```

## Exemple multi-otherwise

```python
validate(age, name="age")
    .assert_that(is_equal_to(18), msg="Must be 18")
    .otherwise(is_equal_to(21), msg="Or must be 21")
    .otherwise(is_equal_to(65), msg="Or must be 65")
    .execute()
```

`age == 30`&nbsp;:

```
age: All predicates failed for value 30.
» At least one of the following conditions must be satisfied:
  | age: Must be 18
  | age: Or must be 21
  | age: Or must be 65
```

## Côté CLI

```python
"profile_path": field(
    validate=lambda chain: chain.assert_that(is_none, msg="Maybe you could omit --profile-path")
                                .otherwise(is_dir,    msg="--profile-path should be a path to a directory")
),
```

Lecture&nbsp;: `profile_path` est valide soit s'il vaut `None`, soit s'il pointe un répertoire.

## Tests de type associés

[`tests/dsl/invariants/test_types.yml`](https://github.com/mojo-molotov/ocarina/blob/main/tests/dsl/invariants/test_types.yml)&nbsp;:

```yaml
- case: otherwise_with_same_type
  description: .otherwise() should accept predicates of the same type
  main: |
    validate(5).assert_that(is_positive).otherwise(is_not_zero)

- case: multiple_otherwise_preserves_type
  description: Multiple .otherwise() calls should preserve the same type throughout
  main: |
    validate(5) \
        .assert_that(is_equal_to(10)) \
        .otherwise(is_equal_to(20)) \
        .otherwise(is_positive) \
        .otherwise(is_not_zero)
```

Le type est conservé tout au long. On ne peut pas mélanger un `Predicate[int]` avec un `Predicate[str]` dans la même chaîne.
