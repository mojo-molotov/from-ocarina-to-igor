---
title: "12.14 — AI, and how Ocarina applies it for real"
description: '"AI-powered" became a totally idiotic marketing slogan in 2023-2026: 99% of products claiming it bolt a chat.completions endpoint onto an existing product. Ocarina proposes, on the contrary, a software infrastructure designed so an AI can contribute like a senior developer. ocarina-with-ai-example is the proof by example.'
weight: 14
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 14
tags: ["typing"]
---

# 12.14&nbsp;—&nbsp;AI, and how Ocarina applies it _for real_

> "_AI-powered_" became a totally idiotic marketing slogan in 2023-2026: 99% of products claiming it bolt a `chat.completions` endpoint onto an existing product. Ocarina proposes, on the contrary, a **software infrastructure designed so an AI can contribute like a senior developer**. [`ocarina-with-ai-example`](https://github.com/mojo-molotov/ocarina-with-ai-example) is the proof by example.

## 1. What AI is today

| Layer                                   | Example                                        | Appearance date                                |
| --------------------------------------- | ---------------------------------------------- | ---------------------------------------------- |
| **Statistical learning**                | Regression, k-means, decision trees            | 1960s-1990s                                    |
| **Deep learning**                       | CNN (vision), RNN/LSTM (text)                  | 2012 (AlexNet&nbsp;—&nbsp;mainstream adoption) |
| **Transformer-based foundation models** | GPT, Claude, Gemini, Llama                     | 2017 (paper), 2018 (BERT), 2022 (ChatGPT)      |
| **Agentic workflows**                   | AutoGPT, LangChain, Claude Code, Cursor agents | 2023+                                          |

> _Note: CNNs were invented by Yann LeCun as early as 1989 (MNIST). AlexNet (Krizhevsky, Sutskever, Hinton, Toronto, 2012) was the industrial breakthrough. LeCun, Hinton, and Bengio share the 2018 Turing Award for their foundational contributions to deep learning._

When Ocarina's Holy Book talks about "_AI_", it talks about **layers 3 and 4**: pre-trained transformer-based LLMs, and the agentic loops that invoke them.

### _Attention is All You Need_

| Field        | Value                                                                     |
| ------------ | ------------------------------------------------------------------------- |
| Paper        | **"_Attention Is All You Need_"**                                         |
| Authors      | Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin     |
| Org          | **Google Brain, Google Research, University of Toronto**                  |
| Date         | **June 2017** (arXiv), presented at **NeurIPS December 2017**             |
| Contribution | **Transformer** architecture: self-attention instead of recurrence (LSTM) |

The _Transformer_ architecture lets you _parallelize_ training on GPU. What took weeks in LSTM does hours. Training scales to Internet-size. GPT-1 (2018) → GPT-2 (2019) → GPT-3 (2020, 175B params) → GPT-4 (2023) → Claude 3 (2024) → Claude 4 (2025).

### Actors

| Org                                                   | Models                     | Posture                                                               |
| ----------------------------------------------------- | -------------------------- | --------------------------------------------------------------------- |
| **OpenAI** (Sam Altman, San Francisco)                | GPT-4o, o1, GPT-5, GPT-5.5 | _Closed weights_, subscription                                        |
| **Anthropic** (Dario & Daniela Amodei, San Francisco) | Claude 3, 3.5, 4           | _Closed weights_, focus on safety and _alignment_ (Constitutional AI) |
| **Google DeepMind**                                   | Gemini 1.5, 2.0, 2.5       | _Closed weights_, Google integration                                  |
| **Meta AI**                                           | Llama 2, 3, 4              | _Open weights_ (almost open source)                                   |
| **xAI** (Musk)                                        | Grok 1, 2, 3               | Partial _open weights_                                                |
| **Mistral AI** (Paris)                                | Mistral, Mixtral           | _Open weights_, European                                              |

## 2. Operational capabilities of a 2025-2026 LLM

To understand how Ocarina uses them, you need to **list honestly** what a modern LLM can and cannot do.

### What an LLM does well

| Capability                                       | Level |
| ------------------------------------------------ | ----- |
| Reformulation, translation                       | ★★★★★ |
| _Local_ code generation (one file, one function) | ★★★★★ |
| Understanding docs that fit in context           | ★★★★★ |
| Detecting patterns in code                       | ★★★★  |
| Generating tests _from_ documented code          | ★★★★  |
| Mechanical refactor (rename, extract)            | ★★★★  |
| Following a convention if explicitly documented  | ★★★★  |
| Applying a fixed grammar (bounded, typed DSL)    | ★★★★★ |

### What an LLM does poorly, and how Ocarina responds

| Limit                                         | Consequence                                                         | Ocarina response                                                                |
| --------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Hallucinations**                            | Invents nonexistent functions / classes                             | _Mypy strict_                                                                   |
| **Long-context degradation**                  | Loses precision on the middle of a long file (_lost in the middle_) | Short modules, split _SKILL.md_ files                                           |
| **No runtime feedback without tooling**       | If nothing tells it that it crashed, the LLM continues              | Ocarina _probes_ (see [`15-typing-ai-rl-probes.md`](15-typing-ai-rl-probes.md)) |
| **Prefers popular patterns**                  | Drifts toward pytest, async/await, mock                             | Explicit documentation of Ocarina's _refusals_                                  |
| **Doesn't fill in a poorly specified domain** | Unsatisfying with ill-defined technologies                          | Well defined, algebraic conventions, ISTQB-first                                |
| **No memory between sessions**                | Loses project conventions                                           | `CLAUDE.md`, _skills_                                                           |
| **No intuition about invariants**             | Generates code that passes tests but doesn't respect the spirit     | Structural _ROP_ that enforces the grammar                                      |

## 3. What "_AI-first_" means operationally

| Level                                 | Characteristics                                              | Example                                         |
| ------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------- |
| **0&nbsp;—&nbsp;Slogan**              | "_Powered by AI_" without a real surface                     | Majority of 2024 SaaS                           |
| **1&nbsp;—&nbsp;External chatbot**    | OpenAI endpoint in a UI wrapper                              | Majority of _AI-enhanced_                       |
| **2&nbsp;—&nbsp;RAG over the docs**   | Retrieves passages, glues them into the response             | Algolia DocSearch + OpenAI plugin, Mintlify     |
| **3&nbsp;—&nbsp;Native AI interface** | The product is _designed_ for an agent to act on it          | **MCP servers, llms.txt, AI SDK, Cursor rules** |
| **4&nbsp;—&nbsp;Co-design**           | The product creates deliverables _co-written_ by an AI agent | **Ocarina + `ocarina-with-ai-example`**         |

Ocarina is one of very few projects to reach **level 4** publicly and with auditable evidence.

## 4. AI-first artifacts in Ocarina

### `llms.txt`, `llms-full.txt`

De-facto standard proposed by [`llmstxt.org`](https://llmstxt.org) (Jeremy Howard, fast.ai), 2024.

- `llms.txt`: a short Markdown index, designed for an agent to find _what to read_.
- `llms-full.txt`: the _full concatenated doc_, designed for a single prompt that ingests everything.

Ocarina exposes both. See [`09-holy-book/06-public-resources.md`](../09-holy-book/06-public-resources.md)

### `CLAUDE.md` / `CLAUDE.slim.md`

**Anthropic** convention: `CLAUDE.md` at the project root, automatically read by Claude Code (and compatibles):

- Project identity, philosophy.
- Conventions to follow.
- Main commands.
- Known gotchas.

Ocarina maintains:

- Long `CLAUDE.md` (large context) for deep _onboarding_.
- Short `CLAUDE.slim.md` (token thrift) for routine interactions.

### Skills (`SKILL.md`)

40+ skills exposed by the Holy Book. One skill = one `SKILL.md` file:

- YAML metadata (`name`, `description`).
- Step-by-step procedure.
- Invocation conditions ("_when the user asks for X, do Y_").

Lets Claude Code, Cursor, etc. **plug in**. See [`09-holy-book/03-skills/`](../09-holy-book/03-skills/)

### `ocarina-with-ai-example`

A full e2e project, written to test a real app (CURA), **co-written by Claude**. The repo's `CLAUDE.md` documents the _hard-won rules_ learned during co-writing.

This suite is a **proof by example** that Ocarina's _AI-first_ approach isn't an invention: it has been tested against a SUT in documented collaboration with an LLM. See [`08-ai-example/`](../08-ai-example/)

## 5. "_AI-marketing_" vs "_AI-for-real_"

| Criterion                  | AI-marketing                      | AI-for-real (Ocarina)                                |
| -------------------------- | --------------------------------- | ---------------------------------------------------- |
| Documented AI surface      | "_Powered by GPT-4_"              | `llms.txt`, `llms-full.txt`, `CLAUDE.md`, 40+ skills |
| Proof of AI use            | None or wobbly                    | `ocarina-with-ai-example`                            |
| Doc format                 | PDF / SaaS dashboard only         | Raw Markdown                                         |
| Agent compatibility        | Nonexistent                       | Built for Claude Code, Cursor, Continue, Cline       |
| Grammar convention         | Ad-hoc                            | Strict ROP + ISTQB, static typing                    |
| LLM context management     | Neglected (huge monolithic files) | Modularized to the end                               |
| Reaction to hallucinations | None                              | Well-defined technology, type errors, max strictness |
| Reproducibility            | Non-deterministic by construction | _Probes_ + caching                                   |

## 6. Why this preparation _gives Ocarina an edge for the next 5 years_

1. The barrier to entry of e2e testing will **collapse** because an LLM can write most of the _boilerplate_.
2. **Only** LLM-compatible frameworks will stay relevant; the others will become _legacy_.
3. LLM compatibility depends on **three things**:
   - A **small** well-defined DSL (fits in context).
   - A **formal grammar** (mypy / ROP / ISTQB).
   - **Structured documentation** (Markdown + skills).
4. Ocarina ticks every box.
5. Pytest, Cypress, Playwright, Robot Framework don't. Their surface is too large (hundreds of plugins), their grammar too fuzzy (async, fixtures), their documentation too fragmented (SaaS sites, videos, scattered plugins).

Ocarina bets that **AI will devour** large-surface frameworks, exactly as Tugan Bara was ejected by AI in copywriting (see [`10-infopreneurs-tugan-bara-ai.md`](10-infopreneurs-tugan-bara-ai.md)).

## 7. How AI _actually_ works on Ocarina

```
1. Claude reads /CLAUDE.md (project conventions).
2. Claude reads /docs/what-is-it.md (philosophy).
3. Claude reads /SKILL_<feature>.md (matching skill).
4. Claude reads /tests/scenarios/<family>/*.py (sample).
5. Claude writes a new `.py` file.
6. Mypy strict runs automatically.
7. If mypy fails → Claude reads the diagnostic, fixes, reruns.
8. If mypy passes → Claude runs the test against the SUT.
9. If the test fails → Claude reads the output, adjusts probes, re-reads.
10. If the test passes → Claude commits, pushes, opens a PR.
```

Steps 2, 3, 4, 6, 9 are **constrained by Ocarina's infrastructure**. Without `CLAUDE.md`, step 1 is random. Without mypy strict, step 6 doesn't exist. Without `transient_errors`, `match_page`, and `watcher`s, step 9 produces _flaky tests_.

That's what makes Ocarina **designed for AI**, not _bolted to AI_.

## 8. Related reading

- [`13-lambda-calculus-rop-origins.md`](13-lambda-calculus-rop-origins.md)&nbsp;—&nbsp;Ocarina's DSL's theoretical base, which makes it _LLM-compatible_.
- [`15-typing-ai-rl-probes.md`](15-typing-ai-rl-probes.md)&nbsp;—&nbsp;why typing + RL + probes are the triad that makes AI productive.
- [`../08-ai-example/`](../08-ai-example/)&nbsp;—&nbsp;the proof by example: the AI suite.
- [`../09-holy-book/03-skills/`](../09-holy-book/03-skills/)&nbsp;—&nbsp;the exposed skills.
