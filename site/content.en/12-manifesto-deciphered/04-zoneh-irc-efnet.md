---
title: "12.04 — Zone-H, IRC, EFnet"
description: "Three infrastructures without which the 1998-2012 hacker scene would never have been the same: Zone-H (deface archive), IRC, EFnet (the historical IRC network). The Holy Book cites Zone-H only once, but it's a keyword that opens an entire infrastructure."
weight: 4
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 4
---

# 12.04&nbsp;—&nbsp;Zone-H, IRC, EFnet

> Three infrastructures without which the 1998-2012 hacker scene would never have been the same: **Zone-H** (deface archive), **IRC**, **EFnet** (the historical IRC network). The Holy Book cites Zone-H only once, but it's a keyword that opens an entire infrastructure.

## 1. Zone-H&nbsp;—&nbsp;deface archive (2002 → today)

### Foundation

- **Date**: March 2, 2002.
- **HQ**: Estonia.
- **Founder**: **Roberto Preatoni** (alias **`Sys64738`**).
- **URL**: [`zone-h.org`](https://zone-h.org)

### Function

1. An attacker defaces a site (replaces the homepage with their own version, signed).
2. The attacker (or a witness) submits the URL to Zone-H.
3. Zone-H moderates: verifies the deface is authentic.
4. If OK: the defaced site is **archived forever** on Zone-H (HTML+CSS+assets snapshot).
5. The deface author signs with their alias. Sourcing is public.

### Impact

For 10-15 years, Zone-H was **the public scoreboard** of the global _grey hat_ scene. Every notable deface was archived. For a _script kiddie_, climbing the Zone-H rankings was _the_ goal to _prove_:

- _Single defacements_: raw count.
- _Mass defacements_: deface _n_ sites in one attack (mass script + shared flaw).
- _Special defacements_: government sites, .mil, banks.

### Roberto Preatoni&nbsp;—&nbsp;_Sys64738_

The alias **`Sys64738`** is a reference to the _Commodore 64_: `SYS 64738` was the BASIC command for a soft reboot of a C64. Classic tribute from the late-1980s generation.

Preatoni had a mixed career:

- Founder of **WabiSabiLabi** (2007), a controversial 0day vulnerability marketplace (ambitious concept, catastrophic execution).
- Arrested on **November 5, 2007** as part of the Telecom Italia espionage scandal: his former company had been hired by Telecom Italia's security division in 2003-2004, and team members were indicted for illegal wiretapping and unauthorized access to computer systems.
- Regular speaker at **DEF CON** and **HITBSecConf**.

Sources: [Zone-H&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/Zone-H), [Roberto Preatoni / Sys64738&nbsp;—&nbsp;InfoConDB](https://infocondb.org/presenter/roberto-preatoni-sys64738)

### Why the Holy Book cites it

> _That's who we are: from Zone-H to a settled life._

- **Zone-H** = the before. The age of deface, of play, of criminal risk, of IRC _crews_.
- **"_a settled life_"** = the after. Salaried work, freelance, SaaS, conferences, certifications.

The bridge between the two wasn't built by the whole scene. Many stayed black hat (and ended in prison, or died). Many dropped off entirely. A minority crossed to _white hat_ (YTCracker's trajectory). And another minority took a different path: **Research**.

## 2. IRC&nbsp;—&nbsp;the protocol that carried everything

### Definition

**IRC** = _Internet Relay Chat_, multi-user text-chat protocol in client/server form, invented in 1988 by Jarkko Oikarinen. RFC 1459 (1993).

[INTERNET RELAY CHATTER FATES, Jewbird](https://soundcloud.com/birdneststream/internt-relay-chatter-fates)

```
                   ┌─────────────┐
                   │ IRC client  │ (mIRC / irssi / weechat / X-Chat / ...)
                   └─────┬───────┘
                         │ TCP 6667 (or 6697 SSL)
                         ▼
                   ┌─────────────┐
                   │ IRC server  │
                   └─────┬───────┘
                         │
                         │ inter-server links (mesh)
                         ▼
                   ┌────────────────────────────┐
                   │ Network = N linked servers │
                   │ (EFnet, IRCnet, Undernet,  │
                   │  DALnet, freenode, etc.)   │
                   └────────────────────────────┘
```

### Why central for the hacker scene

Between 1993 and 2012, IRC was _the_ social medium of hackers:

- Real-time technical discussions.
- Coordination of defaces (private channels).
- Distribution of _0day_ and _warez_.
- Recruitment of _crews_.
- Receiving an _invite_ to a private channel was a mark of recognition.

No public logs (unless someone logged and posted).  
No centralized moderation.  
No ads.

It was _underground by design_.

### The decline

IRC declined from around 2010 onward, crushed by:

- **Discord**
- **Slack**
- **Telegram**

But part of the old-school scene stayed on IRC. EFnet, OFTC, Libera.Chat (post-Freenode 2021), TCP DIRECT, EpiKnet still run. It became a _ghost network_&nbsp;—&nbsp;few people, but what's left is _filtered_.

## 3. EFnet&nbsp;—&nbsp;the historical network

### Definition

**EFnet** (_Eris-Free Network_) is one of the oldest still-operating IRC networks, founded in 1990.

EFnet was _the_ network of the _warez_, _zero-day_, _crackers_, _phreakers_ scene during 1996-2008. Most memorable channels&nbsp;—&nbsp;`#hax`, `#exploit`, `#voicebox`, `#carders`, `#legion`, `#vc`, `#2600`&nbsp;—&nbsp;lived on EFnet.

The identity of a 2000s hacker could often boil down to: "_I hung out on such-and-such channel on EFnet, we did such-and-such_".

Source: [EFnet&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/EFnet)

## 4. IRC in the Holy Book

| Term                         | IRC meaning                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Usage in the Holy Book                                                                                    |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| **`skid`** / _script kiddie_ | Hacker running scripts they don't understand                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | "YOU would have been that _lamer_, that kid who just wanted to show off and run PoCs found on Exploit-DB" |
| **`normie`**                 | Average / uninitiated user                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | "_Fucking normies!_"                                                                                      |
| **`lamer`**                  | Older pejorative variant of skid                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | id.                                                                                                       |
| **`rookie`**                 | Newcomer, beginner. The most contemptible are regularly used by _underground_ communities as fall-guys, or are so dumb they trip themselves up (s/o _NormalLeVrai_ who lamentably tried to ransom a state agency for a 20K crust of bread with English and an extortion message worthy of a third-grader's essay, got told off by the authorities that he "_would do better to focus on his social life_", and now pretends to be a former ShinyHunters and LAPSUS$ operator while peddling "_0-days_, _Zero-Click_ WhatsApp RCEs" for 3K when those are the kind of _0-days_ Mossad or APT29 holds&nbsp;—&nbsp;_clown_) | "like a _rookie_"                                                                                         |
| **`zine`** (= _magazine_)    | _Underground_ publication, often ASCII (e-zine)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | implicit                                                                                                  |
| **`crew`**                   | Small group of hackers, intimate, tight-knit                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | "_We are a real FAMILY!_"                                                                                 |

## 5. The bridge to Ocarina

Same _underground_ posture, same rejection of the _normie_, same identity _crew_ (the author _alone against all_).

When the Holy Book says:

> _We are a real FAMILY!_

It's an _IRC channel_ speaking. The "_we_" is figurative. It remains impossible to say _who_ is really behind it, and it will remain so forever. All we can say is that it's exactly the _tone_ of a private 2003 EFnet `#channel`.

## 6. Zone-H&nbsp;/&nbsp;IRC conventions in his signature

The typical _signing convention_ of a Zone-H actor:

```
   ╔══════════════════════════════════════════════════╗
   ║                                                  ║
   ║   H4CK3D BY: <alias>                             ║
   ║   GR33TZ: <other_aliases_of_the_crew>            ║
   ║                                                  ║
   ║   [ASCII art: skull / dragon / lulz boat]        ║
   ║                                                  ║
   ║   "Quote here, often musical or mantra"          ║
   ║                                                  ║
   ╚══════════════════════════════════════════════════╝
```

1. **The pseudo**.
2. **The `gr33tz`** (= _greetings_, the _crew_ list, also regularly said in music as _shoutout to_). Marks inclusion.
3. **A quote or a mantra**.

The Holy Book reproduces _exactly_ this structure:

```
Built by [@mojo-molotov](https://github.com/mojo-molotov)
Fueled by figatellu and Квас.
```

- Alias: `@mojo-molotov` (ostentatious Markdown typo).
- Implicit _gr33tz_: figatellu (Corsican sausage, wink), Квас (Russian drink, another wink).
- Quote: replaced by the quotes scattered through the Holy Book.

It's a **Zone-H signature** in GitHub README format. Immediate recognition for those who know.
