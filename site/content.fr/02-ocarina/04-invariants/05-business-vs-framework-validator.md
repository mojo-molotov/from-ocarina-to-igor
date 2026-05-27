---
title: "02.04.05 — BusinessInvariantValidator vs FrameworkInvariantValidator"
description: "Deux factories — strictement identiques en code — qui existent uniquement pour signaler l'intention."
weight: 5
date: 2026-05-20
series: ["invariants"]
series_order: 5
tags: ["ocarina"]
---

# 02.04.05&nbsp;—&nbsp;`BusinessInvariantValidator` vs `FrameworkInvariantValidator`

> Deux factories&nbsp;—&nbsp;strictement identiques en code&nbsp;—&nbsp;qui existent **uniquement pour signaler l'intention**.

## Code

```python
class _BaseCustomInvariantValidator:
    @staticmethod
    def create[T](
        value: T,
        name: str,
        build_chain: Callable[[ValidationStartBlock[T], T], ValidationAssertBlock[T]],
    ) -> ValidationAssertBlock[T]:
        return _create_business_invariant_validator(
            value, name, lambda chain: build_chain(chain, value)
        )


@final
class BusinessInvariantValidator(_BaseCustomInvariantValidator):
    """Factory for creating business domain invariant validators.

    Use this for domain-specific validation logic (e.g., "user must be adult",
    "order total must match items").
    """


@final
class FrameworkInvariantValidator(_BaseCustomInvariantValidator):
    """Factory for creating framework-level invariant validators.

    Use this for technical/framework validation logic (e.g., "config must be valid",
    "test structure must be correct").
    """
```

```python
def _create_business_invariant_validator[T](
    value: T,
    name: str,
    build_chain: ValidationChainBuilder[T],
) -> ValidationAssertBlock[T]:
    start_block = validate(value, name=name)
    return build_chain(start_block)
```

## Pourquoi deux classes&nbsp;?

1. `BusinessInvariantValidator` _signale_ qu'on valide une règle métier&nbsp;; `FrameworkInvariantValidator`, une règle technique du framework. À la lecture du code, l'intention saute aux yeux.
2. **Grep**. On peut chercher `FrameworkInvariantValidator.create` pour trouver _tous les invariants framework_. Idem pour les business rules côté projet.
3. **Maintenabilité**. Si l'on veut un jour ajouter du comportement (log différent, stack-trace différente) à l'une ou à l'autre, on peut le faire sans refactor de tous les call-sites.

## Usages

| Invariant                                                                                 | Catégorie | Où il vit                                                          |
| ----------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------ |
| `validate_workers_amount`                                                                 | Framework | `src/ocarina/custom_invariants/testing/workers.py`                 |
| `validate_test_runners_ids`                                                               | Framework | `src/ocarina/custom_invariants/testing/oc_test_runners_ids.py`     |
| `validate_test_runners_names`                                                             | Framework | `src/ocarina/custom_invariants/testing/oc_test_runners_names.py`   |
| `validate_test_suites_names`                                                              | Framework | `src/ocarina/custom_invariants/testing/oc_test_suites_names.py`    |
| `validate_test_campaigns_names`                                                           | Framework | `src/ocarina/custom_invariants/testing/oc_test_campaigns_names.py` |
| `validate_test_cycle_name`                                                                | Framework | `src/ocarina/custom_invariants/testing/oc_test_cycles_names.py`    |
| _Exemple métier_&nbsp;: «&nbsp;_l'username doit être l'un de la whitelist_&nbsp;»         | Business  | À écrire côté projet utilisateur                                   |
| _Exemple métier_&nbsp;: «&nbsp;_la date de réservation doit être future et < 1 an_&nbsp;» | Business  | À écrire côté projet utilisateur                                   |

## Pattern complet

```python
# src/ocarina/custom_invariants/testing/workers.py
from ocarina.dsl.invariants.assertions import is_not_zero, is_positive
from ocarina.dsl.invariants.validate import FrameworkInvariantValidator


def _workers_amount_chain(
    chain: ValidationStartBlock[int],
    value: int,
) -> ValidationAssertBlock[int]:
    msg = f"Value Error: Number of workers must be at least 1 (got: {value})."
    return chain.assert_that(is_positive, msg=msg).assert_that(is_not_zero, msg=msg)


def validate_workers_amount(
    *, workers_amount: int, name: str
) -> ValidationAssertBlock[int]:
    """Validate that workers amount is at least 1."""
    return FrameworkInvariantValidator.create(
        workers_amount, name, _workers_amount_chain
    )
```

1. Une fonction privée `_workers_amount_chain(chain, value) -> ValidationAssertBlock` qui définit le _quoi_.
2. Une fonction publique `validate_workers_amount(*, workers_amount, name)` qui fournit l'API et délègue à `FrameworkInvariantValidator.create`.
3. Utilisation côté `TestSuite.run`&nbsp;: `validate_workers_amount(...).execute().raise_if_invalid()`.

## Quelle factory pour quel cas

Holy Book (extrait du chapitre «&nbsp;_Extensibilité_&nbsp;»)&nbsp;:

> Convention&nbsp;: `FrameworkInvariantValidator.create` pour les invariants techniques, `BusinessInvariantValidator.create` pour le métier.

| Règle                                                             | Catégorie             |
| ----------------------------------------------------------------- | --------------------- |
| «&nbsp;`max_workers >= 1`&nbsp;»                                  | Framework (technique) |
| «&nbsp;_tous les noms de tests sont uniques_&nbsp;»               | Framework             |
| «&nbsp;`DASH_PASSWORD` ne doit pas être vide&nbsp;»               | Business              |
| «&nbsp;_la date de réservation doit être une date future_&nbsp;»  | Business              |
| «&nbsp;_`user.email` matche le pattern interne entreprise_&nbsp;» | Business              |

## Règle tacite&nbsp;: ne pas mélanger

Le checker n'empêche pas de mélanger&nbsp;; la convention le déconseille. Si un invariant valide à la fois une règle métier et une règle technique, le mieux est de le **scinder** en deux invariants. Cela permet d'avoir des messages d'erreur plus précis (et plus actionnables) en cas d'échec agrégé.
