---
title: "02.03.04 — chain_actions and ChainRunner"
description: "chain_actions and the ChainRunner: the fold primitive that flattens a scenario into a list of actions instead of a staircase of chained calls."
weight: 4
date: 2026-05-20
series: ["railway"]
series_order: 4
tags: ["ocarina", "rop"]
---

# 02.03.04&nbsp;—&nbsp;`chain_actions` and `ChainRunner`

> Source file: [`src/ocarina/dsl/testing_with_railway/chain_actions.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/chain_actions.py)
>
> The primitive that makes the DSL "flat." Without it, an N-step scenario is a staircase of `.then(...).failure(...).success(...).execute()`. With it, it's a list.

## “Parenthesis hell”

> Solution:
>
> ```python
> # Flat, readable syntax
> runner = chain_actions(
>     action1.failure(h1).success(h2),
>     action2.failure(h3).success(h4),
>     action3.failure(h5).success(h6)
> )
> chain = runner.run()  # Execute when ready
> ```
>
> Benefits:
>
> - **Lazy evaluation**: Build chain without executing
> - **Flat syntax**: No deep nesting
> - **Automatic short-circuiting**: Stops on first failure
> - **Composability**: ChainRunner is a value

_(Excerpt from the docstring.)_

## `ChainRunner[T]`

```python
@final
class ChainRunner[T]:
    def __init__(self, *, thunk: Thunk[ActionChain[T]]) -> None:
        self._thunk = thunk

    def run(self) -> ActionChain[T]:
        return self._thunk()
```

1. **`@final`**, no user inheritance.
2. **Kwargs-only constructor** (`*, thunk: ...`) blocks the classic slip: `ChainRunner(no_idea)`, which would have been ambiguous.
3. **The `thunk` is a `Thunk[ActionChain[T]]`**&nbsp;—&nbsp;i.e. `Callable[[], ActionChain[T]]`. No side effect runs before `.run()`.
4. **`.run()` returns the `ActionChain[T]`**: you get the state machine back (see [`02-action-chain-states.md`](02-action-chain-states.md)) and can query `has_failed`, `is_ok`, `result`.

## `chain_actions[T](first, *rest)`

```python
def chain_actions[T](
    first: ActionSuccess[T], *rest: ActionSuccess[T]
) -> ChainRunner[T]:

    def thunk() -> ActionChain[T]:
        def reducer(chain: ActionChain[T], step: ActionSuccess[T]) -> ActionChain[T]:
            if chain.has_failed():
                return chain
            return (
                chain.then(step.__action__)
                .failure(step.__failure_handler__)
                .success(step.__success_handler__)
                .execute()
            )
        return reduce(reducer, rest, first.execute())

    return ChainRunner(thunk=thunk)
```

It's a _fold left_:

| FP concept                   | Python realization                                                                     |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| Initial element (`init`)     | `first.execute()`&nbsp;—&nbsp;runs the first act, you already have an `ActionChain[T]` |
| Iteration (`xs`)             | `rest` (the argument `*`)                                                              |
| Reducer (`(acc, x) -> acc'`) | `reducer(chain, step) -> ActionChain[T]`                                               |
| Short-circuit                | `if chain.has_failed(): return chain`                                                  |
| Iterative composition        | `chain.then(step.__action__).failure(...).success(...).execute()`                      |

## Why `first` and `*rest` are separate

1. **Strict typing**: we guarantee at least one `ActionSuccess[T]`. `chain_actions()` with no args won't compile.
2. **Fold seed**: a fold needs an initial value (`ActionChain[T]`), so the first act has to be _executed_ before the loop. With `*all`, we'd have to invent an empty neutral `ActionChain[T]` ("the empty rail") and carry a "nothing done" state.
3. **Readability**: `chain_actions(action1.failure...success(...), action2.failure...success(...), ...)` reads naturally.

## Why nested functions

```python
def thunk() -> ActionChain[T]:
    def reducer(...): ...
    return reduce(reducer, rest, first.execute())
return ChainRunner(thunk=thunk)
```

- **`thunk` closes over `first` and `rest`**. So `chain_actions` is a _closure_ on its arguments. When `runner.run()` fires later, the `thunk()` replays those captures.
- **`reducer` lives _inside_ `thunk`**: it doesn't need to capture external variables, and keeping it here instead of at module level avoids leaking a private symbol to the rest of the package.

## Composition: `ChainRunner`

- **Store** a `ChainRunner` in a variable and reuse it.
- **Pass it as an argument**.
- **Multiply** a list of `ChainRunner`s: `[runner] * 5` runs the execution 5 times when the sequence plays. The Holy Book calls it out (Scenarios composability chapter, Repetitions section).
- **Aliasing** is trivial:

```python
click_confirm_cookies = drive_page(
    act(on_homepage, confirm_cookie_banner)
        .failure(log_error_with_current_url("Failed to dismiss banner..."))
        .success(log_success_with_current_url_and_take_screenshot("Banner dismissed!"))
)

# … later …
return [
    match_page(branches=[
        when(check_that_page.has_cookies_banner, name="cookies", then=[click_confirm_cookies]),
        when(check_that_page.has_not_cookies_banner, name="no cookies", then=[]),
    ]),
    drive_page(...),
]
```

## `drive_page` is a monomorphism of `chain_actions`

The framework's `drive_page` is just:

```python
def drive_page(
    first: ActionSuccess[TPOM], *rest: ActionSuccess[TPOM]
) -> ChainRunner[TPOM]:
    return chain_actions(first, *rest)
```

See [`06-drive-page.md`](06-drive-page.md) for why the alias exists.

## Annotated execution trace

Concrete case: three acts, the second fails.

```
runner = drive_page(act1, act2, act3)   # ⚠️  nothing executed yet

chain = runner.run()                    # ▶︎  execution:
  ┌─ first.execute()                      = ActionChain(ok=True, result=Ok(...))   ← fold's initial state
  │
  ├─ reduce(reducer, [act2, act3], <ActionChain above>)
  │      │
  │      ├─ reducer(<ok chain>, act2) :
  │      │     chain.then(act2.__action__)        → ActionStart        (success rail)
  │      │     .failure(act2.__failure_handler__) → ActionFailure
  │      │     .success(act2.__success_handler__) → ActionSuccess
  │      │     .execute()                         → action raises → Fail
  │      │                                        → failure_handler(exc)  ❌
  │      │                                        → ActionChain(ok=False, result=Fail(exc))
  │      │
  │      └─ reducer(<failed chain>, act3) :
  │            chain.has_failed() → True → return chain      ⚠️  act3 never executed
  │
  └─ return ActionChain(ok=False, result=Fail(exc))
```

## `functools`

```python
from functools import reduce
```

No `toolz`, no `funcy`, no homemade wrapper. Just `functools.reduce`&nbsp;—&nbsp;Python's canonical fold signature.

## Dedicated tests

[`tests/scenarios/test_railway_and_action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_railway_and_action_chain.py) covers:

- chaining 3+ acts in sequence,
- short-circuit after the 2nd failure (the 3rd never runs),
- `act` counting through `ActCounter` (the counter doesn't tick on short-circuited steps).
