---
title: "Chapter 09 — Holy Book"
description: "The Holy Book, Ocarina's public documentation: VitePress in FR, EN and RU, AI-generated PDFs and 40-plus skills exposed to LLMs."
weight: 10
date: 2026-05-20
tags: ["holy-book"]
sidebar:
  open: true
---

# Chapter 09&nbsp;—&nbsp;Holy Book

> Ocarina's public documentation. VitePress, FR + EN + RU, AI-generated PDFs, 40+ _skills_ exposed to LLMs. URL: <https://mojo-molotov.github.io/ocarina-holy-book/>

## Outline

|  #  | File                                               | Topic                                                             |
| :-: | -------------------------------------------------- | ----------------------------------------------------------------- |
| 01  | [`01-stack-vitepress.md`](01-stack-vitepress.md)   | VitePress 2 alpha + @sugarat theme + in-house plugins + pagefind. |
| 02  | [`02-i18n.md`](02-i18n.md)                         | I18n FR/EN/RU: page structure, conventions.                       |
| 03  | [`03-skills/`](03-skills/)                         | The 40+ _skills_ exposed to AIs, grouped into families.           |
| 04  | [`04-claude-md.md`](04-claude-md.md)               | `CLAUDE.md` / `CLAUDE.slim.md` exposed on the site.               |
| 05  | [`05-pdf-generation.md`](05-pdf-generation.md)     | FR/EN/RU PDF generation via `prompts/generate-books/`.            |
| 06  | [`06-public-resources.md`](06-public-resources.md) | Table of public URLs (`llms.txt`, `llms-full.txt`, PDFs, etc.).   |

## Goals

The Holy Book **exists as much for humans as for LLMs**:

- Generates `llms.txt` / `llms-full.txt` at build (standards for exposing content to LLMs).
- Exposes `CLAUDE.md` / `CLAUDE.slim.md`.
- Serves the FR/EN/RU PDFs.
- Documents 40+ _skills_ accessible to tools like Claude Code.

The **practical embodiment** of "_AI is the bridge_" (cf. [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md)).

## Ideology

The Holy Book (chapter "First feedbacks"):

> Code is raw data. Auditable. Inspectable. **A white box.** Exactly what AI has known how to work with since its very beginnings.

The Holy Book operationalizes this bet. Without it, an LLM has to _guess_ how Ocarina works. With it, it _consults_ documentation written explicitly for it.

## Pages

```
docs/
├── index.md                                                      # Blog landing
├── what-is-it.md                                                 # What is Ocarina?
├── first-feedbacks.md                                            # First feedbacks
├── setup.md                                                      # First steps
├── scenarios-composability.md                                    # First scenarios
├── datasets-smoke-tests-setup-teardown-proxy-api-and-caching.md  # First jutsus
├── handling-flakiness.md                                         # First real-world hurdles
├── extensibility.md                                              # Extensibility
└── using-ocarina-with-ai.md                                      # Using Ocarina with AI
```

Each page also exists in FR (`docs/fr/`).  
And in RU (`docs/ru/`).

VitePress _frontmatter_ conventions:

```yaml
---
sticky: 1
# pagefind-indexed: false
description: ...
date: 2026-04-24
head:
  - - meta
    - property: og:image
      content: http://...
---
```

## Related reading

- Which concepts the doc pages revisit: [`../02-ocarina/`](../02-ocarina/), [`../03-functional/`](../03-functional/)
- The AI discipline documented in `using-ocarina-with-ai.md`: [`../08-ai-example/01-ai-manifesto.md`](../08-ai-example/01-ai-manifesto.md)
