---
title: "12.02 — LulzSec, the Lulzboat, AntiSec"
description: "LulzSec, the Lulzboat and AntiSec: three distinct subjects the manifesto invokes in one breath, and the separate history of each."
weight: 2
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 2
---

# 12.02&nbsp;—&nbsp;LulzSec, the Lulzboat, AntiSec

> Three distinct subjects: (1) **LulzSec** as a group, (2) **the Lulzboat** as identity metaphor, (3) **AntiSec** as a movement (two versions: 1999 and 2011). The Holy Book invokes them in one breath; each has its own history.

## 1. AntiSec (1999)&nbsp;—&nbsp;the original movement

### Origin

In the late 1990s, the infosec industry _professionalized_: companies formed around selling firewalls, antiviruses, audits. A norm emerged: **_full disclosure_**, publicly releasing vulnerabilities, their PoCs, their exploits, with the argument that it forces vendors to patch quickly.

Part of the _underground community_ saw this practice as a **business model dressed up as ethics**. The argument: full disclosure doesn't serve security, it feeds an economy where you _sell the fear_ you helped create. The same actors releasing exploits sell the solutions.

The **Anti Security** (`antisec`) movement was born against it. Its principle:

> No full disclosure. No public exploits. Bugs stay in the _underground_. Tools stay private. The mailing lists "_Bugtraq_", "_full-disclosure_", "_vuln-dev_", "_vendor-sec_" are considered _enemies_.

Declared targets of the original _AntiSec movement_:

- Sites: **SecurityFocus**, **SecuriTeam**, **Packet Storm**, **milw0rm**.
- Mailing lists: **`full-disclosure`**, **`vuln-dev`**, **`vendor-sec`**, **`Bugtraq`**.
- Public IRC forums where exploits circulated openly.

Source: [Antisec Movement&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/Antisec_Movement)

### Why it matters for Ocarina

The original AntiSec **did not win**. Full disclosure became the norm. CVE, CVSS, NVD, bug bounty programs: the whole market aligned on the opposite stance.

But the _structural_ argument&nbsp;—&nbsp;"_this industry creates the problem it sells_"&nbsp;—&nbsp;was never refuted. It came back in other forms (anti-vendor-lock, anti-SaaS, anti-No-Code movements). Ocarina inherits this line: refusal of testing _vendors_ (_BrowserStack_, _Sauce Labs_, etc.), refusal of "_platform solutions_", _white-box_ auditability of the code.

The Holy Book formalizes it (chapter "_Anti slipologues_"):

> For too long, computing has been held hostage by a minority, a "_1%_", that thought it would be clever to turn it into a playground for insiders.

This "_minority_" is, roughly, the anti-AntiSec industrial complex. Modern full disclosure is its tool. Ocarina was born against it.

## 2. LulzSec (May – June 2011)&nbsp;—&nbsp;50 days of chaos

### Origin

**Lulz Security** (LulzSec) was born in May 2011, an Anonymous _splinter group_. Six main members:

| Pseudo       | Identity          | Role                                                         |
| ------------ | ----------------- | ------------------------------------------------------------ |
| **Sabu**     | Hector Monsegur   | Leader, turned FBI informant by June 2011 (revealed in 2012) |
| **Topiary**  | Jake Davis        | Spokesperson, communiqués author                             |
| **Kayla**    | Ryan Ackroyd      | Technical exploits                                           |
| **Tflow**    | Mustafa Al-Bassam | Exploits, dev                                                |
| **AVUnit**   | never identified  | &nbsp;—&nbsp;                                                |
| **pwnsauce** | Darren Martyn     | &nbsp;—&nbsp;                                                |

50 days of attacks hitting public, media, and _entertainment_ sectors:

- **PBS** (May 2011), fake news "_Tupac alive in New Zealand_" on _Newshour_, in retaliation for an unfavorable WikiLeaks _Frontline_ documentary.
- **Sony Pictures**, massive user-base dump after the PSN debacle.
- **CIA.gov**, DDoS.
- **Fox**, X Factor contestant DB leak.
- **US Senate**, site infiltrated.
- **InfraGard Atlanta** (FBI partner), credential dump.
- **HBGary Federal** (FBI partner), credential dump, attack carried out under the Anonymous banner before LulzSec formed.

Sources: [LulzSec&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/LulzSec), [Operation AntiSec&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/Operation_AntiSec)

### The LulzSec Manifesto (June 2011)

For their 1000th tweet, LulzSec released a manifesto:

> "_We're not, only because we don't have to be. (...) We release personal data so that equally evil people can entertain us with what they do with it._"

_Owned nihilism_, aestheticized. Hacking for the "_lulz_", not for political conviction, not for wealth&nbsp;—&nbsp;for _fun_ and to _exhibit_ the system's fragility.

LulzSec brought back the term **AntiSec** under a new banner: **Operation AntiSec** (June 2011), in collaboration with Anonymous. Targets: governments, security organizations, vuln-dev mailing lists.

## 3. The Lulzboat

The **Lulzboat** is LulzSec's stylized _pirate ship_, repeated everywhere:

- Twitter banners.
- Pastebin headers: `▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ TheLulzBoat ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄`.
- Communiqués signed "_The Lulz Boat / Lulz Security_".

Boat ASCII art, Stuart Little / Captain Hook / Nyan Cat.

[![Antisec, The LulzSec Anthem, YTCracker, 2011](/assets/img/antisec-yt-2011.png)](https://www.youtube.com/watch?v=xDyBIpqZcNI)

> "_If you're sittin' below deck / In the Lulzboat, salute, bitch, and show some respect_"
>
> &nbsp;—&nbsp;YTCracker, **`#antisec`** (June 22, 2011), which became the official anthem of _Operation AntiSec_.

The line is quoted _as-is_ in Ocarina's Holy Book:

> "_In the Lulzboat, salute, bitch, and show some respect._"

A **generational password.**

### YTCracker and LulzSec

YTCracker (Bryce Case Jr.) is _strictly speaking_ outside LulzSec&nbsp;—&nbsp;he wasn't one of the 6 members&nbsp;—&nbsp;but he was **associated**:

- He personally knew several members.
- He wrote `#antisec` _during_ the operation.
- His song was used by Anonymous / LulzSec in their communiqué videos.

See [`03-ytcracker-nerdcore-digital-gangster.md`](03-ytcracker-nerdcore-digital-gangster.md) for the YTCracker detail.

## 4. The end (June 2011 → March 2012)

The night of June 25–26, 2011, LulzSec released **"_50 days of lulz_"**, their dissolution communiqué:

> "_For the past 50 days we've been disrupting and exposing corporations, governments, often the general population itself, and quite possibly everything in between, just because we could._"

Six months later, in March 2012, the US DoJ indicted five of the six members. Sabu had been cooperating with the FBI since June 2011&nbsp;—&nbsp;he ratted.

Source: [LulzSec finally calls it quits&nbsp;—&nbsp;GeekBurn](https://geekburn.wordpress.com/2011/06/26/lulzsec-finally-calls-it-quits-after-50-days-of-mayhem/)

## 5. Rhetoric "_`Don't fuck with us.`_" → "_`YOU FUCKED WITH US!`_"

The **`Don't fuck with us`** mantra comes from the original _carding/defacement_ scene (see [`05-indonesian-hackers.md`](05-indonesian-hackers.md), where its systematic presence on **YogyaCarderLink** deface pages is documented). LulzSec and Anonymous **inherited** it: it structured the entire _grey hat_ scene of the 2000s before being picked up by the 2010–2012 operations.

| Grammatical tense                                       | Effect                                                                      |
| ------------------------------------------------------- | --------------------------------------------------------------------------- |
| **`Don't fuck with us.`** (future conditional, warning) | _Defensive_ posture. _We don't do anything as long as you don't attack us._ |
| **`YOU FUCKED WITH US!`** (declaration of retaliation)  | _We warned you, you did it anyway, now own up._                             |

Ocarina's Holy Book phrases it word-for-word in the same language, in any translation:

> **YOU FUCKED WITH US!**

The whole invective passage (see [`06-yung-innanet-vxug.md`](06-yung-innanet-vxug.md)) isn't _gratuitous_ aggression&nbsp;—&nbsp;it's a late, explosive _response_ to years of pressure. It's the contextual adaptation of a framework author who spent years being dictated how _he should_ write his code.

These "_two-tense_" codes are **universal in this scene**. You find them in:

- YogyaCarderLink defaces (`Don't fuck with us.` signature at the bottom of the page).
- Post-HBGary pastebins (_Anonymous_, February 2011).
- LulzSec retaliation communiqués (_Operation Payback_&nbsp;—&nbsp;RIAA, MPAA, then WikiLeaks defense).
- Lulz Boat communiqués responding to arrests.

## 6. Lineage with Ocarina

Ocarina doesn't _obviously_ present itself as a hacker project in the 2011 sense. It's MIT, hosted on GitHub, breaks nothing. But it **inherits**:

| LulzSec / AntiSec trait                     | Ocarina trait                                    |
| ------------------------------------------- | ------------------------------------------------ |
| Rejection of professionalization as a value | Rejection of "_pytest plugin_" and of ecosystems |
| Rejection of full disclosure as business    | A single runtime dep, auditable code             |
| Claimed _group identity_                    | "_It's my car_"                                  |
| Direct, no-politeness rhetoric              | "_Fuck You. Not complicated._" (DHH)             |
| _Underground_ aesthetic                     | AI illustrations, pamphlet tone                  |
| _Lulz_ as tonality                          | Constant humor in the Holy Book                  |

Ocarina is what those people do **20 years later**, when they write a test framework during the day. It's the same ethic, in a different medium.
