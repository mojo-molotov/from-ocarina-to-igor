---
title: "02.04.04 — .then(...) et chain_validations(...)"
description: "then et chain_validations : deux mécanismes pour composer plusieurs validations, changer le type validé et conserver la chaîne d'assertions."
weight: 4
date: 2026-05-20
series: ["invariants"]
series_order: 4
tags: ["ocarina"]
---

# 02.04.04&nbsp;—&nbsp;`.then(...)` et `chain_validations(...)`

> Deux mécanismes différents pour composer plusieurs validations en une seule.

## `.then(new_value)`

```python
def then[U](self, new_value: U, *, name: str | None = None) -> ValidationStartBlock[U]:
    return ValidationStartBlock(new_value, self._chain, name)
```

1. **Change le type** de `T` à `U`. Le checker accepte le passage à un autre type.
2. **Conserve la chaîne** (`self._chain`). Toutes les assertions précédentes restent dans la chaîne&nbsp;; toutes les suivantes _s'ajoutent_ à la chaîne.
3. **Bascule le `name`**&nbsp;: c'est le `name` fourni à `.then()` qui sera utilisé pour les assertions ajoutées ensuite (et non celui du block précédent).

### Cas d'usage canonique

```python
validate(user, name="user")
    .assert_that(is_not_none)
    .then(user.email, name="user.email")
    .assert_that(is_email)
    .then(user.age, name="user.age")
    .assert_that(is_positive)
    .assert_that(is_less_than_or_equal_to(120))
    .execute()
    .raise_if_invalid()
```

Lecture&nbsp;: on valide `user` puis `user.email` puis `user.age`. Si _toutes_ ces validations passent&nbsp;: OK. Si ne serait-ce qu'_une seule_ échoue, toutes les erreurs sont agrégées dans le `AggregateInvariantViolationError`.

Avantage&nbsp;: un seul `.execute()`, un seul message d'erreur, une seule propagation. Pas besoin d'écrire trois `validate(...).execute().raise_if_invalid()`.

### Subtilité

Le `_chain` est **partagé par référence** entre tous les blocks. C'est volontaire&nbsp;:

> The validation chain accumulator is mutable and shared across blocks in the same chain&nbsp;; blocks hold a reference to it, not a copy.

(Extrait du _docstring_ d'introduction de `validation_chain.py`.)

C'est ce qui permet d'utiliser `.then()` proprement&nbsp;: on n'a pas à recombiner après coup.

## `chain_validations(*)`

```python
def chain_validations(
    first: ValidationAssertBlock[Any],
    *rest: ValidationAssertBlock[Any],
) -> ValidationAssertBlock[Any]:
    merged_chain = _ValidationChain()
    merged_chain._merge_chain(first._chain)
    for block in rest:
        merged_chain._merge_chain(block._chain)
    return ValidationAssertBlock(first._value, merged_chain, first._name)
```

1. **Crée une nouvelle chaîne**. Pas de mutation des chaînes en argument.
2. **Merge dans l'ordre**&nbsp;: tous les steps de la première chaîne, puis tous les steps de la seconde, puis de la troisième, etc.
3. **Retourne un `ValidationAssertBlock`**&nbsp;: on peut appeler `.execute()` dessus.

### Cas d'usage

```python
# Exemple libre : validations indépendantes pré-construites
user_validation = validate(user, name="user").assert_that(is_not_none)
email_validation = validate(email, name="email").assert_that(is_email)
age_validation = validate(age, name="age").assert_that(is_positive)

chain_validations(user_validation, email_validation, age_validation).execute().raise_if_invalid()
```

```python
# Dans TestCycle.__init__
chain_validations(
    validate_test_cycle_name(cycle_name=name, name="test_cycle"),
    validate_campaigns_names(campaigns=all_campaigns, name="all campaigns (smoke + deep tests)"),
    validate_test_suites_names(suites=campaign._suites, name="suites"),
    validate_test_runners_names(tests=suite._tests, name="tests"),
).execute().raise_if_invalid()
```

## `.then()` vs `chain_validations(*)`

| Critère          | `.then()`                                                      | `chain_validations()`                                                                                              |
| ---------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Quand l'utiliser | Plusieurs valeurs **liées** (`user`, `user.email`, `user.age`) | Plusieurs validations **indépendantes** déjà construites                                                           |
| Style            | Linéaire dans une chaîne                                       | Composition après-coup                                                                                             |
| Mutation         | Mute la chaîne sous-jacente                                    | Crée une nouvelle chaîne (pas de mutation)                                                                         |
| Type de retour   | `ValidationStartBlock[U]`                                      | `ValidationAssertBlock[Any]`                                                                                       |
| Cas d'usage      | Validation d'une dataclass et de ses champs                    | Validation des invariants framework au constructeur d'un `TestCycle`, ou validation d'un invariant métier complexe |

## Tests de type

[`tests/dsl/invariants/test_types.yml`](https://github.com/mojo-molotov/ocarina/blob/main/tests/dsl/invariants/test_types.yml) contient&nbsp;:

```yaml
- case: then_allows_type_change
  description: .then() should allow switching to a different type in the validation chain
  main: |
    validate(42).assert_that(is_positive).then("email@test.com").assert_that(is_email)
```

Le checker accepte de passer d'`int` à `str` _via_ `.then()`, mais refuse une assertion incompatible avec le type courant&nbsp;:

```python
validate(42).assert_that(is_email)
#                        ^^^^^^^^
# error: Argument 1 to "assert_that" has incompatible type
#   "Callable[[str], None]"; expected "Callable[[int], None]"
```
