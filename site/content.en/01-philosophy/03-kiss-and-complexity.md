---
title: "01.03 — KISS and ostentatious complexity"
description: "Ocarina's answer to the simplicity critique: KISS properly understood, the difference between simple and unsophisticated, and a refusal of ostentatious complexity."
weight: 3
date: 2026-05-20
series: ["philosophy"]
series_order: 3
tags: ["rop", "typing"]
---

# 01.03&nbsp;—&nbsp;KISS and ostentatious complexity

## The criticism that landed

First public feedback Ocarina got, _systematic_ per the author:

> The first "criticisms" were often the same: _"You're bragging about something that's very simple."_

The Holy Book takes its time answering. Three pillars: the **operating** nature of simplicity, the **simple ≠ unsophisticated** distinction, and the **rejection of every "creative" counter-proposal** that came in.

## Simple ≠ unsophisticated

> This is also why **KISS** (_Keep it simple, stupid_) is so misunderstood in the industry. Many assume "simple" means "unsophisticated." It would be hard to misread a principle more thoroughly.

What's "simple" is the **result** of work. A terminal state, not a starting one.

## The counter-proposals that got refused

The "First feedbacks" chapter walks through, **one by one**, the contributions other "peers" tried to push. Every one quoted _to be refused_:

> - Twisting Ocarina's ROP (_Railway Oriented Programming_) implementation until it lost all meaning, since they didn't even know what ROP is,
> - Dropping "_hooks_" and other so-called "_ninja techniques_" right in the middle of test steps,
> - Abandoning typing,
> - Rewriting in Rust over "performance" concerns,
> - Forcing their clueless take on lazy evaluation and _IoC_ down my throat like it's gospel,
> - "Explaining" imperative vs. declarative programming to me while spewing complete nonsense,
> - "Talking" to me about _event-driven programming_, while still spouting nonsense,
> - And worst of all, pontificating about a horrifying theory of "declarative object-oriented programming,"
> - Etc.

Each refusal traces back to an Ocarina _design choice_:

| Refusal                             | Ocarina choice                                                                                                                                                                                                                                                               |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Twisting ROP"                      | `Result[T]`, state machine `ActionStart → ActionFailure → ActionSuccess → ActionChain`, `Neutral*` for the failure rail. Strictly linear. Can't be hijacked. See [`../02-ocarina/03-railway/02-action-chain-states.md`](../02-ocarina/03-railway/02-action-chain-states.md). |
| "Hooks in the middle of test steps" | Hooks locked to `create_act(on_failure=…, on_run_effect=…, act_counter_effect=…)`. No injectable _global_ hook. See [`../02-ocarina/03-railway/05-create-act-hooks.md`](../02-ocarina/03-railway/05-create-act-hooks.md).                                                    |
| "Abandoning typing"                 | `mypy strict = true`, `ruff select = ALL`, PEP 695 generics everywhere, `pytest-mypy-plugins` to _test the types_. See [`../04-internal-tests/04-mypy-plugins-types.md`](../04-internal-tests/04-mypy-plugins-types.md).                                                     |
| "Rewriting in Rust"                 | Pure Python. The framework's subject is _readability_ and _trade vocabulary_, not raw performance&nbsp;—&nbsp;which doesn't depend on the orchestration language here.                                                                                                       |
| "IoC / lazy misunderstanding"       | `Effect`, `Thunk`, `ChainRunner`, `validate(...).execute()`, `Watcher.callback`&nbsp;—&nbsp;everything's lazy, IoC documented in the code. See [`../03-functional/`](../03-functional/README.md).                                                                            |
| "Declarative object-oriented"       | `@final` everywhere. No uncontrolled inheritance. Extension by **composition** (closures, project adapters).                                                                                                                                                                 |

## The compliment being sought

> And if, upon reading a first test scenario, the reaction is _"this is super simple…"_ it would be a shame to mean it as criticism: that is exactly the compliment being sought.
> Thank you.

That line is central. Simplicity of the result _is_ the quality metric. The inverse&nbsp;—&nbsp;"look how sophisticated this is"&nbsp;—&nbsp;gets labeled _narcissism_ in the Holy Book:

> **Narcissism** expresses itself through making everything shamefully complicated for the sole purpose of _domination_. Not through acquiring skills and simplifying processes, since the end result is total malfunction: chaos.

## Intolerance of failure, a narcissist tell

The Holy Book names a clinical category: intolerance of failure as the narcissist's signature in a testing environment.

> They can also be recognized by their _intolerance of failure_. They systematically want to show how much THEY have "thought of everything."
>
> Never any red with a narcissist, only green, only "ready to ship to production."

Ocarina goes the other way. **A documented failure is worth more.** Exactly the posture `ocarina-with-ai-example` holds, keeping its tests red on CURA's gaps (see [`../08-ai-example/05-security-gaps.md`](../08-ai-example/05-security-gaps.md)). From `CURA_TEST_STRATEGY.md`:

> Any failure outside the intentional gap fails and the expected chrome BFcache reds listed above (plus the `--workers 3` contention flake) is either a regression or a transient network error. Transient errors are auto-retried; persistent failures require investigation.

And the rule is engraved in the AI project's `CLAUDE.md`:

> Spec changes: `update-frd-and-tests` (FRD first, tests follow). **Gap tests are reframed, not flipped.**

## Practicality as the goal

The chapter's closing line:

> Instead of going _nerdy_, Ocarina focuses on solving _small problems_ without creating bigger ones.
> The conclusion drawn from this is: "Ocarina is practical."
> This is the purpose of Ocarina: its practicality.
