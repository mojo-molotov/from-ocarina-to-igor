# Ch 09 — Holy Book

Chapter brief for LLM navigation. Source articles: `site/content.en/09-holy-book/`.

## Articles

| File | Description |
| --- | --- |
| `01-stack-vitepress.md` | VitePress 2 alpha + @sugarat theme + in-house plugins + Pagefind local search. Build toolchain. |
| `02-i18n.md` | Internationalization: FR (primary) / EN / RU. Page structure, translation conventions, fallback behavior. |
| `03-skills/_index.md` | Skills taxonomy map: 40+ LLM procedures grouped into families (review, analyse, black-hat, comprehend, pick, author, refactor, state, setup). **Contains ASCII diagram.** |
| `03-skills/01-review.md` | `review` skill family: code review procedures. |
| `03-skills/02-analyse.md` | `analyse` skill family: analysis procedures. |
| `03-skills/03-black-hat.md` | `black-hat` skill family: adversarial testing procedures. |
| `03-skills/04-comprehend.md` | `comprehend` skill family: understanding procedures. |
| `03-skills/05-pick.md` | `pick` skill family: selection / decision procedures. |
| `03-skills/06-author.md` | `author` skill family: authoring / writing procedures. |
| `03-skills/07-refactor.md` | `refactor` skill family: refactoring procedures. |
| `03-skills/08-state.md` | `state` skill family: state-management procedures. |
| `03-skills/09-setup.md` | `setup` skill family: environment setup procedures. |
| `04-claude-md.md` | `CLAUDE.md` / `CLAUDE.slim.md` structure and content, exposed publicly on the Holy Book site. **Contains ASCII diagram.** |
| `05-pdf-generation.md` | FR/EN/RU PDF generation pipeline via `prompts/generate-books/`. Reportlab + AI orchestration. **Contains ASCII diagram.** |
| `06-public-resources.md` | Table of all public URLs: `llms.txt`, `llms-full.txt`, PDFs, skills directory, Allure report, GitHub repos. |

## Key concepts

- **Holy Book URL**: `https://mojo-molotov.github.io/ocarina-holy-book/`
- **`llms.txt` / `llms-full.txt`**: generated at build time. `llms.txt` is a structured sitemap for LLMs. `llms-full.txt` is the entire Holy Book content concatenated. Both are standards for exposing documentation to LLMs.
- **40+ skills**: versioned LLM procedures (like plugins for AI agents) covering the full lifecycle of working with Ocarina — from writing a new scenario to debugging a CI failure. Skills are at `https://github.com/mojo-molotov/ocarina-holy-book/tree/main/docs/.vitepress/public/skills`.
- **`CLAUDE.md`**: the AI operating instructions file, exposed publicly so users can copy it into their own projects. `CLAUDE.slim.md` is a condensed version for contexts with token limits.
- **PDF generation**: the Holy Book generates trilingual PDFs using Reportlab, orchestrated by an AI agent reading `prompts/generate-books/`. The pipeline is documented with a flow diagram.
- **Three languages**: FR is the primary language (author's native language). EN and RU are maintained. The i18n article documents which pages exist in all three and which fall back to FR.

## Diagrams

- `03-skills/_index.md` — skills taxonomy map.
- `04-claude-md.md` — CLAUDE.md structure.
- `05-pdf-generation.md` — PDF generation pipeline.

## Connections

- Public resources referenced throughout the primer → `06-public-resources.md`
- Skills used in Ch 08 (AI example) → `03-skills/`
- CLAUDE.md usage in ocarina-with-ai-example → Ch 08 (`03-canonical-documents.md`)
- CI workflow that builds and deploys the Holy Book → Ch 10

## Not covered here

The Holy Book's full content — the primer describes the Holy Book's structure and public resources. The Holy Book itself is the authoritative source for user-facing documentation (setup, onboarding, first scenarios). Read `llms-full.txt` for complete content.

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
