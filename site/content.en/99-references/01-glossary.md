---
title: "99.01 — Glossary"
description: "Terminology used in the Ocarina ecosystem. Original sources in parentheses."
weight: 1
date: 2026-05-20
series: ["references"]
series_order: 1
tags: ["references"]
---

# 99.01&nbsp;—&nbsp;Glossary

> Terminology used in the Ocarina ecosystem. Original sources in parentheses.

## Railway Oriented Programming (ROP)

| Term                                                                              | Definition                                                                                                                                                |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ROP** (Wlaschin, F#)                                                            | Functional pattern: success and failure are two parallel _rails_; a failure switches the computation to the failure rail, where it stays (short-circuit). |
| **`Result[T]`**                                                                   | Discriminated union `Ok[T] \| Fail`. Error carried as **value**, not raised exception.                                                                    |
| **`Ok[T]`**                                                                       | Success wrapper, `value: T`.                                                                                                                              |
| **`Fail`**                                                                        | Failure wrapper, `error: Exception`.                                                                                                                      |
| **`is_ok`, `is_fail`**                                                            | `TypeGuard`s that narrow a `Result[T]` to `Ok[T]` or `Fail`.                                                                                              |
| **`Action[T]`**                                                                   | `Thunk[Result[T]]`&nbsp;—&nbsp;argumentless function returning a `Result[T]`.                                                                             |
| **`ActionStart[T]`**                                                              | Initial state of the ROP action builder. Expects `.failure(...)`.                                                                                         |
| **`ActionFailure[T]`**                                                            | After `.failure(...)`. Expects `.success(...)`.                                                                                                           |
| **`ActionSuccess[T]`**                                                            | After `.success(...)`. Expects `.execute()`.                                                                                                              |
| **`ActionChain[T]`**                                                              | After `.execute()`. Carries `has_failed: bool` and `result: Result[T]`. Allows `.then(...)`.                                                              |
| **`NeutralActionStart[T]`, `NeutralActionFailure[T]`, `NeutralActionSuccess[T]`** | _Inert_ states of the failure rail. Stub by no longer doing anything.                                                                                     |
| **`ChainRunner[T]`**                                                              | Lazy encapsulation of an `ActionChain`. Executed by `.run()`.                                                                                             |
| **`drive_page`**                                                                  | Opinionated semantic alias for `chain_actions`. "_Take control of a page_".                                                                               |
| **`match_page` / `when`**                                                         | Conditional branching. First-match wins.                                                                                                                  |
| **`create_act`**                                                                  | Low-level primitive to create `act` (_test step_). Wrapped by the user project.                                                                           |
| **`act`** (project-side)                                                          | User wrapper for `create_act` with a project-specific `on_failure` hook. Represents a _test step_.                                                        |

## ISTQB / test-professional vocabulary

| Term                 | Definition                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------- |
| **ISTQB**            | International Software Testing Qualifications Board. Professional body of software testing. |
| **Test cycle**       | Top level. A complete execution.                                                            |
| **Test campaign**    | Level under the cycle. Not directly defined in ISTQB but recognized in tester vocabulary.   |
| **Test suite**       | Level under the campaign. A collection of _executable_ tests.                               |
| **Test case**        | A test case. Atomic unit.                                                                   |
| **Test step**        | A test step. Atomic action inside a test case.                                              |
| **Smoke test**       | Minimal check proving the system is _running_. If failure, the rest is useless.             |
| **Setup / Teardown** | Pre/post-condition of a test.                                                               |

## Ocarina (orchestration)

| Term                                      | Definition                                                                                                       |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **`Test[Driver]`**                        | ISTQB test. Metadata + scenario factory + fragments + skip.                                                      |
| **`TestSuite[Driver]`**                   | ISTQB suite. Parallelization (_thread pool_), saturation, ID filtering, retries.                                 |
| **`TestCampaign[Driver]`**                | Campaign. Sequence of suites with shared workers config.                                                         |
| **`TestCycle[Driver]`**                   | ISTQB cycle. Smoke (with `fail-fast` vs `wait-for-all` modes) + main.                                            |
| **`TestExecutor[Driver]`**                | Executes a single attempt of a test. Stateless.                                                                  |
| **`TestFlow[Driver]`**                    | Replay loop (1 + max_retries) with linear backoff.                                                               |
| **`TestRunner[Driver]`**                  | Output of `Test.spawn(driver, logger)`. Aggregator of chain_runners + setup + teardown + watchers.               |
| **`Scenario[Driver]`** (frozen dataclass) | Encapsulates `test_chain`, `setup`, `teardown`, `watchers`.                                                      |
| **`TestChain`**                           | `Sequence[ChainRunner[Any]]`. The sequence to execute to apply the test.                                         |
| **`Watcher[Driver]`**                     | _Daemon thread_ observing something extra on a test. Periodic callback.                                          |
| **`Saturation`**                          | Random test-cloning mechanism to reach `max_workers`. Copies named `[COPY N] <name>` (or `[+N]` per convention). |
| **`Transient errors`**                    | Tuple of exceptions triggering a replay.                                                                         |
| **`max_retries_per_test`**                | Number of replays. Default, 8 ("_9 lives like a cat_ 🐱").                                                       |
| **`autoscreen_on_fail`**                  | Automatic screenshot on failing test step.                                                                       |

## Ocarina (invariants DSL)

| Term                                     | Definition                                                                                       |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **`validate(value, name="...")`**        | Entry point of the invariants DSL.                                                               |
| **`ValidationStartBlock[T]`**            | Initial state. Expects `.assert_that(...)`.                                                      |
| **`ValidationAssertBlock[T]`**           | After `.assert_that(...)`. Accepts `.assert_that`, `.otherwise`, `.then`, `.execute`.            |
| **`.assert_that(predicate)`**            | Adds a logical AND.                                                                              |
| **`.otherwise(predicate)`**              | Adds a logical OR. Combined via `_any_of`.                                                       |
| **`.then(new_value)`**                   | Switches the current value in the chain. Keeps accumulated errors.                               |
| **`.execute()`**                         | Executes the chain, returns a `_ValidationResult` (inert until `.raise_if_invalid()` is called). |
| **`chain_validations(*)`**               | Merge several `ValidationAssertBlock`s into one.                                                 |
| **`InvariantViolationError`**            | Exception raised by predicates.                                                                  |
| **`AggregateInvariantViolationError`**   | Aggregation of multiple `InvariantViolationError`s. Raised by `.raise_if_invalid()`.             |
| **`DuplicatesError`**                    | `InvariantViolationError` subclass raised by `has_unique_elements`.                              |
| **`BusinessInvariantValidator.create`**  | Factory for business invariants.                                                                 |
| **`FrameworkInvariantValidator.create`** | Factory for framework invariants.                                                                |

## Ocarina (infra + ports)

| Term                                                                    | Definition                                                                                                                                                                |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`POMBase`**                                                           | Framework-agnostic ABC. Methods `verify` + `get_current_title`.                                                                                                           |
| **`SeleniumTitleMixin`**                                                | Selenium-specific mixin. Implements `get_current_title` and types `_driver: WebDriver`.                                                                                   |
| **`WebDriversPool[Driver]`**                                            | Thread-safe drivers pool. Semaphore + Queue (_THE QUEUE damn it!_) + warmup with watchdog.                                                                                |
| **`WarmupTimeoutError`**                                                | Raised by `pool.warmup()` when it stalls.                                                                                                                                 |
| **`DriverBuilder[Driver]`**                                             | Builder that manages the profile tmp dir and produces `(driver, dispose)`.                                                                                                |
| **`BuiltWebDriver[Driver]`**                                            | `tuple[Driver, Effect]`&nbsp;—&nbsp;driver + dispose.                                                                                                                     |
| **`Screenshotter[TDriver]`**                                            | Thread-safe screenshot utility. Burst mode, healthcheck.                                                                                                                  |
| **`ScreenshotterConfig[TDriver]`**                                      | Config (frozen dataclass): output_dir, file_ext, health_check, save_full_page, etc.                                                                                       |
| **`ActCounter`**                                                        | Interface. Counts `act`s called per attempt.                                                                                                                              |
| **`ThreadsBasedActCounter`**                                            | Thread-local implementation of `ActCounter`.                                                                                                                              |
| **`ILogger`**                                                           | Logging port (ABC). Methods: `debug`, `info`, `warning`, `error`, `critical`, `success`, `test_name`, `exception`, `raw`, `set_prefix`, `set_domain_taxonomy`, `cleanup`. |
| **`ITakeScreenshot[Driver]`**                                           | Protocol `(driver, logger, category) -> None`.                                                                                                                            |
| **`PrintLogger` / `FileLogger` / `PrintAndFileLogger` / `MutedLogger`** | 4 canonical implementations of `ILogger`.                                                                                                                                 |
| **`driver_healthcheck(driver)`**                                        | Pings `driver.title`; raises `DriverDiedError` if THE DRIVER IS DEAD.                                                                                                     |
| **`DriverDiedError`**                                                   | Exception raised by `driver_healthcheck`.                                                                                                                                 |
| **`PageVerificationError`**                                             | Exception raised by `POM.verify` when the page isn't the right one.                                                                                                       |
| **`NoMatchingBranchError`**                                             | Exception raised by `match_page` when no `when` matches.                                                                                                                  |

## Ocarina (opinionated)

| Term                                                | Definition                                                                          |
| --------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **`CliBuilder`**                                    | Declarative builder over argparse. Error aggregation.                               |
| **`CliArg`**                                        | Declaration of a CLI argument.                                                      |
| **`CliStore[TKeys]`**                               | Write-once store for parsed CLI values. `TKeys: Literal[...]` for autocomplete.     |
| **`_CliField[T]`**                                  | Write-once field with validator.                                                    |
| **`phantom_validate`**                              | No-op validator for fields that don't need extra validation.                        |
| **`CliStoreSingleton`**                             | Singleton around `CliStore`.                                                        |
| **`create_selenium_auto_cli_store()`**              | Factory that dispatches by OS.                                                      |
| **`bootstrap(test_cycle, run_plugins, post_exec)`** | Canonical entry point.                                                              |
| **`run_plugins(*plugins, exceptions_logger)`**      | Runs plugins in parallel if N>1.                                                    |
| **`pretty_print_results`**                          | Plugin that prints results to the terminal (ANSI).                                  |
| **`generate_docx_proof`**                           | Plugin to create DOCX test proofs.                                                  |
| **`generate_json_results`**                         | Plugin that transcribes the same results as `pretty_print_results`, in JSON format. |
| **`timing`**                                        | Context manager that measures duration.                                             |

## Functional programming

| Term                      | Definition                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------------- |
| **`Effect`**              | `Callable[[], None]`&nbsp;—&nbsp;argumentless, returnless function, deferred.                   |
| **`Thunk[T]`**            | `Callable[[], T]`&nbsp;—&nbsp;argumentless function, deferred.                                  |
| **`Closure`**             | Function capturing an environment.                                                              |
| **`Fold` / `reduce`**     | Reduction of a sequence to a single value (_catamorphism_).                                     |
| **`TypeGuard`**           | PEP 647&nbsp;—&nbsp;annotation that _narrows_ a type on the type-checker side.                  |
| **`Discriminated union`** | Union of disjoint types, discriminated by a test (typically `isinstance`).                      |
| **`Sealed union`**        | Discriminated union whose variants are all `@final`.                                            |
| **`@final`**              | PEP 591&nbsp;—&nbsp;declares that a class can't be subclassed (no infinite covariance).         |
| **`Self`**                | PEP 673&nbsp;—&nbsp;return type that refers to the instantiated class (not the declared class). |
| **`Protocol`**            | PEP 544&nbsp;—&nbsp;structural type; any object with the right shape is usable.                 |
| **`PEP 695`**             | Generics syntax `class Foo[T]:` (Python 3.12+).                                                 |

## Author vocabulary

| Term                                                       | Meaning                                                                                                                                                                                                                                                                           |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Slipologue**                                             | Neologism. The one pretending "_to know everything_" without practice. Pollutes technical discussions with _mental models_. A pain in the ass using ChatGPT or Wikipedia to always have an answer for everything, pretending to speak about a subject he masters when he doesn't. |
| **Vues de l'esprit** (mental models)                       | Imaginary concept; inapplicable theoretical vision.                                                                                                                                                                                                                               |
| **White box**                                              | Auditable, readable code, no hidden logic. Opposite of _black box_.                                                                                                                                                                                                               |
| **Raw data**                                               | Source code, files, simple formats.                                                                                                                                                                                                                                               |
| **Programming astrology**                                  | Esoteric patterns without measurable benefit.                                                                                                                                                                                                                                     |
| **In the Lulzboat, salute, bitch, and show some respect.** | Quote from **YTCracker&nbsp;—&nbsp;`#antisec`** (2011), official anthem of _Operation AntiSec_. See [`../12-manifesto-deciphered/01-sourced-citations.md`](../12-manifesto-deciphered/01-sourced-citations.md)                                                                    |
| **Fucking skids, fucking normies**                         | IRC / EFnet identity marker.                                                                                                                                                                                                                                                      |

## Hacker scene (chapter 12)

| Term                                  | Definition                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AntiSec movement (1999)**           | Movement opposed to the cybersecurity industry and _full disclosure_. Refusal to publish exploits / vulnerabilities. Targets: SecurityFocus, Packet Storm, Bugtraq mailing list, etc.                                                                                                                                                  |
| **Operation AntiSec (2011)**          | Resurrection of the movement by LulzSec + Anonymous. 50 days of hacks (May-June 2011).                                                                                                                                                                                                                                                 |
| **LulzSec**                           | Hacker group active May-June 2011. Anonymous _splinter_. Manifesto "_we do it for the lulz_". Arrests in 2012.                                                                                                                                                                                                                         |
| **The Lulzboat**                      | LulzSec's identity metaphor. Pirate-ship ASCII art signing their communiqués.                                                                                                                                                                                                                                                          |
| **Sabu**                              | Hector Monsegur, LulzSec leader, turned by the FBI in June 2011.                                                                                                                                                                                                                                                                       |
| **Topiary**                           | Jake Davis, LulzSec spokesperson.                                                                                                                                                                                                                                                                                                      |
| **YTCracker**                         | Bryce Case Jr. (born 1982). _Nerdcore_ rapper, former black hat (NASA Goddard 1999), founder of _Digital Gangster_ (forum, 2005).                                                                                                                                                                                                      |
| **Nerdcore**                          | Hip-hop subgenre whose lyrics are _really_ for nerds (code, hacking, sci-fi, math). Coined by MC Frontalot (2000).                                                                                                                                                                                                                     |
| **Digital Gangster**                  | Hacker forum founded by YTCracker in 2005 (`digitalgangster.com`). 36,000 members at peak. Source of several iconic hacks (Paris Hilton, Miley Cyrus, Twitter Obama, etc.).                                                                                                                                                            |
| **NerdRap Entertainment System**      | YTCracker's founding album (2005). Beats over NES OSTs, Nerdcore lyrics.                                                                                                                                                                                                                                                               |
| **Darknet Diaries**                   | Podcast by **Jack Rhysider** on cybersecurity history. **Episode 78 (_Nerdcore_)** is dedicated to YTCracker. Transcript: <https://darknetdiaries.com/transcript/78/>                                                                                                                                                                  |
| **Zone-H**                            | Public website-deface archive (founded March 2, 2002 by Roberto Preatoni / Sys64738, based in Estonia). 2002-2015 grey-hat scoreboard.                                                                                                                                                                                                 |
| **IRC**                               | _Internet Relay Chat_ (1988). Multi-user text-chat client/server protocol. Central social medium for hackers 1993-2012.                                                                                                                                                                                                                |
| **EFnet**                             | _Eris-Free Network_. Historical IRC network (1990). Center of the _warez_, _0day_, _phreakers_ scene 1996-2008.                                                                                                                                                                                                                        |
| **Channel** (`#name`)                 | IRC room.                                                                                                                                                                                                                                                                                                                              |
| **`skid` / _script kiddie_**          | Hacker running scripts they don't understand. Insult.                                                                                                                                                                                                                                                                                  |
| **`normie`**                          | Average user, uninitiated. Insult.                                                                                                                                                                                                                                                                                                     |
| **`lamer`**                           | BBS-era variant of _skid_.                                                                                                                                                                                                                                                                                                             |
| **`gr33tz`**                          | _Greetings_, crew list, at the bottom of a deface.                                                                                                                                                                                                                                                                                     |
| **`zine`**                            | _E-zine_, underground magazine, often ASCII.                                                                                                                                                                                                                                                                                           |
| **VX Underground (VXUG)**             | Public malware-samples repository (founded ~2019 by smelly_vx). Original sysadmin: **Yung Innanet / kayos**.                                                                                                                                                                                                                           |
| **Yung Innanet / kayos**              | Original sysadmin of VX Underground and musician. Passed October 18, 2025. The Holy Book **directly** quotes lyrics from his track **`true colors`** ([SoundCloud](https://soundcloud.com/queed-inc/true-colors)), signed "_(btw: RIP, DG descendant…)_".                                                                              |
| **YogyaCarderLink (YCL)**             | Indonesian hacker collective (Yogyakarta), early 2000s. Two recurring mantras on their defaces: "_We Can Do All What You Can't Do._" and **`Don't fuck with us.`**                                                                                                                                                                     |
| **Honker (红客)**                     | Chinese _red hacker_. Patriotic, ideologically driven hacker. Appeared after the 1998 Indonesia riots.                                                                                                                                                                                                                                 |
| **Villains but not Monsters**         | Moral distinction at the heart of the hacker scene: a _Villain_ confronts power, a _Monster_ persecutes the weak. Real enthusiasts hate _monsters_ (often former bullied who reproduce the harm they suffered).                                                                                                                        |
| **DEF CON**                           | Annual hacker conference, now in Las Vegas (formerly at the _Caesars Forum_).                                                                                                                                                                                                                                                          |
| **BOFH (Bastard Operator From Hell)** | Fiction series by **Simon Travaglia** (New Zealand), published on Usenet in the '90s then on _The Register_. Archetype of the user-despising sysadmin. Source of the vocabulary _PEBKAC_, _RTFM_, _ID-10-T error_.                                                                                                                     |
| **Usenet**                            | Distributed _newsgroups_ system. Founding medium of hacker culture.                                                                                                                                                                                                                                                                    |
| **Shodan**                            | Search engine for internet-connected _devices_ (IP cameras, ICS, IoT, open servers). Founded by **John Matherly**. [`shodan.io`](https://shodan.io)                                                                                                                                                                                    |
| **ViolVocal**                         | French-speaking community (mid-2000s) of organized _prank callers_ / phone harassers on forum + Mumble/TeamSpeak server. SIP spoofing, public call _streams_, doxing, impersonating police officers to consult restricted databases without authorization, etc. Shut down after prosecutions. Francophone case of underground cruelty. |
| **4chan / /b/**                       | Imageboard founded by moot (Christopher Poole) in 2003. /b/ = no-rules, no-archive, totally anonymous board. Matrix of Anonymous (2006-2008) and modern meme culture. Community regularly orchestrating harassment, having notably degraded Terry A. Davis's health.                                                                   |
| **Anonymous**                         | Collective entity emerged from 4chan /b/ around 2006-2008. Op Chanology (Scientology 2008), Op Tunisia (2011), Op Sony (2011). IRC coordination.                                                                                                                                                                                       |
| **Doxing**                            | Publication of a target's personal info with intent to harm.                                                                                                                                                                                                                                                                           |
| **Swatting**                          | False emergency call (often SIP-spoofed) declaring a serious crime at the victim's address, triggering SWAT deployment. Fatal cases documented.                                                                                                                                                                                        |
| **OSINT**                             | _Open Source Intelligence_. Information gathering from public sources.                                                                                                                                                                                                                                                                 |
| **OPSEC**                             | _Operations Security_. Rigorous maintenance of operational anonymity over time.                                                                                                                                                                                                                                                        |
| **Honeypot**                          | Fake server / fake account / fake leak baiting attackers to detect them. Scene defensive tool.                                                                                                                                                                                                                                         |
| **Snitch / Fed**                      | Informant / undercover federal agent. Top-priority detection in any _underground_ community.                                                                                                                                                                                                                                           |
| **Prompt injection**                  | Insertion of malicious content into an LLM's context to hijack its behavior. OWASP LLM01:2025. First in the LLM Top 10.                                                                                                                                                                                                                |
| **MCP (Model Context Protocol)**      | Anthropic standard protocol (2024) to expose _tools_ and _resources_ to an LLM. Each third-party MCP server adds an attack surface.                                                                                                                                                                                                    |
| **Hard-won rules**                    | Internal project conventions documented in `CLAUDE.md` after costly lessons. Prevents LLMs from repeating errors already encountered.                                                                                                                                                                                                  |

## Ocarina ideology

| Term                              | Definition                                                                                                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Villain (hacker sense)**        | Reclaimed identity of the sovereign hacker acting outside institutions, opposed to conventions and _corporate branding_. The Villain confronts power but respects the weakest. |
| **Monster (hacker sense)**        | One who technically exploits their skill to persecute vulnerable people (harasser, doxxer, etc.). Structural _enemy_ of the real hacker scene.                                 |
| **Tooling culture**               | Conviction that well-written technical tools (Nmap, Wireshark, Metasploit, Burp, sqlmap, et al.) made by small teams are worth a thousand marketing presentations.             |
| **Tribal loyalty (hacker scene)** | Absolute intra-community loyalty + extreme external suspicion. Long admission tests, _vouching_ by established members, brutal excommunication on betrayal.                    |
| **Eyes everywhere**               | Operational hyper-vigilance learned in the _underground_ context (IRC admin legally responsible for their channels' actions).                                                  |

## Industry / counter-models

| Term                               | Definition                                                                                                                                                                                           |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Infopreneur**                    | Entrepreneur whose product is sold information: courses, e-books, masterminds. American model (Dan Kennedy, Russell Brunson), imported into France via Tugan Bara.                                   |
| **Copywriting**                    | Art of writing persuasive _sales texts_. Core trade of infopreneurs. Largely automatable by AI since 2023.                                                                                           |
| **Funnel**                         | _Sales funnel_: free content → front-end product (€97) → flagship product (€997-4997) → premium coaching.                                                                                            |
| **Marketing Underground**          | Tugan Bara's flagship program (2018-2023). Owned "_bad guy_" posture.                                                                                                                                |
| **Tugan Bara / Arnaud Labossière** | French archetype of the 2018-2024 infopreneur model. HEC dropout. Sold Tugan.ai in 2024. Ultimately the only infopreneur who really explained the profession to a whole francophone-scene community. |
| **MRR**                            | _Monthly Recurring Revenue_. Monthly amount billed to subscription customers. Central SaaS indicator.                                                                                                |
| **ARR**                            | _Annual Recurring Revenue_. Annual amount earned from SaaS sales.                                                                                                                                    |

## AI, ML, RL

| Term                            | Definition                                                                                                                               |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **LLM**                         | _Large Language Model_. Transformer model pre-trained on a large corpus. Claude, GPT, Gemini, Llama, Mistral.                            |
| **Transformer**                 | Architecture introduced by _Attention Is All You Need_.                                                                                  |
| **Foundation model**            | Pre-trained model reused for multiple tasks via _fine-tuning_ or _prompting_.                                                            |
| **RL (Reinforcement Learning)** | Learning by interaction with an environment, guided by a _reward signal_. Sutton & Barto 1998.                                           |
| **Constitutional AI (CAI)**     | Anthropic alignment method (Bai et al., 2022). The model critiques and revises its own responses according to a written _constitution_.  |
| **Probe**                       | Empirical learning primitive for AI.                                                                                                     |
| **llms.txt, llms-full.txt**     | Jeremy Howard standard (fast.ai), 2024. Short Markdown index (`llms.txt`) + concatenated full doc (`llms-full.txt`) for agent ingestion. |
| **SKILL.md**                    | Lets an AI agent plug into a project skill.                                                                                              |
| **CLAUDE.md**                   | Provides Claude Code with a set of rules.                                                                                                |
