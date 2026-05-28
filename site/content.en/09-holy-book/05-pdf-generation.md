---
title: "09.05 — PDF generation (generate-books)"
description: "The Holy Book's public PDF generation: FR, EN and RU books produced by AI from the docs folder, a Python script and a prompt."
weight: 5
date: 2026-05-20
series: ["holy-book"]
series_order: 5
---

# 09.05&nbsp;—&nbsp;PDF generation (`generate-books`)

> The public PDFs (`ocarina-ru.pdf`, `ocarina-en.pdf`, `ocarina-fr.pdf`...) are **AI-generated** from the `docs/` folder, a Python script, and a Markdown prompt.

## Tree

```
prompts/generate-books/
├── prompt.md                     # spec (read by the AI)
├── script.py                     # Python implementation
├── NotoSans-Regular.ttf
├── NotoSans-Bold.ttf
├── NotoSans-Italic.ttf
├── NotoSans-BoldItalic.ttf
├── NotoSansMath-Regular.ttf
├── NotoSansMono-Regular.ttf
├── NotoSansSymbols2-Regular.ttf
├── NotoNaskhArabic-Regular.ttf
└── NotoColorEmoji-Regular.ttf
```

### 1. A `prompt.md` + a `script.py`

`prompt.md`:

> # Ocarina PDF Generator
>
> ## What this is
>
> A system that turns a VitePress `docs/` folder (Markdown + images) into three polished A4 PDFs&nbsp;—&nbsp;one Russian, one English, one French. The system is two files: this prompt (the spec) and `script.py` (the implementation). They are designed to be used together in an agentic environment.
>
> ## How to run it
>
> ### Inputs you receive
>
> 1. **`docs.zip`**&nbsp;—&nbsp;a ZIP archive containing a VitePress `docs/` folder with `.md` files and images.
> 2. **Font files**&nbsp;—&nbsp;a set of Noto `.ttf` files. They are provided as a convenience to avoid download issues; they are ordinary fonts, nothing special.
> 3. **`prompt.md`**&nbsp;—&nbsp;this file.
> 4. **`script.py`**&nbsp;—&nbsp;the Python script.

The AI receives these 4 inputs, follows `prompt.md`, runs `script.py`. Output: N PDFs.

### 2. The Noto fonts

Why Noto? Because Noto **covers all of unicode**&nbsp;—&nbsp;no missed glyphs, no empty boxes.

Critical for a doc that mixes:

- French + English + Russian + Arabic (multiple alphabets, specific Arabic _reshaper_).
- Russian (Cyrillic: "Игорь Казанова").
- Arabic ("الجبر").
- Mathematical symbols.
- Emojis ("🎶", "📖", "✈️").

| Font                                        | Covers                                               |
| ------------------------------------------- | ---------------------------------------------------- |
| `NotoSans-{Regular,Bold,Italic,BoldItalic}` | Latin + Cyrillic + diacritics (the bulk of the text) |
| `NotoSansMath-Regular`                      | Mathematical symbols                                 |
| `NotoSansMono-Regular`                      | Code (monospace)                                     |
| `NotoSansSymbols2-Regular`                  | Misc symbols (arrows, etc.)                          |
| `NotoNaskhArabic-Regular`                   | Arabic                                               |
| `NotoColorEmoji-Regular`                    | Emojis (special render via PNG raster)               |

9 font files. Together they cover essentially all unicode used in the Holy Book.

### 3. `script.py`

```python
#!/usr/bin/env python3
"""
Ocarina PDF Generator
=====================

Generates one compressed A4 PDF per locale from a VitePress docs/ folder.

Usage:
    1. Set DOCS_DIR and FONTS_DIR below to match your environment.
    2. pip install reportlab pillow pyyaml pygments pikepdf numpy \\
                  arabic-reshaper python-bidi fonttools cairosvg
    3. python3 script.py

Inputs:  docs/ folder with .md files + images, Noto font files
Outputs: ocarina-en.pdf, ocarina-fr.pdf in OUTPUT_DIR
"""
```

| Lib                               | Role                                                  |
| --------------------------------- | ----------------------------------------------------- |
| `reportlab`                       | Generates the PDF (layout, paragraphs, images)        |
| `pillow`                          | Manipulates images (resize, format conversions)       |
| `pyyaml`                          | Parses VitePress frontmatter                          |
| `pygments`                        | Highlights code (syntax coloring)                     |
| `pikepdf`                         | Compresses the PDF at the end                         |
| `numpy`                           | Math utility for layout                               |
| `arabic-reshaper` + `python-bidi` | Renders Arabic correctly (right-to-left + ligatures)  |
| `fonttools`                       | Reads the emoji SVG tables                            |
| `cairosvg`                        | Converts SVGs (extracted from the emoji table) to PNG |

### 4. Emoji rendering

`script.py`:

```python
"""
Character rendering philosophy:
    - Text characters (covered by NotoSans/NotoMath/NotoSymbols2) are always
      rendered as vector glyphs via drawString or <font> tags. Never as PNGs.
    - Color emoji (NotoColorEmoji) are rasterized to PNG via fontTools SVG
      table extraction + cairosvg. Pillow cannot render this font.
    - Outline PNG rasterization is a last resort for supplementary-plane
      symbols (cp >= U+10000) where ReportLab has a glyph-index encoding bug.
"""
```

| Type                                             | Strategy                                                                                      |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Text characters (plain text)                     | Native ReportLab vector glyph                                                                 |
| Color emoji ("real" emoji)                       | Extract SVG from font → rasterize via cairosvg → insert PNG into the PDF                      |
| Supplementary plane symbols (rare but important) | PNG fallback&nbsp;—&nbsp;the airplane emoji is important for telling slipologues to clear off |

### 5. Output

```
pub/
├── ocarina-en.pdf
├── ocarina-fr.pdf
└── ocarina-ru.pdf
```

The `pub.ts` plugin on the VitePress side then exposes these files.

## Why AI for generation

| Traditional solution                                                                                                     | AI solution                                                                 |
| ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| Pandoc + LaTeX template + hours of fine-tuning + documentation drifting into other files (double work, sometimes triple) | A prompt + a script + AI, ingests the VitePress site directly from Markdown |
| Static layouts hard to customize per-page                                                                                | The AI adapts case by case                                                  |
| Costly maintenance (every doc change breaks the layout)                                                                  | The AI adapts                                                               |

## Generation cadence

Not automatic. The author launches it manually to refresh the PDFs. Releasing a new version is a deliberate choice.

## "_Agentic environment_"

`prompt.md`:

> They are designed to be used together in an agentic environment.

The AI receives the files, reads the prompt, runs the script, iterates on errors, and returns the PDFs. Typically Claude Code or equivalent.

## Result

A4 PDFs with:

- Cover.
- Table of contents.
- Good typography.
- Highlighted code (Pygments).
- Multi-language.
- Emojis.
- Compressed (pikepdf) for reasonable size.

Canonical URLs:

- https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf
- https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf
- https://mojo-molotov.github.io/ocarina-holy-book/ocarina-ru.pdf
