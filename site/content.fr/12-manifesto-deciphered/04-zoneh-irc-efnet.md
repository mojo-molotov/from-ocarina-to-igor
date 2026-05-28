---
title: "12.04 — Zone-H, IRC, EFnet"
description: "Zone-H, IRC et EFnet : trois infrastructures de la scène hackers 1998-2012, dont un seul mot dans le manifeste ouvre toute une culture."
weight: 4
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 4
---

# 12.04&nbsp;—&nbsp;Zone-H, IRC, EFnet

> Trois infrastructures sans lesquelles la scène hackers 1998-2012 n'aurait jamais été la même&nbsp;: **Zone-H** (archive de defaces), **IRC**, **EFnet** (le réseau IRC historique). Le Holy Book ne cite Zone-H qu'une fois, mais c'est un mot-clé qui ouvre toute une infrastructure.

## 1. Zone-H&nbsp;—&nbsp;archive des defaces (2002&nbsp;→&nbsp;aujourd'hui)

### Fondation

- **Date**&nbsp;:&nbsp;2 mars 2002.
- **Siège**&nbsp;:&nbsp;Estonie.
- **Fondateur**&nbsp;:&nbsp;**Roberto Preatoni** (alias **`Sys64738`**).
- **URL**&nbsp;:&nbsp;[`zone-h.org`](https://zone-h.org)

### Fonction

1. Un attaquant deface un site (remplace la homepage par sa propre version, signée).
2. L'attaquant (ou un témoin) soumet l'URL à Zone-H.
3. Zone-H modère&nbsp;:&nbsp;vérifie que le deface est authentique.
4. Si OK&nbsp;:&nbsp;le site défiguré (_deface_) est **archivé pour toujours** sur Zone-H (snapshot du HTML+CSS+assets).
5. L'auteur du deface signe avec son alias. Le sourçage est public.

### Impact

Pendant 10-15 ans, Zone-H a été **le tableau d'affichage public** de la scène _grey hat_ mondiale. Chaque deface notable était archivé. Pour un _script kiddie_, monter dans le classement Zone-H était _le_ but pour _prouver_&nbsp;:

- _Single defacements_&nbsp;:&nbsp;nombre brut.
- _Mass defacements_&nbsp;:&nbsp;deface _n_ sites en une attaque (script de masse&nbsp;+&nbsp;faille commune).
- _Special defacements_&nbsp;:&nbsp;sites gouvernementaux, .mil, banques.

### Roberto Preatoni&nbsp;—&nbsp;_Sys64738_

L'alias **`Sys64738`** est une référence au _Commodore 64_&nbsp;:&nbsp;`SYS 64738` était la commande BASIC pour faire un soft reboot d'un C64. Hommage typique de la génération qui a grandi à la fin des années 1980.

Preatoni a eu une carrière en demi-teinte&nbsp;:

- Fondateur de **WabiSabiLabi** (2007), marketplace controversé de vulnérabilités 0day (concept ambitieux, exécution catastrophique).
- Arrêté le **5 novembre 2007** dans le cadre du scandale d'espionnage Telecom Italia&nbsp;:&nbsp;son ancienne société avait été engagée par la division sécurité de Telecom Italia en 2003-2004, et les membres de l'équipe ont été inculpés d'écoutes illégales et d'accès non autorisé à des systèmes informatiques.
- Conférencier régulier à la **DEF CON** et **HITBSecConf**.

Sources&nbsp;:&nbsp;[Zone-H&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/Zone-H), [Roberto Preatoni /&nbsp;Sys64738&nbsp;—&nbsp;InfoConDB](https://infocondb.org/presenter/roberto-preatoni-sys64738)

### Pourquoi le Holy Book le cite

> _Voilà qui nous sommes&nbsp;: de Zone-H à une vie rangée._

- **Zone-H**&nbsp;=&nbsp;l'avant. L'âge du deface, du jeu, des risques pénaux, des _crews_ IRC.
- **«&nbsp;_une vie rangée_&nbsp;»**&nbsp;=&nbsp;l'après. Le salariat, le freelance, le SaaS, les conférences, les certifications.

Le pont entre les deux n'a pas été fait par toute la scène. Beaucoup sont restés black hat (et ont fini en prison, ou sont morts). Beaucoup ont décroché complètement. Une minorité a basculé en _white hat_ (la trajectoire de YTCracker). Et une autre minorité a pris une autre voie &nbsp;:&nbsp;**la Recherche**.

## 2. IRC&nbsp;—&nbsp;le protocole qui a tout porté

### Définition

**IRC** = _Internet Relay Chat_, protocole de chat textuel multi-utilisateurs en client/serveur, inventé en 1988 par Jarkko Oikarinen. RFC 1459 (1993).

[INTERNET RELAY CHATTER FATES, Jewbird](https://soundcloud.com/birdneststream/internt-relay-chatter-fates)

```
                   ┌─────────────┐
                   │ client IRC  │ (mIRC / irssi / weechat / X-Chat / ...)
                   └─────┬───────┘
                         │ TCP 6667 (ou 6697 SSL)
                         ▼
                   ┌─────────────┐
                   │ serveur IRC │
                   └─────┬───────┘
                         │
                         │ inter-server links (mesh)
                         ▼
                   ┌───────────────────────────┐
                   │ Network = N serveurs liés │
                   │ (EFnet, IRCnet, Undernet, │
                   │  DALnet, freenode, etc.)  │
                   └───────────────────────────┘
```

### Pourquoi central pour la scène hackers

Entre 1993 et 2012, IRC était _le_ médium social des hackers&nbsp;:

- Discussions techniques en temps réel.
- Coordination de defaces (channels privés).
- Distribution de _0day_ et _warez_.
- Recrutement de _crews_.
- Recevoir une _invitation_ à un channel privé était une marque de reconnaissance.

Pas de logs publics (sauf si quelqu'un loggait et publiait).  
Pas de modération centralisée.  
Pas de pub.

C'était _underground by design_.

### Le déclin

IRC a décliné à partir de 2010 environ, écrasé par&nbsp;:

- **Discord**
- **Slack**
- **Telegram**

Mais une partie de la scène vieille école est restée sur IRC. EFnet, OFTC, Libera.Chat (post-Freenode 2021), TCP&nbsp;DIRECT, EpiKnet, tournent toujours. C'est devenu un _ghost network_, peu de monde, mais ce qui reste est _trié_.

## 3. EFnet&nbsp;—&nbsp;le réseau historique

### Définition

**EFnet** (_Eris-Free Network_) est l'un des plus anciens réseaux IRC encore opérationnels, fondé en 1990.

EFnet était _le_ réseau de la scène _warez_, _zero-day_, _crackers_, _phreakers_ pendant les années 1996-2008. La plupart des channels mémorables, `#hax`, `#exploit`, `#voicebox`, `#carders`, `#legion`, `#vc`, `#2600`, vivaient sur EFnet.

L'identité d'un hacker des années 2000s pouvait souvent se résumer à&nbsp;: «&nbsp;_je traînais sur tel channel sur EFnet, on faisait tel truc_&nbsp;».

Source&nbsp;: [EFnet&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/EFnet)

## 4. IRC dans le Holy Book

| Terme                             | Sens IRC                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Usage dans le Holy Book                                                                                                      |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **`skid`** /&nbsp;_script kiddie_ | Hacker qui exécute des scripts qu'il ne comprend pas                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | «&nbsp;TOI, tu aurais été ce _lamer_, ce gamin qui aurait juste voulu frimer et lancer des PoC trouvés sur Exploit-DB&nbsp;» |
| **`normie`**                      | Utilisateur lambda, non-initié                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | «&nbsp;Putains de _normies_&nbsp;!&nbsp;»                                                                                    |
| **`lamer`**                       | Variante péjorative de skid, plus ancienne                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | id.                                                                                                                          |
| **`rookie`**                      | Nouveau, débutant. Les plus méprisables sont régulièrement utilisés par les communautés _underground_ pour «&nbsp;_porter le chapeau_&nbsp;», ou sont si bêtes qu'ils arrivent à se mettre en défaut tout seuls (s/o _NormalLeVrai_ qui a lamentablement essayé de rançonner une agence étatique à hauteur d'un quignon de pain de 20K avec un anglais et un message d'extorsion dignes d'une rédaction d'élève de CE2, s'est fait recadrer par les autorités comme quoi il «&nbsp;_ferait mieux de se consacrer à sa vie sociale_&nbsp;», et prétexte à présent être un ancien opérateur de ShinyHunters et de LAPSUS$ tout en vendant des «&nbsp;_0-day_, RCE _Zero-Click_ WhatsApp&nbsp;» à 3K alors que c'est le genre de _0-days_ que détiennent le Mossad ou APT29, _bouffon_) | «&nbsp;comme un _rookie_&nbsp;»                                                                                              |
| **`zine`** (=&nbsp;_magazine_)    | Publication _underground_, souvent ASCII (e-zine)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | implicite                                                                                                                    |
| **`crew`**                        | Petit groupe de hackers, intime, soudé                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | «&nbsp;_Nous sommes une vraie FAMILLE&nbsp;!_&nbsp;»                                                                         |

## 5. Le pont avec Ocarina

Même posture _underground_, même refus du _normie_, même _crew_ identitaire (l'auteur _seul contre tous_).

Quand le Holy Book dit&nbsp;:

> _Nous sommes une vraie FAMILLE&nbsp;!_

C'est un _channel IRC_ qui parle. Le «&nbsp;_nous_&nbsp;» est imagé. Il reste impossible à dire «&nbsp;_qui_&nbsp;» est vraiment derrière, et ça le restera pour toujours. Tout ce que l'on peut dire, c'est que c'est très exactement le _ton_ d'un `#channel` privé d'EFnet de 2003.

## 6. Conventions Zone-H /&nbsp;IRC dans sa signature

Le _signing convention_ d'un acteur de Zone-H typique&nbsp;:

```
   ╔══════════════════════════════════════════════════╗
   ║                                                  ║
   ║   H4CK3D BY: <alias>                             ║
   ║   GR33TZ: <other_aliases_du_crew>                ║
   ║                                                  ║
   ║   [ASCII art : skull / dragon / lulz boat]       ║
   ║                                                  ║
   ║   "Citation ici, souvent musicale ou mantra"     ║
   ║                                                  ║
   ╚══════════════════════════════════════════════════╝
```

1. **Le pseudo**.
2. **Les `gr33tz`** (=&nbsp;_greetings_, la liste du _crew_, aussi régulièrement dit en musique sous la forme _shoutout to_). Marque l'inclusion.
3. **Une citation ou un mantra**.

Le Holy Book reproduit _exactement_ cette structure&nbsp;:

```
Built by [@mojo-molotov](https://github.com/mojo-molotov)
Fueled by figatellu and Квас.
```

- Alias&nbsp;: `@mojo-molotov` (typo Markdown ostentatoire).
- _Gr33tz_ implicites&nbsp;:&nbsp;figatellu (saucisse corse, clin d'œil), Квас (boisson russe, autre clin d'œil).
- Citation&nbsp;:&nbsp;remplacée par les citations dispersées dans le Holy Book.

C'est une **signature Zone-H** mise au format README GitHub. Reconnaissance immédiate pour qui sait.
