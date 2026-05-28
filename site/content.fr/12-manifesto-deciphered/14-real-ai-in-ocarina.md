---
title: "12.14 — L'IA, et comment Ocarina l'applique pour de vrai"
description: "Au-delà du slogan AI-powered : comment Ocarina conçoit une infrastructure logicielle où une IA peut contribuer comme un développeur senior."
weight: 14
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 14
tags: ["typage"]
---

# 12.14&nbsp;—&nbsp;L'IA, et comment Ocarina l'applique _pour de vrai_

> «&nbsp;_AI-powered_&nbsp;» est devenu en 2023-2026 un slogan marketing complètement débile&nbsp;:&nbsp;99&nbsp;% des produits qui le revendiquent enrichissent un produit existant avec un endpoint `chat.completions`. Ocarina propose, à l'opposé, une **infrastructure logicielle pensée pour qu'une IA puisse contribuer comme un développeur senior**. [`ocarina-with-ai-example`](https://github.com/mojo-molotov/ocarina-with-ai-example) étant la preuve par l'exemple.

## 1. Ce qu'est l'IA aujourd'hui

| Couche                                  | Exemple                                        | Date d'apparition                              |
| --------------------------------------- | ---------------------------------------------- | ---------------------------------------------- |
| **Statistical learning**                | Régression, k-means, decision trees            | 1960s-1990s                                    |
| **Deep learning**                       | CNN (vision), RNN/LSTM (texte)                 | 2012 (AlexNet&nbsp;—&nbsp;adoption mainstream) |
| **Transformer-based foundation models** | GPT, Claude, Gemini, Llama                     | 2017 (papier), 2018 (BERT), 2022 (ChatGPT)     |
| **Workflows agentiques**                | AutoGPT, LangChain, Claude Code, Cursor agents | 2023+                                          |

> _Note&nbsp;:&nbsp;le CNN est inventé par Yann LeCun dès 1989 (MNIST). AlexNet (Krizhevsky, Sutskever, Hinton, Toronto, 2012) en est la percée industrielle. LeCun, Hinton et Bengio partagent le Turing Award 2018 pour leurs contributions fondatrices au deep learning._

Quand le Holy Book d'Ocarina parle «&nbsp;_d'IA_&nbsp;», il parle **des couches 3 et 4**&nbsp;:&nbsp;LLM _transformer-based_ pré-entraînés, et boucles agentiques qui les invoquent.

### _Attention is All You Need_

| Champ        | Valeur                                                                               |
| ------------ | ------------------------------------------------------------------------------------ |
| Papier       | **«&nbsp;_Attention Is All You Need_&nbsp;»**                                        |
| Auteurs      | Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin                |
| Org          | **Google Brain, Google Research, University of Toronto**                             |
| Date         | **Juin 2017** (arXiv), présenté à **NeurIPS décembre 2017**                          |
| Contribution | Architecture **Transformer**&nbsp;:&nbsp;self-attention au lieu de récurrence (LSTM) |

L'architecture _Transformer_ permet de _paralléliser_ l'entraînement sur GPU. Ce qui prenait des semaines en LSTM se fait en heures. L'entraînement passe à l'échelle d'Internet. GPT-1 (2018)&nbsp;→&nbsp;GPT-2 (2019)&nbsp;→&nbsp;GPT-3 (2020, 175&nbsp;B params)&nbsp;→&nbsp;GPT-4 (2023)&nbsp;→&nbsp;Claude 3 (2024)&nbsp;→&nbsp;Claude 4 (2025).

### Acteurs

| Org                                                   | Modèles                    | Posture                                                             |
| ----------------------------------------------------- | -------------------------- | ------------------------------------------------------------------- |
| **OpenAI** (Sam Altman, San Francisco)                | GPT-4o, o1, GPT-5, GPT-5.5 | _Closed weights_, abonnement                                        |
| **Anthropic** (Dario & Daniela Amodei, San Francisco) | Claude 3, 3.5, 4           | _Closed weights_, focus sécurité et _alignment_ (Constitutional AI) |
| **Google DeepMind**                                   | Gemini 1.5, 2.0, 2.5       | _Closed weights_, intégration Google                                |
| **Meta AI**                                           | Llama 2, 3, 4              | _Open weights_ (presque open source)                                |
| **xAI** (Musk)                                        | Grok 1, 2, 3               | _Open weights_ partiel                                              |
| **Mistral AI** (Paris)                                | Mistral, Mixtral           | _Open weights_, européen                                            |

## 2. Capacités opérationnelles d'un LLM 2025-2026

Pour comprendre comment Ocarina les utilise, il faut **lister honnêtement** ce qu'un LLM moderne peut faire et ce qu'il ne peut pas faire.

### Ce qu'un LLM fait bien

| Capacité                                                    | Niveau |
| ----------------------------------------------------------- | ------ |
| Reformulation, traduction                                   | ★★★★★  |
| Génération de code _local_ (un fichier, une fonction)       | ★★★★★  |
| Compréhension de docs si elles tiennent en contexte         | ★★★★★  |
| Détection de patterns dans du code                          | ★★★★   |
| Génération de tests _à partir_ d'un code documenté          | ★★★★   |
| Refactor mécanique (renommer, extraire)                     | ★★★★   |
| Suivi d'une convention si elle est documentée explicitement | ★★★★   |
| Application d'une grammaire fixe (DSL borné, typé)          | ★★★★★  |

### Ce qu'un LLM fait mal, et comment Ocarina y répond

| Limite                                    | Conséquence                                                                          | Réponse Ocarina                                                                 |
| ----------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Hallucinations**                        | Invente des fonctions /&nbsp;classes inexistantes                                    | _Mypy strict_                                                                   |
| **Dégradation sur long contexte**         | Perd en précision sur les parties centrales d'un long fichier (_lost in the middle_) | Modules courts, _SKILL.md_ découpés                                             |
| **Pas de feedback runtime sans tooling**  | Si rien ne lui dit que ça a planté, le LLM continue                                  | _Probes_ Ocarina (cf. [`15-typing-ai-rl-probes.md`](15-typing-ai-rl-probes.md)) |
| **Préfère les patterns populaires**       | Va vers pytest, async/await, mock                                                    | Documentation explicite des _refus_ Ocarina                                     |
| **Ne comble pas un domaine mal spécifié** | Insatisfaisant avec des technologies mal définies                                    | Bien défini, conventions algébriques, ISTQB-first                               |
| **Pas de mémoire entre sessions**         | Perd les conventions du projet                                                       | `CLAUDE.md`, _skills_                                                           |
| **Pas d'intuition sur les invariants**    | Génère du code qui passe les tests mais ne respecte pas l'esprit                     | _ROP_ structurel qui force la grammaire                                         |

## 3. Ce que veut dire «&nbsp;_IA-first_&nbsp;» opérationnellement

| Niveau                                | Caractéristiques                                          | Exemple                                         |
| ------------------------------------- | --------------------------------------------------------- | ----------------------------------------------- |
| **0&nbsp;—&nbsp;Slogan**              | «&nbsp;_Powered by AI_&nbsp;» sans surface réelle         | Majorité du SaaS 2024                           |
| **1&nbsp;—&nbsp;Chatbot externe**     | Endpoint OpenAI dans un wrapper d'UI                      | Majorité du _AI-enhanced_                       |
| **2&nbsp;—&nbsp;RAG sur la doc**      | Récupère des passages, les colle dans la réponse          | Algolia DocSearch + plugin OpenAI, Mintlify     |
| **3&nbsp;—&nbsp;Interface AI native** | Le produit est _conçu_ pour qu'un agent agisse dessus     | **MCP servers, llms.txt, AI SDK, Cursor rules** |
| **4&nbsp;—&nbsp;Co-conception**       | Le produit crée des livrables _co-écrits_ par un agent IA | **Ocarina + `ocarina-with-ai-example`**         |

Ocarina est l'un des très rares projets à atteindre le **niveau 4** publiquement et avec preuves auditables.

## 4. Les artefacts AI-first dans Ocarina

### `llms.txt`, `llms-full.txt`

Standard de facto proposé par [`llmstxt.org`](https://llmstxt.org) (Jeremy Howard, fast.ai), 2024.

- `llms.txt`&nbsp;:&nbsp;un index Markdown court, conçu pour qu'un agent y trouve _quoi lire_.
- `llms-full.txt`&nbsp;:&nbsp;la _doc complète concaténée_, conçue pour un seul prompt qui ingère tout.

Ocarina expose les deux. Voir [`09-holy-book/06-public-resources.md`](../09-holy-book/06-public-resources.md)

### `CLAUDE.md` /&nbsp;`CLAUDE.slim.md`

Convention **Anthropic**&nbsp;:&nbsp;`CLAUDE.md` à la racine du projet, lu automatiquement par Claude Code (et compatibles)&nbsp;:

- L'identité du projet, sa philosophie.
- Les conventions à respecter.
- Les commandes principales.
- Les pièges connus.

Ocarina maintient&nbsp;:

- `CLAUDE.md` long (gros contexte) pour _onboarding_ approfondi.
- `CLAUDE.slim.md` court (économie de tokens) pour interactions de routine.

### Skills (`SKILL.md`)

40+ skills exposés par le Holy Book. Un skill&nbsp;=&nbsp;un fichier `SKILL.md`&nbsp;:

- Métadonnées YAML (`name`, `description`).
- Procédure pas-à-pas.
- Conditions d'invocation («&nbsp;_quand l'utilisateur demande X, fais Y_&nbsp;»).

Permet à Claude Code, Cursor, etc. de se **plugger**. Voir [`09-holy-book/03-skills/`](../09-holy-book/03-skills/README.md)

### `ocarina-with-ai-example`

Projet e2e entier, écrit pour tester une vraie app (CURA), **co-écrit par Claude**. Le `CLAUDE.md` du dépôt documente les _hard-won rules_ apprises pendant la co-écriture.

Cette suite est une **preuve par l'exemple** que l'approche _AI-first_ d'Ocarina n'est pas une invention&nbsp;:&nbsp;elle a été testée, contre un SUT, en collaboration documentée avec un LLM. Voir [`08-ai-example/`](../08-ai-example/README.md)

## 5. «&nbsp;_AI-marketing_&nbsp;» vs «&nbsp;_AI-pour-de-vrai_&nbsp;»

| Critère                     | AI-marketing                          | AI-pour-de-vrai (Ocarina)                                     |
| --------------------------- | ------------------------------------- | ------------------------------------------------------------- |
| Surface AI documentée       | «&nbsp;_Powered by GPT-4_&nbsp;»      | `llms.txt`, `llms-full.txt`, `CLAUDE.md`, 40+ skills          |
| Preuve d'usage IA           | Aucune ou bancale                     | `ocarina-with-ai-example`                                     |
| Format de doc               | PDF /&nbsp;SaaS dashboard uniquement  | Markdown brut                                                 |
| Compatibilité agent         | Inexistante                           | Conçu pour Claude Code, Cursor, Continue, Cline               |
| Convention de grammaire     | Ad-hoc                                | ROP + ISTQB strict, typage statique                           |
| Gestion du contexte LLM     | Négligé (gros fichiers monolithiques) | Modularisation jusqu'au bout                                  |
| Réaction aux hallucinations | Aucune                                | Technologie bien définie, erreurs de types, strict au maximum |
| Reproductibilité            | Non-déterministe par construction     | _Probes_ + caching                                            |

## 6. Pourquoi cette préparation _avantage Ocarina pour les 5 prochaines années_

1. La barrière à l'entrée du test e2e va **s'effondrer** parce qu'un LLM peut écrire la majorité du _boilerplate_.
2. **Seuls** les frameworks compatibles LLM resteront pertinents, les autres deviendront _legacy_.
3. La compatibilité LLM dépend de **trois choses**&nbsp;:
   - Un **petit** DSL bien défini (tient en contexte).
   - Une **grammaire formelle** (mypy /&nbsp;ROP /&nbsp;ISTQB).
   - Une **documentation structurée** (Markdown + skills).
4. Ocarina coche toutes les cases.
5. Pytest, Cypress, Playwright, Robot Framework ne les cochent pas. Leur surface est trop grande (centaines de plugins), leur grammaire trop floue (async, fixtures), leur documentation trop fragmentée (sites SaaS, vidéos, plugins dispersés).

Ocarina parie que **l'IA va dévorer** les frameworks à _grande surface_, exactement comme Tugan Bara a été dégagé par l'IA dans le copywriting (cf. [`10-infopreneurs-tugan-bara-ai.md`](10-infopreneurs-tugan-bara-ai.md)).

## 7. Comment l'IA travaille _vraiment_ sur Ocarina

```
1. Claude lit /CLAUDE.md (conventions projet).
2. Claude lit /docs/fr/what-is-it.md (philosophie).
3. Claude lit /SKILL_<feature>.md (skill correspondant).
4. Claude lit /tests/scenarios/<famille>/*.py (échantillon).
5. Claude écrit un nouveau fichier `.py`.
6. Mypy strict tourne automatiquement.
7. Si mypy fail → Claude lit le diagnostic, corrige, relance.
8. Si mypy passe → Claude lance le test contre le SUT.
9. Si test fail → Claude lit la sortie, ajuste les probes, relit.
10. Si test passe → Claude commit, push, ouvre PR.
```

Les étapes 2, 3, 4, 6, 9 sont **contraintes par l'infrastructure d'Ocarina**.  
Sans `CLAUDE.md`, l'étape 1 est aléatoire. Sans mypy strict, l'étape 6 n'existe pas.  
Sans `transient_errors`, `match_page` et les `watcher`, l'étape 9 produit des _flaky tests_.

C'est ce qui fait dire qu'Ocarina est **conçu pour l'IA**, pas _branché à l'IA_.

## 8. Lectures connexes

- [`13-lambda-calculus-rop-origins.md`](13-lambda-calculus-rop-origins.md)&nbsp;—&nbsp;la base théorique du DSL d'Ocarina, qui le rend _LLM-compatible_.
- [`15-typing-ai-rl-probes.md`](15-typing-ai-rl-probes.md)&nbsp;—&nbsp;pourquoi typage + RL + probes sont la triade qui rend l'IA productive.
- [`../08-ai-example/`](../08-ai-example/README.md)&nbsp;—&nbsp;la preuve par l'exemple&nbsp;: la suite IA.
- [`../09-holy-book/03-skills/`](../09-holy-book/03-skills/README.md)&nbsp;—&nbsp;les skills exposées.
