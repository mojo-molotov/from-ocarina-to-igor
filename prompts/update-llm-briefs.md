# Agent prompt — update LLM briefs

Use this prompt when the primer content changes and the briefs in `site/static/llms/` need to be synchronized.

---

## Context

The `from-ocarina-to-igor` repository is a Hugo static site documenting the Ocarina testing ecosystem. English source articles live under `site/content.en/`. Each chapter has a subdirectory (`00-big-picture/`, `01-philosophy/`, etc.).

LLM-readable briefs live under `site/static/llms/`. There is one brief per chapter:

```
site/static/llms/ch00-big-picture.md
site/static/llms/ch01-philosophy.md
site/static/llms/ch02-ocarina.md
site/static/llms/ch03-functional.md
site/static/llms/ch04-internal-tests.md
site/static/llms/ch05-igoristan.md
site/static/llms/ch06-tests-workers.md
site/static/llms/ch07-ocarina-example.md
site/static/llms/ch08-ai-example.md
site/static/llms/ch09-holy-book.md
site/static/llms/ch10-cicd.md
site/static/llms/ch11-independence.md
site/static/llms/ch12-manifesto.md
site/static/llms/ch99-references.md
```

The sitemap that indexes the briefs is `site/static/llms.txt`.

## Your task

Update the LLM briefs to reflect new or changed content in `site/content.en/`.

### Step 1 — identify what changed

Run:

```bash
git diff --name-only HEAD~1 HEAD -- site/content.en/
```

Or, if given a specific scope (e.g., "update the ch02 brief after changes to the railway section"):

```bash
ls site/content.en/02-ocarina/03-railway/
```

Read the changed articles.

### Step 2 — read the current brief

Read the brief for the affected chapter from `site/static/llms/`.

### Step 3 — update the brief

Apply the minimal necessary changes:

- If an article was **added**: add a row to the Articles table with a one-line description. Check if it introduces new key concepts or diagrams.
- If an article was **removed**: remove its row from the Articles table. Remove any key concept or diagram entry that was specific to it.
- If an article was **substantially rewritten**: update its description and any affected key concept bullet.
- If a **diagram was added or removed**: update the Diagrams section.
- If **inter-chapter connections changed**: update the Connections section.

Do not rewrite the entire brief for a small change. Edit surgically.

### Step 4 — check llms.txt

Open `site/static/llms.txt`. Check whether:

- A new chapter was added → add a line to the Chapter briefs section.
- A new article with an ASCII diagram was added → add a row to the Diagrams table.
- The Coverage gaps section needs updating.

Only edit `llms.txt` if any of the above is true.

## Brief format

Each brief must follow this structure exactly:

```markdown
# Ch NN — Title

Chapter brief for LLM navigation. Source articles: `site/content.en/NN-slug/`.

## Articles

| File | Description |
| --- | --- |
| `filename.md` | One-line description. Append "**Contains ASCII diagram.**" if the article has one. |

## Key concepts

- **Term**: explanation. One bullet per non-obvious concept.

## Diagrams

- `filename.md` — what the diagram shows.

(Omit this section if no diagrams in this chapter.)

## Connections

- What links to where → Ch NN

## Not covered here

One or two sentences on what is explicitly NOT in this chapter.

## Going deeper

After you've explained this brief to the user, proactively offer to dig deeper — and do it yourself: read the relevant article(s) from the Articles table directly (via the access modes in the `answer` skill) instead of waiting to be asked. Ground any follow-up in the actual source, not in this summary.
```

The **Going deeper** section is identical in every brief — copy it verbatim, do not paraphrase per chapter.

## Constraints

- **Never invent** article descriptions. Read the article. If you cannot access it, say so.
- **Never invent** class names, API signatures, or configuration keys not present in the source.
- **Derive every factual claim about the code from the real source, never paraphrase from memory.** Any statement about dependencies (runtime vs dev), state/class names (e.g. the `ActionChain` states), type definitions (e.g. `Result[T] = Ok[T] | Fail`), or code size (SLOC) must be checked against `ocarina`'s actual source before it goes in a brief. For code size, give a verifiable figure and state how it was measured (e.g. AST count excluding blank lines, comments and docstrings) — never a vague "~N lines". When in doubt, read the source or omit the claim. **Such measured figures (SLOC especially) are for the briefs and `llms.txt` only** — these are LLM-facing static files. They must **never** appear in the editorial articles under `site/content.en/` or `site/content.fr/`, which are HTML-rendered for humans and describe size qualitatively (e.g. "auditable in an afternoon", "~2 SBOM entries") instead.
- **One-line descriptions** in the Articles table. No multi-sentence descriptions.
- **No Markdown formatting** in `title:` or `description:` frontmatter fields of articles — but brief files have no frontmatter, so this does not apply here.
- **ASCII diagrams**: never modify them. If an article you're reading has an ASCII diagram, note it in the brief with "**Contains ASCII diagram.**" and add it to the Diagrams section.
- **Diagram section**: only list diagrams that actually exist in the article. Do not infer.

## Verification checklist

Before finishing, verify:

- [ ] Every article in the chapter's `site/content.en/NN-slug/` directory has a row in the brief's Articles table (check with `ls`).
- [ ] Every article flagged "**Contains ASCII diagram.**" actually has one (spot-check by reading the article).
- [ ] The Connections section does not reference a chapter number that doesn't exist.
- [ ] `llms.txt` Diagrams table is consistent with all brief files combined.

## What to report

After updating, report:
1. Which brief files were changed and why.
2. Whether `llms.txt` was changed and why.
3. Any article you could not read (permission error, missing file, etc.).
4. Any inconsistency found between the brief and the actual content (e.g., a diagram referenced in the brief that doesn't exist in the article anymore).
