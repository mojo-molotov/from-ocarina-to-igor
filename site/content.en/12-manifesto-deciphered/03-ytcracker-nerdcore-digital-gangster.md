---
title: "12.03 — YTCracker, Nerdcore, Digital Gangster"
description: "YTCracker, alias Bryce Case Jr.: the man linking the hacker scene, Nerdcore, the Digital Gangster forum and crypto culture, cited by the manifesto."
weight: 3
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 3
---

# 12.03&nbsp;—&nbsp;YTCracker, Nerdcore, Digital Gangster

> Bryce Case Jr., a single man, connects _four universes_: the US hacker scene (1999-2005), the birth of _Nerdcore_ (nerd hip-hop, 2005-2008), Digital Gangster (forum 2005-2017), and crypto culture (from 2013 onward, notably with _Bitcoin Baron_). The Holy Book quotes him several times.

## 1. Identity

| Field  | Value                                                              |
| ------ | ------------------------------------------------------------------ |
| Name   | **Bryce Case Jr.**                                                 |
| Born   | August 23, 1982, La Mirada, California                             |
| Alias  | **YTCracker** (pronounced "_whitey cracker_")                      |
| Status | Formerly black hat, now white hat (cybersec consultant + musician) |

The pseudo "_YTCracker_" is pronounced _whitey cracker_. It combines "_Yours Truly_", the name of a character in Neal Stephenson's cyberpunk novel _Snow Crash_, and the term _cracker_&nbsp;—&nbsp;the one who breaks into computer systems. Bryce Case himself explained this etymology in several interviews.

Sources: [YTCracker&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/YTCracker), [Caplin News&nbsp;—&nbsp;_YTCracker: The original digital gangster_](https://caplinnews.fiu.edu/ytcracker-the-original-digital-gangster/)

## 2. The NASA hack (1999)

At 17, Bryce defaced the **NASA (Goddard Space Flight Center)** site via a variant of the `msadc.pl` exploit (_Microsoft Active Server Data Connector_, a well-known vulnerability at the time). It's his alias's media launching pad.

- National media coverage.
- Sentenced to 2 years' probation and restitution (the amount isn't really public; sources vary: $24,000 per his official bio, $50,000–$60,000 per _Newsweek_).
- Reputation established in the _defacement_ scene (see [`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)).

He then defaced several .gov and .mil sites in quick succession&nbsp;—&nbsp;all before turning 18. He claimed it in the name of patriotism, to warn rather than destroy.

## 3. Nerdcore

### Definition

**Nerdcore** = a hip-hop subgenre whose lyrical content is explicitly _geek_ / _nerd_: code, video games, sci-fi, hacking, math, sciences. Not an _ironic_ pose: a hip-hop _actually_ written by people who master these topics.

Pioneers / figures:

- **MC Frontalot** (Damian Hess), inventor of the term "_Nerdcore_" in his eponymous track (2000).
- **YTCracker**, the first rapper to couple _hacker street cred_ + Nerdcore.
- **MC Lars**, **MC Chris**, **Optimus Rhyme**, **mc chris**, **Dual Core**, **ZeaLouS1**...

### YTCracker's founding album: _NerdRap Entertainment System_ (2005)

> The album was created by adding vocals to re-mixed digital music from original Nintendo games, and was described in Newsweek as a "classic of the style."

Beats sampled from NES game OSTs. Lyrics on hacking, BBSes, phreakers, script kiddies. It's the album that _defined_ Nerdcore for the 2005-2015 decade.

### `Nerd Life` (2006)

> "_I'm the final word / I'm the null at the end of the string_"

That's what Ocarina implicitly picks up with "_I'm the bug you'll never get rid of_".

| YTCracker (2006)                          | Ocarina Holy Book (2026)                |
| ----------------------------------------- | --------------------------------------- |
| "_I'm the null at the end of the string_" | "_I'm the bug you'll never get rid of_" |

It's a reference to programming. In C, every string must end with a null byte `\0` (_null terminator_), which tells the program where the string ends in memory. If this delimiter is missing or misplaced, reading continues past the intended bounds&nbsp;—&nbsp;that's an _out-of-bounds read_ attack.

Many famous vulnerabilities (including _Heartbleed_, 2014) exploited this type of flaw in C programs. The principle: an attacker sends a string without `\0`, forcing the program to read adjacent memory until it finds one by chance, thus exposing sensitive data (keys, passwords, etc.) that happened to be there.

"_I'm the null at the end of the string_" therefore refers to that missing delimiter: the one that should have stopped the read. It's a posture of **identity impersonation at the memory level**. The hacker poses as the `\0`. Concretely, it evokes controlling or injecting the byte that will be interpreted as the string terminator. He **decides** where the string ends. Either to extend reading past the bounds, or to make it look like a string ends earlier: "_I do what I want._"

Ocarina presents itself as a **persistent bug**. The _grain of sand_ in the gears of the _slipologues_. Same posture, different image.

> "_Nerd life, bitch, it's a revolution  
> Up on top of our evolution  
> Thanks for the fuel that I got in school  
> All you motherfucking bullies: now I make the rules_"

### `Robots Will Definitely Take Your Job`

At the end of the chapter "_First feedbacks_":

> [Peace out.](https://soundcloud.com/ytcracker/ytcracker-robots-will-definitely-take-your-job)

_("Peace out." is a casual / cold farewell typical of this scene.)_

It's a YTCracker track that predicts (ironically) that robots / AI will replace coders. The link placement is deliberately double:

1. At _face value_: "_here's the exit, listen to this as you leave the page_".
2. _Read between the lines_: "_you, \_slipologue_ I just torched, _the robots_&nbsp;—&nbsp;i.e., the AI I'm using to write Ocarina&nbsp;—&nbsp;are going to take your job\_".

It's the final punchline of the pamphlet.

## 4. Digital Gangster (2005-2017)

### The forum

Founded in **2005** by YTCracker. URL: [`digitalgangster.com`](https://digitalgangster.com/)

Hybrid forum:

- Hacking discussions (defaces, exploits, OPSEC).
- Nerdcore.
- Bullshit / lulz / shitposting.
- Trading / carding (unofficially).

At its peak: **36,000 members**, **2 million views/week** (source: YTCracker Wikipedia).

### Iconic hacks attributed to Digital Gangster

| Year | Target                                      | Effect                                 |
| ---- | ------------------------------------------- | -------------------------------------- |
| 2005 | **Paris Hilton T-Mobile breach**            | Sidekick dump: photos, contacts, SMS   |
| 2008 | **Miley Cyrus email**                       | Account hacked, personal photos leaked |
| 2009 | **Twitter accounts of Barack Obama et al.** | Mass account takeover                  |
| 2014 | **Craigslist DNS hijacking**                | Redirect of the entire domain          |

Source: [YTCracker&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/YTCracker)

### Why this forum is central

Digital Gangster is the 0day _underground_ _Reddit_ of 2005-2017. What **`/b/`** was to 4chan, what **Bugtraq** was to the industry, _DG_ was to the US _grey hat_ scene of that decade.

That's what the Holy Book invokes between the lines when it writes "_Fucking skids, fucking normies_"&nbsp;—&nbsp;it's DG's native vocabulary.

### The bridge to Yung Innanet, the "_DG descendant_"

The Holy Book quotes `true colors` adding: "_(btw: RIP, DG descendant…)_". "_DG_" stands for **Digital Gangster**; the author thus signals that **Yung Innanet (kayos)** is an heir of that scene.

Officially, DG closed in 2017 and kayos emerged around 2019 with VXUG, but he was still present on the Discord that followed under the pseudo _Yung Snat_. He himself claims this lineage in [`/issues/trust`](https://soundcloud.com/queed-inc/issues): "_I'm representing the DG descendant_".

One of his signatures is bashing Windows: he constantly returns to "downing" (killing) it with no regret. He's also cited in [_Retarded_](https://soundcloud.com/spokepp4l/retarded), as having been alongside _Jewbird_ and _Atmos The ILLKid_, in the context of an EFnet contest "_celebrating everyone's particularities and differences, which keeps EFnet as exceptional as it is strange_": "_Bumping yung innanet windows down no regrets_".

In [`shadow`](https://soundcloud.com/queed-inc/shadow), same motif, phrased differently:

> _When them shots rang out I suggest you avoid Windows_  
> _I suggest you avoid Windows_  
> _I suggest you avoid Windows_  
> _When them shots rang out I suggest you avoid Windows_  
> _I suggest you avoid Windows_  
> _I suggest you avoid Windows_

Picking up on _Retarded_, in [`0101`](https://soundcloud.com/queed-inc/0101a), _Yung Innanet_ also calls out:

> Free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound  
> They gotta let my fuccin dogs out  
> Free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound

After _Yung Innanet_'s tragic death, _Jewbird_ posted [`fr0z3n`](https://soundcloud.com/birdneststream/fr0z3n), an unreleased track that kayos had himself shared on IRC around 2020, waiting for YTCracker's part to be ready:

> rip kayos&nbsp;—&nbsp;he put this link in irc and was waiting for yt to finish up his part, like around 2020 and it is a unreleased track so i put it here cuz it prob was not released lol

### Shared sensibility

Loneliness, isolation, deaths, addictions, lost loved ones, psychotic episodes, nightmares, and many other tragedies are described **without interruption** in Atmos and Yung Innanet's music.

Atmos, for his part, reappears around 2023 discreetly as `0xDEADCAFE` and publishes [_JUSTINE_](https://soundcloud.com/somta/justine), whose description reads:

> THIS IS THE TALE OF A HACKER THAT GOT STUCK IN THE MATRIX OF INFOSEC  
> JUSTINE IS A FICTIONAL CHARACTER THAT REPRESENT HIS ADDICTION TO DRUGS AND ALCOHOL  
> ONE OF MANY BUT MORE LUCKY THAN OTHER RIP TO ALL THE NURGA WE LOST RIP STARBROTHER , WOJTEK , dreadz all all others
>
> The sad reality is that addiction, drugs abuse is something that took the life of so many hackers .

Themes of loneliness, sexual misery, urban misery, inner wandering / mental distress, addictions, criminality, regrets, and instability return again in a song where you sense Atmos has nonetheless grown stronger since. It's one of his most accessible tracks. The lyrics are in Quebecois French and not directly translatable; the gist of each line is summarized after each quote:

> Free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound, free […]

> "_Justine, Justine, pourquoi t'as croisé ma vie&nbsp;? J'y croyais Justine, quand t'es là tu me donnes des amis […] Justine, Justine, j'pourrais te boire toute la nuit._"  
> _(— Justine, why did you cross my life? I believed in you, Justine; when you're here you give me friends […] Justine, Justine, I could drink you all night long. "Justine" stands for his addiction.)_

> "_Ce milieu m'a impressionné, j'voulais atteindre la lune, mais à la place de tout ça j'ai fini entouré de bandits […]_"  
> _(— This world impressed me, I wanted to reach the moon, but instead I ended up surrounded by crooks.)_

> "_Toujours à deux battements de cœur de la crise cardiaque._"  
> _(— Always two heartbeats away from a heart attack.)_

> "_Mon portefeuille a déjà tenu la claque._"  
> _(— My wallet has already taken the hit.)_

> "_Si ta blonde est consentante, j'y mets la main, ça pelote._"  
> _(— If your girl consents, I'll put my hand there, it's getting fondled. ["blonde" = girlfriend in Quebecois])_

> "_La police m'arrêtera sur le fait._"  
> _(— The cops will catch me red-handed.)_

> "_Mon silence est assez large à cause des finances inarrêtables, ce qui me change en client désagréable. Ce monde m'a tout pris, où même mes femmes (fans&nbsp;?) m'incriminent, voici les histoires de problèmes apparents de l'homme invisible._"  
> _(— My silence is wide because of unstoppable finances, which turns me into an unpleasant client. This world has taken everything from me, where even my women/fans incriminate me; here are the apparent stories of the invisible man.)_

> "_La vie vaut cher mais sur le marché noir l'argent me tente. Donc c'est pour son bien que ça fait onze ans que ma mère attend que je rentre._"  
> _(— Life is expensive, but on the black market money tempts me. So it's for her own good that my mother has been waiting eleven years for me to come home.)_

> "_Camisole de force, si le carnivore te croque._"  
> _(— Straitjacket, if the carnivore bites you.)_

> "_Mais qu'est-ce que t'aurais fait à ma place&nbsp;?_"  
> _(— But what would you have done in my place?)_

> "_J'ai p'têt' braqué mais si tu savais combien j'ai payé de dettes._"  
> _(— I may have robbed, but if you knew how much debt I've paid…)_

Just before releasing _JUSTINE_, still as `0xDEADCAFE`, Atmos had re-published a Yung Innanet track renaming it _PPL NOT GOOD_ (_people not good_).

> _People not good to eachother_
>
> _I said people not good to eachother_  
> _I said people not good to eachother_  
> _Could be your mother, be your sister, be your brother_  
> _Who gon be there when you go ducking for cover?_

That's [_oblivion_](https://soundcloud.com/synrst/o-b-l-i-v-i-o-n)

Atmos annotates this repost as:

> _ALL CREDIT BELONG TO YUNG SNAT - I ONLY REMASTERED FOR MORE BASS_

_Yung Snat_ being one of Yung Innanet's other pseudos.

---

[_Atmos - cold loneliness_](https://soundcloud.com/mookl4f5/cold-loneliness) is a very discreet, completely incomprehensible-on-first-listen track, but terribly dense and heavy with meaning, like many others in the Nerdcore universe that leave computing aside to speak more intimately. Again, the lyrics are Quebecois French; English summaries follow each quote:

> "_Froid de solitude, j'ai froid de solitude._"  
> _(— Cold of loneliness, I am cold from loneliness.)_

> "_Est-ce que t'veux vraiment savoir à quel point on a morflé d'suite&nbsp;? Y fallait crissement qu'on tombe à terre, on s'est mis à s'battre comme des brutes._"  
> _(— Do you really want to know how much we got hammered straight away? We absolutely had to fall to the ground; we started fighting like brutes.)_

> "_J'aurais dû rester au Sino shop [magasin graffiti/street-art]. Devenu parano d'entendre, de le dire, y a une ombre avec machette qui m'suit ou pas&nbsp;?_"  
> _(— I should have stayed at the Sino shop [a graffiti/street-art shop]. Got paranoid from hearing it, from saying it&nbsp;—&nbsp;there's a shadow with a machete following me, or not?)_

> "_Mon cerveau c'est un ordi qui'arrête pas de lagguer, en plus d'être un camé aux feelings douteux. J'veux une biatch, avec elle dans un vol plané en Mini Cooper._"  
> _(— My brain is a computer that won't stop lagging, on top of being a junkie with dubious feelings. I want a girl, with her gliding in a Mini Cooper.)_

> "_Direction Place Major [épicerie, quartier morne]._"  
> _(— Direction Place Major [a grocery store in a dreary district].)_

> "_J'ai rêvé de saccager un magasin de montres._"  
> _(— I dreamed of trashing a watch shop.)_

> "_Des minutes fucking remplies, un salon désertique&nbsp;:&nbsp;[inventaire très sommaire…], plus une rallonge électrique._"  
> _(— Fucking packed minutes, a deserted living room: [very minimal inventory…], plus an extension cord.)_

> "_Dix mois sans baiser […] 'va falloir être carrément actif plus, parce que même entouré je continue à vivre dans un froid d'solitude._"  
> _(— Ten months without sex […] gonna have to be way more active, because even surrounded I keep living in a cold of loneliness.)_

> "_Des gargouilles qui m'attrapent les chevilles, m'emmènent en bas pour une vie nice [probablement des crises psychotiques réelles] […] il m'manque pas grand chose pour que j'm'entaille la jugulaire._"  
> _(— Gargoyles grabbing my ankles, taking me down for a "nice" life [probably actual psychotic episodes] […] it wouldn't take much for me to cut my own jugular.)_

> "_Mes minutes sont comptées, mais comment que ça se fait que c'est à chaque cinq s'condes&nbsp;? […] on m'a construit pour mieux me démolir, l'après c'comme un château de cartes._"  
> _(— My minutes are numbered, but how come it's every five seconds? […] they built me up to better tear me down&nbsp;—&nbsp;the aftermath is a house of cards.)_

> "_Quand je dis "nous", c'est moi, je suis sociopathe._"  
> _(— When I say "we", I mean me, I'm a sociopath.)_

> "_Ils m'ont répété que l'amour me ferait du bien mais y a que d'calisse d'ingrats._"  
> _(— They kept telling me love would do me good, but there are only fucking ingrates.)_

> "_C'que j'ai besoin c'est d'une désintox'._"  
> _(— What I need is detox.)_

> "_Un vrai criminel n'a plus souvent les mains propres_"  
> _(— A real criminal rarely has clean hands.)_

> "_Fucking based_"

> "_Il m'semble que j'allais mieux, j'tais un cobaye pour les nouvelles drugs. J'ai perdu mon chemin, tu m'croises en jaquette bleue._"  
> _(— Seems I was doing better, I was a test subject for new drugs. I lost my way, you'll catch me in a blue gown [hospital].)_

> "_J'ai froid d'solitude, c'pas normal que j'habite tout seul pis qu'on s'entende pas&nbsp;!_"  
> _(— I'm cold from loneliness; it's not normal that I live alone and we don't get along!)_

He also talks about uncontrollably collapsing from exhaustion / blackouts:

> "_'manquerait justement d'dormir sans fermer le fourneau._"  
> _(— All I'd need is to fall asleep without turning off the stove.)_

> "_J'me suis assoupi devant la TV, pis ya mon réveil, j'tais en train de pénétrer celle qu'on appelait AVATAR&nbsp;!_"  
> _(— I dozed off in front of the TV, and then my alarm goes&nbsp;—&nbsp;I was busy sleeping with the one we called AVATAR!)_

## 5. The white-hat shift

Around 2015-2017, Bryce Case Jr. _shifted_ professionally:

- Cybersec consultant for big companies.
- Still produces Nerdcore music.
- Interview on the **Shawn Ryan Show #85** (November 23, 2023).
- Still a regular artist at **DEF CON** since 2011.
- Still a beloved mentor to many young crooks (_said with affection here_).

> But im a teacher of tactics spread solution  
> To students of the game though the fames elusive  
> Im banging crypto when im spitting acoustic  
> Cuz this game has got a case of the loose tip  
> Read between the lines draw conclusions  
> Lifting the shroud off these false illusions  
> This computer is a weapon of mine  
> And i can run the globe in polynomial time
>
> S P A M  
> Send it every day get paid and then  
> S P A M  
> Load another campaign and do it again

— [YTCracker, S P A M 2](https://www.youtube.com/watch?v=SALLlcVYtYQ)

_(Music following notably [**Still Spam**](https://www.youtube.com/watch?v=-zH_nQDZ10k) in his discography, but also [**Life is an inbox**](https://www.youtube.com/watch?v=xoWkDSVORW0), among others.)_

His trajectory is _the model_ the Holy Book implicitly invokes:

> _From Hell to where we are today._  
> _Saved by Research, by good values, by thankless work._

That's exactly Bryce. Transposed to the author's context (early exposure to _YogyaCarderLink_):

> "_From Zone-H to a settled life._"

## 6. Interviews

Two especially documented long-formats:

### Darknet Diaries, episode 78&nbsp;—&nbsp;_Nerdcore_

- **Host**: Jack Rhysider.
- **Title**: _Nerdcore_.
- **Transcript**: <https://darknetdiaries.com/transcript/78/>

It's **the** audio reference on YTCracker. He recounts his journey: teenage school hacks ("_I hacked pretty much every school district in the state_"), institutional targets ("_I did the FAA, New York Department of Agriculture… pretty much every school district in Colorado_"), and the rise of _Nerdcore_ ("_the genre, right around I would say 2006, 2007, started to really kinda gain steam_").

It's the episode where you hear Bryce Case Jr. himself retrace the _black hat 1999_&nbsp;→&nbsp;_nerdcore 2005_ →&nbsp;_Digital Gangster_ →&nbsp;_crypto / consulting_ trajectory.

### Shawn Ryan Show, episode 85 (November 23, 2023)

Long-format video (6h). Broader conversation, _US talk-show_ format, hosted by Shawn Ryan (ex-Navy SEAL). Less technical than Darknet Diaries, more biographical. [Apple Podcasts](https://podcasts.apple.com/md/podcast/85-bryce-case-jr-aka-ytcracker-anonymous-hacker/id1492492083?i=1000635785028), [YouTube](https://www.youtube.com/watch?v=hFS7xONBJSE)

To understand the _scene_: Darknet Diaries. To understand the _person_: Shawn Ryan Show.

## 7. `Cryptoilluminati` (2018)

> "_Told you to snap up a modest position_"  
> "_Of currency minted from factoring digits_"  
> "_Which of you listened?_"

[ytcracker - cryptoilluminati · YouTube](https://www.youtube.com/watch?v=_NL_B9MAKCw)

The Holy Book picks it up in French:

> "_A nice advance, carried by these currencies forged from the factorization of numbers._"

Placed in the section where the author evokes _Code is Law_ (Lessig 1999 / Ethereum 2015). YTCracker _already_ articulates the same thesis but in hip-hop: _crypto is a **scientific** advance, despised by those who didn't listen in time_.

## 8. Lineage with Ocarina

YTCracker does through music what Ocarina does through the _framework_:

| YTCracker                                       | Ocarina                                              |
| ----------------------------------------------- | ---------------------------------------------------- |
| Brutally honest, technical excellence           | Brutally honest, technical excellence                |
| Converted to ethics without denying the past    | Clean code without denying the _underground_ posture |
| Mentor to the next generation (Ryan Montgomery) | _Manifesto_ addressed to the next generation         |
| "_I'm the null at the end of the string_"       | "_I'm the bug you'll never get rid of_"              |
| _Robots Will Definitely Take Your Job_          | _ocarina-with-ai-example_ (99% Claude)               |

## 9. Going further

### Other music

| Title                                | Note                                                                                                                                        |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Take a knee                          | [YouTube](https://www.youtube.com/watch?v=Cf_XhKE4R_o)                                                                                      |
| The Legend                           | [YouTube](https://www.youtube.com/watch?v=9_rR-0guirs)                                                                                      |
| Paint                                | [YouTube](http://youtube.com/watch?v=TS5MUf14gDw)                                                                                           |
| Kacho On!                            | [Soundcloud](https://soundcloud.com/scrubclub/2-mello-kacho-on-feat-ytcracker)                                                              |
| Friend zone                          | [Soundcloud](https://soundcloud.com/ytcracker/ytcracker-friend-zone)                                                                        |
| California Breeze                    | [YouTube](https://www.youtube.com/watch?v=-jn6cT6ZqX0)                                                                                      |
| Subnet mask off                      | [YouTube](https://www.youtube.com/watch?v=1YW_6OXYB7E), covered by Yung Innanet, [mvsk (Soundcloud)](https://soundcloud.com/queed-inc/mvsk) |
| Toolin' up                           | [Soundcloud](https://soundcloud.com/ytcracker/ytcracker-toolin-up)                                                                          |
| Bazaar                               | [YouTube](https://www.youtube.com/watch?v=X6t3CVafuec)                                                                                      |
| Bot in the cut                       | [Soundcloud](http://soundcloud.com/hairetsu/ytcracker-and-hairetsu-bot-i)                                                                   |
| Terminal                             | [YouTube](https://www.youtube.com/watch?v=WBcK-b7Wg1M)                                                                                      |
| Computer Crime                       | [YouTube](https://www.youtube.com/watch?v=2P0RcoY0Snc)                                                                                      |
| Fifty Thousand Dollar Friday         | [Soundcloud](https://soundcloud.com/ytcracker/ytcracker-and-hairetsu-fifty)                                                                 |
| We're Golden                         | [Soundcloud](https://soundcloud.com/rykg-263016260/ytcracker-were-golden-ft)                                                                |
| Convalescence (remix by _Max James_) | [Soundcloud](https://soundcloud.com/maxjamesmusic/ytcracker-convalescence-max-james-remix)                                                  |
| Green Hat (remix by _Max James_)     | [Soundcloud](https://soundcloud.com/maxjamesmusic/ytcracker-green-hat-max-james-remix)                                                      |

### The "_Spam Holy Book_"

[_The Book of Spam_](https://bkofspam.livejournal.com/)

### Mixtapes

[Replays of YTCracker's live Twitch mixtapes are available on YouTube&nbsp;—&nbsp;though the first one he did during Covid, absolutely magnificent, has disappeared.](https://youtu.be/Uo24VZK0znY?t=4116)

### Other artists

- [FreqyXin](https://soundcloud.com/freqyxin/bond-villain-girl)
- [dade (_Neals_ is one of YTCracker's other nicknames)](https://soundcloud.com/0xdade/0xdade-letter-to-neals)
- [hgc](https://soundcloud.com/888hgc/7variablesripyunginnanet)
- [hairetsu](https://soundcloud.com/hairetsu/friends-ive-worked-with-v1)
- [Scarlett Danger (_highly confidential_)](https://soundcloud.com/scarlett_danger/the-tea)
