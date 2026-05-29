# Skill: fetch-primer

**Goal**: fetch primer content at the right depth — brief only, or full article — depending on context and what the question actually needs.

**Primer base URL**: `https://mojo-molotov.github.io/from-ocarina-to-igor/`  
**Related skills**: `{base}/skills/navigate/SKILL.md` · `{base}/skills/answer/SKILL.md` · `{base}/skills/locate/SKILL.md` · `{base}/skills/synthesize/SKILL.md`

**Prerequisite**: a chapter brief slug and optional article path (from `navigate/SKILL.md`, `locate/SKILL.md`, or `answer/SKILL.md`).

---

## Decision: which mode are you in?

| Tools available | Mode |
| --- | --- |
| Bash/shell tools (Read, grep, git) **and** repo already cloned | **Local mode** |
| Bash/shell tools, repo not yet cloned | **Clone mode** |
| WebFetch only — no Bash, no filesystem access | **Remote mode** |

---

## Local mode

The repo is at a known path. Use `Read` directly.

```
Brief:    site/static/llms/ch{NN}-{slug}.md
Article:  site/content.en/{path-from-navigate}
```

Read the brief first. If the brief answers the question: stop.  
If article depth is needed: read the specific article file. Do not read the whole chapter.

---

## Clone mode

No local copy. Run once, then switch to Local mode.

```bash
git clone https://github.com/mojo-molotov/from-ocarina-to-igor.git /tmp/from-ocarina-to-igor
```

Then read from `/tmp/from-ocarina-to-igor/site/content.en/` and `/tmp/from-ocarina-to-igor/site/static/llms/`.

Clone is preferred over remote fetching: the raw markdown is unprocessed, diagrams are intact, all articles are available offline for the session.

---

## Remote mode

No shell access. Use HTTP fetch only.

### Fetch the brief

```
GET https://mojo-molotov.github.io/from-ocarina-to-igor/llms/ch{NN}-{slug}.md
```

The brief lists every article with a one-line description and flags which ones contain ASCII diagrams. Read it to decide whether to go deeper.

### Fetch a specific article

Articles are not served as raw markdown at a stable URL — they are Hugo-rendered HTML pages. To get the raw source of an article in remote mode, fetch from GitHub:

```
GET https://raw.githubusercontent.com/mojo-molotov/from-ocarina-to-igor/main/site/content.en/{article-path}
```

Example:
```
https://raw.githubusercontent.com/mojo-molotov/from-ocarina-to-igor/main/site/content.en/02-ocarina/05-orchestration/02-test-executor.md
```

### Fallback

If neither GitHub raw nor the brief gives enough depth, instruct the user to clone the repo:
```
git clone https://github.com/mojo-molotov/from-ocarina-to-igor.git
```

---

## Depth rules

**Stop at the brief** when:
- The question is "what exists" / "where is X" / "what does Y do at a high level"
- The brief's key concepts bullet answers it directly

**Fetch one article** when:
- The question names a specific class, method, or flow
- The brief says "see article N" or flags a diagram you need

**Fetch multiple articles** when:
- The question spans a sub-folder (e.g. all of `03-railway/`, all of `05-orchestration/`)
- You need to trace a behavior across several levels (e.g. retry logic: `TestFlow` + `TestExecutor`)
- Hard limit: **8 articles per question**. Above that, ask the user to narrow the scope.

---

## Diagram articles

If a question requires a visual structure, check the brief's Diagrams section for the article filename. The raw ASCII diagram is only in the source file — fetch it directly (Local/Clone/Remote-GitHub-raw), do not rely on the rendered HTML.

Never modify or reformat an ASCII diagram when quoting it.
