---
title: "12.15 — Typing, ISTQB, Reinforcement Learning, probes: why AI works in Ocarina"
description: "Why AI works in Ocarina: strict typing, ISTQB alignment and probes, a mechanism borrowed from reinforcement learning, constraint plus reward."
weight: 15
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 15
tags: ["rop", "istqb", "typing"]
---

# 12.15&nbsp;—&nbsp;Typing, ISTQB, Reinforcement Learning, _probes_: why AI works in Ocarina

> Why so much **obsession** over strict typing, formalizing every interface, alignment on **ISTQB**, refusing to execute an assertion without having _observed_? The mechanism is borrowed from **Reinforcement Learning**: an agent only progresses under **constraint** + **reward signal**.

## 1. A naked LLM is just a bad collaborator

An LLM without a structured environment is:

- _Optimistic_&nbsp;—&nbsp;it assumes its code works.
- _Persuasive_&nbsp;—&nbsp;its _output_ is convincing even when wrong.
- _Memoryless_&nbsp;—&nbsp;it forgets conventions between sessions.
- _Feedbackless_&nbsp;—&nbsp;it has no way to know it was wrong.
- _Loves what it deems "most likely"_&nbsp;—&nbsp;it drifts toward _popular_ patterns, not _correct_ ones.

**Without an environment, an LLM is an over-confident junior dev** producing code that _looks_ right, breaks in prod, and learns nothing from the failure.

## 2. Rebuilding a _feedback loop_

| Signal                           | Effect                              | Ocarina tool                                                     |
| -------------------------------- | ----------------------------------- | ---------------------------------------------------------------- |
| Fast **negative feedback**       | "_What you just produced is wrong_" | **mypy strict**, algebraic errors, runtime probes, `Result.Fail` |
| Explicit **positive convention** | "_Here's what to do_"               | **ISTQB vocabulary**, `CLAUDE.md`, versioned _skills_            |

It's a **Reinforcement Learning loop**.

## 3. _Reinforcement Learning_ as theoretical frame

### Origins

| Year | Contribution                                                  | Author(s)                                      |
| ---- | ------------------------------------------------------------- | ---------------------------------------------- |
| 1948 | **Cybernetics**, feedback control                             | Norbert Wiener                                 |
| 1957 | **Dynamic Programming**                                       | Richard Bellman                                |
| 1989 | **Q-learning**&nbsp;—&nbsp;tabular RL (journal article: 1992) | Chris Watkins                                  |
| 1992 | **REINFORCE**&nbsp;—&nbsp;policy gradient                     | Ronald Williams                                |
| 1998 | Canonical book "_Reinforcement Learning: An Introduction_"    | Sutton & Barto                                 |
| 2013 | **DQN**&nbsp;—&nbsp;Deep Q-Network on Atari                   | Mnih, _et al._ (DeepMind)                      |
| 2016 | **AlphaGo** beats Lee Sedol                                   | DeepMind                                       |
| 2017 | **PPO**&nbsp;—&nbsp;Proximal Policy Optimization              | Schulman, _et al._ (OpenAI)                    |
| 2017 | **RLHF**&nbsp;—&nbsp;RL from Human Preferences                | Christiano, Leike, Brown, Martic, Legg, Amodei |
| 2022 | **InstructGPT** → ChatGPT                                     | OpenAI                                         |
| 2022 | **Constitutional AI** (CAI)                                   | Anthropic&nbsp;—&nbsp;Bai _et al._             |

### RL basics

```
   ┌─────────────┐    action     ┌─────────────┐
   │             │──────────────>│             │
   │   AGENT     │               │ ENVIRONMENT │
   │             │<──────────────│             │
   └─────────────┘    state +    └─────────────┘
                      reward
```

- **State** (`state`): what the agent sees.
- **Action** (`action`): what it chooses to do.
- **Reward** (`reward`): signal saying if it's good.
- **Policy** (`π`): the agent's strategy&nbsp;—&nbsp;how it picks its action.

With RL, the agent learns by **exploring** the action space and **reinforcing** the actions leading to better reward.

### Analogy

| Classical RL   | LLM in Ocarina                                                             |
| -------------- | -------------------------------------------------------------------------- |
| Action space   | All possible characters / tokens                                           |
| State          | The prompt + what the LLM has already answered (the _partial output_)      |
| Delayed reward | Green mypy, tests match expectations, PRs merged                           |
| Episode        | A dev session                                                              |
| Policy         | Distribution over tokens conditioned on context (weights + prompt + tools) |

What separates a _useful_ LLM from one that hallucinates is the **density of the reward signal**. The faster and more precise the signal, the more the agent _converges_ toward good patterns.

## 4. Strict typing as RL signal

`mypy --strict` is an **immediate reward signal**:

```
+----------------+
| LLM produces   | <─────────────────────────────────────────────────┐
| Python code    |                                                   │
+--------+-------+                                                   │
         │                                                           │
         v                                                           │
+----------------+                                                   │
| mypy strict    |   <- binary reward signal                         │
| runs in        |      pass / fail                                  │
| < 5 seconds    |      enriched with formal type errors             │
+--------+-------+                                                   │
         │                                                           │
         v                                                           │
   FAIL ─┤───── reads the error, fixes ──────────────────────────────┤
         │                                                           │
   PASS ─┴───── continues ───────────────────────────────────────────┘
                   │
                   v
                 ships
```

| pytest only                                         | mypy strict                                            |
| --------------------------------------------------- | ------------------------------------------------------ |
| Code launched in prod                               | Error caught at static analysis                        |
| Reward arrives when it's already too late (prod/CI) | Reward arrives in _seconds_ from the local environment |
| Reward is _flaky_ (random test)                     | Reward is _deterministic_                              |
| The agent doesn't know _what_ to fix                | The mypy error points to the exact line                |
| Learns to _overcome_ flakes                         | Learns the _correct grammar_                           |

`mypy --strict` is therefore, in the RL grid, **the most efficient reward signal possible for a Python-dev LLM**.

## 5. ISTQB as constraint on the _action space_

**ISTQB** (_International Software Testing Qualifications Board_) standardizes the _test vocabulary_.

Ocarina **maps 1:1** this hierarchy in its code:

| ISTQB         | Ocarina (class)  |
| ------------- | ---------------- |
| Test Step     | `act` (callable) |
| Test Case     | `Test`           |
| Test Suite    | `TestSuite`      |
| Test Campaign | `TestCampaign`   |
| Test Cycle    | `TestCycle`      |

> **Note (_Test Step_):** In the ISTQB glossary, the _test step_ isn't a standalone hierarchical level but an internal component of a _Test Case_ (the action sequence to execute). Ocarina implements it as such (`act`).

> **Note (_Test Campaign_):** The term isn't formally defined in the official ISTQB glossary, unlike the four others. It is, however, in common use and immediately understood by test professionals; it appears notably in ISO 29119 and in most test-management tools (Xray, TestRail, Zephyr). Its inclusion here belongs to shared business vocabulary rather than strict ISTQB terminology.

- The _action space_ is **finite, named, documented**.
- The prompt "_generate a test suite for feature X_" is **unambiguous**.
- Without ISTQB, the pytest equivalent prompt would be: "generate a module with `test_*`functions in the right directory, with the right fixtures in`conftest.py`, in the right scope, respecting the markers"&nbsp;—&nbsp;_all implicit decisions, hence all hallucination opportunities_.

With ISTQB, only one decision: _which tests to put in it_. The _action space_ went from **hundreds of decisions** to **one**.

It is, in RL, **the reduction of exploration space by injecting _domain knowledge_**.

## 6. Why "_formally wired_" everywhere

Ocarina leaves **no hole** in the typing:

- `Result[T]` is parameterized → you always know which `T` is in play.
- `ChainRunner[T]` too.
- Hooks are `Callable` with explicit signatures.
- ...

**No implicit decisions**. When an LLM reads the code, it **can't** be wrong about the expected type: there's only one possible answer, dictated by the _type checker_.

That's what's called, in _type design_, **"_making illegal states unrepresentable_"** (Yaron Minsky, Jane Street). Ocarina applies this principle systematically.

## 7. Why not execute when AI generates a dataset

Concrete case. An LLM produces:

```python
# Pseudo code (not Ocarina)
def test_login_succeeds():
    user = "'; DROP TABLE users; --"
    password = "lol"

    open_login_page()
    fill(user, password)
    click_submit()

    assert current_url() == "/dashboard"
```

It's the result of a _prompt injection_ / _data poisoning_ attack: the LLM shouldn't be doing this.  
If this data reaches execution:

- The `user` field contains an SQL _payload_.
- The target application is compromised, not functionally tested.
- The agent produced an attack, not a test. **It's forbidden.**

### Empirical first

**Empirical**: we _observe_ what's on the page **before** deciding.  
**Probes** _read_ the page and draw findings **before** formalizing a test:

The returned _information_ is rich. The agent _learns_ something at each failure.

### Assertive after

Once we _know_ we're on the right _state_, we can **affirm**:

```python
# Pseudo code (not Ocarina)
def assert_dashboard_loaded(driver: Driver) -> Result[None]:
    welcome = driver.find_element(By.CSS, ".welcome")
    if welcome.text == "Welcome, John":
        return Ok(None)
    return Fail(Reason.bad_welcome_text(welcome.text))
```

It's the **Ocarina sequence**:

```
        ┌─────────────────────────────────────────────┐
        │ 1. PROBE: what do I see?                    │
        └────────────────────┬────────────────────────┘
                             v
        ┌─────────────────────────────────────────────┐
        │ 2. DECIDE: given the state, which action?   │
        └────────────────────┬────────────────────────┘
                             v
        ┌─────────────────────────────────────────────┐
        │ 3. ACT: execute the chosen action           │
        └────────────────────┬────────────────────────┘
                             v
        ┌─────────────────────────────────────────────┐
        │ 4. ASSERT: verify the final invariant       │
        └─────────────────────────────────────────────┘
```

Compared to the _assertive-only_ sequence:

```
        ┌────────────────────────────┐
        │ ACT: do what you believe   │
        └──────────────┬─────────────┘
                       v
        ┌────────────────────────────┐
        │ ASSERT: blow up            │
        └────────────────────────────┘
```

AI works **well** with the first, **poorly** with the second. Ocarina's philosophy is **mathematically compatible** with what RL teaches us about learning: no learned behavior without _observed state_.

## 8. Recap

| Ocarina choice       | Consequence for AI                                                                 |
| -------------------- | ---------------------------------------------------------------------------------- |
| `mypy --strict`      | Reward signal in < 5s, deterministic, precise line                                 |
| ROP (`Result[T]`)    | Forces the LLM to _handle_ the error                                               |
| ISTQB                | Small, unambiguous _action space_                                                  |
| No `async`           | Fuck you                                                                           |
| No pytest plugin     | A single grammar, no mystical fixtures morphing into every possible implementation |
| Mandatory probes     | The LLM performs _observation_ before _affirmation_                                |
| Typed hooks          | No hidden side effects                                                             |
| `CLAUDE.md` / skills | Externalized memory, explicit conventions                                          |
| `llms.txt`           | Index readable by AI in one prompt                                                 |
| MIT, 1 dep           | Auditable by the LLM                                                               |

## 9. Related reading

- [`14-real-ai-in-ocarina.md`](14-real-ai-in-ocarina.md)&nbsp;—&nbsp;what AI is, what Ocarina exposes to it.
- [`13-lambda-calculus-rop-origins.md`](13-lambda-calculus-rop-origins.md)&nbsp;—&nbsp;the typical theory underlying the DSL.
- [`../02-ocarina/03-railway/`](../02-ocarina/03-railway/)&nbsp;—&nbsp;the concrete ROP implementation.
- [`../02-ocarina/06-scenario.md`](../02-ocarina/06-scenario.md)&nbsp;—&nbsp;`drive_page` and `match_page` detailed.
- [`../08-ai-example/`](../08-ai-example/)&nbsp;—&nbsp;the AI suite + its _hard-won rules_.
