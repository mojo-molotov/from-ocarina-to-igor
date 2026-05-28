---
title: "01.05 — Posture politique du projet"
description: "Les cinq engagements opérationnels qui découlent de la philosophie d'Ocarina : incorruptibilité, direction assumée, et leurs conséquences sur le dépôt."
weight: 5
date: 2026-05-20
series: ["philosophie"]
series_order: 5
tags: ["selenium"]
---

# 01.05&nbsp;—&nbsp;Posture politique du projet

> Le Holy Book ne sépare pas la philosophie de la **politique du dépôt** lui-même. Cinq engagements opérationnels en découlent.

## 1. Incorruptibilité

> «&nbsp;_Transmettre Ocarina, c'est transmettre une voiture dont j'ai fait tout l'entretien moi-même, pour moi-même, donc très précautionneusement. En revanche, elle est et restera transmise telle quelle. C'est ma voiture._&nbsp;»
>
> «&nbsp;_J'y ai canalisé toute ma colère, pour y mettre tout mon amour._&nbsp;»
>
> «&nbsp;_Ocarina a une direction. Ceux qui souhaitent l'emmener ailleurs avec leurs vues de l'esprit sont libres d'en faire un fork et de ne jamais me contacter._&nbsp;»

Conséquences pratiques&nbsp;:

- **Refus des contributions «&nbsp;_stylées_&nbsp;»**. La phrase de DHH est citée comme aval&nbsp;: «&nbsp;_Fuck You_.&nbsp;»
- **Refus assumé des PRs /&nbsp;issues non alignées**. «&nbsp;_aucun regret à fermer toute PR ou issue inutile._&nbsp;»
- **Refus de la «&nbsp;_gouvernance démocratique du code_&nbsp;»**. Le projet est explicitement souverain.

Aucune contribution n'est exclue _a priori_&nbsp;: la **barrière à l'entrée** est _l'alignement_ avec la direction.

## 2. Anti-hype

> «&nbsp;_Ce même décembre 2025, cette startup dont le nom sera tu était présentée dans certains médias comme "le test IA No-Code qui ridiculise Selenium et fait trembler BrowserStack". Rien que ça._&nbsp;»

> «&nbsp;_Pour autant, rien de cela ne coupera Ocarina d'une vision qui se développe depuis plus de 15 ans, loin de l'arrogance de tous ces enfants de la hype._&nbsp;»

- Aucune dépendance «&nbsp;_branchée_&nbsp;» sans valeur fondamentale. Une seule dépendance d'exécution (`python-docx`).
- Le projet revendique sa filiation à un héritage ancien (ISTQB, ROP, λ-calcul).
- Le terme «&nbsp;_pamphlet_&nbsp;» est revendiqué («&nbsp;_n'importe quel projet "cutting-edge", quel qu'il soit, démarre d'un pamphlet, est identitaire et passe par une étape de réel anti-marketing._&nbsp;»).

## 3. Anti-slipologues

_Slipologue_ = celui qui prétend «&nbsp;_tout savoir_&nbsp;» sans pratique, et qui pollue les discussions techniques avec des _vues de l'esprit_.

> «&nbsp;_Pendant trop longtemps, l'informatique a été prise en otage par une minorité, un "1%", qui a cru bon de la transformer en terrain de jeux pour initiés&nbsp;: "trucs de geeks", "techniques de ninjas", "orienté objet". Le verdict est sans appel&nbsp;: ça ne tient pas, ou alors très mal._&nbsp;»

Et&nbsp;:

> «&nbsp;_Tout comme l'IA, qui achève tranquillement de rendre la capacité de nuisance de ce "1%" obsolète._&nbsp;»

Conséquences pratiques&nbsp;:

- Pas d'_event-driven programming_ comme nouvelle religion.
- Pas d'_orienté objet déclaratif_.
- Pas de Rust «&nbsp;_pour la performance_&nbsp;» (cf. [`03-kiss-and-complexity.md`](03-kiss-and-complexity.md)).

## 4. Anti No-Code, _Code is Law_

> «&nbsp;_Le code est une donnée brute. Auditable. Consultable. Une boîte blanche. Très exactement ce avec quoi l'IA sait travailler depuis ses débuts._&nbsp;»

Et&nbsp;:

> «&nbsp;_Toujours est-il que le code est ce que l'on a de plus souverain, et qu'une promesse de valeur consistant à nous le retirer nous fait nous pincer le nez._&nbsp;»

Conséquences pratiques&nbsp;:

- Tout le code utilisateur d'Ocarina est du Python&nbsp;: auditable, copiable, exécutable sans plateforme tierce.
- Le framework est explicitement _portable_ «&nbsp;_sans installation_&nbsp;»&nbsp;: «&nbsp;_pour les scénarios les plus extrêmes&nbsp;: Ocarina n'a pas besoin d'être installé. Il se copie, s'adapte, et tourne._&nbsp;»
- Pas de SaaS associé. Pas de _cloud runner_ propriétaire.

## 5. Refus permanent d'`async`/`await`

> «&nbsp;_Ocarina ne supporte pas `async`/`await` et ne le fera jamais._&nbsp;»

Justifications matérialisées&nbsp;:

| Raison                           | Détail                                                                                                                                     |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Selenium est synchrone           | Pas d'API `async` native&nbsp;; tout `async` au-dessus serait une couche d'enrobage stérile.                                               |
| `requests`, `redis` synchrones   | L'écosystème ciblé (HTTP, Redis, fichiers) tient en synchrone sans coût.                                                                   |
| Lisibilité                       | Un scénario `async` impose des `await` au milieu, casse la grammaire visuelle «&nbsp;_ouverture&nbsp;→&nbsp;acts →&nbsp;fermeture_&nbsp;». |
| Concurrence couverte par threads | Le `ThreadPoolExecutor` + le `WebDriversPool` (`Semaphore`) couvrent les besoins de parallélisation. Pas besoin d'`asyncio`.               |
| Verrous distribués via Redis     | Pour les besoins multi-process, c'est Redis qui coordonne (`OTP_SEND_LOCK_KEY`, etc.), pas une event loop.                                 |

## 6. Sécession

> «&nbsp;_Aujourd'hui les gens lancent des projets comme on descend de chez soi acheter un paquet de clopes. (…) Ils se croient malins&nbsp;: la réalité est que tout VC, tout LP, tout le monde, en est bien conscient et chacun tient son rôle dans un jeu de dupes._&nbsp;»

Conséquence&nbsp;: Ocarina est _publié sous le nom d'auteur d'Igor Casanova_, sans entité commerciale derrière, sans promesse de support, sans roadmap publique. Le dépôt est mis à disposition «&nbsp;_tel quel_&nbsp;» au sens MIT du terme.

> «&nbsp;_Quant à moi, je n'ai rien à perdre en termes de réputation puisqu'il n'y a pas de réputation à construire sous ce nom. Uniquement un message à livrer, tel qu'il est, sans filtre._&nbsp;»

## 7. Refus des «&nbsp;_tricks/hacks_&nbsp;» (côté projet IA)

Le `CLAUDE.md` d'`ocarina-with-ai-example` détaille la mise en pratique&nbsp;:

> «&nbsp;_No tricks or hacks. JS-clicks to skip hit-testing, `# noqa` to silence a rule, `time.sleep` to mask a race, `driver.implicitly_wait` to patch a timing bug. If a hack is genuinely the only option, document why no clean fix exists and mark it so a reader doesn't copy the pattern._&nbsp;»

C'est la **mise en discipline** des principes ci-dessus dans une suite réelle.

Contre-exemple cité&nbsp;:

> «&nbsp;_The JS-click-for-logout incident is the canonical anti-example: `ElementClickInterceptedException` had a clean polling fix; the JS click hid the problem._&nbsp;»

## Tableau de synthèse

| Refus                                          | Mécanisme code                              | Lien                                                                                                                                                                             |
| ---------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `async`/`await`                                | Threads + `Semaphore` + Redis               | [`../02-ocarina/10-infra/01-drivers-pool.md`](../02-ocarina/10-infra/01-drivers-pool.md), [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md) |
| Plugin pytest                                  | Runner intégré (`bootstrap`)                | [`../02-ocarina/11-opinionated/06-bootstrap-launcher.md`](../02-ocarina/11-opinionated/06-bootstrap-launcher.md)                                                                 |
| DSL textuel                                    | DSL Python embedded                         | [`../02-ocarina/03-railway/`](../02-ocarina/03-railway/README.md)                                                                                                                |
| Programmation réactive dans les scénarios      | Cache + clés réservées                      | [`../07-ocarina-example/08-caches-locks.md`](../07-ocarina-example/08-caches-locks.md)                                                                                           |
| `# noqa` muet                                  | Toujours explicite et local                 | `pyproject.toml#tool.ruff`                                                                                                                                                       |
| Contributions «&nbsp;_stylées_&nbsp;»          | Modèle MIT _take it or fork it_             | &nbsp;—&nbsp;                                                                                                                                                                    |
| JS-click pour bypasser le hit-testing          | Polling propre                              | [`../08-ai-example/`](../08-ai-example/README.md)                                                                                                                                |
| `time.sleep` pour masquer une race condition   | Polling explicite via `WebDriverWait`       | id.                                                                                                                                                                              |
| `driver.implicitly_wait` patché hors framework | Géré uniquement par `--wait-timeout` du CLI | [`../02-ocarina/11-opinionated/03-selenium-cli.md`](../02-ocarina/11-opinionated/03-selenium-cli.md)                                                                             |

## Mot de la fin

> «&nbsp;_Ocarina n'est pas et ne sera JAMAIS une solution pontifiante._&nbsp;»
> «&nbsp;_Ocarina est et RESTERA une solution pour résoudre des problèmes concrets._&nbsp;»

Cette posture politique a un effet pratique direct sur ce qui mérite d'être lu en profondeur&nbsp;: le code source plutôt qu'un changelog, le Holy Book plutôt qu'un blog post marketing. C'est la promesse d'auditabilité de [`../11-independence/02-auditability.md`](../11-independence/02-auditability.md)
