---
title: "12.13 — Lambda calculus, ROP, Haskell / F# / OCaml, monads"
description: "Ocarina invents nothing on the theoretical front. It applies: from Alonzo Church's lambda calculus (1936) to Eugenio Moggi's (1989) and Philip Wadler's (1992-95) monads, formalized as Railway Oriented Programming by Scott Wlaschin (2014)."
weight: 13
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 13
tags: ["rop", "typing"]
---

# 12.13&nbsp;—&nbsp;Lambda calculus, ROP, Haskell / F# / OCaml, monads

> Ocarina invents nothing on the theoretical front. It **applies**: from Alonzo Church's **lambda calculus** (1936) to Eugenio Moggi's (1989) and Philip Wadler's (1992-95) **monads**, formalized as **Railway Oriented Programming** by Scott Wlaschin (2014).

## 1. Lambda calculus (Church, 1936)

### Definition

**Lambda calculus** (λ-calculus) is a formal system invented by **Alonzo Church** (1903-1995) to study **computability**.

| Primitive       | Notation      | Semantics                                             |
| --------------- | ------------- | ----------------------------------------------------- |
| **Variable**    | `x`, `y`, `z` | A name                                                |
| **Abstraction** | `λx.M`        | Definition of a function with parameter `x`, body `M` |
| **Application** | `M N`         | Call of the function `M` on the argument `N`          |

| Rule             | Effect                                      |
| ---------------- | ------------------------------------------- |
| **α-conversion** | Renaming a bound variable (`λx.x` ≡ `λy.y`) |
| **β-reduction**  | Applying a function: `(λx.M) N → M[x := N]` |
| **η-conversion** | `λx.(f x) ≡ f` if `x` not free in `f`       |

### Why it's foundational

1. **1936**: Church proves λ-calculus is **Turing-complete** (Turing publishes his machine in 1937). _Church-Turing thesis_: anything _mechanically computable_ can be expressed in λ-calculus.
2. **Alan Turing** was Church's doctoral student at Princeton (PhD, 1938).
3. λ-calculus is **simpler** than the Turing machine: only 3 constructions. Everything else&nbsp;—&nbsp;integers, booleans, data structures&nbsp;—&nbsp;is _encoded_ with those 3 bricks (Church encoding).

### Typed lambda calculus (Church, 1940)

Church added **types** in 1940 (_simply typed lambda calculus_, STLC) to forbid self-application paradoxes (`λx.x x`). Each variable has a type, and function application is only allowed if types match.

It's the **direct ancestor** of types in Haskell, OCaml, F#, TypeScript, Python, Rust, etc.

### Curry-Howard (1934-1969)

**Haskell Curry** observed the connection in 1934 (refined in 1958) and **William Howard** extended it in 1969:

> **A typed program _is_ a mathematical proof.**  
> **A type _is_ a proposition.**  
> **The type-checker is a proof checker.**

That's the **Curry-Howard isomorphism**: if code compiles under strict typing, it is **mathematically correct** along the dimensions encoded by the types.

Hence `mypy --strict` in Ocarina: it's not an obsession, it's not autism, it's the **application** of the Curry-Howard theorem in an industrial setting.

## 2. ML (1973 to today)

### Robin Milner and ML (Edinburgh, 1973)

**Robin Milner** (1934-2010, Turing Award 1991) designed **ML** (_Meta Language_) at Edinburgh as a language for **automated proofs** (Edinburgh LCF&nbsp;—&nbsp;_Logic for Computable Functions_).

- **Hindley-Milner type system**: complete type inference without annotations. The compiler _guesses_ (infers) all types.
- **Pattern matching**: `match x with | Cons (h, t) -> ... | Nil -> ...`.
- **Parametric polymorphism**: `'a list` (list of _anything_).
- **Functions as first-class values**: passing a function as an argument.

### ML genealogy

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

> _Note: some indicated dates correspond to design start._
>
> _First public release/implementation dates:_
>
> - _ML → 1979_
> - _Standard ML → 1990_
> - _Caml → 1987_

### Haskell

| Field            | Value                                                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Initiators       | Haskell Committee: **Paul Hudak**, **Simon Peyton Jones**, **Philip Wadler**, **John Hughes**, **Erik Meijer**, _et al._ |
| First version    | Haskell 1.0, **April 1990**                                                                                              |
| Current standard | Haskell 2010 (Haskell 2020 announced)                                                                                    |
| Characteristics  | Pure, lazy, strongly typed, _type classes (ad-hoc polymorphism)_, monads                                                 |

- **Type classes** (Wadler & Blott, _How to make ad-hoc polymorphism less ad hoc_, POPL, 1989), ancestor of Rust traits, Python `Protocol`s, Go interfaces.
- **Monads as a structure for representing effects** (Wadler, 1992-95).
- **Lazy evaluation by default**, a feature almost unique to Haskell.

### OCaml (1996)

| Field          | Value                                                                                                             |
| -------------- | ----------------------------------------------------------------------------------------------------------------- |
| Author         | **Xavier Leroy** (Inria, France)                                                                                  |
| First version  | 1996 (heir of Caml Light 1990)                                                                                    |
| Model          | Strict by default, impure programming allowed (down to `Obj.magic`), multi-paradigm (OOP + FP), garbage-collected |
| Industrial use | **Jane Street** (HFT, ~500 OCaml devs), **Facebook** (Hack, Flow), Inria research                                 |

### F# (2005)

| Field          | Value                                                                                               |
| -------------- | --------------------------------------------------------------------------------------------------- |
| Author         | **Don Syme** (Microsoft Research, Cambridge)                                                        |
| First version  | F# 1.0, 2005 (research), integrated into .NET with Visual Studio 2010 (F# 2.0)                      |
| Model          | Strict, .NET-native, F# Interactive (REPL), _computation expressions_                               |
| Industrial use | Banks (Credit Suisse, JP Morgan), Microsoft, **D-Edge** (hospitality, Paris), trading, data science |

F# is heavily inspired by OCaml, adapted to the .NET ecosystem with syntax more accessible to C# devs. It's in the F# community that **Scott Wlaschin** would formalize ROP.

Also, [F\* (2011, Microsoft Research & Inria)](https://fstar-lang.org/) is F#'s academic cousin: same ML syntax, but oriented toward formal verification with dependent types&nbsp;—&nbsp;it can automatically generate F# or OCaml code from a formally verified program.

## 3. Monads

### Definition

A **monad** is a parameterized type `M[T]` (a generic _container_) together with two operations obeying three laws:

| Operation                                                   | Signature                  | Role                                      |
| ----------------------------------------------------------- | -------------------------- | ----------------------------------------- |
| **`return`** (or `pure`, `unit`)                            | `T → M[T]`                 | Put a value in the container              |
| **`bind`** (`>>=` Haskell, `flatMap` Scala, `then` Ocarina) | `M[T] × (T → M[U]) → M[U]` | Chain two operations by passing the value |

1. **Left identity**: `return(x) >>= f` ≡ `f(x)`
2. **Right identity**: `m >>= return` ≡ `m`
3. **Associativity**: `(m >>= f) >>= g` ≡ `m >>= (λx. f(x) >>= g)`

> Note: monads are sometimes presented as _design patterns_. The comparison isn't entirely wrong&nbsp;—&nbsp;they do structure composition well&nbsp;—&nbsp;but it's reductive. Monads are mathematical abstractions with formal laws, while design patterns are informal recipes without guarantees.

### Famous monads

| Monad               | Represents                     | Interest                                                                                              |
| ------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------- |
| **Maybe / Option**  | A value _maybe absent_         | Replaces `null`                                                                                       |
| **Either / Result** | A success _or_ an error        | Replaces exceptions                                                                                   |
| **List**            | Multiple results               | Composition (_list comprehensions_)                                                                   |
| **IO**              | An action on the outside world | Separates _pure_ from _impure_ (Haskell)                                                              |
| **State**           | A computation carrying state   | Encapsulates a mutable state in a pure context                                                        |
| **Reader**          | Reading an environment         | Dependency injection                                                                                  |
| **Writer**          | Log accumulation               | Pure tracing                                                                                          |
| **Cont**            | Continuations                  | Coroutines, async/await; expresses _classical logic_ (Peirce's law via `call/cc`, Griffin, POPL 1990) |

### Leibniz (1714)

The term _monad_ comes from **Gottfried Wilhelm Leibniz** (_Monadology_, 1714), from Greek _μονάς_ (_monos_, "_one, unique_"). Leibniz defines the monad as "_a simple substance, without parts_", the metaphysical atom of the world. Mac Lane reused the term for category theory. There is **no conceptual lineage** between the Leibnizian monad and the category-theoretic monad: Mac Lane borrowed the term for its etymological sense.

### Eugenio Moggi (1989-91)

**Eugenio Moggi** published in 1989 "_Computational lambda-calculus and monads_" (LICS). He _imported_ monads from **category theory** (Godement, 1958) into **language semantics**. Before Moggi, monads were an abstract construction. After Moggi, it became the **standard** for formalizing side effects.

### Philip Wadler (1990-95)

**Philip Wadler** (then at Glasgow, later Edinburgh) popularized monads in Haskell:

- **"_Comprehending Monads_"** (presented 1990, published 1992)
- **"_The essence of functional programming_"** (POPL, 1992)
- **"_Monads for functional programming_"** (1992/1995)

Wadler showed how to write code _that looks imperative_&nbsp;—&nbsp;a sequence of operations, state, IO&nbsp;—&nbsp;_while remaining pure_ thanks to monads. That's the **pedagogical innovation** that anchored monads in Haskell practice.

## 4. Railway Oriented Programming (ROP)&nbsp;—&nbsp;Scott Wlaschin, 2014

### Context

**Scott Wlaschin**, author of [`fsharpforfunandprofit.com`](https://fsharpforfunandprofit.com) and of the book _Domain Modeling Made Functional_ (Pragmatic Bookshelf, 2018).

In 2014, at **NDC London**, he gave the talk **"_Railway Oriented Programming_"**&nbsp;—&nbsp;video on Vimeo, transcript on _F# for Fun and Profit_.

### Pitch

> _Most code looks like a railway with one track. Success goes through. Failure throws an exception, jumping off the rails._
>
> _Let me show you the two-track railway. Success on one track. Failure on the other. No exception. Every step decides which track to use. The composition is automatic._

> _Note: the pitch above is a paraphrase, not a direct quote._

In operational terms, it's **the Either monad rebranded with a visual metaphor**.

### Diagram

```
        ╔═══════╗    ╔═══════╗    ╔═══════╗
in ────>║ step1 ║───>║ step2 ║───>║ step3 ║────> success ─┐
        ╠═══════╣    ╠═══════╣    ╠═══════╣               ├──► result
        ║       ║───>║       ║───>║       ║────> failure ─┘
        ╚═══════╝    ╚═══════╝    ╚═══════╝
```

Each _step_ is a function `T → Result[U]`. Composition is mechanical: as long as it's _success_, you continue. At the first _failure_, you switch to the lower rail and **short-circuit** every subsequent step.

### Underlying theory

_Either monad_:

```haskell
data Either a b = Left a | Right b
```

- `Right` = success (upper rail).
- `Left` = failure (lower rail).
- `>>=` (bind) = the function that chains by short-circuiting on `Left`.

This is **identical** to `Result[T]` in Ocarina:

```python
Result[T] = Ok[T] | Fail
```

| Haskell       | Wlaschin (F#)                  | Rust               | Ocarina (Python)     |
| ------------- | ------------------------------ | ------------------ | -------------------- |
| `Either a b`  | `Result<'TSuccess, 'TFailure>` | `Result<T, E>`     | `Result[T]`          |
| `Right x`     | `Success x`                    | `Ok(x)`            | `Ok(x)`              |
| `Left e`      | `Failure e`                    | `Err(e)`           | `Fail(error)`        |
| `>>=`         | `>>=` (custom op)              | `?` (try operator) | `fold` / chain state |
| `do` notation | `result { … }` (CE)            | `?`-chain          | `ChainRunner[T]`     |

### Industrial adoption

| Language   | Equivalent pattern                | Mainstream adoption date                     |
| ---------- | --------------------------------- | -------------------------------------------- |
| Haskell    | `Either` monad                    | 1990                                         |
| OCaml      | `result` (stdlib)                 | 2014                                         |
| F#         | `Result<>` (stdlib)               | 2016                                         |
| Rust       | `Result<T, E>` + `?`              | 2010 (release)&nbsp;—&nbsp;`?` operator 2016 |
| Swift      | `Result<Success, Failure>`        | 2019 (Swift 5)                               |
| Kotlin     | `Result<T>`                       | 2018 (stdlib)                                |
| Scala      | `Either[A, B]`                    | 2009 (stdlib)                                |
| TypeScript | _userland_ (`fp-ts`, `effect-ts`) | never standard                               |
| Java       | _userland_ (`Vavr`, `Either`)     | never standard                               |
| Python     | _userland_ → **Ocarina**          | **No e2e framework does it before Ocarina**  |

## 5. How Ocarina implements it

### Lambda calculus → closures

Ocarina uses **closures** systematically where classic OOP would use _inheritance_ or _dependency injection_.

A _closure_ is a **λ-abstraction** with environment capture: `λx.λy.M` partially applied to `N` yields `λy.M[N/x]`, a function that captures `N` in its environment.

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

That's IoC _by closure_, not by injection&nbsp;—&nbsp;lambda calculus at work.

### Hindley-Milner → mypy strict + PEP 695

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

PEP 695 (Python 3.12+) introduces the `[T, U]` syntax.

### Type tests

Ocarina ships a dedicated test suite for types (`test_types.yml`).

**Success cases** confirm that mypy infers correctly, e.g. that `T` is preserved from `ActionStart` through to `ActionChain`:

```yaml
- case: generic_type_preserved_through_chain
  main: |
    chain = ActionStart(lambda: Ok("hello")).failure(lambda e: None).success(lambda: None).execute()
    reveal_type(chain)  # N: Revealed type is .*ActionChain\[.*str.*\]
```

**Failure cases** verify that mypy _does reject_ what should be rejected&nbsp;—&nbsp;that an incompatible _predicate_ or a wrongly signed _handler_ produces an error:

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

**The _runtime_ doesn't check types (it's STATIC typing!)**. `mypy` does. Type tests verify that mypy does its job both ways: that it accepts what's valid **and** that it refuses what isn't.

### Either / Result → ROP

Ocarina's core is **literally** ROP:

- `Result[T] = Ok[T] | Fail`, that's the _Either monad_.
- `ChainRunner[T]`, that's `>>=` composition.
- `action chain state`, that's the _state machine_ implementing the success-rail / failure-rail dichotomy.
- `neutral`, Wlaschin's convention: a _failure_ rail keeps going _as if_ unchanged to the end (equivalent of the `Left e` traversing `bind`s without evaluating).

### F# computation expressions → `ChainRunner` / `chain_actions` / `drive_page`

F# has _computation expressions_ (`result { … }`), Haskell has `do`-notation&nbsp;—&nbsp;both expose `bind`/`>>=`.

`ChainRunner[T]` + `chain_actions` are inspired by the same idea (lazy sequentiality, short-circuit on failure), with a manual API. `drive_page` in `ocarina-example` is its direct semantic alias&nbsp;—&nbsp;it calls `chain_actions` identically:

```python
# ocarina/opinionated/dsl/drive_page.py
def drive_page(
    first: ActionSuccess[TPOM], *rest: ActionSuccess[TPOM]
) -> ChainRunner[TPOM]:
    return chain_actions(first, *rest)
```

Which in real use in `ocarina-example`:

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

The short-circuit is explicit in the `reducer` of `chain_actions`&nbsp;—&nbsp;if a `drive_page` fails, the next ones don't execute:

```python
# ocarina/dsl/testing_with_railway/chain_actions.py
def reducer(chain: ActionChain[T], step: ActionSuccess[T]) -> ActionChain[T]:
    if chain.has_failed():
        return chain  # short-circuit — subsequent steps don't execute
    return (
        chain.then(step.__action__)
        .failure(step.__failure_handler__)
        .success(step.__success_handler__)
        .execute()
    )
```

`match_page` belongs to the same _lazy_ family&nbsp;—&nbsp;it returns a `ChainRunner` whose `_thunk()` only evaluates conditions and runs the matching branch at `.run()` time, exactly like `chain_actions`. What distinguishes it is the nature of composition: conditional rather than sequential, and it can nest. In `ocarina-example`, it's used to navigate pages with non-deterministic state (A/B tests, random banners, anti-bots):

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

The difference with F#/Haskell: in `result { let! x = fetch(); let! y = parse(x) }`, the compiler generates the `bind` automatically. In Ocarina, every step wires its handlers manually&nbsp;—&nbsp;`.failure()` / `.success()`&nbsp;—&nbsp;and `chain_actions` / `drive_page` do the `reduce` explicitly. Same intent of sequentiality with short-circuit, but not the same mechanism.

> **Note**: Python having neither `do`-notation nor _computation expressions_, Ocarina doesn't implement a generalized `bind`. The manual _fluent API_ (`.failure()` / `.success()` / `.execute()`) is the natural choice in this context: it stays readable without theoretical infrastructure, and is sufficient for a test framework's needs.

### Pure across all of ISTQB, impure across POMs

The orchestration, scenario / suite / campaign / cycle declarations **are pure and implement the formal definitions functional testers are used to** (ISTQB).

POMs, meanwhile, remain present to fit what software-test automators are themselves used to, rather than trying to "_shine_" by imposing abstractions no one understands.

Holy Book (chapter "_First feedbacks_"):

> And me, I'm not here for _prestige_. Nor for _profit_.  
> I'm here for our **community**.

> To get there, the question was never to "shine" more than the others.  
> Nor is it actually a real challenge.  
> The question was simply: **what do I really need?**

## 6. Conclusions

The Holy Book doesn't say "_ROP_", "_monad_", "_Curry-Howard_"&nbsp;—&nbsp;but it _applies_ each of these concepts. And its implicit argument is:

1. The theory has been **available for 90 years** (Church, 1936).
2. The e2e test industry **retained nothing of it**. Cypress, Playwright, Robot Framework&nbsp;—&nbsp;none does ROP, none has `mypy --strict`, **none is formal**.
3. Ocarina **applies it in a tangible setting for functional testers** (Python, ISTQB).

The _shift_ Ocarina represents (see [`08-ocarina-in-testing-industry.md`](08-ocarina-in-testing-industry.md)) **isn't an invention**&nbsp;—&nbsp;it's a **redistribution** of mature theory toward a domain that ignored it.

That's Graham's posture in _Beating the Averages_: take a mature academic idea industry hasn't retained, and turn it into a tangible advantage in a deliverable.
