---
title: "00.01 — Ecosystem cartography"
weight: 1
date: 2026-05-20
series: ["big-picture"]
series_order: 1
tags: ["otp"]
---

# 00.01&nbsp;—&nbsp;Ecosystem cartography

The Ocarina ecosystem is **six public repos** under the [`mojo-molotov`](https://github.com/mojo-molotov) GitHub account. They cover **five distinct roles**:

| Role                               | Repo                                                          | Form                                           |
| ---------------------------------- | ------------------------------------------------------------- | ---------------------------------------------- |
| **Framework**                      | `ocarina`                                                     | Python library on PyPI                         |
| **Public System Under Test (SUT)** | `igoristan`                                                   | React + Vike SPA, GitHub Pages                 |
| **Coordination backend**           | `tests-workers`                                               | Vercel Edge API + Upstash Redis                |
| **Example suites**                 | `ocarina-example` (canonical), `ocarina-with-ai-example` (AI) | Python e2e suites driving Igoristan / CURA     |
| **Public documentation**           | `ocarina-holy-book`                                           | VitePress site (EN + FR + RU), PDFs, AI skills |

## The big picture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              OCARINA (BIG PICTURE)                              │
└─────────────────────────────────────────────────────────────────────────────────┘

   ┌──────────────────────────────┐         ┌──────────────────────────────────┐
   │  [PACKAGE]  ocarina          │ ──────► │  [PACKAGE]  ocarina-example      │
   │  Python framework 3.14+      │   pip   │  e2e suite against the Igoristan │
   │  ROP / DSL / orchestration   │ install │  (Selenium + Firefox + Redis)    │
   └──────────────────────────────┘         └──────────────────────────────────┘
            │  │                                       │  ▲   │
            │  │                                       │  │  uses
            │  │ pip install ocarina                   │  │  IGOR_API_KEY
            │  ▼                                       ▼  │   │
            │  ┌────────────────────────────────────┐  drives │
            │  │ [PACKAGE]  ocarina-with-ai-example │  ┌──────┴──────────────────┐
            │  │ e2e suite against CURA Healthcare  │  │ [WEBSITE]  igoristan    │
            │  │ Claude Code, 99% machine-written   │  │ React 19 + Vike         │
            │  └────────────────────────────────────┘  │ GitHub Pages            │
            │              │                           └──────┬──────────────────┘
            │              │ drives                           │ fetches OTP
            │              ▼                                  ▼
            │   ┌──────────────────────────────┐    ┌──────────────────────────────┐
            │   │ [WEBSITE]  CURA Healthcare   │    │ [BACKEND]  tests-workers     │
            │   │ Heroku, open-source PHP      │    │ Vercel Edge Functions        │
            │   └──────────────────────────────┘    │ + Upstash Redis              │
            │                                       │ /api/otp, /otp-history,      │
            │                                       │ /api/corsicadex              │
            │                                       └──────────────────────────────┘
            │                                                 ▲
            │                                                 │ x-api-key
            │                                                 │ (IGOR_API_KEY ≡ API_SECRET)
            │                                                 │
            ▼
   ┌──────────────────────────────┐
   │  [DOCS]  ocarina-holy-book   │
   │  VitePress EN + FR + RU      │
   │  AI skills, PDFs, llms.txt   │
   │  GitHub Pages                │
   └──────────────────────────────┘
```

1. **`ocarina` → example suites**: plain pip dependency (`pip install ocarina`).
2. **Example suites → SUT (Igoristan / CURA)**: browser automation through Selenium.
3. **Igoristan suite ↔ `tests-workers`**: HTTP calls (OTP, Corsicadex). Shared secret: `IGOR_API_KEY` client-side ≡ `API_SECRET` server-side.

## Responsibilities

| Role                 | Contract                                                                                  | Constraint                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Framework            | Ships the DSL, the orchestration, the driver pool, the reporters                          | Stays small, auditable, no hidden deps                                                |
| Public SUT           | A deliberately chaotic playground (random errors, OTP, finicky forms)                     | Lives on GitHub Pages forever, no heavy backend                                       |
| Coordination backend | Coordinates workers on OTP, surfaces data for parallel tests                              | Stateless code, state in Redis (Upstash)                                              |
| Example suites       | Show how Ocarina actually gets used&nbsp;—&nbsp;without AI (canonical) and with AI (CURA) | Public, runnable, complete, in CI                                                     |
| Documentation        | The why, the how, and the AI part                                                         | EN + FR + RU (Corso-Russian tradition), LLM-friendly files like `llms.txt`, plus PDFs |

## Three licenses

| License        | Where                                                                        | Why                                                                                                             |
| -------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **MIT**        | `ocarina`, `ocarina-example`, `ocarina-with-ai-example`, `ocarina-holy-book` | Python code or docs. Transmissible as-is. Sovereign. See [`../11-independence/`](../11-independence/README.md). |
| **ISC**        | `tests-workers`                                                              | Vercel Edge scaffold default. Kept as-is.                                                                       |
| _(unlicensed)_ | `igoristan`                                                                  | Public demo app. Treat it as WTFPL.                                                                             |

## Deliberate friction between repos

The design is **intentionally asymmetric** along certain axes. The friction is the testing tool:

- Igoristan's `useAuth` is _fake_: `Math.random() < 0.9` flunks the login _even with the right password_. Forces Ocarina to replay. See [`../05-igoristan/03-use-auth.md`](../05-igoristan/03-use-auth.md)
- `tests-workers` **drops the milliseconds** from the OTP timestamp (`.000Z`) on purpose, forcing delta-timing coordination. See [`../06-tests-workers/07-otp-coordination-flow.md`](../06-tests-workers/07-otp-coordination-flow.md)
- CURA Healthcare has **documented gaps** in `IDENTIFIED_GAPS.md`. The tests pointed at them fail _on purpose_ in this version of the AI suite. See [`../08-ai-example/05-security-gaps.md`](../08-ai-example/05-security-gaps.md)
- The `Math.random() < 0.3` knob on the `donkey-sausage-eater-detector` page exercises `match_page` (branching on random states). See [`../05-igoristan/02-routes.md`](../05-igoristan/02-routes.md)
- The Igoristan's _random-error_ page exercises `transient_errors` (Ocarina retry) by throwing random errors. The _chaotic form_ throws errors at random without breaking tests directly&nbsp;—&nbsp;that's the watchers' beat. And **random loading times** stress-test your flows against race conditions.

That friction is the **whole point** of this SUT. A website that always works is useless when you're showing off a resilient testing framework.
