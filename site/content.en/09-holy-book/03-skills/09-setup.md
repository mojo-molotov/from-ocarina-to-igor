---
title: "09.03.09 — Setup skills"
description: "The Setup skills exposed to AIs, setup-environment and profile-environment: onboarding a contributor and governing how much latitude the engagement grants the LLM on an Ocarina project."
weight: 9
date: 2026-05-20
series: ["skills"]
series_order: 9
tags: ["holy-book"]
---

# 09.03.09&nbsp;—&nbsp;Setup skills

> Two skills: `setup-environment` (onboarding a new contributor, human or AI) and `profile-environment` (governing how much latitude the engagement grants the LLM). Both feed the suite's assembled `CLAUDE.md`.

## The skill

```
input  : a fresh repo
output : onboarding steps:
            1. venv
            2. pip install (dev deps + ocarina)
            3. ruff / mypy / pre-commit installed
            4. CLAUDE.local.md created (paths requested from user)
            5. runner smoke-check (minimal test that validates everything works)
            6. pre-commit loop tested
```

## Step 1: venv

```bash
python -m venv .venv
source .venv/bin/activate
```

## Step 2: pip install

```bash
pip install . ruff mypy mypy-extensions typing-extensions pre-commit
```

## Step 3: dev tooling

```bash
pre-commit install --config .pre-commit-config.yaml
```

## Step 4: `CLAUDE.local.md`

`CLAUDE.local.md` is **gitignored** and contains machine-specific paths.

The `setup-environment` skill:

1. Checks whether the file exists.
2. If not: creates it from the `CLAUDE.md` template.
3. **Asks** the user for the paths (`chromedriver`, Ocarina ecosystem repo clones).
4. Doesn't guess paths (except `find ~/ -name chromedriver -type f 2>/dev/null` which is documented as a hint).

`CLAUDE.md`:

> `CLAUDE.local.md` is gitignored and stores per-machine paths. If it's missing, create it with the template below&nbsp;—&nbsp;and ask for the paths, don't guess.

## Step 5: runner smoke-check

```bash
python -u src/main.py --browser firefox --driver-path ./geckodriver --workers 3 --only "valid_login"
```

Runs _just_ a smoke test. If it passes: the environment is OK.

`--only valid_login` filters everything else. Allows a fast check rather than a full cycle.

## Step 6: pre-commit loop

```bash
# make a minor edit in src/
git add src/edited_file.py
git commit -m "test: setup smoke"
```

`pre-commit` should run. If it fails, surface it and debug together. In "_vibe testing_" mode, the more aggressive the pre-commit the better: the AI ends up in a context close to reinforcement learning.

If the _pre-commit_ has a "_big_" battery&nbsp;—&nbsp;say, systematically cross-checking formatting, lint, and typing&nbsp;—&nbsp;the AI will be far more effective at self-correcting quickly and can never _commit_ something totally inappropriate (= that doesn't even "_compile_").

## Added value

| Without the skill                                                                                                     | With the skill                          |
| --------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| The newcomer reads the README, does the steps _by hand_, makes mistakes, rages, posts a YouTube video to bash Ocarina | _Sequential_ steps, verified one by one |
| No check that everything really works                                                                                 | Smoke-check confirms                    |
| `CLAUDE.local.md` often forgotten                                                                                     | The skill forces its creation           |

## `profile-environment`&nbsp;—&nbsp;the engagement latitude

`setup-environment` wires the mechanics. `profile-environment` answers a different question: **how much latitude does the human actually grant the LLM on this SUT?**

The whole skill battery has a silent default answer&nbsp;—&nbsp;**"maximum"**. The Holy Book was authored against CURA, an open-source public demo with hardcoded public credentials, so the defaults read: _read the SUT's source, drive a throwaway probe against the live app, research the ecosystem on the open web, public credentials_. A real engagement is narrower.

`profile-environment` runs a profiling interview across **seven latitude dimensions**, resolved _with the human_ (stakeholder decisions, not code-derivable facts):

| Dimension                     | Question                                            |
| ----------------------------- | --------------------------------------------------- |
| Source access                 | Can the LLM read the SUT's source?                  |
| Live-system probing           | Can it drive a throwaway probe against the live app? |
| Data sensitivity              | Demo data, or real / regulated PII?                 |
| Egress & confidentiality      | Is open-web research allowed? Is there an NDA?      |
| Security-testing ceiling      | Where is the active-testing hard line?              |
| Autonomy & approval cadence   | Sign-off before runs?                               |
| Repo / CI / PR change surface | What may it touch?                                  |

It emits a tracked **`CLAUDE.profile.md`** appendix that `setup-environment` concatenates into the suite's `CLAUDE.md`. It is a **ratchet toward restriction**&nbsp;—&nbsp;it only ever _tightens_ the max-latitude defaults and the security hard line, never loosens them.

Run it at the start of any engagement that **isn't** the open public-demo case (a client site, an internal app, an NDA, a live-PII SUT), and re-run it when the terms change (demo&nbsp;→&nbsp;client, staging&nbsp;→&nbsp;prod, an NDA lands, the repo goes private).

## "_Scriptable onboarding_"

A project must be bootstrappable by following a recipe. No tribal knowledge, no "_oh yeah you have to do that too_".

Holy Book quotes:

> Onboarding steps (venv, `pip install`, the skill battery copied into Claude Code, `ruff` / `mypy` / `pre-commit`, runner smoke-check) live in `setup-environment`.

> Ocarina is **dense, immediately operational and strict**. Built so that both humans and LLMs can understand its core and usage without friction.

## Link with the "_auditable in an afternoon_" philosophy

See [`../../11-independence/02-auditability.md`](../../11-independence/02-auditability.md)

Scriptable onboarding is the prelude to the audit: without being able to _run_ the project, you can't understand it.
