---
title: "01.04 — Citations et influences revendiquées"
description: "Les références citées dans le Holy Book ne sont pas neutres : elles fixent le cadre théorique d'Ocarina. On les recoupe ici par grands axes, puis on en propose une lecture d'ensemble."
weight: 4
date: 2026-05-20
series: ["philosophie"]
series_order: 4
tags: ["rop"]
---

# 01.04&nbsp;—&nbsp;Citations et influences revendiquées

> Les références citées dans le Holy Book ne sont pas neutres&nbsp;: elles fixent **le cadre théorique** d'Ocarina. On les recoupe ici par grands axes, puis on en propose une lecture d'ensemble.

## Axe technique&nbsp;—&nbsp;Programmation fonctionnelle, types, langages

| Influence                              | Origine                                                                | Rapport avec Ocarina                                                                                                                                                                                                                                                                  |
| -------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Railway Oriented Programming (ROP)** | Scott Wlaschin (F#), pattern bien connu en programmation fonctionnelle | Le cœur du framework. `Result[T] = Ok[T] \| Fail`, _short-circuit_, builder fluide. Voir [`../02-ocarina/03-railway/`](../02-ocarina/03-railway/README.md).                                                                                                                           |
| **λ-calcul (1930)**                    | Alonzo Church                                                          | Cité comme l'invention qui rend possible la «&nbsp;_formalisation propre_&nbsp;» qu'Ocarina poursuit&nbsp;: «&nbsp;_Ce que l'on pensait depuis les années 1930, **depuis l'invention du λ-calcul**, est enfin scalable à l'échelle que l'on aurait toujours voulu lui donner._&nbsp;» |
| **McCulloch & Pitts (1943)**           | Première formalisation du neurone artificiel                           | Cité comme rappel que les _vrais_ progrès en IA sont anciens et continus, contre la hype récente.                                                                                                                                                                                     |
| **Système de types Python (PEP 695)**  | PEP 695 (Python 3.12+)                                                 | Pré-requis pour le typage générique paramétrique qui structure Ocarina (`TestSuite[Driver]`, `Result[T]`, etc.). Voir [`../03-functional/06-pep-695-generics.md`](../03-functional/06-pep-695-generics.md).                                                                           |

## Axe culturel&nbsp;—&nbsp;Anti-narcissisme, simplicité, KISS bien compris

| Influence                                                                                  | Citation                                                                                                                                 | Pourquoi                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Terry Davis** («&nbsp;_le programmeur le plus intelligent qui ait jamais existé_&nbsp;») | «&nbsp;_Un idiot admire la complexité, un génie admire la simplicité, un physicien essaie de simplifier…_&nbsp;»                         | Argumentaire anti-complexité ostentatoire&nbsp;; pierre angulaire du chapitre «&nbsp;_Premiers retours_&nbsp;».                                                                                        |
| **Lao-Tseu**                                                                               | «&nbsp;_Pour avoir de la connaissance, ajouter des choses chaque jour. Pour avoir de la sagesse, enlever des choses chaque jour._&nbsp;» | Démarche de retrait&nbsp;: ce qui reste après élimination.                                                                                                                                             |
| **Antoine de Saint-Exupéry**                                                               | «&nbsp;_La perfection est atteinte non pas lorsqu'il n'y a plus rien à ajouter, mais lorsqu'il n'y a plus rien à retirer._&nbsp;»        | Reformulation occidentale du précédent. Clos le chapitre «&nbsp;_Premiers scénarios_&nbsp;».                                                                                                           |
| **Alan Watts**                                                                             | «&nbsp;_La meilleure façon de résoudre un problème est souvent d'en sortir._&nbsp;»                                                      | Cité en fin du chapitre «&nbsp;_Premiers jutsus_&nbsp;»&nbsp;: légitime un design qui _refuse_ certaines fonctionnalités (réactivité, async). Légitime la sortie de l'écosystème des _trucs de geeks_. |
| **Rainer Maria Rilke**                                                                     | «&nbsp;_Pour l'instant, vivez les questions…_&nbsp;»                                                                                     | Clos le chapitre «&nbsp;_Premiers pas_&nbsp;». Posture envers la pratique&nbsp;: la maîtrise vient par l'usage.                                                                                        |
| **Marcel Proust**                                                                          | «&nbsp;_Le style (…) est une question non de technique, mais de vision._&nbsp;»                                                          | Clos le chapitre «&nbsp;_Extensibilité_&nbsp;». Justifie le refus d'imposer un DSL&nbsp;:&nbsp;la vision (POMs + actions) prime sur la technique (un format).                                          |

## Axe politique&nbsp;—&nbsp;Code, souveraineté, anti-startup-nation

| Influence                                                       | Origine                                                                                | Rapport avec Ocarina                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **_Code is Law_**                                               | Lawrence Lessig (1999), repris par Ethereum (2015) comme idéal positif                 | Cité comme la posture face à la «&nbsp;_gouvernance démocratique du code_&nbsp;». Le code est la donnée brute, auditable. Le projet revendique&nbsp;: «&nbsp;_De nouveau, avec l'IA, ce maillon qu'il manquait cruellement, crions-le, aussi fort que l'on criait "HACK THE PLANET" en 99&nbsp;: **CODE IS LAW.**_&nbsp;» |
| **DHH&nbsp;—&nbsp;_I won't let you pay me for my open source_** | David Heinemeier Hansson, blog perso                                                   | Cité pour légitimer le refus de contributions non alignées («&nbsp;_Fuck You_&nbsp;» fait référence à la célèbre slide de DHH.)                                                                                                                                                                                           |
| **Paul Graham&nbsp;—&nbsp;_Haters_**                            | Essai PG (`paulgraham.com/fh.html`)                                                    | Justifie la décision de «&nbsp;_ne JAMAIS perdre [son] temps à argumenter lorsque ce n'est pas la peine_&nbsp;».                                                                                                                                                                                                          |
| **Yegor Bugayenko&nbsp;—&nbsp;_Prompt_**                        | Citation «&nbsp;_Retry flaky blocks._&nbsp;»                                           | Fond la politique `transient_errors` + retries linéaires (`TestFlow`). Lire aussi&nbsp;:&nbsp;_Angry Tests_.                                                                                                                                                                                                              |
| **The DAO hack (2016)**                                         | Hack de The DAO sur Ethereum                                                           | Cité pour pointer que ce sont _les bugs_ («&nbsp;_des satanés bugs, à cause de satanés dévs_&nbsp;») qui ont fait reculer l'idée de _Code is Law_, d'où l'importance du typage et de la rigueur.                                                                                                                          |
| **Lee Robinson (ex-Vercel)**                                    | Décembre 2025&nbsp;: remplacement de Sanity par des fichiers Markdown + IA chez Cursor | Soutient le «&nbsp;_retour à la donnée brute_&nbsp;».                                                                                                                                                                                                                                                                     |
| **Cluely (Roy Lee)**                                            | Cité pour illustrer le _bullshit_ entrepreneurial à éviter                             | Contraste explicite avec la philosophie Ocarina.                                                                                                                                                                                                                                                                          |

## Axe identitaire /&nbsp;_underground_

| Influence                                                                                      | Origine                                                                             |
| ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Lulzsec**&nbsp;—&nbsp;«&nbsp;_In the Lulzboat, salute, bitch, and show some respect._&nbsp;» | Antisec (YTCracker, 2011)                                                           |
| **«&nbsp;_We Can Do All What You Can't Do_&nbsp;»**                                            | YogyaCarderLink                                                                     |
| **YTCracker&nbsp;—&nbsp;_Robots Will Definitely Take Your Job_**                               | Lien SoundCloud, musique de fond du chapitre «&nbsp;_Premiers retours_&nbsp;»       |
| **«&nbsp;_HACK THE PLANET_&nbsp;» (1999)**                                                     | Slogan emblématique de la scène hackers des années 1990 + Antisec (YTCracker, 2011) |
| **Zone-H**                                                                                     | Site historique de defaces web                                                      |
| **r/unixporn**, **r/AntiTaff**                                                                 | Subreddits                                                                          |

## Axe IA /&nbsp;outillage moderne

| Influence                  | Origine                                                           | Rapport avec Ocarina                                                                                                                      |
| -------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Claude Code**            | Anthropic                                                         | Outillage de référence du projet IA (`ocarina-with-ai-example`). Cité plusieurs fois comme «&nbsp;_pont_&nbsp;» remplaçant les DSLs.      |
| **IntelliCode (2018)**     | Microsoft                                                         | Cité comme repère temporel («&nbsp;_on y avait déjà goûté, avant même IntelliCode_&nbsp;»).                                               |
| **R., savant fou du silo** | Anecdote personnelle (un collègue de 2013, plugin Emacs IA privé) | Rappel que l'IA générative («&nbsp;_15&nbsp;000 lignes à supprimer pour éviter d'en écrire 1000_&nbsp;») existait avant la hype publique. |
| **Prisma, Vercel, Cursor** | Écosystème SaaS                                                   | Cités comme cas pratiques de _retour à la donnée brute_ assisté par IA.                                                                   |

## Cohérence d'ensemble

Toutes ces influences pointent vers **trois axes convergents**&nbsp;:

1. **La donnée brute typée** comme matériau primaire (lambda-calcul&nbsp;→&nbsp;ROP →&nbsp;Python typé →&nbsp;IA).
2. **La sophistication aboutissant à la simplicité** comme métrique de qualité.
3. **La souveraineté** comme posture politique.

ROP en est l'incarnation technique&nbsp;: faire du _flux d'échec_ une **valeur typée** (Ok/Fail) plutôt qu'un effet de bord (exception levée). Le résultat est à la fois fonctionnel _et_ accessible. Le Holy Book le résume&nbsp;:

> Ocarina rend son mésusage difficile par conception&nbsp;: le compilateur fait foi.

## Ce que ces influences **n'ont pas** apporté

| Absent                                                                                                       | Pourquoi                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Aucune référence à un framework de test concurrent _adopté_ (Cypress, Playwright, Mocha, Jest, RF, Cucumber) | Tous sont mentionnés _en contraste_, jamais en source d'inspiration.                                                      |
| Aucune référence à une école «&nbsp;_Clean Code_&nbsp;» ou «&nbsp;_SOLID_&nbsp;»                             | «&nbsp;_Vous. Ne. Savez. Même pas. Ce que. "Clean code". Veut. Réellement. DIRE._&nbsp;»                                  |
| Aucune référence à un framework DI (Spring, Guice, Hilt)                                                     | L'IoC se fait par closures&nbsp;—&nbsp;voir [`../03-functional/02-closures-ioc.md`](../03-functional/02-closures-ioc.md). |

L'absence est aussi un choix.
