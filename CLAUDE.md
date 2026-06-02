# CLAUDE.md

## Pull requests: always in English

Pull requests on this repo are **always written in English** — title AND body,
with no exception. This holds even when the change is entirely about French
content (`site/content.fr/`) and even when the whole conversation with the user
is in French. The site is bilingual, but the project's PRs (like commit
messages) are English-only. Never open or edit a PR with a French title or body.

## Prompts: reusable task playbooks

The `prompts/` directory holds reusable workflow prompts for recurring tasks on
this repo. Before doing one of these tasks by hand, read the matching prompt and
follow it — they encode the exact procedure, format, and constraints the user
expects.

- `prompts/update-llm-briefs.md` — syncing the LLM briefs in `site/static/llms/`
  (and `site/static/llms.txt`) after content under `site/content.en/` changes.
  Follow it whenever primer content is added, removed, or substantially edited so
  the briefs don't drift from the source.

When a task matches a prompt in `prompts/`, that prompt's instructions take
precedence over improvising. If none matches, proceed normally.

## Measured figures: LLM briefs only, not editorial content

Hard numbers measured from the real `ocarina` source — SLOC counts especially —
belong in the **LLM-facing** files only: the briefs under `site/static/llms/` and
`site/static/llms.txt`. They are static files an LLM reads to size the codebase;
they are not rendered as editorial HTML.

Never put such a measured figure in the **editorial content** under
`site/content.en/` or `site/content.fr/` (it is rendered to HTML and read by
humans on the site). There, describe size qualitatively instead — e.g. "auditable
in an afternoon", "~2 SBOM entries", "a single runtime dependency" — the way the
articles already do.

In the briefs, when you cite a measured figure, give a verifiable number and state
how it was measured (e.g. "~4,060 SLOC, AST count excluding blank lines, comments
and docstrings; ~8,700 raw lines in `src/`") — never a vague "~N lines".

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

## French prose: no English calque

When writing French (`site/content.fr/`), do not transpose English syntax word
for word. Rethink the sentence in French — French word order, verbs, and idioms
are not the English ones. This applies especially when translating an English
article into its French counterpart: translate the *meaning*, not the structure.

Watch for these traps (real ones that slipped through before):

- ❌ "re-dérive l'échec" → ✅ "reprend l'analyse de zéro" (don't calque
  "re-derive")
- ❌ "échelle du synthétique au réel" → ✅ "remonte du synthétique vers le réel"
- ❌ "plan d'effort de test" → ✅ "chiffrage de l'effort de test"
- ❌ "la latitude que l'engagement accorde au LLM" → ✅ "la latitude laissée à
  l'IA pour une mission" (a noun like "engagement" doesn't *accorder* anything;
  it's the human/the mission that sets the bounds)
- ❌ "blast radius" rendered literally → ✅ "ce qu'un changement touche en aval"
- ❌ "(défaut)" for a default value → ✅ "(par défaut)" (calque of "(default)";
  in French it is always *par défaut* — "défaut" alone means a flaw, not a
  default value)

Rule: after translating, reread the French alone. If a phrase sounds like
English wearing French words, rewrite it. Keep the project's own established
vocabulary (e.g. "un rouge"/"un vert" for test status, "flake"/"flakiness",
"smoke-gate") — that is house lexicon, not calque.

Rule: do **two to five anti-calque passes** before presenting French — never
ship a first draft. A single pass reliably leaves calque in. On each pass,
reread the French *alone* (ignore the English source) and hunt specifically
for: noun-phrase calques ("unité d'I/O disque", "le plugin lourd"), verb+object
calques ("écrit un chemin", "ramener à un multiplicateur"), and English
code-jargon metaphors ("chemin" for a code path, "long pole"). Rewrite each,
then pass again — repeat until a read-through trips on nothing. Only then is it
ready. Do not make the reader be the one who catches the calque.

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
