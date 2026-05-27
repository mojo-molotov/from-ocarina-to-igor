---
title: "01.04 — Citations and claimed influences"
description: "The references cited in the Holy Book aren't neutral — they set Ocarina's theoretical frame. We cut them by axis here, then offer the overall reading."
weight: 4
date: 2026-05-20
series: ["philosophy"]
series_order: 4
tags: ["rop"]
---

# 01.04&nbsp;—&nbsp;Citations and claimed influences

> The references cited in the Holy Book aren't neutral&nbsp;—&nbsp;they set Ocarina's **theoretical frame**. We cut them by axis here, then offer the overall reading.

## Technical axis&nbsp;—&nbsp;Functional programming, types, languages

| Influence                              | Origin                                                              | Relation to Ocarina                                                                                                                                                                                                                       |
| -------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Railway Oriented Programming (ROP)** | Scott Wlaschin (F#), a well-known pattern in functional programming | The heart of the framework. `Result[T] = Ok[T] \| Fail`, _short-circuit_, fluent builder. See [`../02-ocarina/03-railway/`](../02-ocarina/03-railway/README.md).                                                                          |
| **λ-calculus (1930)**                  | Alonzo Church                                                       | Cited as the invention that makes possible the “clean formalization” Ocarina pursues: “_What has been on our minds since the 1930s, **since the invention of λ-calculus**, is finally scalable to the degree we always wanted it to be._” |
| **McCulloch & Pitts (1943)**           | First formalization of the artificial neuron                        | Cited as a reminder that the _real_ progress in AI is old and continuous, against the recent hype.                                                                                                                                        |
| **Python type system (PEP 695)**       | PEP 695 (Python 3.12+)                                              | Prerequisite for the generic parametric typing that structures Ocarina (`TestSuite[Driver]`, `Result[T]`, etc.). See [`../03-functional/06-pep-695-generics.md`](../03-functional/06-pep-695-generics.md).                                |

## Cultural axis&nbsp;—&nbsp;Anti-narcissism, simplicity, KISS done right

| Influence                                                     | Citation                                                                                                                                          | Why                                                                                                                                                                                |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Terry Davis** (“the smartest programmer that's ever lived”) | _“An idiot admires complexity, a genius admires simplicity, a physicist tries to make it simple…”_                                                | Anti–ostentatious complexity argument; cornerstone of the “First feedbacks” chapter.                                                                                               |
| **Lao-Tzu**                                                   | _“To attain knowledge, add things every day. To attain wisdom, remove things every day.”_                                                         | A subtractive method: what remains after elimination.                                                                                                                              |
| **Antoine de Saint-Exupéry**                                  | _“Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.”_                                   | Western restatement of the previous one. Closes the “First scenarios” chapter.                                                                                                     |
| **Alan Watts**                                                | _“Muddy water is best cleared by leaving it alone.”_                                                                                              | Cited at the end of the “First jutsus” chapter: legitimizes a design that _refuses_ certain features (reactivity, async). Legitimizes stepping out of the “geek tricks” ecosystem. |
| **Rainer Maria Rilke**                                        | _“Live the questions now. Perhaps then, someday far in the future, you will gradually, without even noticing it, live your way into the answer.”_ | Closes the “First steps” chapter. Stance toward practice: mastery comes from use.                                                                                                  |
| **Marcel Proust**                                             | _“For the writer as well as for the painter, style is not a question of technique, but of vision.”_                                               | Closes the “Extensibility” chapter. Justifies the refusal to impose a DSL: vision (POMs + actions) trumps technique (a format).                                                    |

## Political axis&nbsp;—&nbsp;Code, sovereignty, anti–startup nation

| Influence                                                       | Origin                                                                   | Relation to Ocarina                                                                                                                                                                                                                           |
| --------------------------------------------------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **_Code is Law_**                                               | Lawrence Lessig (1999), reclaimed by Ethereum (2015) as a positive ideal | Cited as the stance against “democratic governance of code”. The project claims it: “_Once again, with AI, that sorely missing digital body, let us scream it, as loud as we screamed_ **‘HACK THE PLANET’** _back in '99:_ **CODE IS LAW.**” |
| **DHH&nbsp;—&nbsp;_I won't let you pay me for my open source_** | David Heinemeier Hansson, personal blog                                  | Cited to legitimize refusing unaligned contributions (“_Fuck You_” references DHH's famous slide).                                                                                                                                            |
| **Paul Graham&nbsp;—&nbsp;_Haters_**                            | PG essay (`paulgraham.com/fh.html`)                                      | Grounds the decision to “never waste time arguing when it isn't worth it”.                                                                                                                                                                    |
| **Yegor Bugayenko&nbsp;—&nbsp;_Prompt_**                        | The quote “_Retry flaky blocks._”                                        | Grounds the `transient_errors` + linear retry policy (`TestFlow`). Read also: _Angry Tests_.                                                                                                                                                  |
| **The DAO hack (2016)**                                         | Hack of The DAO on Ethereum                                              | Cited to point out that it was _bugs_ (“damned bugs, because of damned devs”) that set _Code is Law_ back, hence the importance of typing and rigor.                                                                                          |
| **Lee Robinson (ex-Vercel)**                                    | December 2025: Cursor replacing Sanity with Markdown files + AI          | Backs the “return to raw data”.                                                                                                                                                                                                               |
| **Cluely (Roy Lee)**                                            | Cited as an illustration of entrepreneurial bullshit to avoid            | Explicit contrast with the Ocarina philosophy.                                                                                                                                                                                                |

## Identity / underground axis

| Influence                                                                          | Origin                                                                  |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **LulzSec**&nbsp;—&nbsp;_“In the Lulzboat, salute, bitch, and show some respect.”_ | AntiSec (YTCracker, 2011)                                               |
| **_“We Can Do All What You Can't Do”_**                                            | YogyaCarderLink                                                         |
| **YTCracker&nbsp;—&nbsp;_Robots Will Definitely Take Your Job_**                   | SoundCloud link, background music of the “First feedbacks” chapter      |
| **_“HACK THE PLANET”_ (1999)**                                                     | Emblematic slogan of the 1990s hacker scene + AntiSec (YTCracker, 2011) |
| **Zone-H**                                                                         | Historic web defacement archive                                         |
| **r/unixporn**, **r/AntiTaff**                                                     | Subreddits                                                              |

## AI / modern tooling axis

| Influence                        | Origin                                                          | Relation to Ocarina                                                                                                   |
| -------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Claude Code**                  | Anthropic                                                       | Reference tooling for the AI project (`ocarina-with-ai-example`). Cited several times as the “bridge” replacing DSLs. |
| **IntelliCode (2018)**           | Microsoft                                                       | Cited as a temporal landmark (“we had already tasted it, well before IntelliCode”).                                   |
| **R., the silo's mad scientist** | Personal anecdote (a 2013 colleague, a private Emacs AI plugin) | Reminder that generative AI (“15,000 lines to delete to avoid writing 1,000”) existed before the public hype.         |
| **Prisma, Vercel, Cursor**       | SaaS ecosystem                                                  | Cited as practical cases of an AI-assisted _return to raw data_.                                                      |

## Overall coherence

All these influences converge on **three axes**:

1. **Typed raw data** as primary material (λ-calculus → ROP → typed Python → AI).
2. **Sophistication that lands at simplicity** as quality metric.
3. **Sovereignty** as political stance.

ROP is the technical embodiment. Turn the _failure flow_ into a **typed value** (Ok/Fail), not a side effect (a raised exception). The result is both functional _and_ accessible. The Holy Book sums it up:

> By design, Ocarina makes itself hard to misuse: the compiler has the final say.

## What these influences **didn't** bring

| Absent                                                                                                | Why                                                                                                                    |
| ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| No reference to a competing _adopted_ test framework (Cypress, Playwright, Mocha, Jest, RF, Cucumber) | All are mentioned _in contrast_, never as a source of inspiration.                                                     |
| No reference to a “Clean Code” or “SOLID” school                                                      | “_You. Don't. Even. Know. What. ‘Clean code'. Actually. IS._”                                                          |
| No reference to a DI framework (Spring, Guice, Hilt)                                                  | IoC is done via closures&nbsp;—&nbsp;see [`../03-functional/02-closures-ioc.md`](../03-functional/02-closures-ioc.md). |

Absence is also a choice.
