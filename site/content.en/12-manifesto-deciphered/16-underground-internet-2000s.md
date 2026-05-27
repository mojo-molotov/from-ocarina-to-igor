---
title: "12.16 — The underground internet of 1995-2010: forums, tools, banalization of cruelty"
description: "To understand the rage running through Ocarina's Holy Book, you have to understand what the internet really was before Facebook (2006-2008), before Cloudflare became the gatekeeper (2010+), before moderation was taken seriously. It was a Wild West where state-level capabilities developed in teenagers' bedrooms, where an adversary's privacy could be demolished in 48 hours, and where classical legal recourse was inoperative. This page describes the mechanics, without complacency, without heroization."
weight: 19
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 19
---

# 12.16&nbsp;—&nbsp;The underground internet of 1995-2010: forums, tools, banalization of cruelty

> To understand the rage running through Ocarina's Holy Book, you have to understand **what the internet _really_ was** before Facebook (2006-2008), before Cloudflare became the _gatekeeper_ (2010+), before _moderation_ was taken seriously. It was a _Wild West_ where state-level capabilities developed in teenagers' bedrooms, where an adversary's _privacy_ could be demolished in 48 hours, and where classical legal recourse was **inoperative**. This page describes the mechanics, without complacency, without heroization.

> ⚠️ This page documents **historical techniques** for educational purposes and to contextualize the manifesto. It **does not provide a modus operandi** and **does not endorse** illegal acts. The cruelty described has produced **real victims**.

## 1. Archaeology

### Successive layers

| Period    | Dominant stack                                                                       | Anonymity                                               | Social sphere                          |
| --------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------- | -------------------------------------- |
| 1979-1995 | **Usenet, BBS, FidoNet**                                                             | Strong (pseudo, no traceable user-side IP)              | Small (academics, PC hobbyists)        |
| 1995-2002 | **IRC, Web 1.0, mailing lists, AIM/ICQ**                                             | Strong (proxy chains, dynamic dial-up IP)               | Growing (15-100M users)                |
| 2002-2008 | **phpBB forums, nascent Web 2.0, IRC still central**                                 | Moderate (IRC logs archived, dox even easier)           | Massive (the _general public_ arrives) |
| 2008-2014 | **Facebook + Twitter dominant, IRC and forums declining, 4chan's golden age**        | Low (but 4chan persists with owned anonymity)           | Everyone                               |
| 2014+     | **Smartphone-first, industrialized moderation, _Cloud Act_, _ubiquitous computing_** | Very low (except Tor, except Signal, except no-log VPN) | Saturation                             |

### Usenet (~1979-2002)

**Usenet** is a decentralized system of _newsgroups_: no central server, each server runs by _peering_ with others, messages propagate by replication.

- **Group hierarchy**: `comp.lang.c`, `alt.hacker`, `rec.games.*`, `sci.crypt`, `alt.binaries.*` (warez, scans, etc.).
- **No central moderation**: each server can be cut, but the others replicate.
- **Persistence**: a well-posted Usenet message stays **indefinitely** archived.
- **Killfiles**: the user _moderates themselves_ by ignoring authors.
- **Flame wars**: arguments could last weeks, hundreds of messages, and resurface 10 years later when someone found a thread.

### BBS (Bulletin Board Systems, 1979-mid-1990s)

**BBS** = a dial-up server you connect to with a modem to read/post on themed _boards_. _Local_: no internet, just a phone line from your PC to another teenager's PC bedroom.

It's the **original matrix** of US hacker culture. All the actors documented in this primer (YTCracker, kayos, Sys64738, etc.) passed through there or its direct heirs.

### IRC (Internet Relay Chat, 1988-today)

**IRC** = text chat protocol, multi-channel, multi-server, strongly decentralized. See [`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)

- Thematic channels (`#hack`, `#warez`, `#cracking`, `#defcon`, `#anonymous`...).
- Pseudos modifiable.
- _Ops_ (channel admins) deciding kick/ban.
- _DCC_ (Direct Client-to-Client) to transfer files without going through the server.
- Omnipresent _bots_: `eggdrop`, _channel bots_ watching, kicking _flooders_, sharing files.

## 2. The harmful toolkit

What follows is a **documentary catalog**&nbsp;—&nbsp;each term corresponds to a practice actually common on underground forums of the era.

### Doxing

**Doxing** (from _documents_ → _dox_): publication of all a target's personal info. Legal name, address, phone, employer, parents, children, schools, car plate, social-security numbers, leaked passwords, photos. Regularly garnished with defamation (pedophilia accusations, etc.).

1. _Pivot_ from a unique pseudo to an account on another poorly anonymized forum.
2. _Cross-reference_ available _data leaks_ (_Have I Been Pwned_, _LinkedIn 2012_, _Yahoo 2013_, et al.).
3. _OSINT_ (Open Source Intelligence): aggregating everything public&nbsp;—&nbsp;commercial registry, municipal archives, LinkedIn/Facebook/Instagram profiles, domain _whois_, EXIF-GPS photos.
4. _Social engineering_: calls to telecom carrier support, fake customer service, use of _pretexts_.
5. _Publication_: _doxbin_, pastebin, forums, or equivalent.

**Effect on the victim**: physical harassment (pizza deliveries at best, mass illicit-products orders to trigger a customs alert at worst, fake death notices to relatives, blackmail, etc.), _swatting_, identity theft, employer harassment.

### Swatting

**Swatting**: lying call to law enforcement posing as the victim, a family member, or a spouse, declaring an ongoing hostage-taking or murder at their address, triggering deployment of the **SWAT** (armed assault team).

**Mechanics**:

- Spoofed Caller ID or Skype call with credits obtained via _carding_.
- Voice tone adjusted, credible details (references to the exact address, descriptions of weapons and/or emergency situations).
- Police break down the door, sometimes shoot. There have been **confirmed deaths** following _swattings_ (Andrew Finch, Wichita Kansas, the evening of December 28, 2017, shot at his door, then 28 years old).
- _Cost_ to the victim: major psychological shock, sometimes physical injury, sometimes death.
- _Cost_ to the perpetrator: real prison sentences if identified (Tyler Barriss: 20 years for the Finch swatting).

### Caller ID spoofing via SIP

**SIP** (Session Initiation Protocol) is the standard VoIP protocol since ~2003. With a _low-cost_ SIP provider (overseas, light KYC), you can **send a call** with an **arbitrary** caller ID&nbsp;—&nbsp;any phone number in the world appears on the recipient's display.

Malicious uses:

- Swatting (see above).
- _Voice phishing_ (vishing): impersonating bank customer service.
- Fake emergency calls to a target to force a public reaction.
- Harassing others by impersonating the target's number to provoke score-settling.
- _Caller ID poisoning_: spamming different numbers every hour to saturate the victim.

Legally: **heavily regulated** since 2019 in the US (STIR/SHAKEN), still largely usable from abroad.

### Malware signed on a machine named after the enemy

Operational technique: you _compile_ a malware on a machine whose hostname, username, and build _path_ contain a journalist's, a security researcher's, or a community member's name you want to **humiliate or implicate**. When the malware is analyzed by a sandbox or AV, the build artifacts (string `Built on: /home/journalist_X/...`) hang around the binary and trigger **attribution algorithms** toward the wrong person.

It's a **false flag** operation in the literal sense. Russian **APT** (Advanced Persistent Threat) groups popularized it at state scale (cf. _Olympic Destroyer_, 2018, wrongly attributed to North Korea for months). This **technique** was learned in 2000s underground forums.

### Identity theft + credit subscriptions

With a complete _dox_, one can:

1. Open online bank accounts with the loosest KYC.
2. Subscribe to consumer credit with lax institutions.
3. Make online purchases delivered to _drops_ (third-party addresses).
4. Destroy the victim's _credit score_ by piling up payment defaults.

Consequences for the victim: **years** of paperwork to restore solvency, sometimes a banking ban, sometimes inability to rent an apartment.

### Hacktivism

**Hacktivism** = activism through hacking. Examples:

| Actor                                 | Action                                                              |
| ------------------------------------- | ------------------------------------------------------------------- |
| **Cult of the Dead Cow** (cDc, 1984+) | Back Orifice (1998), Telecomix (Syrian liberations 2011)            |
| **Anonymous** (originated on 4chan)   | Op Chanology (Scientology 2008), Op Tunisia (2011), Op Sony (2011)  |
| **LulzSec** (May-June 2011)           | 50 days of public action, Sony, HBGary, FBI affiliates, Arizona DPS |
| **AntiSec** (2011)                    | Phase of Anonymous + LulzSec                                        |
| **WikiLeaks** (Assange, 2006+)        | Diplomatic cables 2010, Vault 7 (CIA tools) 2017                    |

Hacktivism is **dual**:

- **Public**: actions claimed with manifestos, _Guy Fawkes_-masked videos, communiqués.
- **Backstage**: IRC coordination, internal doxing, infiltrated traitors (Sabu / Hector Monsegur, FBI informant 2011-2012), cross-accusations.

### Swatting + doxing + harassment _combined_

The maximum attack combines all three: you dox the target, call their employer to _reveal_ their past, harass their relatives, _swat_ their home. Publicly documented cases:

- **Brianna Wu, Anita Sarkeesian, Zoë Quinn** (Gamergate, 2014-2015): publicly documented combination.
- **Aaron Swartz** (2010-2013): not swatting but equivalent harassment, suicide January 2013.

### Fake accounts, double accounts, lurk

- **Lurking**: being present on a forum without posting. Lets one **observe** dynamics, spot social vulnerabilities, identify targets, archive evidence.
- **Fake accounts**: account with an invented identity, sometimes maintained for years. Used to _credibilize_ a narrative (false witness, false support).
- **Sockpuppet** / **double account**: several accounts controlled by the same person. Lets one, for example, _reply to oneself_ to create the illusion of consensus.

### Flame, griefers, trolls

| Term        | Meaning                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Flame**   | Virulent insults, often with escalation, triggered by minor disagreement. Can produce a _flame war_ lasting days or more.      |
| **Griefer** | Online player (often MMO, sometimes forums) whose goal is to **ruin** others' experience. Not to win&nbsp;—&nbsp;just to harm. |
| **Troll**   | Shit-stirrer. The original _troll_ is less mean than its descendants, but the evolution is always worse and worse.             |

### DB leaks

**Database leaks**: exfiltration and publication of a complete service database&nbsp;—&nbsp;Ashley Madison (2015), LinkedIn (2012, republished 2016), Yahoo (2013), Adobe (2013), Equifax (2017).

Effect: users of these services see their email + passwords (sometimes plaintext due to poor DB security) + private data **published and indexed**. _Have I Been Pwned_ (Troy Hunt, 2013+) lists 12+ billion records at this point.

### Shodan + cameras and servers

**Shodan** (John Matherly, 2009, [`shodan.io`](https://shodan.io)) is a search engine for **devices connected to the internet**. IP cameras, routers, industrial ICS/SCADA, FTP servers, MQTT servers, _et cetera_:

- `webcamxp` → IP cameras with default web interface, often passwordless.
- `port:23` → open Telnet servers (typically misconfigured IoT).
- `default password` → flags devices identified as using default passwords.

Before Shodan, enumeration required massive, expensive _portscans_. With Shodan, **in 5 seconds**, you have 200 unprotected cameras in any city.

Shodan can also be used for various harassment purposes&nbsp;—&nbsp;detecting poorly secured Minecraft servers to go destroy them "_with griefer friends_".

## 3. BOFH&nbsp;—&nbsp;_Bastard Operator From Hell_ (Simon Travaglia)

**BOFH** is a series of short stories written by **Simon Travaglia** (New Zealand), published on **Usenet** starting in **1992**, then in _Datamation_ and _The Register_.

The narrator is a sysadmin who:

- _Despises_ his users.
- _Sabotages_ annoying coworkers' machines.
- _Falsifies_ logs.
- _Literally kills_ overly tiresome users (with black humor: _elevator accident_, _server-room trap_).
- _Enriches himself_ through internal fraud.

The _BOFH_ became a **cultural archetype**:

- **Known** throughout the sysadmin community.
- **Quotes** integrated into the vocabulary (`PEBKAC` = _Problem Exists Between Keyboard And Chair_, _RTFM_, _ID-10-T error_).
- **Idealized** by sysadmins who ironically identify with it.

Ocarina's author partly inherits this tradition: "_slipologue_" is, in a way, the 2020s version of _PEBKAC_.

In the same vein, also read: [_Master Foo and the Script Kiddie (2003)_](https://rus-linux.net/MyLDP/BOOKS/ArtProgr/script-kiddie.html)

## 4. ViolVocal&nbsp;—&nbsp;the French-speaking case

**ViolVocal** was a **French-speaking community** of organized harassers, active in the 2000s. Forum + voice server (Mumble / TeamSpeak) where members:

- Coordinated **group calls** to targets (rivals, ex-members, anonymous people photographed).
- Used _SIP spoofing_ to call from impersonated numbers.
- Filmed targets' voice reactions and rebroadcast them in public _streams_.
- Practiced **harassment** in the criminal sense: targets harassed for weeks, including minors and vulnerable people.

It's one of the **francophone incarnations** of _no-limit_ culture. VV eventually shut down, some members were identified and prosecuted, but **nothing repaired** the damage done to victims.

**Why mention ViolVocal**: to show that underground cruelty was _not_ an Anglo-only phenomenon. The same mechanics operated in France, on francophone Mumble servers, in francophone MMO subforums, in `#fr.*` IRC channels. The _francophonie_ wasn't spared.

## 5. 4chan and /b/&nbsp;—&nbsp;radical anonymity

**4chan**, founded in 2003 by **Christopher "_moot_" Poole** (then 15), a copy of the Japanese **2chan** (Hiroyuki Nishimura).

- **/b/** (_random_): board with no rules, no archive (threads disappear after a number of pages), total anonymity (no persistent pseudo), massive volume (millions of messages/day at peak).
- **Anonymous** as a collective entity literally emerged from /b/ around 2006-2008.
- Mass-produced _memes_: Pepe, _LOLcats_, Rickroll, _Distracted Boyfriend_, came out of /b/ and were picked up by the mainstream.
- **Cruelty** documented: organized raids against targets (sometimes suicidal children, anorexics, etc.).
- **Pedo-criminality** documented on certain minor boards, which justified serial arrests of moot and his successors.

On April 14, 2025, 4chan was massively hacked:

- Admin access
- Source code and other internal data
- Identities
- ...

Today (2025-2026), 4chan still exists but has lost its centrality to Discord, Reddit, Telegram, et al.

## 6. The "_no limit_" culture&nbsp;—&nbsp;impunity through anonymity

### The subjective perception

For underground forum harmful actors of the era:

| Feeling                        | Reality                                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------------------- |
| "_I'm untouchable_"            | False: _IRC logs_ are kept for years, databases are leaked, _OPSEC_ is hard to maintain      |
| "_I can do anything_"          | False: legal limits exist, but they are **not immediately visible** at the moment of the act |
| "_No one is going to find me_" | False: an IP, a timezone, a recurring typo are enough for an _intelligence agency_           |
| "_It's just a private joke_"   | False: victims suffer **real** consequences, sometimes fatal                                 |

1. Apparent **technical anonymity** (proxy, VPN, Tor).
2. **Distance** between author (at home) and victim (on the other side of the world).
3. **No immediate physical reaction**: the screen filters, you don't see the victim cry.
4. **Peer validation** on the forum: others _congratulate_ the most "_daring_" acts, building _hunt lists_, exchanging "_harassment kits_".
5. **Systematic failure of law enforcement** to intervene quickly, especially when harasser and victim aren't in the same country.

### Why this creates _dangerous profiles_

This combination produces individuals with:

- Real **technical** skills (up to state-level).
- **Zero empathy** toward victims (never seen, "_don't know them_").
- Structural **contempt** for institutions (seen as slow, stupid, corrupt).
- **Identity built** around anti-system "_prowess_".

## 7. Inoperability of classical recourse

### "_Filing a complaint against your neighbor_" no longer works

The European and American legal arsenal was built for societies where:

- The neighbor is **identifiable** (postal address, civil identity).
- The harm is **geographically circumscribed**.
- Evidence is **physical** (testimony, photos, letters).
- The state has **jurisdiction** over the perpetrator.

None of these assumptions hold for online underground harassment:

- The perpetrator is **anonymous** by construction.
- The harm is **globalized**: the victim may be in France, the perpetrator in Russia, the server in the Bahamas.
- Evidence is **digital**, hence fabricable, deletable, contestable.
- The victim's state has **no jurisdiction** over the foreign perpetrator.

A doxing/harassment victim who files a complaint often ends up with:

1. Complaint _shelved_ for lack of identification.
2. Complaint _transferred_ to another jurisdiction that shelves it too.
3. Complaint _rejected_ for territorial incompetence.
4. _Moral_ and _financial_ cost of having tried the procedure.

### _Private vendetta_ becomes the norm

When the judicial system is inoperative, conflict is resolved by:

- **Counter-doxing**: the victim, or an ally, doxes the perpetrator back.
- **Technical counter-attack**: DDoS, deface, exfiltration.
- **Public shaming**: public exposure on Twitter, Reddit, media (_call-out_).
- **Informal hacker tribunals/syndicates**: a group respected in the scene _judges_ and _excommunicates_ the author.

These resolutions are **violent**, **non-reversible**, and **as violent as possible**&nbsp;—&nbsp;they _exist_ **because nothing else works.**

## 8. Marketplace forums

From ~2005-2008, underground forums shifted from a _sharing_ logic to a _commerce_ logic:

| Market                                   | Period                          | Platforms                                                               |
| ---------------------------------------- | ------------------------------- | ----------------------------------------------------------------------- |
| **Carding**: sale of stolen card numbers | From 1999 (forums), 2011+ (Tor) | ShadowCrew, Carder.su, Silk Road, etc.                                  |
| **0day exploits**                        | 2005+                           | Forums, Tor, then _exploit-as-a-service_ (Zerodium, etc.)               |
| **Botnets**                              | 2007+                           | Selling access to _10,000+ compromised machines_ for DDoS, spam, mining |
| **Malware-as-a-service**                 | 2010+                           | You pay to use a malware                                                |
| **Doxing-as-a-service**                  | 2010+                           | _dox-for-hire_: order a dox on anyone                                   |

### Brains and operators

Marketplace forums **separate**:

1. The **brain**: the one who develops the technique.
2. The **operator**: the one who pays to use the technique on their target.

This separation **exploded** the number of victims: before, you had to be technically _capable_ to do harm. Since then, **anyone with a few dollars** could launch a targeted attack.

The same pattern appears with _The Anarchist Cookbook_ (William Powell, 1971), which published instructions for making homemade bombs&nbsp;—&nbsp;except the _Anarchist Cookbook_ produced a few isolated cases, while underground marketplace forums produced **thousands** of victims per month.

### Anarchist Cookbook parallel

| Aspect           | Anarchist Cookbook (1971) | Underground forums (2005+)                          |
| ---------------- | ------------------------- | --------------------------------------------------- |
| Object sold      | Paper instructions        | Software tools + tutorials                          |
| Target audience  | Angry teenagers           | Angry teenagers + organized criminals               |
| Cost             | 0 (PDF or library)        | $50-5000+                                           |
| Misuse risk      | High (_real_ bombs)       | High (_real_ lives destroyed)                       |
| State response   | Surveillance              | Surveillance (rare arrests)                         |
| Long-term effect | Still shared today        | Forums increasingly _underground_, Tor marketplaces |

The **common point** is **the democratization of harm-capability that previously required years of learning.**

## 9. Why this universe produced state-intelligence-level skills

To _survive_ as an active member of an underground forum, you had to develop:

| Skill                                             | Application                                                                                      |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **OPSEC**&nbsp;—&nbsp;Operations Security         | Keep anonymity over 5-10 years without a single leak                                             |
| **OSINT**&nbsp;—&nbsp;Open Source Intelligence    | Dox a target from almost nothing                                                                 |
| **Social engineering**                            | Manipulate a human (tech support, target's ex-friend, employer)                                  |
| **Surveillance**&nbsp;—&nbsp;_eyes everywhere_    | Keep an eye on every forum where their pseudo appears, leaked databases, screenshots, everything |
| **Counter-intelligence**                          | Detect _infiltrators_ (law enforcement, researchers, enemies) posing as members                  |
| **Influence operations**                          | Coordinate a raid across multiple platforms simultaneously, build a narrative                    |
| **Forensics**&nbsp;—&nbsp;anti-forensics          | Erase traces, scramble trails, create false ones                                                 |
| **Crypto**&nbsp;—&nbsp;practical, not theoretical | End-to-end encryption, GPG, etc.                                                                 |

These skills are **identical** to a state intelligence operator's. Agencies (NSA, FSB, MSS, DGSI, GCHQ) **recruit** in this scene since at least 2005, and the best profiles _come from_ there.

## 10. Why "_enemies_"?

The Holy Book's author uses the word **enemy**&nbsp;—&nbsp;and it's not a metaphor.

In this world, you have _enemies_ in the **operational** sense:

- People who **doxed** the author or their relatives.
- People who **publicly denounced**, who **lied** about his acts, who **tried to humiliate him**.
- Communities that **organized** coordinated raids against the scene he belongs to.
- Law enforcement that's useless.

When you've _lived_ these operations, you no longer use the word _adversary_ or _opponent_. You say **enemy**, because that's what it is: someone who wants to provoke a **destruction** (social, professional, sometimes physical) and acts to achieve it.

See [`17-survivor-psyche-programming.md`](17-survivor-psyche-programming.md)

## 11. Connections with the rest of the primer

- [`02-lulzsec-lulzboat-antisec.md`](02-lulzsec-lulzboat-antisec.md)&nbsp;—&nbsp;LulzSec / AntiSec, organized hacktivism.
- [`03-ytcracker-nerdcore-digital-gangster.md`](03-ytcracker-nerdcore-digital-gangster.md)&nbsp;—&nbsp;DG, the reference forum.
- [`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)&nbsp;—&nbsp;IRC, EFnet, Zone-H.
- [`05-indonesian-hackers.md`](05-indonesian-hackers.md)&nbsp;—&nbsp;YogyaCarderLink, carding & defacement.
- [`17-survivor-psyche-programming.md`](17-survivor-psyche-programming.md)&nbsp;—&nbsp;psychological and technical consequences.
