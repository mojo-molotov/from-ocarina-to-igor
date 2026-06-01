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

This is a language-specific rule: it governs **French** prose
(`site/content.fr/`). English prose (`site/content.en/`) keeps the
standard English terms ("parallelization", "marshalling", etc.).

### marshalling → marshallisation (French only)

In French prose, never write the English gerund "marshalling". Use the
French noun **marshallisation**. The verb forms **marshalliser** /
**marshallisé** / **marshallisée** / **marshallisés** are fine and preferred.

Examples (French):
- ✅ "la marshallisation par `submit`"
- ✅ "chaque appel est marshallisé sur le thread propriétaire"
- ❌ "le marshalling par `submit`"

In English (`site/content.en/`), "marshalling" / "marshalled" stay as-is.

### bout-à-bout → de bout en bout (French only)

In French prose, never write "bout-à-bout". Use **de bout en bout** (or
the noun phrase **test de bout en bout**).

Examples (French):
- ✅ "un test de bout en bout"
- ✅ "le scénario vérifié de bout en bout"
- ❌ "un test bout-à-bout"
- ❌ "vérifié bout-à-bout"

The acronym **e2e** stays as-is in both languages.

### hanguer → cesser de répondre (French only)

In French prose, "hanguer" (a franglais coinage from English "to hang")
is not a word. Use **cesser de répondre**, or **se figer** / **rester
bloqué** depending on context.

Examples (French):
- ✅ "renvoie une erreur bornée sans cesser de répondre"
- ✅ "le process se fige au lieu de se terminer"
- ❌ "sans hanguer"
- ❌ "le process hangue"

In English (`site/content.en/`), "hang" / "hangs" stay as-is.

### wall-clock → elapsed real time (both languages)

Never use "wall-clock" / "wall clock". Use **elapsed real time** in
English. In French, use **temps réel écoulé** (e.g. a timeout bound is
"un seuil de temps réel écoulé", not "un délai wall-clock").

Examples:
- ✅ (en) "asserted with an elapsed-real-time ceiling"
- ✅ (fr) "assertion bornée par un seuil de temps réel écoulé"
- ❌ "a wall-clock ceiling" / "un plafond wall-clock"

### ceiling → seuil (French only)

In French prose, don't use the English "ceiling" (nor leave it untranslated).
Use **un seuil** (masculine: "un seuil", "le seuil"). In English, "ceiling"
stays.

Examples (French):
- ✅ "un seuil de liveness"
- ❌ "une ceiling de liveness" / "un ceiling"

### deadline is feminine in French

When "deadline" is used in French prose, it is **feminine**: write
**une deadline** / **la deadline**, never "un deadline".

Examples (French):
- ✅ "ce n'est pas une deadline par opération"
- ❌ "ce n'est pas un deadline par opération"

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
