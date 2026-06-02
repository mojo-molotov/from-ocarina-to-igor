# Ch 03 — Functional programming

Chapter brief for LLM navigation. Source articles: `site/content.en/03-functional/`.

## Articles

| File | Description |
| --- | --- |
| `_index.md` | Chapter landing page. Framing: a transversal rereading of the framework from the FP angle — small code, but it embodies a serious number of named, justified FP patterns. Carries the Holy Book "First feedbacks" quote on people who twisted ROP / lazy evaluation / IoC. |
| `01-effect-thunk-result.md` | `Effect`, `Thunk[T]`, `Result[T]`: the three primitive types. How they compose. |
| `02-closures-ioc.md` | Closures as the primitive of inversion of control — how Ocarina avoids dependency injection frameworks. |
| `03-lazy-evaluation.md` | Laziness throughout: `ChainRunner`, `validate.execute`, `Watcher` callback, lazy prefixes. Nothing executes until asked. |
| `04-fold-reduce.md` | `reduce` (fold left) in `chain_actions`: threading `Result[T]` through a list of thunks. |
| `05-declarative.md` | Declarative style: a scenario _describes_ what should happen, doesn't execute imperatively. |
| `06-pep-695-generics.md` | PEP 695 generics (`type X[T] = ...`, `TypeVar bound`): how Ocarina uses Python 3.14 type syntax. |
| `07-discriminated-unions-typeguards.md` | Discriminated unions + `TypeGuard` + `@final` = sealed unions. How `Result[T]` is a discriminated union. |

## Key concepts

- **`Thunk[T]`**: a zero-argument callable returning `T`. The building block of lazy evaluation in Ocarina.
- **`Result[T]`** is a discriminated union (`Ok[T] | Fail`), not an exception. `Fail` is not generic — the error channel is always `Exception` (deliberate KISS choice). Pattern-matched with `TypeGuard`.
- **Closures as IoC**: instead of DI containers or service locators, Ocarina captures dependencies in closures at construction time. `drive_page(driver)(url)` is a closure.
- **Fold left**: `chain_actions` is `functools.reduce` over thunks, threading the accumulated `Result[T]`. Short-circuits on first `Fail`.
- **PEP 695**: Ocarina requires Python 3.14+ because it uses the new type alias syntax. The chapter explains the generics design.
- **Sealed unions**: `@final` on `Ok` and `Err` + exhaustive `match` = the type checker guarantees every case is handled.
- **Why a dedicated chapter** (framing): Ocarina's code is small but embodies a serious number of FP patterns; this chapter names them, justifies them, and points to where they live. The Holy Book's "First feedbacks" rant — people twisting ROP, lazy evaluation and IoC without understanding them — is why the FP foundations are spelled out explicitly.

## Connections

- The types described here live in Ch 02 (framework internals)
- Tests for these FP patterns → Ch 04 (hypothesis properties, mypy plugins)
- How they appear in practice → Ch 07 (ocarina-example scenarios)

## Not covered here

General FP theory beyond what Ocarina applies. Haskell / F# / OCaml lineage is in Ch 12 (lambda calculus article). Category theory, monads as mathematical objects — not here.

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
