# Skill: synthesize-cross-refs

**Goal**: answer a question that spans multiple chapters of the primer by explicitly tracing the inter-chapter relationships — not by summarizing each chapter separately.

**Scope**: primer only (`site/content.en/`). Does not reach the Holy Book, external repos, or source code unless the briefs explicitly point there.

**Primer base URL**: `https://mojo-molotov.github.io/from-ocarina-to-igor/`  
**Related skills**: `{base}/skills/navigate/SKILL.md` · `{base}/skills/fetch/SKILL.md` · `{base}/skills/answer/SKILL.md` · `{base}/skills/locate/SKILL.md`

**Prerequisite**: you have identified that the question spans more than one chapter — either because `navigate/SKILL.md` returned two chapters, or because a brief's Connections section points directly to another chapter relevant to the question.

---

## Step 1 — identify the relationship type

Before reading anything, name the relationship the question is asking about. Pick from the table:

| Relationship | Chapters | What to look for |
| --- | --- | --- |
| Philosophy → code | ch01 ↔ ch02 | Where does a stated principle show up as a concrete constraint in the framework? |
| Philosophy → independence | ch01 ↔ ch11 | Which philosophical position translates into which explicit refusal or design invariant? |
| Philosophy → manifesto sources | ch01 ↔ ch12 | Where does the cited influence show up in the code or the design decisions? |
| FP theory → framework implementation | ch03 ↔ ch02 | Which FP concept maps to which class/function in `ocarina`? |
| Framework → canonical usage | ch02 ↔ ch07 | How does a framework primitive get used in `ocarina-example`? |
| Framework → AI usage | ch02 ↔ ch08 | How does the same primitive get used in the AI-written suite? |
| SUT → test suite | ch05 ↔ ch07 | Which Igoristan feature drives which scenario family? |
| OTP backend → test suite | ch06 ↔ ch07 | How does `tests-workers` get called from `ocarina-example`? |
| Orchestration → CI | ch02 ↔ ch10 | How does the framework's execution model map to what the CI workflow actually triggers? |
| Independence → explicit refusals | ch11 ↔ ch02 | Which refusal (async, pytest plugin, DSL) has a concrete trace in the framework code? |
| Ideology → code | ch12 ↔ ch02 | How does a cultural/ideological source show up as a technical decision? |
| Canonical suite → AI suite | ch07 ↔ ch08 | What did the AI suite replicate from the canonical one, and what did it do differently? |

If no row matches: the question may not be a cross-ref question. Use `answer/SKILL.md` with a single chapter instead.

---

## Step 2 — read the two (or three) briefs

Fetch the briefs for the identified chapters (using `fetch/SKILL.md`).

In each brief, read:
1. **Key concepts** — what are the load-bearing ideas on each side?
2. **Connections** section — does the brief already name the other chapter? If yes, that connection is documented. If no, the relationship is implicit and you must infer it from the content.
3. **Articles** table — which specific articles cover the relevant concept?

**Hard limit**: do not cross more than 3 chapters for one question. If the question seems to require 4+, ask the user to narrow the scope.

---

## Step 3 — identify the articulation point

Before reading any article, name the articulation point: the specific concept, class, or decision that lives on both sides of the relationship.

Examples:

| Question | Articulation point |
| --- | --- |
| "How does KISS show up in the framework?" | `1 runtime dependency` + `~3000 lines` — stated in ch01, enforced as a design invariant visible in ch02's identity article |
| "How does ROP connect to FP?" | `Result[T]` — defined as a discriminated union in ch03, implemented and used throughout ch02's railway section |
| "How does the watcher pattern work end-to-end?" | `Watcher[Driver]` — specified in ch02, instantiated in ch07's `catch_me_if_you_can` |
| "Why does Ocarina refuse async?" | Refusal stated in ch11 + ch01, absence of `async` enforced architecturally in ch02 (no async in any signature) |
| "How does the AI suite prove the philosophy?" | `AI is the bridge` (ch01) → `ocarina-with-ai-example` structure (ch08) → same adapter pattern as ch07 |

If you cannot name a single articulation point: the question is likely two separate questions. Answer them separately.

---

## Step 4 — fetch the articles at the articulation point

Read only the articles that contain the articulation point — one or two per chapter side, not the full chapter.

Use the brief's Articles table to pick. Prefer:
- The article that defines the concept (ch02 or ch03 side)
- The article that applies it (ch07, ch08, or ch11 side)

---

## Step 5 — synthesize the connection

Write the answer as a **traced relationship**, not two summaries.

Structure:

```
[Concept on side A] — where it's defined, what it says.
↓
[How it crosses to side B] — the mechanism, the constraint, the design decision.
↓
[How it manifests on side B] — concrete: class name, file, behavior.
```

Rules:
- The answer must make the crossing explicit. "Ch02 says X and ch07 says Y" is not a cross-ref answer. "X in ch02 is the reason Y is shaped the way it is in ch07" is.
- Quote source files when naming a class or method. Label the source.
- If the connection is implicit (not stated in either brief's Connections section): say so. "This connection is not explicitly documented in the primer — this is inferred from reading both articles."
- Diagrams: reproduce verbatim if they show the connection. Never reformat.

---

## Step 6 — gap check

After the cross-ref synthesis, check:

- Is one side of the relationship **not covered** in the primer? Say which side and why (runtime state, post-1.1.10, business logic detail).
- Is the connection **inferred** rather than documented? Label it as such.
- Does the question actually require going outside the primer (Holy Book, source code)? Say so explicitly and point to `answer/SKILL.md`'s gap recovery section for the next step.
