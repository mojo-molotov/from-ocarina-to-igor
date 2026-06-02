---
title: "12.09 — Cohérence de l'écosystème"
description: "Comment six dépôts hétérogènes en langages, licences et plateformes servent rigoureusement le même pari : la cohérence de l'écosystème Ocarina."
weight: 9
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 9
---

# 12.09&nbsp;—&nbsp;Cohérence de l'écosystème

> Six dépôts, plusieurs langages, plusieurs technologies, plusieurs licences, plusieurs plateformes de déploiement. À première vue, hétérogène. À deuxième lecture, **rigoureusement cohérent**&nbsp;:&nbsp;chaque pièce sert _exactement le même_ pari.

## 1. Vue d'ensemble&nbsp;:&nbsp;six dépôts, une éthique

```
┌────────────────────────────────────────────────────────────────────────┐
│         L'ÉCOSYSTÈME COMME UN TOUT COHÉRENT                            │
└────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐    Le framework. ROP, types stricts, refus de plugin
  │   ocarina    │    pytest. UNE seule dep d'exécution. Auditable en
  └─────────────┬┘    une après-midi. — PROUVE que la rigueur est légère.
                │
                │
                ▼
  ┌─────────────────┐ La référence d'usage. Adapters projet. Patterns
  │ ocarina-example │ canoniques. Démontre comment on rétrécit la surface
  └─────────────┬───┘ d'API du framework pour son contexte. — PROUVE que
                │     le framework est utilisable « par n'importe qui ».
                │
                ▼
  ┌─────────────────────────┐ Le pari IA. Co-écrit par Claude 99%. CURA
  │ ocarina-with-ai-example │ Healthcheck comme SUT. Findings sourcés jusqu'au PHP.
  └─────────────┬───────────┘ — PROUVE que l'IA + Ocarina peut faire un
                │               vrai travail de testeur senior.
                ▼
       ┌──────────────┐ Le SUT volontairement chaotique. Le terrain.
       │  igoristan   │ — PROUVE qu'on peut tester une appli pathologique
       └────────┬─────┘   sans tricher.
                │
                ▼
       ┌────────────────┐ Le backend de coordination. Vercel Edge,
       │ tests-workers  │ Upstash Redis, anti-précision volontaire.
       └────────┬───────┘ — PROUVE qu'on peut faire de la coordination
                │           distribuée sans plateforme propriétaire.
                │
                ▼
       ┌───────────────────┐ La documentation publique. VitePress + FR/EN/RU
       │ ocarina-holy-book │ + LLM-first (llms.txt, CLAUDE.md, skills).
       └───────────────────┘ — PROUVE qu'on peut écrire de la doc qui sert
                               humain ET IA, sans plateforme tierce.
```

## 2. Un dépôt&nbsp;=&nbsp;un type de défi

| Dépôt                     | Type de défi                             | Pari prouvé                                                                                       |
| ------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `ocarina`                 | Construire un framework petit et profond | «&nbsp;_La rigueur n'est pas une usine à gaz_&nbsp;»                                              |
| `ocarina-example`         | Démontrer un usage canonique             | «&nbsp;Tu peux _vraiment_ écrire des tests rigoureux comme ça&nbsp;»                              |
| `ocarina-with-ai-example` | Faire collaborer un humain et une IA     | «&nbsp;_L'IA est le pont, pas le DSL_&nbsp;»                                                      |
| `igoristan`               | Bâtir un SUT _chaotique_                 | «&nbsp;_Pas de démo sur un site qui fait vingt lignes d'HTML, une démo sur un vrai bordel_&nbsp;» |
| `tests-workers`           | Être le substrat par lequel les tests se coordonnent | «&nbsp;On peut être _stateless_ côté code&nbsp;»                                      |
| `ocarina-holy-book`       | Documenter pour humains _et_ IA          | «&nbsp;_La documentation est avant tout de la donnée brute pour les LLMs_&nbsp;»                  |

Si on enlève l'un de ces dépôts, l'écosystème **perd un argument**.  
Les six sont **solidaires**.

## 3. Les invariants transverses

### Licence

| Dépôt                     | Licence                          |
| ------------------------- | -------------------------------- |
| `ocarina`                 | MIT                              |
| `ocarina-example`         | MIT                              |
| `ocarina-with-ai-example` | MIT                              |
| `ocarina-holy-book`       | MIT                              |
| `igoristan`               | _aucune_ (démo publique)         |
| `tests-workers`           | ISC (par défaut Vercel scaffold) |

MIT partout sauf cas particuliers. **La licence est permissive au maximum dans tous les cas**.

### Signature

Chaque README termine par&nbsp;:

```
Built by [@mojo-molotov](https://github.com/mojo-molotov)
Fueled by figatellu and Квас.
```

**Signature décalée et uniforme**.  
C'est une convention Zone-H&nbsp;/&nbsp;IRC ([`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)).

### Trois conventions Git

| Convention               | Manifestation                                                  |
| ------------------------ | -------------------------------------------------------------- |
| **Conventional Commits** | `commitlint` + `commitizen` (Igoristan, Holy Book, ai-example) |
| **Pre-commit hooks**     | Husky (JS) ou pre-commit Python (`ocarina`, `ocarina-example`) |
| **Pas de `.no-verify`**  | Aucun bypass des hooks. Si ça plante, on fixe.                 |

### Trois conventions CI/CD

| Convention                          | Manifestation                                 |
| ----------------------------------- | --------------------------------------------- |
| **PR-gate rapide**                  | lint + typecheck (ou check-coding-style)      |
| **E2E manuel**                      | `workflow_dispatch` uniquement, jamais sur PR |
| **`if: always()` upload artifacts** | On garde toutes les traces                    |

### Trois conventions de code

| Convention                                     | Manifestation                                       |
| ---------------------------------------------- | --------------------------------------------------- |
| **Strict type checker**                        | `mypy strict` (Python), `tsc --build` strict (TS)   |
| **Linter en `select = ["ALL"]` ou équivalent** | `ruff ALL` (Python), `eslint --max-warnings 0` (TS) |
| **Pas de `# noqa` muet**                       | Toujours justifié, toujours local                   |

## 4. La cohérence des choix de stack par contexte

| Contexte         | Choix                                          | Pourquoi cohérent                                                                         |
| ---------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Framework Python | Python 3.14+ avec PEP 695                      | Typage strict moderne                                                                     |
| Site démo        | React 19&nbsp;+&nbsp;Vike&nbsp;+&nbsp;Tailwind | Stack frontend de _référence_ 2026&nbsp;;&nbsp;pas de dette inutile                       |
| Backend léger    | Vercel Edge + Upstash Redis                    | Stateless, low-cost, low-tech, déployable en 30 secondes                                  |
| Documentation    | VitePress (pas Docusaurus, MkDocs, Sphinx)     | Vite-based, alignement avec le frontend du SUT, aspects LLM-friendly construits à la main |
| Génération PDF   | Reportlab&nbsp;+&nbsp;IA pour orchestrer       | Workflow agentique                                                                        |

## 5. La cohérence du _ton_

Le _ton_ est uniforme, différent selon le médium mais aligné&nbsp;:

| Médium                           | Ton                                                                          |
| -------------------------------- | ---------------------------------------------------------------------------- |
| README `ocarina`                 | Technique sobre, factuel                                                     |
| README `ocarina-example`         | Technique avec touches d'humour («&nbsp;_figatellu and Квас_&nbsp;»)         |
| README `ocarina-with-ai-example` | Honnête et démonstratif («&nbsp;_99% Claude /&nbsp;50% intelligence_&nbsp;») |
| README `igoristan`               | Minimaliste («&nbsp;_Welcome to the Empire_&nbsp;»)                          |
| README `tests-workers`           | Documentation API directe                                                    |
| Holy Book                        | Pamphlétaire, identité forte, citations _underground_                        |
| `CLAUDE.md`                      | Règles strictes, exemples du passé, vocabulaire ferme                        |

Le _Holy Book_ est le point _le plus chaud_.  
Les README sont _froids_.

Cette différence est volontaire&nbsp;:

- `README`&nbsp;=&nbsp;surface technique. Doit être _utilisable_ avec le moins de bruit possible.
- Holy Book&nbsp;=&nbsp;surface philosophique. Doit être _ressenti_.

Comme dans le _zine underground_&nbsp;:&nbsp;la doc technique froide _existe_, mais la _vraie voix_ vit dans le manifeste séparé.

## 6. La cohérence inter-dépôts via les **secrets partagés**

Cf. [`../00-big-picture/04-repo-relations.md`](../00-big-picture/04-repo-relations.md)

Un seul secret (`IGOR_API_KEY` ≡ `API_SECRET`) gouverne toutes les interactions OTP entre&nbsp;:

- `ocarina-example` (consommateur).
- `tests-workers` (serveur).
- `igoristan` (UI qui le passe).

Pas trois secrets, pas une matrice de permissions. **Un**.  
C'est le minimum vital.

> «&nbsp;_Auditable en une après-midi_&nbsp;».

## 7. La cohérence des **bugs**

| Failure volontaire                               | Où               | Pourquoi                                              |
| ------------------------------------------------ | ---------------- | ----------------------------------------------------- |
| `Math.random() < 0.9` sur `useAuth`              | `igoristan`      | Forcer à retry côté Ocarina                           |
| `Math.random() < 0.3` sur la page `random-error` | `igoristan`      | Forcer à utiliser les `transient_errors`              |
| `Math.random() < 0.3` sur `donkey-sausage`       | `igoristan`      | Forcer `match_page`                                   |
| 1/5 chance d'`Error('lol')` sur Corsicamon       | `igoristan`      | Forcer à retry côté Ocarina                           |
| Timestamp OTP amputé des ms                      | `tests-workers`  | Forcer une coordination fine entre tests parallélisés |
| Élément `.catch-me-if-you-can` aléatoire         | `igoristan`      | Forcer l'usage des `Watcher`                          |
| Heroku eco-dyno qui s'endort (CURA)              | externe          | Forcer le warm-up CI                                  |
| BFCache Chrome restore `no-store`                | externe (Chrome) | Forcer la cross-browser matrix                        |
| Password manager Chrome qui catch les inputs     | externe (Chrome) | Forcer un adapter `create_drivers_pool` custom        |

## 8. La cohérence des **refus**

| Dépôt                     | Refus spécifique                                                                             |
| ------------------------- | -------------------------------------------------------------------------------------------- |
| `ocarina`                 | `async/await`, plugin pytest, DSL textuel, contributions «&nbsp;_stylées_&nbsp;»             |
| `ocarina-example`         | Mocks (utilise le vrai Igoristan), e2e sur PR (cher, manuel uniquement)                      |
| `ocarina-with-ai-example` | Tests sécurité actifs, hacks, JS-clicks pour bypass, solutions de contournement dégueulasses |
| `igoristan`               | Tests unitaires (tout est en e2e externe)                                                    |
| `tests-workers`           | CI GitHub (Vercel suffit), framework côté serveur (handlers `.ts` directs)                   |
| `ocarina-holy-book`       | Algolia (Pagefind statique)                                                                  |

## 9. La cohérence avec la posture politique

Cf. [`../11-independence/03-explicit-refusals.md`](../11-independence/03-explicit-refusals.md) et [`../01-philosophy/05-political-stance.md`](../01-philosophy/05-political-stance.md)

L'auteur _refuse_&nbsp;:

- Les contributions «&nbsp;_stylées_&nbsp;»
- Les PRs&nbsp;/&nbsp;issues non alignées
- La «&nbsp;_gouvernance démocratique du code_&nbsp;»
- `async/await`
- Les vendors
- Les plateformes propriétaires
- Le _melon-engineering_

L'écosystème _matérialise_ ces refus&nbsp;:

- Pas de bot GitHub qui auto-merge
- Pas de Discord, pas de Slack
- Pas de financement Patreon&nbsp;/&nbsp;GitHub Sponsors&nbsp;/&nbsp;OpenCollective&nbsp;/&nbsp;aucune demande de _sponsor_
- Pas de SLA, pas de support payant
- Pas de _talks_ sponsorisés
- Pas de _merchandising_

## 10. La méta-cohérence&nbsp;:&nbsp;le _précis_ lui-même

| Trait du précis                    | Aligné avec                        |
| ---------------------------------- | ---------------------------------- |
| Que du Markdown, propulsé par Hugo | Anti-No-Code, anti-SaaS, anti-Dévs |
| Multi-fichiers cross-référencés    | Composition, pas monolithe         |
| Schémas ASCII                      | Pas de tooling propriétaire        |
| Gratuit, pas de paywall            | _Code is Law_                      |
| Pédagogie sans filtre              | Tout est expliqué, RTFM            |
