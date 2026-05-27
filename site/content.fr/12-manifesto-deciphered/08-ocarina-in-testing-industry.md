---
title: "12.08 — Ocarina dans l'industrie du test"
description: "Ocarina n'est pas un meilleur pytest, pas un meilleur Robot Framework, pas un meilleur Cypress. Il est structurellement ailleurs. Ce chapitre essaie d'expliquer le shift qu'il représente, et la longueur d'avance qu'il prend."
weight: 8
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 8
tags: ["istqb", "typage"]
---

# 12.08&nbsp;—&nbsp;Ocarina dans l'industrie du test

> Ocarina n'est pas un _meilleur_ pytest, pas un _meilleur_ Robot Framework, pas un _meilleur_ Cypress. Il est **structurellement ailleurs**. Ce chapitre essaie d'expliquer le _shift_ qu'il représente, et la longueur d'avance qu'il prend.

## 1. La cartographie actuelle de l'industrie

### Trois grandes familles d'outils e2e

| Famille               | Exemples                                                | Modèle                                                  |
| --------------------- | ------------------------------------------------------- | ------------------------------------------------------- |
| **DSL textuels**      | Robot Framework, Cucumber&nbsp;+&nbsp;Gherkin           | Couche de traduction permanente entre _texte_ et _code_ |
| **Plugins de runner** | pytest-selenium, pytest-playwright, pytest-bdd          | Greffés sur pytest, héritent de son lifecycle           |
| **Vendor SaaS**       | BrowserStack, Sauce Labs, LambdaTest, Cypress Dashboard | Test runner local&nbsp;+&nbsp;cloud d'exécution payant  |

### Trois grandes _surfaces de friction_ communes

| Friction                            | Manifestation                                                                                    |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Marketing&nbsp;>&nbsp;Technique** | Outils vendus sur démos, conferences et certifications _orientées_. La _hype_ pilote l'adoption. |
| **Vendor lock-in**                  | Une fois adopté, refactor coûteux, _prise d'otage_.                                              |
| **Effort cognitif déplacé**         | Comprendre l'outil prend plus de temps que de faire son travail.                                 |

## 2. Le pari technique d'Ocarina

1. **Pas de DSL textuel**&nbsp;→&nbsp;Python pur, _embedded DSL_.
2. **Pas de plugin pytest**&nbsp;→&nbsp;runner intégré, fidélité ISTQB absolue.
3. **Pas d'`async`/`await`**&nbsp;→&nbsp;simplicité, compatibilité Selenium synchrone, pas de «&nbsp;_trucs de geeks_&nbsp;».
4. **Pas de SaaS**&nbsp;→&nbsp;tout en local, noyau dur très dense, _boîte blanche_.

Voir aussi&nbsp;:&nbsp;[`../11-independence/03-explicit-refusals.md`](../11-independence/03-explicit-refusals.md)

Ces refus ne sont pas sans raison.  
Chacun est **justifié** par un compromis explicite.  
Enfin, leur **conjonction** produit une solution sans équivalent direct sur le marché.

## 3. Le _shift_ qu'Ocarina représente

### Premier axe&nbsp;:&nbsp;revenir au _vocabulaire_ du test (ISTQB)

L'industrie e2e moderne a un vocabulaire _mélangé_&nbsp;:&nbsp;«&nbsp;_fixture pytest_&nbsp;», «&nbsp;_step def Gherkin_&nbsp;», etc. Aucun acteur métier (testeur fonctionnel certifié ISTQB) n'a ce vocabulaire en tête.

| ISTQB         | Ocarina        |
| ------------- | -------------- |
| Pas de test   | `act`          |
| Cas de test   | `Test`         |
| Suite de test | `TestSuite`    |
| Campagne      | `TestCampaign` |
| Cycle         | `TestCycle`    |

C'est un _shift_&nbsp;:&nbsp;le code _devient lisible_ par un testeur fonctionnel.  
Pas seulement par un développeur Python.

### Deuxième axe&nbsp;: faire du _typage strict_ une discipline métier

Aucun framework e2e populaire n'a `mypy strict = true` comme prérequis.  
Ocarina, si.

- Les erreurs sont attrapées **avant l'exécution**.
- Le DSL est **renforcé par le compilateur** (mélanger des POMs hétérogènes dans un `drive_page` est une erreur _mypy_, pas une erreur runtime).
- La maintenance est extrêmement guidée (le _type checker_ revérifie la cohérence après chaque changement).

C'est un _shift_&nbsp;:&nbsp;on _déplace l'effort_ du _moment où ça pète_ vers le _moment où on l'écrit_.

### Troisième axe&nbsp;: faire de l'IA un client de première classe

Ocarina expose _activement_ vers les LLMs&nbsp;:

- `llms.txt`, `llms-full.txt`.
- `CLAUDE.md`, `CLAUDE.slim.md`.
- 40+ skills versionnés (`SKILL.md`).
- Une suite e2e entière co-écrite par Claude (`ocarina-with-ai-example`).

Aucun framework de test concurrent n'a cette _surface IA_.  
C'est un _shift_&nbsp;:&nbsp;on _conçoit le DSL pour être consommable par l'IA et l'humain_, pas juste par l'humain.

### Quatrième axe&nbsp;: faire de la _souveraineté grammaticale_ une promesse

Ocarina ne fournit pas un DSL fixe. Il fournit&nbsp;:

- `ChainRunner[T]` comme point d'extension.
- Pattern «&nbsp;_adapter projet_&nbsp;» comme convention.
- Composition par closures plutôt qu'héritage.

→ Chaque projet écrit **son propre framework au-dessus du framework** (`act`, `match_page`, `TestSuite` adapter, `TestCampaign` adapter, `EnvGetters`).

C'est un _shift_&nbsp;:&nbsp;on _rend la grammaire_ au projet, plutôt que d'entièrement la confier à l'outil.

## 4. Longueur d'avance

### Sur quoi Ocarina est en avance

| Axe                                  | Avance estimée vs l'industrie                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------------ |
| **Typage strict en e2e**             | 5-10 ans (la plupart des frameworks restent en `Any` partout)                                    |
| **IA-first**                         | 2-5 ans (les autres commencent à exposer des MCP/AI hooks, bien qu'avec une approche discutable) |
| **DSL embedded vs textuel**          | Permanent (différence philosophique, pas de rattrapage prévu)                                    |
| **Vocabulaire ISTQB**                | Permanent (différence philosophique)                                                             |
| **Auditabilité (1 dep d'exécution)** | Permanent (différence philosophique)                                                             |
| **ROP comme cœur**                   | 5-10 ans (la plupart utilisent des exceptions classiques)                                        |

### Sur quoi Ocarina n'est pas en avance

| Axe                       | Réalité                                                                                                                                                        |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Notoriété**             | Inexistant grand public. Audience cible&nbsp;: testeurs avancés.                                                                                               |
| **Écosystème de plugins** | Délibérément minimaliste. L'écosystème Python est l'un des plus énormes de l'industrie et peut être directement embarqué dans un projet Ocarina sans friction. |
| **Cloud-as-a-service**    | Aucun (volontaire). En revanche, Ocarina est nativement pensé pour le _scaling horizontal_.                                                                    |
| **Multi-langage**         | Python uniquement (volontaire).                                                                                                                                |

### Vision

Ocarina **part des hypothèses suivantes**&nbsp;:

1. **Le marché va se déplacer** vers _moins de plateformes_, _plus de code propre_, _plus de développement interne_. L'évolution Sanity&nbsp;→&nbsp;Markdown (Lee Robinson, Cursor, décembre 2025, confirmé par Sanity eux-mêmes dans leur réponse publique) en est un signal.
2. **L'IA va remplacer les frameworks à courbe d'apprentissage longue**. Pourquoi apprendre _Robot Framework_ si Claude peut écrire un test Python en 5 secondes&nbsp;? C'est ce que l'auteur appelle une [_presse Juicero_](https://www.ouest-france.fr/leditiondusoir/2017-09-06/juicero-la-machine-a-jus-de-fruits-qui-ne-sert-a-rien-f38d8076-6c38-4d7b-a57a-947e5e247dda)
3. **Les testeurs fonctionnels seront _revalorisés_** parce qu'ils porteront la _vision métier_, pendant que l'IA portera la _technique_.

Si ces trois hypothèses se vérifient (et il y a des signaux qu'elles vont se vérifier), Ocarina est exactement à la bonne place.

Si elles ne se vérifient pas, Ocarina restera un projet de niche, mais l'auteur l'accepte explicitement («&nbsp;_C'est ma voiture_&nbsp;»).

## 5. Le marché&nbsp;—&nbsp;analyse honnête

### Court terme (2026-2028)

- Ocarina restera **niche**. Pas de tooling enterprise, pas de SLA, pas de support payant.
- Adoption par **les consultants** qui veulent un outil _portable_ («&nbsp;_Ocarina dans sa poche_&nbsp;»).
- Adoption par **les testeurs fonctionnels** qui veulent délivrer plutôt que de perdre leur temps avec des «&nbsp;_trucs de geeks_&nbsp;» interminables.
- Adoption par **les solo dev&nbsp;/&nbsp;agences boutique** qui écrivent leurs propres tests.
- Adoption par **les équipes paranoïaques sécurité** qui ne peuvent pas recourir à un SaaS.

### Moyen terme (2028-2032)

Trois scénarios&nbsp;:

#### Scénario A&nbsp;—&nbsp;Ocarina reste niche

- 500-2000 utilisateurs.
- Communauté petite mais soudée.
- Pas d'influence sur le marché.
- L'auteur s'en fout complètement. L'aventure continue. Le code reste auditable.

#### Scénario B&nbsp;—&nbsp;Ocarina influence sans être adopté

- Plus probable. Les **idées** d'Ocarina (typage strict en e2e, vocabulaire ISTQB, IA-first) se diffusent et sont reprises par des frameworks plus populaires.
- Ocarina n'est pas adopté massivement, mais devient la _référence intellectuelle_ qu'on cite.
- Comme Hindley-Milner pour les langages de programmation&nbsp;:&nbsp;peu de gens l'écrivent en pratique, mais tous les langages modernes en sont héritiers.

#### Scénario C&nbsp;—&nbsp;Ocarina est adopté largement

- Moins probable. Exige un événement déclencheur.
- Si ça arrive&nbsp;: Ocarina aura attendu son moment.

### Long terme (2032+)

Ocarina est conçu pour _survivre à son auteur_.  
Le code est petit, audité, MIT. Il peut être forké, repris, maintenu par d'autres.

## 6. Comparaison qualitative avec quelques alternatives

| Aspect                           | Ocarina                                                                                                                                  | Robot Framework                     | Playwright                                          | Cypress                  | Selenium IDE                  |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | --------------------------------------------------- | ------------------------ | ----------------------------- |
| DSL textuel                      | ❌&nbsp;Python pur                                                                                                                       | ✅&nbsp;.robot files                | ❌&nbsp;TS pur                                      | ❌&nbsp;JS pur           | ✅&nbsp;Steps file            |
| Plugin runner                    | ❌&nbsp;Runner interne                                                                                                                   | ❌&nbsp;Runner interne              | ✅&nbsp;Jest/Mocha                                  | ❌&nbsp;Runner interne   | (UI)                          |
| Typage strict (mypy/strict)      | ✅&nbsp;ALL                                                                                                                              | ❌&nbsp;(Typage Python encore rare) | ⚠️&nbsp;Support TS mais POMs souvent typés en `any` | ⚠️&nbsp;JSDoc&nbsp;rare  | ❌                            |
| ROP                              | ✅&nbsp;Central                                                                                                                          | ❌&nbsp;Exceptions                  | ❌&nbsp;Exceptions                                  | ❌&nbsp;Exceptions       | ❌                            |
| IA-first                         | ✅&nbsp;documenté, technologie pensée pour depuis le départ                                                                              | ❌                                  | ⚠️&nbsp;Playwright CodeGen                          | ⚠️&nbsp;AI tooling tiers | ❌                            |
| Vocabulaire ISTQB                | ✅&nbsp;strict                                                                                                                           | ⚠️&nbsp;partiel                     | ❌&nbsp;Jest-like                                   | ❌&nbsp;describe/it      | ❌                            |
| Vendor lock-in                   | ❌&nbsp;Aucun                                                                                                                            | ❌&nbsp;Aucun                       | ⚠️&nbsp;Microsoft                                   | ⚠️&nbsp;Cypress.io       | ⚠️&nbsp;Selenium&nbsp;project |
| Auditabilité                     | ✅&nbsp;1 dep d'exécution                                                                                                                | ❌&nbsp;Écosystème&nbsp;interne     | ❌&nbsp;Node deps massives                          | ❌&nbsp;Cypress runtime  | ⚠️&nbsp;                      |
| Async/await                      | ❌&nbsp;Refus                                                                                                                            | ❌                                  | ✅&nbsp;Obligatoire                                 | ✅&nbsp;Obligatoire      | ❌                            |
| Parallélisation                  | ✅&nbsp;ThreadPool&nbsp;+&nbsp;Sémaphore&nbsp;+&nbsp;Stratégie de parallélisation simple et personnalisable par l'utilisateur sans magie | ⚠️&nbsp;pabot                       | ✅&nbsp;Workers JS                                  | ✅&nbsp;Parallel CI      | ❌                            |
| Approche _anti-flakiness_ native | ✅&nbsp;Parallélisation&nbsp;+&nbsp;Clonage de tests&nbsp;+&nbsp;Analyse fine par IA                                                     | ❌                                  | ❌                                                  | ❌                       | ❌                            |

## 7. Les valeurs qu'Ocarina porte

Le code de test&nbsp;:

- **doit être lisible par les testeurs fonctionnels** (vocabulaire ISTQB)
- **doit être un outil de communication inter-équipes avant tout** (idem)
- **doit être lisible par l'IA** (typage strict&nbsp;+&nbsp;linter strict&nbsp;+&nbsp;grammaire bien définie)
- **doit rester maintenable** (séparation fond/forme très forte)
- **doit être piloté par la stratégie de test sans compromis** (batterie de _skills_ énorme)
- **doit être auditable et portable** (une seule dep, MIT, copiable)
- **n'a pas besoin d'une plateforme** pour fonctionner
- **n'a pas à réinventer la roue** (retours aux fondamentaux)
