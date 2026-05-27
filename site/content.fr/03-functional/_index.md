---
title: "Chapitre 03 — Programmation fonctionnelle avec Ocarina"
description: "Comment Ocarina applique la programmation fonctionnelle, et pourquoi ces choix sont structurants. Ce chapitre est plus transversal que les autres : il revisite la mécanique du framework sous l'angle FP."
weight: 4
date: 2026-05-20
tags: ["fonctionnel"]
sidebar:
  open: true
---

# Chapitre 03&nbsp;—&nbsp;Programmation fonctionnelle avec Ocarina

> Comment Ocarina **applique** la programmation fonctionnelle, et **pourquoi**. Ce chapitre est plus _transversal_ que les autres&nbsp;: il revisite la mécanique du framework sous l'angle FP.

## Plan

|  #  | Fichier                                                                          | Sujet                                                                                  |
| :-: | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 01  | [`01-effect-thunk-result.md`](01-effect-thunk-result.md)                         | `Effect`, `Thunk[T]`, `Result[T]`.                                                     |
| 02  | [`02-closures-ioc.md`](02-closures-ioc.md)                                       | Closures comme primitive d'inversion de contrôle.                                      |
| 03  | [`03-lazy-evaluation.md`](03-lazy-evaluation.md)                                 | Paresse partout&nbsp;: ChainRunner, validate.execute, Watcher callback, lazy prefixes. |
| 04  | [`04-fold-reduce.md`](04-fold-reduce.md)                                         | `reduce` (fold left) dans `chain_actions`.                                             |
| 05  | [`05-declarative.md`](05-declarative.md)                                         | Programmation déclarative&nbsp;: un scénario _décrit_, n'exécute pas.                  |
| 06  | [`06-pep-695-generics.md`](06-pep-695-generics.md)                               | Generics PEP 695, `TypeVar bound`, `type X[T] = ...`.                                  |
| 07  | [`07-discriminated-unions-typeguards.md`](07-discriminated-unions-typeguards.md) | Unions discriminées + `TypeGuard` + `@final` = unions «&nbsp;_sealed_&nbsp;».          |

## Pourquoi un chapitre dédié

Le code d'Ocarina est petit, mais il **incarne** un nombre considérable de patterns FP. Ce chapitre est l'occasion de les nommer, de les justifier, et de pointer où est-ce qu'ils se manifestent dans le code.

Citation du Holy Book&nbsp;:

> _Tordre l'implémentation de ROP (Railway Oriented Programming) d'Ocarina jusqu'à lui en faire perdre tout son sens, puisqu'ils ne savaient même pas ce que signifie ROP_, …
> _M'imposer leur incompréhension de l'évaluation paresseuse et de l'IoC comme des vérités absolues_, …
> _M'expliquer ce que sont la programmation impérative et déclarative en racontant n'importe quoi_, …
