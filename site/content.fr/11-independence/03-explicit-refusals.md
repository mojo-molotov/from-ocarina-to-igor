---
title: "11.03 — Refus explicites"
description: "La synthèse des refus explicites d'Ocarina : async, plugin pytest, DSL textuel et programmation réactive, chacun avec sa raison."
weight: 3
date: 2026-05-20
series: ["independance"]
series_order: 3
---

# 11.03&nbsp;—&nbsp;Refus explicites

> Synthèse des refus dispersés dans le Holy Book.

## Tableau récapitulatif

| Refus                                 | Raison                                                                                                                | Référence              |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `async`/`await`                       | Selenium synchrone, Requests synchrone&nbsp;;&nbsp;lisibilité&nbsp;;&nbsp;aucun intérêt d'introduire une _event-loop_ | Holy Book              |
| Plugin pytest                         | Indépendance, fidélité ISTQB                                                                                          | `README` Ocarina       |
| DSL textuel (Robot, Gherkin)          | Pas de couche de traduction                                                                                           | Holy Book              |
| Programmation réactive                | Static scenarios, cache in-memory suffit                                                                              | Holy Book              |
| Tricks et hacks                       | «&nbsp;_Teach the pattern, not the symptom_&nbsp;»                                                                    | `CLAUDE.md` ai-example |
| Contributions «&nbsp;_stylées_&nbsp;» | «&nbsp;_C'est ma voiture_&nbsp;»                                                                                      | Holy Book              |
| Tests sécurité actifs                 | Fonctionnel et statique uniquement, jamais d'attaques                                                                 | `CLAUDE.md` ai-example |

## 1. Refus d'`async`/`await`

Citation centrale&nbsp;:

> Ocarina ne supporte pas `async`/`await` et ne le fera jamais.

| Argument                              | Réponse                                                                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| «&nbsp;_C'est plus rapide_&nbsp;»     | Pas pour Selenium (synchrone par nature)                                                                                        |
| «&nbsp;_Tout le monde le fait_&nbsp;» | Tout le monde le fait souvent _mal_                                                                                             |
| «&nbsp;_Pour les API HTTP_&nbsp;»     | `requests` (synchrone) marche très bien                                                                                         |
| «&nbsp;_Pour les locks_&nbsp;»        | `threading.Lock` + `redis.lock` suffisent                                                                                       |
| «&nbsp;_Pour paralléliser_&nbsp;»     | `ThreadPoolExecutor` (cf. [`../02-ocarina/05-orchestration/04-test-suite.md`](../02-ocarina/05-orchestration/04-test-suite.md)) |

## 2. Refus d'être un plugin pytest

`README` d'Ocarina&nbsp;:

> Ships its own test runner: Ocarina is NOT a pytest plugin.

| Avec plugin pytest                                  | Standalone runner                                |
| --------------------------------------------------- | ------------------------------------------------ |
| Vocabulaire pytest (function, fixture, parametrize) | Vocabulaire ISTQB (test, suite, campaign, cycle) |
| Lifecycle dépend de pytest                          | Lifecycle propre, contrôlable                    |
| Compatibility avec autres plugins pytest            | Pas de surface API à maintenir                   |
| Discoverable via `pytest --collect`                 | `python -u src/main.py` direct                   |

→ Cf. [`../01-philosophy/02-istqb-vs-pytest.md`](../01-philosophy/02-istqb-vs-pytest.md)

## 3. Refus de DSL textuels

Pas de fichier `.robot`, `.feature`, `.spec.yml`. Tout est Python.

Citation (Holy Book `what-is-it`)&nbsp;:

> _Robot Framework_ a essayé de la contourner avec un _DSL_ (...) **leur propre format** et **leur propre écosystème de plugins**. Ainsi, RF impose de-facto ses propres standards&nbsp;: c'est le coût immédiat de sa promesse.

| DSL textuel                                            | DSL Python embedded                   |
| ------------------------------------------------------ | ------------------------------------- |
| Couche de traduction (parser, runtime alternatif)      | Aucune&nbsp;: c'est juste Python      |
| Refactoring difficile (chercher dans des `.robot`)     | Refactoring trivial (IDE Python)      |
| Type checking impossible /&nbsp;partiel                | Type checking complet (`mypy strict`) |
| Outillage propriétaire (PyCharm RF plugin, RIDE, etc.) | N'importe quel éditeur Python         |

→ Cf. [`../01-philosophy/01-flip-the-problem.md`](../01-philosophy/01-flip-the-problem.md)

## 4. Refus de la programmation réactive

Holy Book (chapitre «&nbsp;_Premiers jutsus_&nbsp;», section «&nbsp;_Programmation réactive&nbsp;: NON_&nbsp;»)&nbsp;:

> Les scénarios de test d'Ocarina sont volontairement statiques. Pourtant, une application web est dynamique et parfois, enregistrer une valeur à la volée pour la passer à une étape suivante est tout à fait légitime.
>
> Ocarina n'y répond pas. Il n'en a pas besoin.

Réponse&nbsp;: cache in-memory + clés réservées (cf. [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md))

| Avec réactivité                                     | Sans (cache)                         |
| --------------------------------------------------- | ------------------------------------ |
| Scénarios pleins de _streams_ et de _subscriptions_ | Scénarios déclaratifs lisibles       |
| Debugging difficile (event flow)                    | Debugging trivial (sequential calls) |
| Concurrency hazards subtils                         | `threading.Lock` simple              |
| Dependencies sur RxPY ou similaire                  | Aucune dep réactive                  |

## 5. Refus des «&nbsp;_trucs de geeks_&nbsp;»

`CLAUDE.md` `ocarina-with-ai-example`&nbsp;:

> **No tricks or hacks.** JS-clicks to skip hit-testing, `# noqa` to silence a rule, `time.sleep` to mask a race, `driver.implicitly_wait` to patch a timing bug. If a hack is genuinely the only option, document why no clean fix exists and mark it so a reader doesn't copy the pattern. The JS-click-for-logout incident is the canonical anti-example: `ElementClickInterceptedException` had a clean polling fix; the JS click hid the problem.

| Hack                                                          | Pourquoi c'est non                                                           |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `driver.execute_script("...click()")` pour bypass hit-testing | Cache un défaut UI réel&nbsp;; un utilisateur humain n'aurait pas pu cliquer |
| `# noqa` sans justification                                   | Cache une vraie violation de style/sécurité                                  |
| `time.sleep(N)` pour masquer une race condition               | Conneries de «&nbsp;_timings mystérieux_&nbsp;»                              |
| `driver.implicitly_wait(N)` patché hors framework             | Décorrèle de la config CLI `--wait-timeout`                                  |
| `delete_all_cookies()` pour «&nbsp;_reset state_&nbsp;»       | Un utilisateur ne fait pas ça&nbsp;; cache un vrai bug de session            |
| `driver.refresh()` pour bypass cache                          | Un utilisateur ne fait pas ça&nbsp;; cache un vrai bug                       |
| Query-string cache-busters (`?_=<ts>`)                        | Idem                                                                         |

→ Si un _hack_ est **vraiment** nécessaire&nbsp;: documenter pourquoi.

## 6. Refus des contributions «&nbsp;_stylées_&nbsp;»

Holy Book (chapitre «&nbsp;_Premiers retours_&nbsp;», section «&nbsp;_Incorruptibles_&nbsp;»)&nbsp;:

> «&nbsp;_Transmettre Ocarina, c'est transmettre une voiture dont j'ai fait tout l'entretien moi‑même, pour moi‑même, donc très précautionneusement. En revanche, elle est et restera transmise telle quelle. C'est ma voiture._&nbsp;»

Et&nbsp;:

> «&nbsp;_Contribuer à un projet open source parce que c'est "stylé" est une vision totalement immature et la tolérance à ce phénomène crée des ravages._&nbsp;»

→ Critère d'acceptation des contributions&nbsp;: **alignement** avec la direction. Pas «&nbsp;_est-ce que ça marche_&nbsp;» mais «&nbsp;est-ce que ça _respecte_ la philosophie du projet&nbsp;?&nbsp;».

L'auteur cite DHH&nbsp;:

> [Ma réponse sera complétée d'une citation de David Heinemeier Hansson (DHH)&nbsp;: "Fuck You".](https://world.hey.com/dhh/i-won-t-let-you-pay-me-for-my-open-source-d7cf4568)

[![Fuck you](/assets/img/dhh-fuck-you-vendoritis-2006.jpg)](https://world.hey.com/dhh/i-won-t-let-you-pay-me-for-my-open-source-d7cf4568)

## 7. Refus des tests de sécurité actifs/offensifs

`CLAUDE.md` `ocarina-with-ai-example`&nbsp;:

> This is a **functional** test suite. (...) Inside that scope:
>
> - Static analysis is welcome and encouraged.
> - Functional tests that exercise security-relevant behaviour through the **normal UI/HTTP path** (...) are fine.
>
> **Forbidden, no exceptions:**
>
> - Crafted attack payloads of any kind: SQL injection strings, XSS /&nbsp;HTML /&nbsp;JS payloads, command injection, header/parameter pollution, path traversal, deserialisation payloads.
> - Token tampering, signature stripping, cookie forgery, session-fixation attempts, forced-browsing fuzzers.
> - Cross-origin POSTs constructed outside the suite, scripted directory enumeration, DOS, rate-floods&nbsp;—&nbsp;anything that escalates from "use the app like a user" to "attack the app like an adversary".

→ Limite **stricte**&nbsp;: on _utilise_ l'app comme un utilisateur, on _ne l'attaque pas_ comme un acteur malveillant.

Si on veut tester activement&nbsp;: c'est un autre projet (Burp, ZAP, sqlmap, nouveau contrat et périmètre dédiés).

## Pourquoi

Chaque refus **recentre** le projet&nbsp;:

| Refus                                        | Simplification                                 |
| -------------------------------------------- | ---------------------------------------------- |
| Pas d'`async`                                | Code synchrone lisible                         |
| Pas de plugin pytest                         | Pas de pytest API incompréhensible à apprendre |
| Pas de DSL textuel                           | Pas de parser à maintenir                      |
| Pas de réactivité                            | Cache simple suffit                            |
| Pas de hacks                                 | Code expressif                                 |
| Pas de contributions «&nbsp;_stylées_&nbsp;» | Direction cohérente                            |
| Pas de tests sécurité actifs                 | Respect du périmètre fonctionnel               |

→ Le `non` est aussi du design. Cf. Steve Jobs&nbsp;: «&nbsp;_Innovation is saying no to 1,000 things._&nbsp;»

## Refus de l'expansion sans bénéfice

En réalité, aucun de ces refus n'est dogmatique.  
Chacun est **justifié** par un compromis explicite&nbsp;:

```
Avantage hypothétique : X
Coût opératoire : Y
Verdict : pas la peine
```

Si demain un nouveau cas d'usage justifie de _reconsidérer_ un refus, l'auteur le fera.  
Mais le fardeau de la preuve est sur celui qui propose, pas sur l'auteur.

C'est l'incarnation pratique de la souveraineté.
