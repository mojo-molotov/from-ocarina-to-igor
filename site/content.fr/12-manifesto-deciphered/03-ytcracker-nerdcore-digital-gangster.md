---
title: "12.03 — YTCracker, Nerdcore, Digital Gangster"
description: "Bryce Case Jr., un seul homme, connecte quatre univers&nbsp;:&nbsp;la scène hackers américaine (1999-2005), la naissance de la Nerdcore (hip-hop de nerd, 2005-2008), Digital Gangster (forum 2005-2017), et la culture crypto (dès 2013, avec notamment Bitcoin Baron). Le Holy Book le cite plusieurs fois."
weight: 3
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 3
---

# 12.03&nbsp;—&nbsp;YTCracker, Nerdcore, Digital Gangster

> Bryce Case Jr., un seul homme, connecte _quatre univers_&nbsp;:&nbsp;la scène hackers américaine (1999-2005), la naissance de la _Nerdcore_ (hip-hop de nerd, 2005-2008), Digital Gangster (forum 2005-2017), et la culture crypto (dès 2013, avec notamment _Bitcoin Baron_). Le Holy Book le cite plusieurs fois.

## 1. Identité

| Champ  | Valeur                                                                       |
| ------ | ---------------------------------------------------------------------------- |
| Nom    | **Bryce Case Jr.**                                                           |
| Né     | 23 août 1982, La Mirada, Californie                                          |
| Alias  | **YTCracker** (prononcé «&nbsp;_whitey cracker_&nbsp;»)                      |
| Statut | Anciennement black hat, désormais white hat (consultant cybersec + musicien) |

Le pseudo «&nbsp;_YTCracker_&nbsp;» se prononce _whitey cracker_. Il combine «&nbsp;_Yours Truly_&nbsp;», le nom d'un personnage dans le roman cyberpunk _Snow Crash_ de Neal Stephenson, et le terme cracker&nbsp;—&nbsp;celui qui s'introduit dans des systèmes informatiques. Bryce Case a lui-même expliqué cette étymologie dans plusieurs interviews.

Sources&nbsp;:&nbsp;[YTCracker&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/YTCracker), [Caplin News&nbsp;—&nbsp;_YTCracker: The original digital gangster_](https://caplinnews.fiu.edu/ytcracker-the-original-digital-gangster/)

## 2. Le hack de la NASA (1999)

À 17 ans, Bryce deface le site de la **NASA (Goddard Space Flight Center)** via une variante de l'exploit `msadc.pl` (_Microsoft Active Server Data Connector_, vulnérabilité bien connue à l'époque). C'est la rampe de lancement médiatique de son alias.

- Couverture médiatique nationale.
- Condamné à 2 ans de probation et une restitution (le montant n'est pas vraiment public, les sources varient&nbsp;:&nbsp;24&nbsp;000&nbsp;$ selon sa biographie officielle, 50&nbsp;000–60&nbsp;000&nbsp;$ selon _Newsweek_).
- Réputation établie dans la scène _defacement_ (cf. [`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)).

Il a ensuite deface plusieurs sites .gov et .mil dans la foulée. Tout cela _avant_ ses 18 ans.  
Note&nbsp;:&nbsp;il l'a revendiqué au nom du _patriotisme_, pour _avertir_ plutôt que pour _détruire_.

## 3. Nerdcore

### Définition

**Nerdcore** = sous-genre du hip-hop dont le contenu lyrique est explicitement _geek_ /&nbsp;_nerd_&nbsp;:&nbsp;code, jeux vidéo, sci-fi, hacking, math, sciences. Pas une posture _ironique_&nbsp;:&nbsp;un hip-hop _réellement_ écrit par des gens qui maîtrisent ces sujets.

Pionniers /&nbsp;figures&nbsp;:

- **MC Frontalot** (Damian Hess), inventeur du terme «&nbsp;_Nerdcore_&nbsp;» dans son morceau éponyme (2000).
- **YTCracker**, premier rappeur à coupler _hacker street cred_&nbsp;+&nbsp;Nerdcore.
- **MC Lars**, **MC Chris**, **Optimus Rhyme**, **mc chris**, **Dual Core**, **ZeaLouS1**...

### Album fondateur de YTCracker&nbsp;: _NerdRap Entertainment System_ (2005)

> The album was created by adding vocals to re-mixed digital music from original Nintendo games, and was described in Newsweek as a "classic of the style."

Beats samplés depuis des OSTs de jeux-vidéo de la NES. Lyrics sur le hacking, les BBS, les phreakers, les script kiddies. C'est l'album qui _définit_ la Nerdcore pour la décennie 2005-2015.

### `Nerd Life` (2006)

> «&nbsp;_I'm the final word /&nbsp;I'm the null at the end of the string_&nbsp;»

C'est ce que reprend implicitement Ocarina avec «&nbsp;_Je suis le bug dont tu ne pourras jamais te débarrasser_&nbsp;»

| YTCracker (2006)                                      | Holy Book Ocarina (2026)                                                |
| ----------------------------------------------------- | ----------------------------------------------------------------------- |
| «&nbsp;_I'm the null at the end of the string_&nbsp;» | «&nbsp;_Je suis le bug dont tu ne pourras jamais te débarrasser_&nbsp;» |

C'est une référence à la programmation. En C, toute chaîne de caractères doit se terminer par un octet nul `\0` (_null terminator_), qui indique au programme où s'arrête la chaîne en mémoire. Si ce délimiteur est absent ou mal placé, la lecture continue au-delà des limites prévues, c'est une attaque par _out-of-bounds read_.

De nombreuses vulnérabilités célèbres (dont _Heartbleed_, 2014) ont exploité ce type de failles dans des programmes C. Le principe&nbsp;:&nbsp;un attaquant envoie une chaîne sans `\0`, forçant le programme à lire la mémoire adjacente jusqu'à en trouver un par hasard, exposant ainsi des données sensibles (clés, mots de passe, etc.) qui se trouvaient là.

«&nbsp;_I'm the null at the end of the string_&nbsp;» renvoie donc à ce délimiteur manquant&nbsp;:&nbsp;celui qui aurait dû stopper la lecture. C'est une posture **d'usurpation d'identité au niveau mémoire**. Le hacker se fait passer pour le `\0`. Concrètement, cela évoque le fait qu'il contrôle ou injecte l'octet qui va être interprété comme le terminateur de chaîne. Il **décide** où la string se termine. Soit pour prolonger la lecture au-delà des limites, soit pour faire croire qu'une chaîne se termine plus tôt&nbsp;:&nbsp;«&nbsp;_Je fais ce que je veux._&nbsp;»

Ocarina se présente comme un **bug persistant**. Le _grain de sable_ dans l'engrenage des _slipologues_. Même posture, autre image.

> «&nbsp;_Nerd life, bitch, it's a revolution_  
> _Up on top of our evolution_  
> _Thanks for the fuel that I got in school_  
> _All you motherfucking bullies: now I make the rules_&nbsp;»

### `Robots Will Definitely Take Your Job`

À la fin du chapitre «&nbsp;_Premiers retours_&nbsp;»&nbsp;:

> [Bonne continuation.](https://soundcloud.com/ytcracker/ytcracker-robots-will-definitely-take-your-job)

_(Traduit en anglais «&nbsp;Peace out.&nbsp;», une manière de saluer non-chalante typique de cette scène. «&nbsp;Bonne continuation.&nbsp;» est, ici, une traduction de l'anglais au français.)_

C'est un morceau de YTCracker qui prédit (ironiquement) que les robots&nbsp;/&nbsp;l'IA vont remplacer les codeurs. Le placement du lien est sciemment double&nbsp;:

1. Au _premier degré_&nbsp;: «&nbsp;_voilà ta sortie, écoute ça en quittant la page_&nbsp;».
2. Au _second degré_&nbsp;: «&nbsp;toi, _slipologue_ que je viens d'incendier, _les robots_, c'est-à-dire l'IA dont je me sers pour écrire Ocarina, vont prendre ton job&nbsp;».

C'est la pointe finale du pamphlet.

## 4. Digital Gangster (2005-2017)

### Le forum

Fondé en **2005** par YTCracker. URL&nbsp;:&nbsp;[`digitalgangster.com`](https://digitalgangster.com/)

Forum hybride&nbsp;:

- Discussions hacking (defaces, exploits, OPSEC).
- Nerdcore.
- Bullshit /&nbsp;lulz /&nbsp;shitposting.
- Trading /&nbsp;carding (officieusement).

Au pic&nbsp;: **36&nbsp;000 membres**, **2 millions de vues/semaine** (source&nbsp;: Wikipedia YTCracker).

### Les hacks emblématiques attribués à Digital Gangster

| Année | Cible                                       | Effet                                              |
| ----- | ------------------------------------------- | -------------------------------------------------- |
| 2005  | **Paris Hilton T-Mobile breach**            | Dump du Sidekick&nbsp;:&nbsp;photos, contacts, SMS |
| 2008  | **Miley Cyrus email**                       | Compte hacké, photos personnelles leakées          |
| 2009  | **Twitter accounts of Barack Obama et al.** | Mass account takeover                              |
| 2014  | **Craigslist DNS hijacking**                | Redirect du domain entier                          |

Source&nbsp;: [YTCracker&nbsp;—&nbsp;Wikipedia](https://en.wikipedia.org/wiki/YTCracker)

### Pourquoi ce forum est central

Digital Gangster est le _Reddit_ du 0day _underground_ 2005-2017. Ce que **`/b/`** était à 4chan, ce que **Bugtraq** était à l'industrie, _DG_ l'était à la scène _grey hat_ américaine de cette décennie.

C'est ce que le Holy Book invoque en filigrane quand il écrit «&nbsp;_Putains de skids, putains de normies_&nbsp;», c'est le vocabulaire natif de DG.

### Le pont vers Yung Innanet, le «&nbsp;_DG descendant_&nbsp;»

Le Holy Book cite `true colors` en ajoutant&nbsp;:&nbsp;«&nbsp;_(btw: RIP, DG descendant…)_&nbsp;». «&nbsp;_DG_&nbsp;» désigne **Digital Gangster**, l'auteur signale ainsi que **Yung Innanet (kayos)** est un héritier de cette scène.

Officiellement, DG ferme en 2017 et kayos émerge vers 2019 avec VXUG, mais il était tout de même présent sur le Discord qui a suivi, sous le pseudo _Yung Snat_. Il revendique lui-même cette filiation dans [`/issues/trust`](https://soundcloud.com/queed-inc/issues)&nbsp;:&nbsp;«&nbsp;_I'm representing the DG descendant_&nbsp;».

Une de ses signatures, c'est d'insulter Windows&nbsp;:&nbsp;il revient constamment sur le fait de le "down" (tuer) sans regret. On le retrouve aussi cité dans [_Retarded_](https://soundcloud.com/spokepp4l/retarded), comme ayant été aux côtés de _Jewbird_ et d'_Atmos The ILLKid_, dans le contexte d'un concours EFnet «&nbsp;_célébrant les particularités et différences de chacun, ce qui maintient EFnet aussi exceptionnel qu'étrange_&nbsp;»&nbsp;:&nbsp;«&nbsp;_Bumping yung innanet windows down no regrets_&nbsp;».

Dans [`shadow`](https://soundcloud.com/queed-inc/shadow), même motif, formulé autrement&nbsp;:

> _When them shots rang out I suggest you avoid Windows_  
> _I suggest you avoid Windows_  
> _I suggest you avoid Windows_  
> _When them shots rang out I suggest you avoid Windows_  
> _I suggest you avoid Windows_  
> _I suggest you avoid Windows_

Pour rebondir sur _Retarded_, dans [`0101`](https://soundcloud.com/queed-inc/0101a), _Yung Innanet_ revendique aussi&nbsp;:

> Free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound  
> They gotta let my fuccin dogs out  
> Free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound

Après la mort tragique de _Yung Innanet_, _Jewbird_ a posté [`fr0z3n`](https://soundcloud.com/birdneststream/fr0z3n), une piste inédite que kayos avait lui-même partagée sur IRC vers 2020, en attendant que la partie de YTCracker soit prête&nbsp;:

> rip kayos&nbsp;—&nbsp;he put this link in irc and was waiting for yt to finish up his part, like around 2020 and it is a unreleased track so i put it here cuz it prob was not released lol

### Sensibilité partagée

La solitude, l'isolement, les morts, les addictions, les pertes de proches, les crises psychotiques, les cauchemars, et bien d'autres tragédies sont décrites **sans interruption** dans les musiques d'Atmos et de Yung Innanet.

Atmos, quant à lui, réapparait vers 2023 discrètement en tant que `0xDEADCAFE` et publie [_JUSTINE_](https://soundcloud.com/somta/justine), dont la description est&nbsp;:

> THIS IS THE TALE OF A HACKER THAT GOT STUCK IN THE MATRIX OF INFOSEC  
> JUSTINE IS A FICTIONAL CHARACTER THAT REPRESENT HIS ADDICTION TO DRUGS AND ALCOHOL  
> ONE OF MANY BUT MORE LUCKY THAN OTHER RIP TO ALL THE NURGA WE LOST RIP STARBROTHER , WOJTEK , dreadz all all others
>
> The sad reality is that addiction, drugs abuse is something that took the life of so many hackers .

Les thèmes de la solitude, de la misère sexuelle, de la misère urbaine, de l'errance intérieure&nbsp;/&nbsp;détresse mentale, des addictions, de la criminalité, des regrets et de l'instabilité reviennent de nouveau dans une chanson où l'on ressent qu'Atmos a tout de même pris en force depuis. C'est l'un de ses morceaux les plus accessibles&nbsp;:

> Free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound, free Atmos The ILLKid from the dog pound, free […]

> «&nbsp;_Justine, Justine, pourquoi t'as croisé ma vie&nbsp;? J'y croyais Justine, quand t'es là tu me donnes des amis […] Justine, Justine, j'pourrais te boire toute la nuit._&nbsp;»

> «&nbsp;_Ce milieu m'a impressionné, j'voulais atteindre la lune, mais à la place de tout ça j'ai fini entouré de bandits […]_&nbsp;»

> «&nbsp;_Toujours à deux battements de cœur de la crise cardiaque._&nbsp;»

> «&nbsp;_Mon portefeuille a déjà tenu la claque._&nbsp;»

> «&nbsp;_Si ta blonde est consentante, j'y mets la main, ça pelote._&nbsp;»

> «&nbsp;_La police m'arrêtera sur le fait._&nbsp;»

> «&nbsp;_Mon silence est assez large à cause des finances inarrêtables, ce qui me change en client désagréable. Ce monde m'a tout pris, où même mes femmes (fans&nbsp;?) m'incriminent, voici les histoires de problèmes apparents de l'homme invisible._&nbsp;»

> «&nbsp;_La vie vaut cher mais sur le marché noir l'argent me tente. Donc c'est pour son bien que ça fait onze ans que ma mère attend que je rentre._&nbsp;»

> «&nbsp;_Camisole de force, si le carnivore te croque._&nbsp;»

> «&nbsp;_Mais qu'est-ce que t'aurais fait à ma place&nbsp;?_&nbsp;»

> «&nbsp;_J'ai p'têt' braqué mais si tu savais combien j'ai payé de dettes._&nbsp;»

Juste avant de publier _JUSTINE_, toujours en tant que `0xDEADCAFE`, Atmos avait republié une piste de Yung Innanet en la renommant _PPL NOT GOOD_ (_people not good_).

> _People not good to eachother_
>
> _I said people not good to eachother_  
> _I said people not good to eachother_  
> _Could be your mother, be your sister, be your brother_  
> _Who gon be there when you go ducking for cover?_

C'est [_oblivion_](https://soundcloud.com/synrst/o-b-l-i-v-i-o-n)

Atmos annote ce repost tel que&nbsp;:

> _ALL CREDIT BELONG TO YUNG SNAT&nbsp;-&nbsp;I ONLY REMASTERED FOR MORE BASS_

_Yung Snat_ étant un des autres pseudos de Yung Innanet.

---

[_Atmos - cold loneliness_](https://soundcloud.com/mookl4f5/cold-loneliness), une piste très discrète et complètement incompréhensible à la première écoute, mais terriblement dense et lourde de sens, comme beaucoup d'autres que l'on retrouve aussi dans l'univers de la _Nerdcore_ qui laissent de côté l'informatique pour parler plus intimement&nbsp;:

> «&nbsp;_Froid de solitude, j'ai froid de solitude._&nbsp;»

> «&nbsp;_Est-ce que t'veux vraiment savoir à quel point on a morflé d'suite&nbsp;? Y fallait crissement qu'on tombe à terre, on s'est mis à s'battre comme des brutes._&nbsp;»

> «&nbsp;_J'aurais dû rester au Sino shop [magasin graffiti/street-art]. Devenu parano d'entendre, de le dire, y a une ombre avec machette qui m'suit ou pas&nbsp;?_&nbsp;»

> «&nbsp;_Mon cerveau c'est un ordi qui'arrête pas de lagguer, en plus d'être un camé aux feelings douteux. J'veux une biatch, avec elle dans un vol plané en Mini Cooper._&nbsp;»

> «&nbsp;_Direction Place Major [épicerie, quartier morne]._&nbsp;»

> «&nbsp;_J'ai rêvé de saccager un magasin de montres._&nbsp;»

> «&nbsp;_Des minutes fucking remplies, un salon désertique&nbsp;:&nbsp;[inventaire très sommaire…], plus une rallonge électrique._&nbsp;»

> «&nbsp;_Dix mois sans baiser […] 'va falloir être carrément actif plus, parce que même entouré je continue à vivre dans un froid d'solitude._&nbsp;»

> «&nbsp;_Des gargouilles qui m'attrapent les chevilles, m'emmènent en bas pour une vie nice [probablement des crises psychotiques réelles] […] il m'manque pas grand chose pour que j'm'entaille la jugulaire._&nbsp;»

> «&nbsp;_Mes minutes sont comptées, mais comment que ça se fait que c'est à chaque cinq s'condes&nbsp;? […] on m'a construit pour mieux me démolir, l'après c'comme un château de cartes._&nbsp;»

> «&nbsp;_Quand je dis "nous", c'est moi, je suis sociopathe._&nbsp;»

> «&nbsp;_Ils m'ont répété que l'amour me ferait du bien mais y a que d'calisse d'ingrats._&nbsp;»

> «&nbsp;_C'que j'ai besoin c'est d'une désintox'._&nbsp;»

> «&nbsp;_Un vrai criminel n'a plus souvent les mains propres_&nbsp;»

> «&nbsp;_Fucking based_&nbsp;»

> «&nbsp;_Il m'semble que j'allais mieux, j'tais un cobaye pour les nouvelles drugs._ J'ai perdu mon chemin, tu m'croises en jaquette bleue.&nbsp;»

> «&nbsp;_J'ai froid d'solitude, c'pas normal que j'habite tout seul pis qu'on s'entende pas&nbsp;!_&nbsp;»

Il parle aussi de tomber de fatigue de manière incontrôlée&nbsp;/&nbsp;de _black-outs_&nbsp;:

> «&nbsp;_'manquerait justement d'dormir sans fermer le fourneau._&nbsp;»

> «&nbsp;_J'me suis assoupi devant la TV, pis ya mon réveil, j'tais en train de pénétrer celle qu'on appelait AVATAR&nbsp;!_&nbsp;»

## 5. Le passage white hat

Vers 2015-2017, Bryce Case Jr. _bascule_ professionnellement&nbsp;:

- Consultant cybersec pour grandes entreprises.
- Continue de produire de la musique Nerdcore.
- Interview au **Shawn Ryan Show #85** (23 novembre 2023).
- Toujours présent comme artiste régulier à la **DEF CON** depuis 2011.
- Toujours un mentor adoré de nombreuses petites crapules (_dit avec tendresse ici_).

> But im a teacher of tactics spread solution  
> To students of the game though the fames elusive  
> Im banging crypto when im spitting acoustic  
> Cuz this game has got a case of the loose tip  
> Read between the lines draw conclusions  
> Lifting the shroud off these false illusions  
> This computer is a weapon of mine  
> And i can run the globe in polynomial time
>
> S&nbsp;P&nbsp;A&nbsp;M  
> Send it every day get paid and then  
> S&nbsp;P&nbsp;A&nbsp;M  
> Load another campaign and do it again

— [YTCracker, S&nbsp;P&nbsp;A&nbsp;M&nbsp;2](https://www.youtube.com/watch?v=SALLlcVYtYQ)

_(Musique faisant notamment suite à [**Still Spam**](https://www.youtube.com/watch?v=-zH_nQDZ10k) dans sa discographie, mais aussi à [**Life is an inbox**](https://www.youtube.com/watch?v=xoWkDSVORW0), entre autres.)_

Sa trajectoire est _le modèle_ que le Holy Book invoque implicitement&nbsp;:

> _De l'Enfer à là où nous en sommes aujourd'hui._
> _Sauvés par la Recherche, par de belles valeurs, par le travail ingrat._

C'est exactement Bryce.  
Transposé au contexte de l'auteur (exposition précoce à _YogyaCarderLink_)&nbsp;:

> «&nbsp;_De Zone-H à une vie rangée._&nbsp;»

## 6. Interviews

Deux long-format particulièrement documentés&nbsp;:

### Darknet Diaries, épisode 78&nbsp;—&nbsp;_Nerdcore_

- **Host**&nbsp;: Jack Rhysider.
- **Titre**&nbsp;: _Nerdcore_.
- **Transcript**&nbsp;: <https://darknetdiaries.com/transcript/78/>

C'est **la** référence audio sur YTCracker. Il y raconte son parcours&nbsp;:&nbsp;les hacks scolaires d'adolescent («&nbsp;_I hacked pretty much every school district in the state_&nbsp;»), les cibles institutionnelles («&nbsp;_I did the FAA, New York Department of Agriculture… pretty much every school district in Colorado_&nbsp;»), et la montée de la _Nerdcore_ («&nbsp;_the genre, right around I would say 2006, 2007, started to really kinda gain steam_&nbsp;»).

C'est l'épisode où l'on entend Bryce Case Jr. lui-même retracer la trajectoire _black hat 1999_&nbsp;→&nbsp;_nerdcore 2005_&nbsp;→&nbsp;_Digital Gangster_&nbsp;→&nbsp;_crypto /&nbsp;consulting_.

### Shawn Ryan Show, épisode 85 (23 novembre 2023)

Long-format vidéo (6h). Conversation plus large, format _talk-show américain_, présentée par Shawn Ryan (ex-Navy SEAL). Moins technique que Darknet Diaries, plus biographique. [Apple Podcasts](https://podcasts.apple.com/md/podcast/85-bryce-case-jr-aka-ytcracker-anonymous-hacker/id1492492083?i=1000635785028), [YouTube](https://www.youtube.com/watch?v=hFS7xONBJSE)

→ Pour comprendre la _scène_&nbsp;:&nbsp;Darknet Diaries.  
→ Pour comprendre la _personne_&nbsp;:&nbsp;Shawn Ryan Show.

## 7. `Cryptoilluminati` (2018)

> «&nbsp;_Told you to snap up a modest position_&nbsp;»  
> «&nbsp;_Of currency minted from factoring digits_&nbsp;»  
> «&nbsp;_Which of you listened?_&nbsp;»

[ytcracker - cryptoilluminati · YouTube](https://www.youtube.com/watch?v=_NL_B9MAKCw)

Le Holy Book reprend en français&nbsp;:

> «&nbsp;_Une belle avancée, portée par ces monnaies forgées de la factorisation des nombres._&nbsp;»

Placée dans la section où l'auteur évoque _Code is Law_ (Lessig 1999 /&nbsp;Ethereum 2015). YTCracker articule _déjà_ la même thèse mais en hip-hop&nbsp;:&nbsp;_la crypto est une avancée **scientifique**, méprisée par ceux qui n'ont pas écouté à temps_.

## 8. Filiation avec Ocarina

YTCracker fait par la musique ce qu'Ocarina fait par le _framework_&nbsp;:

| YTCracker                                             | Ocarina                                                                 |
| ----------------------------------------------------- | ----------------------------------------------------------------------- |
| Brutalement honnête, excellence technique             | Brutalement honnête, excellence technique                               |
| Reconverti à l'éthique sans renier le passé           | Code clean sans renier la posture _underground_                         |
| Mentor de la génération suivante (Ryan Montgomery)    | _Manifeste_ adressé à la génération suivante                            |
| «&nbsp;_I'm the null at the end of the string_&nbsp;» | «&nbsp;_Je suis le bug dont tu ne pourras jamais te débarrasser_&nbsp;» |
| _Robots Will Definitely Take Your Job_                | _ocarina-with-ai-example_ (99% Claude)                                  |

## 9. Pour aller plus loin

### Autres musiques

| Titre                                | Note                                                                                                                                         |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Take a knee                          | [YouTube](https://www.youtube.com/watch?v=Cf_XhKE4R_o)                                                                                       |
| The Legend                           | [YouTube](https://www.youtube.com/watch?v=9_rR-0guirs)                                                                                       |
| Paint                                | [YouTube](http://youtube.com/watch?v=TS5MUf14gDw)                                                                                            |
| Kacho On!                            | [Soundcloud](https://soundcloud.com/scrubclub/2-mello-kacho-on-feat-ytcracker)                                                               |
| Friend zone                          | [Soundcloud](https://soundcloud.com/ytcracker/ytcracker-friend-zone)                                                                         |
| California Breeze                    | [YouTube](https://www.youtube.com/watch?v=-jn6cT6ZqX0)                                                                                       |
| Subnet mask off                      | [YouTube](https://www.youtube.com/watch?v=1YW_6OXYB7E), reprise par Yung Innanet, [mvsk (Soundcloud)](https://soundcloud.com/queed-inc/mvsk) |
| Toolin' up                           | [Soundcloud](https://soundcloud.com/ytcracker/ytcracker-toolin-up)                                                                           |
| Bazaar                               | [YouTube](https://www.youtube.com/watch?v=X6t3CVafuec)                                                                                       |
| Bot in the cut                       | [Soundcloud](http://soundcloud.com/hairetsu/ytcracker-and-hairetsu-bot-i)                                                                    |
| Terminal                             | [YouTube](https://www.youtube.com/watch?v=WBcK-b7Wg1M)                                                                                       |
| Computer Crime                       | [YouTube](https://www.youtube.com/watch?v=2P0RcoY0Snc)                                                                                       |
| Fifty Thousand Dollar Friday         | [Soundcloud](https://soundcloud.com/ytcracker/ytcracker-and-hairetsu-fifty)                                                                  |
| We're Golden                         | [Soundcloud](https://soundcloud.com/rykg-263016260/ytcracker-were-golden-ft)                                                                 |
| Convalescence (remix de _Max James_) | [Soundcloud](https://soundcloud.com/maxjamesmusic/ytcracker-convalescence-max-james-remix)                                                   |
| Green Hat (remix de _Max James_)     | [Soundcloud](https://soundcloud.com/maxjamesmusic/ytcracker-green-hat-max-james-remix)                                                       |

### Le «&nbsp;_Spam Holy Book_&nbsp;»

[_The Book of Spam_](https://bkofspam.livejournal.com/)

### Mixtapes

[Des rediffusions de mixtapes réalisées par YTCracker en live sur Twitch sont disponibles sur YouTube, bien que la première qu'il ait faite pendant le Covid, absolument magnifique, a disparu.](https://youtu.be/Uo24VZK0znY?t=4116)

### Autres artistes

- [FreqyXin](https://soundcloud.com/freqyxin/bond-villain-girl)
- [dade (_Neals_ est un des autres surnoms donnés à YTCracker)](https://soundcloud.com/0xdade/0xdade-letter-to-neals)
- [hgc](https://soundcloud.com/888hgc/7variablesripyunginnanet)
- [hairetsu](https://soundcloud.com/hairetsu/friends-ive-worked-with-v1)
- [Scarlett Danger (_hautement confidentiel_)](https://soundcloud.com/scarlett_danger/the-tea)
