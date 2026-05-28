---
title: "01.01 — Flipping the problem"
description: "Ocarina's founding bet against Robot Framework and Cucumber: removing the barrier between those who code and those who define the tests."
weight: 1
date: 2026-05-20
series: ["philosophy"]
series_order: 1
---

# 01.01&nbsp;—&nbsp;Flipping the problem

## The observation

Every modern e2e testing framework was built on one implicit assumption: there's a **barrier** between _people who code_ and _people who define tests_. That barrier gets taken for granted&nbsp;—&nbsp;methodologically, organizationally, sometimes contractually.

> Most testing frameworks were built in a world where the barrier between "those who code" and "those who define tests" was real and structural.

The two _historic_ answers to that assumption show up in the Holy Book:

### Robot Framework

> _Robot Framework_ tried to **work around it** with a _DSL_ (_Domain Specific Language_), complete with **its own format** and **its own plugin ecosystem**. In doing so, RF de facto imposes its own standards: that's the immediate cost of its promise.

The mechanic: swap the complexity of code for the complexity of **a different code**. The entry ticket isn't waived&nbsp;—&nbsp;it's _relocated_. Now you've got to learn the RF syntax, its ecosystem of _libraries_ and _resources_, and its orchestration model.

### Cucumber

> _Cucumber_ tried the same with _Gherkin_: a "natural" language that, in practice, **constrains everyone without truly freeing anyone**. Cost: **a permanent translation layer, Gherkin/code desynchronization**.

The mechanic: build an _illusion_ of natural language that actually has a strict grammar and limited semantics. The cost isn't the language&nbsp;—&nbsp;it's the **permanent translation layer** between Gherkin and Step Definitions code, which drifts the moment nobody's watching.

## The opposite bet

Instead of _dressing up_ the barrier, Ocarina bets that **it's going away**:

> **Ocarina bets on the opposite:** this barrier will disappear. This is a non-debate around which everyone has tied a noose with needlessly complicated tools, mistaking them for solutions. Impact: **operational disaster** the moment a need arises that can't be expressed within a "framework" that is NOT truly generic.

And:

> And the worst part: **all these technologies will keep evolving in the same direction**. NONE of them will make this _shift_, because it would require a paradigm change, **a return to fundamentals that directly contradicts their entire value proposition**.

## AI is the bridge, not the DSL

The Holy Book's rhetorical lock on this point:

> With AI, and tools like _Claude Code_, this bet grows stronger every day. The bridge between technical and non-technical people is no longer an abstraction layer.
>
> **It's AI itself. AI that works on raw data.**

Observable design consequences in the code:

| Design choice                                             | Why it follows from the bet                                               |
| --------------------------------------------------------- | ------------------------------------------------------------------------- |
| No text DSL (no `.robot` files, no `.feature` files)      | AI handles typed Python better than a meta-language with its own grammar. |
| `ruff` ALL + `mypy` strict                                | Type and lint the raw data harder, the AI consumes it more reliably.      |
| `CLAUDE.md`, `CLAUDE.slim.md` exposed                     | AI is a first-class client of the docs.                                   |
| 40+ `skills/` versioned on GitHub                         | LLM-friendly procedures are artifacts like any other.                     |
| `llms.txt` / `llms-full.txt` generated at VitePress build | The site _actively publishes_ to LLMs.                                    |

The practical embodiment is the [`ocarina-with-ai-example`](../08-ai-example/README.md) repo: a _real_ e2e suite **99% written by Claude Code**, with intelligence split 50/50 between the author and the AI.

## The cost of other people's "creativity"

The Holy Book spells out why DSL leveling isn't neutral:

> The biggest cost is a **race to the bottom: fewer options, and a "flexibility" that can only be achieved by _fighting_ your _tools_ rather than using _solutions_**.

> Yet what remains is the need for test code that is **readable, traceable and flexible** in its most **raw** form.

The word _raw_ matters. It comes back elsewhere ("raw data", "the raw data"), and it's the axis Ocarina extends along toward AI. See [`05-political-stance.md`](05-political-stance.md), "Anti No-Code" section.

## What it means for Ocarina's architecture

| Philosophical stance    | Architectural consequence                                                                                                        |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| No text DSL             | No parser, no alternative _runtime_. Pure Python.                                                                                |
| No translation layer    | No Gherkin, no Step Definitions. The `(TPOM) -> TPOM` connector is the smallest unit, written in Python.                         |
| AI as the chosen bridge | A big chunk of the docs is _explicitly_ aimed at LLMs (`llms.txt`, `skills/`, `CLAUDE.md`).                                      |
| No plugin ecosystem     | No pytest plugin. Ocarina ships its own runner. The whole Python ecosystem stays usable, frictionless, at the user's discretion. |
| Max strictness          | `ruff ALL`, `mypy strict`, `@final` everywhere, `noqa` always explicit and local.                                                |
