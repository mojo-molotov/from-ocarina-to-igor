---
title: "09.06 — Public resources"
description: "The full table of public URLs exposed by the Holy Book, for humans, LLMs and scrapers."
weight: 6
date: 2026-05-20
series: ["holy-book"]
series_order: 6
---

# 09.06&nbsp;—&nbsp;Public resources

> Full table of public URLs exposed by the Holy Book. For humans, LLMs, scrapers.

## Listing (potentially non-exhaustive)

| URL                                                                   | Content                                       | Target audience          |
| --------------------------------------------------------------------- | --------------------------------------------- | ------------------------ |
| `https://mojo-molotov.github.io/ocarina-holy-book/`                   | Home (EN)                                     | Human                    |
| `https://mojo-molotov.github.io/ocarina-holy-book/fr/`                | Home (FR)                                     | Human                    |
| `https://mojo-molotov.github.io/ocarina-holy-book/ru/`                | Home (RU)                                     | Human                    |
| `https://mojo-molotov.github.io/ocarina-holy-book/what-is-it`         | Article (EN)                                  | Human                    |
| `https://mojo-molotov.github.io/ocarina-holy-book/fr/what-is-it`      | Article (FR)                                  | Human                    |
| `https://mojo-molotov.github.io/ocarina-holy-book/ru/what-is-it`      | Article (RU)                                  | Human                    |
| ... (other doc pages in EN+FR+RU)                                     | ...                                           | Human                    |
| `https://mojo-molotov.github.io/ocarina-holy-book/llms.txt`           | Minimal index for LLMs                        | LLM                      |
| `https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt`      | All content in plaintext                      | LLM, scraper             |
| `https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md`          | Full project rules                            | LLM, human (onboarding)  |
| `https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md`     | Short project rules                           | LLM (context budget)     |
| `https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf`     | A4 PDF docs (EN)                              | Human (offline)          |
| `https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf`     | A4 PDF docs (FR)                              | Human (offline)          |
| `https://mojo-molotov.github.io/ocarina-holy-book/ocarina-ru.pdf`     | A4 PDF docs (RU)                              | Human (offline)          |
| `https://mojo-molotov.github.io/ocarina-holy-book/skills/<name>`      | AI skill page                                 | Human, LLM               |
| `https://mojo-molotov.github.io/ocarina-holy-book/assets/content/...` | Images, audio (article covers, illustrations) | Human (inline rendering) |

## `llms.txt` (emerging standard)

Spec: <https://llmstxt.org/> (proposed in 2024).

Typical format:

```
# The Ocarina Holy Book

> Ocarina is Igor's automated web browser testing framework.

## Pages

- [What is Ocarina?](https://mojo-molotov.github.io/ocarina-holy-book/what-is-it) — Test frameworks all made the same bad bet. Ocarina does the opposite.
- [First feedbacks](https://mojo-molotov.github.io/ocarina-holy-book/first-feedbacks) — The first wave of criticism Ocarina ever received.
- [First steps](https://mojo-molotov.github.io/ocarina-holy-book/setup) — Onboarding tutorial.
- ... (every page)

## Resources

- [llms-full.txt](https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt) — All content in plaintext.
- [CLAUDE.md](https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md) — AI rules.
- ... etc
```

An LLM visiting the site can **read `llms.txt` first** and know everything that exists.

## `llms-full.txt`

The **plain text** content of every page, concatenated. Lets an LLM (Claude, ChatGPT, etc.) fetch the docs in **a single HTTP fetch** rather than N fetches.

Typical volume: ~500 KB of plain text (for ~5,000 Markdown lines).

## `robots.txt`

```
# docs/public/robots.txt
User-agent: *
Allow: /
```

Everything is crawlable. No restriction on bots or LLMs. "_If you want to know, read, RTFM_." No captcha, no paywall.

## `.nojekyll`

```
# docs/public/.nojekyll
```

(Empty file.)

GitHub Pages uses Jekyll by default. Jekyll was converting files into HTML in a way that broke the skills. This disables it.

## `.spa`

```
# docs/public/.spa
```

VitePress artifact with no special interest, implementation detail.

## `favicon.ico` and `logo.png`

The `favicon.ico` shows in the browser tab. The `logo.png` appears in the banner, top-left (`@sugarat/theme`).

## LLM flow

```
1. GET /llms.txt                              → resource list
2. (option A) GET /llms-full.txt              → everything in one fetch
   (option B) GET /CLAUDE.md                  → compact rules
   (option C) GET /<page>                     → specific page
3. If question on internal mechanics:         → fetch Ocarina's source on GitHub
4. If question on usage:                      → fetch ocarina-example
5. If question on AI usage:                   → fetch ocarina-with-ai-example
```

## Holy Book reminder

The Holy Book (chapter "_Using Ocarina with AI_") lists the URLs in cleartext at the bottom:

> ## Exposed resources
>
> - https://mojo-molotov.github.io/ocarina-holy-book/llms.txt
> - https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt
> - https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md
> - https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-ru.pdf
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf

A **public invitation** to LLMs: "_Here is what we expose for you, help yourselves._"

## Consistency with the political stance

See [`../11-independence/`](../11-independence/)

The author wants AI to consume the docs. A deliberate choice:

- Rather than resisting LLM indexing (paywall, captcha, DRM), we invite.
- Rather than obscuring project rules ("_we don't share our CLAUDE.md_"), we publish.
- Rather than gatekeeping ("_sign up to access_"), we open everything (`robots: Allow: /`).

The embodiment of _Code is Law_ and _sovereign auditability_.
