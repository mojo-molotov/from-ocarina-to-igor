---
title: "09.06 — Ressources publiques"
description: "Le tableau complet des URLs publiques exposées par le Holy Book, pour les humains, les LLMs et les scrapers."
weight: 6
date: 2026-05-20
series: ["holy-book"]
series_order: 6
---

# 09.06&nbsp;—&nbsp;Ressources publiques

> Tableau complet des URLs publiques exposées par le Holy Book. Pour les humains, les LLMs, les scrapers.

## Listing (potentiellement non exhaustif)

| URL                                                                   | Contenu                                         | Public cible             |
| --------------------------------------------------------------------- | ----------------------------------------------- | ------------------------ |
| `https://mojo-molotov.github.io/ocarina-holy-book/`                   | Page d'accueil (EN)                             | Humain                   |
| `https://mojo-molotov.github.io/ocarina-holy-book/fr/`                | Page d'accueil (FR)                             | Humain                   |
| `https://mojo-molotov.github.io/ocarina-holy-book/ru/`                | Page d'accueil (RU)                             | Humain                   |
| `https://mojo-molotov.github.io/ocarina-holy-book/what-is-it`         | Article (EN)                                    | Humain                   |
| `https://mojo-molotov.github.io/ocarina-holy-book/fr/what-is-it`      | Article (FR)                                    | Humain                   |
| `https://mojo-molotov.github.io/ocarina-holy-book/ru/what-is-it`      | Article (RU)                                    | Humain                   |
| ... (autres pages doc en EN+FR+RU)                                    | ...                                             | Humain                   |
| `https://mojo-molotov.github.io/ocarina-holy-book/llms.txt`           | Index minimaliste pour LLMs                     | LLM                      |
| `https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt`      | Tout le contenu en plaintext                    | LLM, scraper             |
| `https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md`          | Règles projet complètes                         | LLM, humain (onboarding) |
| `https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md`     | Règles projet courtes                           | LLM (context budget)     |
| `https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf`     | Doc en PDF A4 (EN)                              | Humain (offline)         |
| `https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf`     | Doc en PDF A4 (FR)                              | Humain (offline)         |
| `https://mojo-molotov.github.io/ocarina-holy-book/ocarina-ru.pdf`     | Doc en PDF A4 (RU)                              | Humain (offline)         |
| `https://mojo-molotov.github.io/ocarina-holy-book/skills/<name>`      | Page d'un skill IA                              | Humain, LLM              |
| `https://mojo-molotov.github.io/ocarina-holy-book/assets/content/...` | Images, sons (covers d'articles, illustrations) | Humain (rendu inline)    |

## `llms.txt` (standard émergent)

Spec&nbsp;: <https://llmstxt.org/> (proposé en 2024).

Format type&nbsp;:

```
# The Ocarina Holy Book

> Ocarina is Igor's automated web browser testing framework.

## Pages

- [Qu'est donc Ocarina ?](https://mojo-molotov.github.io/ocarina-holy-book/fr/what-is-it) — Les frameworks de test ont tous fait le même mauvais pari. Ocarina fait le contraire.
- [Premiers retours](https://mojo-molotov.github.io/ocarina-holy-book/fr/first-feedbacks) — La première des critiques ayant été faite à Ocarina.
- [Premiers pas](https://mojo-molotov.github.io/ocarina-holy-book/fr/setup) — Tutoriel d'onboarding.
- ... (toutes les pages)

## Resources

- [llms-full.txt](https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt) — Tout le contenu plaintext.
- [CLAUDE.md](https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md) — Règles pour IA.
- ... etc
```

Un LLM qui visite le site peut **lire `llms.txt` en premier** et savoir tout ce qui existe.

## `llms-full.txt`

Le contenu **plain text** de toutes les pages, concaténé. Permet à un LLM (Claude, ChatGPT, etc.) de récupérer la doc en **un seul fetch HTTP** plutôt que N fetchs.

Volume typique&nbsp;: ~500 KB de plain text (pour ~5&nbsp;000 lignes Markdown).

## `robots.txt`

```
# docs/public/robots.txt
User-agent: *
Allow: /
```

→ Tout est crawlable. Aucune restriction sur les bots /&nbsp;LLMs.

«&nbsp;_Si tu veux savoir, lis, RTFM_&nbsp;». Pas de captcha, pas de paywall.

## `.nojekyll`

```
# docs/public/.nojekyll
```

(Fichier vide.)

GitHub Pages utilise Jekyll par défaut. Jekyll provoquait une conversion indésirable sous forme de fichiers HTML qui rendait les _skills_ inutilisables. Désactivation de cette merde.

## `.spa`

```
# docs/public/.spa
```

Artefact VitePress sans intérêt particulier, détail d'implémentation.

## `favicon.ico` et `logo.png`

Standards. Le `favicon.ico` apparaît dans l'onglet du browser.  
Le `logo.png` est utilisé dans la bannière, en haut à gauche (`@sugarat/theme`).

## Flot LLM

```
1. GET /llms.txt                              → liste des ressources
2. (option A) GET /llms-full.txt              → tout en un seul fetch
   (option B) GET /CLAUDE.md                  → règles compactes
   (option C) GET /<page>                     → page spécifique
3. Si question sur la mécanique interne :     → fetch le code source d'Ocarina sur GitHub
4. Si question sur l'usage :                  → fetch ocarina-example
5. Si question sur l'usage IA :               → fetch ocarina-with-ai-example
```

## Rappel du Holy Book

Le Holy Book (chapitre «&nbsp;_Utiliser Ocarina avec l'IA_&nbsp;») liste les URLs en clair, en bas de page&nbsp;:

> ## Ressources exposées
>
> - https://mojo-molotov.github.io/ocarina-holy-book/llms.txt
> - https://mojo-molotov.github.io/ocarina-holy-book/llms-full.txt
> - https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.md
> - https://mojo-molotov.github.io/ocarina-holy-book/CLAUDE.slim.md
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-ru.pdf
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-en.pdf
> - https://mojo-molotov.github.io/ocarina-holy-book/ocarina-fr.pdf

→ C'est une **invitation publique** aux LLMs. «&nbsp;_Voici ce qu'on expose pour vous, servez-vous._&nbsp;»

## Cohérence avec la posture politique

Cf. [`../11-independence/`](../11-independence/README.md)

L'auteur _veut_ que l'IA consomme la doc.  
C'est un choix politique&nbsp;:

- Au lieu de **résister** à l'indexation par les LLMs (paywall, captcha, DRM), on **invite**.
- Au lieu d'**obscurcir** les règles projet («&nbsp;_on ne donne pas notre CLAUDE.md_&nbsp;»), on **publie**.
- Au lieu de **monopoliser** la doc («&nbsp;_inscris-toi pour y avoir accès_&nbsp;»), on **ouvre tout** (`robots: Allow: /`).

C'est l'incarnation de _Code is Law_ et de l'_auditabilité souveraine_.
