---
title: "02.03.02 — The builder state machine"
weight: 2
date: 2026-05-20
series: ["railway"]
series_order: 2
tags: ["ocarina", "rop"]
---

# 02.03.02&nbsp;—&nbsp;The builder state machine

> Source file: [`src/ocarina/dsl/testing_with_railway/internals/action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/internals/action_chain.py)
>
> Here's where the _entire_ ROP mechanic lives: four successive typed states that literally (as in: the _type-checker_ literally) refuse any syntactic improvisation. The DSL doubles as its own immune system.

## Overview

```
                      ┌─────────────────┐
   start(action)  →   │  ActionStart[T] │     an Action[T] = Thunk[Result[T]]
                      └────────┬────────┘
                               │ .failure(failure_handler)
                               ▼
                      ┌─────────────────┐
                      │ ActionFailure[T]│
                      └────────┬────────┘
                               │ .success(success_handler)
                               ▼
                      ┌─────────────────┐
                      │ ActionSuccess[T]│
                      └────────┬────────┘
                               │ .execute()   ── runs action(), fires the handler
                               ▼
                      ┌─────────────────┐
                      │ ActionChain[T]  │     holds (has_failed, result)
                      └──────┬──────────┘
                             │ .then(next_action_or_start)
              ┌──────────────┴──────────────┐
              │                             │
   has_failed=True                   has_failed=False
              │                             │
              ▼                             ▼
   ┌──────────────────┐         ┌───────────────────┐
   │ NeutralAction-   │         │ ActionStart[T]    │  → cycle starts over
   │ Start[T]         │         │  (the next action │
   │ (failure rail:   │         │   will execute)   │
   │  the whole chain │         └───────────────────┘
   │  becomes no-op,  │
   │  while keeping   │
   │  the fluent API) │
   └──────────────────┘
              │
              ▼ (.failure → .success → .execute, all no-op)
   ┌──────────────────┐
   │  ActionChain[T]  │   has_failed=True, result=<accumulated Fail>
   └──────────────────┘
```

## The types `Action`, `FailureHandler`, `SuccHandler`

```python
type Action[T]        = Thunk[Result[T]]      # () -> Result[T]
type FailureHandler   = Callable[[Exception], None]
type SuccHandler      = Effect                # () -> None
```

- **`Action[T]` is a `Thunk`.** Calling `ActionStart(action)` does **not** run anything. The action just gets captured.
- **`FailureHandler` gets the exception**, not the `Fail` or the `Result`. Deliberate: 99% of handlers want to log the exception, take a screenshot, and move on.
- **`SuccHandler` is an `Effect`** (no argument). Same idea&nbsp;—&nbsp;a success handler logs a static message, snaps a screenshot, doesn't need the result.

## Typestate Pattern: why you can't get it wrong

The chain is **strictly linear**. Each method returns a different type that only exposes the _next legal step_:

| Type               | Exposed methods                                        | Does NOT expose                         |
| ------------------ | ------------------------------------------------------ | --------------------------------------- |
| `ActionStart[T]`   | `.failure(h)`                                          | `.success`, `.execute` (don't exist!)   |
| `ActionFailure[T]` | `.success(h')`                                         | `.failure` (already called), `.execute` |
| `ActionSuccess[T]` | `.execute()`                                           | `.failure`, `.success`                  |
| `ActionChain[T]`   | `.then(...)`, `.has_failed()`, `.is_ok()`, `.result()` | `.failure`, `.success`, `.execute`      |

Excerpts from the Holy Book (chapter on scenarios composability):

### Attempt 1: Forget `.success`

```python
drive_page(
    act(on_book_a_call_page, verify_book_call_page)
    .failure(just_log_error("..."))
)

# error: Expected type 'ActionSuccess[TPOM ≤: POMBase]', got 'ActionFailure[BookCallPage]' instead
```

### Attempt 2: Put `.success` before `.failure`

```python
drive_page(
    act(on_book_a_call_page, verify_book_call_page)
    .success(log_success_with_url_and_screenshot("..."))   # ← error here
)

# error:
# "ActionStart[BookCallPage]" has no attribute "success"
# Unresolved attribute reference 'success' for class 'ActionStart'
```

### Attempt 3: Swap `.failure` and `.success`

```python
drive_page(
    act(on_book_a_call_page, verify_book_call_page)
    .success(...)
    .failure(...)
)

# error:
# "ActionStart[BookCallPage]" has no attribute "success"
```

The checker outright rejects the code. The grammar lives **in the types**, not in a convention.

## Narrowing via `act()`: preserving `TPOM`

The user project defines `act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]`. `TPOM` survives _all the way through_ the chain:

```python
on_homepage = Homepage(driver=driver)
act(on_homepage, verify_book_call_page)
#                ^^^^^^^^^^^^^^^^^^^^^
# error: Argument 2 to "act" has incompatible type
#   "Callable[[BookCallPage], BookCallPage]";
#   expected "Callable[[Homepage], Homepage]"
```

Mixing heterogeneous `act` calls inside the same `drive_page` is also refused:

```python
drive_page(
    act(on_homepage, ...).failure(...).success(...),
    act(on_book_a_call_page, verify_book_call_page).failure(...).success(...),
    #   ^^^^^^^^^^^^^^^^^^^
    # error: Expected type 'ActionSuccess[Homepage]',
    #        got 'ActionSuccess[BookCallPage]' instead
)
```

That constraint is what forces **every page transition into a new `drive_page`**. The point is **semantic**: reviews get easier (page transitions jump out, missing screenshots are obvious). See [`05-create-act-hooks.md`](05-create-act-hooks.md).

## `ActionSuccess.execute()`

```python
def execute(self) -> ActionChain[T]:
    result = self.__action__()                              # 1. run the action

    if is_fail(result):
        self.__failure_handler__(result.error)              # 2a. fire failure
        return ActionChain(has_failed=True, result=result)  #     failure rail

    self.__success_handler__()                              # 2b. fire success
    return ActionChain(has_failed=False, result=result)     #     success rail
```

1. **The action runs with no argument** (it's a `Thunk[Result[T]]`). Its full context was captured by `create_act` in a _closure_.
2. The _failure_ handler gets `result.error`.
3. The _success_ handler gets **nothing**.
4. `ActionChain` carries two things: a flag (`has_failed: bool`) **and** the `Result`. The flag lets `.then()` branch without another `isinstance` (_hot path_).

## `__action__`, `__failure_handler__`, `__success_handler__`

Triple naming in _dunders_ (double underscores).

Framework-**internal** attributes. The double-underscore says "don't touch, this is plumbing." `chain_actions` reads them to rebuild the chain:

```python
def reducer(chain: ActionChain[T], step: ActionSuccess[T]) -> ActionChain[T]:
    if chain.has_failed():
        return chain
    return (
        chain.then(step.__action__)
        .failure(step.__failure_handler__)
        .success(step.__success_handler__)
        .execute()
    )
```

Direct inspiration: [`xhtmlboi.github.io/articles/yocaml.html`](https://xhtmlboi.github.io/articles/yocaml.html). The recipe: start from "flat," explicit functional composition (parens nested several deep), then introduce an operator (here, `.failure().success().execute()` + `.then()`) that _flattens_ the read while keeping the typing intact. Ocarina copies the pattern, swapping OCaml _rules_ for Selenium _actions_.

## Recap

| Principle                                                 | Consequence                                                                              |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Linearity of the builder                                  | _mypy_ error if you skip a step or change the order                                      |
| `@final` on each class                                    | No user inheritance of the ROP classes                                                   |
| `Action[T]` is a `Thunk`                                  | Lazy evaluation; everything is composable as a value                                     |
| A single `except → Fail` conversion (inside `create_act`) | No exception downstream; everything is a typed value                                     |
| `ActionChain` carries `(has_failed, result)`              | `.then(...)` chooses between `ActionStart` and `NeutralActionStart` via a simple boolean |
| `__action__` etc. as dunders                              | Plumbing; bidirectional relationships inside the framework's implementation              |
