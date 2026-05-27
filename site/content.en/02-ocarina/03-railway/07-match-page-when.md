---
title: "02.03.07 — match_page / when"
weight: 7
date: 2026-05-20
series: ["railway"]
series_order: 7
tags: ["ocarina"]
---

# 02.03.07&nbsp;—&nbsp;`match_page` / `when`

> Source file: [`src/ocarina/dsl/testing_with_railway/match_page.py`](https://github.com/mojo-molotov/ocarina/blob/main/src/ocarina/dsl/testing_with_railway/match_page.py)
>
> Bolted onto the framework **after the fact**. The Holy Book puts it bluntly: "_`match_page` and `when` were added after the fact; the Igoristan was so random that the use case forced itself onto us. Their implementation was simple, proof of the grammar's flexibility: other analogous structures could follow just as easily._"

## The problem

Some pages render differently:

- Cookies banner showing or not.
- A/B test serving two UI variants.
- Degraded mode (maintenance page) instead of the real page.
- Anti-bot captcha.
- …

The scenario needs to **branch** without breaking the ROP chain.

## User-facing API

```python
match_page(
    branches=[
        when(check_that_page.has_cookies_banner,
             name="Has cookies banner",
             then=[drive_page(act(on_homepage, confirm_cookie_banner)
                              .failure(...)
                              .success(...))]),
        when(check_that_page.has_not_cookies_banner,
             name="Has NOT cookies banner",
             then=[]),
    ],
)
```

- **`when(condition, then=..., name=...)`**: declares a branch.
- **`condition`** is a `Thunk[bool]`&nbsp;—&nbsp;a no-arg function returning `True`/`False`. Runs _at runtime_.
- **`then`** is a `TestChain` (a list of `ChainRunner`).
- **`name`** shows up in logs.

> Best practice: don't write a `not has_X()` lambda. Declare two separate _matchers_ (`has_cookies_banner` / `has_not_cookies_banner`) so timeouts can be tuned per branch&nbsp;—&nbsp;two cases, potentially two different timeouts.

## Code: `When`

```python
@final
@dataclass(frozen=True)
class When:
    condition: Thunk[bool]
    then: TestChain
    name: str = ""

when = When        # call alias
```

The `when = When` trick is sleek: the _dataclass constructor_ doubles as a "function"&nbsp;—&nbsp;`when(cond, then=[...], name="...")` is `When(...)`, just spelled differently.

## Exception policy

> - Exceptions listed in `raise_exceptions` are re-raised immediately.
> - All other exceptions raised by `branch.condition()` are interpreted as a non-matching condition (False).

Mechanic: if `condition()` raises a `WebDriverException` (say the page is frozen), you might want either:

- Treat it as "this branch doesn't match" and try the next one (permissive).
- Re-raise so retry kicks in (strict).

The sane move is to pass `raise_exception=transient_errors` to `create_match_page`.

## Code: `_match_page_builder`

```python
def _match_page_builder(*, raised_exceptions: tuple[type[BaseException], ...] = ()):

    def _match_page(logger: ILogger, branches: Sequence[When]) -> ChainRunner[Any]:

        def _thunk() -> ActionChain[Any]:
            for index, branch in enumerate(branches):
                label = branch.name or f"branch[{index}]"
                try:
                    matched = branch.condition()
                    logger.debug(f"match_page: '{label}' -> {matched}")
                except raised_exceptions as exc:
                    logger.exception("match_page: raising exception...", exc=exc)
                    raise
                except Exception as exc:
                    logger.exception(f"match_page: '{label}' raised", exc=exc)
                    matched = False

                if matched:
                    logger.info(f"match_page: '{label}' matched.")
                    return _run_branch(branch.then)

            return ActionChain(
                has_failed=True,
                result=Fail(error=NoMatchingBranchError(
                    f"No when() branch matched out of {len(branches)} candidate(s)."
                )),
            )

        return ChainRunner(thunk=_thunk)

    return _match_page
```

1. **Sequential eval, first-match wins**: the first `True` branch runs, the rest are skipped.
2. **Three-tier logging**: `debug` for the check, `info` for the match, `exception` for the raise.
3. **`try/except` is ordered**: explicitly re-raised exceptions get caught first. Python evaluates `except` clauses in order.
4. **No match → `Fail(NoMatchingBranchError(...))`**. The scenario hops onto the failure rail. Same grammar as ROP everywhere else.

## `_run_branch`

```python
def _run_branch(runners: TestChain) -> ActionChain[Any]:
    last: ActionChain[Any] | None = None
    for runner in runners:
        chain = runner.run()
        last = chain
        if chain.has_failed():
            return chain
    if last is None:
        return ActionChain(has_failed=False, result=Ok(value=None))
    return last
```

1. **No runner**: return `Ok(None)` (empty branch → trivial success).
2. A runner **fails**: immediate short-circuit, return the chain.
3. Else: return the last `ActionChain` (success).

## `create_match_page`

```python
def create_match_page(*, raised_exceptions: tuple[type[Exception], ...] = ()):
    def _match_page(*, logger: ILogger | None = None, branches: Sequence[When]):
        _logger = MutedLogger() if logger is None else logger
        return _match_page_builder(raised_exceptions=raised_exceptions)(
            logger=_logger, branches=branches,
        )
    return _match_page
```

Pattern: **factory of a factory (_woop woop!_)**. The project calls `create_match_page(raised_exceptions=transient_errors)` once and stashes the result as `match_page`. Every scenario call shares the same exception policy.

Detail: no `logger`? Use a `MutedLogger`. **Null Object Pattern**, zero noise.

## Convention

```python
# lib/ext/ocarina/adapters/agnostic/match_page.py
from ocarina.dsl.testing_with_railway.match_page import create_match_page
from constants.sys.transient_errors import transient_errors

match_page = create_match_page(raised_exceptions=transient_errors)
```

→ Every "transient" exception (HTTP error page, missing verification page, etc.) **propagates** instead of getting swallowed as a "non-match." Without this wiring, a test that should retry never retries.

## Full execution diagram

```
match_page(branches=[
    when(cond_A, name="a", then=[runner_A1, runner_A2]),
    when(cond_B, name="b", then=[runner_B1]),
])

▼

ChainRunner(thunk=_thunk)
  └─ .run()
        │
        ▼
   for branch in branches :
       ┌─ try : matched = branch.condition()
       │      log.debug(f"match_page: 'a' -> True/False")
       ├─ except raised_exceptions : log + RE-RAISE  (transient_error → test retried)
       ├─ except Exception         : log + matched = False
       │
       └─ if matched :
              log.info(f"match_page: 'a' matched.")
              return _run_branch(branch.then)
                          │
                          ▼
                 for runner in then :
                     chain = runner.run()
                     if chain.has_failed() : return chain (short-circuit)
                 return last_chain or Ok(None)

   (no branch matched)
   return ActionChain(has_failed=True,
                      result=Fail(NoMatchingBranchError(...)))
```

## The Holy Book spec

Excerpt from "First scenarios":

> `match_page` sits at the same level as `drive_page` and is chainable. Its `then` command again expects a chain of `drive_page` or `match_page`. Branches are defined by `when`.

And:

> `match_page` and `when` were added after the fact; the Igoristan was so random that the use case forced itself onto us. Their implementation was simple, proof of the grammar's flexibility: other analogous structures could follow just as easily.

That flexibility proof matters&nbsp;—&nbsp;it's the framework's meta-argument. The DSL extends by composition ("return a `ChainRunner`") without anyone touching the framework. See [`../../11-independence/01-sovereign-grammar.md`](../../11-independence/01-sovereign-grammar.md)

## Holy Book recommendations

> A _matcher_ minimally checks whether something is true, taking the fastest path.

And:

> ⚠️ Skip the raw `.find_element(s)`&nbsp;—&nbsp;that's the express lane to flakiness.
>
> A 5-second cap won't hurt a horizontally scaled batch, so don't fear it here. And don't dress up a `verify` as a _matcher_: **they're two different tools.**

| Tool                              | Goal                               | Typical timeout         |
| --------------------------------- | ---------------------------------- | ----------------------- |
| `verify(...)`                     | Guarantee you're on the right page | global `--wait-timeout` |
| matcher (`has_cookies_banner`, …) | Identify the right branch          | short (1-5 s)           |
