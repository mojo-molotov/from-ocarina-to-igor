---
title: "Chapitre 12 — Analyse du manifeste"
weight: 13
date: 2026-05-20
tags: ["analyse-manifeste"]
sidebar:
  open: true
---

# Chapitre 12&nbsp;—&nbsp;Analyse du manifeste

> Le Holy Book d'Ocarina est plus qu'une documentation technique&nbsp;:&nbsp;c'est un **manifeste**. Ce chapitre dépile toutes ses citations sourcées, retrace les sous-cultures derrière, et explique le mouvement de fond qu'elles incarnent.
>
> On ne lit pas Ocarina comme un framework qu'on adopte «&nbsp;_parce qu'il est bien_&nbsp;». On l'adopte parce qu'on a _entendu_ le slogan. Le slogan vient _d'ailleurs_. Le «&nbsp;_d'ailleurs_&nbsp;» est documenté ici.

## Plan

|  #  | Fichier                                                                                  | Sujet                                                                                                                                                                                                                               |
| :-: | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01  | [`01-sourced-citations.md`](01-sourced-citations.md)                                     | Toutes les citations du manifeste, attribuées à leur source.                                                                                                                                                                        |
| 02  | [`02-lulzsec-lulzboat-antisec.md`](02-lulzsec-lulzboat-antisec.md)                       | LulzSec, le Lulzboat, Operation AntiSec, le mouvement AntiSec originel (1999).                                                                                                                                                      |
| 03  | [`03-ytcracker-nerdcore-digital-gangster.md`](03-ytcracker-nerdcore-digital-gangster.md) | YTCracker (Bryce Case Jr.), Nerdcore hip-hop, Digital Gangster forum (2005), NASA 1999.                                                                                                                                             |
| 04  | [`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)                                         | Zone-H (Roberto Preatoni «&nbsp;_Sys64738_&nbsp;», 2002), defacements archive, IRC /&nbsp;EFnet comme tissu d'infrastructure.                                                                                                       |
| 05  | [`05-indonesian-hackers.md`](05-indonesian-hackers.md)                                   | YogyaCarderLink, le contexte 1998 (émeutes anti-chinoises, cyber-guerre chinoise), début années 2000 des indonésiens.                                                                                                               |
| 06  | [`06-yung-innanet-vxug.md`](06-yung-innanet-vxug.md)                                     | Yung Innanet (kayos), sysadmin originel de VX Underground, citation tirée de sa musique, décès 18/10/2025 (RIP, sincèrement, mon Héros... _talented and beloved_).                                                                  |
| 07  | [`07-underlying-movement.md`](07-underlying-movement.md)                                 | Le mouvement de fond&nbsp;: hackers qui se sont reconstruits seuls par la Recherche, la «&nbsp;_famille_&nbsp;», l'éthique, «&nbsp;_we don't sleep_&nbsp;».                                                                         |
| 08  | [`08-ocarina-in-testing-industry.md`](08-ocarina-in-testing-industry.md)                 | Ce qu'Ocarina représente pour l'industrie du test&nbsp;: le _shift_, la longueur d'avance.                                                                                                                                          |
| 09  | [`09-ecosystem-coherence.md`](09-ecosystem-coherence.md)                                 | Comment chaque dépôt incarne la même philosophie. La cohérence n'est pas un accident.                                                                                                                                               |
| 10  | [`10-infopreneurs-tugan-bara-ai.md`](10-infopreneurs-tugan-bara-ai.md)                   | Mouvement infopreneur, copywriting, Tugan Bara (Arnaud Labossière), pourquoi l'IA casse cet écosystème malsain, pourquoi c'est une bonne chose.                                                                                     |
| 11  | [`11-saas-arr-fraud.md`](11-saas-arr-fraud.md)                                           | L'industrie SaaS, _cross-subscription rings_, fraude `ARR = MRR × 12`, jeu de dupes LP&nbsp;/&nbsp;VC&nbsp;/&nbsp;founder, pourquoi Ocarina refuse le SaaS.                                                                         |
| 12  | [`12-dhh-paul-graham-haters-mean.md`](12-dhh-paul-graham-haters-mean.md)                 | Qui est **DHH**, qui est **Paul Graham**, lecture de _Haters_ et _Mean People Fail_, pourquoi le Holy Book s'en réclame.                                                                                                            |
| 13  | [`13-lambda-calculus-rop-origins.md`](13-lambda-calculus-rop-origins.md)                 | Lambda-calcul (Church 1936), filière ML, Haskell /&nbsp;OCaml /&nbsp;F#, monades (Moggi, Wadler), formalisation de ROP par Scott Wlaschin (2013).                                                                                   |
| 14  | [`14-real-ai-in-ocarina.md`](14-real-ai-in-ocarina.md)                                   | Ce qu'est l'IA (Transformer 2017, RLHF 2022, Claude 4 2025), et pourquoi Ocarina l'applique _pour de vrai_ vs slogans marketing.                                                                                                    |
| 15  | [`15-typing-ai-rl-probes.md`](15-typing-ai-rl-probes.md)                                 | Pourquoi le typage strict + ISTQB + RL + _probes_ rendent un LLM productif. Empirique avant assertif. Pourquoi pas exécuter quand l'IA génère un dataset.                                                                           |
| 16  | [`16-underground-internet-2000s.md`](16-underground-internet-2000s.md)                   | L'internet souterrain de 1995-2010&nbsp;: Usenet, BBS, IRC, doxing, swatting, SIP spoofing, false-flags, malwares, ViolVocal, 4chan, BOFH (Travaglia), Shodan, forums marchands.                                                    |
| 17  | [`17-survivor-psyche-programming.md`](17-survivor-psyche-programming.md)                 | Psyché du survivant&nbsp;: pourquoi «&nbsp;_ennemis_&nbsp;», «&nbsp;_narcissisme_&nbsp;», «&nbsp;_enfer_&nbsp;», «&nbsp;_survie_&nbsp;», «&nbsp;_yeux partout_&nbsp;», et comment ces adaptations s'inscrivent jusque dans le code. |
| 18  | [`18-villains-defcon-ocarina-ideology.md`](18-villains-defcon-ocarina-ideology.md)       | Philosophie «&nbsp;_Vilains but not Monsters_&nbsp;», DEF CON, «&nbsp;_Live as a white hat, or die as a black hat_&nbsp;» (YTCracker), pourquoi Ocarina est une **idéologie**, pas un OVNI.                                         |

## Pourquoi la culture&nbsp;?

Lire `02-ocarina/*` sans avoir lu ceci, c'est comprendre _l'instrument_ sans en entendre la _partition_. La technique d'Ocarina (ROP, types, paresse, composition) est cohérente parce qu'elle est animée par une **éthique**. Cette éthique n'est pas un préambule décoratif&nbsp;:&nbsp;elle est ce qui a écarté chaque feature, chaque DSL, chaque raccourci alternatif. Et cette éthique vient d'une scène, la scène hackers historique des années 1999-2011, que ce chapitre cartographie.

## Lectures connexes

- Le Holy Book (chapitres «&nbsp;_Premiers retours_&nbsp;» et «&nbsp;_Qu'est donc Ocarina&nbsp;?_&nbsp;»).
- Les influences déjà cataloguées en surface&nbsp;: [`../01-philosophy/04-citations-and-influences.md`](../01-philosophy/04-citations-and-influences.md)
- La posture politique générale&nbsp;: [`../01-philosophy/05-political-stance.md`](../01-philosophy/05-political-stance.md)
