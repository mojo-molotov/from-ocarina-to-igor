# from-ocarina-to-igor

A **book** on the **Ocarina** test-framework ecosystem built by Igor
Casanova ([`mojo-molotov`](https://github.com/mojo-molotov)). It reads
top-to-bottom as a deep, multi-file reverse-engineering of the
framework, its surrounding repositories, its philosophy, and its
cultural roots.

The book lives as a static site under [`site/`](site/), published in
both **English** ([`site/content.en/`](site/content.en/)) and
**French** ([`site/content.fr/`](site/content.fr/)) — English is the
default; French is reachable from the language switcher.

The site is built with **Hugo** + the **hugo-book** theme and ships with
**Pagefind** for client-side search.

---

## What is this book?

Six public repositories make up the Ocarina ecosystem:

| Repository                | Role                                                        |
| ------------------------- | ----------------------------------------------------------- |
| `ocarina`                 | Python framework (PyPI). DSL, orchestration, infra.         |
| `ocarina-example`         | Canonical end-to-end suite against the Igoristan.           |
| `ocarina-with-ai-example` | End-to-end suite against CURA, co-written with Claude Code. |
| `igoristan`               | Deliberately chaotic public SUT (GitHub Pages).             |
| `tests-workers`           | Vercel Edge backend (OTP, Corsicadex).                      |
| `ocarina-holy-book`       | Public documentation site + AI skills.                      |

Reading any one of them in isolation gives you part of the picture. This book ties them together: which repo talks to which, what the
contracts are, why the framework was designed the way it was, and
where it sits relative to the broader industry conversation about
testing.

---

## Table of contents

| Chap. | Subject                                                                                                                       | Folder                                                                 |
| :---: | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
|  00   | Big picture: cartography, execution flow, repo relations                                                                      | [`00-big-picture/`](site/content.en/00-big-picture/)                   |
|  01   | Philosophy of Igor Casanova                                                                                                   | [`01-philosophy/`](site/content.en/01-philosophy/)                     |
|  02   | The Ocarina framework, internal mechanics (Railway, invariants, orchestration, infra, opinionated layer, custom types)        | [`02-ocarina/`](site/content.en/02-ocarina/)                           |
|  03   | Functional programming with Ocarina (Effect, Thunk, Result, closures, lazy evaluation, fold, PEP 695 generics)                | [`03-functional/`](site/content.en/03-functional/)                     |
|  04   | Internal tests of the framework (cram, pytest, mypy plugins, syrupy, hypothesis, coverage policy, Allure)                     | [`04-internal-tests/`](site/content.en/04-internal-tests/)             |
|  05   | The Igoristan, public SUT                                                                                                     | [`05-igoristan/`](site/content.en/05-igoristan/)                       |
|  06   | `tests-workers`, the Vercel Edge backend (OTP coordination, Corsicadex)                                                       | [`06-tests-workers/`](site/content.en/06-tests-workers/)               |
|  07   | `ocarina-example`, the canonical suite                                                                                        | [`07-ocarina-example/`](site/content.en/07-ocarina-example/)           |
|  08   | `ocarina-with-ai-example`, the AI-co-authored suite against CURA                                                              | [`08-ai-example/`](site/content.en/08-ai-example/)                     |
|  09   | Holy Book, public documentation + AI skills                                                                                   | [`09-holy-book/`](site/content.en/09-holy-book/)                       |
|  10   | CI/CD across the whole ecosystem                                                                                              | [`10-cicd/`](site/content.en/10-cicd/)                                 |
|  11   | The independence of testers (sovereign grammar, auditability, explicit refusals)                                              | [`11-independence/`](site/content.en/11-independence/)                 |
|  12   | (Culture) Manifesto deciphered: hacker scene, infopreneurs/SaaS, DHH/PG, λ-calculus, AI & typing, underground 2000s, ideology | [`12-manifesto-deciphered/`](site/content.en/12-manifesto-deciphered/) |
|  99   | Glossary, file index                                                                                                          | [`99-references/`](site/content.en/99-references/)                     |

The same listing lives in [`site/content.en/_index.md`](site/content.en/_index.md), which renders as the site homepage.

---

## Repository layout

```
.
├── README.md              ← you are here
├── CLAUDE.md              ← editorial conventions (FR typography, vocabulary, no-touch zones)
├── scripts/
│   └── setup.sh           ← one-shot post-clone hook activation
├── .githooks/
│   └── pre-commit         ← Prettier on staged site/content.en/**/*.md
├── .github/workflows/
│   └── deploy.yml         ← Hugo build + Mermaid purge + HTML minify + GitHub Pages
└── site/
    ├── hugo.toml          ← Hugo config (minify rules, markup, baseURL conditional via env)
    ├── build.sh           ← local build: Hugo + Pagefind index
    ├── content.en/        ← English chapters (default language)
    ├── content.fr/        ← French chapters
    ├── layouts/           ← overrides on top of hugo-book (render-link, render-image, search modal, filter chips)
    ├── static/            ← assets/img/, fonts, etc.
    └── themes/hugo-book/  ← vendored theme
```

---

## After clone

```bash
./scripts/setup.sh
```

Activates the repository's git hooks via `git config core.hooksPath
.githooks`. Without this, the pre-commit Prettier formatter on staged
markdown won't run. Git does not auto-install hooks from a clone by
design (security); this is the one-shot opt-in.

---

## Running the site locally

```bash
cd site
hugo server                # http://localhost:1313, live-reload
./build.sh                 # full production build → site/public/, incl. Pagefind index
npx -y pagefind --site public --serve   # preview with search enabled
```

Requires Hugo extended ≥ 0.161. Node is needed only for the Pagefind
index step (the build script uses `npx`).

---

## Build pipeline

`site/build.sh` runs three steps and is the single source of truth for
both the local production build and the CI deploy.

1. **Hugo** — `hugo --gc --cleanDestinationDir`, with optional
   `--baseURL` (set via `HUGO_BASEURL` env in CI to
   `https://mojo-molotov.github.io/from-ocarina-to-igor/`) and optional
   `--minify` (gated by `HUGO_MINIFY=1`).
2. **Drop Mermaid** — `rm -f public/mermaid.min.js`. The hugo-book
   theme ships ~3 MB of Mermaid into `static/`; no page in the book
   uses it. A guard immediately after `rm` fails the build if any
   rendered HTML still references the purged asset.
3. **Pagefind indexing** — `npx -y pagefind --site public
--root-selector "article.book-article" --exclude-selectors "pre"`.

CI ([`/.github/workflows/deploy.yml`](.github/workflows/deploy.yml))
adds:

- `HUGO_BASEURL` derived from `actions/configure-pages`.
- `HUGO_MINIFY=1` for CSS/JSON/SVG/XML minification (JS is intentionally
  left untouched via `hugo.toml`).
- A dedicated **HTML minify** step using `html-minifier-terser@7` via
  `bunx`, since Hugo's HTML minifier alone preserves more whitespace than
  desired.
- Upload to GitHub Pages via `actions/deploy-pages`.

---

## Editorial conventions

[`CLAUDE.md`](CLAUDE.md) at the repo root captures the hard rules:

- **ASCII diagrams are off-limits.** They look broken in source on
  purpose — certain line breaks are required for correct rendering on
  the live site (hugo-book + browser quirks). Never reflow them.
- **Vocabulary.** Concurrent execution is "parallélisation" /
  "parallélisés", never "parallélisme" / "en parallèle".
- **Frontmatter is plain text.** No backticks, underscores, or asterisks
  in `title:` or `description:` — they feed the sidebar and the
  `<meta description>` / Open Graph tags, where Markdown is not
  rendered and the raw characters leak into the UI.

French-language articles (under [`site/content.fr/`](site/content.fr/))
use full French typography (non-breaking spaces around `:`, `;`, `?`,
`!`, `→`, `—`, `/`, and inside guillemets), enforced by batch scripts
and locked in by the pre-commit Prettier hook. English articles
(under [`site/content.en/`](site/content.en/)) follow standard
English spacing.

---

## Search

A custom modal on top of the Pagefind JS API (see
[`site/layouts/_partials/docs/inject/body.html`](site/layouts/_partials/docs/inject/body.html)).
Trigger with `⌘K` / `Ctrl+K`.

Filters are surfaced in two collapsible groups:

- **Series** — chapter membership (one per chapter).
- **Tags** — cross-cutting concerns (rop, watcher, scenarios,
  istqb, typage, selenium, otp, etc.).

Selecting multiple values within a group is OR. Selecting across both
groups is AND. Tag relevance is gated by body-occurrence frequency
(threshold of 5 mentions across non-fenced prose); anecdotal mentions
do not earn a tag.

---

## License

The code in this repository (Hugo config, layouts, scripts, build
plumbing) is MIT-licensed. The editorial content under `site/content.en/`
is the author's prose — © Igor Casanova; ask before redistributing.

The vendored `site/themes/hugo-book/` retains its own MIT license from
[alex-shpak/hugo-book](https://github.com/alex-shpak/hugo-book).

---

Built by [@mojo-molotov](https://github.com/mojo-molotov)  
Fueled by figatellu and Квас.

[_So I wanna remember number nine._](https://www.youtube.com/watch?v=djDb1zdnSzA)
