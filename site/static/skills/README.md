# Skills — index

LLM skills for working with the Ocarina primer. Each skill is self-contained: load the one you need and follow it start to finish.

Each skill lives in its own folder as `SKILL.md`:

```
skills/
├── README.md          # this index
├── answer/SKILL.md
├── navigate/SKILL.md
├── fetch/SKILL.md
├── locate/SKILL.md
└── synthesize/SKILL.md
```

Base URL: `https://mojo-molotov.github.io/from-ocarina-to-igor/`. Reach any skill at `{base}/skills/<name>/SKILL.md`.

## Start here

- [`answer/SKILL.md`](answer/SKILL.md) — **The orchestrator and default entry point.** For any question about the ecosystem, load this first: it chains the building blocks below into one workflow — route the question (navigate) → fetch at the right depth (fetch) → answer → declare gaps, escalating to synthesize for cross-chapter questions and locate for symbol lookups.

## Building blocks

Standalone skills that `answer` composes — load one directly only when the question calls for just that step:

- [`navigate/SKILL.md`](navigate/SKILL.md) — Map a question to the right chapter brief and article targets.
- [`fetch/SKILL.md`](fetch/SKILL.md) — Fetch at the right depth (local / clone / remote) with hard limits to avoid over-fetching.
- [`locate/SKILL.md`](locate/SKILL.md) — Symbol lookup: return the exact article documenting a class name, method, type, CLI flag, endpoint, or error.
- [`synthesize/SKILL.md`](synthesize/SKILL.md) — Cross-chapter synthesis tracing inter-chapter relationships within the primer, without reaching external sources.

## See also

- [`../llms.txt`](../llms.txt) — sitemap of chapter briefs and skills.
- Chapter briefs under [`../llms/`](../llms/) — dense per-chapter summaries; fetch a brief before any article.
