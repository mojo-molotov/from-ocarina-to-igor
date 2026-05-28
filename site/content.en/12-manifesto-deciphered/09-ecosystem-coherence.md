---
title: "12.09 — Ecosystem coherence"
description: "How six repositories heterogeneous in languages, licenses and platforms serve rigorously the same bet: the coherence of the Ocarina ecosystem."
weight: 9
date: 2026-05-20
series: ["manifesto-analysis"]
series_order: 9
---

# 12.09&nbsp;—&nbsp;Ecosystem coherence

> Six repos, several languages, several technologies, several licenses, several deployment platforms. At first glance, heterogeneous. On a second read, **rigorously coherent**: every piece serves _exactly the same_ bet.

## 1. Overview: six repos, one ethic

```
┌────────────────────────────────────────────────────────────────────────┐
│         THE ECOSYSTEM AS A COHERENT WHOLE                              │
└────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐    The framework. ROP, strict types, refusal of pytest
  │   ocarina    │    plugin. ONE single runtime dep. Auditable in an
  └─────────────┬┘    afternoon. — PROVES that rigor is lightweight.
                │
                │
                ▼
  ┌─────────────────┐ The reference of use. Project adapters. Canonical
  │ ocarina-example │ patterns. Shows how to narrow the framework's API
  └─────────────┬───┘ surface for your context. — PROVES the framework is
                │     usable "by anyone".
                │
                ▼
  ┌─────────────────────────┐ The AI bet. Co-written by Claude 99%. CURA
  │ ocarina-with-ai-example │ Healthcare as SUT. Findings sourced down to PHP.
  └─────────────┬───────────┘ — PROVES AI + Ocarina can do real senior-tester
                │               work.
                ▼
       ┌──────────────┐ The deliberately chaotic SUT. The playground.
       │  igoristan   │ — PROVES you can test a pathological app without
       └────────┬─────┘   cheating.
                │
                ▼
       ┌────────────────┐ The coordination backend. Vercel Edge,
       │ tests-workers  │ Upstash Redis, deliberate anti-precision.
       └────────┬───────┘ — PROVES you can do distributed coordination
                │           without a proprietary platform.
                │
                ▼
       ┌───────────────────┐ The public documentation. VitePress + FR/EN/RU
       │ ocarina-holy-book │ + LLM-first (llms.txt, CLAUDE.md, skills).
       └───────────────────┘ — PROVES you can write docs that serve human AND
                               AI, without a third-party platform.
```

## 2. One repo = one type of challenge

| Repo                      | Type of challenge                  | Bet proven                                                                  |
| ------------------------- | ---------------------------------- | --------------------------------------------------------------------------- |
| `ocarina`                 | Build a small and deep framework   | "_Rigor isn't a gas factory_"                                               |
| `ocarina-example`         | Demonstrate canonical usage        | "_You can_ actually _write rigorous tests like this_"                       |
| `ocarina-with-ai-example` | Make a human and an AI collaborate | "_AI is the bridge, not the DSL_"                                           |
| `igoristan`               | Build a _chaotic_ SUT              | "_Not a demo on a twenty-HTML-line site&nbsp;—&nbsp;a demo on a real mess_" |
| `tests-workers`           | Coordinate distributed testers     | "You can be _stateless_ on the code side"                                   |
| `ocarina-holy-book`       | Document for humans _and_ AI       | "_Documentation is first and foremost raw data for LLMs_"                   |

Remove one of these repos and the ecosystem **loses an argument**. The six are **solidary**.

## 3. Cross-cutting invariants

### License

| Repo                      | License                       |
| ------------------------- | ----------------------------- |
| `ocarina`                 | MIT                           |
| `ocarina-example`         | MIT                           |
| `ocarina-with-ai-example` | MIT                           |
| `ocarina-holy-book`       | MIT                           |
| `igoristan`               | _none_ (public demo)          |
| `tests-workers`           | ISC (Vercel scaffold default) |

MIT everywhere except special cases. **The license is permissive to the maximum in every case**.

### Signature

Each README ends with:

```
Built by [@mojo-molotov](https://github.com/mojo-molotov)
Fueled by figatellu and Квас.
```

**Offbeat and uniform signature**&nbsp;—&nbsp;a Zone-H&nbsp;/&nbsp;IRC convention ([`04-zoneh-irc-efnet.md`](04-zoneh-irc-efnet.md)).

### Three Git conventions

| Convention               | Manifestation                                                  |
| ------------------------ | -------------------------------------------------------------- |
| **Conventional Commits** | `commitlint` + `commitizen` (Igoristan, Holy Book, ai-example) |
| **Pre-commit hooks**     | Husky (JS) or pre-commit Python (`ocarina`, `ocarina-example`) |
| **No `.no-verify`**      | No hook bypass. If it breaks, fix it.                          |

### Three CI/CD conventions

| Convention                          | Manifestation                            |
| ----------------------------------- | ---------------------------------------- |
| **Fast PR-gate**                    | lint + typecheck (or check-coding-style) |
| **Manual E2E**                      | `workflow_dispatch` only, never on PR    |
| **`if: always()` upload artifacts** | Keep all traces                          |

### Three code conventions

| Convention                                     | Manifestation                                       |
| ---------------------------------------------- | --------------------------------------------------- |
| **Strict type checker**                        | `mypy strict` (Python), `tsc --build` strict (TS)   |
| **Linter in `select = ["ALL"]` or equivalent** | `ruff ALL` (Python), `eslint --max-warnings 0` (TS) |
| **No silent `# noqa`**                         | Always justified, always local                      |

## 4. Coherence of stack choices by context

| Context             | Choice                                         | Why coherent                                                               |
| ------------------- | ---------------------------------------------- | -------------------------------------------------------------------------- |
| Python framework    | Python 3.14+ with PEP 695                      | Modern strict typing                                                       |
| Demo site           | React 19&nbsp;+&nbsp;Vike&nbsp;+&nbsp;Tailwind | _Reference_ 2026 frontend stack; no useless debt                           |
| Lightweight backend | Vercel Edge&nbsp;+&nbsp;Upstash Redis          | Stateless, low-cost, low-tech, deployable in 30 seconds                    |
| Documentation       | VitePress (not Docusaurus, MkDocs, Sphinx)     | Vite-based, aligned with the SUT frontend, hand-built LLM-friendly aspects |
| PDF generation      | Reportlab&nbsp;+&nbsp;AI to orchestrate        | Agentic workflow                                                           |

## 5. Coherence of _tone_

The _tone_ is uniform&nbsp;—&nbsp;different per medium but aligned:

| Medium                           | Tone                                                         |
| -------------------------------- | ------------------------------------------------------------ |
| `ocarina` README                 | Sober technical, factual                                     |
| `ocarina-example` README         | Technical with touches of humor ("_figatellu and Квас_")     |
| `ocarina-with-ai-example` README | Honest and demonstrative ("_99% Claude / 50% intelligence_") |
| `igoristan` README               | Minimalist ("_Welcome to the Empire_")                       |
| `tests-workers` README           | Direct API documentation                                     |
| Holy Book                        | Pamphlet, strong identity, _underground_ quotes              |
| `CLAUDE.md`                      | Strict rules, past examples, firm vocabulary                 |

The _Holy Book_ is the hottest point. READMEs are cold.

This difference is deliberate:

- `README` = technical surface. Must be _usable_ with as little noise as possible.
- Holy Book = philosophical surface. Must be _felt_.

As in the _underground zine_: the cold technical doc _exists_, but the _real voice_ lives in the separate manifesto.

## 6. Cross-repo coherence via **shared secrets**

See [`../00-big-picture/04-repo-relations.md`](../00-big-picture/04-repo-relations.md)

A single secret (`IGOR_API_KEY` ≡ `API_SECRET`) governs all OTP interactions between:

- `ocarina-example` (consumer).
- `tests-workers` (server).
- `igoristan` (UI that passes it).

Not three secrets, not a permissions matrix. **One.** The bare minimum.

> "_Auditable in an afternoon_".

## 7. Coherence of **bugs**

| Deliberate failure                               | Where             | Why                                            |
| ------------------------------------------------ | ----------------- | ---------------------------------------------- |
| `Math.random() < 0.9` on `useAuth`               | `igoristan`       | Force retry on the Ocarina side                |
| `Math.random() < 0.3` on the `random-error` page | `igoristan`       | Force use of `transient_errors`                |
| `Math.random() < 0.3` on `donkey-sausage`        | `igoristan`       | Force `match_page`                             |
| 1/5 chance of `Error('lol')` on Corsicamon       | `igoristan`       | Force retry on the Ocarina side                |
| OTP timestamp stripped of ms                     | `tests-workers`   | Force fine coordination between parallel tests |
| Random `.catch-me-if-you-can` element            | `igoristan`       | Force use of `Watcher`                         |
| Heroku eco-dyno that sleeps (CURA)               | external          | Force CI warm-up                               |
| Chrome BFCache restores `no-store`               | external (Chrome) | Force the cross-browser matrix                 |
| Chrome password manager catches inputs           | external (Chrome) | Force a custom `create_drivers_pool` adapter   |

## 8. Coherence of **refusals**

| Repo                      | Specific refusal                                                           |
| ------------------------- | -------------------------------------------------------------------------- |
| `ocarina`                 | `async/await`, pytest plugin, text DSL, "_stylish_" contributions          |
| `ocarina-example`         | Mocks (uses the real Igoristan), e2e on PR (expensive, manual only)        |
| `ocarina-with-ai-example` | Active security tests, hacks, JS-clicks to bypass, gross workarounds       |
| `igoristan`               | Unit tests (everything is external e2e)                                    |
| `tests-workers`           | GitHub CI (Vercel suffices), server-side framework (direct `.ts` handlers) |
| `ocarina-holy-book`       | Algolia (static Pagefind)                                                  |

## 9. Coherence with the political stance

See [`../11-independence/03-explicit-refusals.md`](../11-independence/03-explicit-refusals.md) and [`../01-philosophy/05-political-stance.md`](../01-philosophy/05-political-stance.md)

The author _refuses_:

- "_Stylish_" contributions
- Misaligned PRs&nbsp;/&nbsp;issues
- "_Democratic code governance_"
- `async/await`
- Vendors
- Proprietary platforms
- _Big-talk engineering_

The ecosystem _materializes_ these refusals:

- No GitHub auto-merge bot
- No Discord, no Slack
- No Patreon&nbsp;/&nbsp;GitHub Sponsors&nbsp;/&nbsp;OpenCollective funding&nbsp;/&nbsp;no _sponsor_ request
- No SLA, no paid support
- No sponsored _talks_
- No _merchandising_

## 10. Meta-coherence: the _primer_ itself

| Trait of the primer            | Aligned with                       |
| ------------------------------ | ---------------------------------- |
| Markdown only, powered by Hugo | Anti-No-Code, anti-SaaS, anti-Devs |
| Cross-referenced multi-files   | Composition, not monolith          |
| ASCII diagrams                 | No proprietary tooling             |
| Free, no paywall               | _Code is Law_                      |
| Unfiltered pedagogy            | Everything is explained, RTFM      |
