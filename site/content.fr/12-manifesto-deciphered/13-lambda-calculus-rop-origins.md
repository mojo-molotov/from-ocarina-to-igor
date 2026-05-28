---
title: "12.13 — Lambda-calcul, ROP, Haskell / F# / OCaml, monades"
description: "Les origines théoriques d'Ocarina : du lambda-calcul de Church aux monades de Moggi et Wadler, jusqu'au Railway Oriented Programming de Wlaschin."
weight: 13
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 13
tags: ["rop", "typage"]
---

# 12.13&nbsp;—&nbsp;Lambda-calcul, ROP, Haskell /&nbsp;F# /&nbsp;OCaml, monades

> Ocarina n'invente rien sur le plan théorique. Il **applique**&nbsp;:&nbsp;du **lambda-calcul** d'Alonzo Church (1936) aux **monades** d'Eugenio Moggi (1989) et Philip Wadler (1992-95), formalisé en tant que **Railway Oriented Programming** par Scott Wlaschin (2014).

## 1. Lambda-calcul (Church, 1936)

### Définition

Le **lambda-calcul** (λ-calcul) est un système formel inventé par **Alonzo Church** (1903-1995) pour étudier la **calculabilité**.

| Primitive       | Notation      | Sémantique                                            |
| --------------- | ------------- | ----------------------------------------------------- |
| **Variable**    | `x`, `y`, `z` | Un nom                                                |
| **Abstraction** | `λx.M`        | Définition d'une fonction de paramètre `x`, corps `M` |
| **Application** | `M N`         | Appel de la fonction `M` sur l'argument `N`           |

| Règle            | Effet                                                |
| ---------------- | ---------------------------------------------------- |
| **α-conversion** | Renommer une variable liée (`λx.x` ≡ `λy.y`)         |
| **β-réduction**  | Appliquer une fonction&nbsp;: `(λx.M) N → M[x := N]` |
| **η-conversion** | `λx.(f x) ≡ f` si `x` non libre dans `f`             |

### Pourquoi c'est fondateur

1. **1936**&nbsp;: Church prouve que le λ-calcul est **Turing-complet** (Turing publie sa machine en 1937). _Thèse Church-Turing_&nbsp;:&nbsp;tout ce qui est _calculable mécaniquement_ peut être exprimé en λ-calcul.
2. **Alan Turing** était le doctorant de Church à Princeton (PhD, 1938).
3. Le λ-calcul est **plus simple** que la machine de Turing&nbsp;:&nbsp;seulement 3 constructions. Tout le reste, entiers, booléens, structures de données, est _encodé_ avec ces 3 briques (encodage de Church).

### Lambda-calcul typé (Church, 1940)

Church ajoute des **types** en 1940 (_simply typed lambda calculus_, STLC) pour interdire les paradoxes d'auto-application (`λx.x x`). Chaque variable a un type, et l'application de fonction n'est autorisée que si les types matchent.

C'est l'**ancêtre direct** des types de Haskell, OCaml, F#, TypeScript, Python, Rust, etc.

### Curry-Howard (1934-1969)

**Haskell Curry** observe le lien en 1934 (puis le raffine en 1958) et **William Howard** l'étend en 1969&nbsp;:

> **Un programme typé _est_ une preuve mathématique.**  
> **Un type _est_ une proposition.**  
> **Le type-checker est un vérificateur de preuves.**

C'est l'**isomorphisme de Curry-Howard**.  
Si le code compile en étant strictement typé, il est **mathématiquement correct** sur les dimensions encodées par les types.

D'où `mypy --strict` dans Ocarina&nbsp;:&nbsp;ce n'est pas une obsession, ce n'est pas de l'autisme, c'est l'**application** du théorème Curry-Howard dans un cadre industriel.

## 2. ML (1973 à aujourd'hui)

### Robin Milner et ML (Edinburgh, 1973)

**Robin Milner** (1934-2010, Turing Award en 1991) conçoit **ML** (_Meta Language_) à Édimbourg comme langage de **preuves automatisées** (Edinburgh LCF&nbsp;—&nbsp;_Logic for Computable Functions_).

- **Hindley-Milner type system**&nbsp;:&nbsp;inférence de types complète sans annotations. Le compilateur _devine_ (infère) tous les types.
- **Pattern matching**&nbsp;:&nbsp;`match x with | Cons (h, t) -> ... | Nil -> ...`.
- **Polymorphism paramétrique**&nbsp;:&nbsp;`'a list` (liste de _n'importe quoi_).
- **Functions as first-class values**&nbsp;:&nbsp;passage d'une fonction comme argument.

### Généalogie ML

```
                      ML (Edinburgh, 1973)
                               │
             ┌─────────────────┼────────────────────┐
             │                 │                    │
             v                 v                    v
      Standard ML             Caml              Lazy ML
      (Milner, 1983)       (INRIA, 1985)     (Chalmers, ~1984)      SASL, KRC (Turner)
             │                 │                    │                       │
     ┌───────┤                 v                    │                       v
     │       │             Caml Light               │                    Miranda
   SML/NJ    │             (INRIA, 1990)            │                (Turner, 1985)
(Bell Labs & │                 │                    │                       │
 Princeton,  └──> Alice ML     │                    └───────────────────────┤
   1987)        (Saarland,     │                                            v
                  2000)        v                                         Haskell
                             OCaml                                 (SPJ, Wadler, 1990)
                       (Leroy, INRIA, 1996)                                 │
                               └────────────────────────────────────────────┤
                                                                            v
                                                                           F#
                                                                    (Don Syme, 2005)
                                                                            │
                                                                            │
                                                                           […]
                                                                            │
                                                                            │
                                                                            v
                                                               Railway Oriented Programming
                                                                (Wlaschin, NDC London, 2014)
                                                                            │
                                                                            v
                                                                 ┌───────────────────────┐
                                                                 │        Ocarina        │
                                                                 │    Casanova (2026)    │
                                                                 │  Python 3.14 · mypy   │
                                                                 │  Result[T]            │
                                                                 │  ChainRunner · fold   │
                                                                 │  action chain state   │
                                                                 └───────────────────────┘
```

> _Note&nbsp;:&nbsp;certaines dates indiquées correspondent aux débuts de conception._
>
> _Dates de première publication/implémentation&nbsp;:_
>
> - _ML&nbsp;→&nbsp;1979_
> - _Standard ML&nbsp;→&nbsp;1990_
> - _Caml&nbsp;→&nbsp;1987_

### Haskell

| Champ            | Valeur                                                                                                                           |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Initiateurs      | Comité Haskell&nbsp;:&nbsp;**Paul Hudak**, **Simon Peyton Jones**, **Philip Wadler**, **John Hughes**, **Erik Meijer**, _et al._ |
| Première version | Haskell 1.0, **avril 1990**                                                                                                      |
| Standard actuel  | Haskell 2010 (Haskell 2020 annoncé)                                                                                              |
| Caractéristiques | Pur, paresseux, fortement typé, _type classes (polymorphisme ad hoc)_, monades                                                   |

- **Type classes** (Wadler & Blott, _How to make ad-hoc polymorphism less ad hoc_, POPL, 1989), ancêtre des traits Rust, des protocols Python `Protocol`, des interfaces Go.
- **Monades comme structure pour la représentation d'effets** (Wadler, 1992-95).
- **Lazy evaluation par défaut**, caractéristique quasi unique d'Haskell.

### OCaml (1996)

| Champ            | Valeur                                                                                                                            |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Auteur           | **Xavier Leroy** (Inria, France)                                                                                                  |
| Première version | 1996 (héritier de Caml Light 1990)                                                                                                |
| Modèle           | Strict par défaut, programmation impure autorisée (jusqu'à `Obj.magic`), multi-paradigmes (POO&nbsp;+&nbsp;FP), Garbage Collector |
| Usage industriel | **Jane Street** (HFT, ~500 dévs OCaml), **Facebook** (Hack, Flow), Inria recherche                                                |

### F# (2005)

| Champ            | Valeur                                                                                                |
| ---------------- | ----------------------------------------------------------------------------------------------------- |
| Auteur           | **Don Syme** (Microsoft Research, Cambridge)                                                          |
| Première version | F# 1.0, 2005 (research), intégré à .NET avec Visual Studio 2010 (F# 2.0)                              |
| Modèle           | Strict, .NET-natif, F# Interactive (REPL), _computation expressions_                                  |
| Usage industriel | Banques (Crédit Suisse, JP Morgan), Microsoft, **D-Edge** (hospitality, Paris), trading, data science |

F# est fortement inspiré d'OCaml, adapté à l'écosystème .NET avec une syntaxe plus accessible aux devs C#. C'est dans la communauté F# que **Scott Wlaschin** formalisera ROP.

Par ailleurs, [F\* (2011, Microsoft Research & Inria)](https://fstar-lang.org/) est le cousin académique de F#&nbsp;:&nbsp;même syntaxe ML, mais orienté vérification formelle avec types dépendants, peut générer automatiquement du code F# ou OCaml à partir d'un programme vérifié formellement.

## 3. Monades

### Définition

Une **monade** est un type paramétré `M[T]` (un _container_ générique) accompagné de deux opérations qui obéissent à trois lois&nbsp;:

| Opération                                                   | Signature                  | Rôle                                         |
| ----------------------------------------------------------- | -------------------------- | -------------------------------------------- |
| **`return`** (ou `pure`, `unit`)                            | `T → M[T]`                 | Mettre une valeur dans le container          |
| **`bind`** (`>>=` Haskell, `flatMap` Scala, `then` Ocarina) | `M[T] × (T → M[U]) → M[U]` | Chaîner deux opérations en passant la valeur |

1. **Identité gauche (_Left_)**&nbsp;: `return(x) >>= f` ≡ `f(x)`
2. **Identité droite (_Right_)**&nbsp;: `m >>= return` ≡ `m`
3. **Associativité**&nbsp;: `(m >>= f) >>= g` ≡ `m >>= (λx. f(x) >>= g)`

> Note&nbsp;:&nbsp;les monades sont parfois présentées comme des _design patterns_. La comparaison n'est pas entièrement fausse&nbsp;:&nbsp;elles structurent bien la composition, mais elle est réductrice. Les monades sont des abstractions mathématiques avec des lois formelles, là où les design patterns sont des recettes informelles sans garanties.

### Monades célèbres

| Monade                        | Représente                        | Intérêt                                                                                                             |
| ----------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Maybe&nbsp;/&nbsp;Option**  | Une valeur _peut-être absente_    | Remplace `null`                                                                                                     |
| **Either&nbsp;/&nbsp;Result** | Un succès _ou_ une erreur         | Remplace les exceptions                                                                                             |
| **List**                      | Plusieurs résultats               | Composition (_list comprehensions_)                                                                                 |
| **IO**                        | Une action sur le monde extérieur | Sépare _pure_ de _impur_ (Haskell)                                                                                  |
| **State**                     | Un calcul qui transporte un état  | Encapsule un état mutable dans un contexte pur                                                                      |
| **Reader**                    | Lecture d'un environnement        | Injection de dépendances                                                                                            |
| **Writer**                    | Accumulation de logs              | Tracing pur                                                                                                         |
| **Cont**                      | Continuations                     | Coroutines, async/await, permet d'exprimer la _logique classique_ (loi de Peirce via `call/cc`, Griffin, POPL 1990) |

### Leibniz (1714)

Le terme _monade_ vient de **Gottfried Wilhelm Leibniz** (_Monadologie_, 1714), du grec _μονάς_ (_monos_, «&nbsp;_un, unique_&nbsp;»). Leibniz y définit la monade comme «&nbsp;_une substance simple, sans parties_&nbsp;», l'atome métaphysique du monde. Mac Lane a repris le terme pour la théorie des catégories. Il n'y a **aucune filiation conceptuelle** entre la monade leibnizienne et la monade de la théorie des catégories&nbsp;:&nbsp;Mac Lane a emprunté le terme pour son sens étymologique.

### Eugenio Moggi (1989-91)

**Eugenio Moggi** publie en 1989 «&nbsp;_Computational lambda-calculus and monads_&nbsp;» (LICS). Il _importe_ les monades de la **théorie des catégories** (Godement, 1958) vers la **sémantique des langages**. Avant Moggi, les monades étaient une construction abstraite. Après Moggi, c'est devenu le **standard** pour formaliser les effets de bord.

### Philip Wadler (1990-95)

**Philip Wadler** (alors à Glasgow, plus tard Edinburgh) popularise les monades en Haskell&nbsp;:

- **«&nbsp;_Comprehending Monads_&nbsp;»** (présenté en 1990, publié en 1992)
- **«&nbsp;_The essence of functional programming_&nbsp;»** (POPL, 1992)
- **«&nbsp;_Monads for functional programming_&nbsp;»** (1992/1995)

Wadler montre comment écrire du code _qui ressemble à de l'impératif_, séquence d'opérations, états, IO, _tout en restant pur_ grâce aux monades.  
C'est l'**innovation pédagogique** qui ancre les monades dans la pratique Haskell.

## 4. Railway Oriented Programming (ROP)&nbsp;—&nbsp;Scott Wlaschin, 2014

### Contexte

**Scott Wlaschin**, auteur du site [`fsharpforfunandprofit.com`](https://fsharpforfunandprofit.com) et du livre _Domain Modeling Made Functional_ (Pragmatic Bookshelf, 2018).

En 2014, à **NDC London**, il donne la conférence **«&nbsp;_Railway Oriented Programming_&nbsp;»**.  
Vidéo sur Vimeo, transcript sur _F# for Fun and Profit_.

### Pitch

> _Most code looks like a railway with one track. Success goes through. Failure throws an exception, jumping off the rails._
>
> _Let me show you the two-track railway. Success on one track. Failure on the other. No exception. Every step decides which track to use. The composition is automatic._

> _Note&nbsp;:&nbsp;le pitch ci-dessus est une paraphrase, pas une citation directe._

C'est, en termes opérationnels, **la monade Either rebaptisée avec une métaphore visuelle**.

### Diagramme

```
        ╔═══════╗    ╔═══════╗    ╔═══════╗
in ────>║ step1 ║───>║ step2 ║───>║ step3 ║────> success ─┐
        ╠═══════╣    ╠═══════╣    ╠═══════╣               ├──► result
        ║       ║───>║       ║───>║       ║────> failure ─┘
        ╚═══════╝    ╚═══════╝    ╚═══════╝
```

Chaque _step_ est une fonction `T → Result[U]`.  
La composition est mécanique&nbsp;:&nbsp;tant que c'est _success_, on continue.  
Au premier _failure_, on bascule dans le rail inférieur et on **court-circuite** tous les steps suivants.

### Théorie sous-jacente

_Either monad_&nbsp;:

```haskell
data Either a b = Left a | Right b
```

- `Right`&nbsp;=&nbsp;succès (rail haut).
- `Left`&nbsp;=&nbsp;échec (rail bas).
- `>>=` (bind)&nbsp;=&nbsp;la fonction qui chaîne en court-circuitant sur `Left`.

C'est **identique** à `Result[T]` dans Ocarina&nbsp;:

```python
Result[T] = Ok[T] | Fail
```

| Haskell       | Wlaschin (F#)                  | Rust               | Ocarina (Python)          |
| ------------- | ------------------------------ | ------------------ | ------------------------- |
| `Either a b`  | `Result<'TSuccess, 'TFailure>` | `Result<T, E>`     | `Result[T]`               |
| `Right x`     | `Success x`                    | `Ok(x)`            | `Ok(x)`                   |
| `Left e`      | `Failure e`                    | `Err(e)`           | `Fail(error)`             |
| `>>=`         | `>>=` (custom op)              | `?` (try operator) | `fold` /&nbsp;chain state |
| `do` notation | `result { … }` (CE)            | `?`-chain          | `ChainRunner[T]`          |

### Adoption industrielle

| Langage    | Pattern équivalent                 | Date d'adoption mainstream                       |
| ---------- | ---------------------------------- | ------------------------------------------------ |
| Haskell    | `Either` monad                     | 1990                                             |
| OCaml      | `result` (stdlib)                  | 2014                                             |
| F#         | `Result<>` (stdlib)                | 2016                                             |
| Rust       | `Result<T, E>` + `?`               | 2010 (release)&nbsp;—&nbsp;`?` operator 2016     |
| Swift      | `Result<Success, Failure>`         | 2019 (Swift 5)                                   |
| Kotlin     | `Result<T>`                        | 2018 (stdlib)                                    |
| Scala      | `Either[A, B]`                     | 2009 (stdlib)                                    |
| TypeScript | _userland_ (`fp-ts`, `effect-ts`)  | jamais standard                                  |
| Java       | _userland_ (`Vavr`, `Either`)      | jamais standard                                  |
| Python     | _userland_&nbsp;→&nbsp;**Ocarina** | **Aucun framework e2e ne le fait avant Ocarina** |

## 5. Comment Ocarina l'implémente

### Lambda-calcul&nbsp;→&nbsp;closures

Ocarina utilise **systématiquement** des _closures_ là où la POO classique utiliserait _l'héritage_ ou _l'injection de dépendances_.

Une _closure_ est une **λ-abstraction** avec capture d'environnement&nbsp;:&nbsp;`λx.λy.M` partiellement appliqué à `N` donne `λy.M[N/x]`, une fonction qui capture `N` dans son environnement.

```python
def my_scenario(driver: WebDriver, logger: ILogger) -> Scenario:
    page = MyPage(driver=driver)

    return Scenario(
        # logger is captured in a closure, not "injected"
        setup=lambda: seed_test_user(logger=logger),
        teardown=lambda: delete_test_user(logger=logger),
        test_chain=[...],
    )
```

C'est de l'IoC _par closure_, pas par injection.  
Le lambda-calcul à l'œuvre.

### Hindley-Milner&nbsp;→&nbsp;mypy strict +&nbsp;PEP 695

```python
class ActionChain[T]:
    def then(
        self, action_or_start: Action[T] | ActionStart[T]
    ) -> ActionStart[T] | NeutralActionStart[T]:
        ...
```

```python
@final
class ValidationStartBlock[T]:
    def assert_that(
        self, predicate: Predicate[T], *, msg: str | None = None
    ) -> ValidationAssertBlock[T]:
        predicate = _with_msg(predicate, msg, self._name)
        self._chain.add_assertion(self._value, predicate, self._name)
        return ValidationAssertBlock(
            self._value, self._chain, self._name, last_predicate=predicate
        )
```

```python
def then[U](
    self, new_value: U, *, name: str | None = None
) -> ValidationStartBlock[U]:
    return ValidationStartBlock(new_value, self._chain, name)
```

PEP 695 (Python 3.12+) introduit la syntaxe `[T, U]`.

### Tests de types

Ocarina intègre une suite de tests dédiée aux types (`test_types.yml`).

**Les cas succès** confirment que mypy infère correctement, par exemple que `T` est préservé de `ActionStart` jusqu'à `ActionChain`&nbsp;:

```yaml
- case: generic_type_preserved_through_chain
  main: |
    chain = ActionStart(lambda: Ok("hello")).failure(lambda e: None).success(lambda: None).execute()
    reveal_type(chain)  # N: Revealed type is .*ActionChain\[.*str.*\]
```

**Les cas échec** vérifient que mypy _rejette bien_ ce qui doit être rejeté, qu'un _prédicat_ incompatible ou un _handler_ mal signé produisent une erreur&nbsp;:

```yaml
- case: incompatible_predicate_type
  main: |
    validate(1234).assert_that(is_email)
  out: |
    main:4: error: .* incompatible type .*

- case: execute_on_action_start_not_allowed
  main: |
    ActionStart(lambda: Ok(42)).execute()
  out: |
    main:4: error: .* has no attribute "execute".*
```

**Le _runtime_ ne vérifie pas les types (c'est du typage STATIQUE&nbsp;!)**. `mypy` le fait. Les tests de types vérifient que mypy fait bien son travail dans les deux sens&nbsp;:&nbsp;qu'il accepte ce qui est valide **et** qu'il refuse ce qui ne l'est pas.

### Either&nbsp;/&nbsp;Result&nbsp;→&nbsp;ROP

Le cœur d'Ocarina est **littéralement** ROP&nbsp;:

- `Result[T] = Ok[T] | Fail`, c'est l'_Either Monad_.
- `ChainRunner[T]`, c'est la composition `>>=`.
- `action chain state`, c'est la _machine à états_ qui implémente la dichotomie rail de succès /&nbsp;rail d'échec.
- `neutral`, convention de Wlaschin&nbsp;:&nbsp;un rail _failure_ continue de faire _comme si_ sans modification jusqu'au bout (équivalent du `Left e` qui traverse les `bind` sans s'évaluer).

### Computation expressions F#&nbsp;→&nbsp;`ChainRunner` /&nbsp;`chain_actions` /&nbsp;`drive_page`

F# a les _computation expressions_ (`result { … }`), Haskell la `do`-notation.  
Les deux proposent `bind`/`>>=`.

`ChainRunner[T]` +&nbsp;`chain_actions` s'inspirent de la même idée (séquentialité lazy, court-circuit sur échec), mais avec une API manuelle. `drive_page` dans `ocarina-example` en est l'alias sémantique direct, il appelle `chain_actions` à l'identique&nbsp;:

```python
# ocarina/opinionated/dsl/drive_page.py
def drive_page(
    first: ActionSuccess[TPOM], *rest: ActionSuccess[TPOM]
) -> ChainRunner[TPOM]:
    return chain_actions(first, *rest)
```

Ce qui donne en usage réel dans `ocarina-example`&nbsp;:

```python
# tests/scenarios/dashboard/access/happy_paths.py
return [
    drive_page(
        act(on_dashboard_login_page, open_dashboard_login_page)
        .failure(just_log_error("Failed to open the dashboard login page..."))
        .success(just_log_success("Opened the dashboard login page!")),
        act(on_dashboard_login_page, verify_dashboard_login_page)
        .failure(log_error_with_current_url("Failed to verify the dashboard login page..."))
        .success(log_success_with_current_url_and_take_screenshot("Verified!")),
    ),
    drive_page(
        act(on_dashboard_welcome_page, verify_dashboard_welcome_page)
        .failure(log_error_with_current_url("Failed to verify the welcome page..."))
        .success(log_success_with_current_url_and_take_screenshot("Verified!")),
    ),
]
```

Le court-circuit est explicite dans le `reducer` de `chain_actions`, si un `drive_page` échoue, les suivants ne s'exécutent pas&nbsp;:

```python
# ocarina/dsl/testing_with_railway/chain_actions.py
def reducer(chain: ActionChain[T], step: ActionSuccess[T]) -> ActionChain[T]:
    if chain.has_failed():
        return chain  # court-circuit — les étapes suivantes ne s'exécutent pas
    return (
        chain.then(step.__action__)
        .failure(step.__failure_handler__)
        .success(step.__success_handler__)
        .execute()
    )
```

`match_page` s'inscrit dans la même famille _lazy_, il retourne un `ChainRunner` dont le `_thunk()` n'évalue les conditions et n'exécute la branche correspondante qu'au moment du `.run()`, exactement comme `chain_actions`. Ce qui le distingue, c'est la nature de la composition&nbsp;: conditionnelle plutôt que séquentielle, et il peut s'imbriquer. Dans `ocarina-example`, il sert à naviguer sur des pages dont l'état est non déterministe à l'avance (A/B tests, bannières aléatoires, anti-bots)&nbsp;:

```python
# tests/scenarios/randomness/level_4/walkthrough.py
return [
    open_madness_random_page,
    match_page(
        branches=[
            when(check_that_madness.is_cors_page, name="is_cors_page",
                 then=go_from_cors_page_to_homepage),
            when(check_that_madness.is_bastia_page, name="is_bastia_page",
                 then=[
                     go_from_this_is_bastia_page_to_random_dsed_page,
                     match_page(
                         branches=[
                             when(check_that_dsed_result.is_bsod_page,
                                  name="is_bsod_page", then=[bsod_dead_end]),
                             when(check_that_dsed_result.is_ids_bypassed_page,
                                  name="is_ids_bypassed_page",
                                  then=go_from_ids_bypassed_page_to_homepage),
                         ],
                     ),
                 ]),
        ],
    ),
]
```

La différence avec F#/Haskell&nbsp;:&nbsp;dans `result { let! x = fetch(); let! y = parse(x) }`, le compilateur génère le `bind` automatiquement. Dans Ocarina, chaque étape câble ses handlers manuellement, `.failure()` /&nbsp;`.success()`, et `chain_actions` /&nbsp;`drive_page` font le `reduce` explicitement. Même intention de séquentialité avec court-circuit, mais pas le même mécanisme.

> **Note**&nbsp;:&nbsp;Python n'offrant ni `do`-notation ni _computation expressions_, Ocarina n'implémente pas de `bind` généralisé. La _fluent API_ manuelle (`.failure()` /&nbsp;`.success()` /&nbsp;`.execute()`) est le choix naturel dans ce contexte&nbsp;:&nbsp;il reste lisible sans infrastructure théorique, et suffisant pour les besoins d'un framework de test.

### Pur à travers tout l'ISTQB, impur à travers les POM

L'orchestration, la déclaration des scénarios de test, des suites, des campagnes et du cycle **sont pures et implémentent les définitions formelles auxquelles sont habitués les testeurs fonctionnels** (ISTQB).

Les POMs, quant à eux, restent présents pour s'adapter à ceux à quoi les automaticiens en test logiciel sont eux-mêmes habitués plutôt que de chercher à «&nbsp;_briller_&nbsp;» en imposant des abstractions que personne ne comprend.

Holy Book (chapitre «&nbsp;_Premiers retours_&nbsp;»)&nbsp;:

> Et moi je ne suis pas là pour le _prestige_. Ni même pour le _profit_.  
> Je suis là pour notre **communauté**.

> Pour en arriver là, la question n'a jamais été de "briller" plus que les autres.  
> Il ne s'agit d'ailleurs pas d'un réel challenge.  
> La question a juste été&nbsp;:&nbsp;**de quoi ai-je réellement besoin&nbsp;?**

## 6. Conclusions

Le Holy Book ne dit pas «&nbsp;_ROP_&nbsp;», «&nbsp;_monade_&nbsp;», «&nbsp;_Curry-Howard_&nbsp;».  
Mais il _applique_ chacun de ces concepts. Et son argument implicite est&nbsp;:

1. La théorie est **disponible depuis 90 ans** (Church, 1936).
2. L'industrie du test e2e **n'en a rien retenu**. Cypress, Playwright, Robot Framework, aucun ne fait de ROP, aucun n'a `mypy --strict`, **aucun n'est formel**.
3. Ocarina **l'applique dans un cadre tangible pour les testeurs fonctionnels** (Python, ISTQB).

Le _shift_ que représente Ocarina (cf. [`08-ocarina-in-testing-industry.md`](08-ocarina-in-testing-industry.md)) **n'est pas une invention**, c'est une **redistribution** de théories matures vers un domaine qui les ignorait.

C'est la posture de Graham dans _Beating the Averages_&nbsp;:&nbsp;prendre une idée académique mature que l'industrie n'a pas retenue, et en faire un avantage tangible dans un livrable.
