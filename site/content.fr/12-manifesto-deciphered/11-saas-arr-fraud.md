---
title: "12.11 — L'industrie SaaS, la fraude à l'ARR, jeu de dupes"
description: "Pourquoi Ocarina rejette le SaaS : un écosystème circulaire où le revenu déclaré est gonflé par convention, décrit comme un jeu de dupes."
weight: 11
date: 2026-05-20
series: ["analyse-manifeste"]
series_order: 11
---

# 12.11&nbsp;—&nbsp;L'industrie SaaS, la fraude à l'ARR, jeu de dupes

> Ocarina **rejette le SaaS**. L'industrie du SaaS est un **écosystème circulaire** où chaque outil vend à chaque autre outil, où le revenu déclaré est gonflé par convention, et où chaque étage de la chaîne capitalistique (LP, VC, founder) entretient sciemment une **plausible deniability** pour pouvoir attaquer les autres en justice le moment venu.

## 1. Le SaaS contemporain

| Couche         | Fournisseurs (échantillon)                                    | Modèle                                     |
| -------------- | ------------------------------------------------------------- | ------------------------------------------ |
| Hosting & CDN  | **Vercel, Netlify, Cloudflare, Fly.io, Render**               | Abonnement par projet /&nbsp;par bandwidth |
| DB             | **Supabase, Neon, PlanetScale, Upstash, MongoDB Atlas**       | Abonnement par compute /&nbsp;par GB       |
| Auth           | **Clerk, Auth0, WorkOS, Stytch**                              | Abonnement par MAU                         |
| Mail           | **Resend, SendGrid, Postmark, Mailgun**                       | Abonnement par mail envoyé                 |
| Analytics      | **PostHog, Mixpanel, Amplitude, Plausible, Vercel Analytics** | Abonnement par event                       |
| Error tracking | **Sentry, BugSnag, Rollbar, Highlight**                       | Abonnement par event                       |
| Observability  | **Datadog, New Relic, Honeycomb, Grafana Cloud, Axiom**       | Abonnement par metric volume               |
| Feature flags  | **LaunchDarkly, GrowthBook, Statsig, ConfigCat**              | Abonnement par MAU                         |
| Test e2e       | **BrowserStack, Sauce Labs, LambdaTest, Cypress Dashboard**   | Abonnement par run /&nbsp;par parallel     |
| CI             | **GitHub Actions, CircleCI, Buildkite, Vercel CI**            | Abonnement par minute                      |
| Code review    | **Graphite, Codeball, CodeRabbit, Sourcery**                  | Abonnement par PR /&nbsp;par dev           |
| Comms internes | **Slack, Linear, Notion, Figma, Loom, Pitch**                 | Abonnement par seat                        |
| Billing        | **Stripe, Lago, Orb, Metronome**                              | % du revenu traité                         |
| CRM            | **HubSpot, Salesforce, Attio, Pipedrive**                     | Abonnement par seat                        |
| Support        | **Intercom, Zendesk, Plain, Help Scout**                      | Abonnement par seat + par message          |
| AI tooling     | **OpenAI, Anthropic, Cursor, Vercel AI SDK, Replicate**       | Abonnement par token + par seat            |

## 2. Abonnements croisés

```
   ┌──────────┐ paie     ┌──────────┐
   │ Vercel   │─────────>│ Stripe   │
   │          │<─────────│          │
   └──────────┘     paie └──────────┘
        │                     │
   paie │                     │ paie
        v                     v
   ┌──────────┐          ┌──────────┐
   │ Linear   │<────────>│ Notion   │
   └──────────┘  paient  └──────────┘
        │                     │
        v                     v
   ┌───────────────────────────────┐
   │ Slack, Figma, Loom, Sentry,   │
   │ Datadog, Clerk, Cursor, …     │
   │ tous abonnés à tous           │
   └───────────────────────────────┘
```

- **Vercel** paie un abonnement à _Stripe_ (billing), _Datadog_ (obs), _Linear_ (planning), _Figma_ (design), _Loom_ (présentations internes), _Slack_ (comms), _Notion_ (docs).
- **Stripe** paie un abonnement à _Vercel_ (hosting pour ses dashboards), _Linear_, _Figma_, _Slack_…
- **Linear** paie un abonnement à _Vercel_, _Stripe_, _Notion_, _Figma_, _Slack_.
- **Notion** paie un abonnement à _Linear_, _Stripe_, _Slack_, _Figma_.

Et ainsi de suite. **Tout le monde paie tout le monde.**

## 3. MRR&nbsp;→&nbsp;ARR et _fraude par convention_

### Définitions

| Terme   | Définition                                                                                                                                                                                |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MRR** | _Monthly Recurring Revenue_, la somme mensuelle facturée aux clients sous abonnement                                                                                                      |
| **ARR** | _Annual Recurring Revenue_, la somme annuelle facturée aux clients sous abonnement. Souvent, le MRR projeté sur un an&nbsp;:&nbsp;**`ARR = MRR × 12`**, ce qui est franchement frauduleux |

### Fraude conventionnelle

`ARR = MRR × 12` est une **vue de l'esprit**&nbsp;:

1. **MRR contient des plans annuels prépayés** divisés par 12. Si un client paie 12&nbsp;000&nbsp;€ en une fois pour l'année, certains comptent +1&nbsp;000&nbsp;€ de MRR. S'il _churn_ (se désabonne) au 3ème mois, le «&nbsp;_MRR_&nbsp;» n'a jamais été _récurrent_.
2. **MRR contient des promos /&nbsp;discounts ignorés**. Un client à 50&nbsp;% de réduction sur 6 mois est compté à plein tarif dans le MRR chez certains.
3. **L'ARR projeté ignore le churn**. La _projection ARR_ suppose 0 churn, alors que le churn réaliste en SaaS B2B/B2C est imprévisible.
4. **MRR contient des utilisateurs optimistes après avoir essayé le _free-tier_**. Un _trial_ qui passe en _paid_ est compté immédiatement comme MRR perpétuel.
5. **Les _upsells_ futurs sont parfois inclus** dans certaines présentations d'ARR («&nbsp;_net new ARR_&nbsp;», «&nbsp;_expansion ARR_&nbsp;»).

Résultat&nbsp;:&nbsp;un MRR de 100&nbsp;K€ peut produire un **ARR déclaré** de 1,2&nbsp;M€ alors que le revenu **réel** annualisé sera, peut-être, 600-800&nbsp;K€.

### Pourquoi personne ne le dit

Parce que **personne n'a intérêt à le faire**.  
Les incitations alignent tout le monde sur l'inflation&nbsp;:

| Acteur                                             | Bénéfice d'un ARR gonflé                                                                             |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Founder**                                        | Valorisation plus haute à la prochaine levée de fonds. Salaire de série A+. Options qui valent plus. |
| **VC (associé)**                                   | _Mark-to-market_ de son portefeuille plus élevé&nbsp;→&nbsp;bonus _carried interest_ déclaré aux LPs |
| **VC (fonds)**                                     | Meilleur _track record_ pour lever les prochains fonds                                               |
| **LP** (assureurs, _endowments_, fonds de pension) | Performance déclarée plus haute&nbsp;→&nbsp;bonus du gestionnaire d'allocation                       |
| **Banque/lender** (venture debt)                   | Couverture _ARR_ plus large&nbsp;→&nbsp;prêt accordé                                                 |
| **Acheteur potentiel (M&A)**                       | Justifie le _premium_ qu'il paie auprès de _son_ conseil d'administration                            |
| **Employés** (vesting d'options)                   | _Strike_ qui semble bas par rapport à la valorisation suivante                                       |

## 4. Le jeu de dupes, _plausible deniability_

Le mécanisme frauduleux fonctionne tant qu'il _grossit_. Le moment où ça casse (récession, taux qui montent, IPO ratée, audit), il faut pouvoir **se retourner**. Chaque étage a donc construit, dès le départ, une _plausible deniability_&nbsp;:

```
┌─────────────────────────────────────────────────────────────┐
│ LP (Limited Partner)                                        │
│ "Le VC m'a présenté un mark-to-market. Je l'ai cru. Je      │
│ suis une victime."                                          │
└────────────────┬────────────────────────────────────────────┘
                 │ porte plainte ↓
                 v
┌─────────────────────────────────────────────────────────────┐
│ VC (General Partner)                                        │
│ "Le founder m'a présenté ses chiffres ARR. Je les ai pris   │
│ tels quels. C'est lui le "representations & warranties".    │
└────────────────┬────────────────────────────────────────────┘
                 │ porte plainte ↓
                 v
┌─────────────────────────────────────────────────────────────┐
│ Founder                                                     │
│ "Mon CFO a calculé. Mes auditeurs ont validé. J'ai signé    │
│ ce que mes équipes ont produit."                            │
└────────────────┬────────────────────────────────────────────┘
                 │ porte plainte ↓
                 v
┌─────────────────────────────────────────────────────────────┐
│ CFO / Auditeur (Big 4)                                      │
│ "Le founder a fourni les data. J'ai appliqué les standards  │
│ comptables. Si la définition de MRR était floue, c'est le   │
│ cadre US-GAAP / IFRS qui est flou."                         │
└─────────────────────────────────────────────────────────────┘
```

Chacun se laisse une _porte de sortie juridique_&nbsp;:&nbsp;«&nbsp;_je ne savais pas, on m'a présenté ces chiffres, c'est `<étage en dessous>` qui ment_&nbsp;».

_Note&nbsp;:&nbsp;ce schéma est une caricature volontaire du mécanisme de plausible deniability.
La réalité juridique est plus désordonnée&nbsp;:&nbsp;les poursuites ne descendent pas
systématiquement de palier en palier, la SEC ou le DoJ interviennent souvent
directement sans suivre cet ordre. La structure reste néanmoins représentative
des incitations à l'auto-protection de chaque étage._

---

Cas d'école documentés publiquement&nbsp;:

| Cas                         | Mécanisme                                                                                    | Conséquence                                                                       |
| --------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **WeWork (2019)**           | Métrique inventée «&nbsp;_community-adjusted EBITDA_&nbsp;»                                  | IPO retirée en 2019 (cotation finalement via SPAC en 2021), Adam Neumann remplacé |
| **FTX (2022)**              | _Mark_ de tokens illiquides comme _revenue_                                                  | Faillite, Sam Bankman-Fried condamné                                              |
| **Frank /&nbsp;JPM (2023)** | Charlie Javice&nbsp;:&nbsp;4,25&nbsp;M utilisateurs&nbsp;→&nbsp;300&nbsp;K réels             | 175&nbsp;M$ payés par JPM                                                         |
| **Bench Accounting (2024)** | Fermeture brutale sans préavis, 600 employés, 35&nbsp;000 clients sans accès à leurs données | Dissolution immédiate                                                             |
| **IRL (2022)**              | 95&nbsp;% des «&nbsp;_20&nbsp;M utilisateurs_&nbsp;» étaient des _bots_                      | Procès SoftBank vs founder                                                        |

## 5. Le rôle des _SaaS_ pour les outils de test

C'est là où l'argument touche directement Ocarina.  
Trois exemples concrets&nbsp;:

### Cypress.io

- 2017&nbsp;—&nbsp;release, open source.
- 2019&nbsp;—&nbsp;SaaS Cypress Dashboard (parallelization, analytics, recording).
- Décembre 2020&nbsp;—&nbsp;Série B de 40&nbsp;M$ menée par OpenView.
- Modèle&nbsp;:&nbsp;on ne peut pas _vraiment_ paralléliser Cypress sans payer le Dashboard. **Lock-in**.

### BrowserStack

- Modèle&nbsp;:&nbsp;tu paies par parallel session. Une suite e2e de 200 tests, 4 navigateurs, 30 min&nbsp;:&nbsp;**la facture à l'année devient salée**.
- Vendu comme «&nbsp;_infrastructure_&nbsp;» alors que c'est une _location_ de VM Selenium standard.

### Sauce Labs /&nbsp;LambdaTest

- Idem BrowserStack. _Commodity_ vendue comme _platform_.

### Le constat d'Ocarina

Tu peux faire _exactement la même chose_ avec&nbsp;:

- **Python 3.14** (gratuit).
- **Selenium** (gratuit).
- **Ocarina** (MIT, 1 dep).
- **GitHub Actions** (gratuit jusqu'à un volume raisonnable).

→&nbsp;**Coût annuel**&nbsp;:&nbsp;0&nbsp;€.  
→&nbsp;**Coût en abonnements**&nbsp;:&nbsp;0&nbsp;€.  
→&nbsp;**Audit**&nbsp;:&nbsp;trivial (un seul dépôt à lire).  
→&nbsp;**Lock-in**&nbsp;:&nbsp;zéro (MIT, code lisible en une après-midi).

## 6. Pourquoi le manifeste est un cri de guerre là-dessus

1. La technique nécessaire pour tester en e2e est **largement gratuite** (Selenium, navigateurs, Python).
2. L'industrie a inventé une **couche payante artificielle** entre cette technique et l'utilisateur final (_presse Juicero_).
3. Les ingénieurs sont **les dupes** finaux&nbsp;:&nbsp;ils paient via leur entreprise pour des outils que la communauté open source produit en plus propre.

Dans des cas d'entreprises énormes comme Vercel ou Stripe, le modèle est compréhensible.  
Dans le cas de _petites startups_, ce n'est rien de plus que du _culte du cargo_ ou encore du _mimétisme_ complètement naïf d'enfants qui veulent jouer aux _grandes personnes_.

Ocarina est l'**alternative**.  
Pas en disant «&nbsp;_notre SaaS est moins cher_&nbsp;», mais en disant «&nbsp;_il n'y a pas de SaaS, le code est là, lis-le, MIT_&nbsp;».

## 7. Connexion avec les autres dossiers du précis

- [`10-infopreneurs-tugan-bara-ai.md`](10-infopreneurs-tugan-bara-ai.md)&nbsp;—&nbsp;Même mécanique côté info-produits&nbsp;:&nbsp;on vend du vent à des gens qui le revendent eux-mêmes.
- [`08-ocarina-in-testing-industry.md`](08-ocarina-in-testing-industry.md)&nbsp;—&nbsp;Le _shift_ qu'Ocarina propose face à cette industrie.
- [`../11-independence/03-explicit-refusals.md`](../11-independence/03-explicit-refusals.md)&nbsp;—&nbsp;Les refus de SaaS, cloud, plateforme.
- [`../11-independence/02-auditability.md`](../11-independence/02-auditability.md)&nbsp;—&nbsp;Pourquoi 1 dep d'exécution est un argument _comptable_, pas seulement esthétique.

## 8. Et après&nbsp;?

La thèse implicite d'Ocarina&nbsp;:

1. La récession des taux 2022+ va **dégonfler** mécaniquement les ARR.
2. Les LP vont commencer à demander des **audits nettement plus sérieux** (déjà visible en 2024-2025).
3. Les _founders_ qui ne peuvent plus lever vont **raboter** leur stack SaaS.
4. Le moment où une équipe va dire «&nbsp;_on annule les 15 abonnements à 5&nbsp;K€/mois et on écrit notre stack en interne_&nbsp;» est **imminent**.
