---
title: "12.11 — The SaaS industry, ARR fraud, the con"
description: "Why Ocarina rejects SaaS: a circular ecosystem where declared revenue is inflated by convention, described as a con."
weight: 11
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 11
---

# 12.11&nbsp;—&nbsp;The SaaS industry, ARR fraud, the con

> Ocarina **rejects SaaS**. The SaaS industry is a **circular ecosystem** where every tool sells to every other tool, where declared revenue is inflated by convention, and where every layer of the capital chain (LP, VC, founder) deliberately maintains a **plausible deniability** so as to sue the others when the time comes.

## 1. Contemporary SaaS

| Layer          | Providers (sample)                                            | Model                                    |
| -------------- | ------------------------------------------------------------- | ---------------------------------------- |
| Hosting & CDN  | **Vercel, Netlify, Cloudflare, Fly.io, Render**               | Subscription per project / per bandwidth |
| DB             | **Supabase, Neon, PlanetScale, Upstash, MongoDB Atlas**       | Subscription per compute / per GB        |
| Auth           | **Clerk, Auth0, WorkOS, Stytch**                              | Subscription per MAU                     |
| Mail           | **Resend, SendGrid, Postmark, Mailgun**                       | Subscription per sent email              |
| Analytics      | **PostHog, Mixpanel, Amplitude, Plausible, Vercel Analytics** | Subscription per event                   |
| Error tracking | **Sentry, BugSnag, Rollbar, Highlight**                       | Subscription per event                   |
| Observability  | **Datadog, New Relic, Honeycomb, Grafana Cloud, Axiom**       | Subscription per metric volume           |
| Feature flags  | **LaunchDarkly, GrowthBook, Statsig, ConfigCat**              | Subscription per MAU                     |
| E2E test       | **BrowserStack, Sauce Labs, LambdaTest, Cypress Dashboard**   | Subscription per run / per parallel      |
| CI             | **GitHub Actions, CircleCI, Buildkite, Vercel CI**            | Subscription per minute                  |
| Code review    | **Graphite, Codeball, CodeRabbit, Sourcery**                  | Subscription per PR / per dev            |
| Internal comms | **Slack, Linear, Notion, Figma, Loom, Pitch**                 | Subscription per seat                    |
| Billing        | **Stripe, Lago, Orb, Metronome**                              | % of processed revenue                   |
| CRM            | **HubSpot, Salesforce, Attio, Pipedrive**                     | Subscription per seat                    |
| Support        | **Intercom, Zendesk, Plain, Help Scout**                      | Subscription per seat + per message      |
| AI tooling     | **OpenAI, Anthropic, Cursor, Vercel AI SDK, Replicate**       | Subscription per token + per seat        |

## 2. Cross-subscriptions

```
   ┌──────────┐ pays     ┌──────────┐
   │ Vercel   │─────────>│ Stripe   │
   │          │<─────────│          │
   └──────────┘     pays └──────────┘
        │                     │
   pays │                     │ pays
        v                     v
   ┌──────────┐          ┌──────────┐
   │ Linear   │<────────>│ Notion   │
   └──────────┘   pay    └──────────┘
        │                     │
        v                     v
   ┌───────────────────────────────┐
   │ Slack, Figma, Loom, Sentry,   │
   │ Datadog, Clerk, Cursor, …     │
   │ all subscribed to all         │
   └───────────────────────────────┘
```

- **Vercel** pays a subscription to _Stripe_ (billing), _Datadog_ (obs), _Linear_ (planning), _Figma_ (design), _Loom_ (internal presentations), _Slack_ (comms), _Notion_ (docs).
- **Stripe** pays a subscription to _Vercel_ (hosting for its dashboards), _Linear_, _Figma_, _Slack_…
- **Linear** pays a subscription to _Vercel_, _Stripe_, _Notion_, _Figma_, _Slack_.
- **Notion** pays a subscription to _Linear_, _Stripe_, _Slack_, _Figma_.

And so on. **Everyone pays everyone.**

## 3. MRR → ARR and _fraud by convention_

### Definitions

| Term    | Definition                                                                                                                                                            |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MRR** | _Monthly Recurring Revenue_, the monthly amount billed to subscription customers                                                                                      |
| **ARR** | _Annual Recurring Revenue_, the annual amount billed to subscription customers. Often, MRR projected over one year: **`ARR = MRR × 12`**, which is frankly fraudulent |

### Conventional fraud

`ARR = MRR × 12` is a **mental model**:

1. **MRR contains prepaid annual plans** divided by 12. If a client pays €12,000 upfront for the year, some count +€1,000 of MRR. If they _churn_ at month 3, the "_MRR_" was never _recurring_.
2. **MRR contains ignored promos / discounts**. A client at 50% off for 6 months is counted at full price in MRR by some.
3. **Projected ARR ignores churn**. The _ARR projection_ assumes 0 churn, while realistic SaaS B2B/B2C churn is unpredictable.
4. **MRR contains optimistic users after trying the _free-tier_**. A _trial_ that converts to _paid_ is counted immediately as perpetual MRR.
5. **Future _upsells_ are sometimes included** in some ARR presentations ("_net new ARR_", "_expansion ARR_").

Result: an MRR of €100K can produce a **declared ARR** of €1.2M while the **actual** annualized revenue will, perhaps, be €600-800K.

### Why nobody says it

Because **no one has an interest in saying it**&nbsp;—&nbsp;incentives align everyone on inflation:

| Actor                                          | Benefit of an inflated ARR                                                          |
| ---------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Founder**                                    | Higher valuation at the next round. Series A+ salary. Options worth more.           |
| **VC (partner)**                               | _Mark-to-market_ of his portfolio higher → declared _carried interest_ bonus to LPs |
| **VC (fund)**                                  | Better _track record_ to raise the next fund                                        |
| **LP** (insurers, _endowments_, pension funds) | Higher declared performance → allocation manager bonus                              |
| **Bank/lender** (venture debt)                 | Wider _ARR_ coverage → loan granted                                                 |
| **Potential acquirer (M&A)**                   | Justifies the _premium_ paid to _their_ board                                       |
| **Employees** (options vesting)                | _Strike_ that looks low compared to the next valuation                              |

## 4. The con, _plausible deniability_

The fraudulent mechanism works as long as it _grows_. The moment it breaks (recession, rates climb, failed IPO, audit), people need to be able to **turn around**. Every layer thus built, from the start, a _plausible deniability_:

```
┌─────────────────────────────────────────────────────────────┐
│ LP (Limited Partner)                                        │
│ "The VC presented me a mark-to-market. I believed it. I am  │
│ a victim."                                                  │
└────────────────┬────────────────────────────────────────────┘
                 │ sues ↓
                 v
┌─────────────────────────────────────────────────────────────┐
│ VC (General Partner)                                        │
│ "The founder presented me his ARR numbers. I took them at   │
│ face value. He's the 'representations & warranties' party." │
└────────────────┬────────────────────────────────────────────┘
                 │ sues ↓
                 v
┌─────────────────────────────────────────────────────────────┐
│ Founder                                                     │
│ "My CFO computed. My auditors validated. I signed what my   │
│ teams produced."                                            │
└────────────────┬────────────────────────────────────────────┘
                 │ sues ↓
                 v
┌─────────────────────────────────────────────────────────────┐
│ CFO / Auditor (Big 4)                                       │
│ "The founder provided the data. I applied accounting        │
│ standards. If the MRR definition was fuzzy, the US-GAAP /   │
│ IFRS framework is fuzzy."                                   │
└─────────────────────────────────────────────────────────────┘
```

Each one leaves themselves a _legal exit_: "_I didn't know, those numbers were presented to me, it's `<layer below>` who lies_".

_Note: this diagram is a deliberate caricature of the plausible-deniability mechanism. Legal reality is messier: suits don't systematically descend layer by layer; the SEC or DoJ often intervene directly without following this order. The structure remains nonetheless representative of each layer's self-protection incentives._

---

Publicly documented case studies:

| Case                        | Mechanism                                                                                  | Consequence                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| **WeWork (2019)**           | Invented metric "_community-adjusted EBITDA_"                                              | IPO withdrawn in 2019 (listing eventually via SPAC in 2021), Adam Neumann replaced |
| **FTX (2022)**              | _Mark_ of illiquid tokens as _revenue_                                                     | Bankruptcy, Sam Bankman-Fried convicted                                            |
| **Frank / JPM (2023)**      | Charlie Javice: 4.25M users → 300K real                                                    | $175M paid by JPM                                                                  |
| **Bench Accounting (2024)** | Sudden shutdown without notice, 600 employees, 35,000 clients without access to their data | Immediate dissolution                                                              |
| **IRL (2022)**              | 95% of the "_20M users_" were _bots_                                                       | SoftBank suit vs founder                                                           |

## 5. The role of _SaaS_ for testing tools

That's where the argument touches Ocarina directly&nbsp;—&nbsp;three concrete examples:

### Cypress.io

- 2017&nbsp;—&nbsp;release, open source.
- 2019&nbsp;—&nbsp;Cypress Dashboard SaaS (parallelization, analytics, recording).
- December 2020&nbsp;—&nbsp;Series B of $40M led by OpenView.
- Model: you can't _truly_ parallelize Cypress without paying for the Dashboard. **Lock-in**.

### BrowserStack

- Model: you pay per parallel session. An e2e suite of 200 tests, 4 browsers, 30 min: **the annual bill gets salty**.
- Sold as "_infrastructure_" when it's a _rental_ of standard Selenium VMs.

### Sauce Labs / LambdaTest

- Same as BrowserStack. _Commodity_ sold as _platform_.

### Ocarina's observation

You can do _exactly the same_ with:

- **Python 3.14** (free).
- **Selenium** (free).
- **Ocarina** (MIT, 1 dep).
- **GitHub Actions** (free up to reasonable volume).

**Annual cost**: €0. **Subscription cost**: €0. **Audit**: trivial (a single repo to read). **Lock-in**: zero (MIT, code readable in an afternoon).

## 6. Why the manifesto is a war cry on this

1. The technique needed to test e2e is **largely free** (Selenium, browsers, Python).
2. The industry invented an **artificial paid layer** between this technique and the end user (_Juicero press_).
3. Engineers are the ultimate **dupes**: they pay through their company for tools that the open-source community produces more cleanly.

In cases of huge companies like Vercel or Stripe, the model is understandable.  
In the case of _small startups_, it's nothing but _cargo cult_ or completely naive _mimicry_ by kids who want to play _grown-ups_.

Ocarina is the **alternative**&nbsp;—&nbsp;not by saying "_our SaaS is cheaper_", but by saying "_there is no SaaS, the code is there, read it, MIT_".

## 7. Connection with the other primer files

- [`10-infopreneurs-tugan-bara-ai.md`](10-infopreneurs-tugan-bara-ai.md)&nbsp;—&nbsp;Same mechanic on the info-product side: selling air to people who resell it themselves.
- [`08-ocarina-in-testing-industry.md`](08-ocarina-in-testing-industry.md)&nbsp;—&nbsp;The _shift_ Ocarina proposes against this industry.
- [`../11-independence/03-explicit-refusals.md`](../11-independence/03-explicit-refusals.md)&nbsp;—&nbsp;The refusals of SaaS, cloud, platform.
- [`../11-independence/02-auditability.md`](../11-independence/02-auditability.md)&nbsp;—&nbsp;Why 1 runtime dep is an _accounting_ argument, not just an aesthetic one.

## 8. And then?

Ocarina's implicit thesis:

1. The 2022+ rate hike will **deflate** ARRs mechanically.
2. LPs will start asking for **much more serious audits** (already visible in 2024-2025).
3. _Founders_ who can no longer raise will **trim** their SaaS stack.
4. The moment when a team will say "_we cancel the 15 €5K/month subscriptions and write our stack in-house_" is **imminent**.
