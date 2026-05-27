#!/usr/bin/env python3
"""Restore the `# title` (and the summary blockquote) into each page body.
hugo-book expects the H1 in the Markdown content; it does not render the
frontmatter `title`. Idempotent: skips files whose body already starts with `# `.
"""
import os
import re

CONTENT = os.path.join(os.path.dirname(__file__), "content")


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    return s


def main():
    done = 0
    for root, _, files in os.walk(CONTENT):
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
            if not m:
                continue
            fm, body = m.group(1), m.group(2)
            body = body.lstrip("\n")
            if body.startswith("# "):
                continue
            title = desc = None
            for line in fm.split("\n"):
                if line.startswith("title:"):
                    title = unquote(line[len("title:"):])
                elif line.startswith("description:"):
                    desc = unquote(line[len("description:"):])
            if not title:
                continue
            new_body = "# " + title + "\n\n"
            if desc:
                new_body += "> " + desc + "\n\n"
            new_body += body
            with open(path, "w", encoding="utf-8") as f:
                f.write("---\n" + fm + "\n---\n\n" + new_body)
            done += 1
    print(f"{done} files: title restored into the body.")


if __name__ == "__main__":
    main()
