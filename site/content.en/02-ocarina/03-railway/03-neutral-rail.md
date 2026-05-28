---
title: "02.03.03 — The failure rail: NeutralAction*"
description: "Ocarina's failure rail: the NeutralAction classes that absorb actions chained after a failure, with no user-side if."
weight: 3
date: 2026-05-20
series: ["railway"]
series_order: 3
tags: ["ocarina"]
---

# 02.03.03&nbsp;—&nbsp;The failure rail: `NeutralAction*`

> Edge case in the builder: what happens when you _chain_ an action onto an `ActionChain` that has already failed?

## Why _Neutral_ classes rather than a user-side `if`

When you chain an action onto an already-failed `ActionChain`, you slide into three _Neutral_ classes that honor the same API but do nothing.

Picture the DSL without this. User code would look like:

```python
chain = act1.failure(h).success(h).execute()

if chain.is_ok():
    chain = chain.then(act2).failure(h).success(h).execute()

if chain.is_ok():
    chain = chain.then(act3).failure(h).success(h).execute()
```

_Imperative_, unreadable, and the whole point of the DSL is gone. The neutral rail keeps the writing flat:

```python
chain = (
    act1.failure(h).success(h).execute()
    .then(act2).failure(h).success(h).execute()
    .then(act3).failure(h).success(h).execute()
)
```

Every action is **always** called syntactically. But the moment `chain.then(act2)` lands on a failed `ActionChain`, it returns a `NeutralActionStart`. The rest of the chain (`.failure → .success → .execute`) **flows through** the neutrals doing nothing.

## Code of the three classes

```python
@final
class NeutralActionStart[T]:
    def __init__(self, *, result: Result[T] | None) -> None:
        self._result = result

    def failure(self, *args, **kwargs) -> NeutralActionFailure[T]:
        return NeutralActionFailure(result=self._result)


@final
class NeutralActionFailure[T]:
    def __init__(self, *, result: Result[T] | None) -> None:
        self._result = result

    def success(self, *args, **kwargs) -> NeutralActionSuccess[T]:
        return NeutralActionSuccess(result=self._result)


@final
class NeutralActionSuccess[T]:
    def __init__(self, *, result: Result[T] | None) -> None:
        self._result = result

    def execute(self) -> ActionChain[T]:
        return ActionChain(has_failed=True, result=self._result)
```

### 1. `*args, **kwargs` ignored

```python
def failure(self, *args, **kwargs) -> NeutralActionFailure[T]:
```

Neutrals swallow _any argument_&nbsp;—&nbsp;handler, kwargs&nbsp;—&nbsp;and drop them on the floor. The `# noqa: ARG002` in the source on `*args` says it out loud: we don't read it, on purpose.

### 2. Same return types as the active classes

`NeutralActionStart.failure` returns `NeutralActionFailure`, exactly like `ActionStart.failure` returns `ActionFailure`. That isomorphism is what unlocks fluent composition.

### 3. `result: Result[T] | None`

The `None` covers chains **interrupted before** producing a result. Spelled out in the docstring:

> ActionChain: `result` may be Ok, Fail, or None if skipped.

### 4. Propagating the initial `result`

The `Fail` from the first failure is **propagated as-is** all the way through. The initial `Fail`'s `result` is what `chain.result()` returns at the end. No wrapping, no re-incarnation.

### 5. `has_failed=True` is frozen

Once on the failure rail, there's **no way off**.

### 6. `@final` here too

No extending it.

## The switch point: `ActionChain.then(...)`

```python
def then(
    self, action_or_start: Action[T] | ActionStart[T]
) -> ActionStart[T] | NeutralActionStart[T]:
    if self._has_failed:
        return NeutralActionStart(result=self._result)

    if isinstance(action_or_start, ActionStart):
        action = action_or_start.__action__
    else:
        action = action_or_start

    return ActionStart(action)
```

1. **Accepts `Action[T] | ActionStart[T]`**: pass an `Action` directly or an `ActionStart` (we then pull its `__action__`). Useful for `chain_actions`, which iterates over `ActionSuccess` instances and uses their `__action__`.
2. **Return type is a union**: `ActionStart[T] | NeutralActionStart[T]`. The checker handles both the same way&nbsp;—&nbsp;both expose `.failure(...)`.
3. **O(1) branch**: a `bool`, not an `isinstance`.

## Timeline

Case: three acts in a `drive_page`, the second fails.

```
t0 : start
t1 : act1.execute()             → Ok                → ActionChain(has_failed=False, result=Ok)
t2 : chain.then(act2)           → ActionStart       (success rail)
t3 : .failure(h)                → ActionFailure
t4 : .success(h)                → ActionSuccess
t5 : .execute()                 → action() raises → Fail
                                → failure_handler(exc)        ❌ FIRE
                                → ActionChain(has_failed=True, result=Fail)
t6 : chain.then(act3)           → NeutralActionStart          ⚠️  switching to failure rail
t7 : .failure(h)                → NeutralActionFailure        (h IGNORED)
t8 : .success(h)                → NeutralActionSuccess        (h IGNORED)
t9 : .execute()                 → ActionChain(has_failed=True, result=<the Fail from t5>)
```

Subtle point: the _third_ act's handlers are **never called**. Not the failure one, not the success one. That's _short-circuit_ taken literally.

## Why not `Optional` everywhere

You could picture a variant without `NeutralAction*`, where each builder method checked `if self._already_failed: ...`. The price tag:

- One extra `bool` per class.
- A _runtime_ check at every method.
- An API that's harder to reason about&nbsp;—&nbsp;every method has two behaviors.

The _three neutral classes_ are easier to read (one class, one behavior) and faster (no check). Textbook KISS&nbsp;—&nbsp;see [`../../01-philosophy/03-kiss-and-complexity.md`](../../01-philosophy/03-kiss-and-complexity.md).

## Tests dedicated to the neutral rail

[`tests/scenarios/test_railway_and_action_chain.py`](https://github.com/mojo-molotov/ocarina/blob/main/tests/scenarios/test_railway_and_action_chain.py) hits this exact point, e.g.:

```python
@allure.title("A drive_page with a mid-failure short-circuits subsequent acts")
def test_drive_page_short_circuits_after_failure() -> None:
    pom = RecordingPOM(raise_on={"second"})
    runner = drive_page(
        create_act(pom, lambda p: p.step("first")).failure(lambda _: None).success(lambda: None),
        create_act(pom, lambda p: p.step("second")).failure(lambda _: None).success(lambda: None),
        create_act(pom, lambda p: p.step("third")).failure(lambda _: None).success(lambda: None),
    )
    chain = runner.run()
    assert chain.has_failed()
    assert pom.calls == ["first", "second"]   # ✅ "third" never called
```
