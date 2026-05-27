---
title: "09.04 — CLAUDE.md and CLAUDE.slim.md"
description: "The Holy Book actively publishes the CLAUDE.md files. This lets an LLM fetch the project's docs without going through the repo."
weight: 4
date: 2026-05-20
series: ["holy-book"]
series_order: 4
---

# 09.04&nbsp;—&nbsp;`CLAUDE.md` and `CLAUDE.slim.md`

> The Holy Book **actively publishes** the `CLAUDE.md` files. This lets an LLM fetch the project's docs without going through the repo.

## The two files

```
ai/
├── CLAUDE.md       # full version (rules + project layout)
└── CLAUDE.slim.md  # short version (rules only)
```

## Public URLs

```
https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md
https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md
```

Holy Book quote (chapter "_Using Ocarina with AI_"):

> Slim when context is heavy; full for onboarding and reviews. Full wins on disagreement.

## Slim/Full differences

| Aspect                    | `CLAUDE.md` | `CLAUDE.slim.md` |
| ------------------------- | ----------- | ---------------- |
| Volume                    | ~600+ lines | ~150-200 lines   |
| Rules                     | ✅ all      | ✅ all           |
| Detailed justifications   | ✅          | ❌               |
| Past examples (expertise) | ✅          | ❌               |
| Project organization      | ✅          | ❌               |
| Technical hierarchy       | ✅          | ❌               |
| PR conventions            | ✅          | ❌               |
| Expected CI shape         | ✅          | ❌               |

## Right file at the right time

```
Onboarding (first contact with the project)  →  CLAUDE.md  (read all)
Normal run (just apply rules)                 →  CLAUDE.slim.md (save tokens)
PR review                                     →  CLAUDE.md (justifications)
Deep audit                                    →  CLAUDE.md (everything)
```

## `CLAUDE.md`

Typical sections (based on `ocarina-with-ai-example`):

1. **Project context**: repo, framework, SUT.
2. **Project philosophy**: "_No tricks or hacks_", "_Teach the pattern, not the symptom_".
3. **Layout**: full repo tree.
4. **Conventions**: 12+ concrete rules.
5. **Hard-won rules**: lessons from past failures.
6. **Test strategy**: cycle structure.
7. **Running tests**: CLI commands.
8. **Reports and screenshots**: usage rules.
9. **Scenario fragments**: extraction criteria.
10. **Data-driven tests**: conventions.
11. **Supplementary conventions**.

## `CLAUDE.slim.md`

Just the **rules** (no detailed justifications, no examples):

```markdown
# Slim rules — Ocarina with AI example

- No tricks or hacks. Polling fix > JS click bypass.
- Teach the pattern, not the symptom.
- Security tests: functional and static, never active.
- Use constants: no magic numbers.
- Datasets: human decision; propose, don't execute.
- Empirically verify the SUT before encoding.
- Re-derive each run: no diagnosis inheritance.
- One scenario per file (data-driven exception).
- Top docstring as arrows flow.
- All create_selenium_test() at bottom of file.
- POM selectors at top of class.
- Always WebDriverWait, never raw find_element.
- Implicit wait set by CLI, never patched in POM/test code.
- Gap tests: reframed, not flipped to green.
- Watcher signals: negative only.
- Distributed when resource is shared.
- Mtime, not filename.
- ...
```

Each line = one rule.

## Why expose to LLMs

| Without public exposure                                                       | With exposure                       |
| ----------------------------------------------------------------------------- | ----------------------------------- |
| An LLM has to clone the repo to read the CLAUDE.md                            | Canonical URL → a single `WebFetch` |
| No "_offline_" discovery (a user asking an Ocarina question without the repo) | The LLM can read the docs directly  |
| Hard for LLM search engines to index                                          | Naturally indexed                   |

## The _user doc_ vs _LLM doc_ distinction

| Doc                                                 | Audience      | Format                              |
| --------------------------------------------------- | ------------- | ----------------------------------- |
| Holy Book (`/setup`, `/scenarios-composability`, …) | Human         | Prose, examples, illustrations      |
| `CLAUDE.md`                                         | LLM (+ human) | Dry rules, condensed justifications |
| `skills/*/SKILL.md`                                 | LLM           | Operational recipes                 |

Three audiences, three formats. The Holy Book serves all three&nbsp;—&nbsp;the **practical embodiment** of "_AI is the bridge_".

## "_Canonical resources_" pattern

URLs are stable:

```
https://mojo-molotov.github.io/ocarina-holy-book/llms.txt
https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt
https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md
https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md
https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf
https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf
```

Documented in the Holy Book (chapter "_Using Ocarina with AI_"), at the end:

> ## Exposed resources
>
> - https://mojo-molotov.github.io/ocarina-holy-book/llms.txt
> - https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt
> - https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md
> - https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-ru.pdf
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf
