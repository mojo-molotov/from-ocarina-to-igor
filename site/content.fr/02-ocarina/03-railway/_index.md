---
title: "Chapitre 02.03 — Railway Oriented Programming"
description: "Le Railway Oriented Programming au cœur d'Ocarina : succès et échec comme deux rails parallèles, court-circuit, et composition syntaxique lisible."
weight: 3
date: 2026-05-20
tags: ["ocarina", "rop"]
sidebar:
  open: true
---

# Chapitre 02.03&nbsp;—&nbsp;Railway Oriented Programming

> Le cœur d'Ocarina. Tout le DSL repose sur cette mécanique&nbsp;: représenter le succès et l'échec comme deux _rails parallèles_, faire qu'un échec _bascule_ le train sur le rail d'échec, et l'y fait rester (court-circuit), préserver la composition syntaxique pour que le scénario reste lisible.

## Plan

|  #  | Fichier                                                  | Sujet                                                                                                           |
| :-: | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-result.md`](01-result.md)                           | `Result[T] = Ok[T] \| Fail`, `is_ok`/`is_fail`                                                                  |
| 02  | [`02-action-chain-states.md`](02-action-chain-states.md) | Machine à états `ActionStart → ActionFailure → ActionSuccess → ActionChain`.                                    |
| 03  | [`03-neutral-rail.md`](03-neutral-rail.md)               | Rail d'échec&nbsp;: `NeutralActionStart`&nbsp;/&nbsp;`NeutralActionFailure`&nbsp;/&nbsp;`NeutralActionSuccess`. |
| 04  | [`04-chain-actions-fold.md`](04-chain-actions-fold.md)   | `ChainRunner[T]` (thunk) + `chain_actions` (fold).                                                              |
| 05  | [`05-create-act-hooks.md`](05-create-act-hooks.md)       | `create_act` et ses hooks (`on_failure`, `on_run_effect`, `act_counter_effect`).                                |
| 06  | [`06-drive-page.md`](06-drive-page.md)                   | `drive_page`, alias sémantique.                                                                                 |
| 07  | [`07-match-page-when.md`](07-match-page-when.md)         | `match_page` /&nbsp;`when` + politique d'exceptions.                                                            |

## Filiation

L'inspiration directe est le **Railway Oriented Programming** popularisé par Scott Wlaschin (F#).

> Tordre l'implémentation de ROP (_Railway Oriented Programming_) d'Ocarina jusqu'à lui en faire perdre tout son sens, puisqu'ils ne savaient même pas ce que signifie ROP.

L'implémentation Python d'Ocarina est **faite respectueusement**&nbsp;:&nbsp;elle ajoute la _machine à états du builder_ (_Typestate Pattern_), le _rail d'échec neutralisé_, et la _composition paresseuse_ via `ChainRunner`. Voir [`02-action-chain-states.md`](02-action-chain-states.md) pour la mécanique complète.

## Métaphore reprise du module

Extrait du docstring de `action_chain.py`&nbsp;:

> **Railway metaphor**:
>
> Code as railway track with two rails:
>
> - Success rail (top): Actions execute normally&nbsp;→&nbsp;Ok results
> - Failure rail (bottom): Action failed&nbsp;→&nbsp;Fail results
>
> When an action fails, the train switches to the failure rail and stays there (short-circuits). Subsequent actions become no-ops.

```
                       act1           act2           act3
                        │              │              │
                        ▼              ▼              ▼
Success rail  ─────[ EXECUTE ]────[ EXECUTE ]────[ EXECUTE ]─────┐
                        │                                        │
                        │ (fail → switch)                        ├──►  Result
                        ▼                                        │
Failure rail  ─────[  NO-OP  ]────[  NO-OP  ]────[  NO-OP  ]─────┘

Deux rails parallèles, mêmes étapes. Si act1 échoue, le train bascule sur
le rail d'échec et y reste : les actes suivants restent appelables (l'API
.failure/.success/.execute existe), mais ils ne font rien (no-op).
```

## Pourquoi ROP plutôt que `try/except`

| Aspect                           | `try/except` classique                                    | ROP                                                  |
| -------------------------------- | --------------------------------------------------------- | ---------------------------------------------------- |
| Propagation de l'échec           | Implicite (l'exception remonte)                           | Explicite (la valeur `Fail` découle)                 |
| Vérification par le type-checker | Impossible (toutes les exceptions sont possibles partout) | Forte (`Result[T]` est une union discriminée)        |
| Composition                      | Imbrication (`try { … try { … } }`)                       | Linéaire (`.then().then().then()`)                   |
| Court-circuit                    | Manuel (`if exc: return`)                                 | Automatique (rail d'échec)                           |
| Handlers                         | Couplés à un `except` proche                              | Découplés (`.failure(handler)`, `.success(handler)`) |

Conséquence pratique&nbsp;: **le nombre de `try/except` dans le code projet chute drastiquement**. L'utilisateur ne ressent plus la pression de prévoir «&nbsp;_tous les `try/except` possibles et imaginables_&nbsp;», il reprend le contrôle sur _pourquoi_ il voudrait en utiliser un, dans les rares cas où ça reste pertinent.

## Le contrat global du DSL

| Primitive                          | Type de retour        | Lisibilité                                       |
| ---------------------------------- | --------------------- | ------------------------------------------------ |
| `act(pom, action)`                 | `ActionStart[TPOM]`   | «&nbsp;_je commence un pas_&nbsp;»               |
| `.failure(h)`                      | `ActionFailure[TPOM]` | «&nbsp;_sur l'échec, fais h_&nbsp;»              |
| `.success(h')`                     | `ActionSuccess[TPOM]` | «&nbsp;_sur le succès, fais h'_&nbsp;»           |
| `.execute()`                       | `ActionChain[TPOM]`   | «&nbsp;_exécute le pas_&nbsp;»                   |
| `drive_page(act1, act2, …)`        | `ChainRunner[TPOM]`   | «&nbsp;_je prends le contrôle d'une page_&nbsp;» |
| `match_page(branches=[when(...)])` | `ChainRunner[Any]`    | «&nbsp;_je branche selon l'état observé_&nbsp;»  |

Tout `scenario.test_chain` est une `Sequence[ChainRunner[Any]]`. Tout point d'extension utilisateur (un nouveau combinateur, un `skip_if`, etc.) doit retourner un `ChainRunner`. Voir [`../06-scenario.md`](../06-scenario.md) et [`../../03-functional/`](../../03-functional/README.md)
