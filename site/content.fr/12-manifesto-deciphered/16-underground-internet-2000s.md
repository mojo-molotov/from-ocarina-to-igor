---
title: "12.16 — L'internet souterrain des années 1995-2010 : forums, outils, banalisation de la cruauté"
description: "Pour comprendre la rage qui traverse le Holy Book d'Ocarina, il faut comprendre ce qu'était vraiment internet avant Facebook (2006-2008), avant que Cloudflare ne devienne le gardien des portes (2010+), avant que la modération ne soit prise au sérieux. C'était un Far West où des compétences étatiques se développaient dans des chambres d'adolescents, où la vie privée d'un adversaire pouvait être démolie en 48 heures, et où les recours juridiques classiques étaient inopérants. Cette page décrit la mécanique, sans complaisance, sans héroïsation."
weight: 19
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 19
---

# 12.16&nbsp;—&nbsp;L'internet souterrain des années 1995-2010&nbsp;: forums, outils, banalisation de la cruauté

> Pour comprendre la rage qui traverse le Holy Book d'Ocarina, il faut comprendre **ce qu'était _vraiment_ internet** avant Facebook (2006-2008), avant que Cloudflare ne devienne le _gardien des portes_ (2010+), avant que la _modération_ ne soit prise au sérieux. C'était un _Far West_ où des compétences étatiques se développaient dans des chambres d'adolescents, où la _vie privée_ d'un adversaire pouvait être démolie en 48 heures, et où les recours juridiques classiques étaient **inopérants**. Cette page décrit la mécanique, sans complaisance, sans héroïsation.

> ⚠️ Cette page documente des **techniques historiques** à des fins éducatives et de mise en contexte du manifeste. Il **ne donne pas de mode opératoire** et **ne fait pas l'apologie** d'actes illégaux. La cruauté décrite a fait des **victimes réelles**.

## 1. Archéologie

### Les couches successives

| Période   | Stack dominante                                                                               | Anonymat                                             | Sphère sociale                       |
| --------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------ |
| 1979-1995 | **Usenet, BBS, FidoNet**                                                                      | Fort (pseudo, pas d'IP traçable côté utilisateur)    | Petite (universitaires, amateurs PC) |
| 1995-2002 | **IRC, Web 1.0, mailing lists, AIM/ICQ**                                                      | Fort (proxy chains, dial-up IP dynamique)            | Croissante (15-100M utilisateurs)    |
| 2002-2008 | **Forums phpBB, Web 2.0 naissant, IRC encore central**                                        | Modéré (logs IRC archivés, dox encore plus facile)   | Massive (le _grand public_ arrive)   |
| 2008-2014 | **Facebook&nbsp;+&nbsp;Twitter dominants, IRC et forums en déclin, heure de gloire de 4chan** | Faible (mais 4chan persiste sur l'anonymat assumé)   | Tout le monde                        |
| 2014+     | **Smartphone-first, modération industrialisée, _Cloud Act_, _informatique ubiquitaire_**      | Très faible (sauf Tor, sauf Signal, sauf VPN no-log) | Saturation                           |

### Usenet (~1979-2002)

**Usenet** est un système décentralisé de _newsgroups_&nbsp;:&nbsp;pas de serveur central, chaque serveur fonctionne par _peering_ avec d'autres, propagation des messages par réplication.

- **Hiérarchie de groupes**&nbsp;:&nbsp;`comp.lang.c`, `alt.hacker`, `rec.games.*`, `sci.crypt`, `alt.binaries.*` (warez, scans, etc.).
- **Pas de modération centrale**&nbsp;:&nbsp;chaque serveur peut être coupé, mais les autres répliquent.
- **Persistance**&nbsp;:&nbsp;un message Usenet bien posté reste **indéfiniment** archivé.
- **Killfiles**&nbsp;:&nbsp;l'utilisateur _modère lui-même_ en ignorant des auteurs.
- **Flame wars**&nbsp;:&nbsp;les disputes pouvaient durer des semaines, des centaines de messages, et ressurgir 10 ans plus tard quand quelqu'un retrouvait un thread.

### BBS (Bulletin Board Systems, 1979-mid-1990s)

**BBS**&nbsp;=&nbsp;serveur dial-up auquel on se connecte avec un modem pour lire/poster sur des _boards_ thématiques. _Local_&nbsp;:&nbsp;pas d'internet, juste d'un téléphone à un PC dans la chambre d'un autre adolescent.

C'est la **matrice originelle** de la culture hacker américaine. Tous les acteurs documentés dans ce précis (YTCracker, kayos, Sys64738, etc.) sont passés par là ou par ses héritiers directs.

### IRC (Internet Relay Chat, 1988-aujourd'hui)

**IRC**&nbsp;=&nbsp;protocole de chat textuel multi-canal, multi-serveur, fortement décentralisé. Cf. [`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)

- Canaux thématiques (`#hack`, `#warez`, `#cracking`, `#defcon`, `#anonymous`...).
- Pseudos modifiables.
- _Ops_ (administrateurs de canal) qui décident des kick/ban.
- _DCC_ (Direct Client-to-Client) pour transférer des fichiers sans passer par le serveur.
- _Bots_ omniprésents&nbsp;:&nbsp;`eggdrop`, _channel bots_ qui surveillent, kickent les _flooders_, partagent des fichiers.

## 2. La trousse à outils du nuisible

Ce qui suit est un **catalogue documentaire**, chaque terme correspond à une pratique réellement courante sur les forums _underground_ de l'époque.

### Doxing

**Doxing** (de _documents_&nbsp;→&nbsp;_dox_)&nbsp;:&nbsp;publication de toutes les informations personnelles d'une cible. Nom légal, adresse, téléphone, employeur, parents, enfants, écoles, immatriculation auto, numéros de sécu, mots de passe leakés, photos. Régulièrement agrémenté de diffamation (accusations de pédophilie, etc.).

1. _Pivot_ depuis un pseudo unique vers un compte sur un autre forum mal anonymisé.
2. _Cross-reference_ des _data leaks_ disponibles (_Have I Been Pwned_, _LinkedIn 2012_, _Yahoo 2013_, _et al._).
3. _OSINT_ (Open Source Intelligence), agrégation de tout ce qui est public&nbsp;:&nbsp;registre du commerce, archives municipales, profils LinkedIn/Facebook/Instagram, _whois_ de domaines, photos avec EXIF GPS.
4. _Social engineering_&nbsp;:&nbsp;appels au support technique des opérateurs téléphoniques, faux services clients, utilisation de _prétextes_.
5. _Publication_&nbsp;:&nbsp;_doxbin_, pastebin, forums ou équivalent.

**Effet sur la victime**&nbsp;:&nbsp;harcèlement physique (envois de pizzas au mieux, produits illicites en masse pour provoquer une alerte chez les douanes au pire, annonces factices de décès à des proches, chantage, etc.), _swatting_, usurpation d'identité, harcèlement de l'employeur.

### Swatting

**Swatting**&nbsp;:&nbsp;appel mensonger aux forces de l'ordre en se faisant passer pour la victime, un membre de sa famille ou un conjoint, déclarant une prise d'otage ou un meurtre en cours à son adresse, déclenchant l'envoi du **SWAT** (équipe d'assaut armée).

**Mécanique**&nbsp;:

- Caller ID spoofé ou appel Skype avec des crédits obtenus via du _carding_.
- Adaptation du ton de la voix, détails crédibles (références à l'adresse exacte, descriptions d'armes et/ou de situations d'urgence).
- La police défonce la porte, parfois tire, il y a eu **des morts confirmés** suite à des _swattings_ (Andrew Finch, Wichita Kansas, le soir du 28 décembre 2017, abattu à sa porte, alors âgé de 28 ans).
- _Coût_ pour la victime&nbsp;:&nbsp;choc psychologique majeur, parfois blessures physiques, parfois la mort.
- _Coût_ pour l'auteur&nbsp;:&nbsp;peines de prison réelles si identifié (Tyler Barriss&nbsp;:&nbsp;20 ans pour le swatting Finch).

### Caller ID spoofing via SIP

**SIP** (Session Initiation Protocol) est le protocole VoIP standard depuis ~2003. Avec un fournisseur SIP _low-cost_ (à l'étranger, faible KYC), on peut **envoyer un appel** avec un caller ID **arbitraire**&nbsp;:&nbsp;n'importe quel numéro de téléphone du monde s'affiche chez le destinataire de l'appel.

Usages malveillants&nbsp;:

- Swatting (vu ci-dessus).
- _Voice phishing_ (vishing)&nbsp;:&nbsp;se faire passer pour le service client de la banque.
- Faux appels d'urgence vers une cible pour la faire réagir publiquement.
- Harcèlement d'autres personnes en usurpant le numéro de la cible pour provoquer des règlements de comptes.
- _Caller ID poisoning_&nbsp;:&nbsp;spammer des numéros différents toutes les heures pour saturer la victime.

Légalement&nbsp;:&nbsp;**fortement régulé** depuis 2019 aux USA (STIR/SHAKEN), encore largement utilisable depuis l'étranger.

### Malware signé sur une machine baptisée du nom de l'ennemi

Technique opérationnelle&nbsp;:&nbsp;on _compile_ un malware sur une machine dont le hostname, le nom d'utilisateur, le _path de build_, contiennent le nom d'un journaliste, d'un chercheur en sécurité, d'un membre de la communauté qu'on veut **humilier ou impliquer**. Quand le malware est analysé par une sandbox ou un AV, les artefacts du build (chaîne `Built on: /home/journaliste_X/...`) traînent dans le binaire et déclenchent les **algorithmes d'attribution** à la mauvaise personne.

C'est une opération **false flag** au sens littéral. Des groupes **APT** (Advanced Persistent Threat) russes l'ont popularisée à l'échelle étatique (cf. _Olympic Destroyer_, 2018, attribué à tort à la Corée du Nord pendant des mois). Cette **technique** a été apprise dans les forums _underground_ des années 2000.

### Usurpation d'identité&nbsp;+&nbsp;souscriptions à des crédits

Avec un _dox_ complet, on peut&nbsp;:

1. Ouvrir des comptes bancaires en ligne avec les KYC les plus laxistes.
2. Souscrire à des crédits à la consommation chez les organismes peu regardants.
3. Faire des achats en ligne livrés à des _drops_ (adresses tierces).
4. Détruire le _credit score_ de la victime en accumulant les défauts de paiement.

Conséquences pour la victime&nbsp;:&nbsp;**des années** de procédure pour rétablir sa solvabilité, parfois interdiction bancaire, parfois impossibilité de louer un appartement.

### Hacktivisme

**Hacktivisme**&nbsp;=&nbsp;activisme par le hack. Exemples&nbsp;:

| Acteur                                | Action                                                                |
| ------------------------------------- | --------------------------------------------------------------------- |
| **Cult of the Dead Cow** (cDc, 1984+) | Back Orifice (1998), Telecomix (libérations syriennes 2011)           |
| **Anonymous** (originaire de 4chan)   | Op Chanology (Scientologie 2008), Op Tunisia (2011), Op Sony (2011)   |
| **LulzSec** (mai-juin 2011)           | 50 jours d'action publique, Sony, HBGary, FBI affiliates, Arizona DPS |
| **AntiSec** (2011)                    | Phase d'Anonymous&nbsp;+&nbsp;LulzSec                                 |
| **WikiLeaks** (Assange, 2006+)        | Diplomatic cables 2010, Vault 7 (CIA tools) 2017                      |

L'hacktivisme est **double**&nbsp;:

- **Public**&nbsp;:&nbsp;actions revendiquées avec manifestes, vidéos avec le masque de _Guy Fawkes_, communiqués.
- **Backstage**&nbsp;:&nbsp;coordination IRC, doxing interne, traîtres infiltrés (Sabu /&nbsp;Hector Monsegur, balance au FBI en 2011-2012), accusations croisées.

### Swatting&nbsp;+&nbsp;doxing&nbsp;+&nbsp;harcèlement _combinés_

L'attaque maximale combine les trois&nbsp;:&nbsp;on dox la cible, on appelle son employeur pour _révéler_ son passé, on harcèle ses proches, on _swat_ son domicile. Cas documentés&nbsp;:

- **Brianna Wu, Anita Sarkeesian, Zoë Quinn** (Gamergate, 2014-2015)&nbsp;:&nbsp;combinaison documentée publiquement.
- **Aaron Swartz** (2010-2013)&nbsp;:&nbsp;pas swatting mais harcèlement équivalent, suicide janvier 2013.

### Faux comptes, double comptes, lurk

- **Lurking**&nbsp;:&nbsp;être présent sur un forum sans poster. Permet d'**observer** les dynamiques, repérer les vulnérabilités sociales, identifier les cibles, archiver les preuves.
- **Faux comptes**&nbsp;:&nbsp;compte avec une identité inventée, parfois entretenu sur des années. Sert à _crédibiliser_ un narratif (faux témoignage, faux soutien).
- **Sockpuppet**&nbsp;/&nbsp;**double compte**&nbsp;:&nbsp;plusieurs comptes contrôlés par la même personne. Permet par exemple de _se répondre à soi-même_ pour créer l'illusion d'un consensus.

### Flame, griefers, trolls

| Terme       | Sens                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Flame**   | Insultes virulentes, souvent avec escalade, déclenchée par un désaccord mineur. Peut produire une _flame war_ de plusieurs jours ou plus.   |
| **Griefer** | Joueur en ligne (souvent MMO, parfois forums) dont l'objectif est de **gâcher** l'expérience des autres. Pas pour gagner, juste pour nuire. |
| **Troll**   | Fouteur de merde. Le _troll_ originel est moins méchant que ses descendants, mais l'évolution est toujours de pire en pire.                 |

### DB leaks

**Database leaks**&nbsp;:&nbsp;exfiltration et publication d'une base de données complète d'un service.  
Exemples&nbsp;:&nbsp;Ashley Madison (2015), LinkedIn (2012, republié en 2016), Yahoo (2013), Adobe (2013), Equifax (2017).

Effet&nbsp;:&nbsp;les utilisateurs de ces services voient leur email +&nbsp;mots de passe (parfois en clair à cause d'une mauvaise sécurisation en DB) +&nbsp;données privées **publiés et indexés**. _Have I Been Pwned_ (Troy Hunt, 2013+) répertorie 12+ milliards d'enregistrements à ce stade.

### Shodan&nbsp;+&nbsp;caméras et serveurs

**Shodan** (John Matherly, 2009, [`shodan.io`](https://shodan.io)) est un moteur de recherche pour les **devices connectés à internet**. Caméras IP, routeurs, ICS/SCADA industriels, serveurs FTP, serveurs MQTT, _et cetera_&nbsp;:

- `webcamxp`&nbsp;→&nbsp;caméras IP avec interface web par défaut, souvent sans mot de passe.
- `port:23`&nbsp;→&nbsp;serveurs Telnet ouverts (généralement IoT mal configurés).
- `default password`&nbsp;→&nbsp;indique les devices identifiés comme utilisant un mot de passe par défaut.

Avant Shodan, l'énumération demandait des _portscans_ massifs et coûteux. Avec Shodan, **en 5 secondes** on a 200 caméras non protégées dans n'importe quelle ville.

Shodan peut aussi être utilisé à des fins d'harcèlement diverses et variées, comme détecter des serveurs Minecraft mal sécurisés pour aller les détruire «&nbsp;entre amis _griefers_&nbsp;».

## 3. BOFH&nbsp;—&nbsp;_Bastard Operator From Hell_ (Simon Travaglia)

**BOFH** est une série de nouvelles écrites par **Simon Travaglia** (Nouvelle-Zélande), publiée sur **Usenet** à partir de **1992**, puis dans _Datamation_ et _The Register_.

Le narrateur est un sysadmin qui&nbsp;:

- _Méprise_ ses utilisateurs.
- _Sabote_ les machines des collègues énervants.
- _Falsifie_ les logs.
- _Tue_ littéralement les utilisateurs trop pénibles (avec humour noir&nbsp;:&nbsp;_accident d'ascenseur_, _piège dans la salle serveur_).
- _S'enrichit_ par fraude interne.

Le _BOFH_ est devenu un **archétype culturel**&nbsp;:

- **Connu** dans toute la communauté sysadmin.
- **Citations** intégrées au vocabulaire (`PEBKAC`&nbsp;=&nbsp;_Problem Exists Between Keyboard And Chair_, _RTFM_, _ID-10-T error_).
- **Idéalisé** par les sysadmins qui s'y reconnaissent ironiquement.

L'auteur d'Ocarina hérite en partie de cette tradition&nbsp;:&nbsp;«&nbsp;_slipologue_&nbsp;» est en quelque sorte la version 2020s du _PEBKAC_.

Dans la même lignée, lire aussi&nbsp;:&nbsp;[_Master Foo and the Script Kiddie (2003)_](https://rus-linux.net/MyLDP/BOOKS/ArtProgr/script-kiddie.html)

## 4. ViolVocal&nbsp;—&nbsp;le cas francophone

**ViolVocal** était une **communauté francophone** d'harceleurs en bande organisée, active dans les années 2000s. Forum&nbsp;+&nbsp;serveur vocal (Mumble /&nbsp;TeamSpeak) où les membres&nbsp;:

- Coordonnaient des **appels groupés** vers des cibles (rivaux, ex-membres, anonymes pris en photo).
- Utilisaient du _SIP spoofing_ pour appeler avec des numéros usurpés.
- Filmaient les réactions vocales des cibles et les rejouaient en _stream_ public.
- Pratiquaient le **harcèlement** au sens criminel&nbsp;:&nbsp;cibles harcelées pendant des semaines, dont des mineurs et des personnes vulnérables.

C'est l'une des **incarnations francophones** de la culture _no-limit_. VV a fini par fermer, certains membres ont été identifiés et poursuivis, mais **rien n'a permis de réparer** les dommages subis par les victimes.

**Pourquoi mentionner ViolVocal**&nbsp;:&nbsp;pour montrer que la cruauté _underground_ n'était _pas_ un phénomène uniquement anglophone. La même mécanique opérait en France, sur les serveurs Mumble francophones, dans les sous-forums de jeux MMO francophones, dans les chans IRC `#fr.*`. La _francophonie_ n'a pas été préservée.

## 5. 4chan et /b/&nbsp;—&nbsp;l'anonymat radical

**4chan**, fondé en 2003 par **Christopher «&nbsp;_moot_&nbsp;» Poole** (alors à l'âge de 15 ans), copie du japonais **2chan** (Hiroyuki Nishimura).

- **/b/** (_random_)&nbsp;:&nbsp;board sans règles, sans archive (les threads disparaissent après un certain nombre de pages), anonymat total (pas de pseudo persistant), volume massif (millions de messages/jour à son pic).
- **Anonymous** comme entité collective émerge littéralement de /b/ vers 2006-2008.
- _Memes_ produits en masse&nbsp;:&nbsp;Pepe, _LOLcats_, Rickroll, _Distracted Boyfriend_, sortent de /b/ et sont récupérés par le grand public.
- **Cruauté** documentée&nbsp;:&nbsp;raids organisés contre des cibles (parfois enfants suicidaires, anorexiques, etc.).
- **Pédocriminalité** documentée sur certains boards mineurs, ce qui a justifié les arrestations en série de moot et ses successeurs.

Le 14 avril 2025, 4chan a été massivement hacké&nbsp;:

- Accès administrateur
- Code source et autres données internes
- Identités
- ...

Aujourd'hui (2025-2026), 4chan existe encore mais a perdu sa centralité au profit de Discord, Reddit, Telegram, _et al._

## 6. La culture «&nbsp;_no limit_&nbsp;»&nbsp;—&nbsp;l'impunité par anonymat

### La perception subjective

Pour les nuisibles des forums _underground_ de l'époque&nbsp;:

| Sentiment                                    | Réalité                                                                                                            |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| «&nbsp;_Je suis intouchable_&nbsp;»          | Faux&nbsp;:&nbsp;les _logs IRC_ sont conservés des années, les bases sont leakées, l'_OPSEC_ est dure à maintenir  |
| «&nbsp;_Je peux tout faire_&nbsp;»           | Faux&nbsp;:&nbsp;il y a des limites légales, mais elles ne sont **pas immédiatement visibles** au moment de l'acte |
| «&nbsp;_Personne ne va me retrouver_&nbsp;»  | Faux&nbsp;:&nbsp;une IP, une timezone, une faute de frappe récurrente suffisent à des _intelligence agencies_      |
| «&nbsp;_C'est juste une private joke_&nbsp;» | Faux&nbsp;:&nbsp;les victimes subissent des conséquences **réelles**, parfois fatales                              |

1. **Anonymat technique** apparent (proxy, VPN, Tor).
2. **Distance** entre l'auteur (chez lui) et la victime (à l'autre bout du monde).
3. **Absence de réaction physique immédiate**&nbsp;:&nbsp;l'écran filtre, on ne voit pas la victime pleurer.
4. **Validation de pairs** sur le forum&nbsp;:&nbsp;les autres _félicitent_ les actes les plus «&nbsp;_audacieux_&nbsp;», constitutions de _tableaux de chasse_, échanges de «&nbsp;_kits d'harcèlement_&nbsp;».
5. **Échec systématique des forces de l'ordre** à intervenir rapidement, surtout lorsque l'harceleur et la victime ne sont pas dans le même pays.

### Pourquoi ça crée des _profils dangereux_

Cette combinaison produit des individus dotés de&nbsp;:

- Compétences **techniques** réelles (allant jusqu'à être d'un niveau étatique).
- **0 empathie** envers les victimes (jamais vues, «&nbsp;_'connait pas_&nbsp;»).
- **Mépris** structurel pour les institutions (vues comme lentes, stupides, corrompues).
- **Identité construite** autour de la «&nbsp;_prouesse_&nbsp;» anti-système.

## 7. L'inopérabilité des recours classiques

### «&nbsp;_Porter plainte contre son voisin_&nbsp;» ne marche plus

L'arsenal juridique européen et américain a été construit pour des sociétés où&nbsp;:

- Le voisin est **identifiable** (adresse postale, identité civile).
- Le préjudice est **circonscrit** géographiquement.
- Les preuves sont **physiques** (témoignages, photos, lettres).
- L'État a **juridiction** sur l'auteur.

Aucune de ces hypothèses ne tient pour un harcèlement _underground_ en ligne&nbsp;:

- L'auteur est **anonyme** par construction.
- Le préjudice est **globalisé**&nbsp;:&nbsp;la victime peut être en France, l'auteur en Russie, le serveur aux Bahamas.
- Les preuves sont **numériques**, donc fabricables, supprimables, contestables.
- L'État de la victime n'a **aucune juridiction** sur l'auteur étranger.

Une victime de doxing/harassment qui porte plainte se retrouve souvent avec&nbsp;:

1. Plainte _classée sans suite_ par manque d'identification.
2. Plainte _transférée_ à une autre juridiction qui la classe aussi.
3. Plainte _rejetée_ pour incompétence territoriale.
4. Coût _moral_ et _financier_ d'avoir tenté la procédure.

### La _vendetta privée_ devient la norme

Quand le système judiciaire est inopérant, le _conflit_ se résout par&nbsp;:

- **Contre-doxing**&nbsp;:&nbsp;la victime, ou un allié, dox l'auteur en retour.
- **Contre-attaque** technique&nbsp;:&nbsp;DDoS, deface, exfiltration.
- **Public shaming**&nbsp;:&nbsp;exposition publique sur Twitter, Reddit, médias (_call-out_).
- **Hacker tribunals/syndicates informels**&nbsp;:&nbsp;un groupe respecté dans la scène _juge_ et _excommunie_ l'auteur.

Ces résolutions sont **violentes**, **non-réversibles**, et **les plus violentes possible**.  
Elles _existent_ **parce que rien d'autre ne marche.**

## 8. Les forums marchands

À partir de ~2005-2008, les forums _underground_ passent d'une logique de _partage_ à une logique de _commerce_&nbsp;:

| Marché                                                    | Période                        | Plateformes                                                                 |
| --------------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------------- |
| **Carding**&nbsp;:&nbsp;vente de numéros de cartes volées | Dès 1999 (forums), 2011+ (Tor) | ShadowCrew, Carder.su, Silk Road, etc.                                      |
| **Exploits 0day**                                         | 2005+                          | Forums, Tor, puis _exploit-as-a-service_ (Zerodium, etc.)                   |
| **Botnets**                                               | 2007+                          | Vente d'accès à _10&nbsp;000+ machines compromises_ pour DDoS, spam, mining |
| **Malware-as-a-service**                                  | 2010+                          | On paie pour utiliser un malware                                            |
| **Doxing-as-a-service**                                   | 2010+                          | _dox-for-hire_&nbsp;:&nbsp;commande un dox sur n'importe qui                |

### Cerveaux et exécutants

Les forums marchands **séparent**&nbsp;:

1. Le **cerveau**&nbsp;:&nbsp;celui qui développe la technique.
2. L'**exécutant**&nbsp;:&nbsp;celui qui paie pour utiliser la technique sur sa cible.

Cette séparation a fait **exploser** le nombre de victimes&nbsp;:&nbsp;avant, il fallait être _capable_ techniquement pour faire du mal. Depuis, **n'importe qui avec quelques dollars** pouvait lancer une attaque ciblée.

On retrouve le même pattern avec _The Anarchist Cookbook_ (William Powell, 1971), qui publiait des instructions pour fabriquer des bombes artisanales, sauf que l'_Anarchist Cookbook_ produisait quelques cas isolés, alors que les forums marchands _underground_ produisaient **des milliers** de victimes par mois.

### Parallèle Anarchist Cookbook

| Aspect             | Anarchist Cookbook (1971)    | Forums _underground_ (2005+)                          |
| ------------------ | ---------------------------- | ----------------------------------------------------- |
| Objet vendu        | Instructions papier          | Outils logiciels +&nbsp;tutos                         |
| Audience cible     | Adolescents en colère        | Adolescents en colère +&nbsp;criminels organisés      |
| Coût               | 0 (PDF ou bibliothèque)      | 50-5000+&nbsp;$                                       |
| Risque de mésusage | Élevé (bombes _réelles_)     | Élevé (vies _réelles_ détruites)                      |
| Réponse étatique   | Surveillance                 | Surveillance (arrestations rares)                     |
| Effet long terme   | Toujours partagé aujourd'hui | Forums de plus en plus _underground_, marchés sur Tor |

Le **point commun** est **la démocratisation d'une capacité de nuisance qui demandait avant des années d'apprentissage.**

## 9. Pourquoi cet univers a engendré des compétences dignes de services de _renseignement_

Pour _survivre_ en tant que membre actif d'un forum _underground_, il fallait développer&nbsp;:

| Compétence                                     | Application                                                                                           |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **OPSEC**&nbsp;—&nbsp;Operations Security      | Maintenir l'anonymat sur 5-10 ans, pas une seule fuite                                                |
| **OSINT**&nbsp;—&nbsp;Open Source Intelligence | Doxer une cible à partir de presque rien                                                              |
| **Social engineering**                         | Manipuler un humain (support technique, ex-amie de la cible, employeur)                               |
| **Surveillance**&nbsp;—&nbsp;_eyes everywhere_ | Garder un œil sur tous les forums où son pseudo apparaît, les bases leakées, les screenshots, tout    |
| **Counter-intelligence**                       | Détecter les _infiltrés_ (forces de l'ordre, chercheurs, ennemis) qui se font passer pour des membres |
| **Influence operations**                       | Coordonner un raid sur plusieurs plateformes simultanément, construire un narratif                    |
| **Forensics**&nbsp;—&nbsp;anti-forensics       | Effacer ses traces, brouiller les pistes, créer de fausses traces                                     |
| **Crypto**&nbsp;—&nbsp;pratique, pas théorique | Chiffrement de bout en bout, GPG, etc                                                                 |

Ces compétences sont **identiques** à celles d'un opérateur de renseignement étatique.  
Les agences (NSA, FSB, MSS, DGSI, GCHQ) **embauchent** dans cette scène depuis 2005 minimum, et les meilleurs profils _viennent_ de là.

## 10. Pourquoi des «&nbsp;_ennemis_&nbsp;»&nbsp;?

L'auteur du Holy Book emploie le mot **ennemi**.  
Ce n'est pas une métaphore.

Dans ce monde, on a des _ennemis_ au sens **opérationnel**&nbsp;:

- Personnes qui ont **doxé** l'auteur ou ses proches.
- Personnes qui ont **dénoncé** publiquement, qui ont **menti** sur ses actes, qui ont **tenté de l'humilier**.
- Communautés qui ont **organisé** des raids coordonnés contre la scène à laquelle il appartient.
- Forces de l'ordre qui servent à rien.

Quand on a _vécu_ ces opérations, on n'utilise plus le mot _adversaire_ ou _opposant_. On dit **ennemi**, parce que c'est ce que c'est&nbsp;:&nbsp;quelqu'un qui veut provoquer une **destruction** (sociale, professionnelle, parfois physique) et qui agit pour l'obtenir.

Cf. [`17-survivor-psyche-programming.md`](17-survivor-psyche-programming.md)

## 11. Connexions avec le reste du précis

- [`02-lulzsec-lulzboat-antisec.md`](02-lulzsec-lulzboat-antisec.md)&nbsp;—&nbsp;LulzSec /&nbsp;AntiSec, hacktivisme organisé.
- [`03-ytcracker-nerdcore-digital-gangster.md`](03-ytcracker-nerdcore-digital-gangster.md)&nbsp;—&nbsp;DG, le forum-référence.
- [`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)&nbsp;—&nbsp;IRC, EFnet, Zone-H.
- [`05-indonesian-hackers.md`](05-indonesian-hackers.md)&nbsp;—&nbsp;YogyaCarderLink, carding & defacement.
- [`17-survivor-psyche-programming.md`](17-survivor-psyche-programming.md)&nbsp;—&nbsp;conséquences psychologiques et techniques.
