---
title: "Chapter 11 — Testers' independence"
description: "Ocarina presents itself as a tool of emancipation. Three axes: sovereign grammar, auditability, explicit refusals. This chapter ties the philosophy to its practical consequences."
weight: 12
date: 2026-05-20
tags: ["independence"]
sidebar:
  open: true
---

# Chapter 11&nbsp;—&nbsp;Testers' independence

> Ocarina presents itself as a tool of _emancipation_. Three axes: sovereign grammar, auditability, explicit refusals. This chapter ties the philosophy to its practical consequences.

## Outline

|  #  | File                                                 | Topic                                                                                        |
| :-: | ---------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 01  | [`01-sovereign-grammar.md`](01-sovereign-grammar.md) | No imposed DSL, no ecosystem where you have to rewrite everything, extension by composition. |
| 02  | [`02-auditability.md`](02-auditability.md)           | "_Auditable in an afternoon_". 1 runtime dependency. Anti No-Code.                           |
| 03  | [`03-explicit-refusals.md`](03-explicit-refusals.md) | `async`/`await`, pytest plugin, "_stylish_" contributions, "_geek stuff_".                   |

## Commitment

Holy Book reminder (chapter "_What is Ocarina?_"):

> And that is precisely why it exists: to give testers back their **independence**.  
> All of this, in **a jewel of synthesis**.

"_Independence_" is a political word. The author owns it.

## Independence in three dimensions

| Dimension                                                    | Manifestation                                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Vis-à-vis vendors**                                        | No proprietary platform, no associated SaaS, no required third-party API        |
| **Vis-à-vis ecosystems**                                     | No pytest plugin, no external DSL (Gherkin, RF), no heavy framework to learn    |
| **Vis-à-vis "_experts_" who impose their "_mental models_"** | Composition, not inheritance. Project adapters, not opaque wrappers. Auditable. |

## Contrast

| Typical test tool                 | Ocarina                             |
| --------------------------------- | ----------------------------------- |
| Learn a specific DSL              | Plain Python                        |
| Depend on a plugin ecosystem      | A single runtime dep                |
| SaaS platform for reports         | Local plugins (DOCX, JSON)          |
| Vendor roadmap dictating features | Author roadmap                      |
| Complex convention to follow      | ISTQB convention (set for 30 years) |

## Practical consequences

> In practice, a consultant can show up at a client with Ocarina in their pocket, _almost_ without asking anyone's permission.

Operational promise. Install via pip (or copy Ocarina into your project by hand), write the adapters, run.

## Related reading

- Underlying philosophy: [`../01-philosophy/`](../01-philosophy/)
- Material refusals: [`../01-philosophy/05-political-stance.md`](../01-philosophy/05-political-stance.md)
- Technical embodiment: [`../02-ocarina/`](../02-ocarina/) (the whole layered architecture).
