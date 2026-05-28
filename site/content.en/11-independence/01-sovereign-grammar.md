---
title: "11.01 — Sovereign grammar"
description: "Ocarina's sovereign grammar: no imposed DSL or plugin ecosystem, extension happens through composition and never through inheritance."
weight: 1
date: 2026-05-20
series: ["independence"]
series_order: 1
---

# 11.01&nbsp;—&nbsp;Sovereign grammar

> No imposed DSL. No plugin ecosystem. Extension by **composition**, never by inheritance.

## Vision

Holy Book quote (chapter "_What is Ocarina?_"):

> _What if delegating one's grammar to "standards" had never been a good idea?_
>
> The real gap in E2E testing **is not about imposing the "best" Newspeak**.  
> Short answer: Ocarina is **extensible**.
>
> Any verb and conjunction can be created, all governed by **strict rules that keep the whole thing deeply consistent**.
>
> What remains is to guarantee **traceability and robustness**.

## "_Return a `ChainRunner`_"

Holy Book quote (chapter "_Extensibility_"):

> The test-scenario grammar is built on a single type: `ChainRunner[T]`. A scenario is a `list[ChainRunner]` executed sequentially, short-circuiting on the first failure. `drive_page` is just a thin wrapper around `chain_actions`, which builds a `ChainRunner`. Any function returning a `ChainRunner` plugs in without touching the framework.

**A single extension type**: `ChainRunner[T]`. Anything returning one is composable.

## "_match_page added after the fact_"

The Holy Book explicitly mentions that `match_page` is a _post-design_ addition:

> `match_page` was added after the fact to handle variable-state pages (optional banners, A/B tests, maintenance pages...): it evaluates conditions in order and runs the first matching branch.

Proof by example: if `match_page` could be added without touching the existing DSL, so can `skip_if`, `repeat_n`, or anything else. See [`../02-ocarina/03-railway/07-match-page-when.md`](../02-ocarina/03-railway/07-match-page-when.md)

## "_skip_if_"

Holy Book quote:

> Another example would be **`skip_if`**: intentionally bypassing a portion of the scenario on a condition without failing (would return a neutral `Ok`), useful for environment or data-dependent optional steps.

A hypothetical idiom to implement yourself. Trivial implementation: a `ChainRunner[Any]` that invokes the condition, then either runs the branch or returns `Ok(None)`.

The user can write it in their project **right now**, without waiting for an Ocarina release.

## Project adapters

The user project **never uses** Ocarina classes directly&nbsp;—&nbsp;it wraps them in adapters:

```python
# project/lib/ext/ocarina/adapters/agnostic/act.py
def act(pom: TPOM, action: Callable[[TPOM], TPOM]) -> ActionStart[TPOM]:
    def failure_hook(pom: TPOM, exc: Exception) -> Fail:
        # ... project policy ...
    return create_act(pom, action, on_failure=failure_hook)


# project/lib/ext/ocarina/adapters/selenium/test_suite.py
class TestSuite(OriginalTestSuite[WebDriver]):
    def __init__(self, *, name, tests, drivers_pool, ...):
        super().__init__(
            ...,
            max_retries_per_test=8,                    # ← pinned for the project
            transient_errors=transient_errors,         # ← project-scoped
            ...
        )
```

Every project has **its own framework** on top of the framework. Grammatical sovereignty made concrete.

## No forced version-locking

If the framework evolves (e.g. adds a `max_retries_per_test` parameter), the project:

- Either accepts the default (nothing to do).
- Or updates its `TestSuite` adapter to pin a new value.

No cascading breaking changes across the whole project.

## "_Narrowing_"

The Holy Book (chapter "_First steps_", `TestSuite` adapter section):

> This is the most important adapter to understand. `TestSuite` natively exposes a large number of parameters. The goal of this adapter is to create a **facade** around it: some values are hardcoded once and for all, others are optionally exposed with sensible defaults. _Narrowing_.

The project adapter **shrinks** Ocarina's API surface to what the project needs.

## No plugin ecosystem

See [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md):

> _Robot Framework_ tried to dodge that with a _DSL_ (_Domain Specific Language_), including **their own format** and **their own plugin ecosystem**. So RF de-facto imposes its own standards: that's the immediate cost of its promise.

Ocarina **refuses** to have a plugin ecosystem.

| With ecosystem                                                 | Without                            |
| -------------------------------------------------------------- | ---------------------------------- |
| Plugin marketplace, versions to track                          | No marketplace, just code          |
| Risk of plugin breakage on upgrade                             | No risk                            |
| De-facto imposed standards ("_how to write a good RF plugin_") | Freedom of pattern                 |
| Hidden dependencies                                            | Everything is local to the project |

The "plugin" you're looking for is `pip install <your lib>`. Most of the time, no need to reinvent the world.

## Grammar **governed by strict rules**

Quote:

> governed by **strict rules that keep the whole thing deeply consistent**.

| Rule                                       | In practice                                |
| ------------------------------------------ | ------------------------------------------ |
| `ChainRunner[T]` for every extension point | Type checking enforces consistency         |
| `@final` everywhere in the DSL             | No user inheritance, mandatory composition |
| `mypy strict = true`                       | No "freedom" of weak typing                |
| `ruff select = ["ALL"]`                    | No "freedom" of style                      |
| Narrowing project adapters                 | No default API surface, just what's needed |

**Grammatical freedom** lives on top of strict discipline. Rigor is what makes freedom possible.

## λ-calculus

See [`../01-philosophy/04-citations-and-influences.md`](../01-philosophy/04-citations-and-influences.md):

> What was thought since the 1930s, **since the invention of λ-calculus**, is finally scalable at the scale we always wanted to give it.

λ-calculus is the ultimate example of sovereign grammar: extremely minimal core (`λx.M`), strict rules (β-reduction, α-conversion, η-conversion), everything else composes. No "_λ plugin_".

Ocarina takes the same stance.

## Consistency with AI

A sovereign, statically typed grammar is **readable by an AI** because it's small and governed by algebraic rules that make sense. No ad-hoc DSL to parse, no _mental models_ to fight.

That's what makes `ocarina-with-ai-example` feasible: Claude reads the `CLAUDE.md`, understands the strict rules, applies them. It _could not_ collaborate as well on an RF project with exotic plugins, because it would have to learn each plugin and miss a lot of "_tacit_" rules.
