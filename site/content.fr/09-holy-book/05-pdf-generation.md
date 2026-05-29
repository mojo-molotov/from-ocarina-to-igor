---
title: "09.05 — Génération de PDF (generate-books)"
description: "La génération des PDF publics du Holy Book : des livres FR, EN et RU produits par IA à partir du dossier docs, d'un script Python et d'un prompt."
weight: 5
date: 2026-05-20
series: ["holy-book"]
series_order: 5
---

# 09.05&nbsp;—&nbsp;Génération de PDF (`generate-books`)

> Les PDFs publics (`ocarina-ru.pdf`, `ocarina-en.pdf`, `ocarina-fr.pdf`...) sont **générés par IA** à partir du dossier `docs/`, d'un script Python et d'un prompt Markdown.

## Arborescence

```
prompts/generate-books/
├── prompt.md                     # spec (lu par l'IA)
├── script.py                     # implémentation Python
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

### 1. Un `prompt.md` + un `script.py`

`prompt.md`&nbsp;:

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

→ L'IA reçoit ces 4 inputs, suit le `prompt.md`, exécute le `script.py`. Output&nbsp;: N PDFs.

### 2. Les fonts Noto

Pourquoi Noto&nbsp;? Parce que Noto **couvre tout l'unicode**.  
Pas de glyphes ratés (boites vides).

Critique pour une doc qui mélange&nbsp;:

- Français + anglais + russe + arabe (plusieurs alphabets, _reshaper_ spécifique pour l'arabe).
- Russe (cyrillique&nbsp;: «&nbsp;Игорь Казанова&nbsp;»).
- Arabe («&nbsp;الجبر&nbsp;»).
- Symboles mathématiques.
- Émojis («&nbsp;🎶&nbsp;», «&nbsp;📖&nbsp;», «&nbsp;✈️&nbsp;»).

| Police                                      | Couvre                                               |
| ------------------------------------------- | ---------------------------------------------------- |
| `NotoSans-{Regular,Bold,Italic,BoldItalic}` | Latin + Cyrillique + diacritiques (le gros du texte) |
| `NotoSansMath-Regular`                      | Symboles mathématiques                               |
| `NotoSansMono-Regular`                      | Code (monospace)                                     |
| `NotoSansSymbols2-Regular`                  | Symboles divers (flèches, etc.)                      |
| `NotoNaskhArabic-Regular`                   | Arabe                                                |
| `NotoColorEmoji-Regular`                    | Emojis (rendu spécial via PNG raster)                |

→ 9 fichiers de fonts. Ensemble&nbsp;: couvre essentiellement tout l'unicode utilisé dans le Holy Book.

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

| Lib                               | Rôle                                                   |
| --------------------------------- | ------------------------------------------------------ |
| `reportlab`                       | Génère le PDF (layout, paragraphes, images)            |
| `pillow`                          | Manipule les images (resize, conversions de format)    |
| `pyyaml`                          | Parse les frontmatter VitePress                        |
| `pygments`                        | Highlight le code (couleur syntaxique)                 |
| `pikepdf`                         | Compresse le PDF en fin                                |
| `numpy`                           | Math utility pour le layout                            |
| `arabic-reshaper` + `python-bidi` | Rend l'arabe correctement (right-to-left + ligatures)  |
| `fonttools`                       | Lit les tables SVG des émojis                          |
| `cairosvg`                        | Convertit les SVG (extraction de l'emoji table) en PNG |

### 4. Rendering des émojis

`script.py`&nbsp;:

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

| Type                                              | Stratégie                                                                                 |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Text characters (juste du texte)                  | Vector glyph natif ReportLab                                                              |
| Color emoji ("vrai" émoji)                        | Extract SVG du font&nbsp;→&nbsp;rasterize via cairosvg →&nbsp;insert PNG dans le PDF |
| Supplementary plane symbols (rare mais important) | Fallback PNG, l'émoji avion est important pour dire aux slipologues de déguerpir          |

### 5. Output

```
pub/
├── ocarina-en.pdf
├── ocarina-fr.pdf
└── ocarina-ru.pdf
```

Le plugin `pub.ts` côté VitePress expose ensuite ces fichiers.

## Pourquoi l'IA pour générer

| Solution traditionnelle                                                                                                                             | Solution IA                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Pandoc + LaTeX template + heures de fine-tuning + documentation qui dérive sous forme d'autres fichiers (travail en double, parfois même en triple) | Un prompt + un script + IA, ingère directement le site VitePress basé sur des fichiers Markdown |
| Layouts statiques difficiles à customiser per-page                                                                                                  | L'IA adapte au cas par cas                                                                      |
| Maintenance coûteuse (chaque changement de doc casse le layout)                                                                                     | L'IA s'adapte                                                                                   |

## Cadence de génération

Pas automatique.  
L'auteur lance manuellement quand il veut rafraîchir les PDFs.  
Le choix de créer une nouvelle publication est manuel.

## «&nbsp;_Agentic environment_&nbsp;»

`prompt.md`&nbsp;:

> They are designed to be used together in an agentic environment.

→ Suppose un environnement où l'IA&nbsp;:

- Reçoit les fichiers.
- Lit le prompt.
- Exécute le script.
- Itère si erreur.
- Retourne les PDFs.

C'est typiquement Claude Code ou un workflow équivalent.

## Résultat

PDFs A4 avec&nbsp;:

- Couverture.
- Table des matières.
- Bonne mise en forme.
- Code highlighted (Pygments).
- Multi-langues.
- Emojis.
- Compressé (pikepdf) pour taille raisonnable.

URLs canoniques&nbsp;:

- https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf
- https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf
- https://mojo-molotov.github.io/ocarina-holy-book/ocarina-ru.pdf
