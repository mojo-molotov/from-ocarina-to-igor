#!/usr/bin/env python3
"""Migrate from-ocarina-to-igor to Hugo: frontmatter, _index.md, tags, series."""
import os
import re

CONTENT = os.path.join(os.path.dirname(__file__), "content")

KEYWORDS = {
    "rop": ["railway", "result-oriented", "chainrunner", "drive_page", "match_page"],
    "istqb": ["istqb"],
    "typage": ["mypy", "pep 695", "typeguard"],
    "ci-cd": ["github actions", "workflow", "ci/cd", "wireit", "workflow_dispatch"],
    "watcher": ["watcher"],
    "scenarios": ["scénario", "scenario"],
    "selenium": ["selenium", "webdriver", "geckodriver"],
    "otp": ["otp", "corsicadex", "redis"],
    "skills-ia": ["skill", "claude", "llm"],
    "invariants": ["invariant", "validate(", "assert_that"],
    "parallelisation": ["saturation", "parallélis", "thread pool"],
    "manifeste": ["lulzsec", "hacker", "ytcracker", "nerdcore", "antisec"],
}


def clean(name):
    return re.sub(r"^\d+-", "", name)


def number(name):
    m = re.match(r"^(\d+)", name)
    return int(m.group(1)) if m else 0


def yq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_body(text):
    """Return (title, description, body); strip the H1 and a single-line summary blockquote."""
    lines = text.split("\n")
    title = None
    desc = None
    out = []
    i = 0
    n = len(lines)
    # H1
    while i < n:
        if title is None and re.match(r"^#\s+", lines[i]):
            title = re.sub(r"^#\s+", "", lines[i]).strip()
            i += 1
            break
        out.append(lines[i])
        i += 1
    # skip blank lines, then detect a single-line blockquote
    j = i
    while j < n and lines[j].strip() == "":
        j += 1
    if j < n and lines[j].startswith(">") and (j + 1 >= n or not lines[j + 1].startswith(">")):
        desc = re.sub(r"^>\s?", "", lines[j]).strip()
        i = j + 1
        while i < n and lines[i].strip() == "":
            i += 1
    out.extend(lines[i:])
    body = "\n".join(out).lstrip("\n")
    return title, desc, body


def process(path, rel):
    parts = rel.split(os.sep)
    fname = parts[-1]
    is_root = rel == "_index.md"
    is_readme = fname == "README.md"

    with open(path, encoding="utf-8") as f:
        raw = f.read()
    title, desc, body = parse_body(raw)

    if is_root:
        num = 0
        chapter = None
        parent = None
    elif is_readme:
        parent = parts[-2]
        num = number(parent)
        chapter = parts[0]
    else:
        num = number(fname)
        parent = parts[-2]
        chapter = parts[0]

    if not title:
        title = clean(fname[:-3]) if fname != "README.md" else clean(parent or "Index")

    fm = ["---"]
    fm.append(f"title: {yq(title)}")
    if desc:
        fm.append(f"description: {yq(desc)}")
    fm.append(f"weight: {num}")
    fm.append("date: 2026-05-20")

    if not is_root and not is_readme:
        s = clean(parent)
        fm.append(f"series: [{yq(s)}]")
        fm.append(f"series_order: {num}")

    if not is_root:
        tags = [clean(chapter)]
        low = raw.lower()
        for tag, kws in KEYWORDS.items():
            if any(k in low for k in kws) and tag not in tags:
                tags.append(tag)
        tags = tags[:5]
        fm.append("tags: [" + ", ".join(yq(t) for t in tags) + "]")

    fm.append("---")
    out = "\n".join(fm) + "\n\n" + body
    if not out.endswith("\n"):
        out += "\n"

    if is_readme:
        dst = os.path.join(os.path.dirname(path), "_index.md")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(out)
        os.remove(path)
        return f"README.md -> _index.md  {rel}"
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        return f"page              {rel}"


def main():
    count = 0
    for root, _, files in os.walk(CONTENT):
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, CONTENT)
            msg = process(path, rel)
            count += 1
    print(f"{count} files processed.")


if __name__ == "__main__":
    main()
