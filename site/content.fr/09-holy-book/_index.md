---
title: "Chapitre 09 — Holy Book"
description: "Documentation publique d'Ocarina. VitePress, FR + EN + RU, PDF générés par IA, plus de 40 skills exposés aux LLMs. URL : <https://mojo-molotov.github.io/ocarina-holy-book/>"
weight: 10
date: 2026-05-20
tags: ["holy-book"]
sidebar:
  open: true
---

# Chapitre 09&nbsp;—&nbsp;Holy Book

> Documentation publique d'Ocarina. VitePress, FR + EN + RU, PDF générés par IA, plus de 40 _skills_ exposés aux LLMs. URL&nbsp;: <https://mojo-molotov.github.io/ocarina-holy-book/>

## Plan

|  #  | Fichier                                            | Sujet                                                                 |
| :-: | -------------------------------------------------- | --------------------------------------------------------------------- |
| 01  | [`01-stack-vitepress.md`](01-stack-vitepress.md)   | VitePress 2 alpha + theme @sugarat + plugins maison + pagefind.       |
| 02  | [`02-i18n.md`](02-i18n.md)                         | I18n FR/EN/RU&nbsp;: structure des pages, conventions.                |
| 03  | [`03-skills/`](03-skills/README.md)                | Les 40+ _skills_ exposées aux IA, classées en familles.               |
| 04  | [`04-claude-md.md`](04-claude-md.md)               | `CLAUDE.md` /&nbsp;`CLAUDE.slim.md` exposés sur le site.              |
| 05  | [`05-pdf-generation.md`](05-pdf-generation.md)     | Génération des PDF FR/EN/RU via `prompts/generate-books/`             |
| 06  | [`06-public-resources.md`](06-public-resources.md) | Tableau des URLs publiques (`llms.txt`, `llms-full.txt`, PDFs, etc.). |

## Objectifs

Le Holy Book **existe aussi bien pour les humains que pour les LLMs**&nbsp;:

- Génère `llms.txt` /&nbsp;`llms-full.txt` au build (standards pour exposer du contenu aux LLMs).
- Expose `CLAUDE.md` /&nbsp;`CLAUDE.slim.md`.
- Sert les PDFs FR/EN/RU.
- Documente 40+ _skills_ accessibles aux outils comme Claude Code.

C'est l'**incarnation pratique** du «&nbsp;_l'IA est le pont_&nbsp;» (cf. [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md)).

## Idéologie

> Pour autant, ce qu'il nous reste à présent, c'est le besoin d'un code de test **lisible, traçable et flexible**, sous sa forme la plus **brute**.
>
> Avec l'IA, et des outils comme _Claude Code_, ce pari devient chaque jour plus solide.

Le Holy Book est l'_outil_ qui rend ce pari opérationnel. Sans lui, un LLM aurait à _deviner_ comment Ocarina marche. Avec lui&nbsp;: il _consulte_ une doc qui lui est _explicitement destinée_.

## Pages

```
docs/fr/
├── index.md                                                      # Page d'accueil blog
├── what-is-it.md                                                 # Qu'est donc Ocarina ?
├── first-feedbacks.md                                            # Premiers retours
├── setup.md                                                      # Premiers pas
├── scenarios-composability.md                                    # Premiers scénarios
├── datasets-smoke-tests-setup-teardown-proxy-api-and-caching.md  # Premiers jutsus
├── handling-flakiness.md                                         # Premiers obstacles du monde réel
├── extensibility.md                                              # Extensibilité
└── using-ocarina-with-ai.md                                      # Utiliser Ocarina avec l'IA
```

Chaque page existe en EN aussi (`docs/`).  
Ainsi qu'en RU (`docs/ru`).

Conventions de _frontmatter_ VitePress&nbsp;:

```yaml
---
sticky: 1
# pagefind-indexed: false
description: ...
date: 2026-04-24
head:
  - - meta
    - property: og:image
      content: http://...
---
```

## Lectures connexes

- Quels concepts les pages de doc reprennent&nbsp;: [`../02-ocarina/`](../02-ocarina/README.md), [`../03-functional/`](../03-functional/README.md)
- La discipline IA documentée dans `using-ocarina-with-ai.md`&nbsp;: [`../08-ai-example/01-ai-manifesto.md`](../08-ai-example/01-ai-manifesto.md)
