---
title: "Chapitre 02.04 — Invariants"
description: "Sous-DSL d'Ocarina dédié à l'expression d'invariants typés et composables. Utilisé partout : par la CLI, par les POMs, par les custom_invariants/testing/ qui valident la cohérence des suites avant exécution."
weight: 4
date: 2026-05-20
tags: ["ocarina", "rop", "invariants"]
sidebar:
  open: true
---

# Chapitre 02.04&nbsp;—&nbsp;Invariants

> Sous-DSL d'Ocarina dédié à l'expression d'invariants typés et composables. Utilisé partout&nbsp;:&nbsp;par la CLI, par les POMs, par les `custom_invariants/testing/` qui valident la cohérence des suites avant exécution.

## Plan

|  #  | Fichier                                                                          | Sujet                                                                                                                                   |
| :-: | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-validate-flow.md`](01-validate-flow.md)                                     | Le flot complet `validate(value) → assert_that → execute → raise_if_invalid` + la classe `_ValidationChain`.                            |
| 02  | [`02-assertions.md`](02-assertions.md)                                           | Catalogue des assertions builtin (`is_str`, `is_email`, `is_positive`, `is_in`, `has_unique_elements`, `each`, `is_valid_filename`, …). |
| 03  | [`03-otherwise-any-of.md`](03-otherwise-any-of.md)                               | `.otherwise(...)` et la combinaison OR via `_any_of`.                                                                                   |
| 04  | [`04-then-chain-of-validations.md`](04-then-chain-of-validations.md)             | `.then(new_value)` et `chain_validations(...)` pour la composition.                                                                     |
| 05  | [`05-business-vs-framework-validator.md`](05-business-vs-framework-validator.md) | `BusinessInvariantValidator` vs `FrameworkInvariantValidator`                                                                           |
| 06  | [`06-invariant-errors.md`](06-invariant-errors.md)                               | `InvariantViolationError`, `DuplicatesError`, `AggregateInvariantViolationError`.                                                       |

## Le pourquoi du DSL d'invariants

1. **Garde-fou avant exécution.** `TestSuite.__init__` valide _avant_ de lancer quoi que ce soit que les noms /&nbsp;IDs des tests sont uniques, que `max_workers >= 1`, etc.
2. **Validation CLI.** Chaque flag a son `validate=lambda chain: chain.assert_that(...)` dans le `CliStore`. Les erreurs s'agrègent et sortent en un seul message d'erreur.
3. **Validation côté POM.** Les actions de POM peuvent valider leurs paramètres («&nbsp;_`retries` doit être positif_&nbsp;») via `validate(retries, name="retries").assert_that(is_positive).execute().raise_if_invalid()`.

Le Holy Book le résume&nbsp;:

> Utilisable dans les POMs, `validate` permet d'exprimer des invariants sous forme de chaînes. L'exécution est **différée**&nbsp;: il faut appeler `.execute()` explicitement.
>
> Le résultat expose `is_valid`, `errors` et `validated_values`. Il est inerte par défaut. `.raise_if_invalid()` remonte l'exception si besoin.

## Principes de conception

| Principe               | Réalisation                                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Exécution différée** | `.execute()` est obligatoire. Avant ça, la chaîne est composable mais inerte.                                       |
| **Erreurs agrégées**   | `_ValidationChain` exécute tous les steps et collecte les erreurs&nbsp;; pas de _fail-fast_.                        |
| **Composition typée**  | `.then(U)` change de type&nbsp;; le `T` est conservé dans la chaîne.                                                |
| **OR logique**         | `.otherwise(pred)` combine avec le précédent via `_any_of`.                                                         |
| **Type safety**        | `validate("lol").assert_that(is_positive)` provoque une erreur _mypy_ (prédicat incompatible).                      |
| **Réutilisabilité**    | `BusinessInvariantValidator.create(...)` ou `FrameworkInvariantValidator.create(...)` pour factoriser un invariant. |

## Lien fort avec ROP

Le sous-DSL invariants **suit la même grammaire** que ROP&nbsp;:

| ROP                                                                                               | Invariants                                                                             |
| ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `ActionStart[T]`&nbsp;→&nbsp;`ActionFailure[T]` →&nbsp;`ActionSuccess[T]` →&nbsp;`ActionChain[T]` | `ValidationStartBlock[T]` →&nbsp;`ValidationAssertBlock[T]` →&nbsp;`_ValidationResult` |
| Composition flat via `chain_actions(*)`                                                           | Composition flat via `chain_validations(*)`                                            |
| Évaluation paresseuse (`Thunk[ActionChain[T]]`)                                                   | Évaluation paresseuse (`.execute()`)                                                   |
| `Result[T]`                                                                                       | `_ValidationResult` (avec `is_valid`, `errors`, `validated_values`)                    |
| Erreur agrégée par `Fail`                                                                         | Erreur agrégée par `AggregateInvariantViolationError`                                  |

C'est **le même pattern** appliqué à un autre domaine. Voir [`../03-railway/`](../03-railway/README.md) pour le pattern d'origine.
