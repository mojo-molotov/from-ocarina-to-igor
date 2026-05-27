# CLAUDE.md

## ASCII diagrams: do not touch

Never modify, "fix", or reformat ASCII diagrams in the markdown content under
`site/content/`. This includes line breaks that look "broken", trailing spaces,
odd alignment, or characters that seem inconsistent.

Some of these layouts are deliberate — the user has verified that certain
seemingly-wrong line breaks are required to render correctly on the live site
(hugo-book + browser rendering quirks). What looks broken in the source is
often what makes the diagram display correctly in prod.

Rule: leave every ASCII diagram exactly as it is. If a diagram seems wrong,
ask before changing anything. Do not "clean up" diagrams as part of an
unrelated edit.

## Vocabulary: concurrent programming

When writing about concurrent execution in programming contexts, use:

- **parallélisation** (not "parallélisme")
- **parallélisés** / **parallélisée** (not "en parallèle")

Examples:
- ✅ "la parallélisation des tests smoke"
- ✅ "les jobs sont parallélisés"
- ❌ "le parallélisme des tests"
- ❌ "les jobs s'exécutent en parallèle"

This applies to prose in `site/content/` and to any new explanation involving
threads, async, workers, CI matrix jobs, etc.

## Frontmatter: plain text only

In `site/content/**/*.md` frontmatter, the `title:` and `description:` fields
must be **plain editorial text**. No Markdown formatting:

- ❌ no backticks (`` `Foo` ``)
- ❌ no underscores for italics (`_foo_`)
- ❌ no asterisks for bold (`**foo**`)
- ❌ no inline code, no links, no anything

Why: these fields feed the sidebar title and the `<meta description>` /
Open Graph tags. Hugo doesn't render Markdown there — the raw characters
leak into the UI and the SEO output. Sidebars look broken, meta descriptions
get junk like `` `TestCycle[Driver]` `` literal.

Use plain words. Capitalize a class name normally if needed. The H1 in the
body of the article can keep all the Markdown formatting you want.
