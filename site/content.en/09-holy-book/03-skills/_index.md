---
title: "09.03 — Skills exposed to AIs"
description: "The 40-plus AI-facing skills exposed by the Holy Book: LLM-oriented procedures, versioned on GitHub and organized into families."
weight: 3
date: 2026-05-20
tags: ["holy-book"]
sidebar:
  open: true
---

# 09.03&nbsp;—&nbsp;Skills exposed to AIs

> More than 40 _skills_ (procedures aimed at LLMs) versioned on GitHub. Grouped **into families**. Documented in the Holy Book (chapter "_Using Ocarina with AI_").

## File tree

```
ai/skills/
├── README.md
└── <skill-name>/
    └── SKILL.md
```

Each skill = one folder + a `SKILL.md`.

`SKILL.md`:

- YAML frontmatter with `name` and `description` (used by Claude to decide whether to _trigger_ this skill).
- Markdown body: the detailed procedure, sections, steps, examples.

`README.md`:

- Skills index: groups by family, recalls possible interconnections.

The `docs/.vitepress/plugins/skills.ts` plugin walks this folder and copies them into public pages `/skills/<name>`.

## Families (non-exhaustive list)

|  #  | Family                         | Topic                                                                    |
| :-: | ------------------------------ | ------------------------------------------------------------------------ |
| 01  | [Review](01-review.md)         | Static reads, surface findings                                           |
| 02  | [Analyse](02-analyse.md)       | Dynamic: flakiness, fixture, watcher, screenshot                         |
| 03  | [Black-hat](03-black-hat.md)   | Business-logic-vulnerability ideation                                                 |
| 04  | [Comprehend](04-comprehend.md) | Catalog, ecosystem, SUT constraints, Ocarina indexing in the LLM context |
| 05  | [Pick](05-pick.md)             | Artifact usage (screenshots, logs, reports)                              |
| 06  | [Author](06-author.md)         | Delegate deliverable production to the LLM                               |
| 07  | [Refactor](07-refactor.md)     | Refactor, DRY, introduce retries in POMs                                 |
| 08  | [State](08-state.md)           | Question SUT states (stubs, data persistence...)                         |
| 09  | [Setup](09-setup.md)           | Set up the environment (`setup-environment`) + govern engagement latitude (`profile-environment`) |
| ... | ...                            | ...                                                                      |

## "_Surface, don't apply_"

> **Surface, don't apply.** Skills produce; the user decides.

Every skill produces a report, a suggestion, or a diff. The human decides whether to apply it.

## Recurring chains

### 1. Failing cycle

```
review-report          →  analyse-*         →  write-a-probe
        ↓                       ↓                      ↓
   classification         instrumentation         throwaway script
                                                       ↓
findings propagated to IDENTIFIED_GAPS.md / FRD / scenario comments
                                                       ↓
                                                probe deleted
```

### 2. Promising black-hat scenario

```
empiricism             →  extend-coverage
    ↓                          ↓
verify the SUT          often intentionally failing
```

### 3. Spec change

```
update-frd-and-tests    (FRD first, tests follow)
        ↓
gap tests are reframed, not blindly flipped from red to green
```

### 4. New Ocarina primitive

```
understand-ocarina      →  update → resume
        ↓
walks the docs
```

## Cross-cutting discipline

1. **Surface, don't apply.** The user decides.
2. **Empirical, not assertive.** Ritual phrase: "_Fair point, I'm assuming. Let me verify empirically._"
3. **Gap tests are reframed, not turned green.**
4. **Watcher emissions are negative signals only.** A watcher emitting "_login succeeded_" breaks the contract.
5. **Use distributed systems when a resource is shared.**
6. **Artifact identification by mtime, not just by filename.** UUID suffixes are random.
7. **Latitude only tightens.** The defaults assume an open public demo (read the SUT's source, probe the live app, public credentials). `profile-environment` narrows them per engagement; nothing ever loosens the security hard line.

## Out of scope

> - Doesn't generate tests autonomously.
> - Doesn't patch hallucinations in CI; a failure triggers `review-report` + `analyse-*`.
> - Doesn't rewrite the spec; only `update-frd-and-tests` does, with a revision line.
> - Doesn't run active security tests. Ever.

The perimeter is strict. AI is a tool, not a substitute for human judgment.
