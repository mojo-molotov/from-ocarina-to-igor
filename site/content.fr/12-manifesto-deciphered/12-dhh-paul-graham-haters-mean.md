---
title: "12.12 — DHH, Paul Graham, Haters, Mean People Fail"
description: "DHH et Paul Graham dans le manifeste : pourquoi les essais Haters et Mean People Fail sont le précédent intellectuel direct du chapitre Premiers retours."
weight: 12
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 12
---

# 12.12&nbsp;—&nbsp;DHH, Paul Graham, _Haters_, _Mean People Fail_

> Le Holy Book cite deux grands noms&nbsp;: **David Heinemeier Hansson (DHH)** et **Paul Graham (pg)**. Ces deux auteurs ne sont pas cités au hasard, chacun incarne une **posture rhétorique** précise. Ce fichier explique qui ils sont, ce qu'ils ont écrit, et pourquoi l'essai _Haters_ de Paul Graham (et son frère cadet _Mean People Fail_) sont le _précédent intellectuel_ direct du chapitre «&nbsp;_Premiers retours_&nbsp;».

## 1. David Heinemeier Hansson (DHH)

### Identité

| Champ            | Valeur                                                                                                          |
| ---------------- | --------------------------------------------------------------------------------------------------------------- |
| Nom complet      | **David Heinemeier Hansson**                                                                                    |
| Né               | **15 octobre 1979**, Copenhague (Danemark)                                                                      |
| Pseudo           | **DHH**                                                                                                         |
| Société          | _Co-owner_ et CTO de **37signals** (rejoint en 2001 comme _contractor_, _co-owner_ depuis)                      |
| Œuvre majeure    | **Ruby on Rails** (2003-2004)&nbsp;—&nbsp;framework web Ruby                                                    |
| Twitter /&nbsp;X | [`@dhh`](https://x.com/dhh)                                                                                     |
| Blog             | [`world.hey.com/dhh`](https://world.hey.com/dhh)                                                                |
| Livres           | _Rework_ (2010), _Remote_ (2013), _It Doesn't Have to Be Crazy at Work_ (2018), tous co-écrits avec Jason Fried |

### Trajectoire

| Année     | Événement                                                                                                                                                    |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1999      | 37signals (initialement studio de design web)                                                                                                                |
| 2003      | DHH rejoint comme contractor part-time pour écrire Basecamp                                                                                                  |
| 2004      | **Release de Ruby on Rails** depuis le code de Basecamp                                                                                                      |
| 2005      | DHH élu _Hacker of the Year_ par OSCON                                                                                                                       |
| 2010      | _Rework_, livre best-seller                                                                                                                                  |
| 2014      | Conférence _The Distributed Future of Work_&nbsp;—&nbsp;manifeste pré-pandémie                                                                               |
| 2020      | _Hey_, alternative email à Gmail                                                                                                                             |
| 2021      | Affaire publique&nbsp;:&nbsp;conflit interne 37signals sur la politique d'entreprise. DHH écrit sa _politique sans-politique_.                               |
| 2022      | **«&nbsp;_I won't let you pay me for my open source_&nbsp;»**&nbsp;—&nbsp;refuse explicitement les sponsorships GitHub                                       |
| 2023      | **Sortie du cloud**. _Annonce que 37signals quitte AWS_ et revient au _bare metal_, économisant 7&nbsp;M$ sur 5 ans. Lance la suite **ONCE** (auto-hébergé). |
| 2024-2026 | Continue à pamphlétiser publiquement contre le _SaaS gospel_, la _vendoritis_, le DEI obligatoire, les conventions corporate.                                |

### Posture

- **Anti-cloud**&nbsp;:&nbsp;revenir à un serveur loué chez Hetzner ou un data center est _supérieur_ à AWS dans 90&nbsp;% des cas. Le _cloud_ est une **rente** vendue comme _innovation_.
- **Anti-SaaS d'agence**&nbsp;:&nbsp;_Hey_, _ONCE_, et _Campfire_ sont vendus en _licence perpétuelle_, pas en abonnement.
- **Anti-monorepo monstrueux**&nbsp;:&nbsp;Basecamp est explicitement un _Majestic Monolith_, contre la mode des micro-services.
- **Anti-conformisme social en entreprise**&nbsp;:&nbsp;refus de débattre de politique interne pendant les heures de travail.
- **Pro-Open Source authentique**&nbsp;:&nbsp;Rails est MIT, et DHH _refuse l'argent_ qu'on lui propose pour le maintenir&nbsp;—&nbsp;c'est sa déclaration que _le code donné est donné_, pas un produit déguisé en don.

### Pourquoi le Holy Book cite «&nbsp;_I won't let you pay me for my open source_&nbsp;»

> «&nbsp;_I won't let you pay me for my open source&nbsp;—&nbsp;Fuck You_&nbsp;»  
> —&nbsp;DHH, [`world.hey.com/dhh/i-won-t-let-you-pay-me-for-my-open-source-d7cf4568`](https://world.hey.com/dhh/i-won-t-let-you-pay-me-for-my-open-source-d7cf4568)

Ce post de DHH dit en substance&nbsp;:

1. Open source&nbsp;=&nbsp;un don. Pas un service. Pas un produit.
2. Si vous _payez_ le mainteneur, vous transformez le don en transaction.
3. La transaction crée une **dette d'obligation**&nbsp;:&nbsp;le mainteneur doit maintenir, faire du support, fix, écouter les besoins du _payeur_.
4. Mieux vaut **garder ça comme un don** et que le mainteneur conserve sa **liberté**.

C'est exactement la position d'Ocarina aussi&nbsp;:

- Ocarina est **MIT**.
- Il n'y a pas de **GitHub Sponsors**, pas de **OpenCollective**, pas de Patreon.
- L'auteur ne demande **rien** en échange du code.
- Et il **garde sa liberté éditoriale totale**.

Le Holy Book invoque DHH parce que DHH est le seul créateur de framework grand-public (Rails est utilisé par GitHub, Shopify, Airbnb) à avoir _explicitement refusé_ la monétisation de son don. C'est un précédent rare.

## 2. Paul Graham (pg)

### Identité

| Champ               | Valeur                                                                                                                                                      |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nom                 | **Paul Graham**                                                                                                                                             |
| Né                  | **13 novembre 1964**, Weymouth (Angleterre)                                                                                                                 |
| Carrière académique | PhD en Computer Science, Harvard, 1990. Thèse&nbsp;:&nbsp;_The State of a Program and Its Uses_.                                                            |
| Diplôme art         | RISD (Rhode Island School of Design)&nbsp;—&nbsp;peinture                                                                                                   |
| Œuvre logicielle    | **Viaweb** (1995, premier éditeur de boutique en ligne web-based). Racheté par **Yahoo** en 1998&nbsp;→&nbsp;devient Yahoo Store. Écrit en **Common Lisp**. |
| Fondation           | **Y&nbsp;Combinator** (2005, avec Jessica Livingston, Robert Morris, Trevor Blackwell)&nbsp;—&nbsp;incubateur de startups                                   |
| Œuvres écrites      | _On Lisp_ (1993), _ANSI Common Lisp_ (1995), _Hackers and Painters_ (2004), 100+ essais sur [`paulgraham.com`](https://paulgraham.com)                      |
| Twitter /&nbsp;X    | [`@paulg`](https://x.com/paulg)                                                                                                                             |

### Trajectoire

- **Hackers and Painters** (2004)&nbsp;—&nbsp;le manifeste fondateur de _Y&nbsp;Combinator_. Thèse&nbsp;:&nbsp;les bons hackers pensent comme des artistes (peintres), pas comme des ingénieurs (architectes).
- **Y&nbsp;Combinator**&nbsp;:&nbsp;modèle d'incubation par _batches_, devenu standard mondial. A produit Stripe, Airbnb, Dropbox, Reddit, Twitch, Coinbase, Instacart, DoorDash.
- Step-back en 2014&nbsp;:&nbsp;passe la main de YC à **Sam Altman**. Continue à écrire des essais.
- 2018-2026&nbsp;:&nbsp;essais plus _philosophiques_ («&nbsp;_Identity_&nbsp;», «&nbsp;_Cities and Ambition_&nbsp;», «&nbsp;_Mind the Gap_&nbsp;», «&nbsp;_Wealth_&nbsp;»).

### Posture

- **Schemer-Lisper de cœur**&nbsp;:&nbsp;continue de défendre Common Lisp comme «&nbsp;_le langage qui a 30 ans d'avance_&nbsp;» bien après que la mode soit passée.
- **Anti-corporate**&nbsp;:&nbsp;_Hackers and Painters_ est en grande partie un argument contre le travail _en entreprise_. Le **hacker** est défini par opposition au _suit_.
- **Pro-founder**&nbsp;:&nbsp;le founder a toujours raison parce qu'il _porte_ le risque. Les VC qui imposent leur direction se trompent presque toujours.
- **Pro-essai**&nbsp;:&nbsp;Paul Graham défend l'**essai** comme forme intellectuelle. Sa thèse&nbsp;:&nbsp;on _pense en écrivant_, pas avant d'écrire.
- **Anti-haters** (cf. _Mean People Fail_, ci-dessous).

## 3. _Haters_ (Paul Graham, mai 2014)

URL&nbsp;:&nbsp;[`paulgraham.com/fh.html`](https://paulgraham.com/fh.html) (lit. _"For Haters"_, abrégé `fh.html`).

### Thèse

> _Hatred is by far the most common motive for hostile online comments._

Paul Graham distingue&nbsp;:

| Catégorie | Description                                                                      |
| --------- | -------------------------------------------------------------------------------- |
| _Critic_  | Quelqu'un qui désapprouve _ce que tu fais_ et l'argumente                        |
| _Hater_   | Quelqu'un qui te _hait personnellement_ et utilise ce que tu fais comme prétexte |

Les _haters_ sont reconnaissables&nbsp;:

- Ils sont **systématiquement négatifs** sur tout ce que tu fais.
- Ils sont **factuellement imprécis**&nbsp;—&nbsp;ils inventent ce qu'ils n'aiment pas.
- Ils sont **frustrés** dans leur propre vie (succès personnel faible, statut social bas).
- Ils _souffrent_ de ton existence comme d'une **insulte personnelle**.

### Pourquoi ils existent

Paul Graham dit&nbsp;:

1. La personne attaquée _réussit_ à un certain truc (création, _fame_, projet)
2. Le _hater_ est juste un _fanboy_ monté en sens inverse

### Conclusion de l'essai

> _The exhortation isn't to ignore haters, but to recognize them as a side effect of doing anything._

Si tu fais un truc qui marche, les _haters_ apparaissent **par construction**. Leur existence est le _coût_ du succès, pas un signe que tu as fait quelque chose de mal.

### Pourquoi le Holy Book cite _Haters_

Le chapitre «&nbsp;_Premiers retours_&nbsp;» du Holy Book documente précisément ce type de feedback.

Igor Casanova **renvoie** au texte de Paul Graham parce que c'est le **précédent canonique**&nbsp;:&nbsp;les _haters_ d'Ocarina, de la programmation fonctionnelle, de l'IA, du code réellement KISS, sont l'instance d'un phénomène général, déjà théorisé par un auteur respecté de la scène _hacker-fondateur_.

## 4. _Mean People Fail_ (Paul Graham, novembre 2014)

URL&nbsp;: [`paulgraham.com/mean.html`](https://paulgraham.com/mean.html)

### Thèse

> _It struck me recently how few of the most successful people I know are mean. There are exceptions, but remarkably few._

1. Internet nous a montré jusqu'à quel point certaines personnes peuvent être purement _méchantes_
2. Bien qu'il y ait une grande quantité de connards dont on était épargné jusqu'alors et qu'ils sont à présent visibles, on remarque qu'ils n'existent pas vraiment davantage auprès des personnes qui ont réussi dans leur vie
3. Les _gnomes bêtes et méchants_ (reformulation personnelle) sont généralement peu brillants pour faire décoller une startup
4. Être méchant pousse à être stupide, à se bagarrer plutôt qu'à faire son travail, et épuise tout le monde pour rien
5. Les personnes méchantes n'attirent pas à elles les meilleurs talents, plutôt des personnes qui ont _besoin d'un job_
6. Les personnes qui ont davantage envie de rendre le monde meilleur qu'envie de faire de l'argent ont un taux de succès plus élevé
7. Le monde passe selon lui d'un jeu à somme nulle où chacun se bat pour s'accaparer des denrées rares à un jeu où l'on _gagne_ en ayant de bonnes idées et en créant de nouvelles choses
8. Il insiste en disant que l'environnement doit être sain pour que l'on puisse jouer à un jeu constructif plutôt que de faire la guerre ou se dire que son gouvernement est là pour tout piller
9. Paul Graham et sa femme, Jessica, travaillent dur pour éduquer leurs enfants à ne pas être méchants&nbsp;;&nbsp;ils tolèrent le bruit, le bazar et la _junk food_, mais pas la méchanceté. Parce qu'être méchant ne peut mener qu'à échouer.

> «&nbsp;_22 years, I could never be a hater, 22 blunts in this game I'm a player._&nbsp;»

[_Yung Innanet, icecoldwater, Soundcloud_](https://soundcloud.com/queed-inc/icecoldwater)

### Pont vers _Haters_

Paul Graham redirige vers _Mean People Fail_ depuis _Haters_.

## 5. Mise en regard&nbsp;:&nbsp;DHH vs Paul Graham

| Axe                              | DHH                                                                                                                                                                                             | Paul Graham                                                   |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Génération                       | 1979&nbsp;—&nbsp;second wave indie                                                                                                                                                              | 1964&nbsp;—&nbsp;first wave hacker-founder                    |
| Langage de référence             | Ruby                                                                                                                                                                                            | Lisp                                                          |
| Modèle                           | Founder _qui exécute_ (Basecamp, Hey, ONCE)                                                                                                                                                     | Founder _qui théorise_ (essais, YC)                           |
| Posture argumentative            | Pamphlétaire, frontal, twitter-bagarre                                                                                                                                                          | Essayiste, distant, structurel                                |
| Bête noire                       | Le cloud, le SaaS extractif                                                                                                                                                                     | Les VC corporate, les _suits_                                 |
| Refuse                           | Sponsorships open source, conventions DEI                                                                                                                                                       | Big company, _committee_                                      |
| Auto-empoyé                      | Oui (37signals&nbsp;=&nbsp;sa boîte)                                                                                                                                                            | Oui (YC&nbsp;=&nbsp;sa boîte)                                 |
| Lecture du «&nbsp;_hater_&nbsp;» | _Ruby on Rails: The Documentary_ débute par une citation&nbsp;:&nbsp;«&nbsp;_Let the dog barks, Sancho. It's a sign we are moving forward._&nbsp;» **Exactement comme le Holy Book le formule** | «&nbsp;_Comprends le mécanisme et passe à autre chose_&nbsp;» |

Le Holy Book reprend **les deux** parce qu'il _est_ les deux&nbsp;:&nbsp;pamphlétaire à la DHH si ce n'est plus, essayiste à la Paul Graham.

## 6. Ruby on Rails: The Documentary

Voir aussi&nbsp;:&nbsp;[Ruby on Rails: The Documentary, YouTube](https://www.youtube.com/watch?v=HDKUEXBF3B4)

## 7. Filiation dans le manifeste Ocarina

Citation directe&nbsp;:

> _Lire aussi&nbsp;:&nbsp;«&nbsp;Haters&nbsp;», par Paul Graham._

Citation directe&nbsp;:

> «&nbsp;_I won't let you pay me for my open source&nbsp;—&nbsp;Fuck You_&nbsp;»

Et plus ironique encore, Y&nbsp;Combinator tire son nom du _combinateur&nbsp;Y_, un concept central du _λ-calcul_.  
Paul Graham est également un grand adepte du _Lisp_, qui est l'un des langages les plus iconiques du monde de la _programmation fonctionnelle_.

Quant à Ruby, le langage de programmation de prédilection de DHH, il s'agit aussi d'un langage qui a beaucoup été inspiré de Smalltalk, ainsi que de Lisp, avant les autres (Java, C++, PHP, etc.).

## 8. Connexions avec le reste du précis

- Citation #11 (_Haters_) dans [`01-sourced-citations.md`](01-sourced-citations.md)
- Citation #12 (_I won't let you pay me for my open source_) dans [`01-sourced-citations.md`](01-sourced-citations.md)
- Posture politique générale&nbsp;: [`../01-philosophy/05-political-stance.md`](../01-philosophy/05-political-stance.md)
- Refus du SaaS&nbsp;: [`11-saas-arr-fraud.md`](11-saas-arr-fraud.md)
