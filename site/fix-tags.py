#!/usr/bin/env python3
"""Merge the `cicd` tag into `ci-cd` and de-duplicate tag lists."""
import os
import re

CONTENT = os.path.join(os.path.dirname(__file__), "content")


def main():
    changed = 0
    for root, _, files in os.walk(CONTENT):
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                lines = f.read().split("\n")
            for i, line in enumerate(lines):
                m = re.match(r"(tags:\s*\[)(.*)(\])\s*$", line)
                if not m:
                    continue
                items = [x.strip().strip('"') for x in m.group(2).split(",") if x.strip()]
                out = []
                for v in items:
                    v = "ci-cd" if v == "cicd" else v
                    if v not in out:
                        out.append(v)
                new = m.group(1) + ", ".join('"%s"' % v for v in out) + m.group(3)
                if new != line:
                    lines[i] = new
                    changed += 1
                break
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
    print(f"{changed} files: tags normalized (cicd -> ci-cd).")


if __name__ == "__main__":
    main()
