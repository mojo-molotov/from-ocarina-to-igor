---
title: "01.05 — The project's political stance"
description: "The five operational commitments flowing from Ocarina's philosophy: incorruptibility, an assumed direction, and their consequences for the repository."
weight: 5
date: 2026-05-20
series: ["philosophy"]
series_order: 5
tags: ["selenium"]
---

# 01.05&nbsp;—&nbsp;The project's political stance

> The Holy Book doesn't separate philosophy from the **politics of the repo** itself. Five operating commitments come out of it.

## 1. Incorruptibility

> Sharing Ocarina means **sharing a car I have maintained entirely myself, for myself, therefore with great care**. Still, it is shared as-is, and will remain so.
> It's _my_ car.
>
> **I channeled all my anger into it, to pour all my love into it.**
>
> Ocarina has a direction.
> Those who wish to take it elsewhere with their _wishful thinking_ are free to fork it and never contact me.

Practical consequences:

- **Refuses "stylish" contributions.** DHH's phrase is cited as endorsement: "_Fuck You._"
- **Owned refusal of unaligned PRs&nbsp;/&nbsp;issues.** "_No regrets in closing any useless PR or issue._"
- **Refuses "democratic governance of code."** The project is explicitly sovereign.

No contribution is excluded _a priori_. The **bar to clear** is _alignment_ with the direction.

## 2. Anti-hype

> That same December 2025, the startup whose name shall go unspoken was featured in certain media outlets as “_the AI No-Code test that humiliates Selenium and has BrowserStack shaking._” No less.

> None of this, however, will steer Ocarina away from a vision that has been taking shape for over 15 years, far from the arrogance of all these _children of the hype_.

- No "trendy" dependency without fundamental value. One runtime dependency (`python-docx`).
- The project claims its lineage from an ancient heritage (ISTQB, ROP, λ-calculus).
- The word "pamphlet" is owned: "_any truly 'cutting-edge' project, whatever it may be, starts from a **pamphlet**, is rooted in **identity**, and goes through a stage of genuine **anti-marketing**._"

## 3. Anti-slipologists

_Slipologist_ = someone who claims to "know everything" without ever practicing, and who pollutes technical discussions with _wishful thinking_.

> For too long, **software has been held hostage** by a minority, a “1%” who saw fit to turn it into a **playground for the initiated**: “geek tricks,” “ninja techniques,” “object-oriented.” **The verdict is clear: it doesn't hold up, or barely does.**

And:

> **As does AI, which is quietly rendering the “1%”'s capacity for harm obsolete.**

Practical consequences:

- No _event-driven programming_ as a new religion.
- No _declarative object-oriented_.
- No Rust “for the performance” (see [`03-kiss-and-complexity.md`](03-kiss-and-complexity.md)).

## 4. Anti No-Code, _Code is Law_

> Code is raw data. Auditable. Inspectable. **A white box.**
> Exactly what AI has known how to work with since its very beginnings.

And:

> The fact remains that code is the most sovereign asset we have, and a value proposition centered on taking it away from us makes us hold our nose.

Practical consequences:

- All Ocarina user code is Python. Auditable, copyable, runnable without any third-party platform.
- The framework is explicitly _portable_ without installation: "_In the most extreme cases: Ocarina doesn't need to be installed. Copy it, adapt it, run it._"
- No SaaS attached. No proprietary _cloud runner_.

## 5. Permanent refusal of `async`/`await`

> The only constraint: Ocarina will never support `async`/`await`.

Material justifications:

| Reason                              | Detail                                                                                                        |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Selenium is synchronous             | No native `async` API. Any `async` on top would be a sterile wrapping layer.                                  |
| `requests`, `redis` are synchronous | The targeted ecosystem (HTTP, Redis, files) runs in sync at no cost.                                          |
| Readability                         | An `async` scenario forces `await` keywords in the middle. Breaks the visual grammar "open → act → close."    |
| Concurrency covered by threads      | `ThreadPoolExecutor` + `WebDriversPool` (`Semaphore`) cover the parallelization needs. No `asyncio` required. |
| Distributed locks via Redis         | For multi-process needs, Redis coordinates (`OTP_SEND_LOCK_KEY`, etc.). Not an event loop.                    |

## 6. Secession

> Today, people launch projects the way you'd pop out to buy a pack of cigarettes. (…) They think they're smart, but: the reality is that **every VC and every LP is well aware of it,** and each plays their part in a _fool's game_.

Consequence: Ocarina ships _under Igor Casanova's author name_. No commercial entity behind it. No support promise. No public roadmap. The repo is offered "as is" in the MIT sense.

> As for me, I have nothing to lose in terms of reputation, there is no reputation to build under this name. Only a message to deliver, as it is, unfiltered.

## 7. Refusal of “tricks/hacks” (on the AI project)

`ocarina-with-ai-example`'s `CLAUDE.md` spells out the discipline:

> **No tricks or hacks.** JS-clicks to skip hit-testing, `# noqa` to silence a rule, `time.sleep` to mask a race, `driver.implicitly_wait` to patch a timing bug. If a hack is genuinely the only option, document why no clean fix exists and mark it so a reader doesn't copy the pattern.

That's the **operational discipline** of the principles above, in a real suite.

Counter-example cited:

> The JS-click-for-logout incident is the canonical anti-example: `ElementClickInterceptedException` had a clean polling fix; the JS click hid the problem.

## Summary table

| Refusal                                         | Code mechanism                                | Link                                                                                                                                                                             |
| ----------------------------------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `async`/`await`                                 | Threads + `Semaphore` + Redis                 | [`../02-ocarina/10-infra/01-drivers-pool.md`](../02-ocarina/10-infra/01-drivers-pool.md), [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md) |
| pytest plugin                                   | Integrated runner (`bootstrap`)               | [`../02-ocarina/11-opinionated/06-bootstrap-launcher.md`](../02-ocarina/11-opinionated/06-bootstrap-launcher.md)                                                                 |
| Textual DSL                                     | Embedded Python DSL                           | [`../02-ocarina/03-railway/`](../02-ocarina/03-railway/README.md)                                                                                                                |
| Reactive programming inside scenarios           | Cache + reserved keys                         | [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md)                                                                                           |
| Silent `# noqa`                                 | Always explicit and local                     | `pyproject.toml#tool.ruff`                                                                                                                                                       |
| “Stylish” contributions                         | MIT model, _take it or fork it_               | &nbsp;—&nbsp;                                                                                                                                                                    |
| JS-click to bypass hit-testing                  | Clean polling                                 | [`../08-ai-example/`](../08-ai-example/README.md)                                                                                                                                |
| `time.sleep` to mask a race condition           | Explicit polling via `WebDriverWait`          | id.                                                                                                                                                                              |
| `driver.implicitly_wait` patched outside the FW | Handled only through the CLI `--wait-timeout` | [`../02-ocarina/11-opinionated/03-selenium-cli.md`](../02-ocarina/11-opinionated/03-selenium-cli.md)                                                                             |

## Closing word

> **Ocarina is not and will never be a _pontificating_ solution.**
> Ocarina is and **WILL REMAIN a solution for solving real-world issues.**

That political stance has direct practical fallout on what's worth reading in depth: the source, not a changelog. The Holy Book, not a marketing blog post. That's the auditability promise of [`../11-independence/02-auditability.md`](../11-independence/02-auditability.md)
