---
title: "12.02 — LulzSec, le Lulzboat, AntiSec"
description: "Trois sujets distincts : (1) LulzSec en tant que groupe, (2) le Lulzboat en tant que métaphore identitaire, (3) AntiSec en tant que mouvement (deux versions : 1999 et 2011). Le Holy Book les invoque d'un même souffle ; ils ont chacun leur histoire."
weight: 2
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 2
---

# 12.02&nbsp;—&nbsp;LulzSec, le Lulzboat, AntiSec

> Trois sujets distincts&nbsp;: (1) **LulzSec** en tant que groupe, (2) **le Lulzboat** en tant que métaphore identitaire, (3) **AntiSec** en tant que mouvement (deux versions&nbsp;:&nbsp;1999 et 2011). Le Holy Book les invoque d'un même souffle&nbsp;;&nbsp;ils ont chacun leur histoire.

## 1. AntiSec (1999)&nbsp;—&nbsp;le mouvement originel

### Origine

À la fin des années 1990, l'industrie de la sécurité informatique se _professionnalise_&nbsp;:&nbsp;des entreprises naissent autour de la vente de firewalls, d'antivirus, d'audits. Une norme émerge&nbsp;:&nbsp;la **_full disclosure_**, publier publiquement les vulnérabilités, leurs PoC, leurs exploits, avec comme argument que cela force les éditeurs à patcher rapidement.

Une partie de la _communauté underground_ voit dans cette pratique un **business modèle déguisé en éthique**. L'argument ici&nbsp;:&nbsp;la _full disclosure_ ne sert pas la sécurité, elle alimente une économie où l'on _vend la peur_ qu'on a soi-même contribué à créer. Les mêmes acteurs qui publient les exploits sont ceux qui vendent les solutions.

Le mouvement **Anti Security** (`antisec`) naît contre.  
Son principe&nbsp;:

> Pas de full disclosure. Pas d'exploits publics. Les bugs restent dans l'_underground_. Les outils restent privés. Les mailing lists «&nbsp;_Bugtraq_&nbsp;», «&nbsp;_full-disclosure_&nbsp;», «&nbsp;_vuln-dev_&nbsp;», «&nbsp;_vendor-sec_&nbsp;» sont considérées comme des _ennemis_.

Cibles déclarées de l'_AntiSec movement_ originel&nbsp;:

- Sites&nbsp;: **SecurityFocus**, **SecuriTeam**, **Packet Storm**, **milw0rm**.
- Mailing lists&nbsp;: **`full-disclosure`**, **`vuln-dev`**, **`vendor-sec`**, **`Bugtraq`**.
- Forums IRC publics où les exploits circulent ouvertement.

Source&nbsp;: [Antisec Movement&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/Antisec_Movement)

### Pourquoi ça compte pour Ocarina

L'AntiSec originel **n'a pas gagné**. La _full disclosure_ est devenue la norme. CVE, CVSS, NVD, bug bounty programs&nbsp;:&nbsp;tout le marché s'est aligné sur la position opposée.

Mais l'argument _structurel_, «&nbsp;_cette industrie crée le problème qu'elle vend_&nbsp;», n'a jamais été réfuté. Il est revenu sous d'autres formes (mouvement anti-vendor lock, anti-SaaS, anti-No-Code). Ocarina hérite de cette ligne&nbsp;:&nbsp;refus des _vendors_ de test (_BrowserStack_, _Sauce Labs_, etc.), refus des «&nbsp;_solutions plateforme_&nbsp;», auditabilité du code en _boîte blanche_.

Le Holy Book le formalise (chapitre «&nbsp;_Anti slipologues_&nbsp;»)&nbsp;:

> Pendant trop longtemps, l'informatique a été prise en otage par une minorité, un «&nbsp;_1%_&nbsp;», qui a cru bon de la transformer en terrain de jeux pour initiés.

Cette «&nbsp;_minorité_&nbsp;» est, _grosso modo_, le complexe industriel anti-AntiSec. La _full disclosure_ moderne est son outil. Ocarina est né contre.

## 2. LulzSec (mai – juin 2011)&nbsp;—&nbsp;50 jours de chaos

### Origine

**Lulz Security** (LulzSec) naît en mai 2011, _splinter group_ d'Anonymous. Six membres principaux&nbsp;:

| Pseudo       | Identité          | Rôle                                                          |
| ------------ | ----------------- | ------------------------------------------------------------- |
| **Sabu**     | Hector Monsegur   | Leader, devenu informateur FBI dès juin 2011 (révélé en 2012) |
| **Topiary**  | Jake Davis        | Spokesperson, écriture des communiqués                        |
| **Kayla**    | Ryan Ackroyd      | Exploits techniques                                           |
| **Tflow**    | Mustafa Al-Bassam | Exploits, dev                                                 |
| **AVUnit**   | jamais identifié  | &nbsp;—&nbsp;                                                 |
| **pwnsauce** | Darren Martyn     | &nbsp;—&nbsp;                                                 |

50 jours d'attaques touchant les secteurs publics, médiatiques, et de l'_entertaining_&nbsp;:

- **PBS** (mai 2011), fake news «&nbsp;_Tupac alive in New Zealand_&nbsp;» sur le site _Newshour_, en représailles d'un documentaire WikiLeaks défavorable de _Frontline_.
- **Sony Pictures**, dump massif de la base utilisateurs, après la débâcle PSN.
- **CIA.gov**, DDoS.
- **Fox**, leak du X Factor contestant DB.
- **US Senate**, site infiltré.
- **InfraGard Atlanta** (partenaire FBI), dump des _credentials_.
- **HBGary Federal** (partenaire FBI), dump des _credentials_, attaque menée sous bannière Anonymous, avant la formation de LulzSec.

Sources&nbsp;: [LulzSec&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/LulzSec), [Operation AntiSec&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/Operation_AntiSec)

### Le Manifeste LulzSec (juin 2011)

À leur 1000ème tweet, LulzSec publie un manifeste&nbsp;:

> «&nbsp;_We're not, only because we don't have to be. (...) We release personal data so that equally evil people can entertain us with what they do with it._&nbsp;»

_Nihiliste assumé_, esthétisé. Le hack pour le «&nbsp;_lulz_&nbsp;», pas pour la conviction politique, pas pour la richesse, pour _l'amusement_ et pour _exhiber_ la fragilité du système.

LulzSec a fait ressusciter le terme **AntiSec** sous une nouvelle bannière&nbsp;:&nbsp;**Operation AntiSec** (juin 2011), en collaboration avec Anonymous. Cibles&nbsp;: gouvernements, organismes de sécurité, mailing lists vuln-dev.

## 3. Le Lulzboat

Le **Lulzboat** est le _bateau pirate_ stylisé de LulzSec, repris partout&nbsp;:

- Bannières Twitter.
- Headers Pastebin&nbsp;:&nbsp;`▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ TheLulzBoat ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄`.
- Communiqués signés «&nbsp;_The Lulz Boat&nbsp;/&nbsp;Lulz Security_&nbsp;».

ASCII art de bateau, Stuart Little&nbsp;/&nbsp;Captain Hook&nbsp;/&nbsp;Nyan Cat.

[![Antisec, The LulzSec Anthem, YTCracker, 2011](/assets/img/antisec-yt-2011.png)](https://www.youtube.com/watch?v=xDyBIpqZcNI)

> «&nbsp;_If you're sittin' below deck /&nbsp;In the Lulzboat, salute, bitch, and show some respect_&nbsp;»
>
> &nbsp;—&nbsp;YTCracker, **`#antisec`** (22 juin 2011), devenu l'hymne officiel de l'_Operation AntiSec_.

La phrase est citée _telle quelle_ dans le Holy Book d'Ocarina&nbsp;:

> «&nbsp;_In the Lulzboat, salute, bitch, and show some respect._&nbsp;»

C'est un **mot de passe générationnel.**

### YTCracker et LulzSec

YTCracker (Bryce Case Jr.) est extérieur à LulzSec _stricto sensu_, il n'était pas dans les 6 membres, mais il était **associé**&nbsp;:

- Il connaissait personnellement plusieurs membres.
- Il a écrit `#antisec` _pendant_ l'opération.
- Sa chanson a été utilisée par Anonymous&nbsp;/&nbsp;LulzSec dans leurs vidéos de communiqués.

Cf. [`03-ytcracker-nerdcore-digital-gangster.md`](03-ytcracker-nerdcore-digital-gangster.md) pour le détail concernant YTCracker.

## 4. La fin (juin 2011&nbsp;→&nbsp;mars 2012)

La nuit du 25 au 26 juin 2011, LulzSec publie **«&nbsp;_50 days of lulz_&nbsp;»**, leur communiqué de dissolution&nbsp;:

> «&nbsp;_For the past 50 days we've been disrupting and exposing corporations, governments, often the general population itself, and quite possibly everything in between, just because we could._&nbsp;»

Six mois plus tard, en mars 2012, le DoJ américain inculpe cinq des six membres.  
Sabu collaborait avec le FBI depuis juin 2011, il a balancé.

Source&nbsp;:&nbsp;[LulzSec finally calls it quits&nbsp;—&nbsp;GeekBurn](https://geekburn.wordpress.com/2011/06/26/lulzsec-finally-calls-it-quits-after-50-days-of-mayhem/)

## 5. Rhétorique «&nbsp;_`Don't fuck with us.`_&nbsp;»&nbsp;→&nbsp;«&nbsp;_`YOU FUCKED WITH US!`_&nbsp;»

Le mantra **`Don't fuck with us`** vient de la scène _carding/defacement_ originelle (cf. [`05-indonesian-hackers.md`](05-indonesian-hackers.md), où l'on documente sa présence systématique sur les pages de deface de **YogyaCarderLink**). LulzSec et Anonymous en **héritent**&nbsp;:&nbsp;c'est ce qui a structuré l'ensemble de la scène _grey hat_ des années 2000s avant d'être repris par les opérations en 2010-2012.

| Temps grammatical                                             | Effet                                                                      |
| ------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **`Don't fuck with us.`** (futur conditionnel, avertissement) | Posture _défensive_. _On ne fait rien tant que vous ne nous attaquez pas._ |
| **`YOU FUCKED WITH US!`** (déclaration de représailles)       | _On vous avait prévenu, vous l'avez fait quand même, maintenant assumez._  |

Le Holy Book d'Ocarina le formule mot pour mot dans la même langue, toute traduction confondue&nbsp;:

> **YOU FUCKED WITH US!**

Tout le passage d'invective (cf. [`06-yung-innanet-vxug.md`](06-yung-innanet-vxug.md)) n'est pas une agression _gratuite_, c'est une _réponse_ tardive et explosive à des années de pressions. C'est l'adaptation au contexte d'un auteur de _frameworks_ qui s'est fait dicter pendant des années comment _il devrait_ écrire son code.

Ces codes des «&nbsp;_deux temps_&nbsp;» sont **universels dans cette scène**. On les retrouve dans&nbsp;:

- Les defaces de YogyaCarderLink (signature `Don't fuck with us.` en bas de page).
- Les pastebins post-HBGary (_Anonymous_, février 2011).
- Les communiqués de LulzSec de représailles (_Operation Payback_&nbsp;—&nbsp;RIAA, MPAA, puis défense de WikiLeaks).
- Les communiqués Lulz Boat de réponse aux arrestations.

## 6. Filiation avec Ocarina

Ocarina ne se présente _évidemment_ pas comme un projet hacker au sens 2011. Il est en MIT, hébergé sur GitHub, ne casse rien. Mais il **hérite**&nbsp;:

| Trait LulzSec /&nbsp;AntiSec                 | Trait Ocarina                                             |
| -------------------------------------------- | --------------------------------------------------------- |
| Refus de la professionalisation comme valeur | Refus du «&nbsp;_plugin pytest_&nbsp;» et des écosystèmes |
| Refus de la full disclosure comme business   | Une seule dep d'exécution, code auditable                 |
| _Identité de groupe_ revendiquée             | «&nbsp;_C'est ma voiture_&nbsp;»                          |
| Rhétorique directe, sans politesse           | «&nbsp;_Fuck You. Pas compliqué._&nbsp;» (DHH)            |
| Esthétique _underground_                     | Illustrations IA, ton pamphlétaire                        |
| _Lulz_ comme tonalité                        | Humour permanent dans le Holy Book                        |

Ocarina est ce que ces gens font **20 ans plus tard**, quand ils écrivent un framework de test pendant la journée. C'est la même éthique, dans un autre médium.
